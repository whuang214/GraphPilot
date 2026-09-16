"""Tests for the per-type example diagrams.

Each supported diagram type ships a curated pool under ``examples/answers``. These are
the fixtures confirmed against the React Flow load/edit/save round-trip, so they must
be schema-valid, pass shared validation with no blocking errors, and already be in the
canonical normalized form the frontend reverse adapter emits (notably: no empty-string
labels, which the adapter treats as absent, and no React Flow runtime-only fields).

The former direct/context *training* pools were few-shot prompt content for the
provider-backed generator. That generator is gone, so the split is too: one pool, and
nothing in it is prompt material.
"""

import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES, get_type_profile
from services.diagrams.validation.diagram_validation_service import DiagramValidationService

BLUEPRINTS_DIR = Path(settings.BASE_DIR) / "assets" / "blueprints"

EXPECTED_EVAL = 12


def _example_outputs(diagram_type: str) -> list[Path]:
    base = BLUEPRINTS_DIR / diagram_type
    return sorted((base / "examples" / "answers").glob("*/output.gp.json"))


class CanonicalSampleTests(SimpleTestCase):
    def setUp(self):
        self.svc = DiagramValidationService()

    def test_every_supported_type_has_an_example(self):
        """An answer is a draft and the diagram it produces. Nothing else.

        There used to be a `prompt.md` beside each one. It stood in for a pipeline stage
        that can never run here — prompt to draft needs a model, so it is not reproducible
        — and its request duplicated `draft.request.original`. Its other content was tags
        from the retired scoring pipeline.
        """
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                outputs = _example_outputs(diagram_type)
                self.assertTrue(outputs, msg=f"no examples/answers/<name>/output.gp.json for {diagram_type}")
                for output in outputs:
                    self.assertTrue(
                        (output.parent / "draft.json").is_file(),
                        msg=f"missing draft.json beside {output}",
                    )
                    self.assertFalse(
                        (output.parent / "prompt.md").exists(),
                        msg=f"prompt.md is retired; the request lives in the draft ({output.parent.name})",
                    )

    def test_examples_are_valid(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            for path in _example_outputs(diagram_type):
                with self.subTest(example=str(path)):
                    diagram = json.loads(path.read_text(encoding="utf-8"))
                    self.assertEqual(diagram["diagramType"], diagram_type)
                    result = self.svc.validate(diagram)
                    self.assertTrue(
                        result.valid,
                        msg=[f"{i.severity.value}:{i.code}:{i.message}" for i in result.issues],
                    )

    def test_examples_are_canonically_normalized(self):
        # The reverse adapter omits empty labels and never persists React Flow
        # runtime-only fields. Examples must already match that emitted shape so
        # an unedited load -> save round-trip is a no-op.
        runtime_only = {"selected", "dragging", "resizing", "measured", "positionAbsolute"}
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            for path in _example_outputs(diagram_type):
                with self.subTest(example=str(path)):
                    diagram = json.loads(path.read_text(encoding="utf-8"))
                    for edge in diagram["edges"]:
                        self.assertNotEqual(edge.get("label"), "", msg=f"empty label on edge {edge.get('id')}")
                    for node in diagram["nodes"]:
                        self.assertNotEqual(node["data"]["label"], "", msg=f"empty label on node {node.get('id')}")
                        self.assertFalse(runtime_only.intersection(node.keys()), msg=f"runtime field on node {node.get('id')}")
                    for edge in diagram["edges"]:
                        self.assertFalse(runtime_only.intersection(edge.keys()), msg=f"runtime field on edge {edge.get('id')}")

    def test_notes_use_comment_links_instead_of_domain_relationships(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            for path in _example_outputs(diagram_type):
                diagram = json.loads(path.read_text(encoding="utf-8"))
                note_ids = {
                    node["id"] for node in diagram["nodes"]
                    if (node.get("data") or {}).get("semanticType") == "note"
                }
                for edge in diagram["edges"]:
                    if edge.get("source") in note_ids or edge.get("target") in note_ids:
                        self.assertEqual(
                            (edge.get("data") or {}).get("semanticType"),
                            "commentLink",
                            msg=f"{path}: note edge {edge.get('id')} is not a commentLink",
                        )

    def test_decision_branches_use_structured_guards(self):
        for path in _example_outputs("activity_diagram"):
            diagram = json.loads(path.read_text(encoding="utf-8"))
            decision_ids = {
                node["id"] for node in diagram["nodes"]
                if (node.get("data") or {}).get("semanticType") == "decisionNode"
            }
            for decision_id in decision_ids:
                outgoing = [
                    edge for edge in diagram["edges"]
                    if edge.get("source") == decision_id
                    and (edge.get("data") or {}).get("semanticType") == "controlFlow"
                ]
                if len(outgoing) > 1:
                    self.assertTrue(
                        all(isinstance((edge.get("data") or {}).get("guard"), str) for edge in outgoing),
                        msg=f"{path}: decision {decision_id} has a branch without data.guard",
                    )


class ExamplePoolTests(SimpleTestCase):
    """One curated pool per type, and no residue of the retired few-shot pools."""

    def _names(self, diagram_type: str) -> set[str]:
        return {path.parent.name for path in _example_outputs(diagram_type)}

    def test_pool_counts(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(len(self._names(diagram_type)), EXPECTED_EVAL)

    def test_retired_training_pools_are_absent(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            base = BLUEPRINTS_DIR / diagram_type
            for retired in ("direct-examples", "context-examples"):
                with self.subTest(diagram_type=diagram_type, pool=retired):
                    self.assertFalse((base / retired).exists())


class VocabularyCoverageTests(SimpleTestCase):
    """Require bounded core semantic-type coverage without specialist padding."""

    def _present(self, diagram_type: str) -> tuple[set, set, set]:
        nodes, edges, stereotypes = set(), set(), set()
        for path in _example_outputs(diagram_type):
            diagram = json.loads(path.read_text(encoding="utf-8"))
            for node in diagram["nodes"]:
                data = node.get("data") or {}
                if data.get("semanticType"):
                    nodes.add(data["semanticType"])
                if data.get("stereotype"):
                    stereotypes.add(data["stereotype"])
            for edge in diagram["edges"]:
                data = edge.get("data") or {}
                if data.get("semanticType"):
                    edges.add(data["semanticType"])
                if data.get("stereotype"):
                    stereotypes.add(data["stereotype"])
        return nodes, edges, stereotypes

    def test_every_semantic_type_is_covered(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                profile = get_type_profile(diagram_type)
                nodes, edges, stereotypes = self._present(diagram_type)
                self.assertEqual(nodes, set(profile.allowed_node_semantic_types))
                self.assertEqual(edges, set(profile.allowed_edge_semantic_types))
                self.assertEqual(stereotypes, set())

    def test_samples_use_core_identities_and_derived_compartments(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            for path in _example_outputs(diagram_type):
                diagram = json.loads(path.read_text(encoding="utf-8"))
                for element in diagram["nodes"] + diagram["edges"]:
                    data = element.get("data") or {}
                    self.assertNotIn("stereotype", data, str(path))
                    self.assertNotIn("compartments", data, str(path))
                node_semantics = {(node.get("data") or {}).get("semanticType") for node in diagram["nodes"]}
                self.assertFalse({"classifier", "part", "value"} & node_semantics, str(path))
