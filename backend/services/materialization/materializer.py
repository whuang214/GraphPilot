"""Turn a validated draft into a canonical diagram.

A pure function: same draft and same evidence digests produce the same diagram, every
time. No provider, no randomness, no clock beyond the metadata timestamp.

The notation rules the retired pipeline asked a model to satisfy — and then rejected it
for missing — are **applied here by construction**. A composition always gets its source
end; a generalization never gets one. A malformed relationship is not something this code
can emit.
"""

import copy
from typing import Any, Dict, Mapping, Optional, Tuple

from services.diagrams.catalog.diagram_shapes import Diagram, LogicalDiagram
from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.materialization.canonical_assembly import assemble_canonical, conform_logical

#: Which relationship ends each semantic type carries.
#:
#: ``composition`` deliberately does **not** set ``aggregation``. It is its own canonical
#: edge identity and the element catalog already gives it ``target_marker="diamond_filled"``,
#: so the diamond is drawn at the whole from the type alone. Setting ``aggregation`` as
#: well draws a *second* diamond at the part — ``aggregation`` is how a plain
#: ``association`` expresses composition, not how ``composition`` does.
#:
#: Its source end therefore exists only to carry the part's role and multiplicity, and is
#: built only when the host states one.
_SOURCE_END = {
    "composition": "optional",
    "association": "optional",
    "generalization": "none",
    "dependency": "none",
    "commentLink": "none",
    "controlFlow": "none",
    "include": "none",
    "extend": "none",
}
_TARGET_END = {
    "composition": "optional",
    "association": "optional",
    "dependency": "optional",
    "generalization": "none",
    "commentLink": "none",
    "controlFlow": "none",
    "include": "none",
    "extend": "none",
}

_FEATURE_SECTIONS = ("properties", "operations", "constraints", "literals")


def to_logical(draft: Mapping[str, Any]) -> LogicalDiagram:
    """Project a validated draft onto the logical graph, with no coordinates."""
    diagram_type = draft["diagramType"]
    nodes = [_node(element) for element in draft["elements"]]
    edges = [_edge(relationship) for relationship in draft["relationships"]]
    return conform_logical({"nodes": nodes, "edges": edges}, diagram_type)


def materialize(
    draft: Mapping[str, Any],
    *,
    evidence_digests: Mapping[str, str],
    layout_service: DiagramLayoutService,
) -> Tuple[Diagram, str]:
    """Return the canonical diagram and the layout engine that positioned it."""
    diagram_type = draft["diagramType"]
    logical = to_logical(draft)
    return assemble_canonical(
        logical,
        diagram_type,
        draft["diagramName"],
        "graphpilot-materializer",
        layout_service,
        generation_metadata=_provenance_metadata(draft, evidence_digests),
    )


# ---- elements ----------------------------------------------------------------------


def _node(element: Mapping[str, Any]) -> Dict[str, Any]:
    node: Dict[str, Any] = {
        "id": element["id"],
        "semanticType": element["semanticType"],
        "label": element["label"],
        "origin": _origin(element),
    }
    if element.get("stereotype") is not None:
        node["stereotype"] = element["stereotype"]
    if element.get("parentId") is not None:
        node["parentId"] = element["parentId"]
    # A use case's extension points are drawn in its own compartment and only the host
    # knows them. They were renderable and unauthorable until now.
    if element.get("extensionPoints"):
        node["extensionPoints"] = list(element["extensionPoints"])
    features = _features(element.get("features"))
    if features:
        node["features"] = features
    return node


