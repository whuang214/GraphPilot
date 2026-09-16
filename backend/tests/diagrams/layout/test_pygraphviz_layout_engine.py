import copy
import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from services.diagrams.rendering.diagram_render_service import DiagramRenderService
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.diagrams.layout.diagram_layout_service import (
    DiagramLayoutService,
    LayoutEdge,
    LayoutEngineUnavailableError,
    LayoutError,
    LayoutInputNode,
    PyGraphvizLayoutEngine,
)


BLUEPRINTS = Path(__file__).resolve().parents[3] / "assets" / "blueprints"


def _paths():
    return sorted(BLUEPRINTS.glob("*/examples/answers/*/output.gp.json"))


def _inputs(diagram):
    nodes = [
        LayoutInputNode(
            id=node["id"],
            semantic_type=(node.get("data") or {}).get("semanticType", ""),
            label=(node.get("data") or {}).get("label", ""),
            width=node.get("width"),
            height=node.get("height"),
            parent_id=node.get("parentId"),
        )
        for node in diagram["nodes"]
    ]
    edges = [LayoutEdge(edge["source"], edge["target"]) for edge in diagram["edges"]]
    return nodes, edges


def _overlap(a, b):
    return (
        a.x < b.x + b.width
        and a.x + a.width > b.x
        and a.y < b.y + b.height
        and a.y + a.height > b.y
    )


class _Attr(dict):
    pass


class _FakeNode:
    def __init__(self):
        self.attr = _Attr()


class _FakeAGraph:
    active = 0
    max_active = 0
    closes = 0
    edge_count = 0
    tokens = []
    fail_layout = False
    gate = threading.Lock()

    @classmethod
    def reset(cls):
        cls.active = 0
        cls.max_active = 0
        cls.closes = 0
        cls.edge_count = 0
        cls.tokens = []
        cls.fail_layout = False

    def __init__(self, strict, directed, name="G"):
        self.strict = strict
        self.directed = directed
        self.name = name
        self.graph_attr = _Attr()
        self.node_attr = _Attr()
        self.nodes = {}
        with self.gate:
            type(self).active += 1
            type(self).max_active = max(type(self).max_active, type(self).active)

    def add_node(self, token, **attrs):
        type(self).tokens.append(token)
        node = self.nodes.setdefault(token, _FakeNode())
        node.attr.update(attrs)

    def add_edge(self, source, target, key):
        type(self).edge_count += 1

    def layout(self, prog):
        if type(self).fail_layout:
            raise RuntimeError("native failure")
        time.sleep(0.002)
        self.graph_attr["bb"] = f"0,0,300,{max(100, len(self.nodes) * 100)}"
        for index, node in enumerate(self.nodes.values()):
            node.attr["pos"] = f"{100 + index * 10},{50 + index * 100}"

    def get_node(self, token):
        return self.nodes[token]

    def close(self):
        type(self).closes += 1
        with self.gate:
            type(self).active -= 1


class _Observer:
    def __init__(self):
        self.events = []

    def on_stage(self, event):
        self.events.append(event)

    def on_provider_call(self, event):
        pass

    def on_candidate(self, event):
        pass

    def on_result(self, event):
        pass


