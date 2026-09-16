"""Tests for the canonical universal element catalog."""

from django.test import SimpleTestCase

from services.diagrams.catalog import element_catalog as cat
from services.diagrams.catalog.constants import DEFAULT_NODE_SIZES
from services.diagrams.catalog.diagram_types import (
    ACTIVITY_DIAGRAM,
    BDD_DIAGRAM,
    CUSTOM_DIAGRAM,
    SUPPORTED_DIAGRAM_TYPES,
    USE_CASE_DIAGRAM,
    get_type_profile,
)

_ACTIVITY_NODES = {
    "initialNode", "opaqueAction", "decisionNode", "mergeNode", "forkNode",
    "joinNode", "activityFinalNode", "note",
}
_USE_CASE_NODES = {"actor", "useCase", "subject", "note"}
_BDD_NODES = {"block", "note"}
_EXPECTED_EDGES = {
    ACTIVITY_DIAGRAM: {"controlFlow", "commentLink"},
    USE_CASE_DIAGRAM: {"association", "generalization", "include", "extend", "commentLink"},
    BDD_DIAGRAM: {"association", "composition", "generalization", "dependency", "commentLink"},
}


class CatalogIntegrityTests(SimpleTestCase):
    def test_control_node_defaults_leave_room_for_glyph_and_label(self):
        for semantic_type in ("initialNode", "activityFinalNode", "flowFinalNode"):
            self.assertEqual(DEFAULT_NODE_SIZES[semantic_type], (90, 60))

    def test_every_element_has_full_catalog_metadata(self):
        for semantic_type, spec in cat.ELEMENT_CATALOG.items():
            with self.subTest(semantic_type=semantic_type):
                self.assertEqual(spec.semantic_type, semantic_type)
                self.assertIn(spec.kind, ("node", "edge"))
                self.assertIn(spec.notation, ("common", "uml", "sysml"))
                self.assertTrue(spec.description.strip())
                self.assertTrue(spec.spec_ref.strip())
                self.assertTrue(spec.metamodel_form.strip())
                self.assertTrue(spec.category.strip())
                self.assertTrue(spec.valid_in)
                self.assertLessEqual(set(spec.valid_in), set(SUPPORTED_DIAGRAM_TYPES) | {CUSTOM_DIAGRAM})
                self.assertLessEqual(set(spec.authorable_in), set(spec.valid_in))
                if spec.kind == "node":
                    self.assertIn(spec.primitive, cat.RENDER_PRIMITIVES)
                else:
                    self.assertIsNone(spec.primitive)
                    self.assertIn(spec.target_marker, {"arrow", "triangle", "diamond_filled", "none"})

    def test_helpers_derive_from_catalog(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            self.assertEqual(
                cat.allowed_node_semantic_types(diagram_type),
                frozenset(
                    semantic_type for semantic_type, spec in cat.ELEMENT_CATALOG.items()
                    if spec.kind == "node" and diagram_type in spec.valid_in
                ),
            )
            self.assertEqual(
                cat.allowed_edge_semantic_types(diagram_type),
                frozenset(
                    semantic_type for semantic_type, spec in cat.ELEMENT_CATALOG.items()
                    if spec.kind == "edge" and diagram_type in spec.valid_in
                ),
            )

    def test_container_and_dashed_sets(self):
        self.assertEqual(
            cat.container_semantic_types(),
            frozenset({
                "activityPartition", "interruptibleActivityRegion", "structuredActivityNode",
                "sequenceNode", "conditionalNode", "loopNode", "expansionRegion", "subject", "package",
            }),
        )
        self.assertEqual(
            cat.dashed_edge_semantic_types(),
            frozenset({"commentLink", "include", "extend", "dependency", "connectorPropertyLink", "realization"}),
        )


class CanonicalSubsetTests(SimpleTestCase):
    def test_profiles_have_exact_core_nodes(self):
        self.assertEqual(set(get_type_profile(ACTIVITY_DIAGRAM).allowed_node_semantic_types), _ACTIVITY_NODES)
        self.assertEqual(set(get_type_profile(USE_CASE_DIAGRAM).allowed_node_semantic_types), _USE_CASE_NODES)
        self.assertEqual(set(get_type_profile(BDD_DIAGRAM).allowed_node_semantic_types), _BDD_NODES)

    def test_specialist_nodes_remain_supported_but_not_authorable(self):
        for semantic_type, diagram_type in (
            ("flowFinalNode", ACTIVITY_DIAGRAM),
            ("callBehaviorAction", ACTIVITY_DIAGRAM),
            ("activityPartition", ACTIVITY_DIAGRAM),
            ("enumeration", BDD_DIAGRAM),
            ("proxyPort", BDD_DIAGRAM),
        ):
            spec = cat.ELEMENT_CATALOG[semantic_type]
            self.assertIn(diagram_type, spec.valid_in)
            self.assertNotIn(diagram_type, spec.authorable_in)

    def test_profiles_have_exact_canonical_edges(self):
        for diagram_type, expected in _EXPECTED_EDGES.items():
            self.assertEqual(set(get_type_profile(diagram_type).allowed_edge_semantic_types), expected)

    def test_profile_coerce_defaults(self):
        expected = {
            ACTIVITY_DIAGRAM: ("opaqueAction", "controlFlow"),
            USE_CASE_DIAGRAM: ("useCase", "association"),
            BDD_DIAGRAM: ("block", "association"),
        }
        for diagram_type, defaults in expected.items():
            profile = get_type_profile(diagram_type)
            self.assertEqual((profile.default_node_semantic_type, profile.default_edge_semantic_type), defaults)


class MarkersPortsAndCustomTests(SimpleTestCase):
    def test_fixed_edge_markers_match_canonical_relationships(self):
        expected = {
            "controlFlow": (False, "arrow", "none"),
            "association": (False, "none", "none"),
            "composition": (False, "diamond_filled", "none"),
            "generalization": (False, "triangle", "none"),
            "include": (True, "arrow", "none"),
            "extend": (True, "arrow", "none"),
            "commentLink": (True, "none", "none"),
            "containment": (False, "none", "crosshair"),
            "dependency": (True, "arrow", "none"),
        }
        for semantic_type, want in expected.items():
            spec = cat.ELEMENT_CATALOG[semantic_type]
            self.assertEqual((spec.dashed, spec.target_marker, spec.source_marker), want)

    def test_core_authorable_helpers_exclude_compatibility_entries(self):
        self.assertEqual(set(cat.authorable_node_semantic_types(ACTIVITY_DIAGRAM)), _ACTIVITY_NODES)
        self.assertEqual(set(cat.authorable_node_semantic_types(BDD_DIAGRAM)), _BDD_NODES)
        self.assertEqual(set(cat.authorable_edge_semantic_types(BDD_DIAGRAM)), _EXPECTED_EDGES[BDD_DIAGRAM])
        self.assertNotIn("proxyPort", cat.authorable_node_semantic_types(CUSTOM_DIAGRAM))
        self.assertIn("class", cat.authorable_node_semantic_types(CUSTOM_DIAGRAM))

    def test_custom_type_allows_the_whole_catalog(self):
        profile = get_type_profile(CUSTOM_DIAGRAM)
        self.assertEqual(set(profile.allowed_node_semantic_types), set(cat.all_node_semantic_types()))
        self.assertEqual(set(profile.allowed_edge_semantic_types), set(cat.all_edge_semantic_types()))
        self.assertEqual(profile.notation, "mixed")

    def test_canvas_only_generics_do_not_leak_into_generatable_types(self):
        generics = {"class", "interface", "component", "package", "requirement", "realization"}
        self.assertTrue(generics <= set(cat.ELEMENT_CATALOG))
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            allowed = set(cat.allowed_node_semantic_types(diagram_type)) | set(cat.allowed_edge_semantic_types(diagram_type))
            self.assertFalse(generics & allowed)
