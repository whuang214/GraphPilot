"""Text a node is responsible for drawing must fit inside it.

Every failure here is the same shape: the host supplied a field, the validator accepted
it, the `.gp.json` stores it, and the picture does not show it. That is worse than a
rejection, because nothing tells anyone it happened.

The causes were all a sizer and a drawer working the same thing out separately and
disagreeing:

  - a compartment was allocated `(1 + n) * line + 6` and drew `(1 + n) * line + 14`
  - a block's height counted *items* while the drawing wrapped them into more *lines*
  - a node's height never grew for a label too long to fit on one line
  - a note claimed its full height for text but drew that text half a fold lower
"""

import json
import re
from pathlib import Path

from django.test import SimpleTestCase

from services.diagrams.catalog.constants import (
    BDD_COMPARTMENT_LINE,
    BDD_HEADER_HEIGHT,
    FONT_SIZE,
    bdd_block_min_size,
    bdd_compartment_height,
    feature_compartments,
)
from services.diagrams.layout.diagram_layout_service import node_size
from services.diagrams.rendering.diagram_render_service import DiagramRenderService

BLUEPRINTS = Path(__file__).resolve().parents[3] / "assets" / "blueprints"
TEXT = re.compile(r"<text\b([^>]*)>([^<]*)</text>")


def _diagram(nodes, edges=(), diagram_type="bdd_diagram"):
    return {
        "schemaVersion": "graphpilot.diagram.v1", "kind": "diagram", "id": "d", "name": "t",
        "diagramType": diagram_type, "nodes": list(nodes), "edges": list(edges),
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "metadata": {"source": "test", "createdAt": "2026-01-01T00:00:00Z",
                     "updatedAt": "2026-01-01T00:00:00Z"},
    }


def _node(identifier, semantic, label, x, y, width, height, **data):
    return {
        "id": identifier, "type": "gpNode", "position": {"x": x, "y": y},
        "width": width, "height": height,
        "data": {"label": label, "semanticType": semantic, **data},
    }


def _text_bottoms(svg):
    """Every drawn string's baseline, so a caller can check it against a box."""
    rows = []
    for match in TEXT.finditer(svg):
        attrs, content = match.group(1), match.group(2)
        if not content.strip():
            continue
        rows.append((
            float(re.search(r'\by="([\d.\-]+)"', attrs).group(1)),
            content.strip(),
        ))
    return rows


class CompartmentArithmeticTests(SimpleTestCase):
    def test_the_size_of_a_compartment_matches_what_is_drawn(self):
        """The italic heading, then one line per row. Off by 8px per compartment before."""
        for items in (0, 1, 5):
            with self.subTest(items=items):
                drawn = FONT_SIZE + 2 + (1 + items) * BDD_COMPARTMENT_LINE
                self.assertEqual(bdd_compartment_height(items), drawn)

    def test_a_block_is_tall_enough_for_three_compartments(self):
        features = {
            "properties": [{"name": f"field{i}", "type": "str"} for i in range(4)],
            "operations": [{"name": "compute"}, {"name": "refresh"}],
            "constraints": [{"expression": "value > 0"}],
        }
        _width, height = bdd_block_min_size("Thing", features)

        needed = BDD_HEADER_HEIGHT + sum(
            bdd_compartment_height(len(items)) for _label, items in feature_compartments(features)
        )
        self.assertGreaterEqual(height, needed)

    def test_a_long_constraint_makes_the_block_taller_not_wider(self):
        """Width is capped, so the text wraps and the height has to absorb it."""
        short = {"constraints": [{"expression": "a > 0"}]}
        long = {"constraints": [{
            "expression": "available_balance(sender.wallet) >= amount and "
                          "recipient is not sender and the payment is idempotent"
        }]}

        short_w, short_h = bdd_block_min_size("Thing", short)
        long_w, long_h = bdd_block_min_size("Thing", long)

        self.assertLessEqual(long_w, 320)
        self.assertGreater(long_h, short_h)


class DrawnTextFitsTests(SimpleTestCase):
    def setUp(self):
        self.renderer = DiagramRenderService()

    def test_every_compartment_line_is_drawn_inside_its_block(self):
        features = {
            "properties": [{"name": "amountMinor", "type": "PositiveIntegerField"},
                           {"name": "paidAt", "type": "DateTimeField"}],
            "operations": [{"name": "isOpen"}, {"name": "isOverdue"}, {"name": "daysLate"},
                           {"name": "canRenew"}],
            "constraints": [{"expression": "renewals < MAX_RENEWALS"},
                            {"expression": "copy.book has no open Hold"}],
        }
        width, height = bdd_block_min_size("Loan", features)
        diagram = _diagram([_node("a", "block", "Loan", 0, 0, width, height, features=features)])

        svg = self.renderer.to_svg(diagram)

        for baseline, content in _text_bottoms(svg):
            self.assertLessEqual(
                baseline, height + 1,
                msg=f"{content!r} is drawn at y={baseline}, below the block's {height}px",
            )

    def test_a_long_note_grows_instead_of_losing_its_last_line(self):
        wordy = (
            "The overdue test runs twice. CheckoutForm.clean rejects it as a form error, "
            "then account_is_locked rejects it again inside check_out. Only the second pass "
            "also weighs the balance, so the two are not interchangeable."
        )
        width, height = node_size("note", wordy)
        diagram = _diagram([_node("n", "note", wordy, 0, 0, width, height)])

        svg = self.renderer.to_svg(diagram)

        drawn = _text_bottoms(svg)
        self.assertTrue(drawn)
        for baseline, content in drawn:
            self.assertLessEqual(
                baseline, height + 1,
                msg=f"{content!r} is drawn at y={baseline}, below the note's {height}px",
            )
        # And the ellipsis is not being used to hide the overflow.
        self.assertNotIn("\u2026", " ".join(content for _y, content in drawn))

    def test_a_short_label_does_not_inflate_a_node(self):
        """The growth is for wrapped text only; ordinary nodes keep their base size."""
        self.assertEqual(node_size("opaqueAction", "Save"), (160.0, 60.0))
        self.assertEqual(node_size("note", "ok"), (170.0, 80.0))

    def test_a_shape_that_labels_itself_from_below_never_grows(self):
        """An actor's name sits under the figure; extra height would distort it."""
        for semantic in ("actor", "initialNode", "activityFinalNode", "forkNode"):
            with self.subTest(semantic=semantic):
                _w, base = node_size(semantic, "x")
                _w2, tall = node_size(semantic, "a considerably longer label than that one")
                self.assertEqual(base, tall)


class CorpusTests(SimpleTestCase):
    def test_no_committed_example_draws_its_own_text_outside_itself(self):
        renderer = DiagramRenderService()
        offenders = []
        for output in sorted(BLUEPRINTS.glob("*/examples/answers/*/output.gp.json")):
            diagram = json.loads(output.read_text(encoding="utf-8"))
            boxes = {
                node["id"]: (
                    node["position"]["y"],
                    node["position"]["y"] + (node.get("height") or 0),
                )
                for node in diagram["nodes"] if not node.get("parentId")
            }
            if not boxes:
                continue
            lowest = max(bottom for _top, bottom in boxes.values())
            for baseline, content in _text_bottoms(renderer.to_svg(diagram)):
                # A label below every node is an edge label, which is allowed to sit
                # anywhere; this only catches text running off the bottom of the canvas.
                if baseline > lowest + 40:
                    offenders.append(f"{output.parent.name}: {content!r} at y={baseline}")
        self.assertEqual(offenders, [])
