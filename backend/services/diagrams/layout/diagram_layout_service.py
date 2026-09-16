"""Layout subsystem for generated diagrams.

Generation asks the LLM for a *logical* diagram — nodes and how they
connect, with no coordinates. This module turns that logical graph into positioned,
sized nodes the renderer and editor can use.

Design: ``docs/02-design-and-features/04-generation-design.md`` (Layout).

:class:`PyGraphvizLayoutEngine` is the sole flat layout engine. It invokes bundled
libgvc ``dot`` in process while :class:`DiagramLayoutService` owns per-type sizing,
``parentId`` containment, top-level absolute positions, and child positions relative
to their parent.
"""

from __future__ import annotations

import math
import os
import platform
import sys
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from services.shared.schema_identities import LAYOUT_CONFIGURATION_VERSIONS
from services.diagrams.catalog.constants import (
    DEFAULT_DIRECTION,
    DEFAULT_NODE_GAP,
    DEFAULT_RANK_GAP,
    FONT_SIZE,
    LABEL_INSIDE_SEMANTIC_TYPES,
    LINE_HEIGHT,
    NOTE_FOLD,
    TEXT_PADDING,
    wrapped_line_count,
    LAYOUT_BASE_SIZES as _BASE_SIZES,
    LAYOUT_CHAR_WIDTH as _CHAR_WIDTH,
    LAYOUT_CONTAINER_HEADER as _CONTAINER_HEADER,
    LAYOUT_CONTAINER_PAD as _CONTAINER_PAD,
    LAYOUT_FALLBACK_SIZE as _FALLBACK_SIZE,
    LAYOUT_LABEL_PADDING as _LABEL_PADDING,
    LAYOUT_MAX_WIDTH as _MAX_WIDTH,
    TYPE_DIRECTION,
    TYPE_NODE_GAP,
    TYPE_RANK_GAP,
)

# ---------------------------------------------------------------------------
# Public data shapes
# ---------------------------------------------------------------------------


@dataclass
class LayoutInputNode:
    """A logical node to be laid out (no coordinates yet)."""

    id: str
    semantic_type: str = ""
    label: str = ""
    width: Optional[float] = None
    height: Optional[float] = None
    parent_id: Optional[str] = None
    port_side: Optional[str] = None
    port_offset: Optional[float] = None


@dataclass
class LayoutEdge:
    source: str
    target: str


@dataclass
class PositionedNode:
    """A laid-out node. ``x``/``y`` is the top-left corner; for a node with a
    ``parent_id`` the position is **relative to its parent** (React Flow / canonical
    convention), otherwise it is absolute."""

    id: str
    x: float
    y: float
    width: float
    height: float
    parent_id: Optional[str] = None


@dataclass
class LayoutResult:
    nodes: List[PositionedNode]
    engine: str
    positions: Dict[str, PositionedNode] = field(init=False)

    def __post_init__(self) -> None:
        self.positions = {n.id: n for n in self.nodes}


class LayoutError(Exception):
    code = "layout_failed"

    def __init__(self, message: str = "PyGraphviz layout failed.", *, stage: str = "layout") -> None:
        super().__init__(message)
        self.details = {"engine": "pygraphviz-dot", "stage": stage}


class LayoutEngineUnavailableError(LayoutError):
    code = "layout_engine_unavailable"

    def __init__(self, message: str = "Pinned PyGraphviz 2.0 runtime is unavailable.") -> None:
        super().__init__(message, stage="availability")


@dataclass(frozen=True)
class PyGraphvizLayoutTrace:
    engine: str
    pygraphviz_version: str
    runtime_platform: str
    emulation: Optional[str]
    layout_configuration_version: str
    node_count: int
    edge_count: int
    duration_ms: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "engine": self.engine,
            "pygraphvizVersion": self.pygraphviz_version,
            "runtimePlatform": self.runtime_platform,
            "emulation": self.emulation,
            "layoutConfigurationVersion": self.layout_configuration_version,
            "nodeCount": self.node_count,
            "edgeCount": self.edge_count,
            "durationMs": self.duration_ms,
        }


# ---------------------------------------------------------------------------
# Sizing + per-type direction
# ---------------------------------------------------------------------------
# Direction + base-size constants now live in services/catalog/constants.py (imported above).


