"""Every answer key must be producible by the pipeline it is the answer for.

An example used to be a prompt and a hand-written canonical diagram. Nothing connected
the two, so the corpus began *after* materialization and the stage where the notation
rules live — the filled diamond coming from the relationship type, edge dashing, end
policy, route mode, origin construction — was never exercised by a realistic diagram.

Each example now also carries `draft.json`: what a host should have written. These
assertions pin the transform between the two.

Deriving those drafts found three pieces of notation the committed answers used and no
draft could express — a use case's `extensionPoints`, an `extend`'s `condition` and
`extensionLocations`, and a navigable association end — plus 316 element and edge ids
that failed the draft's own slug rule. The answers were not producible by the product.
"""

import json
from pathlib import Path

from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.drafts.draft_validation_service import DraftValidationService
from services.materialization.canonical_assembly import assemble_canonical
from services.materialization.materializer import to_logical

ANSWERS = sorted(
    (Path(__file__).resolve().parents[2] / "assets" / "blueprints")
    .glob("*/examples/answers/*/output.gp.json")
)


def _semantics(diagram):
    """Everything the draft is responsible for. Geometry and timestamps are not."""
    return {
        "type": diagram["diagramType"],
        "nodes": sorted(
            (
                node["id"],
                node["data"]["semanticType"],
                node["data"].get("label", ""),
                node.get("parentId"),
                json.dumps(node["data"].get("features"), sort_keys=True),
                json.dumps(node["data"].get("extensionPoints"), sort_keys=True),
            )
            for node in diagram["nodes"]
        ),
        "edges": sorted(
            (
                edge["id"],
                edge["data"]["semanticType"],
                edge["source"],
                edge["target"],
                json.dumps(edge["data"].get("sourceEnd"), sort_keys=True),
                json.dumps(edge["data"].get("targetEnd"), sort_keys=True),
                edge["data"].get("guard"),
                edge["data"].get("condition"),
                json.dumps(edge["data"].get("extensionLocations"), sort_keys=True),
            )
            for edge in diagram["edges"]
        ),
    }


class AnswerDraftTests(SimpleTestCase):
    def test_every_answer_has_a_draft(self):
        missing = [p.parent.name for p in ANSWERS if not (p.parent / "draft.json").exists()]
        self.assertEqual(missing, [])
        self.assertEqual(len(ANSWERS), 36)

    def test_every_draft_is_one_a_host_could_submit(self):
        service = DraftValidationService()
        refused = []
        for output_path in ANSWERS:
            draft = json.loads((output_path.parent / "draft.json").read_text(encoding="utf-8"))
            findings = service.validate(draft).findings
            if findings:
                refused.append(f"{output_path.parent.name}: {findings[0].code} {findings[0].path}")
        self.assertEqual(refused, [])

    def test_materializing_each_draft_reproduces_its_answer(self):
        """The transform is pinned. Change a notation rule and this says which answers move."""
        layout = DiagramLayoutService()
        drifted = []
        for output_path in ANSWERS:
            draft = json.loads((output_path.parent / "draft.json").read_text(encoding="utf-8"))
            expected = json.loads(output_path.read_text(encoding="utf-8"))
            built, _engine = assemble_canonical(
                to_logical(draft),
                draft["diagramType"],
                draft["diagramName"],
                "test",
                layout,
            )
            if _semantics(built) != _semantics(expected):
                drifted.append(output_path.parent.name)
        self.assertEqual(drifted, [])

    def test_every_answer_carries_the_provenance_materialization_builds(self):
        """`origin` is deterministic from the draft, so an answer without one is not the
        artifact the product emits.

        All 36 lacked it until this was checked: they were hand-written before provenance
        existed, and the canonical schema still treats `origin` as optional so nothing
        complained. The round-trip above compares *semantics*, which deliberately excludes
        volatile fields — and `origin` is not volatile, it is the point.
        """
        for output_path in ANSWERS:
            diagram = json.loads(output_path.read_text(encoding="utf-8"))
            with self.subTest(example=output_path.parent.name):
                for node in diagram["nodes"]:
                    self.assertIn("origin", node, node["id"])
                    self.assertEqual(node["origin"]["assurance"], "conceptual")
                for edge in diagram["edges"]:
                    self.assertIn("origin", edge, edge["id"])

    def test_a_conceptual_draft_cites_nothing(self):
        """These describe a description, not a repository, so evidence would be a lie."""
        for output_path in ANSWERS:
            draft = json.loads((output_path.parent / "draft.json").read_text(encoding="utf-8"))
            with self.subTest(example=output_path.parent.name):
                self.assertEqual(draft["authority"], "conceptual")
                self.assertEqual(draft["evidence"], [])
                for element in draft["elements"]:
                    self.assertEqual(element["assurance"], "conceptual")
