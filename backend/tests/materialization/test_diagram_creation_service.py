"""One draft in, a saved and rendered diagram out, with no provider anywhere."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from services.diagrams.rendering.diagram_render_service import (
    DiagramRenderService,
    DiagramRenderServiceError,
)
from services.materialization.diagram_creation_service import (
    DiagramAlreadyExists,
    DiagramCreationService,
    DraftRefused,
)

#: A citation names a symbol, and the symbol has to be findable in the lines it points at
#: — so the fixture contains one. It did not: every line read `line <n>`, and the draft
#: below cites `TodoService` at lines 10–40, which was accepted because nothing compared
#: the two. Our own fixture was making the claim the product now refuses.
_SOURCE = "\n".join(
    "class TodoService:" if n == 12 else f"line {n}" for n in range(1, 61)
)


def _draft(**overrides):
    draft = {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "todo-structure",
        "diagramType": "bdd_diagram",
        "authority": "as_implemented",
        "requests": ["Make a BDD diagram of the Todo API as implemented."],
        "evidence": [
            {
                "id": "ev-service",
                "kind": "code",
                "locator": {
                    "path": "src/todo_api/services/todo_service.py",
                    "symbol": "TodoService",
                    "lineRange": {"start": 10, "end": 40},
                },
                "summary": "TodoService validates and then persists.",
            },
            {
                "id": "ev-main",
                "kind": "code",
                "locator": {"path": "src/todo_api/main.py", "lineRange": {"start": 1, "end": 20}},
                "summary": "build_application wires the repository into the service.",
            },
        ],
        "elements": [
            {
                "id": "todo-application",
                "semanticType": "block",
                "label": "TodoApiApplication",
                "assurance": "grounded",
                "evidenceRefs": ["ev-main"],
            },
            {
                "id": "todo-service",
                "semanticType": "block",
                "label": "TodoService",
                "features": {
                    "properties": [
                        {"kind": "reference", "name": "todos", "type": "TodoRepository"}
                    ]
                },
                "assurance": "grounded",
                "evidenceRefs": ["ev-service"],
            },
            {
                "id": "todo-repository",
                "semanticType": "block",
                "label": "TodoRepository",
                "assurance": "assumed",
                "assumptionRef": "asm-repository-port",
            },
        ],
        "relationships": [
            {
                "id": "service-part-of-application",
                "semanticType": "composition",
                "source": "todo-service",
                "target": "todo-application",
                "sourceRole": "todoService",
                "sourceMultiplicity": {"lower": 1, "upper": 1},
                "assurance": "grounded",
                "evidenceRefs": ["ev-main"],
            },
            {
                "id": "service-uses-repository",
                "semanticType": "dependency",
                "source": "todo-service",
                "target": "todo-repository",
                "assurance": "grounded",
                "evidenceRefs": ["ev-service"],
            },
        ],
        "assumptions": [
            {
                "id": "asm-repository-port",
                "statement": "TodoRepository is a port rather than a concrete class.",
                "reason": "Only the in-memory implementation is wired.",
                "acceptedBy": "host",
            }
        ],
    }
    draft.update(overrides)
    return draft


class DiagramCreationServiceTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        for relative in ("src/todo_api/services/todo_service.py", "src/todo_api/main.py"):
            path = self.workspace / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_SOURCE, encoding="utf-8")
        self.service = DiagramCreationService()

    def _create(self, draft=None):
        return self.service.create(str(self.workspace), draft or _draft())

    # ---- the whole path ---------------------------------------------------------

    def test_a_draft_becomes_a_saved_rendered_diagram(self):
        result = self._create()

        self.assertEqual(result.node_count, 3)
        self.assertEqual(result.edge_count, 2)
        self.assertEqual(result.warnings, ())
        self.assertTrue(result.diagram_path.is_file())
        self.assertTrue(result.svg_path.is_file())
        self.assertEqual(result.diagram_path.name, "todo-structure.gp.json")
        self.assertEqual(result.svg_path.name, "todo-structure.svg")
        self.assertIn("<svg", result.svg_path.read_text(encoding="utf-8"))

    def test_the_saved_file_is_the_canonical_diagram_with_inline_evidence(self):
        result = self._create()
        saved = json.loads(result.diagram_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["schemaVersion"], "graphpilot.diagram.v1")
        self.assertEqual(saved["diagramType"], "bdd_diagram")
        self.assertEqual(saved["metadata"]["authority"], "as_implemented")
        self.assertEqual(
            [record["id"] for record in saved["metadata"]["evidence"]], ["ev-service", "ev-main"]
        )
        self.assertTrue(
            all(record["contentDigest"].startswith("sha256:") for record in saved["metadata"]["evidence"])
        )
        assurance = saved["metadata"]["assurance"]
        self.assertEqual(assurance["assumedElementIds"], ["todo-repository"])
        # The assumption itself is on disk, not only a reference to it.
        self.assertEqual([a["id"] for a in assurance["assumptions"]], ["asm-repository-port"])
        self.assertTrue(assurance["assumptions"][0]["statement"])

    def test_draft_ids_survive_to_disk(self):
        saved = json.loads(self._create().diagram_path.read_text(encoding="utf-8"))

        self.assertEqual(
            [node["id"] for node in saved["nodes"]],
            ["todo-application", "todo-service", "todo-repository"],
        )
        self.assertEqual(
            [edge["id"] for edge in saved["edges"]],
            ["service-part-of-application", "service-uses-repository"],
        )

    def test_the_composition_part_end_is_on_disk_without_aggregation(self):
        saved = json.loads(self._create().diagram_path.read_text(encoding="utf-8"))
        composition = next(e for e in saved["edges"] if e["data"]["semanticType"] == "composition")

        self.assertEqual(
            composition["data"]["sourceEnd"],
            {"role": "todoService", "multiplicity": {"lower": 1, "upper": 1}},
        )

    def test_evidence_digests_are_taken_from_the_cited_regions(self):
        first = json.loads(self._create().diagram_path.read_text(encoding="utf-8"))
        digests = {r["id"]: r["contentDigest"] for r in first["metadata"]["evidence"]}

        # Different regions of files with identical content still differ.
        self.assertNotEqual(digests["ev-service"], digests["ev-main"])

    # ---- refusals ---------------------------------------------------------------

    def test_it_refuses_to_overwrite_an_existing_diagram(self):
        self._create()

        with self.assertRaises(DiagramAlreadyExists) as raised:
            self._create()
        self.assertTrue(raised.exception.diagram_path.is_file())

    def test_an_invalid_draft_is_refused_with_every_reason_and_writes_nothing(self):
        draft = _draft()
        draft["elements"][0]["semanticType"] = "opaqueAction"
        draft["relationships"][0]["targetRole"] = "owner"
        del draft["elements"][1]["evidenceRefs"]

        with self.assertRaises(DraftRefused) as raised:
            self._create(draft)

        codes = {finding.code for finding in raised.exception.findings}
        self.assertEqual(
            codes, {"semantic_type_unsupported", "assurance_unsupported", "notation_invalid"}
        )
        self.assertFalse((self.workspace / ".graphpilot").exists())

    def test_the_refusal_code_names_the_cause_rather_than_its_consequences(self):
        """A wrong element type also breaks every relationship touching it."""
        draft = _draft()
        draft["elements"][0]["semanticType"] = "opaqueAction"

        with self.assertRaises(DraftRefused) as raised:
            self._create(draft)

        codes = {finding.code for finding in raised.exception.findings}
        self.assertIn("notation_invalid", codes)
        self.assertEqual(raised.exception.code, "semantic_type_unsupported")

    def test_an_unresolved_reference_outranks_the_findings_it_produces(self):
        draft = _draft()
        draft["relationships"][0]["target"] = "ghost"

        with self.assertRaises(DraftRefused) as raised:
            self._create(draft)
        self.assertEqual(raised.exception.code, "unresolved_reference")

    def test_unreadable_evidence_is_refused_before_anything_is_written(self):
        draft = _draft()
        draft["evidence"][0]["locator"]["lineRange"] = {"start": 1, "end": 9999}

        with self.assertRaises(DraftRefused) as raised:
            self._create(draft)

        self.assertEqual(raised.exception.code, "evidence_unreadable")
        self.assertIn("last valid end is 60", raised.exception.findings[0].message)
        self.assertFalse((self.workspace / ".graphpilot").exists())

    # ---- degraded but successful -------------------------------------------------

    def test_a_failed_render_still_leaves_a_created_diagram(self):
        """Losing the picture does not undo the save, so the host re-renders."""
        with self.assertLogs("services.materialization.diagram_creation_service", "ERROR"), patch.object(
            DiagramRenderService, "render", side_effect=DiagramRenderServiceError("boom")
        ):
            result = self._create()

        self.assertTrue(result.diagram_path.is_file())
        self.assertIsNone(result.svg_path)
        self.assertEqual([w["code"] for w in result.warnings], ["render_failed"])
        self.assertTrue(result.warnings[0]["retryable"])

    # ---- provider-free ------------------------------------------------------------

    def test_nothing_in_the_create_path_imports_a_provider(self):
        import services.materialization.diagram_creation_service as module

        source = Path(module.__file__).read_text(encoding="utf-8")
        for banned in ("openai", "AzureOpenAI", "llm", "prompt"):
            self.assertNotIn(banned, source)

    def test_a_conceptual_draft_needs_no_source_files_at_all(self):
        draft = {
            "schemaVersion": "graphpilot.draft.v1",
            "kind": "diagramDraft",
            "diagramName": "sketch",
            "diagramType": "activity_diagram",
            "authority": "conceptual",
            "requests": ["Sketch a submission flow."],
            "elements": [
                {"id": "start", "semanticType": "initialNode", "label": "Start", "assurance": "conceptual"},
                {"id": "submit", "semanticType": "opaqueAction", "label": "Submit", "assurance": "conceptual"},
                {"id": "done", "semanticType": "activityFinalNode", "label": "Done", "assurance": "conceptual"},
            ],
            "relationships": [
                {"id": "start-submit", "semanticType": "controlFlow", "source": "start", "target": "submit", "assurance": "conceptual"},
                {"id": "submit-done", "semanticType": "controlFlow", "source": "submit", "target": "done", "assurance": "conceptual"},
            ],
        }
        result = self.service.create(str(self.workspace), draft)
        saved = json.loads(result.diagram_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["metadata"]["authority"], "conceptual")
        self.assertNotIn("evidence", saved["metadata"])
        self.assertTrue(result.svg_path.is_file())