class PyGraphvizEngineUnitTests(SimpleTestCase):
    def setUp(self):
        _FakeAGraph.reset()
        self.fake_module = SimpleNamespace(__version__="2.0", AGraph=_FakeAGraph)

    def _fake_engine(self, **kwargs):
        engine = PyGraphvizLayoutEngine(**kwargs)
        return mock.patch.object(engine, "_module", return_value=self.fake_module), mock.patch.object(
            engine, "_runtime_identity", return_value=("windows-x64", None)
        ), engine

    def test_exact_coordinate_flip_uses_bounding_box_and_normalizes(self):
        positions = PyGraphvizLayoutEngine._convert(
            [
                {"id": "a", "token": "n000", "width": 10.0, "height": 20.0},
                {"id": "b", "token": "n001", "width": 20.0, "height": 10.0},
            ],
            {"n000": "20,80", "n001": "60,40"},
            "10,20,110,120",
        )
        self.assertEqual(positions, {"a": (0.0, 0.0), "b": (35.0, 45.0)})

    def test_malformed_missing_nonfinite_and_inverted_native_geometry_fails(self):
        nodes = [{"id": "a", "token": "n000", "width": 10.0, "height": 20.0}]
        for raw, box in (
            ({"n000": "20,80"}, None),
            ({"n000": "20,80"}, "bad"),
            ({}, "0,0,100,100"),
            ({"n000": "bad"}, "0,0,100,100"),
            ({"n000": "nan,20"}, "0,0,100,100"),
            ({"n000": "20,20"}, "100,0,0,100"),
        ):
            with self.subTest(raw=raw, box=box), self.assertRaises(LayoutError):
                PyGraphvizLayoutEngine._convert(nodes, raw, box)

    def test_safe_tokens_non_strict_directed_graph_and_parallel_edges(self):
        patch_module, patch_runtime, engine = self._fake_engine()
        nodes = [
            LayoutInputNode("id with spaces", width=100, height=50),
            LayoutInputNode("punctuation:[]{}", width=100, height=50),
        ]
        edges = [
            LayoutEdge("id with spaces", "punctuation:[]{}"),
            LayoutEdge("id with spaces", "punctuation:[]{}"),
        ]
        with patch_module, patch_runtime:
            positions = engine.layout(nodes, edges, "TB", 64, 72)
        self.assertEqual(set(positions), {node.id for node in nodes})
        self.assertEqual(_FakeAGraph.edge_count, 2)
        self.assertEqual(_FakeAGraph.tokens, ["n000", "n001"])
        self.assertEqual(_FakeAGraph.closes, 1)

    def test_process_lock_covers_creation_through_close_for_ten_threads(self):
        patch_module, patch_runtime, engine = self._fake_engine()
        nodes = [LayoutInputNode("a", width=100, height=50)]
        with patch_module, patch_runtime, ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(lambda _: engine.layout(nodes, [], "TB", 64, 72), range(30)))
        self.assertTrue(all(result == {"a": (0.0, 0.0)} for result in results))
        self.assertEqual(_FakeAGraph.max_active, 1)
        self.assertEqual(_FakeAGraph.closes, 30)

    def test_native_error_always_closes_graph(self):
        patch_module, patch_runtime, engine = self._fake_engine()
        _FakeAGraph.fail_layout = True
        with patch_module, patch_runtime, self.assertRaises(LayoutError):
            engine.layout([LayoutInputNode("a", width=100, height=50)], [], "TB", 64, 72)
        self.assertEqual(_FakeAGraph.active, 0)
        self.assertEqual(_FakeAGraph.closes, 1)

    def test_input_validation_is_outside_native_lifecycle_and_256_is_boundary(self):
        engine = PyGraphvizLayoutEngine()
        cases = (
            ([LayoutInputNode("a", width=0, height=10)], [], "TB"),
            ([LayoutInputNode("a"), LayoutInputNode("a")], [], "TB"),
            ([LayoutInputNode("a")], [LayoutEdge("a", "missing")], "TB"),
            ([LayoutInputNode(str(i)) for i in range(257)], [], "TB"),
        )
        with mock.patch.object(engine, "_module") as module:
            for nodes, edges, direction in cases:
                with self.subTest(count=len(nodes)), self.assertRaises(LayoutError):
                    engine.layout(nodes, edges, direction, 64, 72)
            module.assert_not_called()

    def test_explicit_engine_failure_is_called_once_without_fallback(self):
        engine = PyGraphvizLayoutEngine()
        service = DiagramLayoutService(engine=engine)
        with mock.patch.object(engine, "available", return_value=True), mock.patch.object(
            engine,
            "layout",
            side_effect=LayoutError("failed"),
        ) as layout, self.assertRaises(LayoutError):
            service.layout(
                "activity_diagram",
                [LayoutInputNode("a", width=100, height=50)],
                [],
            )
        layout.assert_called_once()

    def test_trace_identity_is_bounded_and_not_canonical(self):
        traces = []
        patch_module, patch_runtime, engine = self._fake_engine(trace_sink=traces.append)
        nodes = [LayoutInputNode("a", width=100, height=50)]
        with patch_module, patch_runtime:
            engine.layout(nodes, [], "TB", 64, 72)
        self.assertEqual(len(traces), 1)
        self.assertEqual(
            set(traces[0].to_dict()),
            {
                "engine",
                "pygraphvizVersion",
                "runtimePlatform",
                "emulation",
                "layoutConfigurationVersion",
                "nodeCount",
                "edgeCount",
                "durationMs",
            },
        )
        self.assertEqual(traces[0].layout_configuration_version, "graphpilot.generation.layout.activity.v1")

    def test_runtime_platform_matrix_and_arm64_policy(self):
        cases = (
            ("win32", "AMD64", {}, ("windows-x64", None)),
            ("win32", "AMD64", {"PROCESSOR_ARCHITEW6432": "ARM64"}, ("windows-x64", "windows-x64-on-arm64")),
            ("darwin", "x86_64", {}, ("macos-x64", None)),
            ("darwin", "arm64", {}, ("macos-arm64", None)),
            ("linux", "x86_64", {}, ("linux-x64", None)),
            ("linux", "aarch64", {}, ("linux-aarch64", None)),
        )
        for system, machine, env, expected in cases:
            with self.subTest(expected=expected), mock.patch(
                "services.diagrams.layout.diagram_layout_service.sys.platform", system
            ), mock.patch(
                "services.diagrams.layout.diagram_layout_service.platform.machine", return_value=machine
            ), mock.patch.dict(
                "services.diagrams.layout.diagram_layout_service.os.environ", env, clear=True
            ):
                self.assertEqual(PyGraphvizLayoutEngine._runtime_identity(), expected)
        with mock.patch("services.diagrams.layout.diagram_layout_service.sys.platform", "win32"), mock.patch(
            "services.diagrams.layout.diagram_layout_service.platform.machine", return_value="ARM64"
        ), self.assertRaises(LayoutEngineUnavailableError):
            PyGraphvizLayoutEngine._runtime_identity()

    def test_exact_version_and_plugin_probe(self):
        engine = PyGraphvizLayoutEngine()
        self.assertTrue(engine.available())
        import pygraphviz

        self.assertEqual(pygraphviz.__version__, "2.0")
        with mock.patch.dict("sys.modules", {"pygraphviz": SimpleNamespace(__version__="1.99")}):
            with self.assertRaises(LayoutEngineUnavailableError):
                engine._module()


