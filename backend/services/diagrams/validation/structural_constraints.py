"""Per-type structural constraints — a deterministic "structural critic".

LADEX-informed (see ``docs/02-design-and-features/04-generation-design.md``): structural
correctness is checked **algorithmically, not by an LLM**. These rules express each MVP
diagram type's well-formedness *beyond* the generic graph/vocabulary checks. For activity diagrams they are the UML activity-diagram rules (exactly one
initial node, at least one end node, a start with no incoming and an end with no outgoing
flow, guarded decision branches, reachability from the start); the use-case (UML) and BDD
(SysML) rules are derived and kept **deliberately conservative** so they never false-positive
on well-formed diagrams.

Consumers:
- ``DiagramValidationService`` (Layer 4): surfaced as advisory ``structural_constraint``
  warnings for **every** diagram (keyed off ``diagramType``; a ``custom`` board has no rules), and
- the direct/context generation critique/refine loops, which read those findings back from the
  ``ValidationResult`` and hard-block if any remain after the refine budget.

It operates on the **canonical** diagram dict: a node's semantic type is
``node["data"]["semanticType"]`` and a decision branch's guard is the edge's top-level
``label``. Validation surfaces these findings only as **advisory warnings** (never a runtime
save-blocker), so freeform ``custom`` boards and UI saves are unaffected; only generation
pipelines escalate them to a hard gate.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, NamedTuple


class Violation(NamedTuple):
    """A single structural-rule violation: a stable ``rule`` id + a human message."""

    rule: str
    message: str


def _data(item: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    data = item.get("data")
    return data if isinstance(data, dict) else {}


def _sem(item: Dict[str, Any]) -> Any:
    return _data(item).get("semanticType")


def _ids_of(nodes: List[Dict[str, Any]], semantic: str) -> List[Any]:
    return [n.get("id") for n in nodes if _sem(n) == semantic]


def _guard(edge: Dict[str, Any]) -> str:
    guard = _data(edge).get("guard")
    if isinstance(guard, str) and guard.strip():
        return guard.strip()
    label = edge.get("label")
    return label.strip() if isinstance(label, str) else ""


def _reachable(starts: List[Any], edges: List[Dict[str, Any]]) -> set:
    adjacency: Dict[Any, List[Any]] = {}
    for edge in edges:
        adjacency.setdefault(edge.get("source"), []).append(edge.get("target"))
    seen: set = set()
    stack = list(starts)
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, []))
    return seen


# ---------------------------------------------------------------------------
# Activity diagrams — UML activity-diagram rules (LADEX SC1–SC6)
# ---------------------------------------------------------------------------


def _check_activity(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Violation]:
    violations: List[Violation] = []
    starts = _ids_of(nodes, "initialNode")
    ends = _ids_of(nodes, "activityFinalNode")
    decisions = _ids_of(nodes, "decisionNode")
    flow_edges = [
        edge for edge in edges
        if _sem(edge) in {"controlFlow", "objectFlow", "exceptionHandler"}
    ]

    if len(starts) != 1:
        violations.append(
            Violation("single_start", f"must have exactly one start node (found {len(starts)})")
        )
    if not ends:
        violations.append(Violation("has_end", "must have at least one end node"))

    incoming = {e.get("target") for e in flow_edges}
    outgoing: Dict[Any, List[Dict[str, Any]]] = {}
    for edge in flow_edges:
        outgoing.setdefault(edge.get("source"), []).append(edge)

    for start in starts:
        if start in incoming:
            violations.append(Violation("start_no_incoming", f"start node {start!r} must have no incoming flow"))
    for end in ends:
        if end in outgoing:
            violations.append(Violation("end_no_outgoing", f"end node {end!r} must have no outgoing flow"))

    for decision in decisions:
        branches = outgoing.get(decision, [])
        if len(branches) < 2:
            violations.append(
                Violation("decision_branches", f"decision node {decision!r} must have at least two outgoing flows")
            )
        unguarded = [e.get("id") for e in branches if not _guard(e)]
        if unguarded:
            violations.append(
                Violation("decision_guards", f"decision node {decision!r} has unlabelled (unguarded) branch(es): {unguarded}")
            )

    # Fork/join (UML 2.5.1): a fork splits one flow into concurrent flows (>=2 out);
    # a join synchronises concurrent flows back (>=2 in). Kept conservative.
    incoming_count: Dict[Any, int] = {}
    incoming_sources: Dict[Any, set] = {}
    for edge in flow_edges:
        target = edge.get("target")
        incoming_count[target] = incoming_count.get(target, 0) + 1
        incoming_sources.setdefault(target, set()).add(edge.get("source"))
    for fork in _ids_of(nodes, "forkNode"):
        if len({edge.get("target") for edge in outgoing.get(fork, [])}) < 2:
            violations.append(
                Violation("fork_outgoing", f"fork node {fork!r} must have outgoing flows to at least two distinct targets")
            )
    for fork in _ids_of(nodes, "forkNode"):
        if incoming_count.get(fork, 0) != 1:
            violations.append(Violation("fork_incoming", f"fork node {fork!r} must have exactly one incoming flow"))
    for join in _ids_of(nodes, "joinNode"):
        if len(incoming_sources.get(join, set())) < 2:
            violations.append(
                Violation("join_incoming", f"join node {join!r} must have incoming flows from at least two distinct sources")
            )
        if len(outgoing.get(join, [])) != 1:
            violations.append(Violation("join_outgoing", f"join node {join!r} must have exactly one outgoing flow"))
    for merge in _ids_of(nodes, "mergeNode"):
        if incoming_count.get(merge, 0) < 2:
            violations.append(Violation("merge_incoming", f"merge node {merge!r} must have at least two incoming flows"))
        if len(outgoing.get(merge, [])) > 1:
            violations.append(Violation("merge_outgoing", f"merge node {merge!r} may have at most one outgoing flow"))
    action_ids = {
        n.get("id") for n in nodes
        if _sem(n) and (_sem(n).endswith("Action") or _sem(n) == "opaqueAction")
    }
    for node in nodes:
        if _sem(node) in {"inputPin", "outputPin", "valuePin", "actionInputPin"} and node.get("parentId") not in action_ids:
            violations.append(Violation("pin_owner", f"pin {node.get('id')!r} must be owned by an action"))

    if len(starts) == 1:
        reachable = _reachable(starts, flow_edges)
        non_flow_symbols = {
            "note", "activityParameterNode", "inputPin", "outputPin", "valuePin", "actionInputPin", "expansionNode",
            "activityPartition", "interruptibleActivityRegion", "structuredActivityNode",
            "sequenceNode", "conditionalNode", "loopNode", "expansionRegion",
        }
        unreachable = [n.get("id") for n in nodes if _sem(n) not in non_flow_symbols and n.get("id") not in reachable]
        if unreachable:
            violations.append(
                Violation("reachable_from_start", f"node(s) not reachable from the start node: {unreachable}")
            )
    return violations


# ---------------------------------------------------------------------------
# Use-case diagrams — derived UML rules (conservative)
# ---------------------------------------------------------------------------

#: The half-sentence the ``extend_has_location`` violation is built from, and the whole
#: sentence the authoring contract publishes on the two fields it governs.
#:
#: Both live here, beside the check, because they were previously only in the check. The
#: draft schema calls ``extensionLocations`` and ``extensionPoints`` optional, so a host
#: that could not find an extension point in the source omitted both — obeying the
#: workflow's *"prefer omission to a guess"* — and was then refused for naming none. It
#: complied by inventing a point name the source never uses. A rule that turns an
#: honest omission into a fabrication has to be stated where the field is read, and
#: stated from the same string that enforces it so the two cannot drift.
EXTEND_LOCATION_REQUIREMENT = "must name an extension location"

#: What the contract prints. Says where each half goes, because the rule spans two
#: fields on two different objects.
EXTEND_LOCATION_RULE = (
    f"An `extend` relationship {EXTEND_LOCATION_REQUIREMENT}: name it in the "
    "relationship's `extensionLocations`, and declare the same text in the base use "
    "case's `extensionPoints`. UML has no unnamed extension — the point where the "
    "extension attaches is part of what the relationship says. If the source does not "
    "show one, do not invent a name: drop the `extend`, and say what you could not "
    "establish in your reply to the user."
)


def _check_use_case(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Violation]:
    violations: List[Violation] = []
    use_cases = set(_ids_of(nodes, "useCase"))
    actors = set(_ids_of(nodes, "actor"))
    subjects = set(_ids_of(nodes, "subject"))
    if not use_cases:
        violations.append(Violation("has_use_case", "must contain at least one use case"))
    if not actors:
        violations.append(Violation("has_actor", "must contain at least one actor"))
    for edge in edges:
        # Include and extend are distinct UML relationships with opposite source/target roles.
        if _sem(edge) in ("include", "extend"):
            if edge.get("source") not in use_cases or edge.get("target") not in use_cases:
                violations.append(
                    Violation(
                        "include_extend_between_use_cases",
                        f"{_sem(edge)} edge {edge.get('id')!r} must connect two use cases",
                    )
                )
            if _sem(edge) == "extend" and edge.get("target") in use_cases:
                raw_locations = _data(edge).get("extensionLocations")
                edge_locations = [value for value in raw_locations if isinstance(value, str)] if isinstance(raw_locations, list) else []
                base = next((node for node in nodes if node.get("id") == edge.get("target")), {})
                raw_available = _data(base).get("extensionPoints")
                available = {value for value in raw_available if isinstance(value, str)} if isinstance(raw_available, list) else set()
                if not edge_locations:
                    violations.append(
                        Violation(
                            "extend_has_location",
                            f"extend edge {edge.get('id')!r} {EXTEND_LOCATION_REQUIREMENT}",
                        )
                    )
                elif not set(edge_locations) <= available:
                    violations.append(
                        Violation("extend_location_exists", f"extend edge {edge.get('id')!r} names an unknown extension point")
                    )
        elif _sem(edge) == "association":
            source, target = edge.get("source"), edge.get("target")
            if not ((source in actors and target in use_cases) or (source in use_cases and target in actors)):
                violations.append(
                    Violation(
                        "association_actor_use_case",
                        f"association edge {edge.get('id')!r} must connect an actor and a use case",
                    )
                )
        elif _sem(edge) == "generalization":
            source, target = edge.get("source"), edge.get("target")
            both_use_cases = source in use_cases and target in use_cases
            both_actors = source in actors and target in actors
            if not (both_use_cases or both_actors):
                violations.append(
                    Violation(
                        "generalization_same_kind",
                        f"generalization edge {edge.get('id')!r} must connect two use cases or two actors",
                    )
                )
    for node in nodes:
        if subjects and _sem(node) == "useCase" and node.get("parentId") not in subjects:
            violations.append(
                Violation(
                    "use_case_in_subject",
                    f"use case {node.get('id')!r} must be contained by a displayed subject",
                )
            )
    return violations


# ---------------------------------------------------------------------------
# BDD diagrams — derived SysML rules (conservative)
# ---------------------------------------------------------------------------


def _check_bdd(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Violation]:
    violations: List[Violation] = []
    kind_by_id = {n.get("id"): _sem(n) for n in nodes}
    if "block" not in kind_by_id.values():
        violations.append(Violation("has_block", "must contain at least one block definition"))
    owner_kinds = {
        "block", "interfaceBlock", "associationBlock", "propertySpecificType",
        "port", "proxyPort", "fullPort",
    }
    for node in nodes:
        if _sem(node) in {"port", "proxyPort", "fullPort"}:
            owner = node.get("parentId")
            if owner not in kind_by_id or kind_by_id.get(owner) not in owner_kinds:
                violations.append(
                    Violation("port_owner", f"port {node.get('id')!r} must be owned by a valid block or port context")
                )
            if _sem(node) == "proxyPort":
                port = _data(node).get("port")
                if not (isinstance(port, dict) and port.get("type")):
                    violations.append(
                        Violation("proxy_port_type", f"proxy port {node.get('id')!r} must have an interface-block type")
                    )
    for edge in edges:
        if _sem(edge) == "generalization":
            source_kind = kind_by_id.get(edge.get("source"))
            target_kind = kind_by_id.get(edge.get("target"))
            if source_kind is None or target_kind is None or source_kind != target_kind:
                violations.append(
                    Violation(
                        "generalization_same_kind",
                        f"generalization edge {edge.get('id')!r} must connect definitions of the same semantic type",
                    )
                )
        if _sem(edge) == "composition":
            source_kind = kind_by_id.get(edge.get("source"))
            target_kind = kind_by_id.get(edge.get("target"))
            if source_kind != "block" or target_kind != "block":
                violations.append(
                    Violation("composition_blocks", f"composition edge {edge.get('id')!r} must connect a part Block to a whole Block")
                )
        if _sem(edge) == "association":
            data = _data(edge)
            source_end = data.get("sourceEnd") if isinstance(data.get("sourceEnd"), dict) else {}
            target_end = data.get("targetEnd") if isinstance(data.get("targetEnd"), dict) else {}
            source_aggregation = source_end.get("aggregation", "none")
            target_aggregation = target_end.get("aggregation", "none")
            if source_aggregation != "none" and target_aggregation != "none":
                violations.append(
                    Violation("single_aggregate_end", f"association edge {edge.get('id')!r} may aggregate at only one end")
                )
    return violations


_CHECKERS: Dict[str, Callable[[List[Dict[str, Any]], List[Dict[str, Any]]], List[Violation]]] = {
    "activity_diagram": _check_activity,
    "use_case_diagram": _check_use_case,
    "bdd_diagram": _check_bdd,
}


_DESCRIPTIONS: Dict[str, str] = {
    "activity_diagram": (
        "- Exactly one initialNode; at least one activityFinalNode.\n"
        "- The initialNode has no incoming flow; activityFinalNode nodes have no outgoing flow.\n"
        "- Every decisionNode has at least two outgoing flows, each carrying a guard.\n"
        "- A forkNode has exactly one incoming flow and outgoing flows to at least two distinct targets; a joinNode has incoming flows from at least two distinct sources and exactly one outgoing.\n"
        "- A mergeNode has at least two incoming and at most one outgoing flow; every pin is owned by an action.\n"
        "- Every flow-participating node is reachable from the initialNode."
    ),
    "use_case_diagram": (
        "- Include at least one actor and useCase; when a subject is displayed, every useCase is contained by it.\n"
        "- `include` and `extend` connect two use cases; extend names a declared extension point.\n"
        "- `generalization` connects two use cases or two actors of the same kind.\n"
        "- `association` connects an actor to a use case."
    ),
    "bdd_diagram": (
        "- Include at least one block definition.\n"
        "- `association`, `composition`, `generalization`, and `dependency` each require two existing Block endpoints.\n"
        "- `generalization` connects a child source Block to a parent target Block.\n"
        "- `composition` connects a part source Block to a whole target Block.\n"
        "- `dependency` connects a dependent source Block to a supplier target Block.\n"
        "- `association` represents plain/reference structure between Blocks.\n"
        "- Note attachments use `commentLink`; `commentLink` is excluded from structural Block-endpoint and connectivity rules."
    ),
}


def check_structural_constraints(diagram: Dict[str, Any], diagram_type: str) -> List[Violation]:
    """Return the structural-rule violations for *diagram* (empty when well-formed).

    Unknown diagram types yield no violations.
    """
    checker = _CHECKERS.get(diagram_type)
    if checker is None:
        return []
    raw_nodes = diagram.get("nodes") if isinstance(diagram.get("nodes"), list) else []
    raw_edges = diagram.get("edges") if isinstance(diagram.get("edges"), list) else []
    nodes = [node for node in raw_nodes if isinstance(node, dict)]
    edges = [edge for edge in raw_edges if isinstance(edge, dict)]
    return checker(nodes, edges)


def describe(diagram_type: str) -> str:
    """Return a short, human-readable rule list for *diagram_type* (for prompts)."""
    return _DESCRIPTIONS.get(diagram_type, "")
