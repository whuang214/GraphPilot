"""Centralized tuning constants for the diagram services (Tier-3 consolidation).

One place to adjust the visual, layout, and validation knobs that were previously
scattered across ``diagram_render_service``, ``diagram_layout_service``, and
``diagram_validation_service``. The owning services import these names back, so values
and behavior are unchanged — this is purely about having a single place to tune them.

Note: the render *fallback* node sizes and the layout *base* node sizes are deliberately
**separate** maps. They serve different roles (render falls back to these only when a
saved node omits a size; layout uses its base sizes as the starting size it then widens
for labels) and intentionally differ in some values, so they are kept distinct.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Shared visual defaults (render + generation)
# ---------------------------------------------------------------------------

STYLE_DEFAULTS: Dict[str, Any] = {
    "background": "#ffffff",
    "borderColor": "#333333",
    "color": "#111111",
    "borderWidth": 1,
    "borderStyle": "solid",
}

EDGE_DEFAULTS: Dict[str, Any] = {
    "stroke": "#333333",
    "strokeWidth": 2,
}

# ---------------------------------------------------------------------------
# Render: node sizing fallback + text/visual tuning
# ---------------------------------------------------------------------------

# Fallback node sizes by semanticType, used only when a node omits width/height.
DEFAULT_NODE_SIZES: Dict[str, Tuple[float, float]] = {
    "initialNode": (90, 60),
    "activityFinalNode": (90, 60),
    "flowFinalNode": (90, 60),
    "mergeNode": (120, 50),
    "forkNode": (120, 30),
    "joinNode": (120, 30),
    "opaqueAction": (160, 60),
    "decisionNode": (140, 80),
    "objectNode": (160, 60),
    "centralBufferNode": (160, 60),
    "dataStoreNode": (160, 70),
    "inputPin": (24, 24),
    "outputPin": (24, 24),
    "valuePin": (24, 24),
    "actionInputPin": (24, 24),
    "expansionNode": (24, 24),
    "note": (160, 80),
    "actor": (90, 120),
    "useCase": (200, 70),
    "subject": (320, 240),
    "block": (180, 90),
    "valueType": (180, 90),
    "constraintBlock": (180, 100),
    "interfaceBlock": (180, 90),
    "enumeration": (180, 90),
    "propertySpecificType": (180, 90),
    "instanceSpecification": (180, 90),
    "unit": (180, 80),
    "quantityKind": (180, 80),
    "associationBlock": (180, 100),
    "port": (44, 44),
    "proxyPort": (44, 44),
    "fullPort": (44, 44),
}
FALLBACK_SIZE: Tuple[float, float] = (140, 60)

PADDING = 24
FONT_FAMILY = "system-ui, sans-serif"
FONT_SIZE = 12
# Label fitting: the renderer has no DOM/font metrics, so a label's width is estimated
# as len(text) * font * CHAR_WIDTH_RATIO (a deterministic stand-in). Labels word-wrap,
# then shrink toward MIN_FONT_SIZE, then gain an ellipsis as a last resort.
MIN_FONT_SIZE = 8
LINE_HEIGHT = 1.2
CHAR_WIDTH_RATIO = 0.58
TEXT_PADDING = 8

# ---------------------------------------------------------------------------
# Raster (SVG -> PNG): server-side rasterization of the SVG the renderer emits
# ---------------------------------------------------------------------------
# The SVG is the canonical output; the PNG is derived from it via ``resvg`` so the
# MCP tools / agents get the same picture the editor's client-side PNG export does
# (which rasterizes the very same shared SVG). White matte (diagrams assume it) and
# a 2x scale mirror the editor's ``svgToPngBlob`` default. The render uses system
# fonts; ``RASTER_SANS_FONT`` resolves the SVG's generic ``sans-serif`` family.
RASTER_BACKGROUND = "#ffffff"
RASTER_SANS_FONT = "Arial"
RASTER_SCALE = 2.0
# Bound the default in-memory PNG size; explicit saved PNG artifacts opt out of this cap.
RASTER_MAX_PX = 2400

# ---------------------------------------------------------------------------
# Layout: per-type flow direction + base sizing
# ---------------------------------------------------------------------------

# Per-type primary flow direction: 'TB' top-to-bottom, 'LR' left-to-right.
TYPE_DIRECTION: Dict[str, str] = {
    "activity_diagram": "TB",
    "use_case_diagram": "LR",
    "bdd_diagram": "TB",
}
DEFAULT_DIRECTION = "TB"
TYPE_NODE_GAP: Dict[str, float] = {
    "activity_diagram": 64.0,
    "use_case_diagram": 64.0,
    "bdd_diagram": 56.0,
}
TYPE_RANK_GAP: Dict[str, float] = {
    "activity_diagram": 72.0,
    "use_case_diagram": 96.0,
    "bdd_diagram": 72.0,
}
DEFAULT_NODE_GAP = 56.0
DEFAULT_RANK_GAP = 72.0

# Per-type routing for *generated* diagrams, stamped onto each edge at creation so an
# already-saved diagram a user has arranged by hand is never silently re-routed.
#
# The split follows what each notation's topology does to an orthogonal router.
#
# Use case and BDD both fan in: several actors reach use cases inside one boundary, and
# several parts compose into one whole. Orthogonal routing has no obstacle avoidance, so
# each edge runs along the same corridor and *through* the nodes between — three parts
# composing into a block render as a chain of unrelated siblings. Straight edges leave at
# distinct angles and the picture reads correctly.
#
# Activity keeps orthogonal. It is a rank-ordered top-to-bottom flow where right angles
# are the conventional notation and read more clearly, and its branches diverge rather
# than converge through other nodes.
TYPE_ROUTE_MODE: Dict[str, str] = {
    "use_case_diagram": "straight",
    "bdd_diagram": "straight",
}

# Base node sizes by semanticType. Width is widened for long labels (see node_size).
LAYOUT_BASE_SIZES: Dict[str, Tuple[float, float]] = {
    **DEFAULT_NODE_SIZES,
    "decisionNode": (150, 90),
    "note": (170, 80),
    "block": (190, 90),
    "valueType": (190, 90),
    "constraintBlock": (190, 100),
    "interfaceBlock": (190, 90),
    "enumeration": (190, 90),
}
LAYOUT_FALLBACK_SIZE: Tuple[float, float] = (150, 60)
LAYOUT_CHAR_WIDTH = 7.5  # approx px per label char at the editor's 12px font
LAYOUT_LABEL_PADDING = 36
LAYOUT_MAX_WIDTH = 320
# Spacing used to pad a container around its children (and a header band on top).
LAYOUT_CONTAINER_PAD = 24.0
LAYOUT_CONTAINER_HEADER = 28.0

# ---------------------------------------------------------------------------
# Validation: non-blocking structural-warning thresholds
# ---------------------------------------------------------------------------

LONG_LABEL_LENGTH = 120
HIGH_NODE_COUNT = 200
HIGH_EDGE_COUNT = 400

# ---------------------------------------------------------------------------
# BDD block compartments (parts / references / values / operations / literals …)
# ---------------------------------------------------------------------------
# The name header + each non-empty compartment's (italic) label + item lines. The
# min-height fits that content so writers (layout sizing, seed authoring, and the
# editor's mirrored auto-fit) size a block to its compartments — keeping the canvas
# and the SVG export in agreement on height. Empty classifiers use one compact name
# section; classifiers with feature content retain the established larger minimum.
BDD_HEADER_HEIGHT = 34.0
BDD_COMPARTMENT_LINE = FONT_SIZE * LINE_HEIGHT
BDD_COMPARTMENT_PAD = 6.0
BDD_EMPTY_MIN_HEIGHT = 48.0
BDD_FILLED_MIN_HEIGHT = 90.0


def _multiplicity_text(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    lower, upper = value.get("lower"), value.get("upper")
    if lower is None or upper is None:
        return ""
    return str(lower) if lower == upper else f"{lower}..{upper}"


def _parameter_text(value: Any) -> str:
    """One parameter, in UML signature form.

    A canonical parameter is an object; a draft supplies a plain string, which
    `_clean_parameters` converts on the way in. Both are handled because this also runs
    over documents the editor has round-tripped.
    """
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, dict):
        return ""
    name = str(value.get("name") or "").strip()
    if not name:
        return ""
    type_name = str(value.get("type") or "").strip()
    return f"{name}: {type_name}" if type_name else name


def feature_compartments(features: Any) -> list[tuple[str, list[str]]]:
    if not isinstance(features, dict):
        return []
    grouped: Dict[str, list[str]] = {}
    for prop in features.get("properties") or []:
        if not isinstance(prop, dict) or not str(prop.get("name") or "").strip():
            continue
        kind = str(prop.get("kind") or "property")
        name = str(prop["name"]).strip()
        type_name = str(prop.get("type") or "").strip()
        direction = str(prop.get("direction") or "").strip()
        mult = _multiplicity_text(prop.get("multiplicity"))
        default = prop.get("default")
        text = f"{direction} {name}".strip() if kind == "flow" else name
        if type_name:
            text += f": {type_name}"
        if mult:
            text += f" [{mult}]"
        if default is not None:
            text += f" = {default}"
        grouped.setdefault(f"{kind} properties", []).append(text)
    # `parameters` and `returnType` were accepted, validated and persisted, and then
    # dropped here — every operation drew as `name()`. A field that is valid, saved and
    # invisible is worse than a rejected one: the author believes it was recorded. The
    # properties branch above already renders type and multiplicity, so this is the same
    # UML signature form the block beside it uses.
    operations = []
    for operation in features.get("operations") or []:
        if not isinstance(operation, dict) or not str(operation.get("name") or "").strip():
            continue
        parameters = ", ".join(
            _parameter_text(item) for item in operation.get("parameters") or []
            if _parameter_text(item)
        )
        text = f"{str(operation['name']).strip()}({parameters})"
        return_type = str(operation.get("returnType") or "").strip()
        if return_type:
            text += f": {return_type}"
        operations.append(text)
    if operations:
        grouped["operations"] = operations
    receptions = [str(v).strip() for v in features.get("receptions") or [] if str(v).strip()]
    if receptions:
        grouped["receptions"] = receptions
    # A constraint's `name` was discarded the same way. UML writes a named constraint as
    # `{name} expression`, which is how a reader tells one invariant from another when a
    # block carries several.
    constraints = []
    for constraint in features.get("constraints") or []:
        if not isinstance(constraint, dict) or not str(constraint.get("expression") or "").strip():
            continue
        expression = str(constraint["expression"]).strip()
        name = str(constraint.get("name") or "").strip()
        constraints.append(f"{{{name}}} {expression}" if name else expression)
    if constraints:
        grouped["constraints"] = constraints
    literals = [str(v).strip() for v in features.get("literals") or [] if str(v).strip()]
    if literals:
        grouped["literals"] = literals
    return list(grouped.items())


def bdd_compartment_height(item_count: int) -> float:
    """The vertical space one compartment takes up **when drawn**.

    This mirrors ``_draw_classifier_compartments`` line for line: the italic heading's
    baseline sits ``FONT_SIZE + 2`` below the compartment's top edge, then every row —
    the heading and each item — advances by one line.

    The two used to be worked out separately and disagreed by 9px per compartment, so a
    block with three compartments lost its last line off the bottom edge. The field was
    in the file and missing from the picture. Keep this the single source of that
    arithmetic; if the drawing changes, change it here.
    """
    return FONT_SIZE + 2 + (1 + item_count) * BDD_COMPARTMENT_LINE


def bdd_block_min_height(features: Any) -> float:
    compartments = feature_compartments(features)
    if not compartments:
        return BDD_EMPTY_MIN_HEIGHT

    height = BDD_HEADER_HEIGHT
    for _label, items in compartments:
        height += bdd_compartment_height(len(items))
    # The last row's descender falls below its baseline.
    height += BDD_COMPARTMENT_PAD
    return round(max(height, BDD_FILLED_MIN_HEIGHT), 1)


#: Shapes that draw their label **inside** the outline, so a long label has to make the
#: shape taller. Everything absent from this set — actor, initial and final nodes, fork and
#: join bars, pins, ports — writes its label underneath itself, where growing the shape
#: would distort a characteristic proportion instead of making room.
LABEL_INSIDE_SEMANTIC_TYPES = frozenset({
    "note", "opaqueAction", "objectNode", "centralBufferNode", "dataStoreNode",
    "useCase", "decisionNode", "mergeNode", "sendSignalAction", "acceptEventAction",
    "callBehaviorAction", "callOperationAction", "valueSpecificationAction",
})


#: A note's dog-ear eats this much width and height. Mirrors the `fold` in `_draw_note`.
NOTE_FOLD = 14.0


def wrapped_line_count(label: Any, width: float, reserve: float = 0.0) -> int:
    """How many lines *label* occupies once wrapped into a shape of *width*.

    *reserve* is width the shape cannot use for text — a note's dog-ear, for instance.
    """
    text = str(label or "").strip()
    if not text:
        return 0
    usable = max(1.0, width - reserve - TEXT_PADDING * 2)
    per_line = max(1, int(usable / (FONT_SIZE * CHAR_WIDTH_RATIO)))
    return max(1, math.ceil(len(text) / per_line))


def bdd_compartment_rows(items: Sequence[str], width: float) -> int:
    """How many drawn lines *items* occupy once wrapped to a block of *width*.

    A block is capped at ``LAYOUT_MAX_WIDTH``, so a long constraint expression cannot be
    made to fit by widening. It wraps instead, and the block has to be tall enough for
    the lines it wraps onto — otherwise the text runs out of the bottom of the box.
    """
    usable = max(1.0, width - TEXT_PADDING * 2)
    per_line = max(1, int(usable / (FONT_SIZE * CHAR_WIDTH_RATIO)))
    return sum(max(1, math.ceil(len(item) / per_line)) for item in items)


#: A use case with extension points draws them below its own label, inside the ellipse:
#: a separator, an italic "extension points" heading, then the points on one line. The
#: renderer places the last of those 30px below the centre and shifts the label 10px up,
#: so the ellipse has to be tall enough for both or the compartment spills out of the
#: bottom of the shape. The same disagreement between a drawer and a sizer clipped every
#: BDD block before H2 measured it.
USE_CASE_EXTENSION_SEPARATOR = 8.0
USE_CASE_EXTENSION_LINE = 11.0
USE_CASE_EXTENSION_LABEL_SHIFT = 10.0


def use_case_min_size(label: Any, extension_points: Any) -> Optional[Tuple[float, float]]:
    """Size a use case ellipse, or decline when it has nothing extra to hold.

    Returns ``None`` for the ordinary case so layout keeps its own base size, and only
    intervenes when extension points would otherwise be drawn outside the shape.
    """
    points = [str(v).strip() for v in (extension_points or ()) if str(v).strip()]
    if not points:
        return None

    base_w, base_h = LAYOUT_BASE_SIZES.get("useCase", LAYOUT_FALLBACK_SIZE)
    longest = max([str(label or ""), "extension points", ", ".join(points)], key=len)
    # An ellipse only offers its full width across the middle, so text needs more room
    # inside one than inside a rectangle of the same size.
    width = min(LAYOUT_MAX_WIDTH,
                max(base_w, len(longest) * LAYOUT_CHAR_WIDTH * 1.35 + LAYOUT_LABEL_PADDING))

    # Below the centre: separator, heading, the points themselves, then breathing room.
    below = (USE_CASE_EXTENSION_SEPARATOR + USE_CASE_EXTENSION_LINE * 2
             + USE_CASE_EXTENSION_LABEL_SHIFT)
    height = max(base_h, (below + USE_CASE_EXTENSION_LABEL_SHIFT) * 2)
    return float(round(width, 1)), float(round(height, 1))


def bdd_block_min_size(label: Any, features: Any) -> Tuple[float, float]:
    compartments = feature_compartments(features)
    longest = str(label or "")
    for compartment_label, items in compartments:
        if len(compartment_label) > len(longest):
            longest = compartment_label
        for item in items:
            if len(item) > len(longest):
                longest = item
    base_w = LAYOUT_BASE_SIZES.get("block", LAYOUT_FALLBACK_SIZE)[0]
    width = min(LAYOUT_MAX_WIDTH, max(base_w, len(longest) * LAYOUT_CHAR_WIDTH + LAYOUT_LABEL_PADDING))

    if not compartments:
        return float(width), float(BDD_EMPTY_MIN_HEIGHT)

    # Height follows the wrapped row count at the width just chosen, not the item count.
    height = BDD_HEADER_HEIGHT
    for _compartment_label, items in compartments:
        height += bdd_compartment_height(bdd_compartment_rows(items, width))
    height += BDD_COMPARTMENT_PAD
    return float(width), float(round(max(height, BDD_FILLED_MIN_HEIGHT), 1))
