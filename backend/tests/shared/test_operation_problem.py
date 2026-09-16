from django.test import SimpleTestCase

from services.shared.operation_problem import (
    OperationProblem,
    operation_problem,
    operation_warning,
)


class OperationProblemTests(SimpleTestCase):
    def test_serializes_required_fields_and_omits_absent_details(self):
        problem = operation_problem("unsafe_path", "Path escapes the workspace.")

        self.assertEqual(
            problem.to_dict(),
            {
                "code": "unsafe_path",
                "message": "Path escapes the workspace.",
                "retryable": True,
            },
        )

    def test_details_are_copied_and_internal_error_is_not_retryable(self):
        details = {"issues": [{"code": "invalid", "path": "$", "message": "Invalid."}]}
        problem = operation_problem("internal_error", "Internal failure.", details=details)
        serialized = problem.to_dict()
        serialized["details"]["issues"][0]["code"] = "changed"

        self.assertFalse(problem.retryable)
        self.assertEqual(problem.details["issues"][0]["code"], "invalid")

    def test_explicit_retryability_is_still_honoured(self):
        problem = operation_problem(
            "render_failed",
            "The saved diagram could not be drawn.",
            retryable=False,
            details={"stage": "svg"},
        )

        self.assertEqual(problem.to_dict()["retryable"], False)

    def test_draft_refusals_are_never_retryable(self):
        """Repeating an identical draft fails identically; the draft has to change."""
        for code in (
            "draft_invalid",
            "draft_too_large",
            "possible_secret",
            "duplicate_id",
            "unresolved_reference",
            "cyclic_parent",
            "semantic_type_unsupported",
            "containment_unsupported",
            "notation_invalid",
            "guard_required",
            "assurance_unsupported",
            "evidence_required",
            "evidence_unexpected",
            "evidence_unreadable",
            "evidence_stale",
            "orphan_evidence",
            "orphan_assumption",
            "diagram_exists",
            "unsupported_diagram_type",
        ):
            with self.subTest(code=code):
                self.assertFalse(operation_problem(code, "Refused.").retryable)

    def test_codes_from_the_retired_provider_pipeline_are_gone(self):
        """A registry that outlives its subsystem quietly legitimises dead codes."""
        for code in (
            "llm_provider_unavailable",
            "llm_refusal",
            "semantic_review_invalid",
            "readiness_review_failed",
            "generation_response_invalid",
            "request_finalized",
            "context_too_large",
        ):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    operation_problem(code, "Failure.")

    def test_unknown_code_requires_explicit_retryability(self):
        with self.assertRaises(ValueError):
            operation_problem("unknown", "Unknown.")
        self.assertIsInstance(
            operation_problem("future_code", "Future.", retryable=True),
            OperationProblem,
        )


class OperationWarningTests(SimpleTestCase):
    """A warning rides out on a *successful* call, so nothing refuses it on the way.

    That is precisely why it needs a gate at construction: `operation_problem` above has
    one and its codes stayed documented, while the warnings were raw dicts and their table
    drifted. There is no `retryable=` escape hatch here, unlike `operation_problem` --
    an unregistered warning cannot be forced through.
    """

    def test_an_unregistered_code_cannot_be_emitted(self):
        with self.assertRaises(ValueError):
            operation_warning("looks_wrong", "Something looks wrong.")

    def test_a_registered_code_carries_its_details_through(self):
        warning = operation_warning(
            "layout_overlap", "  Two boxes overlap.  ", pairs=[["a", "b"]],
        )

        self.assertEqual(
            warning,
            {"code": "layout_overlap", "message": "Two boxes overlap.", "pairs": [["a", "b"]]},
        )

    def test_an_empty_message_is_refused(self):
        with self.assertRaises(ValueError):
            operation_warning("hard_to_read", "   ")
