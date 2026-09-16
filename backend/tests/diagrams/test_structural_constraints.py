"""Offline tests for the deterministic structural critic.

Covers the per-type structural rules in ``services.diagrams.validation.structural_constraints`` and guards
that none of them false-positive on the curated eval-pool answer keys.
"""

import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES
from services.diagrams.validation.structural_constraints import check_structural_constraints, describe


def _node(nid, sem, label="x"):
    return {"id": nid, "type": "node", "data": {"label": label, "semanticType": sem}}


def _edge(eid, src, tgt, sem="controlFlow", label=None):
    edge = {"id": eid, "source": src, "target": tgt, "data": {"semanticType": sem}}
    if label is not None:
        edge["label"] = label
    return edge


def _rules(diagram, diagram_type):
    return {v.rule for v in check_structural_constraints(diagram, diagram_type)}


def _activity(nodes, edges):
    return {"diagramType": "activity_diagram", "nodes": nodes, "edges": edges}


_CLEAN_NODES = [
    _node("initialNode", "initialNode", "Start"),
    _node("a", "opaqueAction", "Do"),
    _node("d", "decisionNode", "OK?"),
    _node("e1", "activityFinalNode", "Yes end"),
    _node("e2", "activityFinalNode", "No end"),
]
_CLEAN_EDGES = [
    _edge("e_sa", "initialNode", "a"),
    _edge("e_ad", "a", "d"),
    _edge("e_d1", "d", "e1", label="yes"),
    _edge("e_d2", "d", "e2", label="no"),
]


