"""Project a saved diagram back into the draft that would produce it.

The saved `.gp.json` is the only durable store of a diagram's semantics, and it has **two
authors**: a host that materialized it, and a person who may since have added a node,
retyped an edge or renamed a label in the browser. Any second copy of those semantics — a
durable draft on disk, one embedded in the diagram's metadata, a layout sidecar — goes
stale the moment the person deletes something, and nothing detects it.

So there is no second copy. The draft is computed from the file on demand and thrown away
afterwards, which is what makes it impossible for the two to disagree.

**Class-1 fields only.** Every field in a saved diagram belongs to exactly one of three
classes (`docs/03-design/05-edit/03-geometry-and-merge.md`), and only class 1 — the fields
a draft can express — is emitted here. Class 2 is carried by id on the next write and class
3 is recomputed, so neither needs to make the round trip. That is why a person's dragged
position and a person's typed description both survive an edit without the host ever seeing
them: not emitting a field is what protects it.

No inference, no matching by label, no guessing. If a value is not in the saved file it is
not in the projection.
"""

from typing import Any, Dict, List, Mapping, Optional

#: Node `data` keys a draft can express, in the order the draft schema declares them.
_ELEMENT_DATA = ("stereotype", "features", "extensionPoints")

#: Edge `data` keys a draft can express.
_EDGE_DATA = ("guard", "condition", "extensionLocations")

#: Relationship-end fields, and the draft name each takes. `sourceNavigable` is absent
#: because the draft dropped it: an arrowhead on the source end of an association appeared
#: in none of the 48 committed diagrams, while `targetNavigable` covers the case that does.
_ENDS = (
    ("sourceEnd", "role", "sourceRole"),
    ("targetEnd", "role", "targetRole"),
    ("sourceEnd", "multiplicity", "sourceMultiplicity"),
    ("targetEnd", "multiplicity", "targetMultiplicity"),
    ("targetEnd", "navigable", "targetNavigable"),
)


def _put(out: Dict[str, Any], key: str, value: Any) -> None:
    """Set *key* only when there is something to set.

    A draft field that is present-but-empty is not the same as one that is absent: the
    contract tells hosts to omit what the source does not establish, so emitting
    `"stereotype": ""` would hand back a value nobody authored and invite it to be kept.
    """
    if value is None or value == "" or value == [] or value == {}:
        return
    out[key] = value


def _element(node: Mapping[str, Any]) -> Dict[str, Any]:
    data = node.get("data") or {}
    origin = node.get("origin") or {}
    out: Dict[str, Any] = {
        "id": node["id"],
        "semanticType": data.get("semanticType", ""),
        "label": data.get("label", ""),
    }
    for key in _ELEMENT_DATA:
        _put(out, key, data.get(key))
    _put(out, "parentId", node.get("parentId"))

    # `assurance` is required on every element, so it is set rather than `_put`. A diagram
    # written before origins existed has none; `conceptual` is the honest default there,
    # because it claims nothing about the repository — which is exactly what an element
    # with no recorded provenance can support.
    out["assurance"] = origin.get("assurance") or "conceptual"
    _put(out, "evidenceRefs", list(origin.get("evidenceRefs") or ()))
    refs = origin.get("assumptionRefs") or ()
    if refs:
        # The draft takes one; the canonical carries a list. Every materialized diagram
        # has at most one, because `assumptionRef` is what wrote it.
        out["assumptionRef"] = refs[0]
    return out


def _relationship(edge: Mapping[str, Any]) -> Dict[str, Any]:
    data = edge.get("data") or {}
    origin = edge.get("origin") or {}
    out: Dict[str, Any] = {
        "id": edge["id"],
        "semanticType": data.get("semanticType", ""),
        "source": edge.get("source", ""),
        "target": edge.get("target", ""),
    }
    # The edge label is carried at the edge's top level, not under `data`. It includes a
    # `«include»` or `«extend»` keyword a host authored, and omitting it here would delete
    # that label on the first edit.
    _put(out, "label", edge.get("label"))
    for key in _EDGE_DATA:
        _put(out, key, data.get(key))
    # Ends live under `data`, not at the edge's top level. Reading them from the wrong
    # place silently dropped every role, multiplicity and navigability on every edge —
    # invisible in the round-trip test until its comparison covered them, and caught by
    # diffing the regenerated gallery.
    for end_name, field, draft_name in _ENDS:
        _put(out, draft_name, (data.get(end_name) or {}).get(field))

    out["assurance"] = origin.get("assurance") or "conceptual"
    _put(out, "evidenceRefs", list(origin.get("evidenceRefs") or ()))
    refs = origin.get("assumptionRefs") or ()
    if refs:
        out["assumptionRef"] = refs[0]
    return out


def _evidence(record: Mapping[str, Any]) -> Dict[str, Any]:
    """One citation, without its digest.

    `contentDigest` is backend-derived — the backend hashes the cited region on save, and a
    draft that authors one is refused. Emitting it would hand a host a value it is not
    allowed to send back.
    """
    return {
        "id": record["id"],
        "kind": record["kind"],
        "locator": {
            key: value for key, value in (record.get("locator") or {}).items()
            if key in ("path", "symbol", "lineRange")
        },
        "summary": record.get("summary", ""),
    }


def project(diagram: Mapping[str, Any], *, basis: Optional[Mapping[str, Any]] = None
            ) -> Dict[str, Any]:
    """Return the `graphpilot.draft.v1` document that describes *diagram*'s semantics.

    The result is a valid draft **minus exactly one thing**: the `requests` list holds the
    saved history with nothing appended, so a host cannot write without saying why. That
    missing row is the edit it is about to make.
    """
    metadata = diagram.get("metadata") or {}
    draft: Dict[str, Any] = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": diagram.get("name", ""),
        # `originalType` is what the draft asked for; `diagramType` is what the file is
        # now, and a diagram crossed in the editor reads `custom`, which no draft can
        # express. The read refuses that case before it reaches here.
        "diagramType": diagram.get("diagramType", ""),
        "authority": metadata.get("authority", "conceptual"),
        "requests": [entry["text"] for entry in metadata.get("requests") or ()],
    }
    if basis is not None:
        draft["basis"] = dict(basis)

    evidence = [_evidence(record) for record in metadata.get("evidence") or ()]
    if evidence:
        draft["evidence"] = evidence

    draft["elements"] = [_element(node) for node in diagram.get("nodes") or ()]
    draft["relationships"] = [_relationship(edge) for edge in diagram.get("edges") or ()]

    assumptions: List[Dict[str, Any]] = [
        {
            "id": item["id"],
            "statement": item["statement"],
            "reason": item["reason"],
            "acceptedBy": item["acceptedBy"],
        }
        for item in ((metadata.get("assurance") or {}).get("assumptions") or ())
    ]
    if assumptions:
        draft["assumptions"] = assumptions

    return draft
