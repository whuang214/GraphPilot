"""Does the diagram still say what the draft said?

Every other check in the product examines the diagram alone — is it legal, structurally
sound, readable, correctly cited. None asked whether the output matched its input, so a
field materialization quietly discarded produced a diagram that passed all of them.

`g11` is the case that proves it. A host authored `parameters: ["mode: Mode"]`, canonical
assembly only accepted the object form, and the parameter vanished. The draft validated,
`diagram_create` succeeded, the saved diagram was valid, legible and correctly cited — and
had no parameters. **600 tests and three corpus runs missed it.**

Two properties matter equally here, and the second is the one usually skipped: the check
must be silent on the 48 committed examples, *and* it must actually fire. A check that is
only ever silent proves nothing.
"""

import json
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.materialization import canonical_assembly
from services.materialization.diagram_creation_service import DiagramCreationService
from services.materialization.faithfulness import check, describe
from services.materialization.materializer import materialize

BLUEPRINTS = Path(settings.BASE_DIR) / "assets" / "blueprints"


def _draft(**overrides):
    draft = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "faithful",
        "diagramType": "bdd_diagram",
        "authority": "conceptual",
        "requests": ["x"],
        "evidence": [],
        "elements": [{
            "id": "engine", "semanticType": "block", "label": "Engine",
            "assurance": "conceptual",
            "features": {
                "operations": [{"name": "start", "parameters": ["mode: Mode"],
                                "returnType": "Boolean"}],
                "constraints": [{"name": "positiveMass", "expression": "mass > 0"}],
            },
        }],
        "relationships": [],
 "assumptions": [],
    }
    draft.update(overrides)
    return draft


def _build(draft):
    diagram, _engine = materialize(
        draft, evidence_digests={}, layout_service=DiagramLayoutService()
    )
    return diagram


class NothingIsLostTests(SimpleTestCase):
    def test_a_faithful_diagram_reports_nothing(self):
        draft = _draft()

        self.assertEqual(check(draft, _build(draft)), [])
        self.assertEqual(describe([]), "")

    def test_every_committed_example_is_faithful_to_its_draft(self):
        """The check must be quiet on good input or nobody will believe it when it speaks.

        This is also the assertion that would have failed the day `g11` landed, across
        every example whose draft authored an operation parameter.
        """
        noisy = []
        for draft_path in sorted(BLUEPRINTS.glob("*/examples/*/*/draft.json")):
            output = draft_path.parent / "output.gp.json"
            if not output.exists():
                continue
            losses = check(
                json.loads(draft_path.read_text(encoding="utf-8")),
                json.loads(output.read_text(encoding="utf-8")),
            )
            if losses:
                noisy.append(f"{draft_path.parent.name}: {losses[0]}")
        self.assertEqual(noisy, [])


class TheCheckActuallyBitesTests(SimpleTestCase):
    """Restoring the real bug, to prove the check is not merely silent about everything."""

    def test_it_catches_the_parameters_that_g11_discarded(self):
        draft = _draft()
        original = canonical_assembly._clean_parameters

        def objects_only(raw):
            # Exactly the pre-fix behaviour: a string parameter is dropped on the floor.
            return [
                {"name": v["name"].strip(), "direction": "in"}
                for v in (raw if isinstance(raw, list) else [])
                if isinstance(v, dict) and isinstance(v.get("name"), str)
            ]

        canonical_assembly._clean_parameters = objects_only
        try:
            losses = check(draft, _build(draft))
        finally:
            canonical_assembly._clean_parameters = original

        self.assertTrue(losses)
        self.assertEqual(losses[0].kind, "element")
        self.assertEqual(losses[0].field, "features")
        self.assertIn("Mode", str(losses[0]))
        self.assertIn("GraphPilot defect", describe(losses))

    def test_it_catches_an_element_that_never_arrived(self):
        draft = _draft()
        diagram = _build(draft)
        diagram["nodes"] = []

        loss, = check(draft, diagram)

        self.assertEqual(loss.item_id, "engine")
        self.assertIn("not in the diagram at all", str(loss))

    def test_it_catches_a_dropped_relationship_end(self):
        draft = _draft()
        draft["elements"].append({
            "id": "wheel", "semanticType": "block", "label": "Wheel",
            "assurance": "conceptual",
        })
        draft["relationships"] = [{
            "id": "wheel-of-engine", "semanticType": "composition",
            "source": "wheel", "target": "engine",
            "sourceRole": "roadwheel", "assurance": "conceptual",
        }]
        diagram = _build(draft)
        # Simulate assembly forgetting the role it was handed.
        for edge in diagram["edges"]:
            edge["data"].pop("sourceEnd", None)

        loss, = check(draft, diagram)

        self.assertEqual(loss.field, "sourceRole")
        self.assertIn("roadwheel", str(loss))

    def test_it_catches_an_assumption_body_that_did_not_travel(self):
        draft = _draft()
        draft["authority"] = "conceptual"
        draft["elements"][0]["assurance"] = "assumed"
        draft["elements"][0]["assumptionRef"] = "asm-engine-exists"
        draft["assumptions"] = [{
            "id": "asm-engine-exists",
            "statement": "The propulsion unit is a single replaceable engine.",
            "reason": "Every service manual treats it as one part.",
            "acceptedBy": "host",
        }]
        diagram = _build(draft)
        diagram["metadata"].pop("assurance", None)

        losses = check(draft, diagram)

        self.assertTrue(any(loss.kind == "assumption" for loss in losses))


class WhatTheCheckLooksAtTests(SimpleTestCase):
    """It walks elements, relationships, evidence and referenced assumptions. That is all.

    There used to be a `NOT_CARRIED` constant naming three sections the check was said to
    exempt — and `check()` never read it. It was a comment with a type annotation, and a
    test asserting its contents asserted nothing about behaviour. Those sections are gone
    from the draft now, and what remains is the real boundary: the ask is carried into
    `metadata.requests`, so it is checked like everything else.
    """

    def test_the_ask_reaches_the_diagram_and_is_checked(self):
        draft = _draft(requests=["Draw the engine and what constrains it."])

        self.assertEqual(check(draft, _build(draft)), [])

    def test_an_ask_the_diagram_dropped_is_a_loss(self):
        draft = _draft(requests=["Mention the flywheel somewhere."])
        diagram = _build(draft)
        diagram["metadata"].pop("requests")

        self.assertTrue(any(loss.kind == "request" for loss in check(draft, diagram)))


class CreateReportsALossTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = self._tmp.name

    def test_a_clean_create_warns_about_nothing(self):
        result = DiagramCreationService().create(self.workspace, _draft(diagramName="clean"))

        self.assertEqual([w for w in result.warnings if w["code"] == "content_lost"], [])

    def test_a_loss_is_reported_to_the_host_as_our_defect(self):
        """The host cannot fix this and must not be told to try — their draft was accepted."""
        original = canonical_assembly._clean_parameters
        canonical_assembly._clean_parameters = lambda raw: []
        try:
            result = DiagramCreationService().create(self.workspace, _draft(diagramName="lossy"))
        finally:
            canonical_assembly._clean_parameters = original

        warning, = [w for w in result.warnings if w["code"] == "content_lost"]
        self.assertIn("GraphPilot defect", warning["message"])
        self.assertFalse(warning["retryable"])
        # And the diagram is still saved: it is mostly right, and refusing would punish
        # the author for a bug they did not cause.
        self.assertTrue(result.diagram_path.exists())
