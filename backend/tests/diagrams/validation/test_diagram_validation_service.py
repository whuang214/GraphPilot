"""Tests for DiagramValidationService.

These cover the validation layers (schema, structure, advisory blueprint/type,
render-readiness) and the level/valid derivation. The real schema artifact and
real type profiles are used so behavior matches production.
"""

import copy
import math
from pathlib import Path

from django.test import SimpleTestCase

from services.shared.schema_registry import SchemaRegistry
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.diagrams.validation.validation_contract import (
    SCHEMA_CODE_PREFIX,
    Severity,
    ValidationCode,
    ValidationLayer,
    ValidationLevel,
)


SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "schemas" / "diagram.json"
)


def _valid_diagram():
    return {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": "activity_diagram",
        "id": "diagram_order_review",
        "name": "Order Review",
        "metadata": {
            "source": "mcp",
            "blueprintKey": "activity_diagram.default",
        },
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": [
            {
                "id": "node_start",
                "type": "gpNode",
                "position": {"x": 80, "y": 80},
                "width": 140,
                "height": 60,
                "data": {"label": "Start", "semanticType": "initialNode"},
            },
            {
                "id": "node_review",
                "type": "gpNode",
                "position": {"x": 280, "y": 80},
                "width": 180,
                "height": 60,
                "data": {"label": "End", "semanticType": "activityFinalNode"},
            },
        ],
        "edges": [
            {
                "id": "edge_start_to_review",
                "type": "default",
                "source": "node_start",
                "target": "node_review",
                "label": "Next",
                "data": {"semanticType": "controlFlow"},
            }
        ],
    }


def _valid_evidence_record(evidence_id="ev-order-review"):
    return {
        "id": evidence_id,
        "kind": "code",
        "locator": {
            "path": "src/orders/review.py",
            "symbol": "review_order",
            "lineRange": {"start": 10, "end": 42},
        },
        "contentDigest": "sha256:" + "1" * 64,
        "summary": "review_order validates and then completes the order.",
    }


def _valid_custom_diagram():
    """A `custom` universal-canvas diagram mixing catalog notations (actor + action +
    a block classifier). Proves the whole catalog is accepted and the type validates
    once `custom` is in the schema enum (P1). Fully connected + well-formed so it is a
    clean pass with no blocking errors."""
    return {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": "custom",
        "id": "diagram_custom_board",
        "name": "Mixed Board",
        "metadata": {"source": "ui", "authoring": "custom"},
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": [
            {
                "id": "n_actor",
                "type": "gpNode",
                "position": {"x": 80, "y": 80},
                "width": 80,
                "height": 120,
                "data": {"label": "User", "semanticType": "actor"},
            },
            {
                "id": "n_action",
                "type": "gpNode",
                "position": {"x": 280, "y": 100},
                "width": 160,
                "height": 60,
                "data": {"label": "Do Thing", "semanticType": "opaqueAction"},
            },
            {
                "id": "n_block",
                "type": "gpNode",
                "position": {"x": 520, "y": 90},
                "width": 180,
                "height": 80,
                "data": {"label": "Engine", "semanticType": "block"},
            },
        ],
        "edges": [
            {
                "id": "e_actor_action",
                "type": "default",
                "source": "n_actor",
                "target": "n_action",
                "data": {"semanticType": "association"},
            },
            {
                "id": "e_action_block",
                "type": "default",
                "source": "n_action",
                "target": "n_block",
                "data": {"semanticType": "association"},
            },
        ],
    }


