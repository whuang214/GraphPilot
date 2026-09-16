"""Read a saved diagram out as an editable draft, and write an edited one back.

Two halves of one round trip:

* **read** — project the saved `.gp.json` into a draft, stamp what it was based on, and
  put it on disk as `.graphpilot/drafts/<name>.draft.json` for the host to edit in place.
* **write** — merge that draft back over the saved diagram, preserving everything the
  draft cannot express.

This module owns the read half and the working file's lifecycle. The merge lives in
`services.materialization.merge`.

**Why a file rather than a payload.** A host that receives several kilobytes of JSON in a
tool result has to echo the whole thing back to change one label, and every echo is a
chance to drop a field it did not understand. Editing a file in place is the operation an
IDE agent is built for, and what it does not touch cannot be lost. It is also cheaper: a
summary and a path, rather than the document, on every read.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from django.utils import timezone

from services.drafts.draft_projection_service import project
from services.shared.workspace_storage_service import WorkspaceStorageService

class EditRefused(Exception):
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


@dataclass(frozen=True)
class ReadResult:
    draft_path: Path
    diagram_path: Path
    draft: Dict[str, Any]
    basis: Dict[str, str]

    @property
    def element_count(self) -> int:
        return len(self.draft.get("elements") or ())

    @property
    def relationship_count(self) -> int:
        return len(self.draft.get("relationships") or ())


class DiagramEditService:
    def __init__(self, storage: Optional[WorkspaceStorageService] = None) -> None:
        self._storage_factory = storage

    def _storage(self, workspace_dir: str) -> WorkspaceStorageService:
        return self._storage_factory or WorkspaceStorageService(workspace_dir)

    def read(self, workspace_dir: str, diagram_name: str) -> ReadResult:
        """Project the saved diagram into a draft file the host can edit in place.

        Overwrites whatever was at the draft path. A leftover from an abandoned edit
        predates any browser save since, so keeping it would let a host edit a stale
        document and submit a write that deletes what somebody added in between.
        """
        storage = self._storage(workspace_dir)
        diagram_path = storage.diagram_file_path(diagram_name)
        if not diagram_path.is_file():
            # The refusal lists what *is* there. `diagram_read` needs a name and nothing on
            # the surface hands one out, so an audit had to list the workspace folder to
            # find out — step one of the edit path was unreachable through the tools. A
            # refusal that answers the question is cheaper than a tool that exists to.
            available = storage.list_diagram_names()
            raise EditRefused(
                "diagram_not_found",
                f"No diagram named {diagram_name!r} in that workspace."
                + (f" Saved diagrams: {', '.join(available)}." if available
                   else " That workspace holds no diagrams yet; use diagram_create."),
                {"diagramPath": diagram_path.as_posix(), "available": available},
            )

        diagram = storage.load_diagram(diagram_path)
        diagram_type = diagram.get("diagramType")
        if diagram_type not in ("activity_diagram", "use_case_diagram", "bdd_diagram"):
            raise EditRefused(
                # A diagram whose type is `custom` was mixed with elements from another
                # type in the editor. The draft's enum has three values and no way to say
                # `custom`, so no draft can describe one - and falling through to a schema
                # error would leave a host guessing at a rule nothing told it about.
                "diagram_crossed",
                f"{diagram_name!r} holds elements from more than one diagram type, so its "
                f"type is '{diagram_type}' and no draft can describe it. It can still be "
                f"edited in the browser.",
                {"diagramPath": diagram_path.as_posix(), "diagramType": diagram_type},
            )

        basis = {
            "diagram": f"sha256:{storage.diagram_revision(diagram_path)}",
            "readAt": timezone.now().isoformat(),
        }
        draft = project(diagram, basis=basis)

        draft_path = self.draft_path(storage, diagram_name)
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(
            json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return ReadResult(draft_path, diagram_path, draft, basis)

    @staticmethod
    def draft_path(storage: WorkspaceStorageService, diagram_name: str) -> Path:
        return storage.drafts_root() / f"{storage.sanitize_name(diagram_name)}.draft.json"

    def discard(self, workspace_dir: str, diagram_name: str) -> bool:
        """Remove the working file. Called by a successful write, and by nothing else.

        A refused write leaves it, so the host can fix the finding and call again without
        losing the edit it made.
        """
        storage = self._storage(workspace_dir)
        return storage.remove_file(self.draft_path(storage, diagram_name))


def basis_matches(submitted: Optional[Mapping[str, Any]], current_revision: str) -> bool:
    """Whether the diagram is still what the read was based on.

    Missing `basis` counts as a mismatch on an edit. A host that stripped it, or authored a
    draft from nothing, has not read the current file — and a whole-document write from
    something that never saw the file omits everything it does not know about, which
    deletes.
    """
    if not submitted:
        return False
    return submitted.get("diagram") == f"sha256:{current_revision}"
