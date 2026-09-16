"""Take one host-authored draft to a diagram on disk.

The whole create path, in order, with no provider anywhere in it:

    validate draft -> read evidence -> materialize -> layout
    -> validate canonical -> persist -> render

The split that matters is **whose mistake it is**. A refused draft or an unreadable
locator is the caller's, reported as findings they can act on. Anything that fails after
materialization begins is GraphPilot's defect, and the service raises rather than
persisting something malformed.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from services.diagrams.catalog.diagram_shapes import Diagram
from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.persistence.diagram_persistence_service import (
    DiagramPersistenceService,
    DiagramValidationError,
)
from services.diagrams.rendering.diagram_render_service import (
    DiagramRenderService,
    DiagramRenderServiceError,
)
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.drafts.draft_contract import DraftFinding
from services.drafts.draft_validation_service import DraftValidationService
from services.drafts.evidence_service import EvidenceService
from services.materialization import attempt_log
from services.materialization.materializer import materialize
from services.diagrams.rendering.legibility import warning_for as legibility_warning
from services.materialization.faithfulness import check as faithfulness_check
from services.materialization.faithfulness import describe as describe_losses
from services.shared.operation_problem import operation_warning
from services.shared.workspace_storage_service import WorkspaceStorageService

logger = logging.getLogger(__name__)


#: Stands in for a citation nobody read, so a preview can materialize a draft whose
#: evidence has not been resolved. The canonical schema pins digests to
#: `^sha256:[0-9a-f]{64}$`, and this never reaches disk — `preview_warnings` throws the
#: diagram away and keeps only the warnings.
_UNRESOLVED_DIGEST = "sha256:" + "0" * 64


class DraftRefused(Exception):
    """The submitted draft cannot produce a diagram, and here is every reason why."""

    def __init__(self, code: str, findings: Tuple[DraftFinding, ...]) -> None:
        super().__init__(code)
        self.code = code
        self.findings = findings


class DiagramAlreadyExists(Exception):
    """The target diagram is already on disk.

    It may carry edits this draft knows nothing about, so replacing it is an update and
    starting over is an explicit delete.
    """

    def __init__(self, diagram_path: Path) -> None:
        super().__init__(str(diagram_path))
        self.diagram_path = diagram_path


@dataclass(frozen=True)
class CreateResult:
    diagram: Diagram
    diagram_path: Path
    svg_path: Optional[Path]
    layout_engine: str
    #: Ordered non-fatal problems. A failed SVG does not undo a saved diagram.
    warnings: Tuple[Mapping[str, Any], ...]
    #: Always None. `diagram_create` kept the accepted draft here as a record of what a
    #: host claimed; that path is the **edit working file** now, written by `diagram_read`
    #: and consumed by `diagram_update`. A leftover trace there would be indistinguishable
    #: from an edit in flight, and a host that edited one instead of reading would submit a
    #: document that deletes whatever a person added since. Nothing is lost: the projection
    #: reproduces every class-1 field from the diagram, and the ask is in
    #: `metadata.requests`.
    draft_path: Optional[Path] = None

    @property
    def node_count(self) -> int:
        return len(self.diagram["nodes"])

    @property
    def edge_count(self) -> int:
        return len(self.diagram["edges"])


class DiagramCreationService:
    def __init__(
        self,
        *,
        draft_validation: Optional[DraftValidationService] = None,
        layout_service: Optional[DiagramLayoutService] = None,
        persistence: Optional[DiagramPersistenceService] = None,
        render_service: Optional[DiagramRenderService] = None,
    ) -> None:
        self._drafts = draft_validation or DraftValidationService()
        self._layout = layout_service or DiagramLayoutService()
        self._persistence = persistence or DiagramPersistenceService()
        self._render = render_service or DiagramRenderService()
        # The same class `create_exact` validates with, so a preview cannot report a
        # different set of warnings than the create it is previewing.
        self._canonical_validation = DiagramValidationService()

    def preview_warnings(
        self,
        draft: Mapping[str, Any],
        *,
        evidence_digests: Optional[Mapping[str, str]] = None,
    ) -> list[Mapping[str, Any]]:
        """The model warnings a create would return, without creating anything.

        Everything the render-readiness layer knows is a function of the draft: a label
        over 120 characters is a character count, and whether one fits its box is that
        count against a size the layout derives from the same label. None of it needs a
        file on disk. It was nonetheless only reachable through `create` — so three cold
        hosts in one run authored to the contract's stated 256-character limit, were
        warned at 141, 139 and 134, and could not fix any of it, because the diagram was
        already saved and nothing overwrites it. One of them reverse-engineered the real
        threshold by bisecting its own labels.

        `hard_to_read` deliberately stays behind. It measures the SVG that was actually
        drawn — which labels collided with which — and that cannot be known before there
        is a picture. That one is advice on a finished diagram and belongs where it is.

        A digest reaches only `metadata.evidence[].digest`, never a node, an edge or a
        label, so the warnings do not depend on one being real. It must still be
        *present* and well-formed — `_evidence_record` indexes the map directly and the
        canonical schema pins the shape — so any citation the caller has not resolved
        gets a placeholder. Passing an empty map instead raises `KeyError` on every
        `as_implemented` draft, which is nearly all of them.
        """
        digests = {
            str(record.get("id")): _UNRESOLVED_DIGEST
            for record in draft.get("evidence") or ()
        }
        digests.update(evidence_digests or {})
        canonical, _engine = materialize(
            draft, evidence_digests=digests, layout_service=self._layout
        )
        return _structural_warnings(self._canonical_validation.validate(canonical))

    def create(self, workspace_dir: str, draft: Any) -> CreateResult:
        """Turn an accepted draft into the files a reader can open.

        The product's entry point, and the only method here that writes. Everything it
        produces — `<name>.gp.json`, `<name>.svg`, the draft that made them, and the
        attempt log line — lands under `<workspaceDir>/.graphpilot/`.

        **Nothing is written until every refusal has been passed.** A refused draft leaves
        the workspace exactly as it found it and does not consume the diagram name, so a
        host can fix the finding and call again with the same name. That is a promise the
        workflow makes to hosts in as many words, and the ordering below is what keeps it.

        A saved diagram is never overwritten: `DiagramAlreadyExists` is raised instead,
        because the file may carry edits made in the browser that this draft knows nothing
        about.

        Warnings are the other half. They are advice on something that *did* save —
        long labels, structural oddities, text that collided once drawn, and `content_lost`
        when materialization dropped something the draft declared. None of them refuses,
        because the diagram is already better than no diagram.

        Raises:
            DraftRefused: the draft breaks a rule, or a citation could not be read.
            DiagramAlreadyExists: that name is taken.
        """
        # Resolved before the first refusal, not after it. A malformed draft is the single
        # most interesting thing to record and the earliest thing to be thrown out, so
        # anything set up later would miss exactly the attempts worth counting. The path
        # is safety-checked here and never touched unless something is written.
        storage = WorkspaceStorageService(workspace_dir)

        result = self._drafts.validate(draft)
        if not result.valid:
            _record_attempt(storage, draft, accepted=False, findings=result.findings)
            raise DraftRefused(_leading_code(result.findings), result.findings)

        name = draft["diagramName"]
        target = storage.diagram_file_path(name)
        if target.exists():
            # Recorded like any other refusal. It raises before the write, so the earlier
            # version of this method skipped it -- and run 4 counted 12 attempts against
            # 13 made, short in the flattering direction. A host looping on taken names
            # is exactly the friction the count exists to show.
            _record_attempt(
                storage, draft, accepted=False,
                findings=[DraftFinding("diagram_exists", "$.diagramName", str(target))],
            )
            raise DiagramAlreadyExists(target)

        resolution = EvidenceService(storage).resolve(draft.get("evidence") or ())
        if not resolution.valid:
            # A second refusal for the same attempt: the draft was well-formed and its
            # citations were not. Recorded separately, so the two stages stay
            # distinguishable — "the shape was wrong" and "the citations were wrong" are
            # different failures and get fixed differently.
            _record_attempt(storage, draft, accepted=False, findings=resolution.findings)
            raise DraftRefused("evidence_unreadable", resolution.findings)

        canonical, engine = materialize(
            draft,
            evidence_digests=resolution.digests(),
            layout_service=self._layout,
        )

        try:
            outcome = self._persistence.create_exact(workspace_dir, name, canonical)
        except FileExistsError as error:
            # Lost a race between the check above and the exclusive write.
            raise DiagramAlreadyExists(target) from error
        except DiagramValidationError as error:
            # The materializer built this. A canonical failure here is our bug, not the
            # host's, so it must not be reported as a draft problem.
            # `DiagramValidationError` carries `.validation`, not `.result`. Reading the
            # wrong attribute meant the one branch that reports *our* bug raised an
            # AttributeError of its own, hiding the finding it existed to surface. It
            # could only fire when materialization produced an invalid diagram, which is
            # why nothing noticed until a change to `metadata` did exactly that.
            blocking = [
                issue.message for issue in error.validation.issues if issue.severity == "error"
            ]
            raise RuntimeError(
                "Materialization produced an invalid canonical diagram: " + "; ".join(blocking[:5])
            ) from error



        # Materialization is ours, so anything it silently discarded is our defect and the
        # host has no way to see it: their draft was accepted and the diagram is valid.
        # A warning rather than a refusal — the diagram is saved and mostly right, and
        # failing here would punish an author for a bug they did not cause and cannot fix.
        losses = faithfulness_check(draft, canonical)

        svg_path: Optional[Path] = None
        # Canonical validation already ran to decide whether to write, and its non-blocking
        # warnings were being dropped. A host then had to call `diagram_validate` on the
        # file it had just created to learn anything — and the two disagreed, because one
        # counts characters in the model and the other measures the drawn SVG. Reporting
        # both from the one call is what makes them comparable rather than contradictory.
        warnings: list[Mapping[str, Any]] = _structural_warnings(outcome.validation)
        if losses:
            logger.error("Materialization dropped authored content: %s", describe_losses(losses))
            warnings.append(operation_warning(
                "content_lost",
                describe_losses(losses),
                retryable=False,
                lost=[
                    {"kind": l.kind, "id": l.item_id, "field": l.field} for l in losses[:20]
                ],
            ))
        try:
            svg_path = self._render.render(outcome.resolved_path)
            warnings.extend(legibility_warning(canonical, svg_path))
        except (DiagramRenderServiceError, OSError):
            # The diagram is saved. Losing its picture does not undo that, and the host
            # re-renders from the file rather than creating it again.
            logger.exception("Rendering the saved diagram failed")
            warnings.append(operation_warning(
                "render_failed",
                "The diagram was saved but its SVG could not be rendered. "
                "Call diagram_render on the saved file to try again.",
                retryable=True,
            ))

        # Recorded here rather than beside the refusals, for two reasons. The write above
        # is what creates `.graphpilot/`, and the log deliberately never conjures that
        # folder — so logging a first success any earlier would silently drop it. And the
        # warnings are only known now: without them a `hard_to_read` create recorded as
        # `accepted: true, findings: []`, and a later reader concluded it went perfectly.
        _record_attempt(storage, draft, accepted=True, findings=(), warnings=warnings)

        return CreateResult(
            diagram=canonical,
            diagram_path=outcome.resolved_path,
            svg_path=svg_path,
            layout_engine=engine,
            warnings=tuple(warnings),
        )


#: Refusal codes ordered by cause, not severity. A host reads the code before the
#: findings, so it has to name the thing to fix first — and one mistake often produces
#: several findings. A block declared as an ``opaqueAction`` also breaks every
#: relationship touching it; reporting ``notation_invalid`` would send the host to the
#: relationships when the element's type is what is wrong.
_REFUSAL_PRECEDENCE = (
    "draft_too_large",
    "possible_secret",
    # Identity and references: everything below indexes off them.
    "duplicate_id",
    "unresolved_reference",
    "cyclic_parent",
    "orphan_evidence",
    "orphan_assumption",
    # Vocabulary: a wrong type cascades into notation findings.
    "semantic_type_unsupported",
    "containment_unsupported",
    "stereotype_unsupported",
    # Notation, then the claims made about it.
    "notation_invalid",
    "guard_required",
    "evidence_required",
    "evidence_unexpected",
    "assurance_unsupported",
)


def _leading_code(findings: Tuple[DraftFinding, ...]) -> str:
    codes = {finding.code for finding in findings}
    return next((code for code in _REFUSAL_PRECEDENCE if code in codes), "draft_invalid")


def _record_attempt(
    storage: WorkspaceStorageService,
    draft: Any,
    *,
    accepted: bool,
    findings,
    warnings: Sequence[Mapping[str, Any]] = (),
) -> None:
    """Append the attempt, and never let doing so cost a create.

    `storage_root()` can itself raise on an unsafe or unreachable `workspaceDir` — which
    is a real failure the caller is about to hear about properly, not one to surface from
    a logger.
    """
    try:
        attempt_log.record(
            storage.storage_root(), draft,
            accepted=accepted, findings=findings, warnings=warnings,
        )
    except Exception:  # noqa: BLE001 - advisory; the create path owns the real error
        logger.debug(
            "Could not resolve the workspace to record an attempt", exc_info=True
        )


def _structural_warnings(validation: Any) -> list[Mapping[str, Any]]:
    """The non-blocking findings canonical validation already produced.

    These are heuristics on the *model* — a label over 120 characters, an unusually large
    graph — as distinct from `hard_to_read`, which measures the SVG that was actually
    drawn. Neither subsumes the other: a 158-character note label can render perfectly
    inside a large note, and a 40-character label can be clipped by a small node.

    They used to be discarded here, so a host that wanted them had to call
    `diagram_validate` on the file it had just created, and then found two warnings that
    disagreed and never referred to each other.

    `path` is present only when there is one. Not every warning has one — the structural
    critic reports a rule about the graph and names the offending item in its message —
    and a `"path": null` beside a tool that promises "the exact JSON path" reads as a
    missing value rather than an absent one. The other warnings built here (`hard_to_read`,
    `content_lost`) already say "no path" by omitting the key.
    """
    issues = getattr(validation, "issues", None) or ()
    warnings: list[Mapping[str, Any]] = []
    for issue in issues:
        severity = getattr(issue, "severity", None)
        if severity is None or str(getattr(severity, "value", severity)).lower() != "warning":
            continue
        warning: Dict[str, Any] = {
            "code": issue.code,
            "message": issue.message,
            "retryable": False,
        }
        if getattr(issue, "path", ""):
            warning["path"] = issue.path
        details = getattr(issue, "details", None)
        if isinstance(details, Mapping) and details.get("rule"):
            # The structural critic's stable rule id. It was in the ValidationIssue and
            # dropped here, so a host met `structural_constraint` with a sentence and no
            # identifier to look the rule up by.
            warning["rule"] = details["rule"]
        warnings.append(warning)
    return warnings
