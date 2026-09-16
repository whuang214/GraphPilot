"""Whatever `diagram_read` can hand a host, `diagram_update` must accept back.

The edit loop is `diagram_read` -> edit the draft -> `diagram_update`. The projection
copies a saved diagram's values into the draft, so any value the *canonical* schema
permits can arrive in a draft the host never chose. If the *draft* schema then rejects
it, that diagram can be read and never written: permanently uneditable from the IDE, on
a field the host never authored and cannot fix.

That is not hypothetical. `diagram.json` allowed eleven property kinds and
`diagram-draft.json` five, so a `.gp.json` carrying `boundReference` validated, read
cleanly, projected the kind through verbatim, and refused on update with `schema_enum`
-- all six of the extra kinds did. Nothing could create one: `canonical_assembly` writes
only the five, `authoring.md` documents five, and the editor's dropdown offers five. The
enum was aspirational vocabulary, and the only thing it could do was trap a hand-edited
file. It is the same defect as `e6ba256`, where a hand-drawn edge made a diagram
uneditable, in a different field.

Stated as a subset rule rather than a count, so it keeps holding when a vocabulary
legitimately grows -- widen the canonical side alone and this fails.
"""

import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

SCHEMAS = Path(settings.BASE_DIR) / "assets" / "schemas"


def _enums(node, path=""):
    """Every `enum` in a schema, keyed by its `$defs`-relative location."""
    found = {}
    if isinstance(node, dict):
        if isinstance(node.get("enum"), list):
            found[path] = tuple(node["enum"])
        for key, value in node.items():
            found.update(_enums(value, f"{path}/{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.update(_enums(value, f"{path}/{index}"))
    return found


class ProjectionRoundTripVocabularyTests(SimpleTestCase):
    def setUp(self):
        self.canonical = _enums(json.loads((SCHEMAS / "diagram.json").read_text(encoding="utf-8")))
        self.draft = _enums(json.loads((SCHEMAS / "diagram-draft.json").read_text(encoding="utf-8")))

    def test_the_draft_accepts_every_property_kind_a_diagram_may_hold(self):
        canonical = set(self.canonical["/$defs/property/properties/kind"])
        draft = set(self.draft["/$defs/property/properties/kind"])
        unwritable = sorted(canonical - draft)

        self.assertEqual(
            unwritable, [],
            "a saved diagram may hold these, the projection will hand them to a host, and "
            "diagram_update refuses them -- that diagram can never be edited again",
        )

    def test_both_schemas_still_declare_the_kinds_this_compares(self):
        """Guard the instrument. The check above passes vacuously if either lookup

        silently returns nothing, and a `KeyError` here is the honest failure -- a
        renamed `$defs` path must break this test rather than quietly disarm it.
        """
        for name, enums in (("diagram.json", self.canonical),
                            ("diagram-draft.json", self.draft)):
            with self.subTest(schema=name):
                kinds = enums["/$defs/property/properties/kind"]
                self.assertIn("part", kinds)
                self.assertGreaterEqual(len(kinds), 5)
