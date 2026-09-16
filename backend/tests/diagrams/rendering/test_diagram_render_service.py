"""Tests for the SVG render service and the ``diagram_render`` tool.

Covers the pure ``DiagramRenderService.to_svg`` core (well-formed SVG, editor-mirroring
shapes, honored coordinates, container/parentId resolution, error handling), the
file-backed ``render(path)`` wrapper (sibling ``.svg`` write + the missing / malformed /
outside-workspace error cases), and the thin ``diagram_render`` MCP handler's error
mapping to the common shape.
"""

import asyncio
import json
import re
import struct
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from mcp.types import CallToolResult, ImageContent

from mcp_server import server
from services.shared.workspace_storage_service import (
    WorkspaceStorageService,
    DiagramNotFoundError,
    InvalidDiagramJSONError,
)
from services.diagrams.catalog.constants import bdd_block_min_height, bdd_block_min_size
from services.diagrams.rendering.diagram_render_service import (
    FONT_SIZE,
    MIN_FONT_SIZE,
    DiagramRenderService,
    DiagramRenderServiceError,
    _Box,
    _anchor_point,
    _attachment_profile,
    _fit_text,
    _route_orthogonal,
    _route_straight,
    _segment_direction,
    _wrap_text,
)

BLUEPRINTS_DIR = Path(__file__).resolve().parents[3] / "assets" / "blueprints"
ROUTE_FIXTURES = json.loads((Path(__file__).resolve().parents[2] / "edge_routing_fixtures.json").read_text(encoding="utf-8"))

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _run(coro):
    return asyncio.run(coro)


def _payload(result):
    """The machine-readable dict from a plain result or text-only ``CallToolResult``."""
    if isinstance(result, CallToolResult):
        return result.structuredContent or {}
    return result


def _image_blocks(result):
    """Inline image content blocks on a ``CallToolResult`` (empty for a plain dict)."""
    if isinstance(result, CallToolResult):
        return [b for b in result.content if isinstance(b, ImageContent)]
    return []


def _png_dimensions(png: bytes):
    return struct.unpack(">II", png[16:24])


def _example_paths():
    return sorted(BLUEPRINTS_DIR.glob("*/examples/answers/*/output.gp.json"))


def _activity_diagram():
    return {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": "activity_diagram",
        "id": "diagram_render_test",
        "name": "Render Test",
        "metadata": {"source": "test"},
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": [
            {
                "id": "n_start",
                "type": "gpNode",
                "position": {"x": 100, "y": 100},
                "width": 120,
                "height": 50,
                "data": {"label": "Start", "semanticType": "initialNode"},
            },
            {
                "id": "n_decide",
                "type": "gpNode",
                "position": {"x": 100, "y": 220},
                "width": 140,
                "height": 80,
                "data": {"label": "OK?", "semanticType": "decisionNode"},
            },
        ],
        "edges": [
            {
                "id": "e1",
                "source": "n_start",
                "target": "n_decide",
                "label": "go",
                "data": {"semanticType": "controlFlow"},
            }
        ],
    }


def _single_node_diagram(label, *, width=160, height=60, semantic="opaqueAction", node_type="gpNode"):
    data = {"label": label, "semanticType": semantic}
    return {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": "activity_diagram",
        "id": "fit_test",
        "name": "Fit Test",
        "metadata": {"source": "test"},
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": [
            {
                "id": "n1",
                "type": node_type,
                "position": {"x": 0, "y": 0},
                "width": width,
                "height": height,
                "data": data,
            }
        ],
        "edges": [],
    }


