"""Legacy Windows path handling stops at 260 characters, and it lies about it.

Evaluation nests a workspace inside a run directory inside a control workspace,
and diagnostics adds a second tree inside that. The sum crosses MAX_PATH, and
the failures that follow are not obviously about path length: a write raises
"cannot find the path", and -- worse -- an existence check can return False for
a file that is plainly there, so callers that branch on existence take the wrong
branch and fail somewhere else entirely. Long-path-aware hosts may accept the
ordinary path directly; the storage boundary must work in both Windows modes.

That is the shape of two separate defects already paid for: a live anchor run
lost to a 267-character path, and a diagnostics run that reported
diagnostics_write_failed while producing nothing.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from django.test import SimpleTestCase

from services.shared.workspace_storage_service import WorkspaceStorageService, os_path


def _deep(base: Path, target: int) -> Path:
    path = base
    while len(str(path)) < target:
        path = path / "segment-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return path


class LongPathBoundaryTests(SimpleTestCase):
    def setUp(self):
        # Ordinary cleanup cannot delete what these tests create, for the same
        # reason the product could not write it: shutil walks plain paths.
        self._root = tempfile.mkdtemp()
        self.base = Path(self._root).resolve()
        self.addCleanup(self._remove_tree)

    def _remove_tree(self):
        shutil.rmtree(os_path(self.base), ignore_errors=True)
        shutil.rmtree(self.base, ignore_errors=True)

    def test_os_path_is_a_noop_off_windows_and_idempotent_on_it(self):
        once = os_path(self.base)
        self.assertEqual(os_path(once), once)
        if os.name != "nt":
            self.assertEqual(once, self.base)

    def test_it_does_not_disturb_ordinary_paths(self):
        storage = WorkspaceStorageService(self.base)
        target = storage.resolve_safe_path(".graphpilot/diagrams/short.gp.json")

        storage.write_bytes_exclusive(target, b"{}")

        self.assertTrue(storage.is_existing_file(target))
        self.assertEqual(storage.read_bytes(target, max_bytes=64), b"{}")
        # The stored path stays canonical; the prefix never leaks into evidence.
        self.assertNotIn("\\\\?\\", str(target))

    @unittest.skipUnless(os.name == "nt", "MAX_PATH is a Windows limit.")
    def test_a_file_past_max_path_can_be_written_and_read_back(self):
        storage = WorkspaceStorageService(self.base)
        deep = _deep(self.base / ".graphpilot", 300) / "artifact.json"
        self.assertGreater(len(str(deep)), 260)

        storage.write_bytes_exclusive(deep, b'{"ok":true}')

        self.assertEqual(storage.read_bytes(deep, max_bytes=64), b'{"ok":true}')

    @unittest.skipUnless(os.name == "nt", "MAX_PATH is a Windows limit.")
    def test_existence_is_answered_about_the_file_not_its_name_length(self):
        """Existence stays correct with legacy or long-path-aware Windows APIs."""
        storage = WorkspaceStorageService(self.base)
        deep = _deep(self.base / ".graphpilot", 300) / "artifact.json"
        storage.write_bytes_exclusive(deep, b"{}")

        self.assertTrue(str(os_path(deep)).startswith("\\\\?\\"))
        self.assertTrue(storage.is_existing_file(deep))
