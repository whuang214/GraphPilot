"""The universal element catalog.

One place that defines every diagram **element** (node or edge) once: which render
**primitive** it draws as, its notation family, and which diagram types it is valid in.
A diagram type's allowed vocabulary is then a **subset** of this catalog, and small
cross-cutting facts the pipeline needs (which nodes are containers, which edges are
dashed) are derived from it.

Semantic identity follows the clause-traced UML 2.5.1 / SysML 1.6 vocabulary. Elements
that share a glyph remain distinct catalog entries and reuse only the render primitive;
property classifications and relationship-end semantics stay structured data.

This module is a leaf and therefore uses diagram-type name strings directly instead of
importing ``diagram_types`` (which imports this catalog).

See ``docs/02-design-and-features/00-diagram-json-schema.md`` (the standard).
"""

from dataclasses import dataclass, replace
from typing import Dict, FrozenSet, List, Optional

# Diagram-type names (kept as plain strings here to avoid a circular import with
# ``diagram_types``; they mirror the constants re-exported from there).
ACTIVITY_DIAGRAM = "activity_diagram"
USE_CASE_DIAGRAM = "use_case_diagram"
BDD_DIAGRAM = "bdd_diagram"
# The universal "combine anything" canvas. Elements valid only here are
# canvas-only: reusable by hand-authoring + future diagram types, but not part of the
# 3 MVP types' generation vocabulary.
CUSTOM_DIAGRAM = "custom"

# The finite set of shapes the renderer knows. Many exact semantic types share one
# primitive; ports/pins are owned boundary features rather than standalone definitions.
RENDER_PRIMITIVES: FrozenSet[str] = frozenset(
    {
        "note",
        "rounded-rect",
        "initial",
        "final",
        "flow-final",
        "diamond",
        "bar",
        "actor",
        "ellipse",
        "container",
        "classifier-box",
        "object",
        "datastore",
        "pin",
        "partition",
        "region",
        "send-signal",
        "accept-event",
        "port",
    }
)


@dataclass(frozen=True)
class ElementSpec:
    """One catalog element (a node or an edge), defined once."""

    semantic_type: str
    kind: str  # "node" | "edge"
    notation: str  # "common" | "uml" | "sysml"
    valid_in: FrozenSet[str]  # diagram types that allow this element
    description: str
    spec_ref: str
    metamodel_form: str  # metaclass | stereotype | property | relationship | notation
    category: str
    authorable_in: FrozenSet[str] = frozenset()
    primitive: Optional[str] = None  # nodes: the render primitive
    is_container: bool = False  # nodes: acts as a containment box (keeps a child's parentId)
    dashed: bool = False  # edges: drawn with a dashed line
    target_marker: str = "arrow"  # edges: "arrow" | "triangle" | "diamond_filled" | "none"
    source_marker: str = "none"  # edges: "none" | "diamond_filled" | "diamond_hollow"


def _node(
    semantic_type: str,
    primitive: str,
    notation: str,
    valid_in: set,
    description: str,
    spec_ref: str,
    *,
    metamodel_form: str = "metaclass",
    category: str = "element",
    is_container: bool = False,
) -> ElementSpec:
    return ElementSpec(
        semantic_type=semantic_type,
        kind="node",
        notation=notation,
        valid_in=frozenset(valid_in),
        description=description,
        spec_ref=spec_ref,
        metamodel_form=metamodel_form,
        category=category,
        primitive=primitive,
        is_container=is_container,
    )


def _edge(
    semantic_type: str,
    notation: str,
    valid_in: set,
    description: str,
    spec_ref: str,
    *,
    metamodel_form: str = "relationship",
    category: str = "relationship",
    dashed: bool = False,
    target_marker: str = "arrow",
    source_marker: str = "none",
) -> ElementSpec:
    return ElementSpec(
        semantic_type=semantic_type,
        kind="edge",
        notation=notation,
        valid_in=frozenset(valid_in),
        description=description,
        spec_ref=spec_ref,
        metamodel_form=metamodel_form,
        category=category,
        dashed=dashed,
        target_marker=target_marker,
        source_marker=source_marker,
    )


