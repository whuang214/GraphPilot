"""`.env.example` offers exactly the variables `settings.py` reads, and only those.

`GRAPHPILOT_DEFAULT_WORKSPACE_DIR` was removed from `settings.py` and left in this file.
An operator who set it got no error and no effect, and two documents told them it was how
you point GraphPilot at a workspace. `a5` found it, removed the setting and the prose, and
could not remove the line -- it read `AGENTS.md`'s "never edit `.env`" as covering the
tracked example template too, so the dead knob outlived the audit that found it.

The same shape as every other drift here: a hand-maintained description of a machine-
readable thing, with nothing comparing the two. So this compares them.

Read with `ast` rather than a regex. A regex over source cannot tell `os.environ.get('X')`
from the same string in a comment or a docstring, and instruments that could not tell the
difference are what made the last audit's census under-report.
"""

import ast
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BACKEND = Path(settings.BASE_DIR)
SETTINGS = BACKEND / "graphpilot" / "settings.py"
EXAMPLE = BACKEND / ".env.example"
#: The third copy of the same list, and the one that drifted furthest: it said "Seven
#: variables" above a block listing six, having kept the count when `a5` removed the dead
#: row beneath it.
REFERENCE = BACKEND.parent / "docs" / "04-development" / "01-environment.md"

#: Only the project's own configuration. `PATH` and friends are not ours to document.
OURS = re.compile(r"^(DJANGO|GRAPHPILOT)_")


def _read_by_settings():
    """Every `os.environ.get("NAME", ...)` literal in settings.py."""
    tree = ast.parse(SETTINGS.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "get":
            continue
        value = node.func.value
        is_environ = (
            (isinstance(value, ast.Attribute) and value.attr == "environ")
            or (isinstance(value, ast.Name) and value.id == "environ")
        )
        if not is_environ or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            found.add(first.value)
    return {name for name in found if OURS.match(name)}


def _offered_by_example():
    """Every `NAME=` assignment in .env.example, ignoring comments."""
    return {
        match.group(1)
        for match in re.finditer(
            r"^([A-Z][A-Z0-9_]*)=", EXAMPLE.read_text(encoding="utf-8"), re.M
        )
        if OURS.match(match.group(1))
    }


def _listed_by_reference():
    """The variables in the environment reference's backend block, and its stated count."""
    text = REFERENCE.read_text(encoding="utf-8")
    start = text.index("## Environment Variables")
    end = text.index("Frontend examples:", start)
    section = text[start:end]
    names = {
        match.group(1)
        for match in re.finditer(r"^([A-Z][A-Z0-9_]*)=", section, re.M)
        if OURS.match(match.group(1))
    }
    stated = re.search(r"\*\*([A-Za-z]+) variables", section)
    return names, (stated.group(1).lower() if stated else None)


class EnvExampleTests(SimpleTestCase):
    def test_the_example_offers_nothing_the_code_ignores(self):
        """The `GRAPHPILOT_DEFAULT_WORKSPACE_DIR` failure, in the direction it happened."""
        dead = sorted(_offered_by_example() - _read_by_settings())

        self.assertEqual(
            dead, [], "offered to an operator and read by nothing: setting it does nothing",
        )

    def test_the_example_omits_nothing_the_code_reads(self):
        """The other direction: a setting nobody is told exists."""
        undocumented = sorted(_read_by_settings() - _offered_by_example())

        self.assertEqual(
            undocumented, [], "settings.py reads these and the example never mentions them",
        )

    def test_the_environment_reference_lists_the_same_set(self):
        """A third copy of the list, in the document a newcomer is sent to."""
        listed, _ = _listed_by_reference()

        self.assertEqual(
            listed, _read_by_settings(),
            "01-environment.md and settings.py disagree about the environment",
        )

    def test_the_environment_reference_counts_what_it_lists(self):
        """It said "Seven variables" over a block of six for as long as there were six.

        A prose count beside the list it counts is the cheapest possible drift, and the
        only reason it lasted is that nothing ever compared the two.
        """
        listed, stated = _listed_by_reference()
        words = {
            4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
        }

        self.assertEqual(
            stated, words.get(len(listed)),
            f"the document says {stated!r} and then lists {len(listed)}",
        )

    def test_the_reader_actually_finds_the_settings(self):
        """Guard the instrument, not just the thing it measures.

        Both checks above pass trivially if `_read_by_settings` returns an empty set --
        which is precisely how six checks in the last audit reported clean while broken.
        """
        found = _read_by_settings()

        self.assertIn("GRAPHPILOT_STORAGE_DIR", found)
        self.assertIn("DJANGO_SECRET_KEY", found)
        self.assertGreaterEqual(len(found), 5, f"parser found only {found}")
