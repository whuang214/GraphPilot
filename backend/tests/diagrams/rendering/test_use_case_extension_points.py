"""A use case's extension points are drawn inside the ellipse that owns them.

`extensionPoints` became authorable in E3, and the renderer had always drawn them — a
separator, an italic heading, then the points — starting below the label and reaching
30px past the centre. Nothing sized the ellipse to hold any of that, so on the very
first diagram to use the field the compartment hung out of the bottom of the shape.

The same disagreement between a drawer and a sizer clipped every BDD block until H2
measured it, which is why this is asserted against the drawn SVG rather than the model.
"""

import json
import re

from django.test import SimpleTestCase

from services.diagrams.catalog.constants import use_case_min_size
from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.rendering.diagram_render_service import DiagramRenderService
from services.materialization.canonical_assembly import assemble_canonical

_TEXT = re.compile(r'<text\b[^>]*\by="([\d.\-]+)"[^>]*>([^<]*)</text>')


def _use_case(points, label="Complete a todo"):
    logical = {
        "nodes": [
            {"id": "actor", "semanticType": "actor", "label": "Member",
             "origin": {"assurance": "conceptual"}},
            {"id": "uc", "semanticType": "useCase", "label": label,
             "extensionPoints": points, "origin": {"assurance": "conceptual"}},
        ],
        "edges": [
            {"id": "e", "semanticType": "association", "source": "actor", "target": "uc",
             "origin": {"assurance": "conceptual"}},
        ],
    }
    diagram, _engine = assemble_canonical(
        logical, "use_case_diagram", "extension-points", "test", DiagramLayoutService()
    )
    return diagram, DiagramRenderService().to_svg(diagram)


class ExtensionPointSizingTests(SimpleTestCase):
    def test_a_use_case_without_them_keeps_its_base_size(self):
        self.assertIsNone(use_case_min_size("Complete a todo", []))
        self.assertIsNone(use_case_min_size("Complete a todo", None))
        self.assertIsNone(use_case_min_size("Complete a todo", ["   "]))

    def test_extension_points_make_the_ellipse_taller(self):
        plain, _ = _use_case([])
        extended, _ = _use_case(["after the todo is saved"])
        plain_uc = next(n for n in plain["nodes"] if n["id"] == "uc")
        extended_uc = next(n for n in extended["nodes"] if n["id"] == "uc")
        self.assertGreater(extended_uc["height"], plain_uc["height"])

    def test_every_line_is_drawn_inside_the_ellipse(self):
        diagram, svg = _use_case(["after the todo is saved", "on failure"])
        node = next(n for n in diagram["nodes"] if n["id"] == "uc")
        top = node["position"]["y"]
        bottom = top + node["height"]

        drawn = [(float(y), text.strip()) for y, text in _TEXT.findall(svg) if text.strip()]
        mine = [(y, t) for y, t in drawn
                if t in {"Complete a todo", "extension points",
                         "after the todo is saved, on failure"}]
        self.assertEqual(len(mine), 3, f"expected label, heading and points; got {drawn}")
        for y, text in mine:
            with self.subTest(text=text):
                # A baseline sits at the bottom of its glyphs, so allow the ascender.
                self.assertGreater(y - 9, top, f"{text!r} is drawn above the ellipse")
                self.assertLess(y, bottom, f"{text!r} is drawn below the ellipse")

    def test_a_long_point_widens_rather_than_overflowing(self):
        narrow = use_case_min_size("Complete a todo", ["saved"])
        wide = use_case_min_size(
            "Complete a todo", ["after the todo is saved and the reminder is cancelled"]
        )
        self.assertGreater(wide[0], narrow[0])

    def test_the_committed_worked_example_keeps_its_points_inside(self):
        """The use case example is what a host copies; it has to be right."""
        from services.drafts.authoring_contract_service import AuthoringContractService
        from services.materialization.materializer import to_logical

        draft = AuthoringContractService().build("use_case_diagram")["example"]
        diagram, _engine = assemble_canonical(
            to_logical(draft), "use_case_diagram", draft["diagramName"], "test",
            DiagramLayoutService(),
        )
        svg = DiagramRenderService().to_svg(diagram)
        withpoints = [n for n in diagram["nodes"] if (n.get("data") or {}).get("extensionPoints")]
        self.assertTrue(withpoints, "the example is supposed to demonstrate extension points")
        for node in withpoints:
            bottom = node["position"]["y"] + node["height"]
            for y, text in _TEXT.findall(svg):
                if text.strip() == "extension points":
                    self.assertLess(float(y), bottom, json.dumps(node["id"]))
