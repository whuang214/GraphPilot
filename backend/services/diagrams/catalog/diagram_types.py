"""Shared registry for supported diagram types and lightweight per-type profiles.

The type profile is a compact, validation-facing metadata set separate from the
full generation guidance and examples under ``assets/blueprints/``. Validation
uses only this profile for advisory vocabulary checks.
"""

from dataclasses import dataclass
from typing import Dict, FrozenSet

from services.diagrams.catalog.element_catalog import all_edge_semantic_types, all_node_semantic_types
from services.diagrams.catalog.element_catalog import authorable_edge_semantic_types as catalog_edge_types
from services.diagrams.catalog.element_catalog import authorable_node_semantic_types as catalog_node_types


@dataclass(frozen=True)
class DiagramTypeProfile:
    """Lightweight metadata used for advisory validation checks.

    This profile intentionally does not carry generation prompts, starter graphs, or
    layout guidance. Those belong to the blueprint files in ``assets/blueprints/``.
    """

    diagram_type: str
    node_type: str
    allowed_node_semantic_types: FrozenSet[str]
    allowed_edge_semantic_types: FrozenSet[str]
    expected_blueprint_key_prefix: str
    # The vocabulary the model coerces off-list elements to (per-type). The allowed sets
    # above are derived from the shared element catalog (`element_catalog.py`); these two
    # per-type defaults are the conform fallbacks used by generation_pipeline.
    default_node_semantic_type: str = ""
    default_edge_semantic_type: str = ""
    notation: str = "uml"  # "uml" | "sysml" | "mixed" — stamped into metadata.notation on generation


ACTIVITY_DIAGRAM = "activity_diagram"
USE_CASE_DIAGRAM = "use_case_diagram"
BDD_DIAGRAM = "bdd_diagram"
# The universal "combine anything" canvas: a valid type for save/validation — it
# lives in TYPE_PROFILES with the whole catalog as its vocabulary — but it is NOT a
# generatable type, so it stays out of SUPPORTED_DIAGRAM_TYPES (which drives generation, the
# structural critic, eval, and diagram_list_types).
CUSTOM_DIAGRAM = "custom"

SUPPORTED_DIAGRAM_TYPES: list[str] = [ACTIVITY_DIAGRAM, USE_CASE_DIAGRAM, BDD_DIAGRAM]

#: One plain sentence per identifier, because the identifiers are not self-explaining.
#: ``bdd`` in particular reads as behaviour-driven development to any software reader,
#: and two complete observed runs were lost to that: a host gathered behavioural
#: evidence, authored both documents, and only learned at the readiness gate that a
#: structural view was wanted - by which point append-only history refused the
#: correction. Every surface that names a type shows this alongside it.
#: ``meaning`` says what the type is; ``chooseWhen`` says which request it answers. A host
#: is not choosing between three definitions, it is mapping a request onto a type, and the
#: definition alone never did that job.
DIAGRAM_TYPE_GUIDE: Dict[str, Dict[str, str]] = {
    ACTIVITY_DIAGRAM: {
        "meaning": (
            "UML Activity Diagram. Behavioural: ordered actions, decisions, and flow "
            "through one process."
        ),
        "chooseWhen": (
            "The request is about behaviour over time - what happens, in what order, "
            "where the flow branches or runs in parallel. Typical wording: 'what happens "
            "when someone...', 'the steps to...', 'how does X get handled'."
        ),
    },
    USE_CASE_DIAGRAM: {
        "meaning": (
            "UML Use Case Diagram. Actors outside a system boundary and the goals each "
            "can achieve with it."
        ),
        "chooseWhen": (
            "The request is about who uses the system and what they can achieve with it. "
            "Typical wording: 'who uses this', 'what can each role do', 'actors and "
            "their goals'. Goals, not steps - use activity_diagram for how a goal is met."
        ),
    },
    BDD_DIAGRAM: {
        "meaning": (
            "SysML Block Definition Diagram. Structural: blocks, their parts and "
            "properties, and the relationships between them. Not behaviour-driven "
            "development, and not a behavioural view - use activity_diagram for behaviour."
        ),
        "chooseWhen": (
            "The request is about structure - what things exist, what they own, and how "
            "they relate. Typical wording: 'the domain model', 'what this system stores', "
            "'how these types relate'. READ THIS ONE TWICE: `bdd` here abbreviates Block "
            "Definition Diagram, NOT behaviour-driven development. Two runs were lost to "
            "that reading, by hosts that recognised the letters and never read the "
            "meaning. If the request is about behaviour, you want activity_diagram."
        ),
    },
}