class AssuranceBadgeParityTests(SimpleTestCase):
    """The export must mark what the canvas marks.

    `assumed` has been badged on the canvas since the draft contract existed, and the SVG
    had no badge mechanism at all — so the artifact a reader is most likely to be shown,
    pasted into a document or a pull request, was the one that could not tell a cited fact
    from a guess. A picture that quietly drops the honesty marking is worse than one that
    never had it, because nobody knows to look.
    """

    @staticmethod
    def _origin(assurance):
        return {
            "assurance": assurance,
            "evidenceRefs": [],
            "assumptionRefs": [],
            "schemaRules": [],
            "rationale": "why",
        }

    def _svg(self, assurance=None):
        diagram = _single_node_diagram("Charge the card")
        if assurance is not None:
            diagram["nodes"][0]["origin"] = self._origin(assurance)
        # One node is the whole diagram, so a lone `user` element would be suppressed as
        # "entirely hand-drawn". Give it a drafted neighbour to contrast with.
        diagram["nodes"].append({
            "id": "n2",
            "type": "gpNode",
            "position": {"x": 0, "y": 200},
            "width": 160,
            "height": 60,
            "data": {"label": "Drafted", "semanticType": "opaqueAction"},
            "origin": self._origin("grounded"),
        })
        return DiagramRenderService().to_svg(diagram)

    def test_an_assumed_element_is_badged(self):
        self.assertIn("#d9a441", self._svg("assumed"))

    def test_a_hand_drawn_element_is_badged_differently(self):
        """A person's addition and a host's inference are both admissions, and they are
        not the same admission — one was never in the source, the other was inferred from
        it. Same badge shape, different colour, matching the canvas."""
        user = self._svg("user")

        self.assertIn("#8b9adc", user)
        self.assertNotIn("#d9a441", user)

    def test_grounded_and_conceptual_carry_no_badge(self):
        """Badging the norm teaches a reader to ignore badges."""
        for assurance in ("grounded", "conceptual"):
            with self.subTest(assurance=assurance):
                svg = self._svg(assurance)
                self.assertNotIn("#d9a441", svg)
                self.assertNotIn("#8b9adc", svg)

    def test_a_node_with_no_origin_renders_unchanged(self):
        """Every diagram made before origins existed still draws."""
        self.assertIn("<svg", self._svg(None))

    def test_the_badge_sits_on_the_corner_the_canvas_puts_it_on(self):
        """`.gp-assumed` is `top: -9px; right: -9px` on an 18px circle, so the badge
        straddles the node's top-right corner. The export places it at the same point."""
        svg = self._svg("assumed")

        # The node is 160x60 at the origin, so its top-right corner is (160, 0).
        self.assertRegex(svg, r'cx="160(\.0)?"')
        self.assertRegex(svg, r'r="9(\.0)?"')

    def test_the_badge_marks_the_visible_shape_not_the_layout_box(self):
        """An initial node's disc is 30px inside a 90x60 box. Anchoring the badge to the
        box left it floating 30px clear of the only thing on screen, marking nothing."""
        diagram = _single_node_diagram("Start", node_type="gpNode", width=90, height=60)
        diagram["nodes"][0]["data"]["semanticType"] = "initialNode"
        diagram["nodes"][0]["origin"] = self._origin("assumed")
        diagram["nodes"].append({
            "id": "n2",
            "type": "gpNode",
            "position": {"x": 0, "y": 200},
            "width": 160,
            "height": 60,
            "data": {"label": "Drafted", "semanticType": "opaqueAction"},
            "origin": self._origin("grounded"),
        })
        svg = DiagramRenderService().to_svg(diagram)

        box = _Box(0, 0, 90, 60, diagram["nodes"][0])
        _, (bx, by, bw, _bh) = _attachment_profile(box)
        badge = re.search(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="9"', svg)
        self.assertIsNotNone(badge, "expected a badge circle in the SVG")
        self.assertAlmostEqual(float(badge.group(1)), bx + bw, places=3)
        self.assertAlmostEqual(float(badge.group(2)), by, places=3)
        # And emphatically not the layout box's own corner.
        self.assertNotAlmostEqual(float(badge.group(1)), box.right, places=3)


class EntirelyHandDrawnTests(SimpleTestCase):
    """A badge is an admission, and an admission needs something to be an admission
    against. A diagram nobody drafted is `user` end to end, so badging all of it marks
    the norm — which is the exact noise `grounded` goes unbadged to avoid. Every node of
    every hand-drawn PNG export came out wearing a pencil.
    """

    @staticmethod
    def _origin(assurance):
        return {
            "assurance": assurance,
            "evidenceRefs": [],
            "assumptionRefs": [],
            "schemaRules": [],
            "rationale": "why",
        }

    def _diagram(self, *assurances):
        return {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "activity_diagram",
            "id": "hand_drawn",
            "name": "Hand Drawn",
            "metadata": {"source": "manual", "authoring": "custom"},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                {
                    "id": f"n{index}",
                    "type": "gpNode",
                    "position": {"x": 0, "y": index * 120},
                    "width": 160,
                    "height": 60,
                    "data": {"label": f"Step {index}", "semanticType": "opaqueAction"},
                    "origin": self._origin(assurance),
                }
                for index, assurance in enumerate(assurances)
            ],
            "edges": [],
        }

    def test_a_diagram_drawn_entirely_by_hand_carries_no_badges(self):
        svg = DiagramRenderService().to_svg(self._diagram("user", "user", "user"))

        self.assertNotIn("#8b9adc", svg)
        self.assertNotIn("\u270e", svg)

    def test_one_hand_drawn_element_beside_drafted_ones_is_still_marked(self):
        """The case the badge exists for, and the one this must not break."""
        svg = DiagramRenderService().to_svg(self._diagram("conceptual", "user", "conceptual"))

        self.assertEqual(svg.count("#8b9adc"), 1)

    def test_an_all_assumed_diagram_is_still_badged(self):
        """`assumed` names an accepted assumption a host had to author. Unlike `user` it
        is never the by-product of simply using the editor, so it is not the norm."""
        svg = DiagramRenderService().to_svg(self._diagram("assumed", "assumed"))

        self.assertEqual(svg.count("#d9a441"), 2)

    def test_an_empty_diagram_still_renders(self):
        self.assertIn("<svg", DiagramRenderService().to_svg(self._diagram()))


