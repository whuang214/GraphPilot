"""Service that renders a saved GraphPilot diagram to an SVG image.

The renderer is a **pure function of the diagram JSON** (:meth:`DiagramRenderService.to_svg`)
plus a thin file wrapper (:meth:`DiagramRenderService.render`) that loads the saved
``<name>.gp.json`` through :class:`WorkspaceStorageService` and writes the sibling
``<name>.svg`` beside it.

Design: ``docs/02-design-and-features/03-rendering-design.md``. Key principles:

- **Trust the saved layout** — each node's stored ``position``/``width``/``height`` is
  used as-is; the graph is never re-arranged.
- **Look like the editor** — shapes mirror the React Flow custom renderers
  (``frontend/src/editor/canvas/customNodes.tsx``) per ``data.semanticType``.
- **Deterministic and offline** — no network, no LLM; same input → same SVG.
- **Honor styling** — uses the canonical ``style`` subset, falling back to the same
  defaults as the editor.
- **Fail cleanly** — missing / unsafe / malformed input raises; a failed render never
  leaves a half-written file (the write itself is atomic via ``WorkspaceStorageService``).
"""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import drawsvg as draw

from services.diagrams.catalog.constants import (
    CHAR_WIDTH_RATIO,
    DEFAULT_NODE_SIZES,
    EDGE_DEFAULTS,
    FALLBACK_SIZE,
    FONT_FAMILY,
    feature_compartments,
    FONT_SIZE,
    LINE_HEIGHT,
    MIN_FONT_SIZE,
    PADDING,
    RASTER_BACKGROUND,
    RASTER_MAX_PX,
    RASTER_SANS_FONT,
    RASTER_SCALE,
    STYLE_DEFAULTS,
    TEXT_PADDING,
)
from services.shared.workspace_storage_service import WorkspaceStorageService
from services.diagrams.catalog.element_catalog import ELEMENT_CATALOG, container_semantic_types, node_primitive

# How far a relationship end's role/multiplicity sits from its endpoint: along the edge to
# clear the node boundary and any marker there, then sideways to clear the line itself.
_END_LABEL_CLEARANCE = 22.0
_END_LABEL_SIDESTEP = 13.0

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class DiagramRenderServiceError(Exception):
    """Raised when a diagram cannot be rendered to SVG."""


class RasterizationError(DiagramRenderServiceError):
    """Raised when an SVG cannot be rasterized to PNG.

    A subclass of :class:`DiagramRenderServiceError` so existing ``except`` blocks
    keep catching render failures, while PNG-only call sites can distinguish a
    missing / failing rasterizer (and degrade gracefully) from a malformed diagram.
    """


# ---------------------------------------------------------------------------
# Visual constants
# ---------------------------------------------------------------------------
# The style/size/text-fitting constants (mirroring the editor defaults in
# customNodes.tsx) now live in services/catalog/constants.py and are imported above.

# Container semantic types (drawn behind their contents) come from the shared element
# catalog. Node shapes are dispatched by the catalog's render primitive in
# _draw_node; edge dashing + end markers are read per-edge from the catalog in _draw_edge.
CONTAINER_SEMANTIC_TYPES = container_semantic_types()


# ---------------------------------------------------------------------------
# Composed text: what an authored field actually becomes on the picture
# ---------------------------------------------------------------------------
#
# Public because the string a host has to budget for is not the string it authored, and
# the authoring contract now says so by *composing an example with these functions*
# rather than by restating the format. A host budgeted a 40-character `condition` against
# the documented 120-character label limit and overflowed, because what was drawn was
# `«extend» [that condition]`. A number written out beside the renderer would have gone
# stale the first time the decoration changed.


def stereotype_text(keyword: str) -> str:
    """A stereotype heading as it is drawn: the bare word in guillemets."""
    return f"\u00ab{keyword}\u00bb"


def edge_display_label(edge: Dict[str, Any]) -> str:
    """The one string an edge is drawn with, composed from up to four authored parts.

    Mirrors ``frontend/src/editor/lib/edgePresentation.ts``: the ``include``/``extend``
    keyword is derived from the semantic type rather than authored, and ``condition`` and
    ``guard`` are bracketed here rather than by the host.
    """
    data = edge.get("data") or {}
    semantic = data.get("semanticType")
    label = edge.get("label")
    if semantic in ("include", "extend"):
        keyword = stereotype_text(semantic)
        if not str(label or "").strip().startswith(keyword):
            label = keyword + (f" {label}" if label else "")
    if data.get("condition"):
        label = f"{label or ''} [{data['condition']}]".strip()
    if data.get("guard"):
        label = f"{label or ''} [{data['guard']}]".strip()
    return str(label or "")


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


class _Box:
    """Absolute, resolved geometry for a single node."""

    __slots__ = ("x", "y", "w", "h", "node")

    def __init__(self, x: float, y: float, w: float, h: float, node: Dict[str, Any]) -> None:
        self.x, self.y, self.w, self.h, self.node = x, y, w, h, node

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h


_Point = Tuple[float, float]
_RouteAnchor = Dict[str, Union[str, float]]


def _route_anchor(value: Any) -> Optional[_RouteAnchor]:
    if not isinstance(value, dict) or value.get("side") not in {"top", "right", "bottom", "left"}:
        return None
    offset = _num(value.get("offset"), math.nan)
    if not math.isfinite(offset) or offset < 0 or offset > 1:
        return None
    return {"side": value["side"], "offset": offset}


def _route_point(value: Any) -> Optional[_Point]:
    if not isinstance(value, dict):
        return None
    x = _num(value.get("x"), math.nan)
    y = _num(value.get("y"), math.nan)
    return (x, y) if math.isfinite(x) and math.isfinite(y) else None


def _handle_anchor(value: Any) -> Optional[_RouteAnchor]:
    if not isinstance(value, str):
        return None
    parts = value.split("-")
    if len(parts) == 3 and parts[0] == "gp" and parts[1] in {"top", "right", "bottom", "left"} and parts[2] in {"s", "t"}:
        return {"side": parts[1], "offset": 0.5}
    return None


def _attachment_profile(box: _Box) -> Tuple[str, Tuple[float, float, float, float]]:
    data = box.node.get("data") or {} if isinstance(box.node, dict) else {}
    semantic = data.get("semanticType")
    primitive = node_primitive(semantic) if isinstance(semantic, str) else None
    has_label = isinstance(data.get("label"), str) and bool(data["label"].strip())
    if primitive in {"initial", "final", "flow-final"}:
        top = box.y + max(0.0, (box.h - 34.0 - (FONT_SIZE * LINE_HEIGHT if has_label else 0.0)) / 2)
        return "ellipse", (box.x + (box.w - 34.0) / 2 + 2.0, top + 2.0, 30.0, 30.0)
    if primitive == "actor":
        content_height = max(0.0, box.h - 8.0)
        items_height = 48.0 + (FONT_SIZE * LINE_HEIGHT if has_label else 0.0)
        top = box.y + 4.0 + max(0.0, (content_height - items_height) / 2)
        return "ellipse", (box.x + (box.w - 34.0) / 2 + 5.0, top + 2.0, 24.0, 42.0)
    if primitive == "ellipse":
        return "ellipse", (box.x, box.y, box.w, box.h)
    if primitive == "diamond":
        return "diamond", (box.x, box.y, box.w, box.h)
    return "box", (box.x, box.y, box.w, box.h)


def _drawn_entirely_by_hand(nodes: List[Any], edges: List[Any]) -> bool:
    """True when every element in the diagram is one a person drew in the editor.

    A badge is an admission, and an admission is only information beside something it is
    not — which is exactly why `grounded` goes unbadged: marking the norm teaches a reader
    to ignore the mark. A diagram nobody drafted is `user` end to end, so badging all of it
    marks the norm, and every node of every hand-drawn export wore a pencil.
    """
    elements = [e for e in (*nodes, *edges) if isinstance(e, dict)]
    return bool(elements) and all(
        (e.get("origin") or {}).get("assurance") == "user" for e in elements
    )


def _anchor_point(box: _Box, anchor: _RouteAnchor) -> _Point:
    offset = min(1.0, max(0.0, float(anchor["offset"])))
    side = anchor["side"]
    if side == "top":
        point = box.x + box.w * offset, box.y
    elif side == "bottom":
        point = box.x + box.w * offset, box.bottom
    elif side == "left":
        point = box.x, box.y + box.h * offset
    else:
        point = box.right, box.y + box.h * offset
    shape, bounds = _attachment_profile(box)
    if shape == "box":
        return point
    x, y, width, height = bounds
    rx = max(width / 2, 0.001)
    ry = max(height / 2, 0.001)
    cx = x + rx
    cy = y + ry
    dx = point[0] - cx
    dy = point[1] - cy
    scale = (
        1 / max(abs(dx) / rx + abs(dy) / ry, 0.001)
        if shape == "diamond"
        else 1 / max(math.hypot(dx / rx, dy / ry), 0.001)
    )
    return cx + dx * scale, cy + dy * scale


def _profile_center(box: _Box) -> _Point:
    _, bounds = _attachment_profile(box)
    return bounds[0] + bounds[2] / 2, bounds[1] + bounds[3] / 2


def _radial_box_anchor(box: _Box, center: _Point, point: _Point) -> _RouteAnchor:
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    if abs(dx) < 0.001 and abs(dy) < 0.001:
        return {"side": "top", "offset": 0.5}
    candidates: List[Tuple[str, float]] = []
    if dx > 0:
        candidates.append(("right", (box.right - center[0]) / dx))
    elif dx < 0:
        candidates.append(("left", (box.x - center[0]) / dx))
    if dy > 0:
        candidates.append(("bottom", (box.bottom - center[1]) / dy))
    elif dy < 0:
        candidates.append(("top", (box.y - center[1]) / dy))
    side, scale = min((candidate for candidate in candidates if candidate[1] >= 0), key=lambda candidate: candidate[1])
    x = center[0] + dx * scale
    y = center[1] + dy * scale
    offset = (x - box.x) / max(box.w, 1.0) if side in {"top", "bottom"} else (y - box.y) / max(box.h, 1.0)
    return {"side": side, "offset": min(1.0, max(0.0, offset))}


def _outward(point: _Point, side: str, distance: float = 16.0) -> _Point:
    x, y = point
    if side == "top":
        return x, y - distance
    if side == "bottom":
        return x, y + distance
    if side == "left":
        return x - distance, y
    return x + distance, y


