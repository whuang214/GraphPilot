"""The frontend catalog is a hand-maintained mirror, and nothing checked it.

`frontend/src/editor/lib/elementCatalog.ts` mirrors `element_catalog.py`. It is the
riskiest duplication in the repository: the canvas and the SVG export both dispatch on it,
so a disagreement is a diagram that looks different depending on where you open it. The
conventions name canvas-to-export parity explicitly, and there were parity tests for edge
routing and for the schema types — none for this.

Two questions, and the second is the sharper one:

1. **Does the canvas know a glyph for every authorable type?** One it cannot draw appears
   as nothing.
2. **Does the mirror's own authorable set agree with the backend's, per diagram type?**
   This is where drift actually hurts: the palette offers a type `diagram_create` refuses,
   or hides one it would have accepted, and the person only finds out on the refusal.

The mirror declares things in two syntaxes — `node('opaqueAction', 'rounded-rect', …)` and
`['opaqueAction', 'rounded-rect']` — and a first version of this file matched only the
first, then a second matched *any* quoted token and passed while a type was renamed out of
its declaration. Both forms are read here, and the guard was watched failing before it was
trusted.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES
from services.diagrams.catalog.element_catalog import ELEMENT_CATALOG

MIRROR = (
    Path(settings.BASE_DIR).parent
    / "frontend" / "src" / "editor" / "lib" / "elementCatalog.ts"
)


def _text():
    return MIRROR.read_text(encoding="utf-8")


def _drawable():
    """Types the mirror gives a render primitive, in either declaration syntax."""
    text = _text()
    return (
        {m.group(1) for m in re.finditer(r"\bnode\(\s*'(\w+)'\s*,\s*'[\w-]+'", text)}
        | {m.group(1) for m in re.finditer(r"\[\s*'(\w+)'\s*,\s*'[\w-]+'\s*\]", text)}
    )


def _mirror_authorable():
    """`AUTHORABLE_NODES`, per diagram type, as the mirror declares it."""
    text = _text()
    start = text.index("const AUTHORABLE_NODES")
    block = text[start:text.index("\n}", start)]
    found = {}
    for match in re.finditer(r"(\w+):\s*new Set\(\[(.*?)\]\)", block, re.S):
        found[match.group(1)] = set(re.findall(r"'(\w+)'", match.group(2)))
    return found


def _backend_authorable(diagram_type):
    return {
        name for name, spec in ELEMENT_CATALOG.items()
        if diagram_type in (getattr(spec, "authorable_in", None) or ())
        and getattr(spec, "kind", "") == "node"
    }


class ElementCatalogParityTests(SimpleTestCase):
    def test_the_mirror_exists_and_cites_a_real_path(self):
        """It cited `backend/services/catalog/element_catalog.py` for long enough that
        nobody noticed the real file is under `services/diagrams/catalog/`."""
        self.assertTrue(MIRROR.is_file(), f"the frontend catalog moved: {MIRROR}")
        cited = re.search(r"backend/[\w/]+\.py", _text().splitlines()[0])
        self.assertIsNotNone(cited, "the mirror should say what it mirrors")
        self.assertTrue(
            (Path(settings.BASE_DIR).parent / cited.group(0)).is_file(),
            f"the mirror cites {cited.group(0)}, which does not exist",
        )

    def test_the_canvas_has_a_glyph_for_every_authorable_node(self):
        authorable = {
            name for name, spec in ELEMENT_CATALOG.items()
            if getattr(spec, "authorable_in", None) and getattr(spec, "kind", "") == "node"
        }

        missing = sorted(authorable - _drawable())

        self.assertEqual(
            missing, [], "authorable in a draft and the canvas knows no primitive for it"
        )

    def test_the_palette_offers_exactly_what_create_accepts(self):
        """Drift here is invisible until someone is refused. A palette that offers a type
        `diagram_create` rejects wastes the person's work; one that hides an accepted type
        makes the product look smaller than it is."""
        mirror = _mirror_authorable()

        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                self.assertIn(diagram_type, mirror, "the mirror has no set for this type")
                self.assertEqual(
                    sorted(mirror[diagram_type]),
                    sorted(_backend_authorable(diagram_type)),
                    "the palette and the backend disagree about what may be authored",
                )

    def test_the_split_the_header_states_is_the_split_that_exists(self):
        """A number written in a comment and checked by nothing is a number that goes
        stale — which is how the path above went wrong."""
        authorable = {n for n, s in ELEMENT_CATALOG.items() if getattr(s, "authorable_in", None)}
        header = _text()[:1000]

        self.assertEqual(len(ELEMENT_CATALOG), 98)
        self.assertEqual(len(authorable), 26)
        self.assertIn("98", header)
        self.assertIn("26", header)
