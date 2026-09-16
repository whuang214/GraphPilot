"""The `edited` pool: a before/after pair per diagram type, replayed from a scenario.

The pool exists because no single picture answers the question an edit raises. What a
reviewer needs to see is two diagrams and the sentence between them — and the sentence has
to be computed from the pair rather than authored, or it becomes a claim nobody checks.
"""

import json

from django.test import SimpleTestCase

from operations.edited_examples import load_scenario, replay
from operations.management.commands.render_example_gallery import (
    POOLS,
    REGEN_CHOICES,
    _blueprints_dir,
)
from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.drafts.draft_validation_service import DraftValidationService


def _scenarios():
    for diagram_type in SUPPORTED_DIAGRAM_TYPES:
        base = _blueprints_dir() / diagram_type / "examples" / "edited"
        for path in sorted(base.glob("*/scenario.json")):
            yield diagram_type, path.parent


class TheEditedPoolIsWiredUpTests(SimpleTestCase):
    def test_the_pool_and_its_regen_flag_exist(self):
        self.assertIn("edited", POOLS)
        self.assertIn("edited", REGEN_CHOICES)

    def test_every_diagram_type_has_one(self):
        """Two per type, because the geometry that matters differs by notation: a use case
        has containment, an activity has a single chain, a BDD diagram has neither."""
        covered = {diagram_type for diagram_type, _ in _scenarios()}

        self.assertEqual(covered, set(SUPPORTED_DIAGRAM_TYPES))

    def test_the_pool_covers_every_kind_of_edit(self):
        """Add and remove are the obvious two and the least likely to break something.

        The operations that quietly destroy work are the ones that change an existing
        element: a relationship end, an endpoint, or an edit that touches nothing a person
        drew. Each has a scenario, so a regression shows up as a changed picture.
        """
        operations = set()
        for _, example_dir in _scenarios():
            edit = (load_scenario(example_dir) or {}).get("edit") or {}
            operations.update(key for key in edit if key != "request")

        self.assertEqual(
            operations,
            {"addElements", "addRelationships", "relabel", "remove", "change"},
        )

    def test_each_scenario_says_what_it_is_showing(self):
        """A pair with no stated point is two pictures a reviewer has to reverse-engineer."""
        for diagram_type, example_dir in _scenarios():
            with self.subTest(example=example_dir.name):
                self.assertTrue((load_scenario(example_dir) or {}).get("shows"))


