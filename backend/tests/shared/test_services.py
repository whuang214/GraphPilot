"""Tests for DiagramTypeService, SchemaRegistry, and WorkspaceStorageService."""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings

from services.shared.workspace_storage_service import (
    WorkspaceStorageService,
    DiagramNotFoundError,
    InvalidDiagramJSONError,
    UnsafePathError,
)
from services.shared.schema_registry import SchemaRegistry
from services.shared.diagram_type_service import DiagramTypeService


# ---------------------------------------------------------------------------
# DiagramTypeService
# ---------------------------------------------------------------------------


class DiagramTypeServiceTests(SimpleTestCase):
    def setUp(self):
        self.svc = DiagramTypeService()

    def test_list_supported_types_returns_all_three(self):
        types = self.svc.list_supported_types()
        self.assertEqual(types, ["activity_diagram", "use_case_diagram", "bdd_diagram"])

    def test_list_supported_types_returns_copy(self):
        types = self.svc.list_supported_types()
        types.append("extra")
        self.assertEqual(len(self.svc.list_supported_types()), 3)

    def test_list_valid_types_includes_custom(self):
        self.assertEqual(
            self.svc.list_valid_types(),
            ["activity_diagram", "use_case_diagram", "bdd_diagram", "custom"],
        )

    def test_is_supported_true(self):
        self.assertTrue(self.svc.is_supported("activity_diagram"))
        self.assertTrue(self.svc.is_supported("use_case_diagram"))
        self.assertTrue(self.svc.is_supported("bdd_diagram"))
        self.assertTrue(self.svc.is_supported("custom"))

    def test_is_supported_false(self):
        self.assertFalse(self.svc.is_supported("sequence_diagram"))
        self.assertFalse(self.svc.is_supported(""))
        self.assertFalse(self.svc.is_supported("ACTIVITY_DIAGRAM"))

    def test_get_type_profile_activity(self):
        profile = self.svc.get_type_profile("activity_diagram")
        self.assertEqual(profile.diagram_type, "activity_diagram")
        self.assertEqual(profile.node_type, "gpNode")
        self.assertIn("initialNode", profile.allowed_node_semantic_types)
        self.assertIn("opaqueAction", profile.allowed_node_semantic_types)
        self.assertIn("controlFlow", profile.allowed_edge_semantic_types)

    def test_get_type_profile_use_case(self):
        profile = self.svc.get_type_profile("use_case_diagram")
        self.assertEqual(profile.node_type, "gpNode")
        self.assertIn("actor", profile.allowed_node_semantic_types)

    def test_get_type_profile_bdd(self):
        profile = self.svc.get_type_profile("bdd_diagram")
        self.assertEqual(profile.node_type, "gpNode")
        self.assertEqual(profile.allowed_node_semantic_types, {"block", "note"})
        self.assertEqual(
            profile.allowed_edge_semantic_types,
            {"association", "composition", "generalization", "dependency", "commentLink"},
        )

    def test_get_type_profile_raises_for_unsupported(self):
        with self.assertRaises(ValueError):
            self.svc.get_type_profile("sequence_diagram")


# ---------------------------------------------------------------------------
# SchemaRegistry
# ---------------------------------------------------------------------------


