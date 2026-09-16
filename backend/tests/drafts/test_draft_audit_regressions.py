"""Regressions for defects the A0 audit found.

Each of these passed the 495-test suite and was only exposed by deliberately probing an
edge case. They are kept together so the class of mistake stays visible: none of them
were type errors or crashes — every one was a rule that quietly accepted something it
should have refused.
"""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from services.drafts.authoring_contract_service import AuthoringContractService
from services.drafts.draft_validation_service import DraftValidationService
from services.drafts.evidence_service import EvidenceService
from services.shared.workspace_storage_service import WorkspaceStorageService


def _draft(elements, relationships, **over):
    draft = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "audit",
        "diagramType": "bdd_diagram",
        "authority": "conceptual",
        "requests": ["x"],
        "elements": [{**e, "assurance": "conceptual"} for e in elements],
        "relationships": [{**r, "assurance": "conceptual"} for r in relationships],
    }
    draft.update(over)
    return draft


def _block(identifier, **kw):
    return {"id": identifier, "semanticType": "block", "label": identifier.title(), **kw}


def _rel(kind, source, target, **kw):
    return {"id": f"r-{source}-{target}", "semanticType": kind, "source": source, "target": target, **kw}


class SelfReferenceTests(SimpleTestCase):
    def setUp(self):
        self.service = DraftValidationService()

    def test_a_self_parent_is_reported_once_not_twice(self):
        """The explicit check and the cycle walker both fired on the same path."""
        draft = _draft([_block("a", parentId="a"), _block("b")], [])

        findings = [f for f in self.service.validate(draft).findings if f.code == "cyclic_parent"]

        self.assertEqual(len(findings), 1)
        self.assertIn("cannot contain itself", findings[0].message)

    def test_irreflexive_relationships_reject_a_self_loop(self):
        for kind in ("composition", "generalization"):
            with self.subTest(kind=kind):
                draft = _draft([_block("a")], [_rel(kind, "a", "a")])
                findings = self.service.validate(draft).findings

                self.assertFalse(self.service.validate(draft).valid)
                self.assertIn("notation_invalid", {f.code for f in findings})

    def test_include_and_extend_reject_a_self_loop(self):
        for kind in ("include", "extend"):
            with self.subTest(kind=kind):
                draft = _draft(
                    [{"id": "u", "semanticType": "useCase", "label": "U"}],
                    [_rel(kind, "u", "u")],
                    request={
                        "original": "x", "goal": "y",
                        "diagramType": "use_case_diagram", "authority": "conceptual",
                    },
                )
                self.assertFalse(self.service.validate(draft).valid)

    def test_association_and_dependency_may_self_loop(self):
        """A manager who manages a colleague is the same class; that is legitimate."""
        for kind in ("association", "dependency"):
            with self.subTest(kind=kind):
                draft = _draft([_block("a")], [_rel(kind, "a", "a")])
                result = self.service.validate(draft)
                self.assertTrue(result.valid, msg=[f.message for f in result.findings])


class OrphanTests(SimpleTestCase):
    def setUp(self):
        self.service = DraftValidationService()

    def _grounded(self):
        return {
            "schemaVersion": "graphpilot.draft.v1",
            "kind": "diagramDraft",
            "diagramName": "audit",
            "diagramType": "bdd_diagram",
            "authority": "as_implemented",
            "requests": ["x"],
            "evidence": [
                {"id": "ev-a", "kind": "code",
                 "locator": {"path": "src/a.py", "lineRange": {"start": 1, "end": 2}}, "summary": "a"}
            ],
            "elements": [
                {"id": "a", "semanticType": "block", "label": "A",
                 "assurance": "grounded", "evidenceRefs": ["ev-a"]},
            ],
            "relationships": [],
        }

    def test_uncited_evidence_is_refused(self):
        """metadata.evidence means the regions the diagram was built from."""
        draft = self._grounded()
        draft["evidence"].append(
            {"id": "ev-unused", "kind": "code",
             "locator": {"path": "src/b.py", "lineRange": {"start": 1, "end": 2}}, "summary": "unused"}
        )
        findings = self.service.validate(draft).findings

        self.assertEqual([f.code for f in findings], ["orphan_evidence"])
        self.assertEqual(findings[0].path, "$.evidence[1].id")

    def test_unreferenced_assumption_is_refused(self):
        draft = self._grounded()
        draft["assumptions"] = [
            {"id": "asm-x", "statement": "s", "reason": "r", "acceptedBy": "host"}
        ]
        self.assertEqual(
            [f.code for f in self.service.validate(draft).findings], ["orphan_assumption"]
        )

    def test_a_fully_cited_draft_still_passes(self):
        self.assertTrue(self.service.validate(self._grounded()).valid)


class EmptyEvidenceFileTests(SimpleTestCase):
    def test_an_empty_file_cannot_establish_anything(self):
        """"".split("\\n") is [""], so line 1 of an empty file used to resolve."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        workspace = Path(tmp.name)
        (workspace / "empty.py").write_text("", encoding="utf-8")

        resolution = EvidenceService(WorkspaceStorageService(workspace)).resolve(
            [{"id": "ev-a", "kind": "code",
              "locator": {"path": "empty.py", "lineRange": {"start": 1, "end": 1}}, "summary": "s"}]
        )

        self.assertFalse(resolution.valid)
        self.assertEqual(resolution.findings[0].code, "evidence_unreadable")
        self.assertIn("empty", resolution.findings[0].message)

    def test_a_single_line_file_without_a_trailing_newline_still_resolves(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        workspace = Path(tmp.name)
        (workspace / "one.py").write_text("only line", encoding="utf-8")

        resolution = EvidenceService(WorkspaceStorageService(workspace)).resolve(
            [{"id": "ev-a", "kind": "code",
              "locator": {"path": "one.py", "lineRange": {"start": 1, "end": 1}}, "summary": "s"}]
        )
        self.assertTrue(resolution.valid)


class AuthoringContractSurfaceTests(SimpleTestCase):
    def test_an_unsupported_type_never_advertises_custom(self):
        """`custom` is a valid canvas to save but cannot be authored as a draft."""
        with self.assertRaises(ValueError) as raised:
            AuthoringContractService().build("sequence_diagram")

        message = str(raised.exception)
        self.assertNotIn("custom", message)
        self.assertIn("bdd_diagram", message)

    def test_custom_is_refused_rather_than_offered(self):
        with self.assertRaises(ValueError):
            AuthoringContractService().build("custom")
