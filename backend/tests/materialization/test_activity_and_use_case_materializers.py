"""Activity and use-case notation, applied by the same materializer as BDD.

The materializer is type-generic; what differs per type is the vocabulary and the
relationship-end policy. These tests pin the two remaining types against that shared
machinery rather than duplicating it.
"""

import json

from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.rendering.diagram_render_service import DiagramRenderService
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.drafts.draft_validation_service import DraftValidationService
from services.materialization.materializer import materialize


def _draft(diagram_type, elements, relationships, name="sample"):
    return {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": name,
        "diagramType": diagram_type,
        "authority": "conceptual",
        "requests": ["Diagram it."],
        "elements": [{**element, "assurance": "conceptual"} for element in elements],
        "relationships": [{**link, "assurance": "conceptual"} for link in relationships],
    }


def _materialize(draft):
    return materialize(draft, evidence_digests={}, layout_service=DiagramLayoutService())[0]


def _assert_usable(case, draft):
    """A draft the contract accepts must materialize, validate, and draw."""
    case.assertTrue(DraftValidationService().validate(draft).valid)
    canonical = _materialize(draft)
    result = DiagramValidationService().validate(canonical)
    case.assertTrue(result.valid, msg=[issue.message for issue in result.issues])
    case.assertIn("<svg", DiagramRenderService().to_svg(canonical))
    return canonical


class ActivityMaterializerTests(SimpleTestCase):
    def _flow_draft(self):
        return _draft(
            "activity_diagram",
            [
                {"id": "start", "semanticType": "initialNode", "label": "Start"},
                {"id": "receive", "semanticType": "opaqueAction", "label": "Receive Order"},
                {"id": "valid", "semanticType": "decisionNode", "label": "Valid?"},
                {"id": "accept", "semanticType": "opaqueAction", "label": "Accept"},
                {"id": "reject", "semanticType": "opaqueAction", "label": "Reject"},
                {"id": "merge", "semanticType": "mergeNode", "label": "Merge"},
                {"id": "done", "semanticType": "activityFinalNode", "label": "Done"},
            ],
            [
                {"id": "f1", "semanticType": "controlFlow", "source": "start", "target": "receive"},
                {"id": "f2", "semanticType": "controlFlow", "source": "receive", "target": "valid"},
                {"id": "f3", "semanticType": "controlFlow", "source": "valid", "target": "accept", "guard": "valid"},
                {"id": "f4", "semanticType": "controlFlow", "source": "valid", "target": "reject", "guard": "invalid"},
                {"id": "f5", "semanticType": "controlFlow", "source": "accept", "target": "merge"},
                {"id": "f6", "semanticType": "controlFlow", "source": "reject", "target": "merge"},
                {"id": "f7", "semanticType": "controlFlow", "source": "merge", "target": "done"},
            ],
        )

    def test_a_branching_flow_materializes_validates_and_renders(self):
        canonical = _assert_usable(self, self._flow_draft())

        self.assertEqual(len(canonical["nodes"]), 7)
        self.assertEqual(len(canonical["edges"]), 7)
        self.assertEqual([edge["id"] for edge in canonical["edges"]][:2], ["f1", "f2"])

    def test_guards_reach_the_canonical_edges_and_control_flows_carry_no_ends(self):
        canonical = _materialize(self._flow_draft())
        by_id = {edge["id"]: edge["data"] for edge in canonical["edges"]}

        self.assertEqual(by_id["f3"]["guard"], "valid")
        self.assertEqual(by_id["f4"]["guard"], "invalid")
        self.assertNotIn("guard", by_id["f1"])
        for data in by_id.values():
            self.assertNotIn("sourceEnd", data)
            self.assertNotIn("targetEnd", data)

    def test_fork_and_join_concurrency_materializes(self):
        draft = _draft(
            "activity_diagram",
            [
                {"id": "start", "semanticType": "initialNode", "label": "Start"},
                {"id": "fork", "semanticType": "forkNode", "label": "Fork"},
                {"id": "left", "semanticType": "opaqueAction", "label": "Diagnose"},
                {"id": "right", "semanticType": "opaqueAction", "label": "Check Warranty"},
                {"id": "join", "semanticType": "joinNode", "label": "Join"},
                {"id": "done", "semanticType": "activityFinalNode", "label": "Done"},
            ],
            [
                {"id": "a", "semanticType": "controlFlow", "source": "start", "target": "fork"},
                {"id": "b", "semanticType": "controlFlow", "source": "fork", "target": "left"},
                {"id": "c", "semanticType": "controlFlow", "source": "fork", "target": "right"},
                {"id": "d", "semanticType": "controlFlow", "source": "left", "target": "join"},
                {"id": "e", "semanticType": "controlFlow", "source": "right", "target": "join"},
                {"id": "f", "semanticType": "controlFlow", "source": "join", "target": "done"},
            ],
        )
        _assert_usable(self, draft)

    def test_a_fork_needs_no_guards_but_a_decision_does(self):
        """Concurrency takes every branch; choice takes one, so only choice explains itself."""
        forked = _draft(
            "activity_diagram",
            [
                {"id": "fork", "semanticType": "forkNode", "label": "Fork"},
                {"id": "left", "semanticType": "opaqueAction", "label": "Left"},
                {"id": "right", "semanticType": "opaqueAction", "label": "Right"},
            ],
            [
                {"id": "a", "semanticType": "controlFlow", "source": "fork", "target": "left"},
                {"id": "b", "semanticType": "controlFlow", "source": "fork", "target": "right"},
            ],
        )
        self.assertTrue(DraftValidationService().validate(forked).valid)

        decided = json.loads(json.dumps(forked))
        decided["elements"][0]["semanticType"] = "decisionNode"
        findings = DraftValidationService().validate(decided).findings
        self.assertEqual([f.code for f in findings], ["guard_required", "guard_required"])

    def test_a_note_attaches_through_a_comment_link(self):
        draft = _draft(
            "activity_diagram",
            [
                {"id": "act", "semanticType": "opaqueAction", "label": "Persist"},
                {"id": "remark", "semanticType": "note", "label": "Writes through the repository port."},
            ],
            [{"id": "n1", "semanticType": "commentLink", "source": "remark", "target": "act"}],
        )
        canonical = _assert_usable(self, draft)

        self.assertEqual(canonical["edges"][0]["data"]["semanticType"], "commentLink")


