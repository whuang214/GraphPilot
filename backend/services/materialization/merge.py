"""Merge a freshly materialized diagram over the one already on disk.

Every field in a saved diagram belongs to exactly one of three classes, and each class has
one rule. That is the whole mechanism.

| Class | Rule |
| ----- | ---- |
| **1 · host-owned** — appears in the draft   | the draft is the truth; overwrite it |
| **2 · carried** — absent from the draft     | copy the saved value by id, or compute one if the id is new |
| **3 · derived** — absent from the draft     | recompute on every write |

The draft does not need to express everything the diagram holds, because anything it
cannot express is handled by rule 2 or 3, and neither needs the draft. A person's dragged
position and a person's typed `description` are both class 2: preserved by the same
mechanism, for the same reason — the host did not write them and must not lose them.
Splitting them into "geometry" and "semantics" would give one a preservation rule and the
other nothing.

**On a create the saved diagram is empty**, so every element takes the "compute it" branch.
There is one write path, not two. Create is the edit where the file was empty.

The membership of each class is `docs/03-design/05-edit/03-geometry-and-merge.md`, and the
tests read it as an oracle rather than restating it.
"""

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from services.materialization.geometry import grow_to_fit

#: Class 2 on a node: geometry, plus the semantics a draft has no field for. Copied from
#: the saved element when the id survives.
_NODE_CARRIED = (
    "position",
)
#: R2 size, which is class 2 with one qualification: carried, but never below what the
#: fresh content needs. Blind carry clips a relabelled node; `grow_to_fit` owns the
#: arithmetic that avoids both that and undoing a deliberate resize.
_NODE_GROWN = ("width", "height")
_NODE_DATA_CARRIED = (
    "port", "joinSpec", "isAbstract", "unit", "quantityKind", "constraintExpression",
    "constraintParameters", "description", "metadata", "appliedStereotypes",
)

#: Class 2 on an edge. `route` carries the whole object — mode, waypoints, label offset and
#: anchors — except when rewiring invalidates the bend; see `_carry_route`.
_EDGE_CARRIED = ("sourceHandle", "targetHandle")
_EDGE_DATA_CARRIED = (
    "weight", "isInterrupting", "itemFlows", "description", "metadata",
    "appliedStereotypes",
)

#: Class 2 on the document.
_DOCUMENT_CARRIED = ("viewport",)
_METADATA_CARRIED = ("createdAt", "authoring")


@dataclass(frozen=True)
class Removed:
    """An element the write deleted, because the draft did not mention it."""
    id: str
    label: str
    drawn_by_user: bool
    #: Text a person typed that no draft could show, and that goes with the element.
    lost_text: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"id": self.id, "label": self.label}
        if self.drawn_by_user:
            # Named so a person's deleted work is visible in the same breath as the change
            # that caused it, rather than discovered a week later.
            out["drawnBy"] = "user"
        if self.lost_text:
            out["lostText"] = list(self.lost_text)
        return out


#: Class-2 `data` keys holding prose a person typed. The draft cannot express them, which
#: is what protects them on an ordinary edit and what makes them invisible on a removal.
_HUMAN_TEXT = ("description", "constraintExpression")


def _human_text(node: Mapping[str, Any]) -> Tuple[str, ...]:
    """Prose on this element that exists nowhere else.

    An audit deleted a node whose `description` read *"Reynolds 853. Confirmed with Priya,
    Aug 2026."* \u2014 a decision record naming a colleague. The host reported "removed Frame"
    and could not have done better: the description is deliberately absent from the draft,
    so nothing in its read-edit-write loop had ever shown it the text existed.

    The whole reason removal is visible rather than forbidden is that a person can see what
    went. Reporting an id and a label does not achieve that when the thing lost was a
    sentence.
    """
    data = node.get("data") or {}
    return tuple(
        str(data[key]) for key in _HUMAN_TEXT
        if isinstance(data.get(key), str) and data[key].strip()
    )


@dataclass(frozen=True)
class MergeResult:
    diagram: Dict[str, Any]
    removed: Tuple[Removed, ...]
    carried_node_ids: Tuple[str, ...]
    new_node_ids: Tuple[str, ...]


