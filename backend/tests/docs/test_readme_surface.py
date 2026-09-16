"""`README.md`'s integration surface is the real one.

It is the first thing a stranger reads and the last thing anybody updates. Both of its
lists had drifted: **nine MCP tools listed against eleven registered** (`diagram_read` and
`diagram_update` shipped and were never added), and **six REST routes against seven**
(`POST /api/diagrams/resolve` missing). The same file also still described the backend as
doing "LLM-backed generation (Azure OpenAI)" four paragraphs above the sentence explaining
that GraphPilot calls no model.

Nothing could have caught it. `test_command_reference.py` guards management commands and
`test_operation_errors_doc.py` guards error codes, but the surface a reader meets first
was compared to nothing.

Both lists are read from the code, not restated here, so this test cannot itself become a
third copy to maintain.
"""

import ast
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BACKEND = Path(settings.BASE_DIR)
README = BACKEND.parent / "README.md"


def _readme_section(heading, stop="\n## "):
    text = README.read_text(encoding="utf-8")
    start = text.index(heading)
    return text[start:text.index(stop, start + len(heading))]


def _tool_definitions():
    """Every `@mcp.tool()` function: its registered name, and the name it reports errors as.

    The registered name is the function's own, because `@mcp.tool()` takes no argument.
    The second name is the literal passed to `@_sanitize_unexpected_errors(...)`, which is
    what a host sees when the tool raises -- a separate hand-written copy of the same
    string, sitting one line below it.
    """
    tree = ast.parse((BACKEND / "mcp_server" / "server.py").read_text(encoding="utf-8"))
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        registered = any(
            isinstance(d, ast.Call)
            and getattr(d.func, "attr", None) == "tool"
            and getattr(getattr(d.func, "value", None), "id", None) == "mcp"
            for d in node.decorator_list
        )
        if not registered:
            continue
        reported = None
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Call)
                    and getattr(decorator.func, "id", None) == "_sanitize_unexpected_errors"
                    and decorator.args
                    and isinstance(decorator.args[0], ast.Constant)):
                reported = decorator.args[0].value
        found[node.name] = reported
    return found


def _registered_tools():
    return set(_tool_definitions())


def _registered_routes():
    """`METHOD /api/<path>` pairs, from `api/urls.py` plus each view's `@api_view`."""
    urls = ast.parse((BACKEND / "api" / "urls.py").read_text(encoding="utf-8"))
    paths = {}
    for node in ast.walk(urls):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name != "path" or not isinstance(node.args[0], ast.Constant):
            continue
        view = node.args[1]
        view_name = getattr(view, "attr", None) or getattr(view, "id", None)
        if view_name:
            paths[view_name] = node.args[0].value

    views = ast.parse((BACKEND / "api" / "views.py").read_text(encoding="utf-8"))
    methods = {}
    for node in ast.walk(views):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            target = getattr(decorator.func, "id", None) or getattr(decorator.func, "attr", None)
            if target != "api_view" or not decorator.args:
                continue
            for element in getattr(decorator.args[0], "elts", []):
                if isinstance(element, ast.Constant):
                    methods.setdefault(node.name, set()).add(element.value)

    return {
        f"{method} /api/{paths[view]}".rstrip("/")
        for view, verbs in methods.items() if view in paths
        for method in verbs
    }


class ReadmeSurfaceTests(SimpleTestCase):
    def test_the_readme_lists_every_registered_mcp_tool(self):
        section = _readme_section("## Integration surface")
        quoted = set(re.findall(r"`([a-z][a-z0-9_]*)`", section))
        missing = sorted(_registered_tools() - quoted)

        self.assertEqual(missing, [], "registered, and the README never mentions it")

    def test_the_readme_invents_no_mcp_tool(self):
        section = _readme_section("## Integration surface")
        listed = set(re.findall(r"`(diagram_[a-z_]+|health|echo)`", section))
        invented = sorted(listed - _registered_tools())

        self.assertEqual(invented, [], "advertised to a reader and registered by nothing")

    def test_the_readme_states_the_real_tool_and_route_counts(self):
        """The counts are prose beside the list, which is where drift is cheapest."""
        section = _readme_section("## Integration surface")
        tools = re.search(r"MCP tools \(IDE\), (\d+):", section)
        routes = re.search(r"REST API \(browser\), (\d+):", section)

        self.assertIsNotNone(tools, "the README no longer states a tool count")
        self.assertIsNotNone(routes, "the README no longer states a route count")
        self.assertEqual(int(tools.group(1)), len(_registered_tools()))
        self.assertEqual(int(routes.group(1)), len(_registered_routes()))

    def test_the_readme_lists_every_route(self):
        section = _readme_section("## Integration surface")
        quoted = set(re.findall(r"`((?:GET|POST|PUT|PATCH|DELETE) /api/[a-z/]*)`", section))
        missing = sorted(_registered_routes() - quoted)

        self.assertEqual(missing, [], "routed, and the README never mentions it")

    def test_the_readers_of_the_code_actually_find_something(self):
        """Every check above passes on an empty set. Six such checks certified clean in
        the last audit because they were broken, so the parsers get their own assertion."""
        self.assertIn("diagram_create", _registered_tools())
        self.assertIn("diagram_update", _registered_tools())
        self.assertGreaterEqual(len(_registered_tools()), 9)
        self.assertIn("GET /api/health", _registered_routes())
        self.assertGreaterEqual(len(_registered_routes()), 6)

    def test_each_tool_reports_errors_under_its_own_name(self):
        """`@_sanitize_unexpected_errors("...")` repeats the function's name by hand.

        A typo there is invisible until something raises, and then it misnames the tool in
        the one message a host has to debug from.
        """
        wrong = {
            name: reported
            for name, reported in _tool_definitions().items()
            if reported != name
        }

        self.assertEqual(wrong, {}, "a tool would report failures under the wrong name")

    def test_no_provider_is_described_as_part_of_the_backend(self):
        """The README said "LLM-backed generation (Azure OpenAI)" in its repo-layout
        section while its quickstart said there is no provider. A reader deciding whether
        this tool can be used offline met the wrong one first."""
        text = README.read_text(encoding="utf-8")
        offenders = [
            line.strip() for line in text.splitlines()
            if re.search(r"\b(azure|openai)\b", line, re.I)
            and "not a dependency" not in line
        ]

        self.assertEqual(offenders, [], "the README still advertises a provider")