class EdgeRoutingParityTests(SimpleTestCase):
    def test_attachment_profiles_match_visible_primitive_bounds(self):
        cases = [
            (_Box(0, 0, 90, 60, {"data": {"label": "Initial", "semanticType": "initialNode"}}), ("ellipse", (30.0, 7.8, 30.0, 30.0))),
            (_Box(0, 0, 90, 60, {"data": {"label": "Final", "semanticType": "activityFinalNode"}}), ("ellipse", (30.0, 7.8, 30.0, 30.0))),
            (_Box(0, 0, 90, 60, {"data": {"label": "Flow Final", "semanticType": "flowFinalNode"}}), ("ellipse", (30.0, 7.8, 30.0, 30.0))),
            (_Box(0, 0, 90, 60, {"data": {"label": "", "semanticType": "initialNode"}}), ("ellipse", (30.0, 15.0, 30.0, 30.0))),
            (_Box(0, 0, 90, 120, {"data": {"label": "Actor", "semanticType": "actor"}}), ("ellipse", (33.0, 30.8, 24.0, 42.0))),
            (_Box(0, 0, 90, 120, {"data": {"label": "", "semanticType": "actor"}}), ("ellipse", (33.0, 38.0, 24.0, 42.0))),
            (_Box(0, 0, 200, 70, {"data": {"semanticType": "useCase"}}), ("ellipse", (0, 0, 200, 70))),
            (_Box(0, 0, 140, 80, {"data": {"semanticType": "decisionNode"}}), ("diamond", (0, 0, 140, 80))),
            (_Box(0, 0, 160, 60, {"data": {"semanticType": "opaqueAction"}}), ("box", (0, 0, 160, 60))),
        ]
        for box, expected in cases:
            with self.subTest(semantic=box.node["data"]["semanticType"], label=box.node["data"].get("label")):
                shape, bounds = _attachment_profile(box)
                self.assertEqual(shape, expected[0])
                for actual, value in zip(bounds, expected[1]):
                    self.assertAlmostEqual(actual, value, places=6)

    def test_projects_anchors_onto_visible_primitive_boundaries(self):
        initial = _Box(0, 0, 90, 60, {"data": {"label": "Initial", "semanticType": "initialNode"}})
        ellipse = _Box(0, 0, 100, 100, {"data": {"semanticType": "useCase"}})
        actor = _Box(0, 0, 90, 120, {"data": {"label": "Actor", "semanticType": "actor"}})
        diamond = _Box(0, 0, 100, 100, {"data": {"semanticType": "decisionNode"}})
        wide_diamond = _Box(0, 0, 240, 100, {"data": {"semanticType": "mergeNode"}})
        initial_point = _anchor_point(initial, {"side": "top", "offset": 0.5})
        ellipse_point = _anchor_point(ellipse, {"side": "top", "offset": 0.75})
        actor_point = _anchor_point(actor, {"side": "top", "offset": 0.5})
        diamond_point = _anchor_point(diamond, {"side": "top", "offset": 0.75})
        wide_diamond_point = _anchor_point(wide_diamond, {"side": "top", "offset": 0.75})
        self.assertAlmostEqual(initial_point[0], 45, places=2)
        self.assertAlmostEqual(initial_point[1], 7.8, places=2)
        self.assertAlmostEqual(ellipse_point[0], 72.36, places=2)
        self.assertAlmostEqual(ellipse_point[1], 5.28, places=2)
        self.assertAlmostEqual(actor_point[0], 45, places=2)
        self.assertAlmostEqual(actor_point[1], 30.8, places=2)
        self.assertAlmostEqual(diamond_point[0], 66.67, places=2)
        self.assertAlmostEqual(diamond_point[1], 16.67, places=2)
        self.assertAlmostEqual(wide_diamond_point[0], 160, places=2)
        self.assertAlmostEqual(wide_diamond_point[1], 16.67, places=2)

    def test_shared_orthogonal_route_fixtures(self):
        def box(value):
            return _Box(value["x"], value["y"], value["w"], value["h"], {})

        for fixture in ROUTE_FIXTURES["orthogonalCases"]:
            with self.subTest(name=fixture["name"]):
                result = _route_orthogonal(
                    box(fixture["source"]),
                    box(fixture["target"]),
                    fixture["geometry"],
                )
                actual = {
                    "points": [{"x": point[0], "y": point[1]} for point in result["points"]],
                    "mid": {"x": result["mid"][0], "y": result["mid"][1]},
                    "sourceAnchor": result["sourceAnchor"],
                    "targetAnchor": result["targetAnchor"],
                }
                self.assertEqual(actual, fixture["expected"])

    def test_shared_straight_route_fixtures(self):
        def box(value):
            return _Box(value["x"], value["y"], value["w"], value["h"], {})

        for fixture in ROUTE_FIXTURES["straightCases"]:
            with self.subTest(name=fixture["name"]):
                result = _route_straight(box(fixture["source"]), box(fixture["target"]), fixture["geometry"])
                actual = {
                    "points": [{"x": point[0], "y": point[1]} for point in result["points"]],
                    "mid": {"x": result["mid"][0], "y": result["mid"][1]},
                    "sourceAnchor": result["sourceAnchor"],
                    "targetAnchor": result["targetAnchor"],
                }
                self.assertEqual(actual, fixture["expected"])

    def test_segment_direction_normalizes_diagonal_vectors(self):
        direction = _segment_direction((1.0, 2.0), (4.0, 6.0))
        self.assertAlmostEqual(direction[0], 0.6)
        self.assertAlmostEqual(direction[1], 0.8)
        self.assertEqual(_segment_direction((1.0, 1.0), (1.0, 1.0)), (0.0, 0.0))