def _automatic_anchors(source: _Box, target: _Box) -> Tuple[_RouteAnchor, _RouteAnchor]:
    dx = target.cx - source.cx
    dy = target.cy - source.cy
    overlap_left = max(source.x, target.x)
    overlap_right = min(source.right, target.right)
    if overlap_left <= overlap_right:
        x = (overlap_left + overlap_right) / 2
        if dy >= 0:
            return (
                {"side": "bottom", "offset": min(1.0, max(0.0, (x - source.x) / max(source.w, 1.0)))},
                {"side": "top", "offset": min(1.0, max(0.0, (x - target.x) / max(target.w, 1.0)))},
            )
        return (
            {"side": "top", "offset": min(1.0, max(0.0, (x - source.x) / max(source.w, 1.0)))},
            {"side": "bottom", "offset": min(1.0, max(0.0, (x - target.x) / max(target.w, 1.0)))},
        )
    overlap_top = max(source.y, target.y)
    overlap_bottom = min(source.bottom, target.bottom)
    if overlap_top <= overlap_bottom:
        y = (overlap_top + overlap_bottom) / 2
        if dx >= 0:
            return (
                {"side": "right", "offset": min(1.0, max(0.0, (y - source.y) / max(source.h, 1.0)))},
                {"side": "left", "offset": min(1.0, max(0.0, (y - target.y) / max(target.h, 1.0)))},
            )
        return (
            {"side": "left", "offset": min(1.0, max(0.0, (y - source.y) / max(source.h, 1.0)))},
            {"side": "right", "offset": min(1.0, max(0.0, (y - target.y) / max(target.h, 1.0)))},
        )
    horizontal = (
        {"side": "right" if dx >= 0 else "left", "offset": 0.5},
        {"side": "top" if dy >= 0 else "bottom", "offset": 0.5},
    )
    vertical = (
        {"side": "bottom" if dy >= 0 else "top", "offset": 0.5},
        {"side": "left" if dx >= 0 else "right", "offset": 0.5},
    )
    horizontal_points = _connect_pair(_anchor_point(source, horizontal[0]), _anchor_point(target, horizontal[1]), True)
    vertical_points = _connect_pair(_anchor_point(source, vertical[0]), _anchor_point(target, vertical[1]), False)
    if _route_length(horizontal_points) < _route_length(vertical_points) or (
        _route_length(horizontal_points) == _route_length(vertical_points) and abs(dx) >= abs(dy)
    ):
        return horizontal
    return vertical


def _automatic_straight_anchors(
    source: _Box,
    target: _Box,
    geometry: Dict[str, Any],
    source_handle: Any = None,
    target_handle: Any = None,
) -> Tuple[_RouteAnchor, _RouteAnchor]:
    source_anchor = _route_anchor(geometry.get("sourceAnchor")) or _handle_anchor(source_handle)
    target_anchor = _route_anchor(geometry.get("targetAnchor")) or _handle_anchor(target_handle)
    if source_anchor is None and target_anchor is None:
        source_anchor = _radial_box_anchor(source, _profile_center(source), _profile_center(target))
        target_anchor = _radial_box_anchor(target, _profile_center(target), _profile_center(source))
    elif source_anchor is None:
        source_anchor = _radial_box_anchor(source, _profile_center(source), _anchor_point(target, target_anchor))
    elif target_anchor is None:
        target_anchor = _radial_box_anchor(target, _profile_center(target), _anchor_point(source, source_anchor))
    return source_anchor, target_anchor


_SIDES = ("top", "bottom", "left", "right")


#: Boxes are grown by this much when testing whether a route hits one. A line that runs
#: exactly along a node's edge is not technically through it and reads as though it is.
_CLEARANCE = 6.0


def _segment_hits_box(a: _Point, b: _Point, box: "_Box", margin: float = -_CLEARANCE) -> bool:
    """Whether an axis-aligned segment passes through *box*, or hugs its edge."""
    left, right = box.x + margin, box.right - margin
    top, bottom = box.y + margin, box.bottom - margin
    if right <= left or bottom <= top:
        return False
    if abs(a[1] - b[1]) < 0.001:
        low, high = sorted((a[0], b[0]))
        return top < a[1] < bottom and low < right and left < high
    if abs(a[0] - b[0]) < 0.001:
        low, high = sorted((a[1], b[1]))
        return left < a[0] < right and low < bottom and top < high
    return False


def _route_crossings(points: List[_Point], blockers) -> int:
    return sum(
        1 for box in blockers
        if any(_segment_hits_box(a, b, box) for a, b in zip(points, points[1:]))
    )


def _faces_clear_of(source: "_Box", target: "_Box", anchors, blockers, crowding=None):
    """Pick the pair of faces whose route does not run through a third node.

    The natural faces are chosen from the two boxes alone and are nearly always right.
    They are wrong when something sits between them, and no amount of extra spacing helps:
    widening the gaps by half leaves the count unchanged and doubling it makes the count
    worse, because the obstruction is in the corridor the route has to use, not in the
    distance it travels.

    `crowding` reports how many *other* edges already aim at a given face of the target,
    and it is consulted only to break a tie between faces that are equally clear. Without
    it the search took the first clear face it found and stopped, which on a rewired edge
    meant landing on a face another edge was already using — clear of every node, and
    arriving alongside its neighbour after running the length of a third one.
    """
    if not blockers:
        return anchors

    def score(pair):
        first, second = pair
        # Obstacle-aware within the pair too. Of the two L-shapes a face pair allows, one
        # often misses what the other hits; judging the pair on the wrong L condemns a
        # face that was fine, and sends three parts of one whole onto three faces.
        route = _minimal_anchored_route(
            _anchor_point(source, first), _anchor_point(target, second), first, second, blockers
        )
        crowd = crowding(str(second["side"])) if crowding is not None else 0
        return (
            _route_crossings(route, blockers), crowd,
            _route_bend_count(route), _route_length(route),
        )

    best, best_score = anchors, score(anchors)
    if best_score[0] == 0:
        return anchors
    # Only faces that point at the other node are eligible. Without this the search will
    # cheerfully leave the top of a block to reach one below it: fewer crossings, and a
    # picture nobody can follow. A clear route matters less than an edge that leaves in
    # the direction it is going.
    for source_side in _facing(source, target):
        for target_side in _facing(target, source):
            candidate = (
                {"side": source_side, "offset": 0.5},
                {"side": target_side, "offset": 0.5},
            )
            candidate_score = score(candidate)
            if candidate_score < best_score:
                best, best_score = candidate, candidate_score
                # Stop at the first face pair that is both clear *and* unoccupied.
                #
                # Stopping on `clear` alone was the defect: `_facing` puts the most direct
                # face first, so a rewired edge took it as soon as it crossed nothing, and
                # the other terms were never read. That is right whenever the face is free
                # — it is why three parts of one whole fan onto left, top and right rather
                # than scattering — and wrong when the face is already taken, which is how
                # an edge ended up running the length of a third node to arrive beside its
                # neighbour on a face it had to share.
                if candidate_score[0] == 0 and candidate_score[1] == 0:
                    return best
    return best


def _facing(box: "_Box", other: "_Box") -> Tuple[str, ...]:
    """The faces of *box* that point towards *other*, nearest first."""
    dx, dy = other.cx - box.cx, other.cy - box.cy
    horizontal = "right" if dx >= 0 else "left"
    vertical = "bottom" if dy >= 0 else "top"
    return (vertical, horizontal) if abs(dy) >= abs(dx) else (horizontal, vertical)


def _fan_out_anchors(
    edges: List[Dict[str, Any]],
    boxes: Dict[str, "_Box"],
) -> Dict[int, Dict[str, _RouteAnchor]]:
    """Spread endpoints that would otherwise be drawn on the same point.

    Anchors are chosen per edge, so several edges reaching the same side of the same node
    all get the centre of that side and land on top of one another. The picture then shows
    one line where there are several, with their markers stacked — three compositions into
    one block read as an unrelated chain of parts.

    This regroups the automatic anchors by (node, side) and spreads each group evenly.
    Members are ordered by where their *other* end sits along that side's axis, so the
    fan opens without the lines crossing each other.

    Authored anchors, explicit handles, and manual waypoints are left untouched: a user
    who positioned an edge outranks this.
    """
    base: Dict[int, Tuple[_RouteAnchor, _RouteAnchor]] = {}
    natural: Dict[int, Tuple[_RouteAnchor, _RouteAnchor]] = {}

    # Which faces the edges are already aiming at, worked out before any of them is moved.
    # Face choice is otherwise made one edge at a time with no knowledge of the others,
    # which is the same blind spot that makes the spreading below necessary at all.
    aimed_at: Counter = Counter()
    for edge in edges:
        source = boxes.get(edge.get("source"))
        target = boxes.get(edge.get("target"))
        if source is None or target is None:
            continue
        geometry = edge.get("route") if isinstance(edge.get("route"), dict) else {}
        # An authored anchor counts where it was put; everything else counts where routing
        # would naturally send it. Handles are ignored here on purpose, so this pass is the
        # same two lines in both implementations — it is a tiebreak, not a contract.
        authored = _route_anchor(geometry.get("targetAnchor"))
        side = str((authored or _automatic_anchors(source, target)[1])["side"])
        aimed_at[(edge.get("target"), side)] += 1

    for index, edge in enumerate(edges):
        source = boxes.get(edge.get("source"))
        target = boxes.get(edge.get("target"))
        if source is None or target is None:
            continue
        geometry = edge.get("route") if isinstance(edge.get("route"), dict) else {}
        if (
            _route_anchor(geometry.get("sourceAnchor"))
            or _route_anchor(geometry.get("targetAnchor"))
            or geometry.get("waypoints")
            or edge.get("sourceHandle")
            or edge.get("targetHandle")
        ):
            continue
        if geometry.get("mode") == "straight":
            base[index] = _automatic_straight_anchors(source, target, geometry)
            natural[index] = base[index]
            continue
        anchors = _automatic_anchors(source, target)
        natural[index] = anchors
        # Faces are chosen before offsets are spread, because an edge moved onto a
        # different face to dodge a node would otherwise land on whatever already sits
        # there. Nothing else in the diagram is known at the time the natural anchors are
        # picked, so an edge can be sent straight through a third node — on a fork whose
        # bar is narrower than the branch below it, that puts the outer two branches
        # through the middle one and the picture claims the middle branch feeds them.
        blockers = [
            box for node_id, box in boxes.items()
            if node_id not in (edge["source"], edge["target"])
            and (box.node.get("data") or {}).get("semanticType") not in CONTAINER_SEMANTIC_TYPES
        ]
        own_side = str(anchors[1]["side"])
        target_id = edge.get("target")

        def crowding(side: str, _target_id=target_id, _own=own_side) -> int:
            """Other edges aiming at this face of the target — this one not counted."""
            return aimed_at[(_target_id, side)] - (1 if side == _own else 0)

        base[index] = _faces_clear_of(source, target, anchors, blockers, crowding)

    # Grouped by (node, side) only. An edge leaving a side and another arriving at it are
    # two points on the same stretch of boundary, so they compete for the same space and
    # have to be spread together — keying on source-versus-target would leave each a
    # singleton, both parked at the centre.
    groups: Dict[Tuple[str, str], List[Tuple[int, str]]] = {}
    for index, (source_anchor, target_anchor) in base.items():
        groups.setdefault((edges[index]["source"], str(source_anchor["side"])), []).append((index, "source"))
        groups.setdefault((edges[index]["target"], str(target_anchor["side"])), []).append((index, "target"))

    # An override is a *change* from what routing would work out on its own, so a face
    # moved to dodge a node is carried even when it is the only edge on that face.
    overrides: Dict[int, Dict[str, _RouteAnchor]] = {}
    for index, (source_anchor, target_anchor) in base.items():
        natural_source, natural_target = natural[index]
        moved = {}
        # Compared whole, side *and* offset. Comparing only the side meant that when
        # `_faces_clear_of` kept a face but moved the point along it, the move was dropped
        # and the natural offset drawn instead — so the route that got scored as clear was
        # not the route that appeared.
        #
        # A rewired edge showed it: the winning pair left the source on `bottom` and slid
        # it to the middle of the node, which put the line clear of everything. Only the
        # target's face had changed, so only the target was carried, and the line was drawn
        # from the natural offset — directly above the node it was supposed to avoid, and
        # straight down through it.
        if source_anchor != natural_source:
            moved["sourceAnchor"] = source_anchor
        if target_anchor != natural_target:
            moved["targetAnchor"] = target_anchor
        if moved:
            overrides[index] = moved

    for (node_id, side), members in groups.items():
        if len(members) < 2:
            continue
        # Spread only what would actually collide.
        #
        # This used to spread on group size alone, and the premise it was written against
        # — "several edges reaching the same side all get the centre of that side" — is
        # only true when the two boxes do not overlap. When they do, `_automatic_anchors`
        # derives the offset from the *overlap* and the edges are already far apart and
        # already drawn straight. Re-spacing them evenly then took two clean vertical
        # lines and put a two-bend dog-leg in each, for no benefit: a person straightened
        # them in the editor, saved, and the next render bent them back, because the
        # anchors that bend them are recomputed rather than stored.
        def _far_position(member: Tuple[int, str]) -> float:
            index, end = member
            edge = edges[index]
            other = boxes.get(edge["target"] if end == "source" else edge["source"])
            if other is None:
                return 0.0
            return other.cx if side in ("top", "bottom") else other.cy

        ordered = sorted(members, key=_far_position)
        spread = {
            index: {"side": side, "offset": (rank + 1) / (len(ordered) + 1)}
            for rank, (index, _end) in enumerate(ordered)
        }
        box = boxes.get(node_id)
        if box is not None and _spreading_only_makes_it_worse(
            box, side, ordered, spread, base, edges, boxes
        ):
            continue
        for rank, (index, end) in enumerate(ordered):
            key = "sourceAnchor" if end == "source" else "targetAnchor"
            overrides.setdefault(index, {})[key] = spread[index]
    return overrides


