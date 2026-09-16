"""The canonical integration catalogs match the real MCP and browser API surfaces.

The root README introduces the product; full inventories belong to the MCP and API
architecture documents. Compare their tables with code so missing or invented entries
cannot drift silently. Retain the root README's no-provider claim check.
"""

import ast
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BACKEND = Path(settings.BASE_DIR)
README = BACKEND.parent / "README.md"
MCP_REFERENCE = BACKEND.parent / "docs/02-architecture/01-mcp-tools/README.md"
API_REFERENCE = BACKEND.parent / "docs/02-architecture/05-api-routes.md"


def _document_section(path, heading, stop="\n## "):
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    return text[start:].split(stop, 1)[0]


def _documented_tools():
    section = _document_section(MCP_REFERENCE, "## Public surface")
    return set(re.findall(r"^\|\s*`([a-z][a-z0-9_]*)`\s*\|", section, re.M))


def _documented_routes():
    section = _document_section(API_REFERENCE, "## 4. Route Summary")
    rows = re.findall(
        r"^\|\s*`(/api/[^`?]+)(?:\?[^`]*)?`\s*\|\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\|",
        section, re.M,
    )
    return {f"{method} {path}" for path, method in rows}


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
    def test_the_mcp_catalog_lists_every_registered_tool(self):
        missing = sorted(_registered_tools() - _documented_tools())

        self.assertEqual(missing, [], "registered, and the MCP catalog never mentions it")

    def test_the_mcp_catalog_invents_no_tool(self):
        invented = sorted(_documented_tools() - _registered_tools())

        self.assertEqual(invented, [], "advertised to a reader and registered by nothing")

    def test_the_api_summary_invents_no_route(self):
        invented = sorted(_documented_routes() - _registered_routes())

        self.assertEqual(invented, [], "advertised to a reader and routed by nothing")

    def test_the_api_summary_lists_every_route(self):
        missing = sorted(_registered_routes() - _documented_routes())

        self.assertEqual(missing, [], "routed, and the API summary never mentions it")

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