class ToSvgCoreTests(SimpleTestCase):
    def setUp(self):
        self.svc = DiagramRenderService()

    def test_returns_well_formed_svg(self):
        svg = self.svc.to_svg(_activity_diagram())
        self.assertTrue(svg.lstrip().startswith("<?xml"))
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)

    def test_all_answer_key_examples_render(self):
        paths = _example_paths()
        self.assertEqual(len(paths), 36, msg="expected 36 answer-key examples (12 eval per type)")
        for path in paths:
            with self.subTest(example=path.name, parent=path.parent.name):
                diagram = json.loads(path.read_text(encoding="utf-8"))
                svg = self.svc.to_svg(diagram)
                self.assertIn("<svg", svg)
                self.assertIn("</svg>", svg)

    def test_honors_saved_coordinates_in_viewbox(self):
        diagram = _activity_diagram()
        diagram["nodes"][0]["position"] = {"x": 1000, "y": 2000}
        diagram["nodes"][1]["position"] = {"x": 1000, "y": 2200}
        svg = self.svc.to_svg(diagram)
        match = re.search(r'viewBox="([\d.\- ]+)"', svg)
        self.assertIsNotNone(match)
        min_x, min_y, _w, _h = (float(v) for v in match.group(1).split())
        # The view box should sit near the (far-away) saved node coordinates,
        # confirming the renderer trusts positions rather than re-laying out.
        self.assertGreater(min_x, 900)
        self.assertGreater(min_y, 1900)

    def test_decision_renders_as_diamond_path(self):
        svg = self.svc.to_svg(_activity_diagram())
        # The diamond is drawn as a closed 4-point path.
        self.assertRegex(svg, r"<path d=\"M[\d.\-]+,[\d.\-]+ L[\d.\-]+,[\d.\-]+ L[\d.\-]+,[\d.\-]+ L[\d.\-]+,[\d.\-]+ Z\"")

    def test_permitted_arrow_override_moves_only_the_directional_marker(self):
        diagram = _activity_diagram()
        forward = self.svc.to_svg(diagram)
        diagram["edges"][0]["data"]["arrow"] = "backward"
        backward = self.svc.to_svg(diagram)
        route = re.search(r'<path d="(M[^\"]+)" fill="none" stroke=', forward)
        self.assertIsNotNone(route)
        points = re.findall(r"[ML]([\d.-]+),([\d.-]+)", route.group(1))
        source = f"M{points[0][0]},{points[0][1]}"
        target = f"M{points[-1][0]},{points[-1][1]}"
        self.assertGreater(backward.count(source), forward.count(source))
        self.assertGreater(forward.count(target), backward.count(target))

    def test_use_case_shapes_present(self):
        diagram = json.loads(
            (
                BLUEPRINTS_DIR
                / "use_case_diagram/examples/answers/01-streaming-service/output.gp.json"
            ).read_text(encoding="utf-8")
        )
        svg = self.svc.to_svg(diagram)
        self.assertIn("<ellipse", svg)  # useCase nodes
        self.assertIn("<circle", svg)   # actor head

    def test_draws_containers_then_edges_then_nodes_then_edge_labels(self):
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "use_case_diagram",
            "id": "layering",
            "name": "Layering",
            "nodes": [
                {"id": "boundary", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 320, "height": 240, "data": {"label": "Boundary", "semanticType": "subject"}, "style": {"borderColor": "#aa0000"}},
                {"id": "actor", "type": "gpNode", "position": {"x": 20, "y": 80}, "width": 90, "height": 120, "data": {"label": "Actor", "semanticType": "actor"}, "style": {"borderColor": "#0000aa"}},
                {"id": "use-case", "type": "gpNode", "position": {"x": 150, "y": 90}, "width": 140, "height": 70, "data": {"label": "Use Case", "semanticType": "useCase"}, "style": {"borderColor": "#aa00aa"}},
            ],
            "edges": [{"id": "edge", "source": "actor", "target": "use-case", "label": "EDGE-LABEL", "data": {"semanticType": "association"}, "style": {"stroke": "#00aa00"}}],
        }
        svg = self.svc.to_svg(diagram)
        container_index = svg.index('stroke="#aa0000"')
        edge_index = svg.index('stroke="#00aa00"')
        actor_index = svg.index('stroke="#0000aa"')
        use_case_index = svg.index('stroke="#aa00aa"')
        label_index = svg.index("EDGE-LABEL")
        self.assertLess(container_index, edge_index)
        self.assertLess(edge_index, actor_index)
        self.assertLess(edge_index, use_case_index)
        self.assertLess(max(actor_index, use_case_index), label_index)

    def test_activity_initial_final_fork_join_render(self):
        def n(nid, semantic, y, w=60, h=60):
            return {
                "id": nid, "type": "gpNode", "position": {"x": 60, "y": y},
                "width": w, "height": h, "data": {"label": "", "semanticType": semantic},
            }
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1", "kind": "diagram",
            "diagramType": "activity_diagram", "id": "d", "name": "n", "metadata": {},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                n("s", "initialNode", 0), n("f", "forkNode", 100, 120, 30),
                n("a", "opaqueAction", 160, 160, 60), n("j", "joinNode", 260, 120, 30),
                n("e", "activityFinalNode", 320),
            ],
            "edges": [
                {"id": "e1", "source": "s", "target": "f", "data": {"semanticType": "controlFlow"}},
                {"id": "e2", "source": "f", "target": "a", "data": {"semanticType": "controlFlow"}},
                {"id": "e3", "source": "f", "target": "j", "data": {"semanticType": "controlFlow"}},
                {"id": "e4", "source": "a", "target": "j", "data": {"semanticType": "controlFlow"}},
                {"id": "e5", "source": "j", "target": "e", "data": {"semanticType": "controlFlow"}},
            ],
        }
        svg = self.svc.to_svg(diagram)
        self.assertIn("<svg", svg)
        # initial-node disc (1) + activity-final bull's-eye (ring + inner dot) => >= 3 circles.
        self.assertGreaterEqual(svg.count("<circle"), 3)
        self.assertIn('r="15.0"', svg)
        # fork + join synchronization bars => rectangles.
        self.assertGreaterEqual(svg.count("<rect"), 2)

    def test_association_end_aggregation_markers_render_at_either_end(self):
        def bdd(source_aggregation="none", target_aggregation="none"):
            return {
                "schemaVersion": "graphpilot.diagram.v1", "kind": "diagram",
                "diagramType": "bdd_diagram", "id": "d", "name": "n", "metadata": {},
                "viewport": {"x": 0, "y": 0, "zoom": 1},
                "nodes": [
                    {"id": "b1", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 160, "height": 90,
                     "data": {"label": "Whole", "semanticType": "block"}},
                    {"id": "b2", "type": "gpNode", "position": {"x": 0, "y": 220}, "width": 160, "height": 90,
                     "data": {"label": "Part", "semanticType": "block"}},
                ],
                "edges": [{
                    "id": "e", "source": "b1", "target": "b2",
                    "data": {
                        "semanticType": "association",
                        "sourceEnd": {"aggregation": source_aggregation},
                        "targetEnd": {"aggregation": target_aggregation},
                    },
                }],
            }

        plain = self.svc.to_svg(bdd())
        source_shared = self.svc.to_svg(bdd(source_aggregation="shared"))
        target_composite_diagram = bdd(target_aggregation="composite")
        target_composite = self.svc.to_svg(target_composite_diagram)
        composition_diagram = bdd()
        composition_diagram["edges"][0]["data"] = {"semanticType": "composition"}
        composition = self.svc.to_svg(composition_diagram)
        self.assertNotEqual(plain, source_shared)
        self.assertNotEqual(plain, target_composite)
        self.assertEqual(composition, target_composite)
        self.assertGreater(source_shared.count("#ffffff"), target_composite.count("#ffffff"))

    def test_manual_route_and_label_offset_render_from_canonical_geometry(self):
        fixture = ROUTE_FIXTURES["orthogonalCases"][3]
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "bdd_diagram",
            "id": "route",
            "name": "Route",
            "metadata": {},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                {"id": "source", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 100, "height": 60,
                 "data": {"label": "Source", "semanticType": "block"}},
                {"id": "target", "type": "gpNode", "position": {"x": 300, "y": 200}, "width": 100, "height": 60,
                 "data": {"label": "Target", "semanticType": "block"}},
            ],
            "edges": [{
                "id": "edge", "source": "source", "target": "target", "label": "manual",
                "route": {**fixture["geometry"], "labelOffset": {"x": 8, "y": -100}},
                "data": {"semanticType": "association"},
            }],
        }
        svg = self.svc.to_svg(diagram)
        self.assertIn('d="M100.0,15.0 L116.0,15.0 L116.0,40.0 L375.0,40.0 L375.0,200.0"', svg)
        self.assertRegex(svg, r'<text x="313\.0" y="-60\.0"[^>]*>manual</text>')
        min_y = float(re.search(r'viewBox="[\d.\-]+ ([\d.\-]+)', svg).group(1))
        self.assertLess(min_y, -60)

    def test_straight_route_projects_use_case_anchors_to_one_diagonal_segment(self):
        fixture = ROUTE_FIXTURES["straightCases"][2]
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "custom",
            "id": "straight-route",
            "name": "Straight Route",
            "metadata": {},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                {"id": "source", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 100, "height": 60,
                 "data": {"label": "Source", "semanticType": "useCase"}},
                {"id": "target", "type": "gpNode", "position": {"x": 300, "y": 200}, "width": 100, "height": 60,
                 "data": {"label": "Target", "semanticType": "useCase"}},
            ],
            "edges": [{
                "id": "edge", "source": "source", "target": "target",
                "route": fixture["geometry"],
                "data": {"semanticType": "generalization"},
            }],
        }
        svg = self.svc.to_svg(diagram)
        route = re.search(r'<path d="(M[^\"]+)" fill="none"', svg)
        self.assertIsNotNone(route)
        points = [(float(x), float(y)) for x, y in re.findall(r"[ML]([\d.-]+),([\d.-]+)", route.group(1))]
        self.assertEqual(len(points), 2)
        for actual, expected in zip(points, ((94.72136, 16.58359), (372.36068, 203.16718))):
            self.assertAlmostEqual(actual[0], expected[0], places=5)
            self.assertAlmostEqual(actual[1], expected[1], places=5)

    def test_bdd_block_renders_primary_stereotype(self):
        diagram = _single_node_diagram("Gear", semantic="block", node_type="gpNode")
        diagram["diagramType"] = "bdd_diagram"
        diagram["nodes"][0]["data"]["stereotype"] = "enumeration"
        svg = self.svc.to_svg(diagram)
        self.assertIn("«enumeration»", svg)

    def test_direct_include_and_extend_render_keywords(self):
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1", "kind": "diagram",
            "diagramType": "use_case_diagram", "id": "d", "name": "n", "metadata": {},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                {"id": "base", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 180, "height": 70,
                 "data": {"label": "Base", "semanticType": "useCase"}},
                {"id": "other", "type": "gpNode", "position": {"x": 260, "y": 0}, "width": 180, "height": 70,
                 "data": {"label": "Other", "semanticType": "useCase"}},
            ],
            "edges": [
                {"id": "i", "source": "base", "target": "other", "data": {"semanticType": "include"}},
                {"id": "x", "source": "other", "target": "base", "label": "«extend»", "data": {"semanticType": "extend", "condition": "optional"}},
            ],
        }
        svg = self.svc.to_svg(diagram)
        self.assertIn("include", svg)
        self.assertIn("extend", svg)
        self.assertEqual(svg.count("«extend»"), 1)
        self.assertIn("[optional]", svg)

    def test_authorable_relationship_tools_render_catalog_lines_and_markers(self):
        expected = {
            "controlFlow": (False, True),
            "commentLink": (True, False),
            "association": (False, False),
            "composition": (False, True),
            "generalization": (False, True),
            "include": (True, True),
            "extend": (True, True),
            "dependency": (True, True),
            "realization": (True, True),
        }
        for semantic, (dashed, marker) in expected.items():
            diagram = {
                "schemaVersion": "graphpilot.diagram.v1", "kind": "diagram",
                "diagramType": "custom", "id": "relationships", "name": "Relationships", "metadata": {},
                "viewport": {"x": 0, "y": 0, "zoom": 1},
                "nodes": [
                    {"id": "source", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 120, "height": 60, "data": {"label": "", "semanticType": "opaqueAction"}},
                    {"id": "target", "type": "gpNode", "position": {"x": 260, "y": 0}, "width": 120, "height": 60, "data": {"label": "", "semanticType": "opaqueAction"}},
                ],
                "edges": [{"id": "edge", "source": "source", "target": "target", "data": {"semanticType": semantic}, "style": {"stroke": "#123abc"}}],
            }
            with self.subTest(semantic=semantic):
                svg = self.svc.to_svg(diagram)
                self.assertEqual('stroke-dasharray="6,4"' in svg, dashed)
                self.assertEqual(svg.count('stroke="#123abc"'), 2 if marker else 1)

    def test_note_renders_outer_diagonal_and_inner_dog_ear(self):
        diagram = _single_node_diagram("Comment", semantic="note", width=160, height=80)
        svg = self.svc.to_svg(diagram)
        self.assertIn('d="M0.0,0.0 L146.0,0.0 L160.0,14.0 L160.0,80.0 L0.0,80.0 Z"', svg)
        self.assertIn('d="M146.0,0.0 L146.0,14.0 L160.0,14.0"', svg)

    def test_unknown_semantic_type_renders_via_fallback(self):
        # An off-catalog semanticType must still render through the fallback, not crash.
        diagram = _single_node_diagram("Mystery", semantic="quantum_gate")
        svg = self.svc.to_svg(diagram)
        self.assertIn("Mystery", svg)

    def test_universal_generics_render(self):
        # Canvas-only universal shapes—classifier boxes and the port square—must render.
        for semantic in ("class", "interface", "component", "package", "requirement", "port"):
            diagram = _single_node_diagram(f"{semantic}A", semantic=semantic, width=180, height=90)
            svg = self.svc.to_svg(diagram)
            self.assertIn(f"{semantic}A", svg)

    def test_bdd_structured_features_render(self):
        diagram = _single_node_diagram("Vehicle", semantic="block", node_type="gpNode", width=240, height=240)
        diagram["diagramType"] = "bdd_diagram"
        diagram["nodes"][0]["data"]["features"] = {
            "properties": [
                {"kind": "part", "name": "engine", "type": "Engine"},
                {"kind": "value", "name": "mass", "type": "kg", "default": 12},
            ],
            "operations": [{"name": "start"}],
            "receptions": ["started"],
            "constraints": [{"expression": "mass > 0"}],
            "literals": ["PARK"],
        }
        svg = self.svc.to_svg(diagram)
        for text in (
            "part properties", "engine: Engine", "value properties", "mass: kg = 12",
            "operations", "start()", "receptions", "started", "constraints", "mass &gt; 0",
            "literals", "PARK",
        ):
            self.assertIn(text, svg)

    def test_bdd_empty_feature_groups_are_suppressed(self):
        diagram = _single_node_diagram("Vehicle", semantic="block", node_type="gpNode", width=200, height=160)
        diagram["diagramType"] = "bdd_diagram"
        diagram["nodes"][0]["data"]["features"] = {
            "properties": [{"kind": "value", "name": "mass", "type": "kg"}],
            "operations": [], "receptions": [""], "constraints": [], "literals": [],
        }
        svg = self.svc.to_svg(diagram)
        self.assertIn("value properties", svg)
        self.assertIn("mass: kg", svg)
        self.assertNotIn("operations", svg)
        self.assertIn('d="M0.0,34.0 L200.0,34.0"', svg)

    def test_empty_bdd_classifier_preserves_saved_height_without_a_partition(self):
        empty_features = (
            None,
            {},
            {"properties": [{"kind": "value", "name": "   "}], "operations": [], "literals": [""]},
        )
        for features in empty_features:
            with self.subTest(features=features):
                diagram = _single_node_diagram(
                    "Vehicle", semantic="block", node_type="gpNode", width=200, height=160
                )
                diagram["diagramType"] = "bdd_diagram"
                diagram["nodes"][0]["data"]["features"] = features

                svg = self.svc.to_svg(diagram)

                self.assertIn('<rect x="0.0" y="0.0" width="200.0" height="160.0"', svg)
                self.assertNotIn("<path", svg)
                stereotype_y = float(re.search(r'<text x="100\.0" y="([\d.]+)"[^>]*>«block»</text>', svg).group(1))
                name_y = float(re.search(r'<text x="100\.0" y="([\d.]+)"[^>]*>Vehicle</text>', svg).group(1))
                self.assertAlmostEqual((stereotype_y + name_y) / 2, 80.0, delta=2.0)

    def test_bdd_malformed_feature_collections_do_not_crash(self):
        features = {"properties": [5, {}], "operations": [5, "start", {}], "receptions": []}
        diagram = _single_node_diagram("Vehicle", semantic="block", node_type="gpNode", width=200, height=160)
        diagram["diagramType"] = "bdd_diagram"
        diagram["nodes"][0]["data"]["features"] = features
        svg = self.svc.to_svg(diagram)
        self.assertIn("Vehicle", svg)
        self.assertNotIn("engine", svg)
        self.assertGreater(bdd_block_min_height(features), 0)
        width, height = bdd_block_min_size("Vehicle", features)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

    def test_bdd_block_min_height_compacts_only_empty_content(self):
        empty = bdd_block_min_height({})
        suppressed = bdd_block_min_height({"properties": [{"kind": "value", "name": ""}]})
        short_filled = bdd_block_min_height({"properties": [{"kind": "value", "name": "m"}]})
        tall_filled = bdd_block_min_height({
            "properties": [
                {"kind": "part", "name": "a", "type": "A"},
                {"kind": "part", "name": "b", "type": "B"},
                {"kind": "part", "name": "c", "type": "C"},
                {"kind": "value", "name": "m", "type": "kg"},
                {"kind": "value", "name": "n", "type": "kg"},
            ],
        })

        self.assertEqual(empty, 48.0)
        self.assertEqual(bdd_block_min_height(None), empty)
        self.assertEqual(suppressed, empty)
        self.assertEqual(bdd_block_min_size("Vehicle", {})[1], empty)
        self.assertEqual(short_filled, 90.0)
        self.assertGreater(tall_filled, short_filled)

    def test_proxy_and_full_ports_render_type_and_conjugation(self):
        for semantic, keyword in (("proxyPort", "proxy"), ("fullPort", "full")):
            diagram = _single_node_diagram("Power", semantic=semantic, node_type="gpNode", width=140, height=60)
            diagram["diagramType"] = "bdd_diagram"
            diagram["nodes"][0]["data"]["port"] = {"type": "PowerIF", "isConjugated": True}
            svg = self.svc.to_svg(diagram)
            self.assertIn(keyword, svg)
            self.assertIn("PowerIF", svg)

    def test_parent_id_child_is_offset_by_parent_position(self):
        # A child with parentId stores a position relative to its parent; the
        # rendered child must land inside the parent's absolute box.
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "use_case_diagram",
            "id": "d",
            "name": "n",
            "metadata": {},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                {
                    "id": "boundary",
                    "type": "gpNode",
                    "position": {"x": 500, "y": 500},
                    "width": 300,
                    "height": 300,
                    "data": {"label": "Sys", "semanticType": "subject"},
                },
                {
                    "id": "uc",
                    "type": "gpNode",
                    "position": {"x": 40, "y": 40},
                    "width": 120,
                    "height": 60,
                    "data": {"label": "Do", "semanticType": "useCase"},
                    "parentId": "boundary",
                },
            ],
            "edges": [],
        }
        svg = self.svc.to_svg(diagram)
        match = re.search(r'viewBox="([\d.\- ]+)"', svg)
        min_x, min_y, _w, _h = (float(v) for v in match.group(1).split())
        # Child absolute origin is 540,540 — inside the 500..800 boundary; the
        # whole drawing's min corner is driven by the boundary at 500,500 (- pad).
        self.assertLess(min_x, 500)
        self.assertGreater(min_x, 400)

    def test_non_dict_raises(self):
        with self.assertRaises(DiagramRenderServiceError):
            self.svc.to_svg([])  # type: ignore[arg-type]

    def test_missing_nodes_raises(self):
        with self.assertRaises(DiagramRenderServiceError):
            self.svc.to_svg({"edges": []})

    def test_non_object_node_entry_raises_render_error(self):
        with self.assertRaises(DiagramRenderServiceError):
            self.svc.to_svg({"nodes": [1], "edges": []})

    def test_non_object_node_data_raises_render_error(self):
        diagram = _single_node_diagram("Bad")
        diagram["nodes"][0]["data"] = "not an object"
        with self.assertRaises(DiagramRenderServiceError):
            self.svc.to_svg(diagram)

    def test_num_rejects_non_finite_values(self):
        # Guards the path-free preview route: NaN/inf coordinates fall back to a
        # finite default instead of leaking "nan"/"inf" into the SVG.
        from services.diagrams.rendering.diagram_render_service import _num

        self.assertEqual(_num(float("nan"), 5.0), 5.0)
        self.assertEqual(_num(float("inf"), 5.0), 5.0)
        self.assertEqual(_num(float("-inf"), 5.0), 5.0)
        self.assertEqual(_num("not a number", 5.0), 5.0)
        self.assertEqual(_num(None, 5.0), 5.0)
        self.assertEqual(_num(3, 5.0), 3.0)  # valid value passes through

    def test_non_finite_position_renders_without_crashing(self):
        # A NaN/inf position (possible via the pre-validation preview route) must
        # still produce a well-formed SVG (coords fall back to finite defaults).
        diagram = _activity_diagram()
        diagram["nodes"][0]["position"] = {"x": float("nan"), "y": float("inf")}
        svg = self.svc.to_svg(diagram)
        self.assertIn("</svg>", svg)
        self.assertNotIn('"nan"', svg.lower())  # no attribute value is nan

    def test_empty_diagram_renders(self):
        svg = self.svc.to_svg(
            {
                "schemaVersion": "graphpilot.diagram.v1",
                "kind": "diagram",
                "diagramType": "activity_diagram",
                "id": "d",
                "name": "n",
                "metadata": {},
                "viewport": {"x": 0, "y": 0, "zoom": 1},
                "nodes": [],
                "edges": [],
            }
        )
        self.assertIn("</svg>", svg)