#: How far apart two endpoints on one side have to be before spreading leaves them alone.
#: An arrowhead is about 10px across, so this is roughly two of them — enough that the
#: markers do not touch, and small enough that a genuine pile-up is still fanned.
_MIN_ANCHOR_GAP = 22.0


def _spreading_only_makes_it_worse(
    box: "_Box",
    side: str,
    members: List[Tuple[int, str]],
    spread: Dict[int, _RouteAnchor],
    base: Dict[int, Tuple[_RouteAnchor, _RouteAnchor]],
    edges: List[Dict[str, Any]],
    boxes: Dict[str, "_Box"],
) -> bool:
    """Whether this group is better off left where it is.

    Three conditions, all of which have to hold, because each guards against a way the
    previous version of this went wrong:

    1. **The endpoints are already clear of one another.** Measured in pixels along the
       face, not in offsets: a 0.2 gap is 32px on a 160px block and 12px on a 60px one, and
       the thing being avoided is markers touching.
    2. **Leaving them alone adds no crossing.** Spreading sometimes moves an edge off a
       line that would have gone through a third node, and that is worth a bend.
    3. **Leaving them alone removes at least one bend.** Otherwise there is nothing to win
       and the even spacing is as good as anything else.

    Together they undo the spread only where it was taking two already-separated, already
    straight edges and putting a two-bend dog-leg in each — which is what it did to every
    pair of edges whose boxes overlap, because `_automatic_anchors` derives those offsets
    from the overlap and they were never going to collide.
    """
    extent = box.w if side in ("top", "bottom") else box.h
    positions = []
    for index, end in members:
        anchors = base.get(index)
        if anchors is None:
            return False
        anchor = anchors[0] if end == "source" else anchors[1]
        if str(anchor["side"]) != side:
            return False
        positions.append(float(anchor["offset"]) * extent)
    if any(
        second - first < _MIN_ANCHOR_GAP
        for first, second in zip(sorted(positions), sorted(positions)[1:])
    ):
        return False

    improved = False
    for index, end in members:
        edge = edges[index]
        source = boxes.get(edge.get("source"))
        target = boxes.get(edge.get("target"))
        if source is None or target is None:
            return False
        blockers = [
            other for node_id, other in boxes.items()
            if node_id not in (edge.get("source"), edge.get("target"))
            and (other.node.get("data") or {}).get("semanticType") not in CONTAINER_SEMANTIC_TYPES
        ]
        kept = base[index]
        moved = (
            (spread[index], kept[1]) if end == "source" else (kept[0], spread[index])
        )
        kept_route = _minimal_anchored_route(
            _anchor_point(source, kept[0]), _anchor_point(target, kept[1]),
            kept[0], kept[1], blockers,
        )
        moved_route = _minimal_anchored_route(
            _anchor_point(source, moved[0]), _anchor_point(target, moved[1]),
            moved[0], moved[1], blockers,
        )
        if _route_crossings(kept_route, blockers) > _route_crossings(moved_route, blockers):
            return False
        kept_bends = _route_bend_count(kept_route)
        moved_bends = _route_bend_count(moved_route)
        if kept_bends > moved_bends:
            return False
        if kept_bends < moved_bends:
            improved = True
    return improved


def _point_along(points: List[_Point], fraction: float) -> _Point:
    """The point *fraction* of the way along a polyline, by length."""
    total = _route_length(points)
    if total <= 0 or len(points) < 2:
        return points[0] if points else (0.0, 0.0)
    target = max(0.0, min(1.0, fraction)) * total
    walked = 0.0
    for start, end in zip(points, points[1:]):
        segment = math.hypot(end[0] - start[0], end[1] - start[1])
        if segment <= 0:
            continue
        if walked + segment >= target:
            ratio = (target - walked) / segment
            return (start[0] + (end[0] - start[0]) * ratio, start[1] + (end[1] - start[1]) * ratio)
        walked += segment
    return points[-1]