def node_size(semantic_type: str, label: str) -> Tuple[float, float]:
    """Return a default ``(width, height)`` for a node, widened for long labels.

    Used to size logical nodes the LLM did not (and should not) measure. The
    diamond/actor/etc. keep their characteristic proportions; width grows with the
    label so text fits, capped at ``_MAX_WIDTH``.
    """
    base_w, base_h = _BASE_SIZES.get(semantic_type, _FALLBACK_SIZE)
    needed = len(label or "") * _CHAR_WIDTH + _LABEL_PADDING
    width = min(_MAX_WIDTH, max(base_w, needed))

    # Width is capped, so a long label cannot be made to fit on one line — it wraps, and
    # the shape has to be tall enough for the lines it wraps onto. Only shapes that draw
    # their label inside themselves grow; an actor or a fork bar writes its label
    # underneath, where extra height would distort the shape instead of making room.
    height = base_h
    if semantic_type in LABEL_INSIDE_SEMANTIC_TYPES:
        fold = NOTE_FOLD if semantic_type == "note" else 0.0
        lines = wrapped_line_count(label, width, reserve=fold)
        needed_h = lines * FONT_SIZE * LINE_HEIGHT + TEXT_PADDING * 2 + fold
        height = max(base_h, needed_h)
    return float(width), float(round(height, 1))


# ---------------------------------------------------------------------------
# Engine interface
# ---------------------------------------------------------------------------


class LayoutEngine(ABC):
    """Lays out a *flat* graph (no nesting). Containment is handled one level up by
    :class:`DiagramLayoutService`."""

    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        """Whether this engine can run in the current environment."""

    @abstractmethod
    def layout(
        self,
        nodes: List[LayoutInputNode],
        edges: List[LayoutEdge],
        direction: str,
        node_gap: float = DEFAULT_NODE_GAP,
        rank_gap: float = DEFAULT_RANK_GAP,
    ) -> Dict[str, Tuple[float, float]]:
        """Return ``id -> (x, y)`` top-left positions, normalized so the top-left of
        the whole graph sits at the origin. Sizes are taken from each node's
        ``width``/``height`` (assumed already assigned)."""


_PYGRAPHVIZ_NATIVE_LOCK = threading.Lock()
_PYGRAPHVIZ_MAX_NODES = 256