def _features(features: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    """Hand the compartments to canonical normalization.

    Empty compartments are dropped downstream rather than carried as empty arrays, which
    is the shape the renderer and the React Flow adapter already agree on.
    """
    if not features:
        return None
    populated = {
        section: list(features.get(section) or ())
        for section in _FEATURE_SECTIONS
        if features.get(section)
    }
    return copy.deepcopy(populated) or None


# ---- relationships -----------------------------------------------------------------


def _edge(relationship: Mapping[str, Any]) -> Dict[str, Any]:
    semantic = relationship["semanticType"]
    edge: Dict[str, Any] = {
        "id": relationship["id"],
        "source": relationship["source"],
        "target": relationship["target"],
        "semanticType": semantic,
        "origin": _origin(relationship),
    }
    if relationship.get("label"):
        edge["label"] = relationship["label"]
    if relationship.get("guard"):
        edge["guard"] = relationship["guard"]
    # UML draws an extend's condition and the point it attaches to. Both are things only
    # the host can know, so both are carried straight through.
    if relationship.get("condition"):
        edge["condition"] = relationship["condition"]
    if relationship.get("extensionLocations"):
        edge["extensionLocations"] = list(relationship["extensionLocations"])

    source_end = _relationship_end(
        _SOURCE_END.get(semantic, "none"),
        relationship.get("sourceRole"),
        relationship.get("sourceMultiplicity"),
    )
    if source_end is not None:
        edge["sourceEnd"] = source_end

    target_end = _relationship_end(
        _TARGET_END.get(semantic, "none"),
        relationship.get("targetRole"),
        relationship.get("targetMultiplicity"),
        relationship.get("targetNavigable"),
    )
    if target_end is not None:
        edge["targetEnd"] = target_end
    return edge


def _relationship_end(
    policy: str,
    role: Optional[str],
    multiplicity: Optional[Mapping[str, Any]],
    navigable: Optional[bool] = None,
) -> Optional[Dict[str, Any]]:
    """Build one relationship end, or decline to.

    ``optional`` builds one when the host has something to say about that end; ``none``
    never builds one. An empty end object would be permitted by the canonical schema and
    would mean nothing, so it is not emitted.

    Navigability counts as something to say: an arrowhead on an association end is real
    notation, and until it was carried here a host could not put one anywhere — the
    committed answer keys had arrowheads no draft could produce.
    """
    if policy == "none" or (role is None and multiplicity is None and navigable is None):
        return None
    end: Dict[str, Any] = {}
    if role is not None:
        end["role"] = role
    if multiplicity is not None:
        end["multiplicity"] = dict(multiplicity)
    if navigable is not None:
        end["navigable"] = navigable
    return end


# ---- provenance --------------------------------------------------------------------


def _origin(item: Mapping[str, Any]) -> Dict[str, Any]:
    assumption = item.get("assumptionRef")
    return {
        "assurance": item["assurance"],
        "evidenceRefs": list(item.get("evidenceRefs") or ()),
        "assumptionRefs": [assumption] if assumption else [],
        "schemaRules": [],
        "rationale": _rationale(item),
    }


def _rationale(item: Mapping[str, Any]) -> str:
    assurance = item["assurance"]
    if assurance == "grounded":
        refs = ", ".join(item.get("evidenceRefs") or ())
        return f"Established by cited evidence: {refs}."
    if assurance == "assumed":
        return f"Accepted as an assumption: {item['assumptionRef']}."
    return "Conceptual: this diagram makes no claim about a repository."


def _provenance_metadata(
    draft: Mapping[str, Any],
    evidence_digests: Mapping[str, str],
) -> Dict[str, Any]:
    """Carry evidence and the request log inline so the diagram stays self-contained.

    The asks go through as plain text; `assemble_canonical` stamps them, because that is
    where the one clock read for a materialization lives. The host never writes the time:
    a clock it controls is a fact nobody can check, and this list is the only durable
    record of why the diagram looks the way it does.
    """
    authority = draft["authority"]
    metadata: Dict[str, Any] = {
        "authority": authority,
        "requests": list(draft.get("requests") or ()),
    }

    assumed = sorted(
        item["id"]
        for section in ("elements", "relationships")
        for item in draft.get(section) or ()
        if item["assurance"] == "assumed"
    )
    if assumed:
        # The body travels with the reference, for the same reason evidence does: a
        # diagram has to be readable by someone who does not have the draft. It used to
        # persist `assumptionRefs: ["asm-operator-outside"]` and a rationale quoting that
        # id, while the statement, the reason and who accepted it were discarded — so a
        # reader could see that an element was assumed and never learn what was assumed.
        # That is a dangling pointer in a shipped artifact, and worse than not marking it.
        #
        # This is not the prose `D1` excluded. Uncertainties and decisions are commentary
        # on the diagram; an assumption is load-bearing — it is the sole justification for
        # an element being in the picture at all.
        referenced = {
            item["assumptionRef"]
            for section in ("elements", "relationships")
            for item in draft.get(section) or ()
            if item["assurance"] == "assumed" and item.get("assumptionRef")
        }
        metadata["assurance"] = {
            "assumedElementIds": assumed,
            "assumptions": [
                {
                    "id": assumption["id"],
                    "statement": assumption["statement"],
                    "reason": assumption["reason"],
                    "acceptedBy": assumption["acceptedBy"],
                }
                for assumption in draft.get("assumptions") or ()
                if assumption["id"] in referenced
            ],
        }

    if authority == "as_implemented":
        metadata["evidence"] = [
            _evidence_record(record, evidence_digests) for record in draft.get("evidence") or ()
        ]
    return metadata


def _evidence_record(record: Mapping[str, Any], digests: Mapping[str, str]) -> Dict[str, Any]:
    locator: Dict[str, Any] = {
        "path": record["locator"]["path"],
        "lineRange": dict(record["locator"]["lineRange"]),
    }
    if record["locator"].get("symbol") is not None:
        locator["symbol"] = record["locator"]["symbol"]
    return {
        "id": record["id"],
        "kind": record["kind"],
        "locator": locator,
        "contentDigest": digests[record["id"]],
        "summary": record["summary"],
    }
