"""`diagram_check_draft` — the free dry run, exercised the way the workflow tells hosts to.

**This file exists because of a bug that reached three cold hosts.** `diagram_check_draft`
raised `NameError: name 'EvidenceService' is not defined` on *every* call that passed
`workspaceDir`, and had done since the symbol check landed. The name was used and never
imported.

Two things made it worse than a typo:

* `workspaceDir` is the single most emphatic instruction in the product. The workflow says
  **"Pass `workspaceDir` or your citations are not read"**, and the tool description calls
  a wrong citation "the one mistake you cannot repair afterwards". So the instruction we
  shouted loudest pointed at the one code path that could not run.
* The host saw only `"The operation failed unexpectedly."` — nothing suggesting the draft
  was fine and the *tool* was broken. All three hosts wrote their own citation checkers to
  get around it. That is a heroic workaround, not a guard rail.

**600 tests missed it because not one of them called the tool.** Its name appeared in the
published-surface list and nowhere else. A tool listed but never invoked is untested
surface, so the tests below call it the way a host does — including the arguments a host
is told to pass.
"""

import asyncio
import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from mcp_server import server


def _run(coroutine):
    return asyncio.run(coroutine)


def _payload(result):
    """A tool result, whether it came back structured or as text."""
    if getattr(result, "structuredContent", None):
        return result.structuredContent
    if isinstance(result, dict):
        return result
    return json.loads(result.content[0].text)


def _draft(**overrides):
    draft = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "probe",
        "diagramType": "bdd_diagram",
        "authority": "as_implemented",
        "requests": ["diagram the thing"],
        "evidence": [
            {
                "id": "ev-one",
                "kind": "code",
                "locator": {
                    "path": "app/models.py",
                    "symbol": "Thing",
                    "lineRange": {"start": 1, "end": 3},
                },
                "summary": "the Thing model",
            }
        ],
        "elements": [
            {
                "id": "thing",
                "semanticType": "block",
                "label": "Thing",
                "assurance": "grounded",
                "evidenceRefs": ["ev-one"],
            }
        ],
        "relationships": [],
        "assumptions": [],
    }
    draft.update(overrides)
    return draft


class CheckDraftWithAWorkspaceTests(SimpleTestCase):
    """The path every host is instructed to take."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        source = self.workspace / "app" / "models.py"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("class Thing:\n    name = 1\n    kind = 2\n", encoding="utf-8")

    def test_passing_a_workspace_resolves_citations_instead_of_crashing(self):
        result = _payload(_run(server.diagram_check_draft(_draft(), str(self.workspace))))

        self.assertTrue(result["valid"], result.get("findings"))
        self.assertIn("evidence locators resolve", result["checked"])

    def test_a_citation_pointing_at_the_wrong_lines_is_caught_before_the_name_is_spent(self):
        """The whole reason `workspaceDir` is worth insisting on."""
        draft = _draft()
        draft["evidence"][0]["locator"]["symbol"] = "SomethingElse"

        result = _payload(_run(server.diagram_check_draft(draft, str(self.workspace))))

        self.assertFalse(result["valid"])
        self.assertIn(
            "evidence_symbol_not_in_range",
            {finding["code"] for finding in result["findings"]},
        )

    def test_a_missing_file_is_reported_as_a_finding_not_an_internal_error(self):
        draft = _draft()
        draft["evidence"][0]["locator"]["path"] = "app/not_here.py"

        result = _payload(_run(server.diagram_check_draft(draft, str(self.workspace))))

        self.assertFalse(result["valid"])
        self.assertIn(
            "evidence_unreadable", {finding["code"] for finding in result["findings"]}
        )

    def test_without_a_workspace_it_says_plainly_that_citations_were_not_read(self):
        """Degrading quietly here would be worse than failing: the host would believe
        its citations had been checked."""
        result = _payload(_run(server.diagram_check_draft(_draft())))

        self.assertTrue(result["valid"])
        self.assertNotIn("evidence locators resolve", result["checked"])
        self.assertTrue(
            any("evidence locators resolve" in item for item in result["notChecked"]),
            result["notChecked"],
        )

    def test_a_workspace_that_does_not_exist_is_reported_rather_than_raised(self):
        result = _run(server.diagram_check_draft(_draft(), str(self.workspace / "nope")))
        payload = _payload(result)

        # Either a clean finding or a typed operation problem is acceptable; an
        # unhandled exception is not, and that is what this asserts.
        self.assertIsInstance(payload, dict)

    def test_the_dry_run_writes_nothing_at_all(self):
        """`diagram_check_draft` is free. If it ever writes, calling it freely stops
        being safe advice and the whole point of the tool is lost."""
        before = {p for p in self.workspace.rglob("*")}

        _run(server.diagram_check_draft(_draft(), str(self.workspace)))

        self.assertEqual({p for p in self.workspace.rglob("*")}, before)
        self.assertFalse((self.workspace / ".graphpilot").exists())


class CheckDraftMirrorsCreateTests(SimpleTestCase):
    """A dry run that disagrees with the real thing is worse than no dry run."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        source = self.workspace / "app" / "models.py"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("class Thing:\n    name = 1\n    kind = 2\n", encoding="utf-8")

    def test_what_check_accepts_create_also_accepts(self):
        # Note the argument order differs between the two tools -- check_draft takes
        # (draft, workspaceDir) and create takes (workspaceDir, draft). Harmless over MCP,
        # where a host passes a named JSON object, and a trap for anything calling Python.
        draft = _draft(diagramName="mirror-ok")

        checked = _payload(_run(server.diagram_check_draft(draft, str(self.workspace))))
        created = _run(server.diagram_create(str(self.workspace), draft))

        self.assertTrue(checked["valid"])
        self.assertFalse(getattr(created, "isError", False), _payload(created))

    def test_what_check_refuses_create_also_refuses(self):
        draft = _draft(diagramName="mirror-bad")
        draft["evidence"][0]["locator"]["symbol"] = "NotPresent"

        checked = _payload(_run(server.diagram_check_draft(draft, str(self.workspace))))
        created = _run(server.diagram_create(str(self.workspace), draft))

        self.assertFalse(checked["valid"])
        self.assertTrue(getattr(created, "isError", False))
        # And nothing was written, so the name is still free.
        self.assertFalse((self.workspace / ".graphpilot" / "diagrams" / "mirror-bad.gp.json").exists())
