"""Internal deterministic phases shared by diagram generation orchestrators.

One :class:`GenerationPipeline` preparation attempt conforms a logical diagram,
lays it out, assembles canonical JSON, validates it, and extracts structural
findings. LLM calls, retries, path resolution, persistence, and rendering remain
with the mode-specific orchestrators.
"""

from __future__ import annotations

import copy
import math
import re
from typing import Any, Dict, List, Mapping, Optional, Tuple

from django.utils import timezone

from services.diagrams.catalog.constants import TYPE_ROUTE_MODE, bdd_block_min_size, use_case_min_size
from services.diagrams.catalog.diagram_shapes import Diagram, LogicalDiagram
from services.diagrams.catalog.diagram_types import get_type_profile
from services.diagrams.catalog.element_catalog import (
    ELEMENT_CATALOG,
    container_semantic_types,
    dashed_edge_semantic_types,
    node_primitive,
)
from services.diagrams.validation.validation_contract import (
    ValidationCode,
    ValidationIssue,
    ValidationResult,
)
from services.diagrams.rendering.diagram_render_service import EDGE_DEFAULTS, STYLE_DEFAULTS
from services.diagrams.layout.diagram_layout_service import (
    DiagramLayoutService,
    LayoutEdge,
    LayoutInputNode,
)

# Per-element facts come from the shared element catalog—the same values used by validation
# and rendering. Per-type coerce defaults live on the type profile.
_DASHED_EDGE_SEMANTICS = dashed_edge_semantic_types()
# Ownership is checked by exact semantic role: ordinary children need a container, pins need
# an action/expansion-region owner, and ports need a valid block/port context.
_CONTAINER_SEMANTIC_TYPES = container_semantic_types()
_GENERATION_METADATA_KEYS = frozenset({"authority", "assurance", "evidence", "requests"})


# ---------------------------------------------------------------------------
# Conform (vocabulary + structural only)
# ---------------------------------------------------------------------------


def _sanitize_node_id(raw: Any, fallback: str) -> str:
    """Turn an LLM-provided node id into a safe identifier (alphanumeric + ``_-``).

    Spaces/punctuation become ``_`` so ids are clean React Flow / edge identifiers.
    Falls back to *fallback* when nothing usable remains.
    """
    if not isinstance(raw, (str, int)):
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", str(raw)).strip("_-")
    return cleaned or fallback


def _clean_text_list(raw: Any) -> List[str]:
    return [str(value).strip() for value in raw if isinstance(value, (str, int, float)) and str(value).strip()] if isinstance(raw, list) else []


