"""Parallel edges into one node must not be drawn on top of one another.

The defect this guards was invisible to every payload-level test: the JSON was correct and
the picture showed one line where there were three, with their markers stacked at an
identical point. So these assertions are about **drawn geometry**, not fields.
"""

import json
from collections import Counter
from pathlib import Path

from django.test import SimpleTestCase

from services.diagrams.rendering.diagram_render_service import (
    CONTAINER_SEMANTIC_TYPES,
    DiagramRenderService,
    _fan_out_anchors,
    _resolve_boxes,
    _route_crossings,
)

BLUEPRINTS = Path(__file__).resolve().parents[3] / "assets" / "blueprints"
FIXTURES = json.loads(
    (Path(__file__).resolve().parents[2] / "edge_routing_fixtures.json").read_text(encoding="utf-8")
)


def _endpoints(service, diagram):
    boxes = _resolve_boxes(diagram["nodes"])
    fan_out = _fan_out_anchors(diagram["edges"], boxes)
    points = []
    for index, edge in enumerate(diagram["edges"]):
        route = service._edge_route(edge, boxes, diagram["edges"], fan_out.get(index))
        if route:
            points.append(tuple(round(v, 1) for v in route["points"][0]))
            points.append(tuple(round(v, 1) for v in route["points"][-1]))
    return points


class FanOutFixtureTests(SimpleTestCase):
    """Shared with the canvas: frontend/src/editor/lib/edgeRouting.test.ts reads these."""

    def test_shared_fan_out_fixtures(self):
        for case in FIXTURES["fanOutCases"]:
            with self.subTest(case=case["name"]):
                boxes = _resolve_boxes(case["nodes"])
                actual = _fan_out_anchors(case["edges"], boxes)
                self.assertEqual(
                    {str(index): value for index, value in sorted(actual.items())},
                    case["expected"],
                )

    def test_an_authored_anchor_is_never_overridden(self):
        case = next(c for c in FIXTURES["fanOutCases"] if c["name"] == "authored-anchor-is-never-overridden")
        boxes = _resolve_boxes(case["nodes"])

        overrides = _fan_out_anchors(case["edges"], boxes)

        self.assertNotIn(0, overrides)


class CorpusEndpointTests(SimpleTestCase):
    def test_no_committed_example_routes_an_edge_through_a_node(self):
        """An edge passing through a third node makes a claim the diagram does not.

        On a fork whose bar is narrower than the branch below it, the outer two branches
        were drawn straight through the middle one — so the picture said the middle branch
        fed the others. 26 of 512 edges did this before the faces were chosen
        obstacle-aware; this keeps it at zero for the committed set.
        """
        offenders = []
        for path in sorted(BLUEPRINTS.glob("*/examples/answers/*/output.gp.json")):
            diagram = json.loads(path.read_text(encoding="utf-8"))
            boxes = _resolve_boxes(diagram["nodes"])
            fan = _fan_out_anchors(diagram["edges"], boxes)
            service = DiagramRenderService()
            for index, edge in enumerate(diagram["edges"]):
                route = service._edge_route(edge, boxes, diagram["edges"], fan.get(index))
                blockers = [
                    box for node_id, box in boxes.items()
                    if node_id not in (edge["source"], edge["target"])
                    and service._semantic(box) not in CONTAINER_SEMANTIC_TYPES
                ]
                if _route_crossings(route["points"], blockers):
                    offenders.append(f"{path.parent.name}: {edge['source']} -> {edge['target']}")
        self.assertEqual(offenders, [])

    def test_no_two_edges_terminate_on_the_same_point_in_any_committed_example(self):
        """The whole answer-key library, measured through the real renderer.

        Before fan-out: 88 of 598 endpoints coincided across 24 of the 36 examples.
        """
        service = DiagramRenderService()
        offenders = []
        checked = 0
        for output in sorted(BLUEPRINTS.glob("*/examples/answers/*/output.gp.json")):
            diagram = json.loads(output.read_text(encoding="utf-8"))
            points = _endpoints(service, diagram)
            checked += len(points)
            collisions = sum(n for n in Counter(points).values() if n > 1)
            if collisions:
                offenders.append(f"{output.parent.name}: {collisions}")

        self.assertGreater(checked, 500, msg="corpus did not load")
        self.assertEqual(offenders, [])

    def test_every_committed_example_still_renders(self):
        service = DiagramRenderService()
        for output in sorted(BLUEPRINTS.glob("*/examples/answers/*/output.gp.json")):
            with self.subTest(example=output.parent.name):
                svg = service.to_svg(json.loads(output.read_text(encoding="utf-8")))
                self.assertIn("<svg", svg)