class DiagramValidationServiceTests(SimpleTestCase):
    def setUp(self):
        self.svc = DiagramValidationService(
            schema_service=SchemaRegistry(schema_root=SCHEMA_PATH.parent)
        )

    def _codes(self, result):
        return {issue.code for issue in result.issues}

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_valid_diagram_passes(self):
        result = self.svc.validate(_valid_diagram())
        self.assertTrue(result.valid, msg=[i.message for i in result.issues])
        self.assertEqual(result.level, ValidationLevel.PASS)
        self.assertEqual(result.issues, [])

    def test_custom_diagram_type_is_valid(self):
        # `custom` is a first-class save/validate type (whole-catalog vocabulary): it must
        # clear the schema enum + the advisory unsupported-type check with no blocking
        # errors, so a frontend save or future MCP edit of a custom board round-trips.
        result = self.svc.validate(_valid_custom_diagram())
        self.assertTrue(result.valid, msg=[i.message for i in result.issues])
        errors = [i for i in result.issues if i.severity == Severity.ERROR]
        self.assertEqual(errors, [], msg=[i.message for i in errors])
        self.assertNotIn(ValidationCode.UNSUPPORTED_DIAGRAM_TYPE.value, self._codes(result))

    def test_origin_and_inline_evidence_are_strict_optional_canonical_fields(self):
        diagram = _valid_diagram()
        diagram["metadata"].update(
            {"authority": "as_implemented", "evidence": [_valid_evidence_record()]}
        )
        diagram["nodes"][0]["origin"] = {
            "assurance": "grounded",
            "evidenceRefs": [],
            "assumptionRefs": [],
            "schemaRules": ["activity.initial-node"],
            "rationale": "GraphPilot adds the initial marker as notation scaffolding.",
        }
        # A schema-rule element is scaffolding, not a repository claim.
        diagram["nodes"][0]["origin"]["assurance"] = "conceptual"
        diagram["nodes"][1]["origin"] = {
            "assurance": "grounded",
            "evidenceRefs": ["ev-order-review"],
            "assumptionRefs": [],
            "schemaRules": [],
            "rationale": "The cited region establishes completion.",
        }
        diagram["edges"][0]["origin"] = copy.deepcopy(diagram["nodes"][1]["origin"])

        result = self.svc.validate(diagram)

        self.assertTrue(result.valid, msg=[issue.message for issue in result.issues])

    def test_malformed_origin_fails_canonical_schema(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["origin"] = {
            "evidenceRefs": [],
            "assumptionRefs": [],
            "schemaRules": [],
        }

        result = self.svc.validate(diagram)

        self.assertFalse(result.valid)
        self.assertIn("schema_required", self._codes(result))

    def test_grounded_origin_requires_evidence_and_assumed_requires_an_assumption(self):
        grounded = _valid_diagram()
        grounded["nodes"][0]["origin"] = {
            "assurance": "grounded",
            "evidenceRefs": [],
            "assumptionRefs": [],
            "schemaRules": [],
            "rationale": "Claims grounding it does not have.",
        }
        self.assertFalse(self.svc.validate(grounded).valid)

        assumed = _valid_diagram()
        assumed["nodes"][0]["origin"] = {
            "assurance": "assumed",
            "evidenceRefs": [],
            "assumptionRefs": [],
            "schemaRules": [],
            "rationale": "Assumes without naming the assumption.",
        }
        self.assertFalse(self.svc.validate(assumed).valid)

    def test_authority_and_inline_evidence_must_agree(self):
        implemented_without_evidence = _valid_diagram()
        implemented_without_evidence["metadata"]["authority"] = "as_implemented"
        self.assertFalse(self.svc.validate(implemented_without_evidence).valid)

        conceptual_with_evidence = _valid_diagram()
        conceptual_with_evidence["metadata"].update(
            {"authority": "conceptual", "evidence": [_valid_evidence_record()]}
        )
        self.assertFalse(self.svc.validate(conceptual_with_evidence).valid)

        evidence_without_authority = _valid_diagram()
        evidence_without_authority["metadata"]["evidence"] = [_valid_evidence_record()]
        self.assertFalse(self.svc.validate(evidence_without_authority).valid)

        conceptual = _valid_diagram()
        conceptual["metadata"]["authority"] = "conceptual"
        self.assertTrue(self.svc.validate(conceptual).valid)

    def test_retired_generation_context_fields_are_no_longer_a_contract(self):
        """metadata stays open, so these are ordinary unknown keys rather than schema."""
        diagram = _valid_diagram()
        diagram["metadata"]["generationMode"] = "context"
        self.assertTrue(self.svc.validate(diagram).valid)

    def test_stats_counts(self):
        result = self.svc.validate(_valid_diagram())
        self.assertEqual(result.stats.node_count, 2)
        self.assertEqual(result.stats.edge_count, 1)

    def test_to_dict_serializes(self):
        data = self.svc.validate(_valid_diagram()).to_dict()
        self.assertEqual(data["level"], "pass")
        self.assertTrue(data["valid"])

    # ------------------------------------------------------------------
    # Layer 2: schema
    # ------------------------------------------------------------------

    def test_non_dict_input_fails(self):
        result = self.svc.validate([1, 2, 3])
        self.assertFalse(result.valid)
        self.assertIn("invalid_root_type", self._codes(result))

    def test_missing_required_top_level_field_fails_schema(self):
        diagram = _valid_diagram()
        del diagram["name"]
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertTrue(
            any(i.layer == ValidationLayer.SCHEMA for i in result.issues)
        )

    def test_wrong_schema_version_const_fails(self):
        diagram = _valid_diagram()
        diagram["schemaVersion"] = "nope"
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)

    def test_schema_error_code_includes_validator(self):
        diagram = _valid_diagram()
        del diagram["name"]
        result = self.svc.validate(diagram)
        self.assertIn("schema_required", self._codes(result))

    def test_schema_invalid_nested_data_returns_errors_instead_of_raising(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["data"] = "not an object"
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("schema_type", self._codes(result))

    def test_valid_edge_route_geometry_passes_schema(self):
        diagram = _valid_diagram()
        diagram["edges"][0]["route"] = {
            "sourceAnchor": {"side": "right", "offset": 0.25},
            "targetAnchor": {"side": "left", "offset": 0.75},
            "waypoints": [{"x": 200, "y": 110}, {"x": 240, "y": 110}],
            "labelOffset": {"x": 8, "y": -16},
        }
        self.assertTrue(self.svc.validate(diagram).valid)
        diagram["edges"][0]["route"] = {
            "mode": "straight",
            "sourceAnchor": {"side": "right", "offset": 0.25},
            "targetAnchor": {"side": "left", "offset": 0.75},
        }
        self.assertTrue(self.svc.validate(diagram).valid)

    def test_invalid_edge_route_geometry_fails_schema(self):
        invalid_routes = (
            {},
            {"mode": "curved"},
            {"mode": "straight", "waypoints": [{"x": 1, "y": 2}]},
            {"sourceAnchor": {"side": "diagonal", "offset": 0.5}},
            {"targetAnchor": {"side": "left", "offset": 1.1}},
            {"waypoints": [{"x": 1}]},
            {"waypoints": []},
            {"labelOffset": {"x": 1, "y": 2, "z": 3}},
            {"unknown": True},
        )
        for route in invalid_routes:
            with self.subTest(route=route):
                diagram = _valid_diagram()
                diagram["edges"][0]["route"] = route
                result = self.svc.validate(diagram)
                self.assertFalse(result.valid)
                self.assertTrue(any(issue.layer == ValidationLayer.SCHEMA for issue in result.issues))

    def test_non_finite_numbers_are_rejected_at_their_paths(self):
        diagram = _valid_diagram()
        diagram["viewport"] = {"x": math.nan, "y": 0, "zoom": math.inf}
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        issues = {(issue.code, issue.path) for issue in result.issues}
        self.assertIn(("non_finite_number", "$.viewport.x"), issues)
        self.assertIn(("non_finite_number", "$.viewport.zoom"), issues)

    def test_multiplicity_upper_cannot_be_less_than_lower(self):
        diagram = _valid_diagram()
        diagram["edges"][0]["data"]["sourceEnd"] = {
            "multiplicity": {"lower": 2, "upper": 1},
        }
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn(
            ("invalid_multiplicity", "$.edges[0].data.sourceEnd.multiplicity"),
            {(issue.code, issue.path) for issue in result.issues},
        )

    # ------------------------------------------------------------------
    # Issue-code registry
    # ------------------------------------------------------------------

    def test_all_emitted_codes_are_registered(self):
        # One deliberately broken diagram that trips schema, structural, advisory,
        # and render-readiness codes at once, so a broad set of codes is checked.
        diagram = {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "sequence_diagram",  # unsupported type + schema enum failure
            "id": "d_messy",
            "name": "Messy",
            "metadata": {},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [
                {"id": "n1", "type": "gpNode", "position": {"x": 0, "y": 0}, "data": {"label": "A"}},
                # duplicate id + overlapping position + empty label
                {"id": "n1", "type": "gpNode", "position": {"x": 0, "y": 0}, "data": {"label": "  "}},
                # disconnected node + very long label
                {"id": "n3", "type": "gpNode", "position": {"x": 9, "y": 9}, "data": {"label": "x" * 200}},
            ],
            "edges": [
                {"id": "e1", "type": "default", "source": "n1", "target": "ghost"},  # missing target
            ],
        }
        codes = self._codes(self.svc.validate(diagram))
        self.assertTrue(codes)  # sanity: the messy diagram produced issues
        for code in codes:
            # Emitted codes are plain strings (``.value``), never enum instances,
            # and each is in the registry (or the dynamic ``schema_*`` family).
            self.assertIs(type(code), str, msg=f"{code!r} is not a plain str")
            self.assertTrue(
                ValidationCode.is_registered(code),
                msg=f"Unregistered issue code emitted: {code!r}",
            )

    def test_service_emits_no_raw_string_codes(self):
        # Guard: every ``code=`` in the service routes through ``ValidationCode`` or
        # the ``SCHEMA_CODE_PREFIX`` family, so emitted codes can't drift from the
        # registry. (``code="..."`` would be a raw literal that bypasses it.)
        from services.diagrams.validation import diagram_validation_service as module

        source = Path(module.__file__).read_text(encoding="utf-8")
        self.assertNotIn(
            'code="',
            source,
            msg="Raw string issue code found; use ValidationCode / SCHEMA_CODE_PREFIX.",
        )

    # ------------------------------------------------------------------
    # Layer 3: structure
    # ------------------------------------------------------------------

    def test_no_nodes_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"] = []
        diagram["edges"] = []
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("no_nodes", self._codes(result))

    def test_duplicate_node_id_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"][1]["id"] = "node_start"
        diagram["edges"] = []
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("duplicate_node_id", self._codes(result))

    def test_duplicate_edge_id_fails(self):
        diagram = _valid_diagram()
        diagram["edges"].append(copy.deepcopy(diagram["edges"][0]))
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("duplicate_edge_id", self._codes(result))

    def test_missing_edge_target_fails(self):
        diagram = _valid_diagram()
        diagram["edges"][0]["target"] = "node_missing"
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("missing_edge_target", self._codes(result))

    def test_empty_label_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["data"]["label"] = "   "
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("empty_node_label", self._codes(result))

    def test_invalid_size_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["width"] = -5
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("invalid_size", self._codes(result))

    def test_zero_size_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["height"] = 0
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("invalid_size", self._codes(result))

    def test_no_edges_warns_only(self):
        diagram = _valid_diagram()
        diagram["edges"] = []
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertEqual(result.level, ValidationLevel.PASS_WITH_WARNINGS)
        self.assertIn("no_edges", self._codes(result))
        self.assertIn("disconnected_node", self._codes(result))

    def test_overlapping_position_warns(self):
        diagram = _valid_diagram()
        diagram["nodes"][1]["position"] = {"x": 80, "y": 80}
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertIn("overlapping_position", self._codes(result))

    def test_same_relative_position_under_different_parents_does_not_warn(self):
        diagram = _valid_custom_diagram()
        diagram["nodes"] = [
            {"id": "p1", "type": "gpNode", "position": {"x": 0, "y": 0}, "data": {"label": "P1", "semanticType": "package"}},
            {"id": "p2", "type": "gpNode", "position": {"x": 300, "y": 0}, "data": {"label": "P2", "semanticType": "package"}},
            {"id": "c1", "type": "gpNode", "position": {"x": 20, "y": 20}, "parentId": "p1", "data": {"label": "C1", "semanticType": "class"}},
            {"id": "c2", "type": "gpNode", "position": {"x": 20, "y": 20}, "parentId": "p2", "data": {"label": "C2", "semanticType": "class"}},
        ]
        diagram["edges"] = []
        result = self.svc.validate(diagram)
        self.assertNotIn("overlapping_position", self._codes(result))
        self.assertNotIn("disconnected_node", self._codes(result))

    def test_missing_parent_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"][1]["parentId"] = "missing"
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("missing_node_parent", self._codes(result))

    def test_parent_cycle_fails(self):
        diagram = _valid_custom_diagram()
        diagram["nodes"] = [
            {"id": "a", "type": "gpNode", "position": {"x": 0, "y": 0}, "parentId": "b", "data": {"label": "A", "semanticType": "package"}},
            {"id": "b", "type": "gpNode", "position": {"x": 10, "y": 10}, "parentId": "a", "data": {"label": "B", "semanticType": "package"}},
            {"id": "child", "type": "gpNode", "position": {"x": 20, "y": 20}, "parentId": "a", "data": {"label": "Child", "semanticType": "class"}},
        ]
        diagram["edges"] = []
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        cycle_ids = {
            issue.details["nodeId"]
            for issue in result.issues
            if issue.code == "cyclic_node_parent"
        }
        self.assertEqual(cycle_ids, {"a", "b", "child"})

    # ------------------------------------------------------------------
    # Layer 4: advisory blueprint/type checks
    # ------------------------------------------------------------------

    def test_unsupported_diagram_type_fails(self):
        diagram = _valid_diagram()
        diagram["diagramType"] = "sequence_diagram"
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        # schema enum + advisory layer both flag it; advisory code is present.
        self.assertIn("unsupported_diagram_type", self._codes(result))
        issue = next(issue for issue in result.issues if issue.code == "unsupported_diagram_type")
        self.assertIn("custom", issue.message)

    def test_blueprint_key_mismatch_warns_only(self):
        diagram = _valid_diagram()
        diagram["metadata"]["blueprintKey"] = "use_case_diagram.default"
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertEqual(result.level, ValidationLevel.PASS_WITH_WARNINGS)
        self.assertIn("blueprint_key_mismatch", self._codes(result))

    def test_unexpected_node_type_warns_only(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["type"] = "legacyNode"
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertIn("unexpected_node_type", self._codes(result))

    def test_unexpected_node_semantic_type_warns_only(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["data"]["semanticType"] = "actor"
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertIn("unexpected_node_semantic_type", self._codes(result))

    def test_unexpected_edge_semantic_type_warns_only(self):
        diagram = _valid_diagram()
        diagram["edges"][0]["data"]["semanticType"] = "association"
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertIn("unexpected_edge_semantic_type", self._codes(result))

    def test_advisory_warnings_never_block(self):
        # A diagram with several advisory drifts should still be valid.
        diagram = _valid_diagram()
        diagram["metadata"]["blueprintKey"] = "bdd_diagram.default"
        diagram["nodes"][0]["data"]["semanticType"] = "block"
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertTrue(
            all(i.severity != Severity.ERROR for i in result.issues)
        )

    # ------------------------------------------------------------------
    # Layer 5: render-readiness
    # ------------------------------------------------------------------

    def test_structural_constraint_warns_but_does_not_block(self):
        # An activity diagram missing its end node trips the per-type structural critic,
        # now surfaced in Layer 4 as an advisory STRUCTURAL_CONSTRAINT warning (never blocks).
        diagram = _valid_diagram()
        diagram["nodes"][1]["data"]["semanticType"] = "opaqueAction"  # remove the sole final node
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid, msg=[i.message for i in result.issues])
        self.assertEqual(result.level, ValidationLevel.PASS_WITH_WARNINGS)
        self.assertIn(ValidationCode.STRUCTURAL_CONSTRAINT.value, self._codes(result))

    def test_custom_board_has_no_structural_constraint(self):
        # `custom` has no per-type structural rules, so a mixed-catalog board stays clean.
        result = self.svc.validate(_valid_custom_diagram())
        self.assertTrue(result.valid, msg=[i.message for i in result.issues])
        self.assertNotIn(ValidationCode.STRUCTURAL_CONSTRAINT.value, self._codes(result))

    def test_long_label_warns(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["data"]["label"] = "x" * 200
        result = self.svc.validate(diagram)
        self.assertTrue(result.valid)
        self.assertIn("long_label", self._codes(result))

    def test_label_truncated_warns_when_label_exceeds_box(self):
        diagram = _valid_diagram()
        node = diagram["nodes"][1]
        node["width"] = 60
        node["height"] = 40
        node["data"]["label"] = "A very long action label that cannot fit in a tiny box"
        result = self.svc.validate(diagram)
        # Render-readiness truncation is advisory only: still valid, but warned.
        self.assertTrue(result.valid, msg=[i.message for i in result.issues])
        self.assertIn("label_truncated", self._codes(result))

    def test_label_truncated_absent_when_label_fits(self):
        # The default valid diagram has short labels in generously sized boxes.
        result = self.svc.validate(_valid_diagram())
        self.assertNotIn("label_truncated", self._codes(result))

    def test_non_object_node_style_fails(self):
        diagram = _valid_diagram()
        diagram["nodes"][0]["style"] = "red"
        result = self.svc.validate(diagram)
        self.assertFalse(result.valid)
        self.assertIn("invalid_style", self._codes(result))