class ToPngCoreTests(SimpleTestCase):
    """The pure SVG→PNG rasterization core (``to_png``), derived from the same SVG."""

    def setUp(self):
        self.svc = DiagramRenderService()

    def test_returns_valid_png_bytes(self):
        png = self.svc.to_png(_activity_diagram())
        self.assertIsInstance(png, bytes)
        self.assertTrue(png.startswith(_PNG_MAGIC))

    def test_caps_longest_side_at_max_px(self):
        # A diagram with far-apart nodes is taller than max_px at 2x; the cap applies.
        diagram = _activity_diagram()
        diagram["nodes"][1]["position"] = {"x": 100, "y": 3000}
        png = self.svc.to_png(diagram, max_px=512)
        width, height = _png_dimensions(png)
        self.assertLessEqual(max(width, height), 512)

    def test_scale_multiplies_uncapped_output(self):
        diagram = _single_node_diagram("Hi", width=100, height=40)
        small = _png_dimensions(self.svc.to_png(diagram, scale=1.0, max_px=None))
        large = _png_dimensions(self.svc.to_png(diagram, scale=2.0, max_px=None))
        self.assertEqual(large[0], small[0] * 2)
        self.assertEqual(large[1], small[1] * 2)

    def test_renders_text_glyphs(self):
        # The same render with fonts disabled has materially fewer non-white bytes;
        # here we just assert a labelled diagram rasterizes to a non-trivial PNG.
        png = self.svc.to_png(_single_node_diagram("Approve Order"))
        self.assertGreater(len(png), 200)

    def test_non_dict_raises(self):
        with self.assertRaises(DiagramRenderServiceError):
            self.svc.to_png([])  # type: ignore[arg-type]


