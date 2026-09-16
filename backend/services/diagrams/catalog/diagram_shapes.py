"""Static type shapes for GraphPilot's canonical and logical diagram dicts.

These ``TypedDict``s document the structure of the dicts passed between services and
give editors/type-checkers autocomplete + checking with **zero runtime cost** (a
``TypedDict`` is a plain ``dict`` at runtime). They deliberately do **not** perform
runtime validation: the single source of validation truth stays the JSON Schema enforced
by ``DiagramValidationService``, and Pydantic stays at the MCP tool-argument boundary.

Use these annotations where a value is known to be a canonical/logical diagram (e.g. the
output of generation's conform/assemble steps). Boundary functions that accept untrusted
or partial input (validation, edit/save, inline render) intentionally keep ``dict`` /
``Any`` because their inputs may be malformed — that is exactly what they check.
"""

from typing import Any, Dict, List, NotRequired, TypedDict


class Position(TypedDict):
    """A node's top-left position. For a child node it is relative to its parent."""

    x: float
    y: float


class Multiplicity(TypedDict):
    lower: int
    upper: int | str


class ModelProperty(TypedDict):
    kind: str
    name: str
    type: NotRequired[str]
    multiplicity: NotRequired[Multiplicity]
    default: NotRequired[Any]
    direction: NotRequired[str]
    isReadOnly: NotRequired[bool]
    isOrdered: NotRequired[bool]
    isUnique: NotRequired[bool]
    isDerived: NotRequired[bool]


class ModelFeatures(TypedDict):
    properties: NotRequired[List[ModelProperty]]
    operations: NotRequired[List[Dict[str, Any]]]
    receptions: NotRequired[List[str]]
    constraints: NotRequired[List[Dict[str, str]]]
    literals: NotRequired[List[str]]


class NodeData(TypedDict):
    """Canonical node ``data`` payload (additional type-specific keys may appear)."""

    label: str
    semanticType: NotRequired[str]
    stereotype: NotRequired[str]
    features: NotRequired[ModelFeatures]
    extensionPoints: NotRequired[List[str]]
    appliedStereotypes: NotRequired[List[Dict[str, Any]]]
    port: NotRequired[Dict[str, Any]]


class ElementOrigin(TypedDict):
    """Why a reader should believe this element, carried on every node and edge.

    It declared `claimRefs: List[ClaimVersionRef]` — the JSON 1 model's claim pointers,
    retired in `P0` — and omitted the two fields every real origin has. `assurance` is the
    whole point of the structure: it is how a reader knows an element is grounded in cited
    code rather than assumed.

    Slice 1 of this audit kept `ClaimVersionRef` on the grounds that `ElementOrigin`
    referenced it, which was true and not the question. The referrer was wrong. Checking
    that a symbol has a live caller says nothing about whether the caller is correct, and
    the final pass is what caught it.
    """

    assurance: str
    evidenceRefs: List[str]
    assumptionRefs: List[str]
    schemaRules: List[str]
    rationale: str


class DiagramNode(TypedDict):
    """A canonical diagram node."""

    id: str
    type: str
    position: Position
    width: NotRequired[float]
    height: NotRequired[float]
    data: NodeData
    style: NotRequired[Dict[str, Any]]
    parentId: NotRequired[str]
    origin: NotRequired[ElementOrigin]


class EdgeData(TypedDict):
    """Canonical edge ``data`` payload."""

    semanticType: NotRequired[str]
    sourceEnd: NotRequired[Dict[str, Any]]
    targetEnd: NotRequired[Dict[str, Any]]
    condition: NotRequired[str]
    extensionLocations: NotRequired[List[str]]
    itemFlows: NotRequired[List[Dict[str, Any]]]
    guard: NotRequired[str]
    weight: NotRequired[float]
    isInterrupting: NotRequired[bool]


class DiagramEdge(TypedDict):
    """A canonical diagram edge."""

    id: str
    type: NotRequired[str]
    source: str
    target: str
    data: NotRequired[EdgeData]
    style: NotRequired[Dict[str, Any]]
    label: NotRequired[str]
    origin: NotRequired[ElementOrigin]


class Diagram(TypedDict):
    """The canonical GraphPilot diagram document (schema ``graphpilot.diagram.v1``)."""

    schemaVersion: str
    kind: str
    diagramType: str
    id: str
    name: str
    metadata: DiagramMetadata
    viewport: Dict[str, Any]
    nodes: List[DiagramNode]
    edges: List[DiagramEdge]


# ---------------------------------------------------------------------------
# Logical (pre-layout) shapes — what the LLM returns and ``conform_logical`` produces
# (no coordinates/styles; the layout step adds those when assembling the canonical form)
# ---------------------------------------------------------------------------


class LogicalNode(TypedDict):
    id: str
    semanticType: str
    label: str
    stereotype: NotRequired[str]
    parentId: NotRequired[str]
    features: NotRequired[ModelFeatures]
    extensionPoints: NotRequired[List[str]]
    appliedStereotypes: NotRequired[List[Dict[str, Any]]]
    port: NotRequired[Dict[str, Any]]
    origin: NotRequired[ElementOrigin]


class LogicalEdge(TypedDict):
    source: str
    target: str
    semanticType: str
    label: NotRequired[str]
    sourceEnd: NotRequired[Dict[str, Any]]
    targetEnd: NotRequired[Dict[str, Any]]
    condition: NotRequired[str]
    extensionLocations: NotRequired[List[str]]
    itemFlows: NotRequired[List[Dict[str, Any]]]
    guard: NotRequired[str]
    weight: NotRequired[float]
    isInterrupting: NotRequired[bool]
    origin: NotRequired[ElementOrigin]


class LogicalDiagram(TypedDict):
    name: NotRequired[str]
    nodes: List[LogicalNode]
    edges: List[LogicalEdge]
