"""Materialization applies the BDD notation rules rather than checking them.

The retired pipeline asked a model to produce a valid relationship end and rejected it
when it did not. These tests pin the inverse: for every relationship kind, the end this
code emits is the one the notation requires, whether or not the host described it.
"""

import copy
import json
import re

from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.rendering.diagram_render_service import DiagramRenderService
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.drafts.draft_validation_service import DraftValidationService
from services.materialization.materializer import materialize, to_logical

_DIGESTS = {"ev-a": "sha256:" + "1" * 64, "ev-b": "sha256:" + "2" * 64}


def _draft(relationships, elements=None, **overrides):
    draft = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "sample",
        "diagramType": "bdd_diagram",
        "authority": "as_implemented",
        "requests": ["Diagram it."],
        "evidence": [
            {
                "id": "ev-a",
                "kind": "code",
                "locator": {"path": "src/a.py", "symbol": "A", "lineRange": {"start": 1, "end": 9}},
                "summary": "A is defined here.",
            },
            {
                "id": "ev-b",
                "kind": "code",
                "locator": {"path": "src/b.py", "lineRange": {"start": 1, "end": 4}},
                "summary": "B is defined here.",
            },
        ],
        "elements": elements
        or [
            {"id": "whole", "semanticType": "block", "label": "Whole", "assurance": "grounded", "evidenceRefs": ["ev-a"]},
            {"id": "part", "semanticType": "block", "label": "Part", "assurance": "grounded", "evidenceRefs": ["ev-b"]},
        ],
        "relationships": relationships,
    }
    draft.update(overrides)
    return draft


def _relationship(semantic, **fields):
    base = {
        "id": "link",
        "semanticType": semantic,
        "source": "part",
        "target": "whole",
        "assurance": "grounded",
        "evidenceRefs": ["ev-a"],
    }
    base.update(fields)
    return base


def _materialize(draft):
    return materialize(draft, evidence_digests=_DIGESTS, layout_service=DiagramLayoutService())[0]


def _diamond_count(svg: str) -> int:
    """Count drawn diamond markers.

    A closed four-point path. Asserting on the payload is not enough here: the payload
    that produced two diamonds was schema-valid and read correctly.
    """
    return len(
        [
            path
            for path in re.findall(r'<path [^>]*d="([^"]+)"', svg)
            if path.count("L") == 3 and path.rstrip().endswith("Z")
        ]
    )


class RelationshipEndConstructionTests(SimpleTestCase):
    def _edge_data(self, relationship):
        return _materialize(_draft([relationship]))["edges"][0]["data"]

    def test_composition_never_sets_aggregation(self):
        """Its diamond comes from the type. Setting aggregation draws a second one.

        ``aggregation`` is how a plain ``association`` expresses composition. On a
        ``composition`` edge, whose catalog entry already carries
        ``target_marker="diamond_filled"``, it is redundant and renders a spurious
        diamond at the part. Caught by looking at a picture, not at a payload.
        """
        described = self._edge_data(
            _relationship("composition", sourceRole="parts", sourceMultiplicity={"lower": 1, "upper": "*"})
        )
        self.assertEqual(
            described["sourceEnd"], {"role": "parts", "multiplicity": {"lower": 1, "upper": "*"}}
        )
        self.assertNotIn("aggregation", described["sourceEnd"])

    def test_an_undescribed_composition_end_is_omitted_rather_than_empty(self):
        data = self._edge_data(_relationship("composition"))

        self.assertNotIn("sourceEnd", data)
        self.assertNotIn("targetEnd", data)

    def test_a_composition_renders_exactly_one_diamond_at_the_whole(self):
        for relationship in (
            _relationship("composition"),
            _relationship("composition", sourceRole="parts"),
            _relationship("composition", sourceRole="parts", sourceMultiplicity={"lower": 1, "upper": 1}),
        ):
            with self.subTest(relationship=relationship):
                canonical = _materialize(_draft([relationship]))
                self.assertEqual(_diamond_count(DiagramRenderService().to_svg(canonical)), 1)

    def test_generalization_carries_no_ends(self):
        data = self._edge_data(_relationship("generalization"))

        self.assertNotIn("sourceEnd", data)
        self.assertNotIn("targetEnd", data)

    def test_dependency_carries_no_source_end_but_may_carry_a_target_end(self):
        bare = self._edge_data(_relationship("dependency"))
        self.assertNotIn("sourceEnd", bare)

        described = self._edge_data(_relationship("dependency", targetRole="supplier"))
        self.assertNotIn("sourceEnd", described)
        self.assertEqual(described["targetEnd"], {"role": "supplier"})

    def test_association_ends_appear_only_when_described(self):
        bare = self._edge_data(_relationship("association"))
        self.assertNotIn("sourceEnd", bare)
        self.assertNotIn("targetEnd", bare)

        described = self._edge_data(
            _relationship("association", sourceRole="owner", targetMultiplicity={"lower": 0, "upper": "*"})
        )
        self.assertEqual(described["sourceEnd"], {"role": "owner"})
        self.assertEqual(described["targetEnd"], {"multiplicity": {"lower": 0, "upper": "*"}})
        self.assertNotIn("aggregation", described["sourceEnd"])

    def test_comment_link_carries_no_ends(self):
        elements = [
            {"id": "whole", "semanticType": "block", "label": "Whole", "assurance": "grounded", "evidenceRefs": ["ev-a"]},
            {"id": "part", "semanticType": "note", "label": "A remark", "assurance": "grounded", "evidenceRefs": ["ev-b"]},
        ]
        data = _materialize(_draft([_relationship("commentLink")], elements=elements))["edges"][0]["data"]

        self.assertEqual(data["semanticType"], "commentLink")
        self.assertNotIn("sourceEnd", data)
        self.assertNotIn("targetEnd", data)

    def test_every_bdd_relationship_kind_materializes_validates_and_renders(self):
        validation = DiagramValidationService()
        render = DiagramRenderService()
        for semantic in ("association", "composition", "generalization", "dependency"):
            with self.subTest(semantic=semantic):
                canonical = _materialize(_draft([_relationship(semantic)]))
                result = validation.validate(canonical)
                self.assertTrue(result.valid, msg=[i.message for i in result.issues])
                self.assertIn("<svg", render.to_svg(canonical))


