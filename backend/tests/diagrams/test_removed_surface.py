import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.shared.schema_registry import SchemaRegistry
from services.shared.workspace_storage_service import WorkspaceStorageService


BACKEND = Path(settings.BASE_DIR)


class ProviderPipelineRemovalTests(SimpleTestCase):
    """The provider-backed generation pipeline is gone; it must stay gone.

    GraphPilot no longer calls a model to produce a diagram: the host authors the
    semantics and the backend materializes them deterministically. Anything that
    reappears from the old pipeline is a regression, not a restoration.
    """

    def test_removed_service_packages_are_absent(self):
        for relative in (
            "services/readiness",
            "services/generation",
            "services/context",
            "services/llm",
            "services/workflow_audit",
        ):
            with self.subTest(relative=relative):
                self.assertFalse((BACKEND / relative).exists())

    def test_the_picker_resolve_route_is_absent(self):
        """A route the editor never called, for a flow nobody asked for.

        `POST /api/diagrams/resolve` mapped a browser-picked file back to its absolute
        path, because a file picker withholds it. The backend half was complete and
        tested; the frontend helper existed and was tested. **Nothing in the editor ever
        called either.** It is the workflow-audit rig's shape again — a cluster where
        every member has an importer and the whole cluster is unreachable — so the same
        guard: name it, and let the suite refuse its return.
        """
        from api import urls

        registered = {getattr(entry, "name", None) for entry in urls.urlpatterns}
        self.assertNotIn("diagram-resolve", registered)

        for relative, symbol in (
            ("api/views.py", "def diagram_resolve"),
            ("services/shared/workspace_storage_service.py", "def resolve_diagram_identity"),
        ):
            with self.subTest(relative=relative):
                self.assertNotIn(
                    symbol, (BACKEND / relative).read_text(encoding="utf-8")
                )

    def test_the_workflow_audit_rigs_frontend_half_is_absent(self):
        """The rig died in two halves, months apart, and only the first was noticed.

        `services/workflow_audit` is asserted gone above. Its browser half was not:
        `frontend/audit/` plus `playwright.audit.config.ts` survived as a closed
        subtree — the config imported the contract, the spec imported the contract,
        and nothing else imported any of the three. Every member had an importer, so
        every member looked alive, which is the same shape as `a5.f1`.

        Nothing else caught it because nothing else could: the rig sat in no tsconfig
        project, so `tsc -b` never typechecked it, and `npm run verify` runs `e2e`,
        not `e2e:audit`. It named `WorkflowAuditBrowserService` as its caller in
        `frontend/README.md` for months after that class was deleted.
        """
        frontend = BACKEND.parent / "frontend"
        for relative in ("audit", "playwright.audit.config.ts"):
            with self.subTest(relative=relative):
                self.assertFalse((frontend / relative).exists())
        scripts = json.loads((frontend / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertNotIn("e2e:audit", scripts)

    def test_removed_assets_are_absent(self):
        for relative in (
            "assets/prompts",
            "assets/readiness",
            "assets/evaluation",
            "assets/blueprints/bdd_diagram/context-examples",
            "assets/blueprints/bdd_diagram/direct-examples",
        ):
            with self.subTest(relative=relative):
                self.assertFalse((BACKEND / relative).exists())

    def test_only_the_canonical_diagram_contract_and_registered_successors_remain(self):
        identifiers = {item.schema_id for item in SchemaRegistry().list_schema_artifacts()}
        self.assertIn("graphpilot.diagram.v1", identifiers)
        for removed in (
            "graphpilot.context.evidence-manifest.v1",
            "graphpilot.context.diagram-request.v1",
            "graphpilot.context.readiness-review.v1",
            "graphpilot.context.readiness-result.v1",
            "graphpilot.direct.diagram-request.v1",
            "graphpilot.context.logical-diagram.bdd.v1",
            "graphpilot.direct.logical-diagram.bdd.v1",
        ):
            with self.subTest(schema_id=removed):
                self.assertNotIn(removed, identifiers)

    def test_only_the_canonical_and_draft_schema_files_remain(self):
        names = sorted(p.name for p in (BACKEND / "assets" / "schemas").glob("*.json"))
        self.assertEqual(names, ["diagram-draft.json", "diagram.json"])

    def test_the_retired_pipelines_storage_surface_is_gone_entirely(self):
        """This used to assert that `resolve_diagram_request_path` *rejected* a legacy
        path, which required the resolver to exist. `a5.f1` found it dead along with the
        roots beneath it, so the guard now asserts the stronger thing: no method survives
        that could address one of those files.

        The chain hid because each level had a caller. `context_root` was called by
        `evidence_root` and `diagnostics_root`; those were called by
        `evidence_manifest_path` and `readiness_diagnostics_root`; and only at the leaves
        did the callers turn out to be tests. A root with a caller is not alive until you
        ask what the caller is for.
        """
        for gone in (
            "context_root", "evidence_root", "diagram_requests_root", "diagnostics_root",
            "readiness_diagnostics_root", "evidence_manifest_path",
            "resolve_evidence_path", "resolve_diagram_request_path",
            "diagram_request_file_path",
        ):
            with self.subTest(method=gone):
                self.assertFalse(
                    hasattr(WorkspaceStorageService, gone),
                    f"{gone} is back; the retired pipeline's storage surface is closed",
                )
        # And the live ones are untouched — this must not become a test that passes
        # because the class was emptied.
        for kept in ("storage_root", "diagrams_root", "drafts_root", "diagram_file_path"):
            with self.subTest(method=kept):
                self.assertTrue(hasattr(WorkspaceStorageService, kept))
