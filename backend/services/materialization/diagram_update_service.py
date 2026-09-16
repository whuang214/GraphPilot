"""Write an edited draft back over a saved diagram.

The other half of the round trip that `DiagramEditService.read` starts. It materializes the
submitted draft exactly as a create would, then merges the result over what is on disk so
that everything the draft could not express survives.

The order matters and each step earns its place:

1. **validate the draft** — the same rules a create uses, so an edit cannot smuggle
   anything past them.
2. **check the basis** — was the read based on the file that is there now?
3. **check the append** — the request log grows by exactly one row, and the earlier rows
   come back unchanged.
4. **resolve evidence** — new citations hard, existing ones carried and re-checked.
5. **materialize + merge + place** — class 1 from the draft, class 2 by id, class 3 fresh.
6. **history, then write** — the previous version is kept before it is replaced.
"""

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from django.utils import timezone

from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.rendering.diagram_render_service import (
    DiagramRenderService,
    DiagramRenderServiceError,
)
from services.diagrams.persistence.diagram_persistence_service import (
    DiagramPersistenceService,
)
from services.drafts.diagram_edit_service import DiagramEditService, basis_matches
from services.drafts.draft_validation_service import DraftFinding, DraftValidationService
from services.drafts.evidence_service import EvidenceService
from services.diagrams.rendering.legibility import warning_for as legibility_warning
from services.materialization.geometry import new_overlaps, place_new_nodes
from services.materialization.merge import MergeResult, Removed, merge
from services.materialization.materializer import materialize
from services.shared.operation_problem import operation_warning
from services.shared.workspace_storage_service import WorkspaceStorageService

#: How many previous versions are kept beside a diagram.
#:
#: Three, because the value is in the last few seconds of *"that was wrong, put it back"* —
#: not in an archive. An unbounded history of a file somebody edits all afternoon is a
#: directory nobody prunes, in a repository they did not ask to grow.
HISTORY_DEPTH = 3


class UpdateRefused(Exception):
    def __init__(self, code: str, findings: Sequence[DraftFinding] = (), message: str = ""):
        super().__init__(message or code)
        self.code = code
        self.findings = tuple(findings)
        self.message = message or code


@dataclass
class UpdateResult:
    diagram_path: Path
    svg_path: Optional[Path]
    removed: Tuple[Removed, ...]
    added_ids: Tuple[str, ...]
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    history_path: Optional[Path] = None


#: How much of a joined validation summary a host is given before it is cut.
_SUMMARY_BUDGET = 400


def _joined_errors(issues: Sequence[Any]) -> str:
    """One line naming every error, and saying so when it could not name them all.

    This was `"; ".join(...)[:400]`. A slice is a silent edit: with five errors the
    fifth arrived cut mid-word, and nothing in the string said a fifth existed. A host
    fixes the four it can read, calls again, and meets the same refusal — the one piece
    of information it needed was the piece the slice removed.

    Whole messages, then a count of what did not fit. Never a fragment.
    """
    messages = [issue.message for issue in issues if issue.severity == "error"]
    if not messages:
        return "The diagram did not validate."
    kept: List[str] = []
    length = 0
    for message in messages:
        addition = len(message) + (2 if kept else 0)
        if kept and length + addition > _SUMMARY_BUDGET:
            break
        kept.append(message)
        length += addition
    summary = "; ".join(kept)
    remaining = len(messages) - len(kept)
    if remaining:
        summary += f" (and {remaining} more error{'s' if remaining > 1 else ''})"
    return summary


def _request_findings(submitted: Sequence[str], saved: Sequence[Mapping[str, Any]]
                      ) -> List[DraftFinding]:
    """The append rule: one new row, and the earlier ones unchanged.

    Checked against the diagram rather than inside the draft, because "unchanged" is only a
    question with an answer once there is something to compare against. Rewriting history
    is the failure this catches — a host that edits an earlier ask is rewriting why the
    diagram looks the way it does, which is the one thing the log exists to prevent.
    """
    previous = [entry["text"] for entry in saved]
    if len(submitted) != len(previous) + 1:
        return [DraftFinding(
            "requests_invalid", "$.requests",
            f"An edit appends exactly one ask. The diagram has {len(previous)}, so send "
            f"{len(previous) + 1}; this draft has {len(submitted)}.",
        )]
    if list(submitted[:len(previous)]) != previous:
        return [DraftFinding(
            "requests_invalid", "$.requests",
            "The earlier asks must come back unchanged — they are the record of why this "
            "diagram looks the way it does. Append yours to the end.",
        )]
    return []