class IdentityAndProvenanceTests(SimpleTestCase):
    def test_draft_ids_reach_the_canonical_diagram_unchanged(self):
        """Editing matches on identity, so a rewritten ID would break it silently."""
        canonical = _materialize(_draft([_relationship("composition", id="part-of-whole")]))

        self.assertEqual([node["id"] for node in canonical["nodes"]], ["whole", "part"])
        self.assertEqual([edge["id"] for edge in canonical["edges"]], ["part-of-whole"])

    def test_grounded_origin_names_its_evidence(self):
        canonical = _materialize(_draft([_relationship("association")]))
        origin = next(n for n in canonical["nodes"] if n["id"] == "part")["origin"]

        self.assertEqual(origin["assurance"], "grounded")
        self.assertEqual(origin["evidenceRefs"], ["ev-b"])
        self.assertEqual(origin["assumptionRefs"], [])
        self.assertIn("ev-b", origin["rationale"])

    def test_assumed_origin_names_its_assumption_and_the_diagram_lists_it(self):
        draft = _draft([_relationship("association")])
        draft["elements"][1] = {
            "id": "part",
            "semanticType": "block",
            "label": "Part",
            "assurance": "assumed",
            "assumptionRef": "asm-part-exists",
        }
        draft["assumptions"] = [
            {"id": "asm-part-exists", "statement": "Assume a part.", "reason": "Not established.", "acceptedBy": "host"}
        ]
        canonical = _materialize(draft)
        origin = next(n for n in canonical["nodes"] if n["id"] == "part")["origin"]

        self.assertEqual(origin["assurance"], "assumed")
        self.assertEqual(origin["assumptionRefs"], ["asm-part-exists"])
        self.assertEqual(origin["evidenceRefs"], [])

        # `g5`. The reference used to be all that survived: the node pointed at
        # `asm-part-exists` and the statement, the reason and who accepted it were
        # discarded, so a reader could see that an element was assumed and never learn
        # what was assumed. A dangling pointer in a shipped artifact is worse than no
        # marking at all, and the body is small — it travels with the diagram, exactly as
        # cited evidence does.
        assurance = canonical["metadata"]["assurance"]
        self.assertEqual(assurance["assumedElementIds"], ["part"])
        body, = assurance["assumptions"]
        self.assertEqual(body["id"], "asm-part-exists")
        self.assertEqual(body["acceptedBy"], "host")
        self.assertTrue(body["statement"])
        self.assertTrue(body["reason"])

    def test_an_authored_parameter_survives_to_disk(self):
        """`g11`. A host's parameters were accepted and then silently discarded.

        The draft schema asks for a plain string — `"mode: Mode"` is what an author has in
        front of them — and canonical assembly only accepted the object form the editor
        produces. So every parameter a host wrote validated, created successfully, and
        vanished: the saved diagram had `{"name": "start"}` and nothing else.

        Accepted-then-discarded is the worst of the three possible behaviours. Refusing it
        would at least have told the author.
        """
        draft = _draft([])
        draft["elements"][0]["features"] = {
            "operations": [{"name": "start", "parameters": ["mode: Mode", "force"],
                            "returnType": "Boolean"}]
        }

        node = _materialize(draft)["nodes"][0]
        operation, = node["data"]["features"]["operations"]

        self.assertEqual(operation["returnType"], "Boolean")
        self.assertEqual(
            operation["parameters"],
            [
                {"name": "mode", "direction": "in", "type": "Mode"},
                {"name": "force", "direction": "in"},
            ],
        )

    def test_evidence_is_carried_inline_with_its_digest(self):
        canonical = _materialize(_draft([_relationship("association")]))
        evidence = canonical["metadata"]["evidence"]

        self.assertEqual(canonical["metadata"]["authority"], "as_implemented")
        self.assertEqual([record["id"] for record in evidence], ["ev-a", "ev-b"])
        self.assertEqual(evidence[0]["contentDigest"], _DIGESTS["ev-a"])
        self.assertEqual(evidence[0]["locator"]["symbol"], "A")
        self.assertNotIn("symbol", evidence[1]["locator"])

    def test_a_conceptual_diagram_carries_authority_and_no_evidence(self):
        draft = _draft([_relationship("association", assurance="conceptual", evidenceRefs=[])])
        draft["authority"] = "conceptual"
        del draft["evidence"]
        for element in draft["elements"]:
            element["assurance"] = "conceptual"
            del element["evidenceRefs"]
        del draft["relationships"][0]["evidenceRefs"]

        self.assertTrue(DraftValidationService().validate(draft).valid)
        canonical = _materialize(draft)

        self.assertEqual(canonical["metadata"]["authority"], "conceptual")
        self.assertNotIn("evidence", canonical["metadata"])
        self.assertTrue(DiagramValidationService().validate(canonical).valid)


