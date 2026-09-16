import json
import os
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from services.shared.workspace_storage_service import (
    ArtifactNotFoundError,
    ArtifactTooLargeError,
    InvalidJSONFileError,
    UnsafePathError,
    WorkspaceStorageService,
)


@override_settings(GRAPHPILOT_STORAGE_DIR=".graphpilot")
class WorkspaceStorageServiceTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name)
        self.storage = WorkspaceStorageService(self.workspace)

    def tearDown(self):
        self._tmp.cleanup()

    def test_canonical_roots_and_paths(self):
        self.assertEqual(self.storage.storage_root(), self.workspace / ".graphpilot")
        self.assertEqual(self.storage.diagrams_root(), self.workspace / ".graphpilot" / "diagrams")
        self.assertEqual(
            self.storage.drafts_root(),
            self.workspace / ".graphpilot" / "drafts",
        )
        self.assertEqual(
            self.storage.diagram_file_path("Order Approval"),
            self.workspace / ".graphpilot" / "diagrams" / "order-approval.gp.json",
        )

    def test_new_diagrams_are_created_and_listed_only_in_canonical_directory(self):
        legacy = self.storage.storage_root() / "legacy.gp.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(json.dumps({"id": "legacy"}), encoding="utf-8")

        created = self.storage.create_diagram("Current", {"id": "current"})

        self.assertEqual(created.parent, self.storage.diagrams_root())
        self.assertEqual(self.storage.list_diagram_names(), ["current"])
        self.assertEqual(self.storage.load_diagram(legacy), {"id": "legacy"})
        self.assertTrue(legacy.exists())

    def test_bounded_json_read_rejects_missing_large_invalid_and_non_object_files(self):
        missing = self.workspace / "missing.json"
        with self.assertRaises(ArtifactNotFoundError):
            self.storage.read_json_object(missing, max_bytes=10)

        large = self.workspace / "large.json"
        large.write_text('{"value":"too large"}', encoding="utf-8")
        with self.assertRaises(ArtifactTooLargeError):
            self.storage.read_json_object(large, max_bytes=10)

        invalid = self.workspace / "invalid.json"
        invalid.write_text("not json", encoding="utf-8")
        with self.assertRaises(InvalidJSONFileError):
            self.storage.read_json_object(invalid, max_bytes=100)

        array = self.workspace / "array.json"
        array.write_text("[]", encoding="utf-8")
        with self.assertRaises(InvalidJSONFileError):
            self.storage.read_json_object(array, max_bytes=100)

    def test_atomic_json_write_uses_two_spaces_lf_and_final_newline(self):
        path = self.workspace / ".graphpilot" / "context" / "drafts" / "value.json"

        result = self.storage.write_json_object(path, {"z": 1, "a": "é"})

        self.assertEqual(result, path.resolve())
        raw = path.read_bytes()
        self.assertEqual(raw, '{\n  "a": "é",\n  "z": 1\n}\n'.encode("utf-8"))
        self.assertFalse(any(path.parent.glob("*.tmp")))

    def test_exclusive_json_write_never_replaces_existing_snapshot(self):
        path = self.storage.storage_root() / "snapshots" / "run" / "attempt-001.json"
        self.storage.write_json_object_exclusive(path, {"attempt": 1})

        with self.assertRaises(FileExistsError):
            self.storage.write_json_object_exclusive(path, {"attempt": 2})

        self.assertEqual(self.storage.read_json_object(path, max_bytes=100), {"attempt": 1})

    def test_remove_file_is_safe_and_reports_absence(self):
        path = self.workspace / ".graphpilot" / "context" / "drafts" / "candidate.json"
        path.parent.mkdir(parents=True)
        path.write_text("candidate", encoding="utf-8")

        self.assertTrue(self.storage.remove_file(path))
        self.assertFalse(self.storage.remove_file(path))

    def test_symlink_escape_is_rejected_when_supported(self):
        outside = Path(tempfile.mkdtemp())
        link = self.workspace / "outside-link"
        try:
            try:
                os.symlink(outside, link, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable.")
            with self.assertRaises(UnsafePathError):
                self.storage.resolve_safe_path(link / "secret.txt")
        finally:
            if link.is_symlink():
                link.unlink()
            outside.rmdir()