class SchemaRegistryTests(SimpleTestCase):
    def setUp(self):
        # Use the real schema artifact so we test the actual content.
        self.real_schema_root = (
            Path(__file__).resolve().parent.parent.parent / "assets" / "schemas"
        )
        self.svc = SchemaRegistry(schema_root=self.real_schema_root)

    def test_get_diagram_schema_returns_dict(self):
        schema = self.svc.get_diagram_schema()
        self.assertIsInstance(schema, dict)

    def test_get_diagram_schema_id(self):
        self.assertEqual(self.svc.get_diagram_schema().get("$id"), "graphpilot.diagram.v1")

    def test_get_diagram_schema_required_fields(self):
        required = set(self.svc.get_diagram_schema().get("required", []))
        expected = {"schemaVersion", "kind", "diagramType", "id", "name", "metadata", "viewport", "nodes", "edges"}
        self.assertTrue(expected.issubset(required))

    def test_get_diagram_schema_with_valid_diagram_type(self):
        schema = self.svc.get_diagram_schema(diagram_type="activity_diagram")
        self.assertIsInstance(schema, dict)

    def test_get_diagram_schema_with_invalid_diagram_type_raises(self):
        with self.assertRaises(ValueError):
            self.svc.get_diagram_schema(diagram_type="unknown_type")

    def test_get_diagram_schema_cache_is_copy_isolated(self):
        first = self.svc.get_diagram_schema()
        second = self.svc.get_diagram_schema()
        self.assertEqual(first, second)
        self.assertIsNot(first, second)

    def test_get_diagram_schema_summary_keys(self):
        summary = self.svc.get_diagram_schema_summary()
        for key in ("schemaId", "schemaVersion", "requiredTopLevelFields", "supportedDiagramTypes", "nodeRequiredFields", "edgeRequiredFields"):
            self.assertIn(key, summary)

    def test_get_diagram_schema_summary_schema_id(self):
        self.assertEqual(self.svc.get_diagram_schema_summary()["schemaId"], "graphpilot.diagram.v1")

    def test_get_diagram_schema_summary_schema_version_from_const(self):
        self.assertEqual(self.svc.get_diagram_schema_summary()["schemaVersion"], "graphpilot.diagram.v1")

    def test_get_diagram_schema_summary_supported_types(self):
        types = set(self.svc.get_diagram_schema_summary()["supportedDiagramTypes"])
        self.assertEqual(types, {"activity_diagram", "use_case_diagram", "bdd_diagram"})

    def test_get_diagram_schema_summary_node_required_fields(self):
        self.assertIn("id", self.svc.get_diagram_schema_summary()["nodeRequiredFields"])
        self.assertIn("data", self.svc.get_diagram_schema_summary()["nodeRequiredFields"])

    def test_get_diagram_schema_summary_edge_required_fields(self):
        self.assertIn("source", self.svc.get_diagram_schema_summary()["edgeRequiredFields"])
        self.assertIn("target", self.svc.get_diagram_schema_summary()["edgeRequiredFields"])

    def test_get_diagram_schema_summary_with_valid_type(self):
        summary = self.svc.get_diagram_schema_summary(diagram_type="bdd_diagram")
        self.assertIsInstance(summary, dict)

    def test_get_diagram_schema_summary_with_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.svc.get_diagram_schema_summary(diagram_type="flow_diagram")

    def test_get_diagram_schema_summary_mutation_does_not_corrupt_cache(self):
        summary = self.svc.get_diagram_schema_summary()
        summary["requiredTopLevelFields"].append("INJECTED")
        summary["nodeRequiredFields"].append("INJECTED")
        # A fresh summary and the cached schema must be unaffected.
        self.assertNotIn("INJECTED", self.svc.get_diagram_schema_summary()["requiredTopLevelFields"])
        self.assertNotIn("INJECTED", self.svc.get_diagram_schema().get("required", []))

    def test_missing_schema_file_raises(self):
        svc = SchemaRegistry(schema_root=Path("/nonexistent/schemas"))
        with self.assertRaises(FileNotFoundError):
            svc.get_diagram_schema()

    def test_invalid_json_schema_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            schema_root = Path(tmp)
            (schema_root / "diagram.json").write_text("not valid json {{{", encoding="utf-8")
            svc = SchemaRegistry(schema_root=schema_root)
            with self.assertRaises(ValueError):
                svc.get_diagram_schema()


# ---------------------------------------------------------------------------
# WorkspaceStorageService — constructor
# ---------------------------------------------------------------------------


class WorkspaceStorageServiceConstructorTests(SimpleTestCase):
    def test_empty_workspace_raises(self):
        with self.assertRaises(ValueError):
            WorkspaceStorageService("")

    def test_whitespace_workspace_raises(self):
        with self.assertRaises(ValueError):
            WorkspaceStorageService("   ")

    def test_valid_workspace(self):
        with tempfile.TemporaryDirectory() as ws:
            svc = WorkspaceStorageService(ws)
            self.assertIsNotNone(svc)


# ---------------------------------------------------------------------------
# WorkspaceStorageService — path safety
# ---------------------------------------------------------------------------


class WorkspaceStorageServicePathSafetyTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.svc = WorkspaceStorageService(self._tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_safe_absolute_path_inside_workspace(self):
        sub = Path(self._tmp) / "sub" / "file.json"
        resolved = self.svc.resolve_safe_path(sub)
        self.assertTrue(resolved.is_relative_to(Path(self._tmp).resolve()))

    def test_safe_relative_path(self):
        resolved = self.svc.resolve_safe_path("sub/file.json")
        self.assertTrue(resolved.is_relative_to(Path(self._tmp).resolve()))

    def test_windows_extended_prefix_is_the_same_resolved_workspace_path(self):
        if os.name != "nt":
            self.skipTest("Windows extended paths are platform-specific.")
        target = (Path(self._tmp) / ".graphpilot" / "manifest.json").resolve()
        extended = Path("\\\\?\\" + str(target))
        with mock.patch.object(Path, "resolve", return_value=extended):
            resolved = self.svc.resolve_safe_path(target)
        self.assertEqual(resolved, target)
        self.assertTrue(resolved.is_relative_to(Path(self._tmp).resolve()))

    def test_traversal_relative_raises(self):
        with self.assertRaises(UnsafePathError):
            self.svc.resolve_safe_path("../../etc/passwd")

    def test_absolute_path_outside_workspace_raises(self):
        outside = Path(self._tmp).parent / "outside.json"
        with self.assertRaises(UnsafePathError):
            self.svc.resolve_safe_path(str(outside))

    def test_workspace_root_itself_is_safe(self):
        resolved = self.svc.resolve_safe_path(self._tmp)
        self.assertEqual(resolved, Path(self._tmp).resolve())


# ---------------------------------------------------------------------------
# WorkspaceStorageService — storage convention
# ---------------------------------------------------------------------------


class WorkspaceStorageServiceStorageTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.svc = WorkspaceStorageService(self._tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_storage_root_is_inside_workspace(self):
        root = self.svc.storage_root()
        self.assertTrue(root.is_relative_to(Path(self._tmp).resolve()))
        self.assertTrue(root.name == ".graphpilot")

    @override_settings(GRAPHPILOT_STORAGE_DIR="../outside")
    def test_storage_root_rejects_escaping_configuration(self):
        with self.assertRaises(UnsafePathError):
            self.svc.storage_root()

    def test_canonical_diagram_extension(self):
        self.assertEqual(self.svc.diagram_extension(), ".gp.json")

    def test_diagram_file_path_named_file_under_canonical_diagrams_root(self):
        path = self.svc.diagram_file_path("order-approval")
        self.assertEqual(path.name, "order-approval.gp.json")
        self.assertEqual(path.parent, self.svc.diagrams_root())

    def test_diagram_file_path_sanitizes_name(self):
        path = self.svc.diagram_file_path("Order Approval Flow!")
        self.assertEqual(path.name, "order-approval-flow.gp.json")

    def test_sanitize_name_falls_back_to_default(self):
        self.assertEqual(self.svc.sanitize_name("   "), "diagram")
        self.assertEqual(self.svc.sanitize_name("***"), "diagram")

    def test_sanitize_name_strips_trailing_extension(self):
        self.assertEqual(self.svc.sanitize_name("my-flow.gp.json"), "my-flow")

    def test_list_diagram_names_empty(self):
        self.assertEqual(self.svc.list_diagram_names(), [])

    def test_list_diagram_names_returns_sorted_stems(self):
        root = self.svc.diagrams_root()
        root.mkdir(parents=True)
        for name in ("b.gp.json", "a.gp.json", "c.gp.json"):
            (root / name).write_text("{}", encoding="utf-8")
        self.assertEqual(self.svc.list_diagram_names(), ["a", "b", "c"])

    def test_list_diagram_names_ignores_other_files(self):
        root = self.svc.diagrams_root()
        root.mkdir(parents=True)
        (root / "a.gp.json").write_text("{}", encoding="utf-8")
        (root / "a.svg").write_text("<svg/>", encoding="utf-8")
        (root / "notes.txt").write_text("x", encoding="utf-8")
        self.assertEqual(self.svc.list_diagram_names(), ["a"])

    def test_list_diagram_names_returns_empty_when_storage_is_a_file(self):
        # A non-directory where .graphpilot/ would be must not crash iterdir().
        root = self.svc.diagrams_root()
        root.parent.mkdir(parents=True, exist_ok=True)
        root.write_text("not a directory", encoding="utf-8")
        self.assertEqual(self.svc.list_diagram_names(), [])

    def test_unique_name_no_collision(self):
        self.assertEqual(self.svc.unique_name("Order Approval"), "order-approval")

    def test_unique_name_dedupes_on_collision(self):
        root = self.svc.diagrams_root()
        root.mkdir(parents=True)
        (root / "order-approval.gp.json").write_text("{}", encoding="utf-8")
        self.assertEqual(self.svc.unique_name("Order Approval"), "order-approval-2")
        (root / "order-approval-2.gp.json").write_text("{}", encoding="utf-8")
        self.assertEqual(self.svc.unique_name("order-approval"), "order-approval-3")


# ---------------------------------------------------------------------------
# WorkspaceStorageService — load
# ---------------------------------------------------------------------------


class WorkspaceStorageServiceLoadTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.svc = WorkspaceStorageService(self._tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _write_json(self, rel_path: str, data) -> Path:
        p = Path(self._tmp) / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f)
        return p

    def test_load_valid_diagram(self):
        diagram = {"schemaVersion": "graphpilot.diagram.v1", "kind": "diagram"}
        p = self._write_json(".graphpilot/order-approval.gp.json", diagram)
        result = self.svc.load_diagram(p)
        self.assertEqual(result["kind"], "diagram")

    def test_load_raises_for_missing_file(self):
        missing = Path(self._tmp) / ".graphpilot" / "missing.gp.json"
        with self.assertRaises(DiagramNotFoundError):
            self.svc.load_diagram(missing)

    def test_load_raises_for_invalid_json(self):
        p = Path(self._tmp) / ".graphpilot" / "broken.gp.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("not json {{", encoding="utf-8")
        with self.assertRaises(InvalidDiagramJSONError):
            self.svc.load_diagram(p)

    def test_load_raises_for_non_object_json(self):
        p = self._write_json(".graphpilot/list.gp.json", [1, 2, 3])
        with self.assertRaises(InvalidDiagramJSONError):
            self.svc.load_diagram(p)

    def test_load_rejects_non_standard_non_finite_json_numbers(self):
        p = Path(self._tmp) / ".graphpilot" / "non-finite.gp.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"zoom": NaN}', encoding="utf-8")
        with self.assertRaises(InvalidDiagramJSONError):
            self.svc.load_diagram(p)

    def test_load_raises_unsafe_path(self):
        outside = Path(self._tmp).parent / "evil.json"
        with self.assertRaises(UnsafePathError):
            self.svc.load_diagram(outside)


# ---------------------------------------------------------------------------
# WorkspaceStorageService — write helpers
# ---------------------------------------------------------------------------


class WorkspaceStorageServiceWriteTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.svc = WorkspaceStorageService(self._tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_ensure_storage_root_creates_directory(self):
        root = self.svc.ensure_storage_root()
        self.assertTrue(root.exists())
        self.assertEqual(root.name, ".graphpilot")

    def test_ensure_storage_root_is_idempotent(self):
        self.svc.ensure_storage_root()
        # Second call should not raise.
        self.svc.ensure_storage_root()

    def test_create_diagram_writes_named_file(self):
        diagram = {"schemaVersion": "graphpilot.diagram.v1", "kind": "diagram"}
        path = self.svc.create_diagram("Order Approval", diagram)
        self.assertTrue(path.exists())
        self.assertEqual(path.name, "order-approval.gp.json")
        with path.open(encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["kind"], "diagram")

    def test_create_diagram_dedupes_on_collision(self):
        self.svc.create_diagram("Order Approval", {"version": 1})
        second = self.svc.create_diagram("Order Approval", {"version": 2})
        self.assertEqual(second.name, "order-approval-2.gp.json")
        self.assertEqual(self.svc.list_diagram_names(), ["order-approval", "order-approval-2"])

    def test_create_diagram_can_overwrite_without_dedup(self):
        first = self.svc.create_diagram("Order Approval", {"version": 1})
        second = self.svc.create_diagram("Order Approval", {"version": 2}, deduplicate=False)
        self.assertEqual(first, second)
        self.assertEqual(self.svc.load_diagram(second)["version"], 2)

    def test_write_diagram_by_explicit_path(self):
        diagram = {"test": "value"}
        target = Path(self._tmp) / ".graphpilot" / "custom-login.gp.json"
        path = self.svc.write_diagram(target, diagram)
        self.assertTrue(path.exists())
        with path.open(encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["test"], "value")

    def test_write_diagram_is_atomic_round_trip(self):
        diagram = {"id": "round_trip", "schemaVersion": "graphpilot.diagram.v1"}
        target = self.svc.diagram_file_path("round-trip")
        self.svc.write_diagram(target, diagram)
        loaded = self.svc.load_diagram(target)
        self.assertEqual(loaded["id"], "round_trip")

    def test_write_diagram_overwrites_existing(self):
        target = self.svc.diagram_file_path("overwrite-me")
        self.svc.write_diagram(target, {"version": 1})
        self.svc.write_diagram(target, {"version": 2})
        loaded = self.svc.load_diagram(target)
        self.assertEqual(loaded["version"], 2)

    def test_write_diagram_raises_for_unsafe_path(self):
        outside = Path(self._tmp).parent / "evil.json"
        with self.assertRaises(UnsafePathError):
            self.svc.write_diagram(outside, {"id": "x"})

    def test_write_diagram_raises_for_non_dict(self):
        target = self.svc.diagram_file_path("bad")
        with self.assertRaises(TypeError):
            self.svc.write_diagram(target, ["not", "a", "dict"])

    def test_write_diagram_rejects_non_finite_numbers(self):
        target = self.svc.diagram_file_path("bad-number")
        with self.assertRaises(ValueError):
            self.svc.write_diagram(target, {"zoom": float("nan")})
        self.assertFalse(target.exists())