class ShapeAndDeterminismTests(SimpleTestCase):
    def test_populated_feature_compartments_survive_and_empty_ones_are_omitted(self):
        draft = _draft([_relationship("association")])
        draft["elements"][0]["features"] = {
            "properties": [{"kind": "value", "name": "mass", "type": "kg"}],
            "constraints": [{"name": "positive", "expression": "mass > 0"}],
            "operations": [],
        }
        canonical = _materialize(draft)
        features = next(n for n in canonical["nodes"] if n["id"] == "whole")["data"]["features"]

        self.assertEqual(sorted(features), ["constraints", "properties"])
        self.assertEqual(features["properties"][0]["name"], "mass")
        self.assertTrue(DiagramValidationService().validate(canonical).valid)

    def test_the_same_draft_always_produces_the_same_diagram(self):
        draft = _draft([_relationship("composition", sourceRole="parts")])

        first = _materialize(draft)
        second = _materialize(draft)
        for diagram in (first, second):
            # Every clock reading in the document, because "the same diagram" means the
            # same semantics and layout, not the same second.
            diagram["metadata"].pop("createdAt")
            diagram["metadata"].pop("updatedAt")
            for entry in diagram["metadata"].get("requests") or ():
                entry.pop("at")

        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_materialization_never_mutates_the_draft(self):
        draft = _draft([_relationship("composition")])
        before = copy.deepcopy(draft)

        _materialize(draft)

        self.assertEqual(draft, before)

    def test_the_logical_projection_carries_no_coordinates(self):
        logical = to_logical(_draft([_relationship("composition")]))

        for node in logical["nodes"]:
            self.assertNotIn("position", node)
            self.assertNotIn("width", node)

    def test_a_block_cannot_contain_another_and_the_draft_says_so(self):
        """BDD has no container element, so this is refused rather than flattened."""
        elements = [
            {"id": "whole", "semanticType": "block", "label": "Whole", "assurance": "grounded", "evidenceRefs": ["ev-a"]},
            {"id": "part", "semanticType": "block", "label": "Part", "parentId": "whole", "assurance": "grounded", "evidenceRefs": ["ev-b"]},
        ]
        result = DraftValidationService().validate(_draft([_relationship("composition")], elements=elements))

        self.assertFalse(result.valid)
        finding = next(f for f in result.findings if f.code == "containment_unsupported")
        self.assertEqual(finding.path, "$.elements[1].parentId")
        self.assertIn("no container element", finding.message)

    def test_use_case_containment_survives_into_the_canonical_diagram(self):
        draft = {
            "schemaVersion": "graphpilot.draft.v1",
            "kind": "diagramDraft",
            "diagramName": "boundary",
            "diagramType": "use_case_diagram",
            "authority": "conceptual",
            "requests": ["Diagram the actors."],
            "elements": [
                {"id": "system", "semanticType": "subject", "label": "Store", "assurance": "conceptual"},
                {"id": "browse", "semanticType": "useCase", "label": "Browse", "parentId": "system", "assurance": "conceptual"},
                {"id": "shopper", "semanticType": "actor", "label": "Shopper", "assurance": "conceptual"},
            ],
            "relationships": [
                {"id": "shopper-browses", "semanticType": "association", "source": "shopper", "target": "browse", "assurance": "conceptual"}
            ],
        }
        self.assertTrue(DraftValidationService().validate(draft).valid)

        canonical = _materialize(draft)
        contained = {node["id"]: node.get("parentId") for node in canonical["nodes"]}
        self.assertEqual(contained["browse"], "system")
        self.assertTrue(DiagramValidationService().validate(canonical).valid)
