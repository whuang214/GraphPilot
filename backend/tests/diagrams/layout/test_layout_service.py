import importlib.util
import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import (
    DiagramLayoutService,
    LayoutEdge,
    LayoutEngineUnavailableError,
    LayoutError,
    LayoutInputNode,
    PyGraphvizLayoutEngine,
    node_size,
)


BLUEPRINTS_DIR = Path(__file__).resolve().parents[3] / "assets" / "blueprints"


def _example_paths():
    return (
        sorted(BLUEPRINTS_DIR.glob("*/examples/answers/*/output.gp.json"))
    )


def _to_inputs(diagram):
    nodes = [
        LayoutInputNode(
            id=node["id"],
            semantic_type=(node.get("data") or {}).get("semanticType", ""),
            label=(node.get("data") or {}).get("label", ""),
            parent_id=node.get("parentId"),
        )
        for node in diagram["nodes"]
    ]
    edges = [LayoutEdge(edge["source"], edge["target"]) for edge in diagram["edges"]]
    return nodes, edges


def _overlap(left, right):
    return (
        left.x < right.x + right.width
        and left.x + left.width > right.x
        and left.y < right.y + right.height
        and left.y + left.height > right.y
    )


class NodeSizeTests(SimpleTestCase):
    def test_short_label_uses_base_size(self):
        self.assertEqual(node_size("opaqueAction", "Go"), (160.0, 60.0))

    def test_long_label_widens(self):
        width, _ = node_size("opaqueAction", "A very long action label that should widen the box")
        self.assertGreater(width, 160.0)

    def test_width_is_capped(self):
        width, _ = node_size("opaqueAction", "x" * 500)
        self.assertLessEqual(width, 320.0)

    def test_unknown_semantic_type_uses_fallback(self):
        self.assertEqual(node_size("mystery", ""), (150.0, 60.0))

    def test_expansion_node_uses_boundary_pin_size(self):
        self.assertEqual(node_size("expansionNode", "items"), (73.5, 24.0))


class SoleEngineTests(SimpleTestCase):
    def test_removed_dependency_is_not_installed(self):
        self.assertIsNone(importlib.util.find_spec("grandalf"))

    def test_alternate_engine_injection_is_rejected(self):
        with self.assertRaises(TypeError):
            DiagramLayoutService(engine=mock.Mock())

    def test_default_is_pygraphviz_and_availability_is_checked_once(self):
        service = DiagramLayoutService()
        with mock.patch.object(PyGraphvizLayoutEngine, "available", return_value=True) as available:
            self.assertIsInstance(service.select_engine(), PyGraphvizLayoutEngine)
            self.assertIsInstance(service.select_engine(), PyGraphvizLayoutEngine)
        available.assert_called_once_with()

    def test_unavailable_engine_has_exact_nonretryable_operation_identity(self):
        engine = PyGraphvizLayoutEngine()
        with mock.patch.object(engine, "available", return_value=False):
            with self.assertRaises(LayoutEngineUnavailableError) as caught:
                DiagramLayoutService(engine=engine).layout("activity_diagram", [], [])
        self.assertEqual(caught.exception.code, "layout_engine_unavailable")
        self.assertEqual(
            caught.exception.details,
            {"engine": "pygraphviz-dot", "stage": "availability"},
        )

    def test_native_failure_surfaces_without_secondary_engine(self):
        engine = PyGraphvizLayoutEngine()
        service = DiagramLayoutService(engine=engine)
        with mock.patch.object(engine, "available", return_value=True), mock.patch.object(
            engine,
            "layout",
            side_effect=LayoutError("PyGraphviz native layout failed.", stage="native_layout"),
        ) as layout:
            with self.assertRaises(LayoutError) as caught:
                service.layout(
                    "activity_diagram",
                    [LayoutInputNode("node", width=100, height=50)],
                    [],
                )
        layout.assert_called_once()
        self.assertEqual(caught.exception.code, "layout_failed")
        self.assertEqual(
            caught.exception.details,
            {"engine": "pygraphviz-dot", "stage": "native_layout"},
        )


class DiagramLayoutServiceTests(SimpleTestCase):
    def setUp(self):
        self.engine = PyGraphvizLayoutEngine()
        self.assertTrue(self.engine.available())
        self.service = DiagramLayoutService(engine=self.engine)

    def test_all_curated_answers_lay_out_with_sole_engine(self):
        paths = _example_paths()
        self.assertEqual(len(paths), 36)
        for path in paths:
            with self.subTest(path=path.as_posix()):
                diagram = json.loads(path.read_text(encoding="utf-8"))
                nodes, edges = _to_inputs(diagram)
                result = self.service.layout(diagram["diagramType"], nodes, edges)
                self.assertEqual(result.engine, "pygraphviz-dot")
                self.assertEqual(len(result.nodes), len(nodes))
                self.assertTrue(all(node.width > 0 and node.height > 0 for node in result.nodes))

    def test_top_level_siblings_do_not_overlap(self):
        for path in _example_paths():
            diagram = json.loads(path.read_text(encoding="utf-8"))
            nodes, edges = _to_inputs(diagram)
            top = [
                node
                for node in self.service.layout(diagram["diagramType"], nodes, edges).nodes
                if node.parent_id is None
            ]
            for index, left in enumerate(top):
                for right in top[index + 1 :]:
                    with self.subTest(path=path.as_posix(), left=left.id, right=right.id):
                        self.assertFalse(_overlap(left, right))

    def test_activity_flows_top_to_bottom(self):
        nodes = [
            LayoutInputNode("start", "initialNode", "Start"),
            LayoutInputNode("action", "opaqueAction", "Do"),
            LayoutInputNode("end", "activityFinalNode", "End"),
        ]
        positions = self.service.layout(
            "activity_diagram",
            nodes,
            [LayoutEdge("start", "action"), LayoutEdge("action", "end")],
        ).positions
        self.assertLess(positions["start"].y, positions["action"].y)
        self.assertLess(positions["action"].y, positions["end"].y)

    def test_use_case_flows_left_to_right(self):
        nodes = [
            LayoutInputNode("actor", "actor", "User"),
            LayoutInputNode("use-case", "useCase", "Do Thing"),
        ]
        positions = self.service.layout(
            "use_case_diagram",
            nodes,
            [LayoutEdge("actor", "use-case")],
        ).positions
        self.assertLess(positions["actor"].x, positions["use-case"].x)
        self.assertGreaterEqual(
            positions["use-case"].x - (positions["actor"].x + positions["actor"].width),
            95.0,
        )

    def test_containment_parent_encloses_relative_children(self):
        nodes = [
            LayoutInputNode("subject", "subject", "System"),
            LayoutInputNode("first", "useCase", "One", parent_id="subject"),
            LayoutInputNode("second", "useCase", "Two", parent_id="subject"),
        ]
        positions = self.service.layout(
            "use_case_diagram",
            nodes,
            [LayoutEdge("first", "second")],
        ).positions
        parent = positions["subject"]
        for node_id in ("first", "second"):
            child = positions[node_id]
            self.assertEqual(child.parent_id, "subject")
            self.assertGreaterEqual(child.x, 0)
            self.assertGreaterEqual(child.y, 0)
            self.assertLessEqual(child.x + child.width, parent.width + 0.01)
            self.assertLessEqual(child.y + child.height, parent.height + 0.01)

    def test_repeatable_empty_result(self):
        first = self.service.layout("activity_diagram", [], [])
        second = self.service.layout("activity_diagram", [], [])
        self.assertEqual(first.nodes, [])
        self.assertEqual(first.nodes, second.nodes)
        self.assertEqual(first.engine, "pygraphviz-dot")
