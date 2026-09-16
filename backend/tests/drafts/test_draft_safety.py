"""A draft's prose is copied into a committed diagram, so it is screened."""

from django.test import SimpleTestCase

from services.drafts.draft_safety import MAX_DRAFT_BYTES, secret_findings, size_findings
from services.drafts.draft_validation_service import DraftValidationService


def _draft_with(summary):
    return {
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
                "locator": {"path": "src/a.py", "lineRange": {"start": 1, "end": 2}},
                "summary": summary,
            }
        ],
        "elements": [
            {"id": "a", "semanticType": "block", "label": "A", "assurance": "grounded", "evidenceRefs": ["ev-a"]}
        ],
        "relationships": [],
    }


class SecretScreeningTests(SimpleTestCase):
    def test_labelled_credentials_are_caught(self):
        for text in (
            "The client reads api_key = sk-live-9f3a2b7c1d4e5f6a7b8c",
            'Configured with password: "hunter2-hunter2-hunter2"',
            "Sends Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6",
            "Embeds -----BEGIN RSA PRIVATE KEY----- in the module",
            "client-secret= AbCdEf0123456789XyZ",
        ):
            with self.subTest(text=text):
                self.assertTrue(secret_findings(_draft_with(text)))

    def test_ordinary_prose_about_credentials_is_not_flagged(self):
        for text in (
            "Reads the API key from the environment and fails closed when absent.",
            "The password is hashed with bcrypt before it is stored.",
            "Authorization is checked per list before any mutation.",
            "Loads AZURE_OPENAI_API_KEY from a gitignored .env file.",
        ):
            with self.subTest(text=text):
                self.assertEqual(secret_findings(_draft_with(text)), ())

    def test_the_finding_names_the_exact_field(self):
        findings = secret_findings(_draft_with("token: api_key = sk-live-9f3a2b7c1d4e5f6a"))
        self.assertEqual(findings[0].code, "possible_secret")
        self.assertEqual(findings[0].path, "$.evidence[0].summary")

    def test_structural_fields_are_not_scanned(self):
        """IDs, paths, and semantic types are pattern-bounded and cannot hold one."""
        draft = _draft_with("Ordinary summary.")
        draft["elements"][0]["id"] = "api-key-block"
        self.assertEqual(secret_findings(draft), ())

    def test_the_request_log_is_scanned(self):
        """The most exposed field in the document, and the one the scan could not see.

        `_walk_prose` yields a string when its *key* is in the scanned set, and a string
        inside an array has no key of its own — so `requests` was invisible by
        construction. It is a verbatim user prompt, which is exactly where a pasted error
        message carrying a token ends up, and unlike a host-authored summary nobody
        composed it with care. It also reaches `metadata.requests` in a committed file.
        """
        draft = _draft_with("Ordinary summary.")
        draft["requests"] = [
            "Diagram the auth flow.",
            "It fails with Authorization: Bearer sk-live-9f3a2b7c1d4e5f6a7b8c9d",
        ]

        findings = secret_findings(draft)

        self.assertEqual([f.code for f in findings], ["possible_secret"])
        self.assertEqual(findings[0].path, "$.requests[1]")

    def test_screening_runs_as_part_of_validation(self):
        draft = _draft_with("api_key = sk-live-9f3a2b7c1d4e5f6a7b8c")
        result = DraftValidationService().validate(draft)
        self.assertFalse(result.valid)
        self.assertIn("possible_secret", {f.code for f in result.findings})


class SizeBoundTests(SimpleTestCase):
    def test_an_ordinary_draft_is_within_the_bound(self):
        self.assertEqual(size_findings(_draft_with("Short summary.")), ())

    def test_an_oversized_draft_is_refused_with_both_numbers(self):
        draft = _draft_with("x" * (MAX_DRAFT_BYTES + 1))
        findings = size_findings(draft)

        self.assertEqual(findings[0].code, "draft_too_large")
        self.assertEqual(findings[0].details["maxBytes"], MAX_DRAFT_BYTES)
        self.assertGreater(findings[0].details["actualBytes"], MAX_DRAFT_BYTES)

    def test_the_size_bound_short_circuits_the_rest_of_validation(self):
        draft = _draft_with("x" * (MAX_DRAFT_BYTES + 1))
        draft["elements"][0]["semanticType"] = "opaqueAction"

        result = DraftValidationService().validate(draft)
        self.assertEqual([f.code for f in result.findings], ["draft_too_large"])