class RenderFileWrapperTests(SimpleTestCase):
    def setUp(self):
        self.svc = DiagramRenderService()
        self.workspace = Path(tempfile.mkdtemp(prefix="gp_render_"))
        self.storage = self.workspace / ".graphpilot"
        self.storage.mkdir()
        self.diagrams = self.storage / "diagrams"

    def tearDown(self):
        import shutil

        shutil.rmtree(self.workspace, ignore_errors=True)

    def _save(self, name, diagram):
        return WorkspaceStorageService(str(self.workspace)).create_diagram(name, diagram)

    def test_writes_sibling_svg(self):
        src = self._save("order-approval", _activity_diagram())
        svg_path = self.svc.render(src)
        self.assertEqual(svg_path.name, "order-approval.svg")
        self.assertEqual(svg_path.parent, self.diagrams)
        self.assertTrue(svg_path.is_file())
        self.assertTrue(svg_path.read_text(encoding="utf-8").lstrip().startswith("<?xml"))

    def test_artifact_name_preserves_dots_before_gp_json_suffix(self):
        src = self.storage / "system.v2.gp.json"
        src.write_text(json.dumps(_activity_diagram()), encoding="utf-8")
        self.assertEqual(self.svc.render(src).name, "system.v2.svg")
        self.assertEqual(self.svc.render_png(src).name, "system.v2.png")

    def test_render_png_writes_sibling_png(self):
        src = self._save("order-approval", _activity_diagram())
        png_path = self.svc.render_png(src)
        self.assertEqual(png_path.name, "order-approval.png")
        self.assertEqual(png_path.parent, self.diagrams)
        self.assertTrue(png_path.is_file())
        self.assertTrue(png_path.read_bytes().startswith(_PNG_MAGIC))

    def test_missing_file_raises_not_found(self):
        with self.assertRaises(DiagramNotFoundError):
            self.svc.render(self.storage / "nope.gp.json")

    def test_malformed_json_raises(self):
        bad = self.storage / "broken.gp.json"
        bad.write_text("{not json", encoding="utf-8")
        with self.assertRaises(InvalidDiagramJSONError):
            self.svc.render(bad)

    def test_a_diagram_outside_storage_renders_beside_itself(self):
        """A `.gp.json` in an ordinary folder is an ordinary diagram — the examples the
        product ships are exactly that. Its SVG lands next to it."""
        outside = self.workspace / "loose.gp.json"
        outside.write_text(json.dumps(_activity_diagram()), encoding="utf-8")
        svg_path = self.svc.render(outside)
        self.assertEqual(svg_path.name, "loose.svg")
        self.assertEqual(svg_path.parent, outside.parent)
        self.assertTrue(svg_path.is_file())


