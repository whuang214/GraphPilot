"""Every tool answers on the channel the contract publishes.

`01-mcp-tools/README.md` says "`structuredContent` is the exact tool-specific machine
payload", and `01-diagram-tools.md` tabulates `diagram_render`'s three result variants
under a `structuredContent` heading. Four of eleven tools did not populate it at all, and
`diagram_render` populated it **for PNG but not for SVG** -- the same tool, one line apart,
answering in different places depending on an argument.

A host following the published contract read `structuredContent.svgPath` and found
nothing. Nothing caught it because nothing looked: the unit tests call these coroutines
directly, where a returned `dict` *is* the answer, and the difference only exists once
FastMCP decides how to put that return on the wire. It took driving the real stdio
transport to see it.

This test asserts the property at the boundary that matters -- what a tool hands back --
rather than re-listing which tools exist.
"""

import ast
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

SERVER = Path(settings.BASE_DIR) / "mcp_server" / "server.py"

#: `diagram_workflow` is prose. `_prose_result` omits `structuredContent` deliberately --
#: see its docstring: there is no structure to carry, and FastMCP's auto-wrapping of a
#: bare string shipped the whole document twice. That is a decision, not an omission.
PROSE_ONLY = {"diagram_workflow"}

#: Helpers that build a `CallToolResult` carrying `structuredContent`.
STRUCTURED_BUILDERS = {"_structured_result", "_markdown_result", "_error"}


def _tool_returns():
    """For each `@mcp.tool()` function, the set of things its `return` statements build."""
    tree = ast.parse(SERVER.read_text(encoding="utf-8"))
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(
            isinstance(d, ast.Call)
            and getattr(d.func, "attr", None) == "tool"
            and getattr(getattr(d.func, "value", None), "id", None) == "mcp"
            for d in node.decorator_list
        ):
            continue
        kinds = set()
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Return) or inner.value is None:
                continue
            value = inner.value
            if isinstance(value, ast.Call):
                kinds.add(getattr(value.func, "id", None) or getattr(value.func, "attr", None))
            elif isinstance(value, ast.Dict):
                kinds.add("<bare dict>")
            else:
                kinds.add("<bare value>")
        out[node.name] = kinds
    return out


class ResultChannelTests(SimpleTestCase):
    def test_every_tool_answers_through_a_structured_builder(self):
        """A bare `dict` or `str` return is the defect: FastMCP serializes it into
        `content` and leaves `structuredContent` null, silently."""
        offenders = {
            name: sorted(str(k) for k in kinds)
            for name, kinds in _tool_returns().items()
            if name not in PROSE_ONLY and not kinds <= STRUCTURED_BUILDERS
        }

        self.assertEqual(
            offenders, {},
            "returns a bare value, so the documented structuredContent arrives empty",
        )

    def test_a_tool_does_not_change_channel_between_its_own_branches(self):
        """`diagram_render` answered in `structuredContent` for PNG and in `content` for
        SVG. Whatever a tool chooses, every branch of it must choose the same."""
        mixed = {
            name: sorted(str(k) for k in kinds)
            for name, kinds in _tool_returns().items()
            if {"<bare dict>", "<bare value>"} & kinds and kinds & STRUCTURED_BUILDERS
        }

        self.assertEqual(mixed, {}, "one tool, two contracts, depending on the branch")

    def test_the_reader_finds_the_tools(self):
        """Both checks above pass on an empty mapping."""
        found = _tool_returns()

        self.assertIn("diagram_render", found)
        self.assertIn("diagram_workflow", found)
        self.assertGreaterEqual(len(found), 9, f"only found {sorted(found)}")
