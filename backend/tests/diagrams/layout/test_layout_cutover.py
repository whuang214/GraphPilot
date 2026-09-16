import importlib.util
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import (
    DiagramLayoutService,
    LayoutEngineUnavailableError,
    PyGraphvizLayoutEngine,
)


REPO_ROOT = Path(__file__).resolve().parents[4]


class LayoutCutoverTests(SimpleTestCase):
    def test_removed_code_config_and_dependency_symbols_are_absent(self):
        old_symbols = (
            "class Graphviz" + "LayoutEngine",
            "class Grandalf" + "LayoutEngine",
            "def resolve_" + "dot_path",
        )
        source = (
            REPO_ROOT / "backend/services/diagrams/layout/diagram_layout_service.py"
        ).read_text(encoding="utf-8")
        for symbol in old_symbols:
            self.assertNotIn(symbol, source)
        requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").casefold()
        self.assertNotIn("grand" + "alf", requirements)
        self.assertIsNone(importlib.util.find_spec("grand" + "alf"))

    def test_removed_environment_value_is_ignored_and_local_files_are_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / ".graphviz/bin/dot.exe"
            marker.parent.mkdir(parents=True)
            marker.write_bytes(b"user-owned")
            engine = PyGraphvizLayoutEngine()
            with mock.patch.dict(
                "os.environ",
                {"GRAPHVIZ" + "_DOT_PATH": str(marker)},
                clear=False,
            ), mock.patch.object(engine, "available", return_value=False):
                with self.assertRaises(LayoutEngineUnavailableError):
                    DiagramLayoutService(engine=engine).layout("activity_diagram", [], [])
            self.assertEqual(marker.read_bytes(), b"user-owned")

    def test_no_runtime_layout_selector_exists(self):
        settings_text = (REPO_ROOT / "backend/graphpilot/settings.py").read_text(encoding="utf-8")
        env_example = (REPO_ROOT / "backend/.env.example").read_text(encoding="utf-8")
        self.assertNotIn("GRAPHPILOT_" + "LAYOUT_ENGINE", settings_text)
        self.assertNotIn("GRAPHVIZ" + "_DOT_PATH", settings_text)
        self.assertNotIn("GRAPHPILOT_" + "LAYOUT_ENGINE=", env_example)
        self.assertNotIn("GRAPHVIZ" + "_DOT_PATH=", env_example)