class DiagramRenderToolTests(SimpleTestCase):
    def setUp(self):
        self.workspace = Path(tempfile.mkdtemp(prefix="gp_render_tool_"))
        self.storage = self.workspace / ".graphpilot"
        self.storage.mkdir()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.workspace, ignore_errors=True)

    def test_render_returns_svg_path(self):
        src = WorkspaceStorageService(str(self.workspace)).create_diagram("flow", _activity_diagram())
        result = _payload(_run(server.diagram_render(str(src))))
        self.assertIn("svgPath", result, msg=result)
        svg_path = Path(result["svgPath"])
        self.assertEqual(svg_path.name, "flow.svg")
        self.assertTrue(svg_path.is_file())

    def test_missing_returns_error_shape(self):
        result = _run(server.diagram_render(str(self.storage / "missing.gp.json")))
        self.assertEqual(_payload(result)["error"]["code"], "diagram_not_found")

    def test_outside_workspace_renders_instead_of_refusing(self):
        loose = self.workspace / "loose.gp.json"
        loose.write_text(json.dumps(_activity_diagram()), encoding="utf-8")
        result = _payload(_run(server.diagram_render(str(loose))))
        self.assertIn("svgPath", result, msg=result)
        self.assertEqual(Path(result["svgPath"]).name, "loose.svg")

    def test_malformed_returns_error_shape(self):
        bad = self.storage / "bad.gp.json"
        bad.write_text("{nope", encoding="utf-8")
        result = _run(server.diagram_render(str(bad)))
        self.assertEqual(_payload(result)["error"]["code"], "invalid_diagram_json")

    def test_inline_diagram_returns_svg_without_writing(self):
        result = _payload(_run(server.diagram_render(diagram=_activity_diagram())))
        self.assertNotIn("error", result, msg=result)
        self.assertIn("svg", result)
        self.assertTrue(result["svg"].lstrip().startswith("<?xml"))
        # Inline mode writes nothing to the workspace.
        self.assertEqual(list(self.storage.iterdir()), [])

    def test_inline_invalid_diagram_returns_error_shape(self):
        result = _run(server.diagram_render(diagram={"nodes": "oops"}))
        self.assertEqual(_payload(result)["error"]["code"], "render_failed")

    def test_both_inputs_returns_error_shape(self):
        src = WorkspaceStorageService(str(self.workspace)).create_diagram("flow", _activity_diagram())
        result = _run(server.diagram_render(str(src), diagram=_activity_diagram()))
        self.assertEqual(_payload(result)["error"]["code"], "invalid_arguments")

    def test_no_input_returns_error_shape(self):
        result = _run(server.diagram_render())
        self.assertEqual(_payload(result)["error"]["code"], "invalid_arguments")

    def test_invalid_format_returns_error_shape(self):
        result = _run(server.diagram_render(diagram=_activity_diagram(), format="gif"))
        self.assertEqual(_payload(result)["error"]["code"], "invalid_arguments")

    def test_inline_png_returns_error_requiring_path(self):
        # PNG is a file-save action, so it needs a diagramPath to write beside.
        result = _run(server.diagram_render(diagram=_activity_diagram(), format="png"))
        self.assertEqual(_payload(result)["error"]["code"], "invalid_arguments")
        self.assertEqual(list(self.storage.iterdir()), [])

    def test_path_png_writes_sibling_png_no_inline_image(self):
        src = WorkspaceStorageService(str(self.workspace)).create_diagram("flow", _activity_diagram())
        result = _run(server.diagram_render(str(src), format="png"))
        png_path = Path(_payload(result)["pngPath"])
        self.assertEqual(png_path.name, "flow.png")
        self.assertTrue(png_path.is_file())
        self.assertTrue(png_path.read_bytes().startswith(_PNG_MAGIC))
        # No inline image block: agent-loop clients don't render them cleanly.
        self.assertEqual(_image_blocks(result), [])

    def test_path_png_missing_returns_error_shape(self):
        result = _run(server.diagram_render(str(self.storage / "missing.gp.json"), format="png"))
        self.assertEqual(_payload(result)["error"]["code"], "diagram_not_found")

    def test_path_io_failure_returns_error_shape(self):
        with mock.patch.object(server._render_service, "render", side_effect=OSError("denied")):
            result = _run(server.diagram_render(str(self.storage / "flow.gp.json")))
        self.assertEqual(_payload(result)["error"]["code"], "render_failed")