class ActivityConstraintTests(SimpleTestCase):
    def test_well_formed_activity_has_no_violations(self):
        self.assertEqual(check_structural_constraints(_activity(_CLEAN_NODES, _CLEAN_EDGES), "activity_diagram"), [])

    def test_requires_exactly_one_start(self):
        nodes = _CLEAN_NODES + [_node("start2", "initialNode", "Start 2")]
        self.assertIn("single_start", _rules(_activity(nodes, _CLEAN_EDGES), "activity_diagram"))

    def test_requires_an_end(self):
        nodes = [n for n in _CLEAN_NODES if n["data"]["semanticType"] != "activityFinalNode"]
        edges = [_edge("e_sa", "initialNode", "a"), _edge("e_ad", "a", "d")]
        self.assertIn("has_end", _rules(_activity(nodes, edges), "activity_diagram"))

    def test_start_must_have_no_incoming(self):
        edges = _CLEAN_EDGES + [_edge("e_back", "a", "initialNode")]
        self.assertIn("start_no_incoming", _rules(_activity(_CLEAN_NODES, edges), "activity_diagram"))

    def test_end_must_have_no_outgoing(self):
        edges = _CLEAN_EDGES + [_edge("e_out", "e1", "a")]
        self.assertIn("end_no_outgoing", _rules(_activity(_CLEAN_NODES, edges), "activity_diagram"))

    def test_decision_needs_two_branches(self):
        edges = [_edge("e_sa", "initialNode", "a"), _edge("e_ad", "a", "d"), _edge("e_d1", "d", "e1", label="yes")]
        nodes = [n for n in _CLEAN_NODES if n["id"] != "e2"]
        self.assertIn("decision_branches", _rules(_activity(nodes, edges), "activity_diagram"))

    def test_decision_branches_must_be_guarded(self):
        edges = [
            _edge("e_sa", "initialNode", "a"),
            _edge("e_ad", "a", "d"),
            _edge("e_d1", "d", "e1"),  # unlabelled guard
            _edge("e_d2", "d", "e2", label="no"),
        ]
        self.assertIn("decision_guards", _rules(_activity(_CLEAN_NODES, edges), "activity_diagram"))

    def test_unreachable_node_flagged(self):
        nodes = _CLEAN_NODES + [_node("orphan", "opaqueAction", "Unreachable")]
        self.assertIn("reachable_from_start", _rules(_activity(nodes, _CLEAN_EDGES), "activity_diagram"))

    def test_floating_note_is_exempt_from_reachability(self):
        nodes = _CLEAN_NODES + [_node("n1", "note", "A note")]
        self.assertNotIn("reachable_from_start", _rules(_activity(nodes, _CLEAN_EDGES), "activity_diagram"))

    def test_comment_links_do_not_count_as_activity_flow(self):
        nodes = _CLEAN_NODES + [_node("orphan", "opaqueAction", "Unreachable")]
        edges = _CLEAN_EDGES + [
            _edge("comment_in", "orphan", "initialNode", sem="commentLink"),
            _edge("comment_reach", "a", "orphan", sem="commentLink"),
        ]
        rules = _rules(_activity(nodes, edges), "activity_diagram")
        self.assertNotIn("start_no_incoming", rules)
        self.assertIn("reachable_from_start", rules)

    def test_schema_invalid_nested_data_does_not_crash(self):
        nodes = _CLEAN_NODES + [{"id": "bad", "type": "gpNode", "data": "invalid"}]
        violations = check_structural_constraints(_activity(nodes, _CLEAN_EDGES), "activity_diagram")
        self.assertIsInstance(violations, list)

    def test_fork_needs_two_outgoing(self):
        nodes = _CLEAN_NODES + [_node("f", "forkNode", "Fork")]
        edges = _CLEAN_EDGES + [_edge("e_af", "a", "f"), _edge("e_f1", "f", "e1")]
        self.assertIn("fork_outgoing", _rules(_activity(nodes, edges), "activity_diagram"))

    def test_fork_needs_two_distinct_outgoing_targets(self):
        nodes = _CLEAN_NODES + [_node("f", "forkNode", "Fork")]
        edges = _CLEAN_EDGES + [
            _edge("e_af", "a", "f"),
            _edge("e_f1", "f", "e1"),
            _edge("e_f2", "f", "e1"),
        ]
        self.assertIn("fork_outgoing", _rules(_activity(nodes, edges), "activity_diagram"))

    def test_join_needs_two_incoming(self):
        nodes = _CLEAN_NODES + [_node("j", "joinNode", "Join")]
        edges = _CLEAN_EDGES + [_edge("e_aj", "a", "j"), _edge("e_j1", "j", "e1")]
        self.assertIn("join_incoming", _rules(_activity(nodes, edges), "activity_diagram"))

    def test_join_needs_two_distinct_incoming_sources(self):
        nodes = _CLEAN_NODES + [_node("j", "joinNode", "Join")]
        edges = _CLEAN_EDGES + [
            _edge("e_aj1", "a", "j"),
            _edge("e_aj2", "a", "j"),
            _edge("e_j1", "j", "e1"),
        ]
        self.assertIn("join_incoming", _rules(_activity(nodes, edges), "activity_diagram"))

    def test_well_formed_fork_join_is_clean(self):
        nodes = [
            _node("initialNode", "initialNode"), _node("f", "forkNode"),
            _node("a1", "opaqueAction"), _node("a2", "opaqueAction"),
            _node("j", "joinNode"), _node("activityFinalNode", "activityFinalNode"),
        ]
        edges = [
            _edge("e_sf", "initialNode", "f"),
            _edge("e_f1", "f", "a1"), _edge("e_f2", "f", "a2"),
            _edge("e_1j", "a1", "j"), _edge("e_2j", "a2", "j"),
            _edge("e_je", "j", "activityFinalNode"),
        ]
        self.assertEqual(check_structural_constraints(_activity(nodes, edges), "activity_diagram"), [])


