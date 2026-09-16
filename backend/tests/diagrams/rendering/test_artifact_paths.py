"""Where an artifact goes is one rule, and it had three spellings.

`DiagramRenderService.artifact_sibling` is the owner: it is what actually writes the file.
The other two were

- `WorkspaceStorageService.svg_artifact_path` / `png_artifact_path`, which derived the path
  from a diagram *name* and were called by nothing but their own test, and
- an inline `name.removesuffix(".gp.json") + ".svg"` in `api/views.py`, used to tell a user
  which file was missing when a render-on-save failed.

The third is the one that mattered. It agreed with the renderer by coincidence, and the
coincidence was load-bearing: move artifacts into a subdirectory and that warning names a
path nothing was ever going to write, at the one moment a user depends on the string.
"""

import ast
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.rendering.diagram_render_service import DiagramRenderService
from services.shared.workspace_storage_service import WorkspaceStorageService


class OneOwnerForArtifactPathsTests(SimpleTestCase):
    def test_the_renderer_owns_the_rule(self):
        source = Path("/w/.graphpilot/diagrams/order-approval.gp.json")

        self.assertEqual(
            DiagramRenderService.artifact_sibling(source, ".svg"),
            source.with_name("order-approval.svg"),
        )
        self.assertEqual(
            DiagramRenderService.artifact_sibling(source, ".png"),
            source.with_name("order-approval.png"),
        )

    def test_a_name_without_the_full_suffix_still_lands_beside_its_source(self):
        """`.gp.json` is a multi-part suffix, so `Path.stem` alone leaves `.gp`."""
        source = Path("/w/plain.json")

        self.assertEqual(
            DiagramRenderService.artifact_sibling(source, ".svg"),
            Path("/w/plain.svg"),
        )

    def test_no_second_owner_has_reappeared(self):
        for gone in ("svg_artifact_path", "png_artifact_path"):
            with self.subTest(method=gone):
                self.assertFalse(hasattr(WorkspaceStorageService, gone))

    def test_nothing_rebuilds_the_rule_by_hand(self):
        """An inline `removesuffix(".gp.json")` beside an extension is the rule forked.

        Compiled rather than grepped: the first version of this test flagged the docstring
        above, which *describes* the defect. A rule explained in prose is documentation; a
        rule re-implemented in code is a second owner, and only the second is a finding.
        """
        offenders = []
        for path in Path(settings.BASE_DIR).rglob("*.py"):
            if "tests" in path.parts or ".venv" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                # `x.removesuffix(".gp.json")` anywhere outside the owning method.
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "removesuffix"
                    and any(
                        isinstance(a, ast.Constant) and a.value == ".gp.json"
                        for a in node.args
                    )
                ):
                    offenders.append(f"{path.name}:{node.lineno}")
        self.assertEqual(offenders, [], "the artifact-path rule has forked again")
