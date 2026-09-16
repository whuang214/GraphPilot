"""Evidence is read from the exact cited lines, and freshness is scoped to them."""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.drafts.evidence_service import EvidenceService, region_digest
from services.shared.workspace_storage_service import WorkspaceStorageService

_SOURCE = "\n".join(f"line {n}" for n in range(1, 11))


def _evidence(evidence_id="ev-a", path="src/a.py", start=2, end=4):
    return {
        "id": evidence_id,
        "kind": "code",
        "locator": {"path": path, "lineRange": {"start": start, "end": end}},
        "summary": "Something.",
    }


class EvidenceServiceTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        (self.workspace / "src").mkdir()
        self._write(_SOURCE)
        self.service = EvidenceService(WorkspaceStorageService(self.workspace))

    def test_a_trailing_newline_does_not_invent_an_extra_line(self):
        """A single-host audit cited the true last line and was told the file had one
        more. `text.split("\\n")` leaves a phantom empty element for the terminating
        newline, so a 161-line file reported 162 — wrong advice inside a corrective
        message — and a citation to that phantom line was accepted."""
        body = "alpha\nbeta\ngamma\n"
        (self.workspace / "src" / "trailing.py").write_text(body, encoding="utf-8")
        cite = lambda end: [{  # noqa: E731
            "id": "ev-a", "kind": "code", "summary": "s",
            "locator": {"path": "src/trailing.py", "lineRange": {"start": 1, "end": end}},
        }]
        self.assertTrue(self.service.resolve(cite(3)).valid)
        past = self.service.resolve(cite(4))
        self.assertFalse(past.valid)
        self.assertIn("has 3 lines", past.findings[0].message)
        self.assertIn("last valid end is 3", past.findings[0].message)

    def _write(self, text):
        (self.workspace / "src" / "a.py").write_text(text, encoding="utf-8")

    def test_reads_the_cited_region_and_digests_only_that_region(self):
        resolution = self.service.resolve([_evidence()])

        self.assertTrue(resolution.valid)
        self.assertEqual(resolution.resolved[0].line_count, 3)
        self.assertEqual(
            resolution.resolved[0].content_digest,
            region_digest(["line 2", "line 3", "line 4"]),
        )

    def test_two_records_in_the_same_file_read_it_once_and_digest_differently(self):
        resolution = self.service.resolve([_evidence("ev-a", start=1, end=2), _evidence("ev-b", start=5, end=6)])

        self.assertTrue(resolution.valid)
        digests = resolution.digests()
        self.assertEqual(set(digests), {"ev-a", "ev-b"})
        self.assertNotEqual(digests["ev-a"], digests["ev-b"])

    def test_line_endings_do_not_change_the_digest(self):
        unix = self.service.resolve([_evidence()]).resolved[0].content_digest
        self._write(_SOURCE.replace("\n", "\r\n"))
        windows = self.service.resolve([_evidence()]).resolved[0].content_digest
        self.assertEqual(unix, windows)

    # ---- unreadable -------------------------------------------------------------

    def test_missing_file_is_named(self):
        resolution = self.service.resolve([_evidence(path="src/ghost.py")])
        self.assertEqual([f.code for f in resolution.findings], ["evidence_unreadable"])
        self.assertIn("src/ghost.py", resolution.findings[0].message)

    def test_a_range_past_the_end_states_the_last_valid_line(self):
        """The old surface blamed a missing digest here and sent hosts down a dead end."""
        resolution = self.service.resolve([_evidence(start=8, end=99)])

        finding = resolution.findings[0]
        self.assertEqual(finding.code, "evidence_unreadable")
        self.assertEqual(finding.path, "$.evidence[0].locator.lineRange.end")
        self.assertIn("has 10 lines", finding.message)
        self.assertIn("last valid end is 10", finding.message)
        self.assertEqual(finding.details["lineCount"], 10)

    def test_inverted_range_is_reported(self):
        resolution = self.service.resolve([_evidence(start=7, end=3)])
        self.assertEqual([f.code for f in resolution.findings], ["evidence_unreadable"])

    def test_a_path_escaping_the_workspace_is_refused(self):
        for path in ("../outside.py", "src/../../outside.py"):
            with self.subTest(path=path):
                resolution = self.service.resolve([_evidence(path=path)])
                self.assertEqual([f.code for f in resolution.findings], ["evidence_unreadable"])

    def test_one_bad_record_does_not_hide_the_others(self):
        resolution = self.service.resolve(
            [_evidence("ev-a"), _evidence("ev-b", path="src/ghost.py"), _evidence("ev-c", start=99, end=100)]
        )
        self.assertEqual(len(resolution.findings), 2)
        self.assertEqual([item.evidence_id for item in resolution.resolved], ["ev-a"])

    # ---- freshness --------------------------------------------------------------

    def _recorded(self, start=2, end=4):
        digest = self.service.resolve([_evidence(start=start, end=end)]).resolved[0].content_digest
        return [
            {
                "id": "ev-a",
                "locator": {"path": "src/a.py", "lineRange": {"start": start, "end": end}},
                "contentDigest": digest,
            }
        ]

    # ---- a citation must point at what it names -------------------------------------

    def test_a_symbol_outside_the_cited_range_is_refused(self):
        """The whole product rests on a citation pointing at what it names.

        `symbol` was accepted, stored in the saved diagram, and never compared to the
        lines beside it. A corpus run shipped three diagrams this way — one naming a test
        seventeen lines below the range it cited, so a reader following the citation
        landed on two unrelated tests and would have concluded the element was evidenced.
        """
        self._write("\n".join(["def unrelated():", "    pass", "", "def the_one():"]))
        record = _evidence(start=1, end=2)
        record["locator"]["symbol"] = "the_one"

        findings = self.service.resolve([record]).findings

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "evidence_symbol_not_in_range")
        self.assertIn("the_one", findings[0].message)
        self.assertIn("lines 1-2", findings[0].message)

    def test_a_symbol_inside_the_cited_range_resolves(self):
        self._write("\n".join(["def unrelated():", "    pass", "", "def the_one():"]))
        record = _evidence(start=3, end=4)
        record["locator"]["symbol"] = "the_one"

        self.assertTrue(self.service.resolve([record]).valid)

    def test_a_qualified_symbol_is_judged_on_its_last_segment(self):
        """`Login.submit` is a host saying *where*; only `submit` is text in the file."""
        self._write("\n".join(["const submit = () => {}", "line 2"]))
        record = _evidence(start=1, end=1)
        record["locator"]["symbol"] = "Login.submit"

        self.assertTrue(self.service.resolve([record]).valid)

    def test_a_prose_label_is_not_treated_as_a_symbol(self):
        """Much of what matters has no single name — an import block, a urlpatterns list.

        Only a bare identifier is a checkable claim. A phrase is a human label for a
        region, and refusing those would teach a host to stop supplying symbols at all,
        which costs more than the check saves.
        """
        for label in ("module docstring", "the import block", "urlpatterns list"):
            with self.subTest(symbol=label):
                record = _evidence(start=1, end=2)
                record["locator"]["symbol"] = label
                self.assertTrue(self.service.resolve([record]).valid)

    def test_a_one_word_label_that_looks_like_a_symbol_is_still_checked(self):
        """`imports` is indistinguishable from a variable called `imports`.

        The ambiguity is real and resolved towards checking, because the two costs are not
        equal: a host wrongly refused widens the range or writes "the import block" and
        moves on, while a miscitation that slips through ships a diagram that looks
        evidenced and is not.
        """
        record = _evidence(start=1, end=2)
        record["locator"]["symbol"] = "imports"

        findings = self.service.resolve([record]).findings
        self.assertEqual([f.code for f in findings], ["evidence_symbol_not_in_range"])

    def test_a_symbol_naming_the_module_itself_resolves(self):
        """`security` citing `security.py` names the file, not something inside it."""
        record = _evidence(path="src/a.py", start=1, end=2)
        record["locator"]["symbol"] = "a"

        self.assertTrue(self.service.resolve([record]).valid)

    def test_unchanged_regions_are_current(self):
        self.assertEqual(self.service.recheck(self._recorded()), ())

    def test_a_change_inside_the_cited_region_is_stale(self):
        recorded = self._recorded()
        self._write(_SOURCE.replace("line 3", "line 3 edited"))

        findings = self.service.recheck(recorded)
        self.assertEqual([f.code for f in findings], ["evidence_stale"])
        self.assertEqual(findings[0].details["evidenceId"], "ev-a")

    def test_a_change_outside_the_cited_region_is_not_stale(self):
        """The retired model fingerprinted the repository and staled on any edit."""
        recorded = self._recorded()
        self._write(_SOURCE.replace("line 9", "line 9 edited"))

        self.assertEqual(self.service.recheck(recorded), ())

    def test_an_edit_in_another_file_is_not_stale(self):
        recorded = self._recorded()
        (self.workspace / "src" / "b.py").write_text("unrelated", encoding="utf-8")

        self.assertEqual(self.service.recheck(recorded), ())

    def test_a_truncated_file_reports_the_range_rather_than_a_digest_mismatch(self):
        recorded = self._recorded(start=8, end=10)
        self._write("\n".join(f"line {n}" for n in range(1, 5)))

        findings = self.service.recheck(recorded)
        self.assertEqual([f.code for f in findings], ["evidence_stale"])
        self.assertIn("now 4 lines", findings[0].message)

    def test_a_deleted_file_is_unreadable_rather_than_stale(self):
        recorded = self._recorded()
        (self.workspace / "src" / "a.py").unlink()

        findings = self.service.recheck(recorded)
        self.assertEqual([f.code for f in findings], ["evidence_unreadable"])
