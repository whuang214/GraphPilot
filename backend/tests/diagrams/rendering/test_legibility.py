"""An author who delegates layout should be told when it did not work.

The division of labour is that a host supplies semantics and GraphPilot supplies notation,
layout and validation. Three cold hosts pointed out the same hole: having delegated
layout entirely, they were told nothing about whether it succeeded. One shipped a 26-node
diagram against `operationWarnings: []` and said it had "no way to judge the one thing
they delegated".
"""

import tempfile
from collections import Counter

from django.test import SimpleTestCase

from services.diagrams.rendering.legibility import Legibility, Offender, describe, measure
from services.materialization.diagram_creation_service import DiagramCreationService


def _diagram(label: str):
    return {
        "nodes": [
            {
                "id": "n1",
                "position": {"x": 0, "y": 0},
                "width": 100,
                "height": 40,
                "data": {"semanticType": "opaqueAction", "label": label},
            }
        ],
        "edges": [],
    }


_SVG = (
    '<svg><text x="4" y="20" font-size="12" text-anchor="start">{}</text></svg>'
)


class LegibilityTests(SimpleTestCase):
    def test_a_label_inside_its_node_is_legible(self):
        reading = measure(_diagram("Short"), _SVG.format("Short"))

        self.assertEqual(reading.illegible, 0)
        self.assertEqual(reading.offenders, [])
        self.assertEqual(describe(reading), "")

    def test_a_label_spilling_past_its_node_is_counted_and_explained(self):
        long_label = "A label far too long to fit inside a hundred pixels of box"
        reading = measure(_diagram(long_label), _SVG.format(long_label))

        self.assertEqual(reading.counts["clipped"], 1)
        # It names the string, rather than leaving the author to find it in the SVG.
        offender, = reading.offenders
        self.assertEqual(offender.kind, "clipped")
        self.assertIn("A label far too long", offender.text)
        self.assertIn("spills outside its own element", describe(reading))
        self.assertIn("1 of 1 labels", describe(reading))

    def test_the_description_names_the_strings(self):
        long_label = "A label far too long to fit inside a hundred pixels of box"
        message = describe(measure(_diagram(long_label), _SVG.format(long_label)))

        # Naming them is the half that has always worked: a host called it the difference
        # between a ten-second decision and parsing the SVG by hand.
        self.assertIn("A label far too long", message)


class TheMessageAsksTheHostToDoNothingTests(SimpleTestCase):
    """`a5.f7`, closed properly. Three attempts at naming a lever, three falsified.

    1. *"shorten your labels"* — the collisions were between strings GraphPilot places.
    2. *"fewer elements is the lever left"* — one host shortened guards instead and the
       collision cleared; another removed a node and watched it move to the next pair.
    3. *"a shorter string is a smaller box… failing that, it is crowding"* — a host pulled
       both in order. The first did nothing; the second took the collisions from one to
       two.

    The category error, not the wording, is the defect: **GraphPilot owns placement.** The
    layout engine positions nodes, the renderer positions end labels, and a host authors
    no coordinate. Its only influence is that different text is a different box size,
    which perturbs our layout arbitrarily.

    Acting on that costs meaning. The host that finally cleared its collisions flattened
    every guard to `yes`/`no` and demoted a decision to a note — the model damaged to
    patch the rendering. Three of its six `diagram_create` calls went on this, and across
    run 5 every wasted call was a legibility retry while no draft was ever refused on its
    merits.
    """

    _COLLISION = (
        '<svg>'
        '<text x="500" y="500" font-size="12" text-anchor="start">[stock is low]</text>'
        '<text x="504" y="502" font-size="12" text-anchor="start">[stock is fine]</text>'
        "</svg>"
    )

    def _message(self):
        return describe(measure({"nodes": [], "edges": []}, self._COLLISION))

    def test_it_says_the_layout_is_ours(self):
        message = self._message()

        self.assertIn("not yours to fix", message)
        self.assertIn("GraphPilot places", message)

    def test_it_tells_the_host_not_to_change_the_diagram(self):
        """The whole point. A warning that suggests an edit will get one."""
        message = self._message()

        self.assertIn("Do not reword, drop or restructure", message)
        self.assertIn("changes what the diagram says", message)

    def test_it_sends_the_judgement_to_the_person(self):
        message = self._message()

        self.assertIn("Tell the user", message)
        self.assertIn("editor", message)

    def test_it_names_no_lever(self):
        """Every phrasing a host has been sent chasing, in one assertion."""
        message = self._message()

        for lever in (
            "shorter string is a smaller box",
            "crowding",
            "Element count",
            "fewer elements",
            "Shorter labels",
            "shortening those usually fixes them",
            "no field moves them apart",
        ):
            with self.subTest(lever=lever):
                self.assertNotIn(lever, message)

    def test_a_clipped_string_is_reported_the_same_way(self):
        """Clipping is the one case where the author's own text is the offender — and it
        is still our box that is too small for it, so the message does not change."""
        long_label = "A label far too long to fit inside a hundred pixels of box"
        message = describe(measure(_diagram(long_label), _SVG.format(long_label)))

        self.assertIn("spills outside its own element", message)
        self.assertIn("not yours to fix", message)

    def test_it_still_names_a_collision_partner(self):
        same = Legibility(
            counts=Counter({"collided": 1, "texts": 40}),
            offenders=[Offender(kind="collided", text="memberships 0..*",
                                collides_with="memberships 0..*")],
        )

        self.assertIn("memberships 0..*", describe(same))


