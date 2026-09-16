"""The response shapes the browser-facing load and save routes return.

Each owns its `to_dict`, which is the wire contract the frontend types mirror — so a
field is renamed in one place rather than wherever a response happens to be built.

There were request dataclasses beside these once, and nothing ever constructed them: the
views read `request.query_params` and `request.data` directly, which is idiomatic DRF.
A one-field dataclass nobody instantiates is not a contract, and this docstring used to
claim all four were in use.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from services.shared.operation_problem import OperationProblem


@dataclass
class DiagramLoadResponse:
    """Success response for GET /api/diagrams/load."""

    diagram_path: str
    diagram: Dict[str, Any]
    revision: str

    def to_dict(self) -> Dict[str, Any]:
        return {"diagramPath": self.diagram_path, "diagram": self.diagram, "revision": self.revision}


@dataclass
class DiagramSaveResponse:
    """Success response for POST /api/diagrams/save.

    ``diagram`` is the normalized document that was written, so clients can adopt
    reconciled type/provenance immediately. ``svg_path`` is the sibling ``<name>.svg``
    written by the best-effort render-on-save step; it is omitted when rendering was
    skipped or failed (the save itself still succeeds regardless).
    """

    saved: bool
    diagram_path: str
    diagram: Dict[str, Any]
    revision: str
    svg_path: Optional[str] = None
    warning: Optional[OperationProblem] = None

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "saved": self.saved,
            "diagramPath": self.diagram_path,
            "diagram": self.diagram,
            "revision": self.revision,
        }
        if self.svg_path is not None:
            body["svgPath"] = self.svg_path
        if self.warning is not None:
            body["warning"] = self.warning.to_dict()
        return body
