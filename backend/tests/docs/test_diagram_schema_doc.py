"""The canonical schema document describes the schema that exists.

`01-diagram-json-schema.md` is what someone reads to understand the file GraphPilot writes,
which makes it the worst place in the repository for a field that does not exist — and it
documented `metadata.generationMode` and `metadata.generationContext`, with `request` and
`manifest` sub-objects, as canonical rules. The provider pipeline they belonged to was
retired in `P0`; they were never removed from the document.

`a5.f2` found the same drift from the other side: the schema was silent about four fields
it does write. One document and one schema disagreeing in both directions at once is what
a hand-maintained description of a machine-readable artifact turns into.

Both examples in the document are now captured from a real committed diagram, because every
stale example in this repository was hand-written and correct on the day.
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BACKEND = Path(settings.BASE_DIR)
DOC = (
    BACKEND.parent / "docs" / "03-design" / "02-diagram-schemas" / "01-diagram-json-schema.md"
)
SCHEMA = BACKEND / "assets" / "schemas" / "diagram.json"


def _metadata_properties():
    return set(
        json.loads(SCHEMA.read_text(encoding="utf-8"))["properties"]["metadata"]["properties"]
    )


def _documented():
    """Every `metadata.<field>` the document states a rule for."""
    return set(re.findall(r"`metadata\.(\w+)`", DOC.read_text(encoding="utf-8")))


def _a_real_node_origin():
    """The `origin` off any committed diagram, found rather than named.

    This used to open `generated/kitepay-data-model/output.gp.json` by path. The generated
    pool is wiped and repopulated by every corpus run with whatever names that run's hosts
    chose, so run 5 renaming it to `kitepay-domain-structure` broke two tests that have
    nothing to do with corpus naming. What they need is *an* origin from a real diagram,
    not a particular one.
    """
    for path in sorted((BACKEND / "assets" / "blueprints").rglob("output.gp.json")):
        nodes = json.loads(path.read_text(encoding="utf-8"))["nodes"]
        if nodes and nodes[0].get("origin"):
            return nodes[0]["origin"]
    raise AssertionError("no committed diagram carries a node origin")


class DiagramSchemaDocTests(SimpleTestCase):
    def test_every_metadata_field_in_the_schema_is_documented(self):
        missing = sorted(_metadata_properties() - _documented())

        self.assertEqual(missing, [], "the schema declares these and the document does not")

    def test_the_document_describes_no_field_the_schema_lacks(self):
        invented = sorted(_documented() - _metadata_properties())

        self.assertEqual(
            invented, [], "documented as canonical and absent from the schema",
        )

    def test_the_origin_fields_it_documents_are_the_ones_a_node_carries(self):
        """The first version of this file only compared `metadata.*`, and `claimRefs[]` —
        "exact selected JSON 1 claim ID/version pairs" — sat one table below it, unchecked.

        `origin` is where the assurance model lives: it is how a reader knows whether an
        element is grounded in cited code or assumed. Documenting a field it does not have,
        while omitting `assurance` and `rationale`, is the worst version of this drift.
        """
        carried = set(_a_real_node_origin())
        text = DOC.read_text(encoding="utf-8")
        documented = {
            match.group(1)
            for match in re.finditer(r"^\|\s*`(\w+)(?:\[\])?`\s*\|", text, re.M)
        }

        for field in sorted(carried):
            with self.subTest(field=field):
                self.assertIn(
                    field, documented,
                    f"every node carries origin.{field} and the document never names it",
                )
        self.assertNotIn("claimRefs", text, "claimRefs has not existed since P0")

    def test_the_ElementOrigin_type_matches_what_a_node_carries(self):
        """The document was wrong about `origin` and so was the type describing it.

        `ElementOrigin` declared `claimRefs` — the retired JSON 1 claim pointers — and
        omitted `assurance` and `evidenceRefs`, the two fields the assurance model rests
        on. Slice 1 of this audit kept `ClaimVersionRef` because `ElementOrigin` referenced
        it, which was true and beside the point: a symbol having a live caller says nothing
        about whether the caller is correct.

        Three descriptions of one structure — the schema, the document, and this type — and
        two of them had drifted.
        """
        from services.diagrams.catalog.diagram_shapes import ElementOrigin


        self.assertEqual(
            sorted(ElementOrigin.__annotations__),
            sorted(_a_real_node_origin()),
            "the type and the diagrams disagree about what an origin is",
        )

    def test_the_examples_parse_and_use_only_real_fields(self):
        """A JSON example is the part people copy, so it is the part worth checking."""
        text = DOC.read_text(encoding="utf-8")
        blocks = re.findall(r"```json\n(.*?)```", text, re.S)
        self.assertTrue(blocks, "the schema document should show the shape it describes")

        allowed = _metadata_properties()
        for block in blocks:
            try:
                document = json.loads(block)
            except json.JSONDecodeError:
                continue  # A fragment illustrating one field, not a whole document.
            metadata = document.get("metadata") if isinstance(document, dict) else None
            if not isinstance(metadata, dict):
                continue
            with self.subTest(keys=sorted(metadata)):
                self.assertEqual(sorted(set(metadata) - allowed), [])
