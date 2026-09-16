"""`04-operation-errors.md` documents the codes that exist, and only those.

It is the public error contract — the document an integrator reads to decide what to
handle — and it was maintained by hand beside a registry of the same codes. It had drifted
to **50 codes that do not exist and 22 that were missing**, including two registered the
same week, plus one retryability value that contradicted the code.

That is the duplication this audit keeps finding, in the place it costs most: an integrator
writing a branch for `candidate_not_found` waits forever, and one that never handles
`evidence_symbol_not_in_range` meets it in production.

`d3` could not catch this. It checks that documents do not *name* things the code lacks,
across all documents generically. This is the sharper question one document owes: is the
list complete, and is each row's retryability the one the code will actually send?
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.shared.operation_problem import _RETRYABILITY, _WARNING_CODES

DOC = (
    Path(settings.BASE_DIR).parent
    / "docs" / "02-architecture" / "01-mcp-tools" / "04-operation-errors.md"
)


#: Warning codes that are `ValidationCode` members rather than hand-assembled ones, so
#: they are documented here but are not in `_WARNING_CODES`. Kept explicit so the
#: "invented" check below stays sharp instead of allowing any unknown row.
_VALIDATION_WARNINGS = frozenset({"long_label", "label_truncated", "structural_constraint"})


def _rows():
    """Every `| \\`code\\` | \\`true|false\\` |` row, whichever table it is in."""
    return {
        match.group(1): match.group(2) == "true"
        for match in re.finditer(
            r"^\|\s*`([a-z][a-z0-9_]+)`\s*\|\s*`(true|false)`\s*\|", DOC.read_text(encoding="utf-8"), re.M
        )
    }


def _warning_rows():
    """The codes in the warning table only.

    Anchored to its heading and stopped at the next one, because the retryability tables
    below use the same row shape. Matching `| \\`code\\` |` document-wide would pull in
    every refusal and make the pair of checks below pass for the wrong reason -- the
    A5 lesson about instruments that certify because they are blunt.
    """
    text = DOC.read_text(encoding="utf-8")
    start = text.index("### Successful optional/post-operation warning")
    end = text.index("\n## ", start)
    return {
        match.group(1)
        for match in re.finditer(r"^\|\s*`([a-z][a-z0-9_]+)`\s*\|", text[start:end], re.M)
    }


class OperationErrorsDocTests(SimpleTestCase):
    def test_every_registered_code_is_documented(self):
        missing = sorted(set(_RETRYABILITY) - set(_rows()))

        self.assertEqual(
            missing, [], "an integrator is never told these exist",
        )

    def test_no_documented_code_is_invented(self):
        """The failure mode that cost most: 50 rows for codes nothing can emit."""
        invented = sorted(set(_rows()) - set(_RETRYABILITY))

        self.assertEqual(
            invented, [], "documented and unreachable; a host would wait for these forever",
        )

    def test_the_documented_retryability_is_the_real_one(self):
        """`unsupported_diagram_type` was documented retryable and is not — the same
        identifier fails the same way, so a host told to try again would loop."""
        wrong = {
            code: (documented, _RETRYABILITY[code])
            for code, documented in _rows().items()
            if code in _RETRYABILITY and documented != _RETRYABILITY[code]
        }

        self.assertEqual(wrong, {}, "doc says one thing, the code sends another")

    def test_every_registered_warning_is_documented(self):
        """The refusals got a registry and this test; the warnings got neither.

        They were raw dicts built at the call site, and the warning table beside them was
        maintained by hand — the same arrangement that let the refusal table drift by 50
        codes. `layout_overlap` was added to the update service and shipped with a green
        suite and no row here, which is the drift happening again in the same document.
        """
        missing = sorted(_WARNING_CODES - set(_warning_rows()))

        self.assertEqual(
            missing, [], "arrives on a successful call and is documented nowhere",
        )

    def test_no_documented_warning_is_invented(self):
        """The other direction: a warning removed from the code and left in the table."""
        invented = sorted(set(_warning_rows()) - _WARNING_CODES - _VALIDATION_WARNINGS)

        self.assertEqual(
            invented, [], "documented as a warning and emitted by nothing",
        )

    def test_the_retired_pipeline_is_not_described_as_present(self):
        """Whole sections documented a readiness gate and a `blocked` outcome that no tool
        can return. Those are gone; this stops them coming back."""
        text = DOC.read_text(encoding="utf-8")
        for retired in ("readiness", "JSON 1", "JSON 2", "manifest", "candidate_"):
            with self.subTest(term=retired):
                # One historical aside is allowed, and it is marked as history.
                offenders = [
                    line.strip()
                    for line in text.splitlines()
                    if re.search(rf"\b{re.escape(retired)}", line, re.I)
                    and not line.lstrip().startswith("*(")
                ]
                self.assertEqual(offenders, [])
