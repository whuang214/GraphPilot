"""Tests for the DiagramPersistenceService validate-then-overwrite workflow."""

import json
import shutil
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.diagrams.persistence.diagram_persistence_service import (
    CreateOutcome,
    DiagramPersistenceService,
    DiagramValidationError,
)
from services.shared.workspace_storage_service import DiagramNotFoundError


def _valid_diagram():
    return {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": "activity_diagram",
        "id": "diagram_order_review",
        "name": "Order Review",
        "metadata": {"source": "ui", "blueprintKey": "activity_diagram.default"},
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": [
            {
                "id": "node_start",
                "type": "gpNode",
                "position": {"x": 80, "y": 80},
                "width": 140,
                "height": 60,
                "data": {"label": "Start", "semanticType": "initialNode"},
            },
            {
                "id": "node_review",
                "type": "gpNode",
                "position": {"x": 280, "y": 80},
                "width": 180,
                "height": 60,
                "data": {"label": "Review Order", "semanticType": "opaqueAction"},
            },
        ],
        "edges": [
            {
                "id": "edge_start_to_review",
                "type": "default",
                "source": "node_start",
                "target": "node_review",
                "label": "Next",
                "data": {"semanticType": "controlFlow"},
            }
        ],
    }


class DiagramPersistenceServiceTests(SimpleTestCase):
    def setUp(self):
        self._workspace = tempfile.mkdtemp()
        self._storage_dir = Path(self._workspace) / ".graphpilot"
        self._storage_dir.mkdir(parents=True)
        self._diagram_dir = self._storage_dir / "diagrams"
        self._diagram_path = self._storage_dir / "order-approval.gp.json"
        self.svc = DiagramPersistenceService()

    def tearDown(self):
        shutil.rmtree(self._workspace, ignore_errors=True)

    def test_valid_diagram_is_saved(self):
        self._diagram_path.write_text(json.dumps({"stale": True}), encoding="utf-8")
        outcome = self.svc.save(str(self._diagram_path), _valid_diagram())
        self.assertTrue(outcome.saved)
        self.assertEqual(outcome.resolved_path, self._diagram_path.resolve())
        self.assertTrue(outcome.validation.valid)
        on_disk = json.loads(self._diagram_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, _valid_diagram())

    def test_valid_save_requires_an_existing_file(self):
        with self.assertRaises(DiagramNotFoundError):
            self.svc.save(str(self._diagram_path), _valid_diagram())
        self.assertFalse(self._diagram_path.exists())

    def test_overwrites_existing_file(self):
        self._diagram_path.write_text(json.dumps({"stale": True}), encoding="utf-8")
        outcome = self.svc.save(str(self._diagram_path), _valid_diagram())
        self.assertTrue(outcome.saved)
        on_disk = json.loads(self._diagram_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, _valid_diagram())

    def test_invalid_diagram_is_not_saved(self):
        diagram = _valid_diagram()
        diagram["nodes"] = []  # structural "no_nodes" blocking error
        outcome = self.svc.save(str(self._diagram_path), diagram)
        self.assertFalse(outcome.saved)
        self.assertFalse(outcome.validation.valid)
        self.assertFalse(self._diagram_path.exists())

    def test_invalid_save_leaves_existing_file_untouched(self):
        original = json.dumps(_valid_diagram())
        self._diagram_path.write_text(original, encoding="utf-8")
        diagram = _valid_diagram()
        diagram["nodes"] = []
        outcome = self.svc.save(str(self._diagram_path), diagram)
        self.assertFalse(outcome.saved)
        self.assertEqual(self._diagram_path.read_text(encoding="utf-8"), original)

    def test_blueprint_drift_warning_still_saves(self):
        self._diagram_path.write_text(json.dumps({"stale": True}), encoding="utf-8")
        diagram = _valid_diagram()
        diagram["metadata"]["blueprintKey"] = "bdd_diagram.default"  # mismatch -> warning only
        outcome = self.svc.save(str(self._diagram_path), diagram)
        self.assertTrue(outcome.saved)
        self.assertTrue(outcome.validation.valid)

    def test_a_diagram_outside_a_storage_folder_saves_where_it_lives(self):
        """The `.graphpilot` requirement refused every example the product ships. A loose
        file's own folder is its root, so it saves back in place."""
        stray = Path(self._workspace) / "loose.gp.json"
        stray.write_text(json.dumps({"stale": True}), encoding="utf-8")
        outcome = self.svc.save(str(stray), _valid_diagram())
        self.assertTrue(outcome.saved)
        self.assertEqual(json.loads(stray.read_text(encoding="utf-8")), _valid_diagram())

    def test_non_dict_diagram_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.svc.save(str(self._diagram_path), [1, 2, 3])

    # ------------------------------------------------------------------
    # create(): the validated new-diagram path
    # ------------------------------------------------------------------

    def test_create_writes_valid_new_diagram(self):
        outcome = self.svc.create(self._workspace, "Order Review", _valid_diagram())
        self.assertIsInstance(outcome, CreateOutcome)
        self.assertTrue(outcome.resolved_path.is_file())
        self.assertEqual(outcome.resolved_path, (self._diagram_dir / "order-review.gp.json").resolve())
        self.assertTrue(outcome.validation.valid)
        on_disk = json.loads(outcome.resolved_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, _valid_diagram())

    def test_create_dedupes_on_name_collision(self):
        first = self.svc.create(self._workspace, "dup", _valid_diagram())
        second = self.svc.create(self._workspace, "dup", _valid_diagram())
        self.assertEqual(first.resolved_path.name, "dup.gp.json")
        self.assertEqual(second.resolved_path.name, "dup-2.gp.json")

    def test_create_exact_uses_canonical_name_and_never_deduplicates_or_overwrites(self):
        first = self.svc.create_exact(self._workspace, "exact-name", _valid_diagram())
        self.assertEqual(
            first.resolved_path,
            (self._diagram_dir / "exact-name.gp.json").resolve(),
        )

        with self.assertRaises(FileExistsError):
            self.svc.create_exact(self._workspace, "exact-name", {**_valid_diagram(), "name": "new"})

        on_disk = json.loads(first.resolved_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, _valid_diagram())
        self.assertFalse((self._diagram_dir / "exact-name-2.gp.json").exists())

    def test_create_exact_rejects_noncanonical_name_and_invalid_diagram(self):
        with self.assertRaises(ValueError):
            self.svc.create_exact(self._workspace, "Not Exact", _valid_diagram())
        invalid = _valid_diagram()
        invalid["nodes"] = []
        with self.assertRaises(DiagramValidationError):
            self.svc.create_exact(self._workspace, "invalid", invalid)
        self.assertFalse((self._diagram_dir / "invalid.gp.json").exists())

    def test_create_can_overwrite_without_dedup(self):
        first = self.svc.create(self._workspace, "same", _valid_diagram())
        second = self.svc.create(self._workspace, "same", _valid_diagram(), deduplicate=False)
        self.assertEqual(first.resolved_path, second.resolved_path)

    def test_create_invalid_raises_and_writes_nothing(self):
        diagram = _valid_diagram()
        diagram["nodes"] = []  # structural "no_nodes" blocking error
        with self.assertRaises(DiagramValidationError) as ctx:
            self.svc.create(self._workspace, "bad", diagram)
        # The raised error carries the failing ValidationResult...
        self.assertFalse(ctx.exception.validation.valid)
        # ...and nothing was written.
        self.assertEqual(list(self._diagram_dir.glob("*.gp.json")), [])

    def test_create_blueprint_drift_warning_still_writes(self):
        diagram = _valid_diagram()
        diagram["metadata"]["blueprintKey"] = "bdd_diagram.default"  # mismatch -> warning only
        outcome = self.svc.create(self._workspace, "drift", diagram)
        self.assertTrue(outcome.resolved_path.is_file())
        self.assertTrue(outcome.validation.valid)

    def test_create_non_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.svc.create(self._workspace, "bad", [1, 2, 3])