class UseCaseConstraintTests(SimpleTestCase):
    def test_include_between_use_cases_is_clean(self):
        nodes = [_node("actor", "actor"), _node("uc1", "useCase"), _node("uc2", "useCase")]
        edges = [_edge("e1", "actor", "uc1", sem="association"), _edge("e2", "uc1", "uc2", sem="include")]
        self.assertEqual(check_structural_constraints({"nodes": nodes, "edges": edges}, "use_case_diagram"), [])

    def test_include_touching_actor_is_flagged(self):
        nodes = [_node("actor", "actor"), _node("uc1", "useCase")]
        edges = [_edge("e1", "actor", "uc1", sem="include")]
        self.assertIn(
            "include_extend_between_use_cases",
            _rules({"nodes": nodes, "edges": edges}, "use_case_diagram"),
        )

    def test_extend_location_must_be_declared_by_the_base_use_case(self):
        nodes = [_node("actor", "actor"), _node("base", "useCase"), _node("extension", "useCase")]
        edge = _edge("e1", "extension", "base", sem="extend")
        edge["data"]["extensionLocations"] = ["checkout"]
        rules = _rules({"nodes": nodes, "edges": [edge]}, "use_case_diagram")
        self.assertIn("extend_location_exists", rules)

    def test_generalization_between_actors_is_clean(self):
        nodes = [_node("a1", "actor"), _node("a2", "actor"), _node("uc", "useCase")]
        edges = [
            _edge("e1", "a2", "a1", sem="generalization"),
            _edge("e2", "a1", "uc", sem="association"),
        ]
        self.assertEqual(check_structural_constraints({"nodes": nodes, "edges": edges}, "use_case_diagram"), [])

    def test_generalization_between_use_cases_is_clean(self):
        nodes = [_node("actor", "actor"), _node("uc1", "useCase"), _node("uc2", "useCase")]
        edges = [
            _edge("e1", "uc2", "uc1", sem="generalization"),
            _edge("e2", "actor", "uc1", sem="association"),
        ]
        self.assertEqual(check_structural_constraints({"nodes": nodes, "edges": edges}, "use_case_diagram"), [])

    def test_generalization_mixing_actor_and_use_case_is_flagged(self):
        nodes = [_node("a1", "actor"), _node("uc1", "useCase")]
        edges = [_edge("e1", "a1", "uc1", sem="generalization")]
        self.assertIn(
            "generalization_same_kind",
            _rules({"nodes": nodes, "edges": edges}, "use_case_diagram"),
        )


class BddConstraintTests(SimpleTestCase):
    def test_generalization_between_blocks_is_clean(self):
        nodes = [_node("b1", "block"), _node("b2", "block")]
        edges = [_edge("e1", "b1", "b2", sem="generalization")]
        self.assertEqual(check_structural_constraints({"nodes": nodes, "edges": edges}, "bdd_diagram"), [])

    def test_generalization_touching_non_block_is_flagged(self):
        nodes = [_node("b1", "block"), _node("p1", "valueType")]
        edges = [_edge("e1", "b1", "p1", sem="generalization")]
        self.assertIn(
            "generalization_same_kind",
            _rules({"nodes": nodes, "edges": edges}, "bdd_diagram"),
        )

    def test_generalization_between_same_non_block_kind_is_clean(self):
        # Matched canonical definition kinds may generalize without a false positive.
        nodes = [_node("b", "block"), _node("v1", "valueType"), _node("v2", "valueType")]
        edges = [_edge("e1", "v1", "v2", sem="generalization")]
        self.assertEqual(check_structural_constraints({"nodes": nodes, "edges": edges}, "bdd_diagram"), [])


class CustomConstraintTests(SimpleTestCase):
    def test_parallel_edges_are_unrestricted(self):
        nodes = [_node("a", "block"), _node("b", "block")]
        edges = [_edge("e1", "a", "b", sem="association"), _edge("e2", "a", "b", sem="association")]
        self.assertEqual(check_structural_constraints({"nodes": nodes, "edges": edges}, "custom"), [])


class DescribeTests(SimpleTestCase):
    def test_describe_is_non_empty_for_each_type(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            self.assertTrue(describe(diagram_type).strip(), diagram_type)


class EvalPoolStaysCleanTests(SimpleTestCase):
    """Every curated canonical eval answer key satisfies the structural critic."""

    def test_no_eval_key_violates_structural_constraints(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            base = Path(settings.BASE_DIR) / "assets" / "blueprints" / diagram_type / "examples" / "answers"
            for output_path in sorted(base.glob("*/output.gp.json")):
                answer_key = json.loads(output_path.read_text(encoding="utf-8"))
                violations = check_structural_constraints(answer_key, diagram_type)
                self.assertEqual(
                    violations,
                    [],
                    f"{diagram_type}/{output_path.parent.name} violates: {[v.rule for v in violations]}",
                )