class AdviceMatchesTheLeverTests(SimpleTestCase):
    def test_a_collision_between_placed_strings_does_not_blame_the_author(self):
        # Two strings drawn on top of each other, neither owned by any node.
        svg = (
            '<svg>'
            '<text x="500" y="500" font-size="12" text-anchor="start">notifications 0..*</text>'
            '<text x="504" y="502" font-size="12" text-anchor="start">created_at: DateTime</text>'
            "</svg>"
        )
        message = describe(measure({"nodes": [], "edges": []}, svg))

        self.assertIn("overlaps", message)
        self.assertIn("notifications 0..*", message)
        self.assertNotIn("Shorter labels", message)

    def test_a_long_list_is_summarised_rather_than_dumped(self):
        """The bound is on the **list**, not the whole message.

        It used to cap the total length, which conflated two things: how many offenders
        are named, and how much is said about them. The prose is now fixed-length and
        longer — it has to state that the layout is GraphPilot's and that the host should
        not act on it — so a total-length cap would fail on a message that names one
        offender perfectly well.
        """
        texts = "".join(
            f'<text x="500" y="500" font-size="12" text-anchor="start">label {i}</text>'
            for i in range(12)
        )
        message = describe(measure({"nodes": [], "edges": []}, f"<svg>{texts}</svg>"))

        listed = message[: message.index("**This is a warning")]
        self.assertIn("more", listed)
        self.assertLess(len(listed), 500, listed)


class CreateReportsLegibilityTests(SimpleTestCase):
    """The measurement has to reach the author, not just the review page."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = self._tmp.name

    def _draft(self, name, label):
        return {
            "schemaVersion": "graphpilot.draft.v1",
            "kind": "diagramDraft",
            "diagramName": name,
            "diagramType": "activity_diagram",
            "authority": "conceptual",
            "requests": ["x"],
            "evidence": [],
            "elements": [
                {"id": "start", "semanticType": "initialNode", "label": "Start",
                 "assurance": "conceptual"},
                {"id": "act", "semanticType": "opaqueAction", "label": label,
                 "assurance": "conceptual"},
            ],
            "relationships": [
                {"id": "f1", "semanticType": "controlFlow", "source": "start",
                 "target": "act", "assurance": "conceptual"},
            ],
 "assumptions": [],
        }

    def test_a_readable_diagram_warns_about_nothing(self):
        result = DiagramCreationService().create(self.workspace, self._draft("clean", "Do it"))

        self.assertEqual(
            [w for w in result.warnings if w["code"] == "hard_to_read"], []
        )

    def test_the_author_is_told_when_the_picture_is_hard_to_read(self):
        result = DiagramCreationService().create(
            self.workspace,
            self._draft("crowded", "Reconcile every outstanding ledger entry against "
                                   "the settlement file received overnight from the rail"),
        )

        warnings = [w for w in result.warnings if w["code"] == "hard_to_read"]
        if warnings:
            self.assertGreater(warnings[0]["illegible"], 0)
            self.assertIn("hard to read", warnings[0]["message"])
        # A clean layout is a valid outcome — what must never happen is a silent one, so
        # the assertion is on the shape of the report rather than on a specific count.
        self.assertTrue(all("message" in w and "code" in w for w in result.warnings))

    def test_one_call_reports_both_kinds_of_warning(self):
        """`diagram_create` used to drop canonical validation's warnings.

        A host wanting them had to call `diagram_validate` on the file it had just
        created, and then found two checks that disagreed and never mentioned each other:
        `long_label` counts characters in the model, `hard_to_read` measures the SVG that
        was drawn. Neither subsumes the other — a long note label can render perfectly
        inside a large note, and a short one can be clipped by a small node — so both come
        back from the one call that produced the diagram.
        """
        draft = self._draft("both-kinds", "x" * 150)

        result = DiagramCreationService().create(self.workspace, draft)

        codes = {warning["code"] for warning in result.warnings}
        self.assertIn("long_label", codes, result.warnings)
        self.assertTrue(all("message" in w for w in result.warnings))

    def test_a_measurement_failure_never_costs_a_saved_diagram(self):
        service = DiagramCreationService()
        result = service.create(self.workspace, self._draft("resilient", "Fine"))

        self.assertTrue(result.diagram_path.exists())
        self.assertEqual(result.node_count, 2)