def _by_id(items: Sequence[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    return {item["id"]: item for item in items if "id" in item}


def _carry(fresh: Dict[str, Any], saved: Mapping[str, Any], keys: Sequence[str]) -> None:
    for key in keys:
        if key in saved:
            fresh[key] = copy.deepcopy(saved[key])
        else:
            fresh.pop(key, None)


def _carry_data(fresh: Dict[str, Any], saved: Mapping[str, Any], keys: Sequence[str]) -> None:
    saved_data = saved.get("data") or {}
    data = fresh.setdefault("data", {})
    for key in keys:
        if key in saved_data:
            data[key] = copy.deepcopy(saved_data[key])
        else:
            data.pop(key, None)


def _grow(fresh: Dict[str, Any], saved: Mapping[str, Any], keys: Sequence[str]) -> None:
    """R2. Keep the person's size, but never below what the fresh content needs.

    The fresh value is already the minimum for the new label, stereotype and features,
    because the materializer just computed it. The saved value is whatever the person
    dragged the corner to. R2 is `max` of the two, per element and per axis.
    """
    for key in keys:
        needed = fresh.get(key)
        if needed is None:
            _carry(fresh, saved, (key,))
            continue
        fresh[key] = grow_to_fit(saved.get(key), float(needed))


def _carry_route(fresh: Dict[str, Any], saved: Mapping[str, Any]) -> None:
    """Keep the saved route, unless rewiring made its shape describe a path that is gone.

    A person dragged an edge into a shape that avoided something on the path between two
    particular nodes. Change either endpoint and those waypoints describe a route that no
    longer exists — so they go, and the edge is drawn fresh.

    `route.mode` survives, because a preference for orthogonal or straight is about the
    edge rather than the path it takes.

    This is not the host authoring geometry. It never names a waypoint; it makes a semantic
    change, and the geometry that change invalidates goes with it, exactly as removing a
    node discards its position.
    """
    saved_route = saved.get("route")
    if not saved_route:
        fresh.pop("route", None)
        return
    rewired = (fresh.get("source") != saved.get("source")
               or fresh.get("target") != saved.get("target"))
    if not rewired:
        fresh["route"] = copy.deepcopy(saved_route)
        return
    mode = saved_route.get("mode")
    if mode:
        fresh["route"] = {"mode": mode}
    else:
        fresh.pop("route", None)


def merge(fresh: Mapping[str, Any], saved: Mapping[str, Any]) -> MergeResult:
    """Return *fresh* with every class-2 field taken from *saved* where the id survives.

    `fresh` is what the materializer just built from the submitted draft: class-1 fields
    are already correct and class-3 fields are already recomputed, so this only has to
    restore what the draft could not carry.
    """
    out = copy.deepcopy(dict(fresh))
    saved_nodes = _by_id(saved.get("nodes") or ())
    saved_edges = _by_id(saved.get("edges") or ())

    carried: List[str] = []
    added: List[str] = []
    for node in out.get("nodes") or ():
        previous = saved_nodes.get(node["id"])
        if previous is None:
            added.append(node["id"])
            continue
        _carry(node, previous, _NODE_CARRIED)
        _grow(node, previous, _NODE_GROWN)
        _carry_data(node, previous, _NODE_DATA_CARRIED)
        carried.append(node["id"])

    for edge in out.get("edges") or ():
        previous = saved_edges.get(edge["id"])
        if previous is None:
            continue
        _carry(edge, previous, _EDGE_CARRIED)
        _carry_data(edge, previous, _EDGE_DATA_CARRIED)
        _carry_route(edge, previous)

    _carry(out, saved, _DOCUMENT_CARRIED)
    metadata = out.setdefault("metadata", {})
    saved_metadata = saved.get("metadata") or {}
    for key in _METADATA_CARRIED:
        if key in saved_metadata:
            metadata[key] = copy.deepcopy(saved_metadata[key])

    # `authoring` only ratchets. Once a person has saved from the editor the diagram is
    # `custom` forever: a later host write does not reset it to `generated`, because the
    # human work it records did not stop being true.
    if saved_metadata.get("authoring") == "custom":
        metadata["authoring"] = "custom"

    submitted = {node["id"] for node in out.get("nodes") or ()}
    removed = tuple(
        Removed(
            id=node_id,
            label=(node.get("data") or {}).get("label", ""),
            drawn_by_user=(node.get("origin") or {}).get("assurance") == "user",
            lost_text=_human_text(node),
        )
        for node_id, node in saved_nodes.items()
        if node_id not in submitted
    )

    return MergeResult(out, removed, tuple(carried), tuple(added))