#: One plain sentence per identifier, derived so there is a single definition of each.
DIAGRAM_TYPE_MEANINGS: Dict[str, str] = {
    name: entry["meaning"] for name, entry in DIAGRAM_TYPE_GUIDE.items()
}

TYPE_PROFILES: Dict[str, DiagramTypeProfile] = {
    ACTIVITY_DIAGRAM: DiagramTypeProfile(
        diagram_type=ACTIVITY_DIAGRAM,
        node_type="gpNode",
        allowed_node_semantic_types=catalog_node_types(ACTIVITY_DIAGRAM),
        allowed_edge_semantic_types=catalog_edge_types(ACTIVITY_DIAGRAM),
        expected_blueprint_key_prefix="activity_diagram",
        default_node_semantic_type="opaqueAction",
        default_edge_semantic_type="controlFlow",
    ),
    USE_CASE_DIAGRAM: DiagramTypeProfile(
        diagram_type=USE_CASE_DIAGRAM,
        node_type="gpNode",
        allowed_node_semantic_types=catalog_node_types(USE_CASE_DIAGRAM),
        allowed_edge_semantic_types=catalog_edge_types(USE_CASE_DIAGRAM),
        expected_blueprint_key_prefix="use_case_diagram",
        default_node_semantic_type="useCase",
        default_edge_semantic_type="association",
    ),
    BDD_DIAGRAM: DiagramTypeProfile(
        diagram_type=BDD_DIAGRAM,
        node_type="gpNode",
        allowed_node_semantic_types=catalog_node_types(BDD_DIAGRAM),
        allowed_edge_semantic_types=catalog_edge_types(BDD_DIAGRAM),
        expected_blueprint_key_prefix="bdd_diagram",
        default_node_semantic_type="block",
        default_edge_semantic_type="association",
        notation="sysml",
    ),
    CUSTOM_DIAGRAM: DiagramTypeProfile(
        diagram_type=CUSTOM_DIAGRAM,
        node_type="gpNode",
        # The custom canvas permits the whole catalog, so advisory validation never flags
        # mixing notations and conform imposes no per-type restriction.
        allowed_node_semantic_types=all_node_semantic_types(),
        allowed_edge_semantic_types=all_edge_semantic_types(),
        expected_blueprint_key_prefix="custom",
        default_node_semantic_type="opaqueAction",
        default_edge_semantic_type="association",
        notation="mixed",
    ),
}


def is_supported_diagram_type(diagram_type: str) -> bool:
    """Return whether ``diagram_type`` is one of the supported MVP types."""
    return diagram_type in TYPE_PROFILES


def get_type_profile(diagram_type: str) -> DiagramTypeProfile:
    """Return the type profile for a supported diagram type.

    Raises:
        ValueError: if ``diagram_type`` is not supported.
    """
    try:
        return TYPE_PROFILES[diagram_type]
    except KeyError:
        supported = ", ".join(TYPE_PROFILES)
        raise ValueError(f"Unsupported diagram type: {diagram_type!r}. Supported types: {supported}") from None


def conforms_to_type(nodes, edges, diagram_type: str) -> bool:
    """Whether every node/edge ``semanticType`` is within ``diagram_type``'s allowed subset.

    Lets the save route decide whether an edited diagram still fits its declared type (keep
    it) or has gone off-vocabulary (flip ``diagramType`` to ``custom``). An unknown type
    conforms vacuously; for ``custom`` the allowed set is the whole catalog, so only a
    non-catalog ``semanticType`` fails to conform.
    """
    profile = TYPE_PROFILES.get(diagram_type)
    if profile is None:
        return True
    for node in nodes if isinstance(nodes, list) else []:
        if not isinstance(node, dict):
            continue
        data = node.get("data")
        sem = data.get("semanticType") if isinstance(data, dict) else None
        if isinstance(sem, str) and sem not in profile.allowed_node_semantic_types:
            return False
    for edge in edges if isinstance(edges, list) else []:
        if not isinstance(edge, dict):
            continue
        data = edge.get("data")
        sem = data.get("semanticType") if isinstance(data, dict) else None
        if isinstance(sem, str) and sem not in profile.allowed_edge_semantic_types:
            return False
    return True