_ELEMENTS: List[ElementSpec] = [
    _node("note", "note", "common", {ACTIVITY_DIAGRAM, USE_CASE_DIAGRAM, BDD_DIAGRAM}, "A comment attached to model elements.", "UML 2.5.1 clause 7.2", category="annotation"),
    _node("initialNode", "initial", "uml", {ACTIVITY_DIAGRAM}, "The unique entry point of an activity.", "UML 2.5.1 clause 15.7.18", category="control"),
    _node("activityFinalNode", "final", "uml", {ACTIVITY_DIAGRAM}, "Terminates all flows in an activity.", "UML 2.5.1 clause 15.7.3", category="control"),
    _node("flowFinalNode", "flow-final", "uml", {ACTIVITY_DIAGRAM}, "Terminates only the flow that reaches it.", "UML 2.5.1 clause 15.7.16", category="control"),
    _node("decisionNode", "diamond", "uml", {ACTIVITY_DIAGRAM}, "Selects one outgoing flow according to guards.", "UML 2.5.1 clause 15.7.12", category="control"),
    _node("mergeNode", "diamond", "uml", {ACTIVITY_DIAGRAM}, "Combines alternative incoming flows without synchronization.", "UML 2.5.1 clause 15.7.21", category="control"),
    _node("forkNode", "bar", "uml", {ACTIVITY_DIAGRAM}, "Splits a flow into concurrent outgoing flows.", "UML 2.5.1 clause 15.7.17", category="control"),
    _node("joinNode", "bar", "uml", {ACTIVITY_DIAGRAM}, "Synchronizes concurrent incoming flows.", "UML 2.5.1 clause 15.7.20", category="control"),
    _node("activityParameterNode", "object", "uml", {ACTIVITY_DIAGRAM}, "An activity input or output parameter on the activity boundary.", "UML 2.5.1 clause 15.7.6", category="object"),
    _node("objectNode", "object", "uml", {ACTIVITY_DIAGRAM}, "Holds object tokens in an activity.", "UML 2.5.1 clause 15.7.23", category="object"),
    _node("centralBufferNode", "object", "uml", {ACTIVITY_DIAGRAM}, "A buffer for object tokens shared by activity nodes.", "UML 2.5.1 clause 15.7.8", category="object"),
    _node("dataStoreNode", "datastore", "uml", {ACTIVITY_DIAGRAM}, "A persistent store of object tokens.", "UML 2.5.1 clause 15.7.11", category="object"),
    _node("inputPin", "pin", "uml", {ACTIVITY_DIAGRAM}, "An action input pin.", "UML 2.5.1 clause 16.14.24", metamodel_form="property", category="pin"),
    _node("outputPin", "pin", "uml", {ACTIVITY_DIAGRAM}, "An action output pin.", "UML 2.5.1 clause 16.14.32", metamodel_form="property", category="pin"),
    _node("valuePin", "pin", "uml", {ACTIVITY_DIAGRAM}, "An input pin that supplies a value specification.", "UML 2.5.1 clause 16.14.58", metamodel_form="property", category="pin"),
    _node("actionInputPin", "pin", "uml", {ACTIVITY_DIAGRAM}, "An input pin whose value is produced by another action.", "UML 2.5.1 clause 16.14.4", metamodel_form="property", category="pin"),
    _node("activityPartition", "partition", "uml", {ACTIVITY_DIAGRAM}, "A swimlane grouping activity nodes by responsibility.", "UML 2.5.1 clause 15.7.7", category="group", is_container=True),
    _node("interruptibleActivityRegion", "region", "uml", {ACTIVITY_DIAGRAM}, "A region whose tokens can be terminated by an interrupting edge.", "UML 2.5.1 clause 15.7.19", category="group", is_container=True),
    _node("structuredActivityNode", "region", "uml", {ACTIVITY_DIAGRAM}, "An activity node containing a structured subgraph.", "UML 2.5.1 clause 16.14.55", category="group", is_container=True),
    _node("sequenceNode", "region", "uml", {ACTIVITY_DIAGRAM}, "A structured node executing contained nodes in order.", "UML 2.5.1 clause 16.14.51", category="group", is_container=True),
    _node("conditionalNode", "region", "uml", {ACTIVITY_DIAGRAM}, "A structured node choosing clauses by tests.", "UML 2.5.1 clause 16.14.15", category="group", is_container=True),
    _node("loopNode", "region", "uml", {ACTIVITY_DIAGRAM}, "A structured node repeatedly executing a body.", "UML 2.5.1 clause 16.14.30", category="group", is_container=True),
    _node("expansionRegion", "region", "uml", {ACTIVITY_DIAGRAM}, "A structured region executing over a collection.", "UML 2.5.1 clause 16.14.23", category="group", is_container=True),
    _node("expansionNode", "pin", "uml", {ACTIVITY_DIAGRAM}, "An input or output collection boundary of an expansion region.", "UML 2.5.1 clause 16.14.22", category="pin"),
    _node("actor", "actor", "uml", {USE_CASE_DIAGRAM}, "A role external to the subject that interacts with use cases.", "UML 2.5.1 clause 18.2.1", category="participant"),
    _node("useCase", "ellipse", "uml", {USE_CASE_DIAGRAM}, "A behavior offered by a subject to an actor.", "UML 2.5.1 clause 18.2.5", category="behavior"),
    _node("subject", "container", "uml", {USE_CASE_DIAGRAM}, "The classifier whose behavior the use cases describe.", "UML 2.5.1 clause 18.1.4", category="container", is_container=True),
    _node("block", "classifier-box", "sysml", {BDD_DIAGRAM}, "A modular system definition with structural and behavioral features.", "SysML 1.6 clause 8.3.2.4", metamodel_form="stereotype", category="definition"),
    _node("valueType", "classifier-box", "sysml", {BDD_DIAGRAM}, "A type for values, optionally carrying a unit and quantity kind.", "SysML 1.6 clause 8.3.2.15", metamodel_form="stereotype", category="definition"),
    _node("constraintBlock", "classifier-box", "sysml", {BDD_DIAGRAM}, "A reusable constraint expression with parameters.", "SysML 1.6 clause 10.3", metamodel_form="stereotype", category="definition"),
    _node("interfaceBlock", "classifier-box", "sysml", {BDD_DIAGRAM}, "A block defining interaction features, especially for proxy ports.", "SysML 1.6 clause 9.3.2.10", metamodel_form="stereotype", category="definition"),
    _node("enumeration", "classifier-box", "uml", {BDD_DIAGRAM}, "A data type whose values are named literals.", "UML 2.5.1 clause 10", category="definition"),
    _node("propertySpecificType", "classifier-box", "sysml", {BDD_DIAGRAM}, "A type definition local to one property.", "SysML 1.6 clause 8.3.2.14", metamodel_form="stereotype", category="definition"),
    _node("instanceSpecification", "classifier-box", "uml", {BDD_DIAGRAM}, "An instance-level specification displayed with an underlined name.", "SysML 1.6 clause 8.2.1", category="instance"),
    _node("unit", "classifier-box", "sysml", {BDD_DIAGRAM}, "A unit of measure from the SysML quantities library.", "SysML 1.6 clause 8.3.3.2", metamodel_form="model-library", category="quantity"),
    _node("quantityKind", "classifier-box", "sysml", {BDD_DIAGRAM}, "A kind of quantity measurable in compatible units.", "SysML 1.6 clause 8.3.3.2", metamodel_form="model-library", category="quantity"),
    _node("associationBlock", "classifier-box", "sysml", {BDD_DIAGRAM}, "A Block applied to an AssociationClass so a relationship can own features.", "SysML 1.6 clause 8.3.2.13", metamodel_form="stereotype", category="definition"),
    _node("port", "port", "uml", {BDD_DIAGRAM}, "A typed interaction point owned by a block or property.", "SysML 1.6 clause 9.3.1.6", metamodel_form="property", category="port"),
    _node("proxyPort", "port", "sysml", {BDD_DIAGRAM}, "A port exposing features of its owner or internal parts.", "SysML 1.6 clause 9.3.2.13", metamodel_form="stereotype", category="port"),
    _node("fullPort", "port", "sysml", {BDD_DIAGRAM}, "A port representing a separate element with its own features and behavior.", "SysML 1.6 clause 9.3.2.9", metamodel_form="stereotype", category="port"),
    _node("class", "classifier-box", "uml", {CUSTOM_DIAGRAM}, "A UML class.", "UML 2.5.1 clause 11", category="definition"),
    _node("interface", "classifier-box", "uml", {CUSTOM_DIAGRAM}, "A UML interface.", "UML 2.5.1 clause 10", category="definition"),
    _node("component", "classifier-box", "uml", {CUSTOM_DIAGRAM}, "A UML component.", "UML 2.5.1 clause 11", category="definition"),
    _node("package", "container", "uml", {CUSTOM_DIAGRAM}, "A UML package namespace.", "UML 2.5.1 clause 12", category="container", is_container=True),
    _node("requirement", "classifier-box", "sysml", {CUSTOM_DIAGRAM}, "A normative SysML text requirement with id and text.", "SysML 1.6 clause 16.3.2.5", metamodel_form="stereotype", category="requirement"),
    _edge("commentLink", "common", {ACTIVITY_DIAGRAM, USE_CASE_DIAGRAM, BDD_DIAGRAM}, "A dashed attachment from a comment to the element it annotates.", "UML 2.5.1 clause 7.2", category="annotation", dashed=True, target_marker="none"),
    _edge("controlFlow", "uml", {ACTIVITY_DIAGRAM}, "A flow carrying control tokens.", "UML 2.5.1 clause 15.7.9"),
    _edge("objectFlow", "uml", {ACTIVITY_DIAGRAM}, "A flow carrying object or data tokens.", "UML 2.5.1 clause 15.7.22"),
    _edge("exceptionHandler", "uml", {ACTIVITY_DIAGRAM}, "Transfers execution from a protected node to a handler body.", "UML 2.5.1 clause 15.7.13", category="handler"),
    _edge("association", "uml", {USE_CASE_DIAGRAM, BDD_DIAGRAM}, "A structural relationship whose ends carry roles, multiplicity, and navigability.", "UML 2.5.1 clause 11", target_marker="none"),
    _edge("composition", "sysml", {BDD_DIAGRAM}, "An owned whole/part relationship directed from the part to the whole.", "SysML 1.6 clause 8.3.2.4", target_marker="diamond_filled"),
    _edge("generalization", "uml", {USE_CASE_DIAGRAM, BDD_DIAGRAM}, "An is-a relationship from a specific element to its general parent.", "UML 2.5.1 clause 9", target_marker="triangle"),
    _edge("include", "uml", {USE_CASE_DIAGRAM}, "A base use case unconditionally includes another use case.", "UML 2.5.1 clause 18.2.4", dashed=True),
    _edge("extend", "uml", {USE_CASE_DIAGRAM}, "An extending use case conditionally adds behavior to a base use case.", "UML 2.5.1 clause 18.2.2", dashed=True),
    _edge("dependency", "uml", {BDD_DIAGRAM, CUSTOM_DIAGRAM}, "A client depends on a supplier.", "UML 2.5.1 clause 7", dashed=True),
    _edge("containment", "sysml", {BDD_DIAGRAM}, "Namespace containment from a block to a nested definition.", "SysML 1.6 clause 8.2.1", source_marker="crosshair", target_marker="none"),
    _edge("participantPropertyLink", "sysml", {BDD_DIAGRAM}, "Links an association-block participant property to an association end.", "SysML 1.6 clause 8.3.2.13", target_marker="none"),
    _edge("connectorPropertyLink", "sysml", {BDD_DIAGRAM}, "A dotted callout from a connector to the property representing it.", "SysML 1.6 clause 8.3.2.7", dashed=True, target_marker="none"),
    _edge("realization", "uml", {CUSTOM_DIAGRAM}, "A client implements a supplier specification.", "UML 2.5.1 clause 7", dashed=True, target_marker="triangle"),
]

