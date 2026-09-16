"""Place what is new against the arrangement that already exists.

Merging restores every saved coordinate by id. This module answers the only question that
leaves: where does something genuinely new go?

Five rules, in priority order:

* **R1** preserve by identity — a surviving node keeps its exact saved geometry.
* **R2** a node never shrinks and never clips — size is `max(saved, minimum for content)`.
* **R3** a new node is placed against the *current* arrangement, not the fresh layout's.
* **R4** containment outranks proximity — a child lands inside its parent, always.
* **R5** nothing that already exists ever moves.

R1 and R5 are the same promise from two directions, and they are why this is arithmetic
rather than a second layout pass. Pinning graphviz was tried: with no `inputscale`
coordinates are read as inches and emitted as points, so `200` became `14427` and then
`1036800`; with `inputscale=72` relative spacing survives but the whole drawing translates
and the result is not idempotent — even pinned nodes come back changed. Plain arithmetic
makes existing nodes byte-identical rather than approximately preserved.
"""

from itertools import combinations
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

#: One clear step between things. Matches the layout engine's node separation closely
#: enough that a placed node does not look like it belongs to a different drawing.
GAP = 60.0

_DEFAULT_W, _DEFAULT_H = 160.0, 60.0


def _box(node: Mapping[str, Any]) -> Tuple[float, float, float, float]:
    position = node.get("position") or {}
    x = float(position.get("x", 0.0))
    y = float(position.get("y", 0.0))
    return x, y, float(node.get("width") or _DEFAULT_W), float(node.get("height") or _DEFAULT_H)


