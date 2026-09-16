"""What the person sees when a write goes wrong halfway.

Both cases here were found by asking, of every failure the code can meet, what actually
reaches the human -- and both had the same answer: nothing, or worse than nothing.
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from services.diagrams.persistence.diagram_persistence_service import (
    DiagramPersistenceService,
)
from services.drafts.diagram_edit_service import DiagramEditService
from services.materialization.diagram_creation_service import DiagramCreationService
from services.materialization.diagram_update_service import (
    HISTORY_DEPTH,
    DiagramUpdateService,
)
from services.shared.workspace_storage_service import WorkspaceStorageService


def _draft(name="hist"):
    return {
        "schemaVersion": "graphpilot.draft.v1", "kind": "diagramDraft",
        "diagramName": name, "diagramType": "bdd_diagram", "authority": "conceptual",
        "requests": ["A block."],
        "elements": [{"id": "bike", "semanticType": "block", "label": "Bicycle",
                      "assurance": "conceptual"}],
        "relationships": [],
    }


class HistoryRecordsWhatHappenedTests(SimpleTestCase):
    """History is written after the save, not before it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = self._tmp.name
        DiagramCreationService().create(self.workspace, _draft())
        self.storage = WorkspaceStorageService(self.workspace)
        self.updates = DiagramUpdateService()
        self.edits = DiagramEditService()

    def _history(self):
        folder = self.storage.storage_root() / "history" / self.storage.sanitize_name("hist")
        return sorted(folder.glob("*.gp.json")) if folder.exists() else []

    def _edited_draft(self, note):
        draft = json.loads(
            self.edits.read(self.workspace, "hist").draft_path.read_text(encoding="utf-8")
        )
        draft["requests"].append(note)
        return draft

    def test_a_failed_save_leaves_no_history_behind(self):
        """A backup of a change that never landed is worse than no backup.

        `HISTORY_DEPTH` is three, so three failed updates used to evict every real
        version and leave the person three copies of the state they were already in --
        history destroyed by exactly the failure it exists to protect against.
        """
        before = self.storage.diagram_file_path("hist").read_text(encoding="utf-8")
        draft = self._edited_draft("Touch it.")

        with mock.patch.object(DiagramPersistenceService, "save",
                               side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.updates.update(self.workspace, draft)

        self.assertEqual(self._history(), [], "kept a backup of a change that never happened")
        self.assertEqual(
            self.storage.diagram_file_path("hist").read_text(encoding="utf-8"), before,
        )

    def test_repeated_failures_do_not_evict_real_history(self):
        """The consequence that makes the ordering matter rather than merely be untidy."""
        self.updates.update(self.workspace, self._edited_draft("A real change."))
        self.assertEqual(len(self._history()), 1)
        kept = self._history()[0].read_text(encoding="utf-8")

        for attempt in range(HISTORY_DEPTH + 1):
            draft = self._edited_draft(f"Doomed {attempt}.")
            with mock.patch.object(DiagramPersistenceService, "save",
                                   side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    self.updates.update(self.workspace, draft)

        surviving = self._history()
        self.assertEqual(len(surviving), 1, "failed writes pushed the real version out")
        self.assertEqual(surviving[0].read_text(encoding="utf-8"), kept)

    def test_a_successful_update_still_keeps_the_previous_version(self):
        """So the pair above cannot pass by never writing history at all."""
        before = self.storage.diagram_file_path("hist").read_text(encoding="utf-8")

        self.updates.update(self.workspace, self._edited_draft("A real change."))

        entries = self._history()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].read_text(encoding="utf-8"), before)


class UnreadableFolderIsNotAnEmptyOneTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        DiagramCreationService().create(self._tmp.name, _draft(name="only"))
        self.storage = WorkspaceStorageService(self._tmp.name)

    def test_an_unreadable_diagrams_folder_is_logged_rather_than_passed_off_as_empty(self):
        """`[]` is still the right answer to the caller; silence was not.

        A permissions problem and an empty workspace returned an identical empty list
        with nothing written anywhere, so the person was told they had no diagrams and
        given no thread to pull.
        """
        self.assertEqual(self.storage.list_diagram_names(), ["only"])

        with mock.patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
            with self.assertLogs(
                "services.shared.workspace_storage_service", level="WARNING"
            ) as captured:
                names = self.storage.list_diagram_names()

        self.assertEqual(names, [])
        self.assertIn("permissions", "\n".join(captured.output).lower())