_ACTION_KINDS = {
    "opaqueAction": "A behavior expressed in an implementation-dependent language.",
    "callBehaviorAction": "Invokes a behavior directly.",
    "callOperationAction": "Invokes an operation on a target object.",
    "broadcastSignalAction": "Broadcasts a signal to potential receivers.",
    "sendSignalAction": "Sends a signal to a target.",
    "sendObjectAction": "Sends an object to a target.",
    "acceptEventAction": "Waits for one or more events, including time events.",
    "acceptCallAction": "Accepts an operation call and exposes reply information.",
    "replyAction": "Replies to a previously accepted call.",
    "createObjectAction": "Creates an instance of a classifier.",
    "destroyObjectAction": "Destroys a target object.",
    "readSelfAction": "Returns the context object of a behavior.",
    "readExtentAction": "Returns the current instances of a classifier.",
    "readIsClassifiedObjectAction": "Tests whether an object is classified by a classifier.",
    "reclassifyObjectAction": "Changes the classifiers of an object.",
    "startClassifierBehaviorAction": "Starts a classifier behavior.",
    "startObjectBehaviorAction": "Starts an object behavior.",
    "addStructuralFeatureValueAction": "Adds a value to a structural feature.",
    "removeStructuralFeatureValueAction": "Removes a value from a structural feature.",
    "clearStructuralFeatureAction": "Clears all values of a structural feature.",
    "readStructuralFeatureAction": "Reads a structural feature value.",
    "writeStructuralFeatureAction": "Writes a structural feature value.",
    "addVariableValueAction": "Adds a value to a variable.",
    "removeVariableValueAction": "Removes a value from a variable.",
    "clearVariableAction": "Clears a variable.",
    "readVariableAction": "Reads a variable.",
    "writeVariableAction": "Writes a variable.",
    "createLinkAction": "Creates a link between objects.",
    "createLinkObjectAction": "Creates a link object for an association class.",
    "destroyLinkAction": "Destroys a link.",
    "readLinkAction": "Reads links matching supplied end values.",
    "readLinkObjectEndAction": "Reads an end object from a link object.",
    "readLinkObjectEndQualifierAction": "Reads a qualifier value from a link-object end.",
    "clearAssociationAction": "Destroys all links of an association involving an object.",
    "raiseExceptionAction": "Raises an exception.",
    "reduceAction": "Reduces a collection using a reducer behavior.",
    "testIdentityAction": "Tests two values for identity.",
    "unmarshallAction": "Extracts values from a structured object.",
    "valueSpecificationAction": "Evaluates and returns a value specification.",
}