class ReplayingAScenarioTests(SimpleTestCase):
    """Both halves are generated, so the pair is evidence about the code as it is today.

    A stored before/after would only prove that somebody once saw it work.
    """

    def test_every_scenario_replays_and_holds_the_arrangement(self):
        validation = DiagramValidationService()
        for diagram_type, example_dir in _scenarios():
            with self.subTest(example=example_dir.name):
                pair = replay(load_scenario(example_dir))

                self.assertEqual(
                    pair.moved, (),
                    f"{example_dir.name}: an edit moved something the host never mentioned",
                )
                self.assertTrue(pair.held, "nothing survived the edit at all")
                self.assertTrue(validation.validate(pair.after).valid)

    def test_the_committed_pair_matches_what_replaying_produces(self):
        """`--regen edited` is what writes these, and a stale pair on the page is a page
        that says the code does something it no longer does."""
        for diagram_type, example_dir in _scenarios():
            with self.subTest(example=example_dir.name):
                pair = replay(load_scenario(example_dir))
                for name, produced in (("before.gp.json", pair.before),
                                       ("output.gp.json", pair.after)):
                    committed = json.loads(
                        (example_dir / name).read_text(encoding="utf-8")
                    )
                    # Timestamps are the one thing that legitimately differs run to run.
                    for document in (committed, produced):
                        metadata = document.get("metadata") or {}
                        for stamp in ("createdAt", "updatedAt"):
                            metadata.pop(stamp, None)
                        for entry in metadata.get("requests") or ():
                            entry.pop("at", None)
                    self.assertEqual(committed, produced, f"{example_dir.name}/{name}")

    def test_a_removal_scenario_reports_the_prose_that_went_with_it(self):
        """The audit finding this pool exists to keep visible: a deleted element can carry
        text a person typed, which no draft shows and nothing else would surface."""
        example = next(
            d for _, d in _scenarios() if d.name == "onboarding-trimmed"
        )

        pair = replay(load_scenario(example))

        self.assertEqual([item["id"] for item in pair.removed], ["fax"])
        self.assertIn("Legal asked for this", pair.removed[0]["lostText"][0])

    def test_what_the_scenario_submits_is_a_draft_a_host_could_have_written(self):
        """The scenario's `edit` block is fixture notation — `remove`, `relabel`, `change`
        — and the product has no such concept. A host is handed a whole draft, edits the
        file, and sends the whole thing back.

        So the thing worth checking is not the shorthand but what it produces: for every
        scenario, the submitted document must be a draft `diagram_update` would accept from
        a real host. Same `basis` as the read, exactly one ask appended, and the earlier
        ones unchanged.
        """
        for _, example_dir in _scenarios():
            with self.subTest(example=example_dir.name):
                pair = replay(load_scenario(example_dir))

                self.assertEqual(pair.submitted["basis"], pair.projected["basis"],
                                 "basis is stamped by the read and never authored")
                self.assertEqual(
                    len(pair.submitted["requests"]), len(pair.projected["requests"]) + 1
                )
                self.assertEqual(
                    pair.submitted["requests"][:-1], pair.projected["requests"],
                    "an earlier ask was rewritten",
                )
                self.assertEqual(
                    pair.submitted["requests"][-1],
                    (load_scenario(example_dir)["edit"])["request"],
                )

    def test_the_submitted_draft_is_validated_by_the_same_rules_a_host_faces(self):
        """If it would be refused from a host, the example is not evidence of anything."""
        service = DraftValidationService()
        for _, example_dir in _scenarios():
            with self.subTest(example=example_dir.name):
                result = service.validate(replay(load_scenario(example_dir)).submitted)
                self.assertTrue(
                    result.valid,
                    [f"{f.code} {f.path}" for f in result.findings][:4],
                )

    def test_both_drafts_are_written_out_beside_the_diagrams(self):
        """A reviewer cannot tell whether a host authored a change correctly from two
        pictures. The submitted draft is the artifact that answers it."""
        for _, example_dir in _scenarios():
            with self.subTest(example=example_dir.name):
                for name in ("read.draft.json", "submitted.draft.json",
                             "before.gp.json", "output.gp.json"):
                    self.assertTrue((example_dir / name).is_file(), name)

    def test_changing_a_relationship_end_keeps_the_ends_it_did_not_touch(self):
        """The projection read ends from the wrong level and dropped every role and
        multiplicity on every edge. Nothing failed, because no test compared them."""
        example = next(d for _, d in _scenarios() if d.name == "catalogue-ends")

        pair = replay(load_scenario(example))

        ends = {edge["id"]: (edge.get("data") or {}) for edge in pair.after["edges"]}
        self.assertEqual(
            ends["products-in-catalogue"]["sourceEnd"],
            {"role": "products", "multiplicity": {"lower": 0, "upper": "*"}},
            "an end nobody mentioned was changed",
        )
        self.assertEqual(
            ends["variants-of-product"]["sourceEnd"]["multiplicity"],
            {"lower": 1, "upper": "*"},
        )
        self.assertEqual(
            ends["product-supplier"]["targetEnd"],
            {"role": "suppliedBy", "multiplicity": {"lower": 1, "upper": 1},
             "navigable": True},
        )

    def test_rewiring_an_edge_leaves_every_other_edge_alone(self):
        """The scenario used to hand-bend these two edges to show a bend surviving. It was
        rebuilt: the bends were coordinates invented without looking at the drawing, and
        once fan-out stopped adding its own, the honest picture has none. Route carrying is
        checked precisely in `test_diagram_edit_round_trip` instead of by eye here.
        """
        example = next(d for _, d in _scenarios() if d.name == "refund-rewired")

        pair = replay(load_scenario(example))

        before = {edge["id"]: edge for edge in pair.before["edges"]}
        for edge in pair.after["edges"]:
            was = before.get(edge["id"])
            if was is None or edge["id"] == "e6":
                continue
            with self.subTest(edge=edge["id"]):
                self.assertEqual(edge.get("route"), was.get("route"))
                self.assertEqual(edge["target"], was["target"])
        rewired = next(e for e in pair.after["edges"] if e["id"] == "e6")
        self.assertEqual(rewired["target"], "done")

    def test_something_a_person_drew_survives_an_unrelated_edit(self):
        """It reaches the draft as `user`, which a host may never author, and is written
        straight back. Carrying one is the only way that value legitimately appears."""
        example = next(d for _, d in _scenarios() if d.name == "kiosk-note")

        pair = replay(load_scenario(example))

        note = next(n for n in pair.after["nodes"] if n["id"] == "note-cash")
        was = next(n for n in pair.before["nodes"] if n["id"] == "note-cash")
        self.assertEqual(note["origin"]["assurance"], "user")
        self.assertEqual(note["position"], was["position"])
        self.assertEqual(note["data"]["label"], was["data"]["label"])
        link = next(e for e in pair.after["edges"] if e["id"] == "note-cash-pay")
        self.assertEqual(link["origin"]["assurance"], "user")

    def test_a_new_child_lands_inside_its_parent(self):
        """The use-case scenario exists for this: its only neighbour is an actor outside
        the boundary, so proximity and containment disagree and containment has to win.

        **A child's `position` is relative to its parent**, and the first version of this
        test compared a relative child against an absolute parent. Both numbers happened
        to satisfy the inequality, the test passed, and the new use case was drawn well
        outside the boundary — caught only by looking at the picture on the page.

        So the check is stated the way the file means it: a child is inside its parent when
        its own box, measured from the parent's own origin, fits within the parent's size.
        """
        example = next(d for _, d in _scenarios() if d.name == "portal-export")

        after = replay(load_scenario(example)).after

        nodes = {node["id"]: node for node in after["nodes"]}
        child, parent = nodes["export"], nodes["portal"]
        self.assertEqual(child.get("parentId"), "portal")
        self.assertGreaterEqual(child["position"]["x"], 0)
        self.assertGreaterEqual(child["position"]["y"], 0)
        self.assertLessEqual(child["position"]["x"] + child["width"], parent["width"])
        self.assertLessEqual(child["position"]["y"] + child["height"], parent["height"])

    def test_every_child_of_every_scenario_stays_inside_its_parent(self):
        """Not just the one this scenario was written for. Containment is the rule most
        likely to be broken by a change to placement, and it is cheap to check everywhere.
        """
        for diagram_type, example_dir in _scenarios():
            after = replay(load_scenario(example_dir)).after
            nodes = {node["id"]: node for node in after["nodes"]}
            for node in after["nodes"]:
                parent = nodes.get(node.get("parentId") or "")
                if parent is None:
                    continue
                with self.subTest(example=example_dir.name, node=node["id"]):
                    self.assertGreaterEqual(node["position"]["x"], 0)
                    self.assertGreaterEqual(node["position"]["y"], 0)
                    self.assertLessEqual(
                        node["position"]["x"] + (node.get("width") or 0), parent["width"]
                    )
                    self.assertLessEqual(
                        node["position"]["y"] + (node.get("height") or 0), parent["height"]
                    )
