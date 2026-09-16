"""The two boundary conditions the placement arithmetic turns on.

Both were found by mutation testing rather than by reading: flipping `<` to `<=` in
`_overlaps`, and `or` to `and` in `new_overlaps`, left the whole suite green. Coverage
did not help -- every one of those lines was already executed. They were executed only
with inputs that cannot tell the two versions apart.

Both matter more since `layout_overlap` shipped, because R2 growth now reports collisions
to a host, and a false positive there tells somebody their diagram is broken when it is
merely tidy.
"""

from django.test import SimpleTestCase

from services.materialization.geometry import GAP, _overlaps, new_overlaps, place


def _node(node_id, x, y, w=100.0, h=40.0, parent=None):
    node = {"id": node_id, "position": {"x": x, "y": y}, "width": w, "height": h}
    if parent:
        node["parentId"] = parent
    return node


class OverlapBoundaryTests(SimpleTestCase):
    """Touching is not overlapping."""

    def test_boxes_that_share_an_edge_do_not_overlap(self):
        """`<` not `<=`. A box ending at x=100 and one starting at x=100 are adjacent.

        Counting that as a collision would make `place` step past a perfectly good slot,
        and would make `layout_overlap` warn about a diagram where nothing is obscured.
        """
        left = (0.0, 0.0, 100.0, 40.0)
        touching = (100.0, 0.0, 100.0, 40.0)

        self.assertFalse(_overlaps(left, touching))
        self.assertFalse(_overlaps(touching, left))

    def test_boxes_that_share_a_horizontal_edge_do_not_overlap(self):
        self.assertFalse(_overlaps((0.0, 0.0, 100.0, 40.0), (0.0, 40.0, 100.0, 40.0)))

    def test_the_same_edge_from_the_other_side(self):
        """`_overlaps` is four comparisons and each has its own boundary.

        Three of the four were pinned by the cases above; this is the fourth. A mutation
        run still killed only three until the argument order was reversed here, which is
        the difference between testing a function and testing one of its arguments.
        """
        self.assertFalse(_overlaps((0.0, 40.0, 100.0, 40.0), (0.0, 0.0, 100.0, 40.0)))
        self.assertTrue(_overlaps((0.0, 39.0, 100.0, 40.0), (0.0, 0.0, 100.0, 40.0)))

    def test_one_pixel_of_genuine_intrusion_does_overlap(self):
        """The other side of the same boundary, so this cannot pass by never detecting."""
        self.assertTrue(_overlaps((0.0, 0.0, 100.0, 40.0), (99.0, 0.0, 100.0, 40.0)))
        self.assertTrue(_overlaps((0.0, 0.0, 100.0, 40.0), (0.0, 39.0, 100.0, 40.0)))


class NewOverlapAncestorTests(SimpleTestCase):
    """A child inside its parent is containment, not a collision -- whichever way round
    the two ids happen to sort.

    `new_overlaps` walks `combinations(sorted(ids), 2)`, so for any one pair only one of
    the two `_ancestors` checks is the parent-side one. A fixture whose parent id always
    sorts first exercises one branch and never the other, which is why flipping the `or`
    to `and` survived.
    """

    def _documents(self, parent_id, child_id):
        before = {"nodes": [_node(parent_id, 0.0, 0.0, 400.0, 300.0)], "edges": []}
        after = {
            "nodes": [
                _node(parent_id, 0.0, 0.0, 400.0, 300.0),
                _node(child_id, 20.0, 20.0, 100.0, 40.0, parent=parent_id),
            ],
            "edges": [],
        }
        return before, after

    def test_containment_is_not_a_collision_when_the_parent_sorts_first(self):
        before, after = self._documents("aaa-parent", "zzz-child")

        self.assertEqual(new_overlaps(before, after), [])

    def test_containment_is_not_a_collision_when_the_child_sorts_first(self):
        """The branch the fixtures never reached."""
        before, after = self._documents("zzz-parent", "aaa-child")

        self.assertEqual(new_overlaps(before, after), [])

    def test_two_unrelated_boxes_that_now_sit_on_each_other_are_reported(self):
        """So the pair above cannot pass by never reporting anything at all."""
        before = {
            "nodes": [_node("one", 0.0, 0.0), _node("two", 400.0, 0.0)],
            "edges": [],
        }
        after = {
            "nodes": [_node("one", 0.0, 0.0, 500.0, 40.0), _node("two", 400.0, 0.0)],
            "edges": [],
        }

        self.assertEqual(new_overlaps(before, after), [("one", "two")])

    def test_a_collision_that_already_existed_is_not_reported_as_new(self):
        stacked = {
            "nodes": [_node("one", 0.0, 0.0), _node("two", 10.0, 0.0)],
            "edges": [],
        }

        self.assertEqual(new_overlaps(stacked, stacked), [])


class PlacementUsesTheBoundaryTests(SimpleTestCase):
    def test_a_new_node_may_be_placed_flush_against_an_existing_one(self):
        """Ties the boundary back to the behaviour that depends on it."""
        occupied = {"there": (0.0, 0.0, 100.0, 40.0)}

        x, y = place("new", 100.0, 40.0, edges=[], occupied=occupied)

        self.assertFalse(_overlaps((x, y, 100.0, 40.0), occupied["there"]))
        self.assertGreaterEqual(y, 40.0 + GAP - 0.001)
