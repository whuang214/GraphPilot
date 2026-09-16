"""`d3`. A document that names something the code does not have is a lie with a date on it.

An audit of the 32 active documents found **65 claims** about tools, management commands,
settings and classes that do not exist — six documents were substantially about a pipeline
removed months earlier. Nobody wrote those documents wrongly; the code moved and the prose
did not, which is exactly the failure a test can prevent and a review cannot.

Two directions, because both are real:

* a document **names something absent** — a reader follows instructions that cannot work;
* the tool index **omits something present** — `diagram_check_draft` was missing from it,
  and a host reading only that page would never call the one tool that makes authoring
  cheap.

Forward-looking prose is not drift. A backlog naming an unbuilt tool is doing its job, and
so is a deferred-scope list, provided it says plainly that the thing does not exist. The
exemptions below encode that distinction rather than exempting whole files by name where a
heading can carry the meaning instead.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BACKEND = Path(settings.BASE_DIR)
ROOT = BACKEND.parent
DOCS = ROOT / "docs"

#: Whole documents about future or past work rather than the present system.
FORWARD_LOOKING = {
    "docs/05-delivery/02-backlog.md",
    "docs/05-delivery/03-repository-restructure-plan.md",
    "docs/05-delivery/04-decisions.md",
}

#: A heading that declares what follows to be unbuilt. Everything under it, to the next
#: heading of the same level or higher, may name things that do not exist.
UNBUILT_HEADING = re.compile(
    r"^#{2,6}\s+.*(deferred|not implemented|future|planned|out of scope|non-goals|unsupported)",
    re.I,
)
#: The same admission made inline, for a single row or sentence.
#:
#: `removed`, `deleted` and `gone` earn their place beside the forward-looking words: a
#: document explaining why something was taken out has to name the thing it took out, and
#: that is the opposite of a stale claim. Retiring the draft log tripped this — the guard
#: read *"there was a `GRAPHPILOT_DRAFT_LOG` setting … it is gone"* as an assertion that
#: the setting exists.
#:
#: **A parenthetical aside in italics is history, whatever words it uses.** Growing the
#: word list once per phrasing is a treadmill: this guard has now caught four separate
#: sentences whose entire purpose was to explain a removal, and each time the fix was to
#: teach it another verb. `*(…)*` is the convention those asides already use, so it is the
#: convention the guard reads.
UNBUILT_INLINE = re.compile(
    r"(planned|not implemented|does not exist|deferred|unbuilt|removed|deleted|"
    r"it is gone|no longer|used to|there was a)",
    re.I,
)
#: An italic parenthetical aside — the repository's marker for "this is history".
HISTORICAL_ASIDE = re.compile(r"^\s*\*\(|^\s*\*?\(?(A|An|Two|The)\b.*\bwas\b.*\)\*\s*$")

#: Error codes share the `diagram_`/`context_` prefix and appear in tables as values.
NOT_TOOLS = {
    "diagram_exists", "diagram_not_found", "diagram_invalid", "diagram_too_large",
    "diagram_unreadable", "diagram_name_conflict", "context_too_large",
    # Edit-path refusals, not tools, despite the shared prefix.
    "diagram_crossed",
}
DJANGO_BUILTINS = {
    "test", "migrate", "runserver", "shell", "makemigrations", "collectstatic", "check",
    "createsuperuser", "startapp", "dbshell", "flush",
}


def _active_documents():
    docs = [
        path for path in DOCS.rglob("*.md")
        if not any(part.startswith(("06-", "07-")) for part in path.parts)
        and "07-generation-quality" not in path.as_posix()
    ]
    return sorted(docs) + [ROOT / "README.md", ROOT / "AGENTS.md"]


def _exempt_lines(text: str) -> set:
    exempt, depth = set(), None
    for number, line in enumerate(text.splitlines(), 1):
        heading = re.match(r"^(#{1,6})\s", line)
        if heading:
            level = len(heading.group(1))
            if depth is not None and level <= depth:
                depth = None
            if UNBUILT_HEADING.match(line):
                depth = level
        if depth is not None or UNBUILT_INLINE.search(line) or HISTORICAL_ASIDE.match(line):
            exempt.add(number)
            # An aside can wrap; exempt to its closing `)*`.
            if HISTORICAL_ASIDE.match(line) and not line.rstrip().endswith(")*"):
                for offset, following in enumerate(text.splitlines()[number:], number + 1):
                    exempt.add(offset)
                    if following.rstrip().endswith(")*"):
                        break
    return exempt


class DocumentationMatchesTheCodeTests(SimpleTestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Only functions carrying an `@mcp.tool()` decorator are tools. Matching every
        # `async def` also caught the `wrapped` closures inside the error-sanitizing
        # decorators, which are not surface and must not be documented.
        server = (BACKEND / "mcp_server" / "server.py").read_text(encoding="utf-8")
        cls.tools = set(re.findall(
            r"@mcp\.tool\(\)(?:\s*@[\w.]+(?:\([^)]*\))?)*\s*async def (\w+)\(", server
        ))
        cls.commands = {
            path.stem
            for path in (BACKEND / "operations" / "management" / "commands").glob("*.py")
            if not path.stem.startswith("_")
        }
        cls.settings_names = set(re.findall(
            r"^([A-Z][A-Z0-9_]+)\s*=",
            (BACKEND / "graphpilot" / "settings.py").read_text(encoding="utf-8"),
            flags=re.M,
        ))
        cls.classes = set()
        for path in BACKEND.rglob("*.py"):
            if any(part in {".venv", "__pycache__", "tests"} for part in path.parts):
                continue
            cls.classes |= set(re.findall(
                r"^class (\w+)", path.read_text(encoding="utf-8"), flags=re.M
            ))

    def _claims(self, extract, exists):
        """Every present-tense claim in the active documents that `exists` rejects."""
        found = []
        for path in _active_documents():
            relative = path.relative_to(ROOT).as_posix()
            if relative in FORWARD_LOOKING:
                continue
            text = path.read_text(encoding="utf-8")
            exempt = _exempt_lines(text)
            for number, line in enumerate(text.splitlines(), 1):
                if number in exempt:
                    continue
                for name in extract(line):
                    if not exists(name):
                        found.append(f"{relative}:{number} {name}")
        return sorted(found)

    def test_no_active_document_names_an_mcp_tool_that_is_not_registered(self):
        self.assertEqual(
            self._claims(
                lambda line: re.findall(r"`(diagram_\w+|context_\w+)`", line),
                lambda name: name in self.tools or name in NOT_TOOLS,
            ),
            [],
        )

    def test_no_active_document_names_a_management_command_that_does_not_exist(self):
        self.assertEqual(
            self._claims(
                lambda line: re.findall(r"manage\.py (\w+)", line),
                lambda name: name in self.commands or name in DJANGO_BUILTINS,
            ),
            [],
        )

    def test_no_active_document_names_a_setting_that_is_not_read(self):
        self.assertEqual(
            self._claims(
                lambda line: re.findall(r"`(GRAPHPILOT_[A-Z0-9_]+)`", line),
                lambda name: name in self.settings_names,
            ),
            [],
        )

    def test_no_active_document_names_a_service_class_that_does_not_exist(self):
        self.assertEqual(
            self._claims(
                lambda line: re.findall(r"`(\w*(?:Service|Registry))`", line),
                lambda name: name in self.classes,
            ),
            [],
        )

    def test_the_tool_index_lists_every_registered_tool(self):
        """The other direction. Naming an absent tool misleads; omitting a real one hides.

        `diagram_check_draft` was missing here — the free dry run that stops a host
        spending a diagram name on a draft that was going to be refused. A host reading
        only this page would never have called it.
        """
        index = (DOCS / "02-architecture" / "01-mcp-tools" / "README.md").read_text(encoding="utf-8")
        missing = sorted(
            name for name in self.tools
            if not name.startswith("_") and f"`{name}`" not in index
        )
        self.assertEqual(missing, [], "registered tools absent from the MCP tool index")