class PyGraphvizParityTests(SimpleTestCase):
    def setUp(self):
        self.engine = PyGraphvizLayoutEngine()
        if not self.engine.available():
            self.skipTest("Pinned PyGraphviz 2.0 wheel/plugin is unavailable")
        self.layout = DiagramLayoutService(engine=self.engine)

    def test_repeatability_direction_gaps_and_horizontal_fork_join(self):
        nodes = [
            LayoutInputNode("fork", "forkNode", "Fork"),
            LayoutInputNode("left", "opaqueAction", "Left"),
            LayoutInputNode("right", "opaqueAction", "Right"),
            LayoutInputNode("join", "joinNode", "Join"),
        ]
        edges = [
            LayoutEdge("fork", "left"),
            LayoutEdge("fork", "right"),
            LayoutEdge("left", "join"),
            LayoutEdge("right", "join"),
        ]
        snapshots = []
        for _ in range(3):
            result = self.layout.layout("activity_diagram", copy.deepcopy(nodes), edges)
            snapshots.append([(node.id, node.x, node.y, node.width, node.height) for node in result.nodes])
        self.assertEqual(snapshots[0], snapshots[1])
        self.assertEqual(snapshots[1], snapshots[2])
        pos = {item[0]: item for item in snapshots[0]}
        self.assertLess(pos["fork"][2], pos["left"][2])
        self.assertLess(pos["left"][2], pos["join"][2])
        left, right = sorted((pos["left"], pos["right"]), key=lambda item: item[1])
        self.assertGreaterEqual(right[1] - (left[1] + left[3]), 63.0)
        self.assertGreater(pos["fork"][3], pos["fork"][4])
        self.assertGreater(pos["join"][3], pos["join"][4])

    def test_256_node_boundary_and_ten_thread_real_stress(self):
        nodes = [LayoutInputNode(f"node-{index}", width=80, height=40) for index in range(256)]
        edges = [LayoutEdge(f"node-{index}", f"node-{index + 1}") for index in range(255)]
        positions = self.engine.layout(nodes, edges, "TB", 64, 72)
        self.assertEqual(len(positions), 256)
        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(
                pool.map(
                    lambda _: self.engine.layout(
                        [LayoutInputNode("a", width=80, height=40), LayoutInputNode("b", width=80, height=40)],
                        [LayoutEdge("a", "b")],
                        "TB",
                        64,
                        72,
                    ),
                    range(20),
                )
            )
        self.assertTrue(all(result == results[0] for result in results))

    def test_all_curated_diagrams_layout_validate_render_and_preserve_containment(self):
        paths = _paths()
        self.assertEqual(len(paths), 36)
        validation = DiagramValidationService()
        render = DiagramRenderService()
        for path in paths:
            with self.subTest(path=path.as_posix()):
                original = json.loads(path.read_text(encoding="utf-8"))
                diagram = copy.deepcopy(original)
                nodes, edges = _inputs(diagram)
                result = self.layout.layout(diagram["diagramType"], nodes, edges)
                self.assertEqual(result.engine, "pygraphviz-dot")
                self.assertEqual(len(result.nodes), len(diagram["nodes"]))
                top = [node for node in result.nodes if node.parent_id is None]
                for index, left in enumerate(top):
                    for right in top[index + 1 :]:
                        self.assertFalse(_overlap(left, right))
                by_id = result.positions
                for node in diagram["nodes"]:
                    positioned = by_id[node["id"]]
                    node["position"] = {"x": positioned.x, "y": positioned.y}
                    node["width"] = positioned.width
                    node["height"] = positioned.height
                    self.assertTrue(all(math.isfinite(value) for value in (positioned.x, positioned.y)))
                    if positioned.parent_id:
                        parent = by_id[positioned.parent_id]
                        self.assertGreaterEqual(positioned.x, 0)
                        self.assertGreaterEqual(positioned.y, 0)
                        self.assertLessEqual(positioned.x + positioned.width, parent.width + 0.01)
                        self.assertLessEqual(positioned.y + positioned.height, parent.height + 0.01)
                checked = validation.validate(diagram)
                self.assertTrue(checked.valid, msg=[issue.message for issue in checked.issues])
                svg = render.to_svg(diagram)
                self.assertIn("<svg", svg)
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)
