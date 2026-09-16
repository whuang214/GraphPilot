"""The draft that produced a diagram is kept beside it.

When a diagram turns out to be wrong the question is always *what did the host claim* —
which elements it said existed, what it cited, what it flagged as uncertain. None of that
survives into the `.gp.json`, by design: `D1` decided the diagram carries evidence and
per-element assurance and never the host's prose.

So without a trace the only way to answer is to ask the agent, and it is long gone.
"""

import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.drafts.draft_projection_service import project
from services.materialization.diagram_creation_service import (
    DiagramCreationService,
    DraftRefused,
)


def _draft(name="traced"):
    return {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": name,
        "diagramType": "activity_diagram",
        "authority": "conceptual",
        "requests": ["Two steps in order."],
        "evidence": [],
        "elements": [
            {"id": "start", "semanticType": "initialNode", "label": "Start",
             "assurance": "conceptual"},
            {"id": "work", "semanticType": "opaqueAction", "label": "Do the work",
             "assurance": "conceptual"},
            {"id": "done", "semanticType": "activityFinalNode", "label": "Done",
             "assurance": "conceptual"},
        ],
        "relationships": [
            {"id": "a", "semanticType": "controlFlow", "source": "start", "target": "work",
             "assurance": "conceptual"},
            {"id": "b", "semanticType": "controlFlow", "source": "work", "target": "done",
             "assurance": "conceptual"},
        ],
        "assumptions": [],
    }


class DraftTraceTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = self._tmp.name

    def test_a_create_writes_no_draft_file(self):
        """That path belongs to the edit round trip now.

        `diagram_create` used to keep the accepted draft beside the diagram as a record of
        what the host claimed. `.graphpilot/drafts/<name>.draft.json` is the **edit working
        file**: written by `diagram_read`, consumed by `diagram_update`, and its presence
        means an edit is in flight.

        One path cannot mean both. A leftover trace is indistinguishable from an edit
        somebody started, and a host that edited one instead of calling the read would
        submit a whole-state document built before any browser save -- deleting everything
        a person added since, silently, having done nothing obviously wrong.

        Nothing is lost. The projection reproduces every class-1 field from the saved
        diagram, and the ask itself is in `metadata.requests`.
        """
        result = DiagramCreationService().create(self.workspace, _draft())

        self.assertIsNone(result.draft_path)
        drafts = Path(self.workspace) / ".graphpilot" / "drafts"
        self.assertFalse(drafts.exists() and any(drafts.iterdir()))

    def test_what_the_trace_held_is_recoverable_from_the_diagram(self):
        """The reason dropping it costs nothing, asserted rather than claimed."""
        submitted = _draft()
        result = DiagramCreationService().create(self.workspace, submitted)
        saved = json.loads(result.diagram_path.read_text(encoding="utf-8"))

        recovered = project(saved)

        self.assertEqual(
            [(e["id"], e["label"], e["semanticType"]) for e in recovered["elements"]],
            [(e["id"], e["label"], e["semanticType"]) for e in submitted["elements"]],
        )
        self.assertEqual(recovered["requests"], submitted["requests"])
        self.assertEqual(recovered["authority"], submitted["authority"])

    def test_the_ask_reaches_the_diagram_rather_than_only_the_trace(self):
        """The trace used to be the only place the reasoning survived, and the diagram
        deliberately carried none of it. The ask is the part of that reasoning a later
        reader actually needs — *why does this look like this* — so it is now in the
        diagram, and the trace is no longer the sole copy of anything."""
        result = DiagramCreationService().create(self.workspace, _draft())

        saved = json.loads(result.diagram_path.read_text(encoding="utf-8"))
        self.assertEqual(
            [entry["text"] for entry in saved["metadata"]["requests"]],
            ["Two steps in order."],
        )
        self.assertNotIn("assumptions", saved["metadata"], "no assumption was referenced")

    def test_a_refused_draft_leaves_no_trace(self):
        """A trace is a record of what produced a diagram. Nothing was produced."""
        broken = _draft("refused")
        del broken["elements"][1]["assurance"]

        with self.assertRaises(DraftRefused):
            DiagramCreationService().create(self.workspace, broken)

        drafts = Path(self.workspace) / ".graphpilot" / "drafts"
        self.assertFalse(drafts.exists() and any(drafts.iterdir()))

    def test_an_unwritable_trace_does_not_fail_a_created_diagram(self):
        """The diagram is the product. Losing its trace is a worse log, not a worse diagram."""
        service = DiagramCreationService()
        blocker = Path(self.workspace) / ".graphpilot" / "drafts"
        blocker.parent.mkdir(parents=True, exist_ok=True)
        blocker.write_text("not a directory", encoding="utf-8")

        result = service.create(self.workspace, _draft("resilient"))

        self.assertIsNone(result.draft_path)
        self.assertTrue(result.diagram_path.exists())
        self.assertEqual(result.node_count, 3)