class UseCaseMaterializerTests(SimpleTestCase):
    def _store_draft(self):
        return _draft(
            "use_case_diagram",
            [
                {"id": "store", "semanticType": "subject", "label": "Storefront"},
                {"id": "browse", "semanticType": "useCase", "label": "Browse Catalogue", "parentId": "store"},
                {"id": "checkout", "semanticType": "useCase", "label": "Check Out", "parentId": "store"},
                {"id": "pay", "semanticType": "useCase", "label": "Take Payment", "parentId": "store"},
                {"id": "giftwrap", "semanticType": "useCase", "label": "Gift Wrap", "parentId": "store"},
                {"id": "shopper", "semanticType": "actor", "label": "Shopper"},
                {"id": "member", "semanticType": "actor", "label": "Member"},
            ],
            [
                {"id": "r1", "semanticType": "association", "source": "shopper", "target": "browse"},
                {"id": "r2", "semanticType": "association", "source": "shopper", "target": "checkout"},
                {"id": "r3", "semanticType": "include", "source": "checkout", "target": "pay"},
                {"id": "r4", "semanticType": "extend", "source": "giftwrap", "target": "checkout"},
                {"id": "r5", "semanticType": "generalization", "source": "member", "target": "shopper"},
            ],
        )

    def test_a_full_use_case_diagram_materializes_validates_and_renders(self):
        canonical = _assert_usable(self, self._store_draft())

        self.assertEqual(len(canonical["nodes"]), 7)
        self.assertEqual(len(canonical["edges"]), 5)

    def test_the_subject_contains_its_use_cases_and_not_the_actors(self):
        canonical = _materialize(self._store_draft())
        parents = {node["id"]: node.get("parentId") for node in canonical["nodes"]}

        self.assertEqual(parents["browse"], "store")
        self.assertEqual(parents["checkout"], "store")
        self.assertIsNone(parents["shopper"])
        self.assertIsNone(parents["store"])

    def test_include_extend_and_generalization_carry_no_relationship_ends(self):
        canonical = _materialize(self._store_draft())
        by_id = {edge["id"]: edge["data"] for edge in canonical["edges"]}

        for edge_id in ("r3", "r4", "r5"):
            with self.subTest(edge=edge_id):
                self.assertNotIn("sourceEnd", by_id[edge_id])
                self.assertNotIn("targetEnd", by_id[edge_id])

    def test_include_and_extend_keep_their_authored_direction(self):
        """include runs base to included; extend runs extension to base."""
        canonical = _materialize(self._store_draft())
        by_id = {edge["id"]: edge for edge in canonical["edges"]}

        self.assertEqual((by_id["r3"]["source"], by_id["r3"]["target"]), ("checkout", "pay"))
        self.assertEqual((by_id["r4"]["source"], by_id["r4"]["target"]), ("giftwrap", "checkout"))

    def test_an_actor_association_may_carry_a_multiplicity(self):
        draft = self._store_draft()
        draft["relationships"][0]["targetMultiplicity"] = {"lower": 0, "upper": "*"}
        canonical = _assert_usable(self, draft)

        association = next(edge for edge in canonical["edges"] if edge["id"] == "r1")
        self.assertEqual(association["data"]["targetEnd"], {"multiplicity": {"lower": 0, "upper": "*"}})


class CrossTypeTests(SimpleTestCase):
    def test_each_type_stamps_its_own_notation_family(self):
        cases = {
            "activity_diagram": ("uml", [{"id": "a", "semanticType": "opaqueAction", "label": "Act"}]),
            "use_case_diagram": ("uml", [{"id": "a", "semanticType": "useCase", "label": "Use"}]),
            "bdd_diagram": ("sysml", [{"id": "a", "semanticType": "block", "label": "Block"}]),
        }
        for diagram_type, (notation, elements) in cases.items():
            with self.subTest(diagram_type=diagram_type):
                canonical = _materialize(_draft(diagram_type, elements, []))
                self.assertEqual(canonical["metadata"]["notation"], notation)
                self.assertEqual(canonical["diagramType"], diagram_type)

    def test_a_type_never_accepts_another_type_vocabulary(self):
        service = DraftValidationService()
        for diagram_type, foreign in (
            ("activity_diagram", "block"),
            ("use_case_diagram", "opaqueAction"),
            ("bdd_diagram", "actor"),
        ):
            with self.subTest(diagram_type=diagram_type):
                draft = _draft(diagram_type, [{"id": "a", "semanticType": foreign, "label": "X"}], [])
                codes = {f.code for f in service.validate(draft).findings}
                self.assertIn("semantic_type_unsupported", codes)