def _clean_multiplicity(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    lower, upper = raw.get("lower"), raw.get("upper")
    lower_is_int = isinstance(lower, int) and not isinstance(lower, bool)
    upper_is_int = isinstance(upper, int) and not isinstance(upper, bool)
    if not lower_is_int or lower < 0 or not (upper == "*" or upper_is_int and upper >= lower):
        return None
    return {"lower": lower, "upper": upper}


def _clean_parameters(raw: Any) -> List[Dict[str, Any]]:
    """Accept both shapes a parameter arrives in, and lose neither.

    The canonical form is an object — `{name, direction, type, multiplicity, default}` —
    which is what the editor produces. The **draft** schema asks a host for a plain string,
    because `"mode: Mode"` is what an author has in front of them.

    This only accepted the object, so every parameter a host authored was dropped on the
    floor: the draft validated, `diagram_create` succeeded, and the saved diagram had no
    parameters at all. Accepted, then silently discarded, is the worst of the three
    possible behaviours — worse than refusing it, because the author believes it landed.
    """
    out = []
    for value in raw if isinstance(raw, list) else []:
        if isinstance(value, str) and value.strip():
            # `"mode: Mode"` carries the type after a colon; splitting keeps the two
            # apart so the canonical object is as informative as the string was.
            name, _, type_name = value.partition(":")
            item: Dict[str, Any] = {"name": name.strip() or value.strip(), "direction": "in"}
            if type_name.strip():
                item["type"] = type_name.strip()
            out.append(item)
            continue
        if not isinstance(value, dict) or not isinstance(value.get("name"), str) or not value["name"].strip():
            continue
        direction = value.get("direction") if value.get("direction") in {"in", "out", "inout", "return"} else "in"
        item: Dict[str, Any] = {"name": value["name"].strip(), "direction": direction}
        if isinstance(value.get("type"), str) and value["type"].strip():
            item["type"] = value["type"].strip()
        multiplicity = _clean_multiplicity(value.get("multiplicity"))
        if multiplicity:
            item["multiplicity"] = multiplicity
        if value.get("default") is not None:
            item["default"] = value["default"]
        out.append(item)
    return out


def _clean_property(value: Any) -> Optional[Dict[str, Any]]:
    allowed_kinds = {"part", "reference", "value", "constraint", "flow"}
    if not isinstance(value, dict) or value.get("kind") not in allowed_kinds:
        return None
    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        return None
    item: Dict[str, Any] = {"kind": value["kind"], "name": name.strip()}
    if isinstance(value.get("type"), str) and value["type"].strip():
        item["type"] = value["type"].strip()
    multiplicity = _clean_multiplicity(value.get("multiplicity"))
    if multiplicity:
        item["multiplicity"] = multiplicity
    if value.get("default") is not None:
        item["default"] = value["default"]
    if value["kind"] == "flow" and value.get("direction") in {"in", "out", "inout"}:
        item["direction"] = value["direction"]
    for key in ("isReadOnly", "isOrdered", "isUnique", "isDerived"):
        if isinstance(value.get(key), bool):
            item[key] = value[key]
    return item


def _clean_properties(raw: Any) -> List[Dict[str, Any]]:
    properties = []
    for value in raw if isinstance(raw, list) else []:
        item = _clean_property(value)
        if item:
            properties.append(item)
    return properties


def _clean_features(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    out: Dict[str, Any] = {}
    properties = _clean_properties(raw.get("properties"))
    if properties:
        out["properties"] = properties
    operations = []
    for value in raw.get("operations") if isinstance(raw.get("operations"), list) else []:
        if not isinstance(value, dict) or not isinstance(value.get("name"), str) or not value["name"].strip():
            continue
        item = {"name": value["name"].strip()}
        parameters = _clean_parameters(value.get("parameters"))
        if parameters:
            item["parameters"] = parameters
        if isinstance(value.get("returnType"), str) and value["returnType"].strip():
            item["returnType"] = value["returnType"].strip()
        for key in ("isAbstract", "isStatic", "isQuery"):
            if isinstance(value.get(key), bool):
                item[key] = value[key]
        operations.append(item)
    if operations:
        out["operations"] = operations
    receptions = _clean_text_list(raw.get("receptions"))
    if receptions:
        out["receptions"] = receptions
    constraints = []
    for value in raw.get("constraints") if isinstance(raw.get("constraints"), list) else []:
        if not isinstance(value, dict) or not isinstance(value.get("expression"), str) or not value["expression"].strip():
            continue
        item = {"expression": value["expression"].strip()}
        if isinstance(value.get("name"), str) and value["name"].strip():
            item["name"] = value["name"].strip()
        constraints.append(item)
    if constraints:
        out["constraints"] = constraints
    literals = _clean_text_list(raw.get("literals"))
    if literals:
        out["literals"] = literals
    return out or None


def _clean_stereotypes(raw: Any) -> List[Dict[str, Any]]:
    out = []
    for value in raw if isinstance(raw, list) else []:
        if isinstance(value, str) and value.strip():
            out.append({"name": value.strip()})
        elif isinstance(value, dict) and isinstance(value.get("name"), str) and value["name"].strip():
            item: Dict[str, Any] = {"name": value["name"].strip()}
            if isinstance(value.get("properties"), dict) and value["properties"]:
                item["properties"] = dict(value["properties"])
            out.append(item)
    return out


def _clean_port(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    out: Dict[str, Any] = {}
    if isinstance(raw.get("type"), str) and raw["type"].strip():
        out["type"] = raw["type"].strip()
    if raw.get("side") in {"top", "right", "bottom", "left"}:
        out["side"] = raw["side"]
    offset = raw.get("offset")
    if isinstance(offset, (int, float)) and not isinstance(offset, bool) and math.isfinite(offset):
        out["offset"] = max(0.0, min(1.0, float(offset)))
    for key in ("isConjugated", "isBehavior"):
        if isinstance(raw.get(key), bool):
            out[key] = raw[key]
    for source, target in (("providedFeatures", "providedFeatures"), ("requiredFeatures", "requiredFeatures")):
        values = _clean_text_list(raw.get(source))
        if values:
            out[target] = values
    return out or None


def _clean_item_flows(raw: Any) -> List[Dict[str, Any]]:
    out = []
    for value in raw if isinstance(raw, list) else []:
        if not isinstance(value, dict) or value.get("direction") not in {"sourceToTarget", "targetToSource"}:
            continue
        item = value.get("item")
        if not isinstance(item, str) or not item.strip():
            continue
        cleaned = {"direction": value["direction"], "item": item.strip()}
        if isinstance(value.get("itemProperty"), str) and value["itemProperty"].strip():
            cleaned["itemProperty"] = value["itemProperty"].strip()
        out.append(cleaned)
    return out


def _clean_end(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    out: Dict[str, Any] = {}
    for key in ("role", "type"):
        if isinstance(raw.get(key), str) and raw[key].strip():
            out[key] = raw[key].strip()
    multiplicity = _clean_multiplicity(raw.get("multiplicity"))
    if multiplicity:
        out["multiplicity"] = multiplicity
    if isinstance(raw.get("navigable"), bool):
        out["navigable"] = raw["navigable"]
    if raw.get("aggregation") in {"none", "shared", "composite"}:
        out["aggregation"] = raw["aggregation"]
    for key in ("isOrdered", "isUnique"):
        if isinstance(raw.get(key), bool):
            out[key] = raw[key]
    qualifiers = _clean_properties(raw.get("qualifiers"))
    if qualifiers:
        out["qualifiers"] = qualifiers
    property_path = _clean_text_list(raw.get("propertyPath"))
    if property_path:
        out["propertyPath"] = property_path
    return out or None


def conform_logical(logical: Dict[str, Any], diagram_type: str) -> LogicalDiagram:
    """Clean an LLM logical diagram to the type vocabulary + structural integrity.

    Coerces off-vocabulary semantic types to a per-type default, ensures unique
    node ids and non-empty labels, remaps/drops ``parentId`` references, and drops
    edges whose endpoints don't exist. Returns a new dict (no input mutation).
    """
    profile = get_type_profile(diagram_type)
    allowed_nodes = profile.allowed_node_semantic_types
    allowed_edges = profile.allowed_edge_semantic_types
    default_node = profile.default_node_semantic_type
    default_edge = profile.default_edge_semantic_type

    raw_nodes = logical.get("nodes") if isinstance(logical.get("nodes"), list) else []
    raw_edges = logical.get("edges") if isinstance(logical.get("edges"), list) else []

    seen_ids: set[str] = set()
    id_map: Dict[str, str] = {}
    nodes: List[Dict[str, Any]] = []
    parents: List[Optional[str]] = []

    for i, n in enumerate(raw_nodes):
        if not isinstance(n, dict):
            continue
        orig = n.get("id")
        nid = _sanitize_node_id(orig, f"node_{i + 1}")
        base, k = nid, 2
        while nid in seen_ids:
            nid = f"{base}_{k}"
            k += 1
        seen_ids.add(nid)
        # First occurrence of an original id wins for edge remapping; a later
        # duplicate is renamed but not remapped onto (it would be ambiguous).
        if isinstance(orig, (str, int)) and str(orig) not in id_map:
            id_map[str(orig)] = nid

        sem = n.get("semanticType")
        if sem not in allowed_nodes:
            sem = default_node
        label = n.get("label")
        if not (isinstance(label, str) and label.strip()):
            label = str(sem).replace("_", " ").title()

        node_out: Dict[str, Any] = {"id": nid, "semanticType": sem, "label": label.strip()}
        stereotype = n.get("stereotype")
        if sem == "block" and isinstance(stereotype, str) and stereotype.strip():
            node_out["stereotype"] = stereotype.strip()
        features = _clean_features(n.get("features"))
        if features:
            node_out["features"] = features
        extension_points = _clean_text_list(n.get("extensionPoints"))
        if extension_points and sem == "useCase":
            node_out["extensionPoints"] = extension_points
        applied = _clean_stereotypes(n.get("appliedStereotypes"))
        if applied:
            node_out["appliedStereotypes"] = applied
        port = _clean_port(n.get("port"))
        if port and node_primitive(sem) == "port":
            node_out["port"] = port
        if isinstance(n.get("isAbstract"), bool):
            node_out["isAbstract"] = n["isAbstract"]
        for key in ("unit", "quantityKind", "constraintExpression", "joinSpec"):
            if isinstance(n.get(key), str) and n[key].strip():
                node_out[key] = n[key].strip()
        parameters = _clean_parameters(n.get("constraintParameters"))
        if parameters and sem in {"block", "constraintBlock"}:
            node_out["constraintParameters"] = parameters
        if "origin" in n:
            node_out["origin"] = copy.deepcopy(n["origin"])
        nodes.append(node_out)
        parent = n.get("parentId")
        parents.append(str(parent).strip() if isinstance(parent, (str, int)) and str(parent).strip() else None)

    valid_ids = {n["id"] for n in nodes}
    container_ids = {n["id"] for n in nodes if n["semanticType"] in _CONTAINER_SEMANTIC_TYPES}
    port_owner_ids = {
        n["id"] for n in nodes
        if n["semanticType"] in {
            "block", "interfaceBlock", "associationBlock", "propertySpecificType",
            "port", "proxyPort", "fullPort",
        }
    }
    action_owner_ids = {
        n["id"] for n in nodes
        if ELEMENT_CATALOG.get(n["semanticType"]) and ELEMENT_CATALOG[n["semanticType"]].category == "action"
    }
    expansion_region_ids = {n["id"] for n in nodes if n["semanticType"] == "expansionRegion"}
    for node, parent in zip(nodes, parents):
        if parent is None:
            continue
        mapped = id_map.get(parent, parent)
        primitive = node_primitive(node["semanticType"])
        if node["semanticType"] == "expansionNode":
            owner_is_valid = mapped in expansion_region_ids
        elif primitive == "port":
            owner_is_valid = mapped in port_owner_ids
        elif primitive == "pin":
            owner_is_valid = mapped in action_owner_ids
        else:
            owner_is_valid = mapped in container_ids
        if mapped in valid_ids and mapped != node["id"] and owner_is_valid:
            node["parentId"] = mapped

    by_node_id = {node["id"]: node for node in nodes}
    for node in nodes:
        seen: set[str] = set()
        current = node
        while isinstance(current.get("parentId"), str):
            current_id = current["id"]
            if current_id in seen:
                node.pop("parentId", None)
                break
            seen.add(current_id)
            current = by_node_id.get(current["parentId"], {})

    note_ids = {node["id"] for node in nodes if node["semanticType"] == "note"}
    edges: List[Dict[str, Any]] = []
    for e in raw_edges:
        if not isinstance(e, dict):
            continue
        s = id_map.get(str(e.get("source")), e.get("source"))
        t = id_map.get(str(e.get("target")), e.get("target"))
        if s not in valid_ids or t not in valid_ids:
            continue
        sem = e.get("semanticType")
        if s in note_ids or t in note_ids:
            sem = "commentLink"
        elif sem not in allowed_edges:
            sem = default_edge
        edge: Dict[str, Any] = {"source": s, "target": t, "semanticType": sem}
        # A caller-supplied edge ID is stable identity, not decoration: an edit matches
        # on it. Only an absent one is generated downstream.
        if isinstance(e.get("id"), str) and e["id"].strip():
            edge["id"] = e["id"].strip()
        label = e.get("label")
        if isinstance(label, str) and label.strip():
            edge["label"] = label.strip()
        for key in ("sourceEnd", "targetEnd"):
            end = _clean_end(e.get(key))
            if end:
                edge[key] = end
        applied = _clean_stereotypes(e.get("appliedStereotypes"))
        if applied:
            edge["appliedStereotypes"] = applied
        if sem == "extend":
            if isinstance(e.get("condition"), str) and e["condition"].strip():
                edge["condition"] = e["condition"].strip()
            locations = _clean_text_list(e.get("extensionLocations"))
            if locations:
                edge["extensionLocations"] = locations
        item_flows = _clean_item_flows(e.get("itemFlows"))
        if item_flows and sem == "association":
            edge["itemFlows"] = item_flows
        if isinstance(e.get("guard"), str) and e["guard"].strip():
            edge["guard"] = e["guard"].strip()
        weight = e.get("weight")
        if isinstance(weight, (int, float)) and not isinstance(weight, bool) and math.isfinite(weight) and weight >= 0:
            edge["weight"] = float(weight)
        if isinstance(e.get("isInterrupting"), bool):
            edge["isInterrupting"] = e["isInterrupting"]
        if "origin" in e:
            edge["origin"] = copy.deepcopy(e["origin"])
        edges.append(edge)

    name = logical.get("name") if isinstance(logical.get("name"), str) and logical.get("name").strip() else None
    return {"name": name.strip() if name else None, "nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Assemble (logical -> canonical, via the layout service)
# ---------------------------------------------------------------------------


def _slugify_id(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")
    return base or "generated"


def _copy_generation_metadata(generation_metadata: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    if generation_metadata is None:
        return None
    if not isinstance(generation_metadata, Mapping):
        raise ValueError("generation_metadata must be a mapping of authority, assurance, and evidence.")
    unsupported = set(generation_metadata) - _GENERATION_METADATA_KEYS
    if unsupported:
        keys = ", ".join(sorted(str(key) for key in unsupported))
        raise ValueError(f"Unsupported generation_metadata key(s): {keys}.")
    return copy.deepcopy(generation_metadata)


def assemble_canonical(
    conformed: LogicalDiagram,
    diagram_type: str,
    name: str,
    model: str,
    layout_service: DiagramLayoutService,
    generation_metadata: Optional[Mapping[str, Any]] = None,
) -> tuple[Diagram, str]:
    """Turn a conformed logical diagram into a full canonical diagram + layout engine name."""
    metadata_extension = _copy_generation_metadata(generation_metadata)
    profile = get_type_profile(diagram_type)
    node_type = profile.node_type

    layout_nodes = []
    for n in conformed["nodes"]:
        w = h = None
        if diagram_type == "bdd_diagram" and node_primitive(n["semanticType"]) == "classifier-box":
            w, h = bdd_block_min_size(n["label"], n.get("features"))
        elif n.get("extensionPoints"):
            sized = use_case_min_size(n["label"], n["extensionPoints"])
            if sized:
                w, h = sized
        port = n.get("port") or {}
        layout_nodes.append(
            LayoutInputNode(
                id=n["id"], semantic_type=n["semanticType"], label=n["label"],
                parent_id=n.get("parentId"), width=w, height=h,
                port_side=port.get("side"), port_offset=port.get("offset"),
            )
        )
    layout_edges = [LayoutEdge(source=e["source"], target=e["target"]) for e in conformed["edges"]]
    layout = layout_service.layout(diagram_type, layout_nodes, layout_edges)
    pos = layout.positions

    nodes: List[Dict[str, Any]] = []
    for n in conformed["nodes"]:
        p = pos.get(n["id"])
        data: Dict[str, Any] = {"label": n["label"], "semanticType": n["semanticType"]}
        for key in (
            "stereotype", "features", "extensionPoints", "appliedStereotypes", "port", "isAbstract", "unit",
            "quantityKind", "constraintExpression", "constraintParameters", "joinSpec",
        ):
            if key in n:
                data[key] = n[key]
        node: Dict[str, Any] = {
            "id": n["id"],
            "type": node_type,
            "position": {"x": round(p.x, 2) if p else 0, "y": round(p.y, 2) if p else 0},
            "width": round(p.width, 2) if p else 150,
            "height": round(p.height, 2) if p else 60,
            "data": data,
            "style": dict(STYLE_DEFAULTS),
        }
        if n.get("parentId"):
            node["parentId"] = n["parentId"]
        if "origin" in n:
            node["origin"] = copy.deepcopy(n["origin"])
        nodes.append(node)

    edges: List[Dict[str, Any]] = []
    for i, e in enumerate(conformed["edges"]):
        style = {"stroke": EDGE_DEFAULTS["stroke"], "strokeWidth": EDGE_DEFAULTS["strokeWidth"]}
        if e["semanticType"] in _DASHED_EDGE_SEMANTICS:
            style["strokeDasharray"] = "6 4"
        edge_data: Dict[str, Any] = {"semanticType": e["semanticType"]}
        for key in (
            "sourceEnd", "targetEnd", "condition", "extensionLocations", "itemFlows",
            "appliedStereotypes", "guard", "weight", "isInterrupting",
        ):
            if key in e:
                edge_data[key] = e[key]
        edge: Dict[str, Any] = {
            # A draft's relationship ID reaches the canonical edge unchanged: a later
            # edit matches on identity, never by comparing labels or graph shape.
            "id": e.get("id") or f"edge_{i + 1}_{e['source']}_{e['target']}",
            "type": "default",
            "source": e["source"],
            "target": e["target"],
            "data": edge_data,
            "style": style,
        }
        if e.get("label"):
            edge["label"] = e["label"]
        # Presentation intent GraphPilot owns, stamped per diagram type. Written at
        # creation rather than defaulted in the renderer so a diagram a user has already
        # arranged never changes appearance underneath them.
        route_mode = TYPE_ROUTE_MODE.get(diagram_type)
        if route_mode:
            edge["route"] = {"mode": route_mode}
        if "origin" in e:
            edge["origin"] = copy.deepcopy(e["origin"])
        edges.append(edge)

    now = timezone.now().isoformat()
    metadata: Dict[str, Any] = {
        "source": "mcp",
        "authoring": "generated",
        "generatedBy": model,
        "createdAt": now,
        "updatedAt": now,
        # Identity block: what the diagram is, so an editing agent keeps context
        # even after the diagram is relaxed to `custom` by a freeform edit.
        "originalType": diagram_type,
        "notation": profile.notation,
        "intent": name,
    }
    if metadata_extension is not None:
        metadata.update(metadata_extension)
    # The ask arrives as plain text and is stamped here, from the same clock read as
    # `createdAt`, so one materialization has one time in it rather than two that
    # disagree by a few microseconds. An entry that is already stamped came from an
    # earlier write and keeps the time it actually arrived.
    metadata["requests"] = [
        entry if isinstance(entry, Mapping) else {"at": now, "text": str(entry)}
        for entry in metadata.get("requests") or ()
    ]
    canonical = {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": diagram_type,
        "id": f"diagram_{_slugify_id(name)}",
        "name": name,
        "metadata": metadata,
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": nodes,
        "edges": edges,
    }
    return canonical, layout.engine


def _structural_findings(result: ValidationResult) -> Tuple[ValidationIssue, ...]:
    """The structural-critic findings (advisory, Layer 4) carried in a ValidationResult."""
    return tuple(
        issue
        for issue in result.issues
        if issue.code == ValidationCode.STRUCTURAL_CONSTRAINT.value
    )


