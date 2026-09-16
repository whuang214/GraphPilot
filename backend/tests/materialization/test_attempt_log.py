"""Every `diagram_create` attempt, recorded beside the diagrams it produced.

An accepted draft leaves a diagram and a trace. A refused one leaves nothing, by design —
so the only record that authoring was *hard* was the host's memory of it, and a host that
retried four times and then succeeded reports a success.

There was a setting for this once. `GRAPHPILOT_DRAFT_LOG` took a path and was off unless
set, and across four corpus runs produced a usable measurement **zero** times: it reached
the wrong process twice and held an empty value once. Every failure was silent, because
"off" and "misconfigured" look identical from outside. So there is no setting now — the
log goes where the diagrams go, unconditionally.

With one line held: it never creates the folder. A user whose first draft is refused must
not find a `.graphpilot/` they never asked for.
"""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.materialization import attempt_log
from services.materialization.diagram_creation_service import (
    DiagramCreationService,
    DraftRefused,
)


def _draft(name="logged", **overrides):
    draft = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": name,
        "diagramType": "bdd_diagram",
        "authority": "conceptual",
        "requests": ["x"],
        "evidence": [],
        "elements": [{"id": "one", "semanticType": "block", "label": "One",
                      "assurance": "conceptual"}],
        "relationships": [],
 "assumptions": [],
    }
    draft.update(overrides)
    return draft


class AttemptLogTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.service = DiagramCreationService()

    def _entries(self):
        return attempt_log.read(self.workspace / ".graphpilot")

    def test_a_successful_create_is_recorded(self):
        self.service.create(str(self.workspace), _draft("first"))

        entry, = self._entries()
        self.assertTrue(entry["accepted"])
        self.assertEqual(entry["diagram"], "first")
        self.assertEqual(entry["type"], "bdd_diagram")
        self.assertEqual(entry["findings"], [])
        self.assertEqual(entry["elements"], 1)

    def test_a_refusal_is_recorded_once_the_workspace_is_in_use(self):
        """The whole reason the log exists: a refusal leaves no other trace."""
        self.service.create(str(self.workspace), _draft("first"))

        bad = _draft("second")
        bad["elements"][0]["semanticType"] = "opaqueAction"
        with self.assertRaises(DraftRefused):
            self.service.create(str(self.workspace), bad)

        refused = [e for e in self._entries() if not e["accepted"]]
        self.assertEqual(len(refused), 1)
        self.assertTrue(
            any("semantic_type_unsupported" in f for f in refused[0]["findings"]),
            refused[0]["findings"],
        )

    def test_it_never_creates_the_folder_for_a_refusal(self):
        """A user whose first draft is rejected finds nothing in their repository.

        Two tests in `test_diagram_creation_service` assert the same line from the other
        side. It is worth holding: a tool that litters on failure is one people stop
        pointing at directories they care about.
        """
        bad = _draft("never-written")
        bad["elements"][0]["semanticType"] = "opaqueAction"
        with self.assertRaises(DraftRefused):
            self.service.create(str(self.workspace), bad)

        self.assertFalse((self.workspace / ".graphpilot").exists())

    def test_the_two_refusal_stages_stay_distinguishable(self):
        """"The shape was wrong" and "the citations were wrong" get fixed differently."""
        self.service.create(str(self.workspace), _draft("first"))
        source = self.workspace / "app.py"
        source.write_text("class Thing:\n    pass\n", encoding="utf-8")

        cited = _draft("cited")
        cited["authority"] = "as_implemented"
        cited["evidence"] = [{
            "id": "ev-one", "kind": "code",
            "locator": {"path": "app.py", "symbol": "Thing",
                        "lineRange": {"start": 1, "end": 9999}},
            "summary": "the Thing",
        }]
        cited["elements"][0].update(assurance="grounded", evidenceRefs=["ev-one"])
        with self.assertRaises(DraftRefused):
            self.service.create(str(self.workspace), cited)

        refused = [e for e in self._entries() if not e["accepted"]]
        self.assertTrue(
            any("evidence_unreadable" in f for entry in refused for f in entry["findings"])
        )

    def test_the_log_never_holds_the_draft_itself(self):
        """Codes and counts. A finding's message can quote the source it read, and a
        label can be anything the host wrote."""
        self.service.create(str(self.workspace), _draft("secretive", **{
            "elements": [{"id": "one", "semanticType": "block",
                          "label": "SUPERSECRETLABEL", "assurance": "conceptual"}],
        }))

        raw = (self.workspace / ".graphpilot" / attempt_log.FILENAME).read_text(encoding="utf-8")
        self.assertNotIn("SUPERSECRETLABEL", raw)

    def test_paths_are_shaped_so_repeat_refusals_group(self):
        """Ten refusals on ten elements are one rule, not ten strings."""
        self.assertEqual(
            attempt_log._shape("$.elements[3].assurance"), "$.elements[].assurance"
        )

    def test_a_taken_name_is_recorded_as_the_refusal_it_is(self):
        """`a5.f8`. `diagram_exists` raises before the write, so it was skipped — and run
        4 counted 12 attempts against 13 made. Short, in the flattering direction, which
        for a friction measurement is the worst direction: a host looping on taken names
        looked like a host that never failed."""
        self.service.create(str(self.workspace), _draft("taken"))
        with self.assertRaises(Exception):
            self.service.create(str(self.workspace), _draft("taken"))

        refused = [e for e in self._entries() if not e["accepted"]]
        self.assertEqual(len(refused), 1)
        self.assertTrue(any("diagram_exists" in f for f in refused[0]["findings"]))
        self.assertEqual(attempt_log.summarise(self._entries())["attempts"], 2)

    def test_a_warned_create_does_not_record_as_a_clean_one(self):
        """`a5.f8`, the second half. `findings` holds draft findings, so a create that
        warned recorded as `accepted: true, findings: []` and a later reader concluded it
        went perfectly. A corpus host reported exactly that about run 4's log."""
        long_label = "x" * 200
        self.service.create(str(self.workspace), _draft("wordy", **{
            "elements": [{"id": "one", "semanticType": "block", "label": long_label,
                          "assurance": "conceptual"}],
        }))

        entry, = self._entries()
        self.assertTrue(entry["accepted"])
        self.assertTrue(entry["warnings"], "an accepted create is not necessarily clean")
        self.assertIn("long_label", entry["warnings"])

    def test_a_clean_create_records_no_warnings(self):
        """The counterpart, so the field cannot become decorative.

        Needs two blocks and a relationship: a lone element earns `no_edges`, which is the
        structural critic working and this test's first fixture not being clean.
        """
        self.service.create(str(self.workspace), _draft("tidy", **{
            "elements": [
                {"id": "one", "semanticType": "block", "label": "One",
                 "assurance": "conceptual"},
                {"id": "two", "semanticType": "block", "label": "Two",
                 "assurance": "conceptual"},
            ],
            "relationships": [{
                "id": "one-has-two", "semanticType": "composition",
                "source": "one", "target": "two", "assurance": "conceptual",
            }],
        }))

        entry, = self._entries()
        self.assertEqual(entry["warnings"], [])

    def test_the_summary_is_the_number_a_corpus_run_wants(self):
        self.service.create(str(self.workspace), _draft("a"))
        bad = _draft("b")
        bad["elements"][0]["semanticType"] = "opaqueAction"
        with self.assertRaises(DraftRefused):
            self.service.create(str(self.workspace), bad)
        self.service.create(str(self.workspace), _draft("b"))

        summary = attempt_log.summarise(self._entries())

        self.assertEqual(summary["attempts"], 3)
        self.assertEqual(summary["accepted"], 2)
        self.assertEqual(summary["attemptsPerDiagram"], 1.5)
        self.assertTrue(summary["refusalsByRule"])

    def test_no_attempts_and_no_refusals_are_distinguishable(self):
        """They used to look the same, and one of them means the log is broken."""
        self.assertIsNone(attempt_log.summarise([]))
        self.service.create(str(self.workspace), _draft("clean"))
        self.assertEqual(attempt_log.summarise(self._entries())["refusalsByRule"], {})

    def test_a_broken_log_never_costs_a_diagram(self):
        """It sits on the create path, so it must never be the reason a create fails."""
        (self.workspace / ".graphpilot").mkdir()
        # A directory where the file should be: every write will raise.
        (self.workspace / ".graphpilot" / attempt_log.FILENAME).mkdir()

        result = self.service.create(str(self.workspace), _draft("resilient"))

        self.assertTrue(result.diagram_path.exists())
