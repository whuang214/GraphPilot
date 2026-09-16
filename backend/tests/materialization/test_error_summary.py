"""A refusal that names four of five errors must say the fifth exists.

`validation_failed` joined every error message and sliced the result at 400 characters.
A slice is a silent edit: the last message arrived cut mid-word, and nothing in the
string said anything had been dropped. A host fixes what it can read, calls again, and
meets the same refusal -- the piece of information it needed was the piece the slice
removed.
"""

from dataclasses import dataclass

from django.test import SimpleTestCase

from services.materialization.diagram_update_service import (
    _SUMMARY_BUDGET,
    _joined_errors,
)


@dataclass(frozen=True)
class _Issue:
    message: str
    severity: str = "error"


class JoinedErrorsTests(SimpleTestCase):
    def test_a_short_list_arrives_whole(self):
        summary = _joined_errors([_Issue("no label on 'wheel'"), _Issue("'frame' is orphaned")])

        self.assertEqual(summary, "no label on 'wheel'; 'frame' is orphaned")
        self.assertNotIn("more error", summary)

    def test_what_does_not_fit_is_counted_rather_than_cut(self):
        issues = [_Issue(f"element {i:02d} is missing a label " + "x" * 40) for i in range(12)]

        summary = _joined_errors(issues)

        self.assertIn("more error", summary)
        self.assertNotIn("xx;", summary[-30:])
        # Every message that appears, appears in full.
        for issue in issues:
            if issue.message[:20] in summary:
                self.assertIn(issue.message, summary)

    def test_the_count_is_right(self):
        issues = [_Issue("y" * 150) for _ in range(5)]

        summary = _joined_errors(issues)
        kept = summary.count("y" * 150)

        self.assertIn(f"(and {5 - kept} more errors)", summary)

    def test_one_dropped_error_is_singular(self):
        issues = [_Issue("z" * 199), _Issue("z" * 199), _Issue("z" * 199)]

        self.assertIn("(and 1 more error)", _joined_errors(issues))

    def test_a_single_enormous_message_is_never_dropped_to_nothing(self):
        """The budget must not produce a refusal that names no error at all."""
        summary = _joined_errors([_Issue("q" * (_SUMMARY_BUDGET * 3))])

        self.assertIn("q" * 50, summary)
        self.assertNotIn("more error", summary)

    def test_warnings_are_not_reported_as_errors(self):
        summary = _joined_errors([
            _Issue("this one is real"),
            _Issue("advice, not a refusal", severity="warning"),
        ])

        self.assertEqual(summary, "this one is real")

    def test_no_errors_still_says_something_useful(self):
        self.assertEqual(_joined_errors([]), "The diagram did not validate.")
