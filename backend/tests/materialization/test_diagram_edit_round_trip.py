"""The edit round trip, end to end, against a diagram somebody has arranged.

This is the feature's reason to exist: a person moves blocks, renames one, adds a note, and
later asks the IDE for one more element. Re-creating would recompute every position, which
the person experiences as their work being destroyed.

Each test below is one of the proofs `03-geometry-and-merge.md` requires before a rule
ships. They use the real services rather than fixtures of the merge's own output, because
the failure that matters is a field nobody classified at all.
"""

import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.drafts.diagram_edit_service import DiagramEditService, EditRefused
from services.materialization.diagram_creation_service import DiagramCreationService
from services.materialization.diagram_update_service import (
    HISTORY_DEPTH,
    DiagramUpdateService,
    UpdateRefused,
)
from services.shared.workspace_storage_service import WorkspaceStorageService


def _draft(name="arranged", elements=None, relationships=None, requests=None):
    return {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": name,
        "diagramType": "bdd_diagram",
        "authority": "conceptual",
        "requests": requests or ["Draw the parts of a bicycle."],
        "elements": elements or [
            {"id": "bike", "semanticType": "block", "label": "Bicycle", "assurance": "conceptual"},
            {"id": "wheel", "semanticType": "block", "label": "Wheel", "assurance": "conceptual"},
            {"id": "frame", "semanticType": "block", "label": "Frame", "assurance": "conceptual"},
        ],
        "relationships": relationships if relationships is not None else [
            {"id": "wheel-bike", "semanticType": "composition", "source": "wheel",
             "target": "bike", "assurance": "conceptual"},
            {"id": "frame-bike", "semanticType": "composition", "source": "frame",
             "target": "bike", "assurance": "conceptual"},
        ],
    }


class EditRoundTripTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = self._tmp.name
        self.edits = DiagramEditService()
        self.updates = DiagramUpdateService()
        DiagramCreationService().create(self.workspace, _draft())
        self.storage = WorkspaceStorageService(self.workspace)
        self.path = self.storage.diagram_file_path("arranged")

    def _saved(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _arrange(self, **changes):
        """Stand in for a person using the editor: move things, type a description."""
        diagram = self._saved()
        for node in diagram["nodes"]:
            if node["id"] in changes:
                node.update(changes[node["id"]])
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")
        return diagram

    def _read_and_edit(self, mutate):
        result = self.edits.read(self.workspace, "arranged")
        draft = json.loads(result.draft_path.read_text(encoding="utf-8"))
        mutate(draft)
        return draft

    # ---- R1 and R5: nothing that exists moves -------------------------------------

    def test_a_persons_arrangement_survives_an_edit_that_never_mentions_it(self):
        """The whole feature. Three nodes dragged, then a host adds a fourth."""
        self._arrange(
            bike={"position": {"x": -400.0, "y": 250.0}},
            wheel={"position": {"x": -400.0, "y": 500.0}},
            frame={"position": {"x": -400.0, "y": 750.0}},
        )
        before = {node["id"]: node["position"] for node in self._saved()["nodes"]}

        def add_a_saddle(draft):
            draft["elements"].append({
                "id": "saddle", "semanticType": "block", "label": "Saddle",
                "assurance": "conceptual",
            })
            draft["relationships"].append({
                "id": "saddle-bike", "semanticType": "composition",
                "source": "saddle", "target": "bike", "assurance": "conceptual",
            })
            draft["requests"].append("Add the saddle.")

        self.updates.update(self.workspace, self._read_and_edit(add_a_saddle))

        after = {node["id"]: node["position"] for node in self._saved()["nodes"]}
        for node_id, position in before.items():
            self.assertEqual(after[node_id], position, f"{node_id} moved")
        self.assertIn("saddle", after)

    def test_a_relabel_keeps_the_position_it_had(self):
        self._arrange(wheel={"position": {"x": 900.0, "y": -120.0}})

        def rename(draft):
            for element in draft["elements"]:
                if element["id"] == "wheel":
                    element["label"] = "Front Wheel Assembly With A Long Name"
            draft["requests"].append("Rename the wheel.")

        self.updates.update(self.workspace, self._read_and_edit(rename))

        wheel = next(n for n in self._saved()["nodes"] if n["id"] == "wheel")
        self.assertEqual(wheel["position"], {"x": 900.0, "y": -120.0})

    def test_a_hand_resized_node_never_shrinks(self):
        """R2. Recomputing would undo a deliberate resize; carrying blindly would clip a
        longer label. Taking the larger does neither."""
        self._arrange(bike={"width": 640.0, "height": 400.0})

        def touch(draft):
            draft["requests"].append("Nothing structural.")

        self.updates.update(self.workspace, self._read_and_edit(touch))

        bike = next(n for n in self._saved()["nodes"] if n["id"] == "bike")
        self.assertGreaterEqual(bike["width"], 640.0)
        self.assertGreaterEqual(bike["height"], 400.0)

    def test_a_longer_label_grows_the_box_that_holds_it(self):
        """R2's other half, which nothing asserted for the life of the rule.

        `test_a_hand_resized_node_never_shrinks` above cannot fail: blind carry satisfies
        "never shrinks" trivially, because blind carry is what it does. The relabel test
        renames to a deliberately long string and then checks only the *position*. So the
        half of R2 that needs an implementation — "never clips" — was asserted by neither,
        and `grow_to_fit`, its only implementation, was wired to nothing and read as dead.

        Measured against the width the materializer computes for the same label on a
        create, so this tracks the sizing rule instead of hard-coding a pixel count.
        """
        long_label = "Front Wheel Assembly With A Very Long Name Indeed"
        reference = DiagramCreationService().create(
            self.workspace,
            _draft(name="reference", relationships=[], elements=[
                {"id": "wheel", "semanticType": "block", "label": long_label,
                 "assurance": "conceptual"},
            ]),
        )
        needed = next(
            node["width"]
            for node in json.loads(
                self.storage.diagram_file_path("reference").read_text(encoding="utf-8")
            )["nodes"]
            if node["id"] == "wheel"
        )
        self.assertGreater(needed, 0.0, "reference create produced no width")

        def rename(draft):
            for element in draft["elements"]:
                if element["id"] == "wheel":
                    element["label"] = long_label
            draft["requests"].append("Rename the wheel to something much longer.")

        self.updates.update(self.workspace, self._read_and_edit(rename))

        wheel = next(n for n in self._saved()["nodes"] if n["id"] == "wheel")
        self.assertGreaterEqual(
            wheel["width"], needed,
            "the box kept its old width, so the longer label is clipped inside it",
        )
        self.assertIsNotNone(reference)

    def test_a_box_that_grows_into_its_neighbour_says_so(self):
        """R2's third clause, and the reason the second one is safe to ship.

        R2 grows the box and R5 forbids moving anything to make room, so the two rules
        together can draw one element on top of another. Growing silently is worse than
        leaving the label clipped: a clipped label looks wrong, whereas two boxes drawn
        over each other look deliberate. The design's answer is a warning, and this is it.

        Caught by rendering the picture, not by reading the test — the grow passed its own
        assertion while putting `wheel` straight through `frame`.
        """
        self._arrange(
            wheel={"position": {"x": 0.0, "y": 0.0}, "width": 160.0},
            frame={"position": {"x": 200.0, "y": 0.0}, "width": 160.0},
        )

        def rename(draft):
            for element in draft["elements"]:
                if element["id"] == "wheel":
                    element["label"] = "Front Wheel Assembly With A Very Long Name Indeed"
            draft["requests"].append("Rename the wheel to something much longer.")

        result = self.updates.update(self.workspace, self._read_and_edit(rename))

        overlap = [w for w in result.warnings if w["code"] == "layout_overlap"]
        self.assertTrue(overlap, f"grew into a neighbour without saying so: {result.warnings}")
        self.assertIn(
            ["frame", "wheel"], overlap[0]["pairs"],
            "the warning did not name the pair that collided",
        )

    # ---- class 2: what the draft cannot say ---------------------------------------

    def test_a_typed_description_survives_a_host_edit_that_never_mentions_it(self):
        """`data.description` has no draft field, so the host never sees it. It must come
        back by id, exactly like a position — the two are the same kind of thing."""
        diagram = self._saved()
        for node in diagram["nodes"]:
            if node["id"] == "frame":
                node["data"]["description"] = "Reynolds 853, checked by Priya."
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        def rename(draft):
            for element in draft["elements"]:
                if element["id"] == "frame":
                    element["label"] = "Steel Frame"
            draft["requests"].append("Rename the frame.")

        self.updates.update(self.workspace, self._read_and_edit(rename))

        frame = next(n for n in self._saved()["nodes"] if n["id"] == "frame")
        self.assertEqual(frame["data"]["description"], "Reynolds 853, checked by Priya.")
        self.assertEqual(frame["data"]["label"], "Steel Frame")

    def test_the_viewport_and_created_at_are_carried(self):
        created_at = self._saved()["metadata"]["createdAt"]
        diagram = self._saved()
        diagram["viewport"] = {"x": 42.0, "y": -17.0, "zoom": 1.75}
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        self.updates.update(self.workspace, self._read_and_edit(
            lambda d: d["requests"].append("Touch it.")))

        saved = self._saved()
        self.assertEqual(saved["viewport"], {"x": 42.0, "y": -17.0, "zoom": 1.75})
        self.assertEqual(saved["metadata"]["createdAt"], created_at)
        self.assertNotEqual(saved["metadata"]["updatedAt"], created_at)

    def test_authoring_only_ratchets(self):
        """Once a person has saved from the editor the diagram is `custom` forever. A later
        host write does not reset it, because the human work it records did not stop being
        true."""
        diagram = self._saved()
        diagram["metadata"]["authoring"] = "custom"
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        self.updates.update(self.workspace, self._read_and_edit(
            lambda d: d["requests"].append("Touch it.")))

        self.assertEqual(self._saved()["metadata"]["authoring"], "custom")

    # ---- removal is visible --------------------------------------------------------

    def test_an_element_left_out_is_deleted_and_named_in_the_result(self):
        def drop_the_frame(draft):
            draft["elements"] = [e for e in draft["elements"] if e["id"] != "frame"]
            draft["relationships"] = [
                r for r in draft["relationships"] if r["id"] != "frame-bike"
            ]
            draft["requests"].append("Drop the frame.")

        result = self.updates.update(self.workspace, self._read_and_edit(drop_the_frame))

        self.assertEqual([item.id for item in result.removed], ["frame"])
        self.assertEqual(result.removed[0].label, "Frame")
        self.assertNotIn("frame", {n["id"] for n in self._saved()["nodes"]})

    def test_a_person_drawn_element_is_named_as_theirs_when_removed(self):
        """Nothing is exempt from removal — *"delete that note I added"* is an ordinary
        thing to ask. So the protection is visibility, not refusal."""
        diagram = self._saved()
        diagram["nodes"].append({
            "id": "note-1", "type": "gpNode", "position": {"x": 0, "y": 900},
            "width": 200, "height": 80,
            "data": {"label": "Check with Priya", "semanticType": "note"},
            "origin": {"assurance": "user", "evidenceRefs": [], "assumptionRefs": [],
                       "schemaRules": [], "rationale": "Added in the editor."},
        })
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        def drop_the_note(draft):
            draft["elements"] = [e for e in draft["elements"] if e["id"] != "note-1"]
            draft["requests"].append("Remove the note.")

        result = self.updates.update(self.workspace, self._read_and_edit(drop_the_note))

        self.assertEqual(result.removed[0].as_dict(), {
            "id": "note-1", "label": "Check with Priya", "drawnBy": "user",
        })

    def test_a_bend_survives_unless_the_edge_is_rewired(self):
        """A person bent an edge to avoid something on the path between two nodes. Change
        an endpoint and those waypoints describe a route that no longer exists, so they
        go — but the preference for orthogonal is about the edge rather than the path it
        took, so the mode stays. An edge nobody rewired keeps its bend exactly."""
        diagram = self._saved()
        for edge in diagram["edges"]:
            edge["route"] = {
                "mode": "orthogonal",
                "waypoints": [{"x": 10.0, "y": 20.0}, {"x": 30.0, "y": 40.0}],
            }
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        def rewire(draft):
            for relationship in draft["relationships"]:
                if relationship["id"] == "frame-bike":
                    relationship["target"] = "wheel"
            draft["requests"].append("Hang the frame off the wheel instead.")

        self.updates.update(self.workspace, self._read_and_edit(rewire))

        routes = {edge["id"]: edge.get("route") for edge in self._saved()["edges"]}
        self.assertEqual(routes["frame-bike"], {"mode": "orthogonal"},
                         "a rewired edge kept waypoints describing a path that is gone")
        self.assertEqual(
            routes["wheel-bike"],
            {"mode": "orthogonal",
             "waypoints": [{"x": 10.0, "y": 20.0}, {"x": 30.0, "y": 40.0}]},
            "an untouched bend was discarded",
        )

    def test_a_relationship_drawn_in_the_editor_can_be_read_and_written_back(self):
        """The editor names a hand-drawn edge `edge_<source>_<target>_<uuid>`.

        The canonical schema pins no id pattern and stored it happily; the draft schema
        insisted on a lowercase hyphenated slug. So the projection produced a document
        that failed its own validation, and **a host could never edit a diagram again once
        somebody had drawn one edge on it** — precisely the diagrams the edit path exists
        for. Found by a person drawing an edge, not by any test here.

        The id is the key the merge preserves geometry on, so the projection cannot tidy
        it on the way past. It has to be accepted as it is.
        """
        diagram = self._saved()
        diagram["edges"].append({
            "id": "edge_wheel_frame_1dcdbfcb-8260-4584-aabd-86899b43c23d",
            "source": "wheel", "target": "frame",
            "data": {"semanticType": "association"},
            "route": {"mode": "orthogonal",
                      "targetAnchor": {"side": "right", "offset": 0.38}},
            "origin": {"assurance": "user", "evidenceRefs": [], "assumptionRefs": [],
                       "schemaRules": [], "rationale": "Drawn in the editor."},
        })
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        self.updates.update(self.workspace, self._read_and_edit(
            lambda d: d["requests"].append("Something unrelated.")))

        drawn = next(
            e for e in self._saved()["edges"]
            if e["id"].startswith("edge_wheel_frame_")
        )
        self.assertEqual(drawn["origin"]["assurance"], "user")
        # Route is class 2 and the endpoints did not change, so the person's anchor is
        # carried across untouched rather than recomputed.
        self.assertEqual(drawn["route"]["targetAnchor"], {"side": "right", "offset": 0.38})

    def test_a_person_drawn_element_survives_an_edit_that_keeps_it(self):
        """It comes back through the projection as `user`, and the write accepts it — the
        one way that value legitimately appears in a draft."""
        diagram = self._saved()
        diagram["nodes"].append({
            "id": "note-1", "type": "gpNode", "position": {"x": 0, "y": 900},
            "width": 200, "height": 80,
            "data": {"label": "Check with Priya", "semanticType": "note"},
            "origin": {"assurance": "user", "evidenceRefs": [], "assumptionRefs": [],
                       "schemaRules": [], "rationale": "Added in the editor."},
        })
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        self.updates.update(self.workspace, self._read_and_edit(
            lambda d: d["requests"].append("Leave the note alone.")))

        note = next(n for n in self._saved()["nodes"] if n["id"] == "note-1")
        self.assertEqual(note["origin"]["assurance"], "user")
        self.assertEqual(note["position"], {"x": 0, "y": 900})

    # ---- the basis, and the append rule --------------------------------------------

    def test_a_write_based_on_a_stale_read_is_refused(self):
        """Somebody saved in the browser between the read and the write. Proceeding would
        delete everything they added, because a whole-state write omits what it never saw.
        """
        draft = self._read_and_edit(lambda d: d["requests"].append("Add something."))
        diagram = self._saved()
        diagram["nodes"].append({
            "id": "theirs", "type": "gpNode", "position": {"x": 0, "y": 1200},
            "width": 160, "height": 60,
            "data": {"label": "Added in the browser", "semanticType": "block"},
            "origin": {"assurance": "user", "evidenceRefs": [], "assumptionRefs": [],
                       "schemaRules": [], "rationale": "Added in the editor."},
        })
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        with self.assertRaises(UpdateRefused) as caught:
            self.updates.update(self.workspace, draft)

        self.assertEqual(caught.exception.code, "basis_stale")
        self.assertIn("theirs", {n["id"] for n in self._saved()["nodes"]})

    def test_a_draft_with_no_basis_cannot_update(self):
        """A host that authored from nothing has not read the current file."""
        draft = self._read_and_edit(lambda d: d["requests"].append("x"))
        del draft["basis"]

        with self.assertRaises(UpdateRefused) as caught:
            self.updates.update(self.workspace, draft)

        self.assertEqual(caught.exception.code, "basis_stale")

    def test_an_edit_must_append_exactly_one_ask(self):
        draft = self._read_and_edit(lambda d: None)

        with self.assertRaises(UpdateRefused) as caught:
            self.updates.update(self.workspace, draft)

        self.assertEqual(caught.exception.code, "requests_invalid")

    def test_rewriting_an_earlier_ask_is_refused(self):
        """The log is the record of why the diagram looks the way it does. Editing it is
        the one thing it exists to prevent."""
        def rewrite(draft):
            draft["requests"][0] = "Something the user never said."
            draft["requests"].append("And now this.")

        with self.assertRaises(UpdateRefused) as caught:
            self.updates.update(self.workspace, self._read_and_edit(rewrite))

        self.assertEqual(caught.exception.code, "requests_invalid")
        self.assertIn("unchanged", caught.exception.findings[0].message)

    def test_the_ask_is_stamped_into_the_diagram(self):
        self.updates.update(self.workspace, self._read_and_edit(
            lambda d: d["requests"].append("Add the saddle.")))

        requests = self._saved()["metadata"]["requests"]
        self.assertEqual([entry["text"] for entry in requests][-1], "Add the saddle.")
        self.assertTrue(all(entry["at"] for entry in requests))

    # ---- the working file ----------------------------------------------------------

    def test_a_successful_write_removes_the_working_file(self):
        result = self.edits.read(self.workspace, "arranged")
        self.assertTrue(result.draft_path.is_file())

        draft = json.loads(result.draft_path.read_text(encoding="utf-8"))
        draft["requests"].append("Done.")
        self.updates.update(self.workspace, draft)

        self.assertFalse(result.draft_path.exists())

    def test_a_refused_write_keeps_it_so_the_edit_is_not_lost(self):
        result = self.edits.read(self.workspace, "arranged")
        draft = json.loads(result.draft_path.read_text(encoding="utf-8"))
        draft["elements"][0]["label"] = ""

        with self.assertRaises(UpdateRefused):
            self.updates.update(self.workspace, draft)

        self.assertTrue(result.draft_path.is_file())

    def test_reading_twice_overwrites_rather_than_accumulating(self):
        first = self.edits.read(self.workspace, "arranged")
        second = self.edits.read(self.workspace, "arranged")

        self.assertEqual(first.draft_path, second.draft_path)
        self.assertNotEqual(first.basis["readAt"], second.basis["readAt"])

    # ---- history -------------------------------------------------------------------

    def test_the_previous_version_is_kept_before_it_is_replaced(self):
        before = self._saved()

        result = self.updates.update(self.workspace, self._read_and_edit(
            lambda d: d["requests"].append("Change it.")))

        self.assertIsNotNone(result.history_path)
        self.assertEqual(
            json.loads(result.history_path.read_text(encoding="utf-8"))["nodes"],
            before["nodes"],
        )

    def test_history_keeps_the_last_three_and_no_more(self):
        for index in range(HISTORY_DEPTH + 2):
            self.updates.update(self.workspace, self._read_and_edit(
                lambda d, i=index: d["requests"].append(f"Edit {i}.")))

        folder = Path(self.workspace) / ".graphpilot" / "history" / "arranged"
        self.assertEqual(len(list(folder.glob("*.gp.json"))), HISTORY_DEPTH)

    # ---- what cannot be edited from the IDE ----------------------------------------

    def test_a_crossed_diagram_says_so_rather_than_failing_a_schema_check(self):
        """Mixing element types in the editor flips a diagram to `custom`, and the draft's
        enum has no way to say that. Falling through to a schema error would leave a host
        guessing at a rule nothing told it about."""
        diagram = self._saved()
        diagram["diagramType"] = "custom"
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        with self.assertRaises(EditRefused) as caught:
            self.edits.read(self.workspace, "arranged")

        self.assertEqual(caught.exception.code, "diagram_crossed")
        self.assertIn("browser", caught.exception.message)

    def test_reading_a_diagram_that_is_not_there_says_what_is(self):
        """`diagram_read` needs a name and nothing on the surface hands one out, so an
        audit had to list the workspace folder to find it — step one of the edit path was
        unreachable through the tools. The refusal answers the question instead."""
        with self.assertRaises(EditRefused) as caught:
            self.edits.read(self.workspace, "no-such-thing")

        self.assertEqual(caught.exception.code, "diagram_not_found")
        self.assertIn("arranged", caught.exception.message)
        self.assertEqual(caught.exception.details["available"], ["arranged"])

    # ---- what a removal costs, said out loud ---------------------------------------

    def test_removing_an_element_reports_the_prose_that_goes_with_it(self):
        """The audit's best finding. A deleted node carried a hand-typed description —
        *"Reynolds 853. Confirmed with Priya, Aug 2026."* — a decision record naming a
        colleague. The host reported "removed Frame" and could not have done better: the
        description is deliberately absent from the draft, so nothing in its
        read-edit-write loop had ever shown it the text existed.

        Removal is visible rather than forbidden precisely so a person can see what went.
        An id and a label do not achieve that when the thing lost was a sentence.
        """
        diagram = self._saved()
        for node in diagram["nodes"]:
            if node["id"] == "frame":
                node["data"]["description"] = "Reynolds 853. Confirmed with Priya, Aug 2026."
        self.path.write_text(json.dumps(diagram, indent=2), encoding="utf-8")

        def drop_the_frame(draft):
            draft["elements"] = [e for e in draft["elements"] if e["id"] != "frame"]
            draft["relationships"] = [
                r for r in draft["relationships"] if r["id"] != "frame-bike"
            ]
            draft["requests"].append("Drop the frame.")

        result = self.updates.update(self.workspace, self._read_and_edit(drop_the_frame))

        self.assertEqual(
            result.removed[0].as_dict()["lostText"],
            ["Reynolds 853. Confirmed with Priya, Aug 2026."],
        )

    def test_a_removal_with_no_human_prose_says_nothing_extra(self):
        """Noise in the common case would teach a reader to skim the important one."""
        def drop_the_frame(draft):
            draft["elements"] = [e for e in draft["elements"] if e["id"] != "frame"]
            draft["relationships"] = [
                r for r in draft["relationships"] if r["id"] != "frame-bike"
            ]
            draft["requests"].append("Drop the frame.")

        result = self.updates.update(self.workspace, self._read_and_edit(drop_the_frame))

        self.assertNotIn("lostText", result.removed[0].as_dict())

    # ---- the picture is redrawn ----------------------------------------------------

    def test_the_svg_is_redrawn_so_it_does_not_show_the_deleted_element(self):
        """An audit found the saved diagram updated and its SVG two minutes stale, still
        showing the part that had just been removed and missing the one just added. The
        picture is the artifact a person actually opens, and nothing in the tool output
        said it had not been touched."""
        def swap(draft):
            draft["elements"] = [e for e in draft["elements"] if e["id"] != "frame"]
            draft["relationships"] = [
                r for r in draft["relationships"] if r["id"] != "frame-bike"
            ]
            draft["elements"].append({
                "id": "saddle", "semanticType": "block", "label": "Saddle",
                "assurance": "conceptual",
            })
            draft["requests"].append("Frame out, saddle in.")

        result = self.updates.update(self.workspace, self._read_and_edit(swap))

        self.assertIsNotNone(result.svg_path)
        svg = result.svg_path.read_text(encoding="utf-8")
        self.assertIn("Saddle", svg)
        self.assertNotIn("Frame", svg)

    def test_updating_a_diagram_that_does_not_exist_points_at_create(self):
        draft = _draft(name="never-made", requests=["x"])
        draft["basis"] = {"diagram": "sha256:" + "0" * 64, "readAt": "now"}

        with self.assertRaises(UpdateRefused) as caught:
            self.updates.update(self.workspace, draft)

        self.assertEqual(caught.exception.code, "diagram_not_found")
        self.assertIn("diagram_create", caught.exception.message)
