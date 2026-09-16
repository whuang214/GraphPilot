"""Agent instructions are tracked, portable, and usable from a fresh clone.

AGENTS.md owns the working rules; delivery detail lives in the public workflow.
Neither depends on obsolete, ignored agent configuration from a previous environment.
"""

import re
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

ROOT = Path(settings.BASE_DIR).parent
RULES = ROOT / "AGENTS.md"
WORKFLOW = ROOT / "docs/04-development/06-delivery-workflow.md"


def _tracked(relative: str) -> bool:
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=ROOT, capture_output=True,
    ).returncode == 0


class AlwaysOnRulesTests(SimpleTestCase):
    def test_the_working_rules_do_not_depend_on_obsolete_agent_configuration(self):
        """A clone must not require a previous developer's ignored agent folder."""
        for path in (RULES, WORKFLOW):
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"`\.devin/[^`]+`")

    def test_the_rules_and_workflow_are_tracked(self):
        """`AGENTS.md` names the owners; a clone must actually contain them."""
        for relative in (
            "AGENTS.md",
            "docs/04-development/06-delivery-workflow.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue(
                    _tracked(relative),
                    f"{relative} is not in git, so a fresh clone does not have it",
                )

    def test_no_agent_file_hardcodes_one_machine(self):
        """Instructions that name an absolute home directory only work in one place."""
        offenders = []
        for path in (RULES, WORKFLOW):
            text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9]+|/(?:Users|home)/[A-Za-z0-9]+", text):
                offenders.append(path.relative_to(ROOT).as_posix())

        self.assertEqual(offenders, [], "derive paths from the repository root instead")

    def test_every_document_the_rules_point_at_exists(self):
        """A rule that links to a moved document is a rule nobody can follow."""
        text = RULES.read_text(encoding="utf-8")
        missing = [
            ref for ref in re.findall(r"`((?:docs/|AGENTS)[^`]*\.md)`", text)
            if not (ROOT / ref).is_file()
        ]

        self.assertEqual(missing, [])

    def test_the_delivery_detail_actually_moved(self):
        """The public workflow retains the delivery detail its entry point promises."""
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for topic in ("Tier", "proposed", "file cap", "liveness proof", "digest"):
            with self.subTest(topic=topic):
                self.assertIn(topic, workflow)
