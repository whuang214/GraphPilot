"""A note belongs beside what it annotates.

A note carries no flow, so the layout engine has nothing to rank it by and drops it
wherever the graph has room. In the hospital-portal example that was the opposite corner,
with its dashed link crossing every other edge on the way back.
"""

from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import (
    DiagramLayoutService,
    LayoutEdge,
    LayoutInputNode,
)


def _node(identifier, semantic, width=180.0, height=60.0, parent=None):
    return LayoutInputNode(
        id=identifier, semantic_type=semantic, label=identifier, width=width, height=height,
        parent_id=parent,
    )


class NotePlacementTests(SimpleTestCase):
    def setUp(self):
        self.service = DiagramLayoutService()

    def _positions(self, nodes, edges, diagram_type="bdd_diagram"):
        result = self.service.layout(diagram_type, nodes, edges)
        return {node.id: node for node in result.nodes}

    def test_a_note_is_placed_next_to_its_subject(self):
        nodes = [
            _node("a", "block"), _node("b", "block"), _node("c", "block"),
            _node("n", "note", width=200.0, height=80.0),
        ]
        edges = [
            LayoutEdge(source="a", target="b"),
            LayoutEdge(source="b", target="c"),
            LayoutEdge(source="n", target="c"),
        ]

        positions = self._positions(nodes, edges)
        note, subject, other = positions["n"], positions["c"], positions["a"]

        to_subject = abs(note.x - subject.x) + abs(note.y - subject.y)
        to_other = abs(note.x - other.x) + abs(note.y - other.y)
        self.assertLess(to_subject, to_other)

    def test_a_note_reaches_a_subject_inside_a_container(self):
        """The child's stored position is parent-relative; comparing it raw misplaces the note."""
        nodes = [
            _node("boundary", "subject", width=400.0, height=300.0),
            _node("inside", "useCase", parent="boundary"),
            _node("actor", "actor", width=60.0, height=80.0),
            _node("n", "note", width=200.0, height=80.0),
        ]
        edges = [
            LayoutEdge(source="actor", target="inside"),
            LayoutEdge(source="n", target="inside"),
        ]

        positions = self._positions(nodes, edges, diagram_type="use_case_diagram")
        note = positions["n"]
        boundary = positions["boundary"]
        inside = positions["inside"]
        subject_x = boundary.x + inside.x
        subject_y = boundary.y + inside.y

        self.assertLess(abs(note.y - subject_y), 200.0)
        self.assertLess(abs(note.x - subject_x), 700.0)

    def test_a_note_attached_to_several_elements_is_left_where_the_engine_put_it(self):
        nodes = [_node("a", "block"), _node("b", "block"), _node("n", "note")]
        edges = [
            LayoutEdge(source="a", target="b"),
            LayoutEdge(source="n", target="a"),
            LayoutEdge(source="n", target="b"),
        ]

        with_links = self._positions(nodes, edges)

        plain = self._positions(
            [_node("a", "block"), _node("b", "block"), _node("n", "note")],
            [LayoutEdge(source="a", target="b"),
             LayoutEdge(source="n", target="a"),
             LayoutEdge(source="n", target="b")],
        )
        self.assertEqual((with_links["n"].x, with_links["n"].y), (plain["n"].x, plain["n"].y))

    def test_a_diagram_without_notes_is_untouched(self):
        nodes = [_node("a", "block"), _node("b", "block")]
        edges = [LayoutEdge(source="a", target="b")]

        positions = self._positions(nodes, edges)

        self.assertEqual(set(positions), {"a", "b"})