class PyGraphvizLayoutEngine(LayoutEngine):
    name = "pygraphviz-dot"

    def __init__(
        self,
        *,
        trace_sink: Optional[Callable[[PyGraphvizLayoutTrace], None]] = None,
    ) -> None:
        self._trace_sink = trace_sink
        self._local = threading.local()

    def available(self) -> bool:
        try:
            module = self._module()
            self._runtime_identity()
            graph = None
            with _PYGRAPHVIZ_NATIVE_LOCK:
                try:
                    graph = module.AGraph(strict=False, directed=True)
                    graph.add_node("probe")
                    graph.layout(prog="dot")
                    if not graph.get_node("probe").attr.get("pos"):
                        return False
                finally:
                    if graph is not None:
                        graph.close()
            return True
        except Exception:
            return False

    def layout(
        self,
        nodes,
        edges,
        direction,
        node_gap=DEFAULT_NODE_GAP,
        rank_gap=DEFAULT_RANK_GAP,
    ):
        started = time.perf_counter()
        prepared = self._prepare(nodes, edges, direction, node_gap, rank_gap)
        if not prepared["nodes"]:
            self._record_trace(prepared, started)
            return {}
        module = self._module()
        runtime_platform, emulation = self._runtime_identity()
        graph = None
        raw_positions = {}
        graph_box = None
        try:
            with _PYGRAPHVIZ_NATIVE_LOCK:
                try:
                    graph = module.AGraph(strict=False, directed=True, name="G")
                    graph.graph_attr.update(
                        rankdir=direction,
                        nodesep=self._number(node_gap / 72.0),
                        ranksep=self._number(rank_gap / 72.0),
                    )
                    graph.node_attr.update(shape="box", fixedsize="true", label="")
                    for item in prepared["nodes"]:
                        graph.add_node(
                            item["token"],
                            width=self._number(item["width"] / 72.0),
                            height=self._number(item["height"] / 72.0),
                        )
                    for index, (source, target) in enumerate(prepared["edges"]):
                        graph.add_edge(source, target, key=f"e{index}")
                    graph.layout(prog="dot")
                    graph_box = graph.graph_attr.get("bb")
                    for item in prepared["nodes"]:
                        raw_positions[item["token"]] = graph.get_node(item["token"]).attr.get("pos")
                finally:
                    if graph is not None:
                        graph.close()
        except LayoutError:
            raise
        except Exception as exc:
            raise LayoutError("PyGraphviz native layout failed.", stage="native_layout") from exc
        positions = self._convert(prepared["nodes"], raw_positions, graph_box)
        trace = PyGraphvizLayoutTrace(
            engine=self.name,
            pygraphviz_version=module.__version__,
            runtime_platform=runtime_platform,
            emulation=emulation,
            layout_configuration_version=prepared["configuration"],
            node_count=len(prepared["nodes"]),
            edge_count=len(prepared["edges"]),
            duration_ms=max(0, round((time.perf_counter() - started) * 1000)),
        )
        self._emit(trace, prepared, positions)
        return positions

    def _record_trace(self, prepared, started):
        module = self._module()
        runtime_platform, emulation = self._runtime_identity()
        trace = PyGraphvizLayoutTrace(
            self.name,
            module.__version__,
            runtime_platform,
            emulation,
            prepared["configuration"],
            0,
            0,
            max(0, round((time.perf_counter() - started) * 1000)),
        )
        self._emit(trace, prepared, {})

    def _emit(self, trace, prepared, positions):
        self._local.trace = trace
        if self._trace_sink is not None:
            self._trace_sink(trace)

    @classmethod
    def _prepare(cls, nodes, edges, direction, node_gap, rank_gap):
        if direction not in {"TB", "LR"}:
            raise LayoutError("PyGraphviz direction must be TB or LR.")
        for name, value in (("node_gap", node_gap), ("rank_gap", rank_gap)):
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise LayoutError(f"PyGraphviz {name} must be finite and nonnegative.")
        if len(nodes) > _PYGRAPHVIZ_MAX_NODES:
            raise LayoutError("PyGraphviz layout accepts at most 256 nodes.")
        seen = set()
        prepared_nodes = []
        tokens = {}
        for index, node in enumerate(nodes):
            if not isinstance(node.id, str) or not node.id or node.id in seen:
                raise LayoutError("PyGraphviz layout requires unique nonblank node IDs.")
            seen.add(node.id)
            width = _FALLBACK_SIZE[0] if node.width is None else node.width
            height = _FALLBACK_SIZE[1] if node.height is None else node.height
            if not all(
                isinstance(value, (int, float)) and math.isfinite(value) and value > 0
                for value in (width, height)
            ):
                raise LayoutError("PyGraphviz node dimensions must be finite and positive.")
            token = f"n{index:03d}"
            tokens[node.id] = token
            prepared_nodes.append(
                {
                    "id": node.id,
                    "token": token,
                    "width": float(width),
                    "height": float(height),
                }
            )
        prepared_edges = []
        for edge in edges:
            if edge.source not in tokens or edge.target not in tokens:
                raise LayoutError("PyGraphviz edge endpoint is missing from the flat graph.")
            prepared_edges.append((tokens[edge.source], tokens[edge.target]))
        configuration = cls._configuration_version(direction, node_gap, rank_gap)
        return {
            "nodes": prepared_nodes,
            "edges": prepared_edges,
            "configuration": configuration,
        }

    @staticmethod
    def _convert(nodes, raw_positions, graph_box):
        if not isinstance(graph_box, str):
            raise LayoutError("PyGraphviz output omitted the graph bounding box.")
        try:
            x0, y0, x1, y1 = (float(value) for value in graph_box.split(","))
        except (TypeError, ValueError) as exc:
            raise LayoutError("PyGraphviz graph bounding box is malformed.") from exc
        if not all(math.isfinite(value) for value in (x0, y0, x1, y1)) or x1 < x0 or y1 < y0:
            raise LayoutError("PyGraphviz graph bounding box is nonfinite or inverted.")
        graph_height = y1 - y0
        positions = {}
        for item in nodes:
            raw = raw_positions.get(item["token"])
            if not isinstance(raw, str):
                raise LayoutError(f"PyGraphviz output omitted node position for {item['id']!r}.")
            try:
                cx, cy = (float(value.rstrip("!")) for value in raw.split(","))
            except (TypeError, ValueError) as exc:
                raise LayoutError(f"PyGraphviz node position is malformed for {item['id']!r}.") from exc
            if not math.isfinite(cx) or not math.isfinite(cy):
                raise LayoutError(f"PyGraphviz node position is nonfinite for {item['id']!r}.")
            positions[item["id"]] = (
                cx - x0 - item["width"] / 2,
                graph_height - (cy - y0) - item["height"] / 2,
            )
        if len(positions) != len(nodes):
            raise LayoutError("PyGraphviz output did not provide exactly one position per node.")
        return _normalize(positions)

    @staticmethod
    def _configuration_version(direction, node_gap, rank_gap):
        for diagram_type, configured_direction in TYPE_DIRECTION.items():
            if (
                configured_direction == direction
                and TYPE_NODE_GAP[diagram_type] == node_gap
                and TYPE_RANK_GAP[diagram_type] == rank_gap
            ):
                return LAYOUT_CONFIGURATION_VERSIONS[diagram_type]
        for diagram_type in ("activity_diagram", "use_case_diagram", "bdd_diagram"):
            if (
                TYPE_NODE_GAP[diagram_type] == node_gap
                and TYPE_RANK_GAP[diagram_type] == rank_gap
            ):
                return LAYOUT_CONFIGURATION_VERSIONS[diagram_type]
        raise LayoutError("PyGraphviz layout configuration is not registered.")

    @staticmethod
    def _module():
        try:
            import pygraphviz
        except (ImportError, OSError) as exc:
            raise LayoutEngineUnavailableError(
                "PyGraphviz 2.0 wheel and bundled Graphviz plugins are unavailable."
            ) from exc
        if getattr(pygraphviz, "__version__", None) != "2.0":
            raise LayoutEngineUnavailableError("GraphPilot requires exactly pygraphviz 2.0.")
        return pygraphviz

    @staticmethod
    def _runtime_identity():
        machine = platform.machine().casefold()
        if sys.platform == "win32":
            if machine in {"amd64", "x86_64"}:
                emulation = (
                    "windows-x64-on-arm64"
                    if os.environ.get("PROCESSOR_ARCHITEW6432", "").casefold() == "arm64"
                    else None
                )
                return "windows-x64", emulation
            raise LayoutEngineUnavailableError(
                "Native Windows ARM64 Python is unsupported; use the packaged x64 runtime."
            )
        if sys.platform == "darwin":
            if machine in {"x86_64", "amd64"}:
                return "macos-x64", None
            if machine in {"arm64", "aarch64"}:
                return "macos-arm64", None
        if sys.platform.startswith("linux"):
            if machine in {"x86_64", "amd64"}:
                return "linux-x64", None
            if machine in {"aarch64", "arm64"}:
                return "linux-aarch64", None
        raise LayoutEngineUnavailableError("PyGraphviz runtime platform is unsupported.")

    @staticmethod
    def _number(value):
        return format(float(value), ".12g")