def _overlaps(a: Tuple[float, float, float, float],
              b: Tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def grow_to_fit(saved_size: Optional[float], minimum: float) -> float:
    """R2. A person's oversized box stays oversized; a longer label grows the box.

    Recomputing outright would undo a deliberate resize. Carrying the saved size blindly
    would clip the text after a relabel. Taking the larger does neither.
    """
    if saved_size is None:
        return minimum
    return max(float(saved_size), float(minimum))


def _ancestors(node_id: str, nodes: Mapping[str, Mapping[str, Any]]) -> set:
    chain, current = set(), node_id
    while current:
        node = nodes.get(current)
        parent_id = node.get("parentId") if node else None
        if not parent_id or parent_id in chain:
            break
        chain.add(parent_id)
        current = parent_id
    return chain


def new_overlaps(
    before: Mapping[str, Any], after: Mapping[str, Any]
) -> List[Tuple[str, str]]:
    """R2's third clause: a grown box may collide, and a collision is *warned*, not moved.

    Growing a relabelled node without saying so is worse than leaving it clipped: the
    clipped version at least looks wrong. Two boxes drawn over each other look deliberate,
    and the person who arranged the diagram is the one who finds out.

    Containment is not a collision — a child is supposed to be inside its parent — so
    ancestor pairs are skipped. Pairs already overlapping before the edit are skipped too,
    because this reports what the write introduced, not what it inherited.
    """
    def boxes(document: Mapping[str, Any]) -> Dict[str, Tuple[float, float, float, float]]:
        nodes = {node["id"]: node for node in document.get("nodes") or ()}
        out = {}
        for node_id, node in nodes.items():
            x, y, w, h = _box(node)
            ox, oy = _absolute_origin(node_id, nodes)
            out[node_id] = (x + ox, y + oy, w, h)
        return out

    was, now = boxes(before), boxes(after)
    nodes_after = {node["id"]: node for node in after.get("nodes") or ()}
    found: List[Tuple[str, str]] = []
    for left, right in combinations(sorted(now), 2):
        if left in _ancestors(right, nodes_after) or right in _ancestors(left, nodes_after):
            continue
        if not _overlaps(now[left], now[right]):
            continue
        if left in was and right in was and _overlaps(was[left], was[right]):
            continue
        found.append((left, right))
    return found


def _neighbour_boxes(
    node_id: str,
    edges: Sequence[Mapping[str, Any]],
    placed: Mapping[str, Tuple[float, float, float, float]],
) -> List[Tuple[float, float, float, float]]:
    """The boxes of everything this node connects to, **in the current arrangement**.

    Not the fresh layout's coordinates — those describe a picture that was thrown away.
    """
    found = []
    for edge in edges:
        other = None
        if edge.get("source") == node_id:
            other = edge.get("target")
        elif edge.get("target") == node_id:
            other = edge.get("source")
        if other is not None and other in placed:
            found.append(placed[other])
    return found


def place(
    node_id: str,
    width: float,
    height: float,
    *,
    edges: Sequence[Mapping[str, Any]],
    occupied: Mapping[str, Tuple[float, float, float, float]],
    parent: Optional[Tuple[float, float, float, float]] = None,
) -> Tuple[float, float]:
    """R3 and R4. Return a position for a new node, in the same coordinate space as
    `occupied`.

    Deterministic by construction: pure arithmetic over geometry already on disk, with ties
    broken by sorted id, so a multi-node add never depends on request ordering. No layout
    engine is called.
    """
    neighbours = _neighbour_boxes(node_id, edges, occupied)
    if neighbours:
        centre_x = sum(bx + bw / 2 for bx, _, bw, _ in neighbours) / len(neighbours)
        lowest = max(by + bh for _, by, _, bh in neighbours)
        x, y = centre_x - width / 2, lowest + GAP
    elif occupied:
        boxes = list(occupied.values())
        x = min(bx for bx, _, _, _ in boxes)
        y = max(by + bh for _, by, _, bh in boxes) + GAP
    else:
        x, y = 0.0, 0.0

    # R4: containment outranks proximity. A use case whose only neighbour is an actor
    # outside the subject boundary must still land inside the boundary — the first version
    # of R3 shipped without this and dragged a child clean out of its own container.
    if parent is not None:
        px, py, pw, ph = parent
        x = min(max(x, px + GAP / 2), px + pw - width - GAP / 2)
        y = min(max(y, py + GAP / 2), py + ph - height - GAP / 2)

    # Step along one fixed axis until the box is clear. Bounded so a pathological diagram
    # cannot spin: after that many steps the drawing is beyond saving by arithmetic and the
    # overlap is reported instead.
    for _ in range(200):
        if not any(_overlaps((x, y, width, height), box) for box in occupied.values()):
            break
        y += height + GAP
        if parent is not None:
            px, py, pw, ph = parent
            if y + height > py + ph:
                break
    return x, y


def grow_parent(
    parent: Tuple[float, float, float, float],
    child: Tuple[float, float, float, float],
) -> Tuple[float, float]:
    """R4's other half: if the parent has no free room, grow it. Never place the child out.

    Returns the parent's new width and height. Its position is untouched, because R5 holds
    for containers too — growing one is not moving it.
    """
    px, py, pw, ph = parent
    cx, cy, cw, ch = child
    return (
        max(pw, cx + cw + GAP / 2 - px),
        max(ph, cy + ch + GAP / 2 - py),
    )


def _absolute_origin(node_id: str, nodes: Mapping[str, Mapping[str, Any]]) -> Tuple[float, float]:
    """Where a node actually sits, following `parentId` up to the top.

    **A child's `position` is relative to its parent**, which is the convention React Flow
    uses and the canvas and renderer both assume. Reasoning about neighbours in that space
    is meaningless: a use case at `x: 24` and an actor at `x: -520` are not 544 apart, they
    are whatever the parent's offset makes them.

    The first version of the placement rule mixed the two. Every number agreed, the
    containment test passed, and the new node was drawn outside the boundary it belonged
    to — visible only by looking at the picture.
    """
    x = y = 0.0
    seen = set()
    current = node_id
    while current and current not in seen:
        seen.add(current)
        node = nodes.get(current)
        if node is None:
            break
        parent_id = node.get("parentId")
        if not parent_id:
            break
        parent = nodes.get(parent_id)
        if parent is None:
            break
        position = parent.get("position") or {}
        x += float(position.get("x", 0.0))
        y += float(position.get("y", 0.0))
        current = parent_id
    return x, y


def place_new_nodes(diagram: Dict[str, Any], new_ids: Sequence[str]) -> List[str]:
    """Place every node in *new_ids* against the arrangement the rest of them are in.

    All the reasoning happens in **absolute** coordinates, because that is the only space
    in which "beside its neighbours" and "inside its parent" both mean something. The
    result is converted back to the parent-relative form the file stores.

    Mutates `diagram` in place and returns the ids that were placed, in the order they were
    placed — sorted, so two runs of the same edit produce the same picture.
    """
    nodes = {node["id"]: node for node in diagram.get("nodes") or ()}
    edges = list(diagram.get("edges") or ())
    new = set(new_ids)

    def absolute(node: Mapping[str, Any]) -> Tuple[float, float, float, float]:
        x, y, w, h = _box(node)
        ox, oy = _absolute_origin(node["id"], nodes)
        return x + ox, y + oy, w, h

    occupied = {
        node_id: absolute(node) for node_id, node in nodes.items() if node_id not in new
    }
    placed: List[str] = []
    for node_id in sorted(new):
        node = nodes.get(node_id)
        if node is None:
            continue
        _, _, width, height = _box(node)
        parent_id = node.get("parentId")
        parent = occupied.get(parent_id) if parent_id else None
        x, y = place(
            node_id, width, height, edges=edges, occupied=occupied, parent=parent,
        )

        if parent_id and parent is not None:
            grown_w, grown_h = grow_parent(parent, (x, y, width, height))
            parent_node = nodes.get(parent_id)
            if parent_node is not None and (grown_w, grown_h) != (parent[2], parent[3]):
                parent_node["width"] = grown_w
                parent_node["height"] = grown_h
                occupied[parent_id] = (parent[0], parent[1], grown_w, grown_h)

        occupied[node_id] = (x, y, width, height)
        # Back into the space the file stores. `_absolute_origin` reads the parent chain
        # from `nodes`, and this node's own position is not part of its own origin.
        ox, oy = _absolute_origin(node_id, nodes)
        node["position"] = {"x": x - ox, "y": y - oy}
        placed.append(node_id)
    return placed