class EndLabelPlacementTests(SimpleTestCase):
    """A role or multiplicity belongs beside its endpoint, not inside its node."""

    def _diagram(self):
        return {
            "schemaVersion": "graphpilot.diagram.v1", "id": "d", "name": "ends",
            "diagramType": "bdd_diagram",
            "nodes": [
                {"id": "whole", "type": "gpNode", "position": {"x": 200, "y": 300},
                 "width": 200, "height": 60, "data": {"label": "Vehicle", "semanticType": "block"}},
                {"id": "part", "type": "gpNode", "position": {"x": 0, "y": 0},
                 "width": 200, "height": 60, "data": {"label": "Wheel", "semanticType": "block"}},
            ],
            "edges": [
                {"id": "r", "source": "part", "target": "whole",
                 "route": {"mode": "straight"},
                 "data": {"semanticType": "composition",
                          "sourceEnd": {"role": "wheels", "multiplicity": {"lower": 4, "upper": 4}},
                          "targetEnd": {"role": "vehicle", "multiplicity": {"lower": 1, "upper": 1}}}},
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "metadata": {"source": "test", "createdAt": "2026-01-01T00:00:00Z",
                         "updatedAt": "2026-01-01T00:00:00Z"},
        }

    def test_an_end_label_is_drawn_outside_the_node_it_describes(self):
        import re

        svg = DiagramRenderService().to_svg(self._diagram())
        texts = {
            match.group(3): (float(match.group(1)), float(match.group(2)))
            for match in re.finditer(r'<text x="([\d.\-]+)" y="([\d.\-]+)"[^>]*>([^<]+)</text>', svg)
        }
        self.assertIn("wheels 4", texts)
        self.assertIn("vehicle 1", texts)

        # "Wheel" occupies x 0..200, y 0..60; "Vehicle" occupies x 200..400, y 300..360.
        wheels_x, wheels_y = texts["wheels 4"]
        vehicle_x, vehicle_y = texts["vehicle 1"]
        self.assertFalse(
            0 <= wheels_x <= 200 and 0 <= wheels_y <= 60,
            msg=f"source end label at {(wheels_x, wheels_y)} is inside the Wheel block",
        )
        self.assertFalse(
            200 <= vehicle_x <= 400 and 300 <= vehicle_y <= 360,
            msg=f"target end label at {(vehicle_x, vehicle_y)} is inside the Vehicle block",
        )

    def test_no_end_label_lands_inside_any_node_across_the_corpus(self):
        import re

        service = DiagramRenderService()
        offenders = []
        for output in sorted(BLUEPRINTS.glob("*/examples/answers/*/output.gp.json")):
            diagram = json.loads(output.read_text(encoding="utf-8"))
            ends = {
                text
                for edge in diagram["edges"]
                for end in ("sourceEnd", "targetEnd")
                for text in [_end_text((edge.get("data") or {}).get(end) or {})]
                if text
            }
            if not ends:
                continue
            svg = service.to_svg(diagram)
            boxes = [
                (n["position"]["x"], n["position"]["y"],
                 n["position"]["x"] + (n.get("width") or 0), n["position"]["y"] + (n.get("height") or 0))
                for n in diagram["nodes"]
                if n["data"].get("semanticType") not in {"subject", "activityPartition"}
            ]
            for match in re.finditer(r'<text x="([\d.\-]+)" y="([\d.\-]+)"[^>]*>([^<]+)</text>', svg):
                if match.group(3) not in ends:
                    continue
                x, y = float(match.group(1)), float(match.group(2))
                for left, top, right, bottom in boxes:
                    if left < x < right and top < y < bottom:
                        offenders.append(f"{output.parent.name}: '{match.group(3)}' at {(x, y)}")
                        break
        self.assertEqual(offenders, [])


def _end_text(end):
    parts = []
    role = str(end.get("role") or "").strip()
    if role:
        parts.append(role)
    multiplicity = end.get("multiplicity")
    if isinstance(multiplicity, dict) and multiplicity.get("lower") is not None and multiplicity.get("upper") is not None:
        lower, upper = multiplicity["lower"], multiplicity["upper"]
        parts.append(str(lower) if lower == upper else f"{lower}..{upper}")
    return " ".join(parts)


class FanOutBoundaryTests(SimpleTestCase):
    def test_a_single_edge_is_left_at_its_natural_anchor(self):
        nodes = [
            {"id": "a", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 100, "height": 60,
             "data": {"label": "A", "semanticType": "block"}},
            {"id": "b", "type": "gpNode", "position": {"x": 0, "y": 200}, "width": 100, "height": 60,
             "data": {"label": "B", "semanticType": "block"}},
        ]
        edges = [{"id": "e", "source": "a", "target": "b", "data": {"semanticType": "association"}}]

        self.assertEqual(_fan_out_anchors(edges, _resolve_boxes(nodes)), {})

    def test_an_edge_with_manual_waypoints_is_left_alone(self):
        nodes = [
            {"id": "w", "type": "gpNode", "position": {"x": 100, "y": 200}, "width": 100, "height": 60,
             "data": {"label": "W", "semanticType": "block"}},
            {"id": "a", "type": "gpNode", "position": {"x": 0, "y": 0}, "width": 100, "height": 60,
             "data": {"label": "A", "semanticType": "block"}},
            {"id": "b", "type": "gpNode", "position": {"x": 200, "y": 0}, "width": 100, "height": 60,
             "data": {"label": "B", "semanticType": "block"}},
        ]
        edges = [
            {"id": "manual", "source": "a", "target": "w",
             "route": {"waypoints": [{"x": 20, "y": 120}]}, "data": {"semanticType": "association"}},
            {"id": "auto", "source": "b", "target": "w", "data": {"semanticType": "association"}},
        ]

        overrides = _fan_out_anchors(edges, _resolve_boxes(nodes))

        self.assertNotIn(0, overrides)

    def test_offsets_stay_inside_the_side(self):
        """Never 0 or 1: an endpoint exactly on a corner reads as belonging to neither side."""
        nodes = [{"id": "hub", "type": "gpNode", "position": {"x": 200, "y": 300}, "width": 200, "height": 60,
                  "data": {"label": "Hub", "semanticType": "block"}}]
        edges = []
        for index in range(6):
            nodes.append({
                "id": f"n{index}", "type": "gpNode", "position": {"x": index * 120, "y": 0},
                "width": 100, "height": 60, "data": {"label": f"N{index}", "semanticType": "block"},
            })
            edges.append({"id": f"e{index}", "source": f"n{index}", "target": "hub",
                          "data": {"semanticType": "association"}})

        overrides = _fan_out_anchors(edges, _resolve_boxes(nodes))

        offsets = [anchor["offset"] for value in overrides.values() for anchor in value.values()]
        self.assertTrue(offsets)
        for offset in offsets:
            self.assertGreater(offset, 0.0)
            self.assertLess(offset, 1.0)