for _semantic_type, _description in _ACTION_KINDS.items():
    _primitive = "send-signal" if _semantic_type in {"broadcastSignalAction", "sendSignalAction"} else "accept-event" if _semantic_type in {"acceptEventAction", "acceptCallAction"} else "rounded-rect"
    _ELEMENTS.append(_node(_semantic_type, _primitive, "uml", {ACTIVITY_DIAGRAM}, _description, "UML 2.5.1 clause 16", category="action"))

_AUTHORABLE_NODES = {
    ACTIVITY_DIAGRAM: frozenset({
        "initialNode", "opaqueAction", "decisionNode", "mergeNode", "forkNode",
        "joinNode", "activityFinalNode", "note",
    }),
    USE_CASE_DIAGRAM: frozenset({"actor", "useCase", "subject", "note"}),
    BDD_DIAGRAM: frozenset({"block", "note"}),
    CUSTOM_DIAGRAM: frozenset({"class", "interface", "component", "package", "requirement"}),
}
_AUTHORABLE_EDGES = {
    ACTIVITY_DIAGRAM: frozenset({"controlFlow", "commentLink"}),
    USE_CASE_DIAGRAM: frozenset({"association", "generalization", "include", "extend", "commentLink"}),
    BDD_DIAGRAM: frozenset({"association", "composition", "generalization", "dependency", "commentLink"}),
    CUSTOM_DIAGRAM: frozenset({"dependency", "realization"}),
}
_ELEMENTS = [
    replace(
        element,
        authorable_in=frozenset(
            diagram_type
            for diagram_type in element.valid_in
            if element.semantic_type in (_AUTHORABLE_NODES if element.kind == "node" else _AUTHORABLE_EDGES)[diagram_type]
        ),
    )
    for element in _ELEMENTS
]