class LabelFittingTests(SimpleTestCase):
    """Pure label-fitting helpers."""

    def test_wrap_packs_words_within_width(self):
        self.assertEqual(_wrap_text("one two three", 7), ["one two", "three"])

    def test_wrap_hard_breaks_overlong_word(self):
        self.assertEqual(_wrap_text("verylongtoken", 5), ["veryl", "ongto", "ken"])

    def test_short_label_keeps_base_font_single_line(self):
        self.assertEqual(_fit_text("Start", 200), (["Start"], FONT_SIZE))

    def test_tall_text_shrinks_font_without_losing_words(self):
        lines, font = _fit_text("alpha beta gamma delta epsilon", 70, 40)
        self.assertLess(font, FONT_SIZE)
        self.assertGreaterEqual(font, MIN_FONT_SIZE)
        # No words dropped when only wrapping/shrinking (no ellipsis needed).
        self.assertEqual(" ".join(lines).split(), "alpha beta gamma delta epsilon".split())

    def test_unfittable_text_ellipsizes_at_min_font(self):
        lines, font = _fit_text("x" * 40, 30, 12)
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith("\u2026"))
        self.assertEqual(font, MIN_FONT_SIZE)


class LabelOverflowRenderTests(SimpleTestCase):
    """Integration: long labels wrap to multiple <text> lines in the SVG; a short
    label stays on one."""

    def setUp(self):
        self.svc = DiagramRenderService()

    def test_long_label_wraps_to_multiple_lines(self):
        svg = self.svc.to_svg(_single_node_diagram("Approve the pending customer purchase order"))
        self.assertGreaterEqual(svg.count("<text"), 2)

    def test_short_label_renders_single_line(self):
        svg = self.svc.to_svg(_single_node_diagram("Go"))
        self.assertEqual(svg.count("<text"), 1)


class EdgeLabelTests(SimpleTestCase):
    """Edge labels get a solid background box so the connector doesn't run through
    the text, matching the canvas."""

    def setUp(self):
        self.svc = DiagramRenderService()

    def test_labeled_edge_draws_background_box(self):
        # The label box border colour (#e0e0e0) is used nowhere else in the render.
        svg = self.svc.to_svg(_activity_diagram())
        self.assertIn("#e0e0e0", svg)

    def test_unlabeled_edge_has_no_label_box(self):
        diagram = _activity_diagram()
        diagram["edges"][0].pop("label")
        svg = self.svc.to_svg(diagram)
        self.assertNotIn("#e0e0e0", svg)