def _rects_overlap(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _clear_of_nodes(x: float, y: float, half_w: float, half_h: float, boxes) -> bool:
    for box in boxes:
        if (x + half_w > box.x and box.right > x - half_w
                and y + half_h > box.y and box.bottom > y - half_h):
            return False
    return True


def _label_point(points: List[_Point], boxes, half_w: float, half_h: float) -> _Point:
    """Where to put an edge's label so it does not sit on top of a node.

    The midpoint is the right answer almost always, and the wrong one when an edge is
    long enough to pass under something — a guard on a refusal path landing across a
    decision node and hiding half of it. Walk outwards from the middle and take the
    first position that is clear; if the whole line is covered, keep the midpoint,
    because moving it somewhere arbitrary is worse than leaving it where it belongs.
    """
    preferred = _point_along(points, 0.5)
    if _clear_of_nodes(preferred[0], preferred[1], half_w, half_h, boxes):
        return preferred
    for step in (0.08, 0.16, 0.24, 0.32, 0.4):
        for fraction in (0.5 - step, 0.5 + step):
            candidate = _point_along(points, fraction)
            if _clear_of_nodes(candidate[0], candidate[1], half_w, half_h, boxes):
                return candidate
    return preferred


def _same_point(a: _Point, b: _Point) -> bool:
    return abs(a[0] - b[0]) < 0.001 and abs(a[1] - b[1]) < 0.001


def _normalize_orthogonal_points(points: List[_Point]) -> List[_Point]:
    finite = [point for point in points if math.isfinite(point[0]) and math.isfinite(point[1])]
    deduplicated = [point for index, point in enumerate(finite) if index == 0 or not _same_point(point, finite[index - 1])]
    output: List[_Point] = []
    for point in deduplicated:
        previous = output[-1] if output else None
        before_previous = output[-2] if len(output) > 1 else None
        if before_previous and previous and (
            (abs(before_previous[0] - previous[0]) < 0.001 and abs(previous[0] - point[0]) < 0.001
             and (previous[1] - before_previous[1]) * (point[1] - previous[1]) >= 0)
            or (abs(before_previous[1] - previous[1]) < 0.001 and abs(previous[1] - point[1]) < 0.001
                and (previous[0] - before_previous[0]) * (point[0] - previous[0]) >= 0)
        ):
            output[-1] = point
        else:
            output.append(point)
    return output


def _connect_pair(start: _Point, end: _Point, horizontal_first: bool) -> List[_Point]:
    if abs(start[0] - end[0]) < 0.001 or abs(start[1] - end[1]) < 0.001:
        return [start, end]
    if horizontal_first:
        return [start, (end[0], start[1]), end]
    return [start, (start[0], end[1]), end]


def _route_via(points: List[_Point], horizontal_first: bool) -> List[_Point]:
    output: List[_Point] = []
    for index in range(1, len(points)):
        pair = _connect_pair(points[index - 1], points[index], horizontal_first if index % 2 else not horizontal_first)
        if output:
            pair = pair[1:]
        output.extend(pair)
    return _normalize_orthogonal_points(output)


def _route_length(points: List[_Point]) -> float:
    return sum(
        abs(points[index][0] - points[index - 1][0]) + abs(points[index][1] - points[index - 1][1])
        for index in range(1, len(points))
    )


def _polyline_midpoint(points: List[_Point]) -> _Point:
    if not points:
        return 0.0, 0.0
    total = _route_length(points)
    if total == 0:
        return points[0]
    traversed = 0.0
    for index in range(1, len(points)):
        start, end = points[index - 1], points[index]
        segment = abs(end[0] - start[0]) + abs(end[1] - start[1])
        if traversed + segment >= total / 2:
            ratio = (total / 2 - traversed) / segment
            return start[0] + (end[0] - start[0]) * ratio, start[1] + (end[1] - start[1]) * ratio
        traversed += segment
    return points[-1]


def _follows_side(origin: _Point, outside: _Point, side: str) -> bool:
    if side == "top":
        return abs(origin[0] - outside[0]) < 0.001 and outside[1] <= origin[1]
    if side == "bottom":
        return abs(origin[0] - outside[0]) < 0.001 and outside[1] >= origin[1]
    if side == "left":
        return abs(origin[1] - outside[1]) < 0.001 and outside[0] <= origin[0]
    return abs(origin[1] - outside[1]) < 0.001 and outside[0] >= origin[0]


def _minimal_anchored_route(
    source_point: _Point,
    target_point: _Point,
    source_anchor: _RouteAnchor,
    target_anchor: _RouteAnchor,
    blockers=(),
) -> List[_Point]:
    candidates = [
        _normalize_orthogonal_points(_connect_pair(source_point, target_point, True)),
        _normalize_orthogonal_points(_connect_pair(source_point, target_point, False)),
    ]
    candidates = [
        points for points in candidates
        if len(points) >= 2
        and _follows_side(source_point, points[1], str(source_anchor["side"]))
        and _follows_side(target_point, points[-2], str(target_anchor["side"]))
    ]
    if not candidates:
        source_stub = _outward(source_point, str(source_anchor["side"]))
        target_stub = _outward(target_point, str(target_anchor["side"]))
        candidates = [
            _normalize_orthogonal_points([source_point, *_connect_pair(source_stub, target_stub, True), target_point]),
            _normalize_orthogonal_points([source_point, *_connect_pair(source_stub, target_stub, False), target_point]),
        ]
    candidates.sort(
        key=lambda route: (_route_crossings(route, blockers), _route_bend_count(route), _route_length(route))
    )
    return candidates[0]


def _route_straight(
    source: _Box,
    target: _Box,
    geometry: Any = None,
    source_handle: Any = None,
    target_handle: Any = None,
) -> Dict[str, Any]:
    geometry = geometry if isinstance(geometry, dict) else {}
    source_anchor, target_anchor = _automatic_straight_anchors(source, target, geometry, source_handle, target_handle)
    points = [_anchor_point(source, source_anchor), _anchor_point(target, target_anchor)]
    return {
        "points": points,
        "mid": _polyline_midpoint(points),
        "sourceAnchor": source_anchor,
        "targetAnchor": target_anchor,
    }


def _route_orthogonal(
    source: _Box,
    target: _Box,
    geometry: Any = None,
    source_handle: Any = None,
    target_handle: Any = None,
    blockers=(),
) -> Dict[str, Any]:
    geometry = geometry if isinstance(geometry, dict) else {}
    automatic_source, automatic_target = _automatic_anchors(source, target)
    source_anchor = _route_anchor(geometry.get("sourceAnchor")) or _handle_anchor(source_handle) or automatic_source
    target_anchor = _route_anchor(geometry.get("targetAnchor")) or _handle_anchor(target_handle) or automatic_target
    source_point = _anchor_point(source, source_anchor)
    target_point = _anchor_point(target, target_anchor)
    raw_waypoints = geometry.get("waypoints")
    waypoints = [] if not isinstance(raw_waypoints, list) else [point for point in map(_route_point, raw_waypoints[:32]) if point]
    if waypoints:
        source_stub = _outward(source_point, str(source_anchor["side"]))
        target_stub = _outward(target_point, str(target_anchor["side"]))
        points = _route_via([source_point, source_stub, *waypoints, target_stub, target_point], True)
    else:
        points = _minimal_anchored_route(
            source_point, target_point, source_anchor, target_anchor, blockers
        )
    return {
        "points": points,
        "mid": _polyline_midpoint(points),
        "sourceAnchor": source_anchor,
        "targetAnchor": target_anchor,
    }


def _segment_direction(start: _Point, end: _Point) -> _Point:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    return (0.0, 0.0) if length < 0.001 else (dx / length, dy / length)


def _route_bend_count(points: List[_Point]) -> int:
    bends = 0
    for index in range(2, len(points)):
        first, middle, last = points[index - 2], points[index - 1], points[index]
        if (abs(first[0] - middle[0]) < 0.001) != (abs(middle[0] - last[0]) < 0.001):
            bends += 1
    return bends


def _num(value: Any, default: float) -> float:
    """Coerce *value* to a finite float, falling back to *default*.

    Non-finite values (NaN/inf) fall back too, so a malformed coordinate/size
    never reaches the SVG output as ``nan``/``inf`` (e.g. via the path-free,
    pre-validation preview render route).
    """
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _node_size(node: Dict[str, Any]) -> Tuple[float, float]:
    data = node.get("data") or {}
    semantic = data.get("semanticType")
    dw, dh = DEFAULT_NODE_SIZES.get(semantic, FALLBACK_SIZE)
    return _num(node.get("width"), dw), _num(node.get("height"), dh)


def _wrap_text(text: str, max_chars: int) -> List[str]:
    """Greedily wrap *text* into lines of at most *max_chars*, hard-breaking any
    single word that is itself longer than a line so nothing exceeds the width."""
    lines: List[str] = []
    current = ""
    for word in text.split():
        while len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _fit_text(
    text: str,
    max_width: float,
    max_height: Optional[float] = None,
    *,
    base_font: float = FONT_SIZE,
    min_font: float = MIN_FONT_SIZE,
) -> Tuple[List[str], float]:
    """Fit *text* within *max_width* x *max_height*: word-wrap, then shrink the
    font toward *min_font*, then clamp the line count with a trailing ellipsis.
    Returns the wrapped lines and the font size to draw them at."""
    text = text.strip()
    if not text:
        return [""], base_font
    width = max(1.0, max_width)
    font = base_font
    lines = [text]
    while True:
        max_chars = max(1, int(width / (font * CHAR_WIDTH_RATIO)))
        lines = _wrap_text(text, max_chars)
        fits_height = max_height is None or len(lines) * font * LINE_HEIGHT <= max_height
        if fits_height or font <= min_font:
            break
        font -= 1
    if max_height is not None:
        max_lines = max(1, int(max_height / (font * LINE_HEIGHT)))
        if len(lines) > max_lines:
            max_chars = max(1, int(width / (font * CHAR_WIDTH_RATIO)))
            lines = lines[:max_lines]
            last = lines[-1]
            if len(last) >= max_chars:
                last = last[: max_chars - 1].rstrip()
            lines[-1] = f"{last}\u2026"
    return lines, font


def _text_area(box: _Box, shape: str) -> Tuple[float, Optional[float]]:
    """Usable (width, height) for a centred label inside *shape*. Non-rectangular
    shapes expose less drawable width/height than their bounding box."""
    if shape == "diamond":
        return box.w * 0.6, box.h * 0.6
    if shape == "ellipse":
        return box.w * 0.72, box.h * 0.72
    if shape == "actor":  # label sits beneath the figure
        return box.w, box.h * 0.3
    if shape == "note":
        # The label is drawn centred half a fold *below* the box centre to balance the
        # dog-ear, so that much height is unusable at the bottom. Claiming the full
        # height here pushed the last line out through the base of the note.
        fold = min(14.0, box.w / 4, box.h / 2)
        return (
            max(1.0, box.w - fold - TEXT_PADDING * 2),
            max(1.0, box.h - fold - TEXT_PADDING * 2),
        )
    return max(1.0, box.w - TEXT_PADDING * 2), box.h  # rect / rounded-rect


def _resolve_boxes(nodes: List[Dict[str, Any]]) -> Dict[str, _Box]:
    """Resolve every node to an absolute ``_Box``.

    ``parentId`` children store positions relative to their parent (React Flow
    semantics), so a child's absolute position is the parent's absolute position
    plus its own. Missing parents are treated as absolute; cycles are broken.
    """
    by_id: Dict[str, Dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if isinstance(node_id, str):
            by_id[node_id] = node

    resolved: Dict[str, _Box] = {}
    resolving: set[str] = set()

    def resolve(node_id: str) -> Tuple[float, float]:
        node = by_id[node_id]
        pos = node.get("position") or {}
        x, y = _num(pos.get("x"), 0.0), _num(pos.get("y"), 0.0)
        parent_id = node.get("parentId")
        if isinstance(parent_id, str) and parent_id in by_id and parent_id not in resolving:
            resolving.add(node_id)
            px, py = resolve(parent_id)
            resolving.discard(node_id)
            x, y = px + x, py + y
        return x, y

    for node_id, node in by_id.items():
        ax, ay = resolve(node_id)
        w, h = _node_size(node)
        resolved[node_id] = _Box(ax, ay, w, h, node)
    return resolved


def _resolve_node_style(node: Dict[str, Any]) -> Dict[str, Any]:
    style = node.get("style") or {}
    return {key: style.get(key, default) for key, default in STYLE_DEFAULTS.items()}


def _dash_for(border_style: Any, border_width: float) -> Optional[str]:
    if border_style == "dashed":
        return f"{border_width * 4},{border_width * 3}"
    if border_style == "dotted":
        return f"{border_width},{border_width * 2}"
    return None


# ---------------------------------------------------------------------------
# Rasterization (SVG -> PNG)
# ---------------------------------------------------------------------------


def _rasterize_svg_to_png(
    svg: str,
    natural_width: float,
    natural_height: float,
    *,
    scale: float,
    max_px: Optional[int],
) -> bytes:
    """Rasterize an *svg* string to PNG bytes via ``resvg`` (a pure wheel; no Cairo).

    The PNG is the same picture the editor's client-side export produces — the editor
    rasterizes this very SVG in a browser ``<canvas>``; here ``resvg`` does it so the
    MCP tools / agents get a PNG without a browser. Output is scaled by *scale*
    (default 2x, matching the editor) but, when *max_px* is set, never exceeds that on
    its longest side. ``resvg`` is imported
    lazily so the SVG renderer (and the whole backend) still imports without the wheel.
    """
    try:
        import resvg_py  # noqa: PLC0415 — lazy: PNG is optional; keep it off the SVG hot path
    except ImportError as exc:  # pragma: no cover - only hit when the optional wheel is absent
        raise RasterizationError(
            "PNG rasterization requires the 'resvg-py' package "
            "(install it via 'pip install -r requirements.txt')."
        ) from exc

    longest = max(float(natural_width), float(natural_height), 1.0)
    zoom = scale
    if max_px is not None and longest * zoom > max_px:
        zoom = max_px / longest
    try:
        png = resvg_py.svg_to_bytes(
            svg_string=svg,
            background=RASTER_BACKGROUND,
            sans_serif_family=RASTER_SANS_FONT,
            zoom=zoom,
        )
    except Exception as exc:  # noqa: BLE001 — resvg surfaces ValueError/RuntimeError variants
        raise RasterizationError(f"Could not rasterize the diagram to PNG: {exc}") from exc
    return bytes(png)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class DiagramRenderService:
    """Render a canonical GraphPilot diagram to SVG (mirrors the editor's shapes)."""

    # -- public API ----------------------------------------------------------

    def to_svg(self, diagram: Dict[str, Any]) -> str:
        """Render *diagram* to an SVG string. Pure: performs no file I/O.

        Raises:
            DiagramRenderServiceError: if *diagram* is not a canonical diagram dict.
        """
        return self._build_drawing(diagram).as_svg()

    def to_png(
        self,
        diagram: Dict[str, Any],
        *,
        scale: float = RASTER_SCALE,
        max_px: Optional[int] = RASTER_MAX_PX,
    ) -> bytes:
        """Render *diagram* to PNG bytes. Pure: performs no file I/O.

        Derived from the same SVG :meth:`to_svg` emits (one canonical renderer), then
        rasterized with ``resvg``. *scale* multiplies the natural size; *max_px* caps
        the longest side (pass ``None`` for the full, uncapped artifact). Mirrors the
        editor's client-side SVG→PNG export so editor and agents share one picture.

        Raises:
            DiagramRenderServiceError: if *diagram* is not a canonical diagram dict.
            RasterizationError: if the ``resvg`` rasterizer is unavailable or fails.
        """
        drawing = self._build_drawing(diagram)
        return _rasterize_svg_to_png(
            drawing.as_svg(), drawing.width, drawing.height, scale=scale, max_px=max_px
        )

    def _build_drawing(self, diagram: Dict[str, Any]) -> draw.Drawing:
        """Validate *diagram* and build the ``drawsvg`` drawing shared by SVG + PNG.

        Raises:
            DiagramRenderServiceError: if *diagram* is not a canonical diagram dict.
        """
        if not isinstance(diagram, dict):
            raise DiagramRenderServiceError(
                f"diagram must be a dict; got {type(diagram).__name__}."
            )
        nodes = diagram.get("nodes")
        edges = diagram.get("edges") or []
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise DiagramRenderServiceError(
                "diagram must contain list 'nodes' and 'edges'."
            )
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise DiagramRenderServiceError(f"nodes[{index}] must be an object.")
            if not isinstance(node.get("position"), dict):
                raise DiagramRenderServiceError(f"nodes[{index}].position must be an object.")
            if not isinstance(node.get("data"), dict):
                raise DiagramRenderServiceError(f"nodes[{index}].data must be an object.")
            if "style" in node and not isinstance(node.get("style"), dict):
                raise DiagramRenderServiceError(f"nodes[{index}].style must be an object.")
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise DiagramRenderServiceError(f"edges[{index}] must be an object.")
            if "data" in edge and not isinstance(edge.get("data"), dict):
                raise DiagramRenderServiceError(f"edges[{index}].data must be an object.")
            if "style" in edge and not isinstance(edge.get("style"), dict):
                raise DiagramRenderServiceError(f"edges[{index}].style must be an object.")

        boxes = _resolve_boxes(nodes)
        fan_out = _fan_out_anchors(edges, boxes)
        routed_edges = [
            (edge, self._edge_route(edge, boxes, edges, fan_out.get(index)))
            for index, edge in enumerate(edges)
        ]
        drawing = self._new_drawing(boxes.values(), routed_edges)

        # Nothing to admit when there is nothing to admit it against: see
        # `_drawn_entirely_by_hand`.
        badges = not _drawn_entirely_by_hand(nodes, edges)

        # Draw order: containers (behind) -> edges -> remaining nodes -> labels on top.
        containers = [b for b in boxes.values() if self._semantic(b) in CONTAINER_SEMANTIC_TYPES]
        others = [b for b in boxes.values() if self._semantic(b) not in CONTAINER_SEMANTIC_TYPES]

        for box in containers:
            self._draw_node(drawing, box, badges=badges)
        for edge, route in routed_edges:
            self._draw_edge(drawing, edge, boxes, route)
        for box in others:
            self._draw_node(drawing, box, badges=badges)
        # Labels go on last, and may slide along their edge to avoid landing on a node or
        # on a label already placed. Containers are not obstacles: an edge label inside a
        # system boundary is normal.
        placed_labels: List[Tuple[float, float, float, float]] = []
        for edge, route in routed_edges:
            self._draw_edge_labels(drawing, edge, route, obstacles=others, placed=placed_labels)

        return drawing

    def render(self, diagram_path: Union[str, Path]) -> Path:
        """Load the saved diagram at *diagram_path*, render it, and write the sibling SVG.

        Path safety, loading, and the atomic write all go through
        :class:`WorkspaceStorageService`. The SVG is written to ``<name>.svg`` beside the
        source ``<name>.gp.json``.

        Returns:
            The resolved ``Path`` to the written ``.svg`` file.

        Raises:
            UnsafePathError / DiagramNotFoundError / InvalidDiagramJSONError: from
                :class:`WorkspaceStorageService` for unsafe, missing, or malformed input.
            DiagramRenderServiceError: if the loaded diagram cannot be rendered.
        """
        file_service = WorkspaceStorageService.for_diagram_path(diagram_path)
        safe_source = file_service.resolve_safe_path(diagram_path)
        diagram = file_service.load_diagram(safe_source)
        svg = self.to_svg(diagram)
        svg_path = self.artifact_sibling(safe_source, ".svg")
        return file_service.write_text(svg_path, svg)

    def render_png(
        self,
        diagram_path: Union[str, Path],
        *,
        scale: float = RASTER_SCALE,
        max_px: Optional[int] = None,
    ) -> Path:
        """Load the saved diagram at *diagram_path*, rasterize it, and write ``<name>.png``.

        The explicit "save the full image" path (the ``diagram_render`` PNG option):
        unlike the bounded in-memory default, *max_px* defaults to ``None`` so the saved
        artifact is the full ``scale``× picture. Path safety, loading, and the atomic
        write all go through :class:`WorkspaceStorageService`; the PNG is written beside the
        source ``<name>.gp.json``.

        Returns:
            The resolved ``Path`` to the written ``.png`` file.

        Raises:
            UnsafePathError / DiagramNotFoundError / InvalidDiagramJSONError: from
                :class:`WorkspaceStorageService` for unsafe, missing, or malformed input.
            DiagramRenderServiceError / RasterizationError: if the loaded diagram
                cannot be rendered or rasterized.
        """
        file_service = WorkspaceStorageService.for_diagram_path(diagram_path)
        safe_source = file_service.resolve_safe_path(diagram_path)
        diagram = file_service.load_diagram(safe_source)
        png = self.to_png(diagram, scale=scale, max_px=max_px)
        png_path = self.artifact_sibling(safe_source, ".png")
        return file_service.write_bytes(png_path, png)

    # -- artifact paths, one owner ------------------------------------------

    @staticmethod
    def artifact_sibling(source: Path, ext: str) -> Path:
        """Return the ``<name><ext>`` path beside a ``<name>.gp.json`` source.

        Public because a caller that needs to *name* an artifact must not re-derive the
        rule. `api/views.py` did: when a render-on-save failed it hand-built
        ``name.removesuffix(".gp.json") + ".svg"`` to tell the user which file was
        missing. It agreed with this method by coincidence, and the coincidence was
        load-bearing — change where artifacts go and the failure warning would have named
        a path the renderer was never going to write, which is the one moment a user is
        relying on that string.

        *ext* includes the leading dot (e.g. ``.svg`` / ``.png``). The full multi-part
        suffix (``.gp.json``) is stripped before appending *ext* so the artifact sits
        next to the source as ``<name>.svg`` / ``<name>.png``.
        """
        name = source.name
        diagram_suffix = WorkspaceStorageService.diagram_extension()
        stem = name[: -len(diagram_suffix)] if name.endswith(diagram_suffix) else source.stem
        return source.parent / f"{stem}{ext}"

    @staticmethod
    def _semantic(box: _Box) -> Optional[str]:
        return (box.node.get("data") or {}).get("semanticType")

    def _edge_route(
        self,
        edge: Dict[str, Any],
        boxes: Dict[str, _Box],
        _edges: List[Dict[str, Any]],
        fan_out: Optional[Dict[str, _RouteAnchor]] = None,
    ) -> Optional[Dict[str, Any]]:
        source = boxes.get(edge.get("source"))
        target = boxes.get(edge.get("target"))
        if source is None or target is None:
            return None
        geometry = edge.get("route") if isinstance(edge.get("route"), dict) else {}
        if fan_out:
            # Derived spacing, not authored geometry: the saved diagram is untouched.
            geometry = {**geometry, **fan_out}
        if geometry.get("mode") == "straight":
            return _route_straight(
                source, target, geometry, edge.get("sourceHandle"), edge.get("targetHandle")
            )
        blockers = [
            box for node_id, box in boxes.items()
            if node_id not in (edge.get("source"), edge.get("target"))
            and self._semantic(box) not in CONTAINER_SEMANTIC_TYPES
        ]
        return _route_orthogonal(
            source,
            target,
            geometry,
            edge.get("sourceHandle"),
            edge.get("targetHandle"),
            blockers,
        )

    def _new_drawing(self, boxes, routed_edges) -> draw.Drawing:
        boxes = list(boxes)
        if not boxes:
            return draw.Drawing(120, 80, origin=(0, 0))
        min_x = min(b.x for b in boxes)
        min_y = min(b.y for b in boxes)
        max_x = max(b.right for b in boxes)
        max_y = max(b.bottom for b in boxes)
        for edge, route in routed_edges:
            if not route:
                continue
            points = route["points"]
            min_x = min(min_x, *(point[0] for point in points))
            min_y = min(min_y, *(point[1] for point in points))
            max_x = max(max_x, *(point[0] for point in points))
            max_y = max(max_y, *(point[1] for point in points))
            label = edge_display_label(edge)
            geometry = edge.get("route") if isinstance(edge.get("route"), dict) else {}
            offset = _route_point(geometry.get("labelOffset")) or (0.0, 0.0)
            label_x = route["mid"][0] + offset[0]
            label_y = route["mid"][1] + offset[1]
            if label:
                half_width = (len(label) * FONT_SIZE * CHAR_WIDTH_RATIO + 8) / 2
                half_height = (FONT_SIZE + 6) / 2
                min_x = min(min_x, label_x - half_width)
                max_x = max(max_x, label_x + half_width)
                min_y = min(min_y, label_y - half_height)
                max_y = max(max_y, label_y + half_height)
            item_flows = (edge.get("data") or {}).get("itemFlows") or []
            flow_text = ", ".join(str(flow.get("item")) for flow in item_flows if isinstance(flow, dict) and flow.get("item"))
            if flow_text:
                half_width = len(flow_text) * 10 * CHAR_WIDTH_RATIO / 2
                min_x = min(min_x, label_x - half_width)
                max_x = max(max_x, label_x + half_width)
                max_y = max(max_y, label_y + 24)
        min_x -= PADDING
        min_y -= PADDING
        max_x += PADDING
        max_y += PADDING
        width = max(max_x - min_x, 1)
        height = max(max_y - min_y, 1)
        d = draw.Drawing(width, height, origin=(min_x, min_y))
        d.append(draw.Rectangle(min_x, min_y, width, height, fill="#ffffff"))
        return d

    # -- node drawing --------------------------------------------------------

    def _draw_node(self, d: draw.Drawing, box: _Box, *, badges: bool = True) -> None:
        semantic = self._semantic(box)
        style = _resolve_node_style(box.node)
        label = (box.node.get("data") or {}).get("label") or ""

        # Dispatch on the element catalog's render primitive. Every current
        # semanticType maps to the same shape as before; an unknown semanticType falls
        # back to a rounded box so it still renders (matching the editor's GpNode fallback).
        primitive = node_primitive(semantic)
        if primitive == "note":
            self._draw_note(d, box, style, label)
        elif primitive == "diamond":
            self._draw_diamond(d, box, style, label)
        elif primitive == "actor":
            self._draw_actor(d, box, style, label)
        elif primitive == "ellipse":
            self._draw_ellipse(d, box, style, label)
        elif primitive == "container":
            self._draw_boundary(d, box, style, label)
        elif primitive == "classifier-box":
            self._draw_classifier(d, box, style, label)
        elif primitive == "initial":
            self._draw_initial_node(d, box, style, label)
        elif primitive == "final":
            self._draw_final_node(d, box, style, label)
        elif primitive == "flow-final":
            self._draw_flow_final_node(d, box, style, label)
        elif primitive == "bar":
            self._draw_bar(d, box, style, label)
        elif primitive == "object":
            self._draw_object_node(d, box, style, label)
        elif primitive == "datastore":
            self._draw_object_node(d, box, style, label, keyword="datastore")
        elif primitive == "pin":
            self._draw_pin(d, box, style, label)
        elif primitive in ("partition", "region"):
            self._draw_region(d, box, style, label, dashed=primitive == "region")
        elif primitive == "send-signal":
            self._draw_signal(d, box, style, label, accepting=False)
        elif primitive == "accept-event":
            self._draw_signal(d, box, style, label, accepting=True)
        elif primitive == "port":
            self._draw_port(d, box, style, label)
        else:
            # rounded-rect primitive (action) and any unknown semanticType.
            self._draw_rounded_rect(d, box, style, label, radius=8)

        if badges:
            self._draw_assurance_badge(d, box)

    #: Assurance values that earn a badge, and the glyph each is drawn with.
    #:
    #: Both are admissions. `assumed` is a judgement the source does not establish; `user`
    #: is something a person drew on the canvas, which no draft authored and no citation
    #: backs. `grounded` is the norm in a repository-backed diagram, so badging it would
    #: teach a reader to ignore badges, and `conceptual` describes a whole diagram rather
    #: than one element.
    _BADGES = {
        "assumed": ("?", "#fff4e0", "#8a5a00", "#d9a441"),
        "user": ("\u270e", "#eef2ff", "#3b4a8c", "#8b9adc"),
    }

    def _draw_assurance_badge(self, d: draw.Drawing, box: _Box) -> None:
        """Mark an assumed or hand-drawn element, exactly as the canvas does.

        The canvas has badged `assumed` since the draft contract existed. The export never
        did — so the one artifact a reader is most likely to be shown, in a document or a
        pull request, was the one that could not distinguish a cited fact from a guess.
        Parity is the rule here for a reason: a picture that quietly drops the honesty
        marking is worse than one that never had it, because nobody knows to look.
        """
        origin = box.node.get("origin") or {}
        badge = self._BADGES.get(origin.get("assurance"))
        if not badge:
            return
        glyph, fill, text, stroke = badge
        # Top-right of the shape a reader can see, straddling the corner, matching
        # `.gp-assumed` in the editor's CSS. The visible primitive is not always the
        # layout box: an initial node's 30px disc sits inside a 90x60 box, so anchoring
        # to the box left the badge floating 30px clear of the thing it marks.
        _, (bx, by, bw, _bh) = _attachment_profile(box)
        cx, cy, r = bx + bw, by, 9
        d.append(draw.Circle(cx, cy, r, fill=fill, stroke=stroke, stroke_width=1.5))
        d.append(draw.Text(
            glyph, 12, cx, cy,
            fill=text, font_family="system-ui, sans-serif", font_weight="700",
            text_anchor="middle", dominant_baseline="central",
        ))

    def _stroke_kwargs(self, style: Dict[str, Any]) -> Dict[str, Any]:
        bw = _num(style["borderWidth"], 1)
        kwargs = {
            "stroke": style["borderColor"],
            "stroke_width": bw,
            "fill": style["background"],
        }
        dash = _dash_for(style["borderStyle"], bw)
        if dash:
            kwargs["stroke_dasharray"] = dash
        return kwargs

    def _label(
        self,
        d: draw.Drawing,
        x: float,
        y: float,
        text: str,
        color: str,
        *,
        bold: bool = False,
        max_width: Optional[float] = None,
        max_height: Optional[float] = None,
        grow: str = "center",
    ) -> None:
        if not text:
            return
        # When a bounding width is given, fit the label (wrap / shrink / ellipsis);
        # otherwise keep the legacy single-line behaviour. Each
        # wrapped line is its own centred Text element so vertical placement is
        # explicit (no reliance on drawsvg multi-line handling).
        if max_width is not None:
            lines, font_size = _fit_text(str(text), max_width, max_height)
        else:
            lines, font_size = [str(text)], float(FONT_SIZE)
        kwargs: Dict[str, Any] = {
            "center": True,
            "fill": color,
            "font_family": FONT_FAMILY,
        }
        if bold:
            kwargs["font_weight"] = 600
        line_h = font_size * LINE_HEIGHT
        # "center" balances the block around y; "top" keeps the first line at y and
        # grows downward (for labels anchored near a shape's top, e.g. BDD blocks).
        start_y = y if grow == "top" else y - (len(lines) - 1) * line_h / 2
        for i, line in enumerate(lines):
            d.append(draw.Text(line, font_size, x, start_y + i * line_h, **kwargs))

    def _draw_rounded_rect(self, d, box, style, label, *, radius, bold=False) -> None:
        d.append(draw.Rectangle(box.x, box.y, box.w, box.h, rx=radius, ry=radius, **self._stroke_kwargs(style)))
        w, h = _text_area(box, "rect")
        self._label(d, box.cx, box.cy, label, style["color"], bold=bold, max_width=w, max_height=h)

    def _draw_diamond(self, d, box, style, label) -> None:
        pts = [box.cx, box.y, box.right, box.cy, box.cx, box.bottom, box.x, box.cy]
        d.append(draw.Lines(*pts, close=True, **self._stroke_kwargs(style)))
        w, h = _text_area(box, "diamond")
        self._label(d, box.cx, box.cy, label, style["color"], max_width=w, max_height=h)

    def _draw_ellipse(self, d, box, style, label) -> None:
        d.append(draw.Ellipse(box.cx, box.cy, box.w / 2, box.h / 2, **self._stroke_kwargs(style)))
        extension_points = (box.node.get("data") or {}).get("extensionPoints") or []
        w, h = _text_area(box, "ellipse")
        self._label(d, box.cx, box.cy - (10 if extension_points else 0), label, style["color"], max_width=w, max_height=h)
        if extension_points:
            y = box.cy + 8
            d.append(draw.Line(box.x + box.w * 0.12, y, box.right - box.w * 0.12, y, stroke=style["borderColor"], stroke_width=1))
            d.append(draw.Text("extension points", 9, box.cx, y + 11, center=True, fill=style["color"], font_family=FONT_FAMILY, font_style="italic"))
            d.append(draw.Text(", ".join(str(v) for v in extension_points), 9, box.cx, y + 22, center=True, fill=style["color"], font_family=FONT_FAMILY))

    def _draw_note(self, d, box, style, label) -> None:
        fold = min(14.0, box.w / 4, box.h / 2)
        x, y, r, b = box.x, box.y, box.right, box.bottom
        path = draw.Path(**self._stroke_kwargs(style))
        path.M(x, y).L(r - fold, y).L(r, y + fold).L(r, b).L(x, b).Z()
        d.append(path)
        # The folded-corner triangle.
        fold_line = draw.Path(fill="none", stroke=style["borderColor"], stroke_width=_num(style["borderWidth"], 1))
        fold_line.M(r - fold, y).L(r - fold, y + fold).L(r, y + fold)
        d.append(fold_line)
        w, h = _text_area(box, "note")
        self._label(d, box.cx, box.cy + fold / 2, label, style["color"], max_width=w, max_height=h)

    def _draw_boundary(self, d, box, style, label) -> None:
        # Transparent container drawn behind its contents, with a top label.
        kwargs = self._stroke_kwargs(style)
        kwargs["fill"] = "none"
        d.append(draw.Rectangle(box.x, box.y, box.w, box.h, rx=8, ry=8, **kwargs))
        if label:
            d.append(
                draw.Text(
                    str(label),
                    FONT_SIZE,
                    box.x + 10,
                    box.y + 16,
                    fill=style["color"],
                    font_family=FONT_FAMILY,
                    font_weight=600,
                )
            )

    def _draw_actor(self, d, box, style, label) -> None:
        stroke = style["borderColor"]
        bw = _num(style["borderWidth"], 1)
        # Stick figure occupying the upper part of the box; label beneath.
        _, (figure_x, figure_y, _, _) = _attachment_profile(box)
        origin_x = figure_x - 5
        origin_y = figure_y - 2
        cx = origin_x + 17
        head_cy = origin_y + 8
        body_top = origin_y + 14
        body_bottom = origin_y + 30
        arm_y = origin_y + 20
        leg_y = origin_y + 44
        common = {"stroke": stroke, "stroke_width": bw, "fill": "none", "stroke_linecap": "round"}
        d.append(draw.Circle(cx, head_cy, 6, stroke=stroke, stroke_width=bw, fill=style["background"]))
        d.append(draw.Line(cx, body_top, cx, body_bottom, **common))
        d.append(draw.Line(origin_x + 5, arm_y, origin_x + 29, arm_y, **common))
        d.append(draw.Line(cx, body_bottom, origin_x + 7, leg_y, **common))
        d.append(draw.Line(cx, body_bottom, origin_x + 27, leg_y, **common))
        w, h = _text_area(box, "actor")
        self._label(d, cx, box.bottom - 8, label, style["color"], max_width=w, max_height=h)

    def _draw_classifier(self, d, box, style, label) -> None:
        stroke = style["borderColor"]
        bw = _num(style["borderWidth"], 1)
        d.append(draw.Rectangle(box.x, box.y, box.w, box.h, **self._stroke_kwargs(style)))
        compartments = feature_compartments((box.node.get("data") or {}).get("features"))
        header_h = min(34.0, box.h)
        if compartments:
            d.append(draw.Line(box.x, box.y + header_h, box.right, box.y + header_h, stroke=stroke, stroke_width=bw))
        semantic = self._semantic(box) or ""
        data = box.node.get("data") or {}
        keyword_by_semantic = {
            "block": "block", "valueType": "valueType", "constraintBlock": "constraint",
            "interfaceBlock": "interfaceBlock", "enumeration": "enumeration",
            "propertySpecificType": "propertySpecificType", "associationBlock": "block",
            "unit": "unit", "quantityKind": "quantityKind", "interface": "interface",
            "component": "component", "requirement": "requirement",
        }
        primary = data.get("stereotype")
        keyword = primary.strip() if semantic == "block" and isinstance(primary, str) and primary.strip() else keyword_by_semantic.get(semantic, "")
        if compartments:
            keyword_y = box.y + 12
            label_y = box.y + (25 if keyword else 20)
            label_height = header_h - 14
            label_grow = "top"
        else:
            keyword_y = box.cy - 7
            label_y = box.cy + 7 if keyword else box.cy
            label_height = box.h - (20 if keyword else 8)
            label_grow = "center"
        if keyword:
            d.append(draw.Text(
                stereotype_text(keyword), 10, box.cx, keyword_y,
                center=True, fill=style["color"], font_family=FONT_FAMILY, font_style="italic",
            ))
        self._label(
            d, box.cx, label_y, label, style["color"],
            bold=True, max_width=max(1.0, box.w - TEXT_PADDING * 2),
            max_height=max(1.0, label_height), grow=label_grow,
        )
        if compartments:
            self._draw_classifier_compartments(d, box, style, stroke, bw, header_h)

    def _draw_classifier_compartments(self, d, box, style, stroke, bw, header_h) -> None:
        compartments = feature_compartments((box.node.get("data") or {}).get("features"))
        line_h = FONT_SIZE * LINE_HEIGHT
        text_x = box.x + TEXT_PADDING
        y = box.y + header_h
        for index, (comp_label, items) in enumerate(compartments):
            if index:
                d.append(draw.Line(box.x, y, box.right, y, stroke=stroke, stroke_width=bw))
            baseline = y + FONT_SIZE + 2
            d.append(draw.Text(
                comp_label, 10, text_x, baseline,
                fill=style["color"], font_family=FONT_FAMILY, font_style="italic",
            ))
            baseline += line_h
            # Wrap to the block's width. It is capped at LAYOUT_MAX_WIDTH, so a long
            # constraint cannot be fitted by widening; without wrapping it simply ran off
            # the right-hand edge. `bdd_compartment_rows` sizes the block for these lines.
            per_line = max(1, int(max(1.0, box.w - TEXT_PADDING * 2) / (FONT_SIZE * CHAR_WIDTH_RATIO)))
            for item in items:
                for line in _wrap_text(item, per_line):
                    d.append(draw.Text(
                        line, FONT_SIZE, text_x, baseline,
                        fill=style["color"], font_family=FONT_FAMILY,
                    ))
                    baseline += line_h
            y = baseline

    def _draw_initial_node(self, d, box, style, label) -> None:
        # UML initial node: a small solid filled disc; optional label beneath.
        bw = _num(style["borderWidth"], 1)
        fill = style["borderColor"]
        _, (x, y, width, height) = _attachment_profile(box)
        r = width / 2
        cx = x + r
        cy = y + height / 2
        d.append(draw.Circle(cx, cy, r, fill=fill, stroke=fill, stroke_width=bw))
        if label:
            w, h = _text_area(box, "actor")
            self._label(d, cx, box.bottom - 8, label, style["color"], max_width=w, max_height=h)

    def _draw_final_node(self, d, box, style, label) -> None:
        # UML activity-final node: a "bull's-eye" — a hollow ring with a solid inner dot.
        bw = _num(style["borderWidth"], 1)
        _, (x, y, width, height) = _attachment_profile(box)
        r = width / 2
        cx = x + r
        cy = y + height / 2
        d.append(draw.Circle(cx, cy, r, fill=style["background"], stroke=style["borderColor"], stroke_width=bw))
        d.append(draw.Circle(cx, cy, r * 0.5, fill=style["borderColor"], stroke="none"))
        if label:
            w, h = _text_area(box, "actor")
            self._label(d, cx, box.bottom - 8, label, style["color"], max_width=w, max_height=h)

    def _draw_flow_final_node(self, d, box, style, label) -> None:
        bw = _num(style["borderWidth"], 1)
        _, (x, y, width, height) = _attachment_profile(box)
        r = width / 2
        cx = x + r
        cy = y + height / 2
        d.append(draw.Circle(cx, cy, r, fill=style["background"], stroke=style["borderColor"], stroke_width=bw))
        d.append(draw.Line(cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55, stroke=style["borderColor"], stroke_width=bw))
        d.append(draw.Line(cx + r * 0.55, cy - r * 0.55, cx - r * 0.55, cy + r * 0.55, stroke=style["borderColor"], stroke_width=bw))
        if label:
            self._label(d, cx, box.bottom - 8, label, style["color"], max_width=box.w)

    def _draw_object_node(self, d, box, style, label, keyword=None) -> None:
        d.append(draw.Rectangle(box.x, box.y, box.w, box.h, **self._stroke_kwargs(style)))
        if keyword:
            d.append(draw.Text(stereotype_text(keyword), 10, box.cx, box.y + 14, center=True, fill=style["color"], font_family=FONT_FAMILY, font_style="italic"))
        self._label(d, box.cx, box.cy + (6 if keyword else 0), label, style["color"], max_width=box.w - TEXT_PADDING * 2, max_height=box.h - 12)

    def _draw_pin(self, d, box, style, label) -> None:
        size = min(box.w, box.h, 16.0)
        d.append(draw.Rectangle(box.cx - size / 2, box.cy - size / 2, size, size, **self._stroke_kwargs(style)))
        if label:
            self._label(d, box.cx, box.bottom - 2, label, style["color"], max_width=box.w)

    def _draw_region(self, d, box, style, label, *, dashed) -> None:
        kwargs = self._stroke_kwargs(style)
        kwargs["fill"] = "none"
        if dashed:
            kwargs["stroke_dasharray"] = "6,4"
        d.append(draw.Rectangle(box.x, box.y, box.w, box.h, **kwargs))
        if label:
            d.append(draw.Text(str(label), FONT_SIZE, box.x + 8, box.y + 16, fill=style["color"], font_family=FONT_FAMILY, font_weight=600))

    def _draw_signal(self, d, box, style, label, *, accepting) -> None:
        notch = min(18.0, box.w * 0.16)
        if accepting:
            pts = [box.x + notch, box.y, box.right, box.y, box.right - notch, box.cy, box.right, box.bottom, box.x + notch, box.bottom, box.x, box.cy]
        else:
            pts = [box.x, box.y, box.right - notch, box.y, box.right, box.cy, box.right - notch, box.bottom, box.x, box.bottom]
        d.append(draw.Lines(*pts, close=True, **self._stroke_kwargs(style)))
        self._label(d, box.cx, box.cy, label, style["color"], max_width=box.w - TEXT_PADDING * 2, max_height=box.h - 8)

    def _draw_bar(self, d, box, style, label) -> None:
        # UML fork/join: a solid synchronization bar (filled), spanning the box width.
        bw = _num(style["borderWidth"], 1)
        fill = style["borderColor"]
        bar_h = max(6.0, min(box.h * 0.4, 16.0))
        cy = (box.y + 6 + bar_h / 2) if label else box.cy
        d.append(draw.Rectangle(box.x, cy - bar_h / 2, box.w, bar_h, fill=fill, stroke=fill, stroke_width=bw))
        if label:
            w, h = _text_area(box, "actor")
            self._label(d, box.cx, box.bottom - 8, label, style["color"], max_width=w, max_height=h)

    def _draw_port(self, d, box, style, label) -> None:
        size = min(box.w, box.h, 20.0)
        x = box.cx - size / 2
        y = box.cy - size / 2
        d.append(draw.Rectangle(x, y, size, size, **self._stroke_kwargs(style)))
        semantic = self._semantic(box)
        keyword = "proxy" if semantic == "proxyPort" else "full" if semantic == "fullPort" else ""
        port = (box.node.get("data") or {}).get("port") or {}
        type_name = str(port.get("type") or "")
        text = f"{stereotype_text(keyword)} {label}".strip() if keyword else str(label)
        if type_name:
            text += f": {type_name}"
        if port.get("isConjugated"):
            text = f"~{text}"
        if text:
            self._label(d, box.cx, y + size + 12, text, style["color"], max_width=max(box.w, 120))

    # -- edge drawing --------------------------------------------------------

    def _draw_edge(
        self,
        d: draw.Drawing,
        edge: Dict[str, Any],
        boxes: Dict[str, _Box],
        route: Optional[Dict[str, Any]],
    ) -> None:
        source = boxes.get(edge.get("source"))
        target = boxes.get(edge.get("target"))
        if source is None or target is None or route is None:
            return

        style = edge.get("style") or {}
        stroke = style.get("stroke", EDGE_DEFAULTS["stroke"])
        stroke_width = _num(style.get("strokeWidth"), EDGE_DEFAULTS["strokeWidth"])
        semantic = (edge.get("data") or {}).get("semanticType")
        spec = ELEMENT_CATALOG.get(semantic or "")
        points = route["points"]
        start_dir = _segment_direction(points[0], points[1])
        end_dir = _segment_direction(points[-2], points[-1])

        path_kwargs: Dict[str, Any] = {"fill": "none", "stroke": stroke, "stroke_width": stroke_width}
        dash = style.get("strokeDasharray")
        if dash is None and spec is not None and spec.dashed:
            dash = "6,4"
        if dash:
            path_kwargs["stroke_dasharray"] = str(dash).replace(" ", ",")

        path = draw.Path(**path_kwargs)
        path.M(*points[0])
        for pt in points[1:]:
            path.L(*pt)
        d.append(path)

        tip = points[-1]
        target_marker = spec.target_marker if spec is not None else "arrow"
        source_marker = spec.source_marker if spec is not None else "none"
        edge_data = edge.get("data") or {}
        source_end = edge_data.get("sourceEnd") or {}
        target_end = edge_data.get("targetEnd") or {}
        source_aggregation = source_end.get("aggregation", "none")
        target_aggregation = target_end.get("aggregation", "none")
        arrow_override = edge_data.get("arrow") if semantic in {
            "controlFlow", "objectFlow", "exceptionHandler", "dependency",
        } else None
        show_target_arrow = arrow_override not in ("backward", "none")
        show_source_arrow = arrow_override in ("backward", "both")
        if target_aggregation in ("shared", "composite"):
            self._marker_diamond(d, tip, end_dir, stroke, hollow=target_aggregation == "shared")
        elif target_marker == "diamond_filled":
            self._marker_diamond(d, tip, end_dir, stroke)
        elif target_marker == "triangle":
            self._marker_triangle(d, tip, end_dir, stroke, hollow=True)
        elif target_end.get("navigable") or (target_marker != "none" and show_target_arrow):
            self._marker_arrow(d, tip, end_dir, stroke)
        if source_aggregation in ("shared", "composite"):
            self._marker_diamond(d, points[0], (-start_dir[0], -start_dir[1]), stroke, hollow=source_aggregation == "shared")
        elif source_marker == "crosshair":
            self._marker_crosshair(d, points[0], stroke)
        elif source_end.get("navigable") or show_source_arrow:
            self._marker_arrow(d, points[0], (-start_dir[0], -start_dir[1]), stroke)

    def _draw_edge_labels(
        self,
        d: draw.Drawing,
        edge: Dict[str, Any],
        route: Optional[Dict[str, Any]],
        obstacles=(),
        placed=None,
    ) -> None:
        if route is None:
            return
        style = edge.get("style") or {}
        stroke = style.get("stroke", EDGE_DEFAULTS["stroke"])
        edge_data = edge.get("data") or {}
        points = route["points"]
        geometry = edge.get("route") if isinstance(edge.get("route"), dict) else {}
        offset = _route_point(geometry.get("labelOffset")) or (0.0, 0.0)
        label = edge_display_label(edge)
        box_w = len(label) * FONT_SIZE * CHAR_WIDTH_RATIO + 8 if label else 0.0
        box_h = FONT_SIZE + 6
        if label and obstacles and offset == (0.0, 0.0):
            # No author-placed offset, so the renderer may slide the label clear.
            anchor = _label_point(points, obstacles, box_w / 2, box_h / 2)
        else:
            anchor = route["mid"]
        lx = anchor[0] + offset[0]
        ly = anchor[1] + offset[1]
        if label:
            if placed is not None:
                placed.append((lx - box_w / 2, ly - box_h / 2, lx + box_w / 2, ly + box_h / 2))
            d.append(
                draw.Rectangle(
                    lx - box_w / 2, ly - box_h / 2, box_w, box_h,
                    rx=3, ry=3, fill="#ffffff", stroke="#e0e0e0", stroke_width=1,
                )
            )
            d.append(
                draw.Text(
                    label, FONT_SIZE, lx, ly,
                    center=True, fill="#222222", font_family=FONT_FAMILY,
                )
            )
        # Outward direction at each end, so a role or multiplicity is placed clear of the
        # node it belongs to rather than on top of the node's own label.
        self._draw_end_label(
            d, points[0], edge_data.get("sourceEnd") or {}, stroke,
            outward=_segment_direction(points[0], points[1]) if len(points) > 1 else (0.0, -1.0),
            obstacles=obstacles, placed=placed,
        )
        self._draw_end_label(
            d, points[-1], edge_data.get("targetEnd") or {}, stroke,
            outward=_segment_direction(points[-1], points[-2]) if len(points) > 1 else (0.0, -1.0),
            obstacles=obstacles, placed=placed,
        )
        item_flows = edge_data.get("itemFlows") or []
        if item_flows:
            flow_text = ", ".join(str(flow.get("item")) for flow in item_flows if isinstance(flow, dict) and flow.get("item"))
            if flow_text:
                d.append(draw.Text(flow_text, 10, lx, ly + 14, center=True, fill=stroke, font_family=FONT_FAMILY, font_style="italic"))

    def _draw_end_label(self, d, point, end, color, *, outward, obstacles=(), placed=None) -> None:
        """Draw a relationship end's role and multiplicity beside its own endpoint.

        *outward* is the unit vector pointing from the node into the diagram. The label is
        pushed along it to clear the node boundary, then sideways to clear the edge line.
        A fixed offset cannot do this: on an endpoint sitting on a node's bottom edge it
        placed the text back inside the node, on top of the node's own label.

        Two ends of the same relationship, or two relationships meeting at one node, land
        close enough that a single fixed offset piles their labels on one another. So the
        first clear position wins: further out along the edge, then on the other side of
        it, then further out again.
        """
        if not isinstance(end, dict):
            return
        parts = []
        role = str(end.get("role") or "").strip()
        if role:
            parts.append(role)
        multiplicity = end.get("multiplicity")
        if isinstance(multiplicity, dict) and multiplicity.get("lower") is not None and multiplicity.get("upper") is not None:
            lower, upper = multiplicity["lower"], multiplicity["upper"]
            parts.append(str(lower) if lower == upper else f"{lower}..{upper}")
        if not parts:
            return

        text = " ".join(parts)
        half_w = len(text) * 10 * CHAR_WIDTH_RATIO / 2 + 2
        half_h = 7.0
        dx, dy = outward

        best = None
        for clearance in (_END_LABEL_CLEARANCE, _END_LABEL_CLEARANCE + 16, _END_LABEL_CLEARANCE + 32):
            for side in (1, -1):
                step = _END_LABEL_SIDESTEP * side
                x = point[0] + dx * clearance - dy * step
                y = point[1] + dy * clearance + dx * step
                if best is None:
                    best = (x, y)
                if not _clear_of_nodes(x, y, half_w, half_h, obstacles):
                    continue
                rect = (x - half_w, y - half_h, x + half_w, y + half_h)
                if placed is not None and any(_rects_overlap(rect, other) for other in placed):
                    continue
                best = (x, y)
                break
            else:
                continue
            break

        x, y = best
        if placed is not None:
            placed.append((x - half_w, y - half_h, x + half_w, y + half_h))
        d.append(draw.Text(text, 10, x, y + 3.5, center=True, fill=color, font_family=FONT_FAMILY))

    @staticmethod
    def _route(source: _Box, target: _Box) -> Tuple[List[Tuple[float, float]], Tuple[int, int], Tuple[int, int]]:
        """Return an orthogonal point list plus the start/end segment directions."""
        dx = target.cx - source.cx
        dy = target.cy - source.cy
        if abs(dy) >= abs(dx):  # vertical primary
            if dy >= 0:
                sp, tp, start_dir, end_dir = (source.cx, source.bottom), (target.cx, target.y), (0, 1), (0, 1)
            else:
                sp, tp, start_dir, end_dir = (source.cx, source.y), (target.cx, target.bottom), (0, -1), (0, -1)
            mid = (sp[1] + tp[1]) / 2
            points = [sp, (sp[0], mid), (tp[0], mid), tp]
        else:  # horizontal primary
            if dx >= 0:
                sp, tp, start_dir, end_dir = (source.right, source.cy), (target.x, target.cy), (1, 0), (1, 0)
            else:
                sp, tp, start_dir, end_dir = (source.x, source.cy), (target.right, target.cy), (-1, 0), (-1, 0)
            mid = (sp[0] + tp[0]) / 2
            points = [sp, (mid, sp[1]), (mid, tp[1]), tp]
        return points, start_dir, end_dir

    @staticmethod
    def _orient(tip: Tuple[float, float], direction: Tuple[int, int], length: float):
        """Return (base_center, perpendicular unit) for a marker pointing along *direction*."""
        dxn, dyn = direction
        base = (tip[0] - dxn * length, tip[1] - dyn * length)
        perp = (-dyn, dxn)  # 90-degree rotation
        return base, perp

    def _marker_arrow(self, d, tip, direction, color) -> None:
        length, half = 11.0, 5.0
        base, (px, py) = self._orient(tip, direction, length)
        d.append(
            draw.Lines(
                tip[0], tip[1],
                base[0] + px * half, base[1] + py * half,
                base[0] - px * half, base[1] - py * half,
                close=True, fill=color, stroke=color,
            )
        )

    def _marker_triangle(self, d, tip, direction, color, *, hollow=False) -> None:
        length, half = 15.0, 8.0
        base, (px, py) = self._orient(tip, direction, length)
        d.append(
            draw.Lines(
                tip[0], tip[1],
                base[0] + px * half, base[1] + py * half,
                base[0] - px * half, base[1] - py * half,
                close=True, fill=("#ffffff" if hollow else color), stroke=color, stroke_width=1.5,
            )
        )

    def _marker_crosshair(self, d, point, color) -> None:
        radius = 6.0
        d.append(draw.Circle(point[0], point[1], radius, fill="#ffffff", stroke=color, stroke_width=1.5))
        d.append(draw.Line(point[0] - radius, point[1], point[0] + radius, point[1], stroke=color, stroke_width=1.5))
        d.append(draw.Line(point[0], point[1] - radius, point[0], point[1] + radius, stroke=color, stroke_width=1.5))

    def _marker_diamond(self, d, point, direction, color, *, hollow=False) -> None:
        length, half = 16.0, 6.0
        dxn, dyn = direction
        far = (point[0] + dxn * length, point[1] + dyn * length)
        mid = (point[0] + dxn * length / 2, point[1] + dyn * length / 2)
        perp = (-dyn, dxn)
        d.append(
            draw.Lines(
                point[0], point[1],
                mid[0] + perp[0] * half, mid[1] + perp[1] * half,
                far[0], far[1],
                mid[0] - perp[0] * half, mid[1] - perp[1] * half,
                close=True, fill=("#ffffff" if hollow else color), stroke=color, stroke_width=1.5,
            )
        )