# ---------------------------------------------------------------------------
# Normalization helper
# ---------------------------------------------------------------------------


def _normalize(positions: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
    """Shift positions so the minimum corner sits at the origin (0, 0)."""
    if not positions:
        return {}
    min_x = min(x for x, _ in positions.values())
    min_y = min(y for _, y in positions.values())
    return {nid: (x - min_x, y - min_y) for nid, (x, y) in positions.items()}


# ---------------------------------------------------------------------------
# Service: engine selection, sizing, containment
# ---------------------------------------------------------------------------


class DiagramLayoutService:
    """Lay out a logical diagram into positioned, sized nodes.

    Uses only pinned PyGraphviz 2.0 and handles ``parentId`` containment one level
    deep by laying out each container's children inside it and sizing the container
    to fit.
    """

    def __init__(self, engine: Optional[LayoutEngine] = None) -> None:
        self._engine = engine or PyGraphvizLayoutEngine()
        if not isinstance(self._engine, PyGraphvizLayoutEngine):
            raise TypeError("DiagramLayoutService accepts only PyGraphvizLayoutEngine.")
        self._availability_checked = False

    def select_engine(self) -> LayoutEngine:
        if not self._availability_checked:
            if not self._engine.available():
                raise LayoutEngineUnavailableError()
            self._availability_checked = True
        return self._engine

    def layout(
        self,
        diagram_type: str,
        nodes: List[LayoutInputNode],
        edges: List[LayoutEdge],
    ) -> LayoutResult:
        direction = TYPE_DIRECTION.get(diagram_type, DEFAULT_DIRECTION)
        node_gap = TYPE_NODE_GAP.get(diagram_type, DEFAULT_NODE_GAP)
        rank_gap = TYPE_RANK_GAP.get(diagram_type, DEFAULT_RANK_GAP)

        # Assign default sizes where missing.
        for n in nodes:
            if n.width is None or n.height is None:
                w, h = node_size(n.semantic_type, n.label)
                n.width = n.width or w
                n.height = n.height or h

        engine = self.select_engine()
        return self._position(engine, direction, nodes, edges, node_gap, rank_gap)

    def _position(
        self,
        engine: LayoutEngine,
        direction: str,
        nodes: List[LayoutInputNode],
        edges: List[LayoutEdge],
        node_gap: float,
        rank_gap: float,
    ) -> LayoutResult:
        by_id = {n.id: n for n in nodes}
        boundary_nodes = {
            n.id for n in nodes
            if n.semantic_type in {"port", "proxyPort", "fullPort", "inputPin", "outputPin", "valuePin", "actionInputPin", "expansionNode"}
        }
        children_of: Dict[str, List[LayoutInputNode]] = {}
        ports_of: Dict[str, List[LayoutInputNode]] = {}
        for n in nodes:
            if n.parent_id and n.parent_id in by_id:
                if n.id in boundary_nodes:
                    ports_of.setdefault(n.parent_id, []).append(n)
                else:
                    children_of.setdefault(n.parent_id, []).append(n)

        positioned: Dict[str, PositionedNode] = {}

        # 1) Lay out each container's children; size the container to fit them.
        for parent_id, kids in children_of.items():
            kid_edges = [
                e for e in edges
                if e.source in {k.id for k in kids} and e.target in {k.id for k in kids}
            ]
            # Children follow the diagram's own direction rather than a fixed "TB".
            #
            # Use cases inside a subject rarely connect to each other — their actors are
            # outside the boundary — so they all land on rank 0. Laying rank 0 out under
            # "TB" spreads them across one wide row; the diagram's own "LR" stacks them in
            # a column, which is what the notation wants and what a hand-arranged
            # reference produced.
            child_pos = engine.layout(kids, kid_edges, direction, node_gap, rank_gap)
            for kid in kids:
                x, y = child_pos.get(kid.id, (0.0, 0.0))
                # Offset children below the header band and inside the padding.
                positioned[kid.id] = PositionedNode(
                    id=kid.id,
                    x=x + _CONTAINER_PAD,
                    y=y + _CONTAINER_HEADER,
                    width=float(kid.width),
                    height=float(kid.height),
                    parent_id=parent_id,
                )
            # Size the parent container to enclose its children + padding.
            max_x = max((positioned[k.id].x + k.width for k in kids), default=0.0)
            max_y = max((positioned[k.id].y + k.height for k in kids), default=0.0)
            parent = by_id[parent_id]
            parent.width = max_x + _CONTAINER_PAD
            parent.height = max_y + _CONTAINER_PAD

        # 2) Lay out the top-level graph (nodes with no parent), with containers now
        #    sized. Edges that touch a child are remapped to its top-level ancestor.
        top_nodes = [n for n in nodes if not (n.parent_id and n.parent_id in by_id)]
        top_ids = {n.id for n in top_nodes}

        def ancestor(nid: str) -> str:
            seen = set()
            cur = nid
            while cur in by_id and by_id[cur].parent_id and by_id[cur].parent_id in by_id:
                if cur in seen:
                    break
                seen.add(cur)
                cur = by_id[cur].parent_id
            return cur

        top_edges: List[LayoutEdge] = []
        for e in edges:
            s, t = ancestor(e.source), ancestor(e.target)
            if s in top_ids and t in top_ids and s != t:
                top_edges.append(LayoutEdge(s, t))

        top_pos = engine.layout(top_nodes, top_edges, direction, node_gap, rank_gap)
        for n in top_nodes:
            x, y = top_pos.get(n.id, (0.0, 0.0))
            positioned[n.id] = PositionedNode(
                id=n.id, x=x, y=y, width=float(n.width), height=float(n.height), parent_id=None
            )

        for parent_id, ports in ports_of.items():
            parent = by_id[parent_id]
            for index, port in enumerate(ports):
                default_side = "left" if port.semantic_type in {"inputPin", "valuePin", "actionInputPin"} else "right"
                side = port.port_side or default_side
                offset = port.port_offset if port.port_offset is not None else (index + 1) / (len(ports) + 1)
                offset = max(0.0, min(1.0, offset))
                if side == "left":
                    x, y = -port.width / 2, parent.height * offset - port.height / 2
                elif side == "top":
                    x, y = parent.width * offset - port.width / 2, -port.height / 2
                elif side == "bottom":
                    x, y = parent.width * offset - port.width / 2, parent.height - port.height / 2
                else:
                    x, y = parent.width - port.width / 2, parent.height * offset - port.height / 2
                positioned[port.id] = PositionedNode(
                    id=port.id, x=float(x), y=float(y), width=float(port.width), height=float(port.height), parent_id=parent_id
                )

        _place_notes_beside_their_subject(positioned, nodes, edges)

        ordered = [positioned[n.id] for n in nodes if n.id in positioned]
        return LayoutResult(nodes=ordered, engine=engine.name)

_NOTE_GAP = 48.0


def _place_notes_beside_their_subject(positioned, nodes, edges):
    """Move each note next to the element it annotates.

    A note carries no flow, so the layout engine has nothing to rank it by and drops it
    wherever the graph has room -- often the far corner, with its dashed link crossing the
    whole diagram. Placing it beside its subject makes the annotation readable as an
    annotation.

    Only notes with exactly one commentLink are moved. A note attached to several elements
    has no single right home, so the engine's choice stands.
    """
    note_ids = {n.id for n in nodes if n.semantic_type == "note"}
    if not note_ids:
        return

    subjects = {}
    for edge in edges:
        if edge.source in note_ids:
            subjects.setdefault(edge.source, []).append(edge.target)
        if edge.target in note_ids:
            subjects.setdefault(edge.target, []).append(edge.source)

    def absolute(node_id):
        """Resolve a position to canvas coordinates; a child's x/y is parent-relative."""
        node = positioned.get(node_id)
        if node is None:
            return None
        x, y = node.x, node.y
        parent_id = node.parent_id
        seen = {node_id}
        while parent_id is not None and parent_id in positioned and parent_id not in seen:
            seen.add(parent_id)
            parent = positioned[parent_id]
            x += parent.x
            y += parent.y
            parent_id = parent.parent_id
        return x, y, node.width, node.height

    occupied = []
    for node_id in positioned:
        if node_id in note_ids:
            continue
        resolved = absolute(node_id)
        if resolved:
            x, y, width, height = resolved
            occupied.append((x, y, x + width, y + height))

    for note_id, attached in subjects.items():
        note = positioned.get(note_id)
        if note is None or note.parent_id is not None or len(attached) != 1:
            continue
        resolved = absolute(attached[0])
        if resolved is None:
            continue
        anchor_x, anchor_y, subject_width, subject_height = resolved
        # Prefer the subject's left, then right, then above, then below; take the first
        # placement that collides with nothing already on the canvas.
        candidates = [
            (anchor_x - note.width - _NOTE_GAP, anchor_y),
            (anchor_x + subject_width + _NOTE_GAP, anchor_y),
            (anchor_x, anchor_y - note.height - _NOTE_GAP),
            (anchor_x, anchor_y + subject_height + _NOTE_GAP),
        ]
        for x, y in candidates:
            box = (x, y, x + note.width, y + note.height)
            if not any(
                box[0] < other[2] and other[0] < box[2] and box[1] < other[3] and other[1] < box[3]
                for other in occupied
            ):
                positioned[note_id] = PositionedNode(
                    id=note_id, x=x, y=y, width=note.width, height=note.height, parent_id=None
                )
                occupied.append(box)
                break