ELEMENT_CATALOG: Dict[str, ElementSpec] = {e.semantic_type: e for e in _ELEMENTS}


def allowed_node_semantic_types(diagram_type: str) -> FrozenSet[str]:
    """Node semantic types a diagram type allows (its subset of the catalog)."""
    return frozenset(
        e.semantic_type for e in ELEMENT_CATALOG.values() if e.kind == "node" and diagram_type in e.valid_in
    )


def allowed_edge_semantic_types(diagram_type: str) -> FrozenSet[str]:
    """Edge semantic types a diagram type allows (its subset of the catalog)."""
    return frozenset(
        e.semantic_type for e in ELEMENT_CATALOG.values() if e.kind == "edge" and diagram_type in e.valid_in
    )


def authorable_node_semantic_types(diagram_type: str) -> FrozenSet[str]:
    """Node semantic types exposed for new authoring and generation."""
    return frozenset(
        e.semantic_type for e in ELEMENT_CATALOG.values()
        if e.kind == "node" and (bool(e.authorable_in) if diagram_type == CUSTOM_DIAGRAM else diagram_type in e.authorable_in)
    )


def authorable_edge_semantic_types(diagram_type: str) -> FrozenSet[str]:
    """Edge semantic types exposed for new authoring and generation."""
    return frozenset(
        e.semantic_type for e in ELEMENT_CATALOG.values()
        if e.kind == "edge" and (bool(e.authorable_in) if diagram_type == CUSTOM_DIAGRAM else diagram_type in e.authorable_in)
    )


def all_node_semantic_types() -> FrozenSet[str]:
    """Every node semantic type in the catalog (the ``custom`` canvas allows all)."""
    return frozenset(e.semantic_type for e in ELEMENT_CATALOG.values() if e.kind == "node")


def all_edge_semantic_types() -> FrozenSet[str]:
    """Every edge semantic type in the catalog (the ``custom`` canvas allows all)."""
    return frozenset(e.semantic_type for e in ELEMENT_CATALOG.values() if e.kind == "edge")


def node_primitive(semantic_type: str) -> Optional[str]:
    """The render primitive for a node semantic type, or ``None`` if unknown."""
    spec = ELEMENT_CATALOG.get(semantic_type)
    return spec.primitive if spec and spec.kind == "node" else None


def container_semantic_types() -> FrozenSet[str]:
    """Node semantic types that act as containers (keep a child's ``parentId``)."""
    return frozenset(e.semantic_type for e in ELEMENT_CATALOG.values() if e.is_container)


def dashed_edge_semantic_types() -> FrozenSet[str]:
    """Edge semantic types drawn with a dashed line."""
    return frozenset(e.semantic_type for e in ELEMENT_CATALOG.values() if e.kind == "edge" and e.dashed)
