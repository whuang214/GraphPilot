"""The command reference lists the commands and flags that exist.

`a5.8` added `05-command-reference.md` because the fragments were spread across
`AGENTS.md`, three `README.md` files and two design documents, and no two agreed on the
flags. A single document is only worth having if it stays true, and every documented
command surface this audit checked had drifted — the error registry by 50 codes, the
schema doc by two fields, the tool docs by three response shapes.

So the same treatment: compare it against the commands, both directions, and check that a
documented flag is one `argparse` will actually accept.
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management import load_command_class
from django.test import SimpleTestCase

BACKEND = Path(settings.BASE_DIR)
DOC = BACKEND.parent / "docs" / "04-development" / "05-command-reference.md"
COMMANDS = BACKEND / "operations" / "management" / "commands"
PACKAGE_JSON = BACKEND.parent / "frontend" / "package.json"


def _commands():
    return sorted(p.stem for p in COMMANDS.glob("*.py") if not p.stem.startswith("__"))


def _npm_scripts():
    return sorted(json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))["scripts"])


def _real_flags(name):
    parser = load_command_class("operations", name).create_parser("manage.py", name)
    return {
        option
        for action in parser._actions
        for option in action.option_strings
        if option.startswith("--")
    }


class CommandReferenceTests(SimpleTestCase):
    def test_every_command_is_listed(self):
        text = DOC.read_text(encoding="utf-8")

        missing = [name for name in _commands() if name not in text]

        self.assertEqual(missing, [], "a command a person can run and the reference omits")

    def test_no_command_is_invented(self):
        """`manage.py <something>` in the document has to be a real command."""
        text = DOC.read_text(encoding="utf-8")
        named = set(re.findall(r"manage\.py (\w+)", text))
        builtin = {"test", "migrate", "runserver", "shell", "makemigrations"}

        invented = sorted(named - set(_commands()) - builtin)

        self.assertEqual(invented, [], "documented and not a command")

    def test_every_documented_flag_is_accepted(self):
        """A flag in the reference that argparse rejects is worse than no reference: it
        fails at the moment someone trusted the document."""
        text = DOC.read_text(encoding="utf-8")
        for name in _commands():
            accepted = _real_flags(name) | {"--parallel", "--no-input", "--verbosity"}
            # Flags in a row that also names the command, or in its command block.
            documented = {
                flag
                for line in text.splitlines()
                if name in line or line.lstrip().startswith("| `--")
                for flag in re.findall(r"`(--[\w-]+)`?", line)
            }
            with self.subTest(command=name):
                self.assertEqual(
                    sorted(documented - accepted - _all_flags()), [],
                    f"{name} does not accept these",
                )

    def test_every_real_flag_is_documented(self):
        text = DOC.read_text(encoding="utf-8")
        for name in _commands():
            with self.subTest(command=name):
                undocumented = sorted(
                    flag for flag in _real_flags(name)
                    if flag not in text and flag not in _DJANGO_NOISE
                )
                self.assertEqual(undocumented, [], f"{name} accepts these and nothing says so")


class FrontendCommandsTests(SimpleTestCase):
    """The same treatment for `package.json`, which this guard did not cover.

    It checked Django management commands only, so the Frontend table drifted quietly:
    `build`, `e2e` and `preview` were all runnable and all missing, and the one-time
    `playwright install chromium` — without which `verify` fails at its last leg on a
    fresh machine — was documented in `frontend/README.md` alone.
    """

    def test_every_npm_script_is_listed(self):
        text = DOC.read_text(encoding="utf-8")

        missing = [name for name in _npm_scripts() if f"npm run {name}" not in text]

        self.assertEqual(
            missing, [], "a script in package.json that the reference does not list"
        )

    def test_no_npm_script_is_invented(self):
        text = DOC.read_text(encoding="utf-8")
        named = set(re.findall(r"npm run ([\w:-]+)", text))

        self.assertEqual(sorted(named - set(_npm_scripts())), [], "documented and not a script")

    def test_the_browser_download_is_not_left_to_one_readme(self):
        """`npm install` cannot fetch browsers, so the gate needs a step of its own."""
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("playwright install", text)


#: Flags Django and argparse add to every command; documenting them once per command is
#: noise, and `--help` is how you would find them anyway.
_DJANGO_NOISE = {
    "--help", "--version", "--verbosity", "--settings", "--pythonpath", "--traceback",
    "--no-color", "--force-color", "--skip-checks",
}


def _all_flags():
    """Any flag some command accepts — the document groups them in one table."""
    return {flag for name in _commands() for flag in _real_flags(name)} | _DJANGO_NOISE