class DiagramUpdateService:
    def __init__(
        self,
        drafts: Optional[DraftValidationService] = None,
        layout: Optional[DiagramLayoutService] = None,
        persistence: Optional[DiagramPersistenceService] = None,
        render: Optional[DiagramRenderService] = None,
    ) -> None:
        self._drafts = drafts or DraftValidationService()
        self._layout = layout or DiagramLayoutService()
        self._persistence = persistence or DiagramPersistenceService()
        self._render = render or DiagramRenderService()
        self._edits = DiagramEditService()

    def update(self, workspace_dir: str, draft: Any) -> UpdateResult:
        storage = WorkspaceStorageService(workspace_dir)

        # Before anything else, because `basis` is what marks a draft as an edit at all.
        # Without it the validator reads the document as a create and refuses the request
        # log for carrying more than one ask — true of a create, and a baffling thing to
        # be told while updating. The cause is the missing stamp; say that instead.
        if not isinstance(draft, Mapping) or not draft.get("basis"):
            raise UpdateRefused(
                "basis_stale", (),
                "This draft carries no `basis`, so it did not come from `diagram_read`. "
                "An update submits the whole diagram, so one written from scratch deletes "
                "everything it does not happen to mention. Read the diagram first.",
            )

        result = self._drafts.validate(draft)
        if not result.valid:
            raise UpdateRefused(result.findings[0].code, result.findings)

        name = draft["diagramName"]
        target = storage.diagram_file_path(name)
        if not target.is_file():
            raise UpdateRefused(
                "diagram_not_found", (),
                f"No diagram named {name!r} to update. Use diagram_create for a new one.",
            )
        saved = storage.load_diagram(target)

        if not basis_matches(draft.get("basis"), storage.diagram_revision(target)):
            raise UpdateRefused(
                "basis_stale", (),
                "This diagram changed after you read it — somebody saved in the browser. "
                "Read it again and re-apply your change, or their work is deleted by "
                "everything your draft does not mention.",
            )

        appended = _request_findings(
            draft.get("requests") or (), (saved.get("metadata") or {}).get("requests") or ()
        )
        if appended:
            raise UpdateRefused("requests_invalid", appended)

        # Existing citations are class 2, keyed on evidence id: carried with their digest
        # exactly like a position. Anything new or changed is resolved hard, on the create
        # rules, because it is a claim nobody has checked yet.
        carried_digests = {
            record["id"]: record["contentDigest"]
            for record in (saved.get("metadata") or {}).get("evidence") or ()
        }
        submitted = {record["id"]: record for record in draft.get("evidence") or ()}
        saved_records = {
            record["id"]: record
            for record in (saved.get("metadata") or {}).get("evidence") or ()
        }
        fresh = [
            record for record_id, record in submitted.items()
            if _citation_changed(record, saved_records.get(record_id))
        ]
        evidence = EvidenceService(storage)
        resolution = evidence.resolve(fresh)
        if not resolution.valid:
            raise UpdateRefused("evidence_unreadable", resolution.findings)
        digests = {**carried_digests, **resolution.digests()}

        built, _engine = materialize(
            draft, evidence_digests=digests, layout_service=self._layout
        )
        merged: MergeResult = merge(built, saved)
        place_new_nodes(merged.diagram, merged.new_node_ids)

        metadata = merged.diagram.setdefault("metadata", {})
        metadata["updatedAt"] = timezone.now().isoformat()

        warnings: List[Dict[str, Any]] = []
        outcome = self._persistence.save(str(target), merged.diagram)
        if not outcome.saved:
            raise UpdateRefused(
                "validation_failed", (),
                _joined_errors(outcome.validation.issues),
            )

        # After the save, not before. History records what happened, and this used to
        # record what was attempted: a refused or failed write left a backup of a change
        # that never landed. `HISTORY_DEPTH` is three, so three failed updates in a row
        # evicted every real version and left the person three copies of the state they
        # were already in — history destroyed by the failure of the thing it exists to
        # protect against. `saved` is held in memory, so the previous content is still
        # exactly what goes in.
        history_path = self._keep_previous(storage, name, saved)

        # R2 grows a box whose content outgrew it, and R5 forbids moving anything to make
        # room, so growth can put two boxes on top of each other. The design's answer is to
        # say so: "if the grown box now overlaps a neighbour, that is a warning, not a
        # licence to move anything". Without this the grow is silent, and the person who
        # arranged the diagram is the one who discovers the collision.
        collisions = new_overlaps(saved, merged.diagram)
        if collisions:
            warnings.append(operation_warning(
                "layout_overlap",
                f"{len(collisions)} pair(s) of elements now overlap, because a box grew "
                f"to fit its content and nothing is allowed to move to make room.",
                retryable=False,
                pairs=[list(pair) for pair in collisions],
            ))

        # A region cited by the diagram that has moved since is reported, never refused.
        # Blocking would put an edit at the mercy of files it never looked at: a host asked
        # to add one node would be refused over twelve findings about somebody else's
        # refactor, with no way to act on any of them.
        stale = evidence.recheck([
            record for record in (saved.get("metadata") or {}).get("evidence") or ()
            if record["id"] not in {r["id"] for r in fresh}
        ])
        if stale:
            warnings.append(operation_warning(
                "evidence_stale",
                f"{len(stale)} of {len(carried_digests)} cited regions have changed "
                f"since this diagram was made.",
                evidenceIds=[finding.path for finding in stale],
            ))

        # The picture is the artifact a person actually opens, and an update that left it
        # alone left it showing the element that was just deleted and not the one just
        # added. An audit caught that only by comparing file timestamps -- from the tool
        # output there was no way to know. A failed render does not undo a saved diagram,
        # so it is a warning like any other.
        svg_path = None
        try:
            svg_path = self._render.render(outcome.resolved_path)
            warnings.extend(legibility_warning(merged.diagram, svg_path))
        except (DiagramRenderServiceError, OSError) as exc:
            warnings.append(operation_warning(
                "render_failed",
                f"The diagram was saved but its SVG could not be redrawn: {exc}",
            ))

        self._edits.discard(workspace_dir, name)
        return UpdateResult(
            diagram_path=outcome.resolved_path,
            svg_path=svg_path,
            removed=merged.removed,
            added_ids=merged.new_node_ids,
            warnings=warnings,
            history_path=history_path,
        )

    @staticmethod
    def _keep_previous(
        storage: WorkspaceStorageService, name: str, saved: Mapping[str, Any]
    ) -> Optional[Path]:
        """Copy the current version into `history/<name>/` before replacing it.

        Recovery rather than prevention. A write precondition can only stop the writes it
        anticipates, and the ones that hurt are the ones nobody saw coming — a host
        omitting an element it never knew about deletes it, and no precondition catches
        that because the write is perfectly well-formed.

        Restoring is copying the file back. There is no tool for it: history is files in a
        folder, and a person who wants a version back can take it.
        """
        folder = storage.storage_root() / "history" / storage.sanitize_name(name)
        folder.mkdir(parents=True, exist_ok=True)
        stamp = timezone.now().strftime("%Y%m%dT%H%M%S%f")
        extension = WorkspaceStorageService.diagram_extension()
        path = folder / f"{stamp}{extension}"
        path.write_text(
            json.dumps(saved, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        for old in sorted(folder.glob(f"*{extension}"))[:-HISTORY_DEPTH]:
            old.unlink(missing_ok=True)
        return path


def _citation_changed(
    submitted: Mapping[str, Any], saved: Optional[Mapping[str, Any]]
) -> bool:
    """Whether this citation is new, or points somewhere it did not before."""
    if saved is None:
        return True
    return (
        submitted.get("locator") != {
            key: value for key, value in (saved.get("locator") or {}).items()
            if key != "contentDigest"
        }
        or submitted.get("kind") != saved.get("kind")
    )
