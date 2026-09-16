"""A diagram file is read under a bound, like every other read in this service.

`load_diagram` was the exception. Every neighbour -- `read_bytes`, `read_text`,
`read_json_object` -- takes a `max_bytes` and refuses past it; this one opened the file
and handed the descriptor to `json.load`. Measured: a 40 MB `.gp.json` was read whole in
0.06 seconds, while `read_json_object` refused the same file.

That asymmetry pointed the wrong way. `load_diagram` is the entry point that takes the
*least* trusted input -- a diagram is opened from wherever the caller points, including
a repository somebody else wrote and a path a host passed in -- and it was the one
without a bound.
"""

import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.shared.workspace_storage_service import (
    MAX_DIAGRAM_BYTES,
    ArtifactTooLargeError,
    WorkspaceStorageService,
)


class DiagramSizeBoundTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.storage = WorkspaceStorageService(self._tmp.name)
        self.path = self.storage.diagram_file_path("big")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, payload_bytes: int):
        document = {
            "schemaVersion": "graphpilot.diagram.v1",
            "diagramType": "bdd_diagram",
            "nodes": [{"id": "n", "data": {"label": "x" * payload_bytes}}],
            "edges": [],
        }
        self.path.write_text(json.dumps(document), encoding="utf-8")
        return self.path.stat().st_size

    def test_a_diagram_past_the_bound_is_refused_rather_than_read(self):
        size = self._write(MAX_DIAGRAM_BYTES + 1024)
        self.assertGreater(size, MAX_DIAGRAM_BYTES)

        with self.assertRaises(ArtifactTooLargeError):
            self.storage.load_diagram(self.path)

    def test_a_diagram_of_ordinary_size_still_loads(self):
        """The bound must not become a limit on real work.

        The largest diagram this repository ships is 43 KB; 256 nodes is the layout
        engine's own ceiling. A test that only proved the refusal would pass just as
        well if the bound were one byte.
        """
        self._write(64 * 1024)

        loaded = self.storage.load_diagram(self.path)

        self.assertEqual(loaded["nodes"][0]["id"], "n")
        self.assertGreater(MAX_DIAGRAM_BYTES, 1024 * 1024)
