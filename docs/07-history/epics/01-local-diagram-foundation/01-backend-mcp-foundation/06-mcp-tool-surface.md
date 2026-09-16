# Slice 06: MCP Tool Surface

## Purpose

Expose the Epic 1 shared backend capabilities through thin MCP tools for IDE-driven validation and schema lookup workflows.

## Included Work

- implement `diagram_get_schema`
- implement `diagram_list_types`
- implement `diagram_validate`
- ensure MCP handlers call shared backend services instead of duplicating logic
- add MCP startup notes or integration notes if implementation clarifies the launch shape

## Not In Scope

- `diagram_generate`
- `diagram_render`
- `diagram_update`
- frontend-to-MCP communication

## Target Areas

- backend MCP entry points
- shared-service integration tests where needed
- MCP architecture docs if contracts are refined during implementation

## Exit Criteria

- all three Epic 1 MCP tools work through the documented entry points
- MCP handlers stay thin and service-backed
- schema, type lookup, and validate behavior are shared with the browser-facing backend core

## Next Slice

- `07-smoke-test-and-readmes.md`

## Outcome

✅ Completed as planned. Implemented `diagram_get_schema`, `diagram_list_types`, and `diagram_validate` as thin MCP tools in `backend/mcp_server/server.py`. Each handler delegates to the existing shared services (`DiagramSchemaService.get_schema_summary`, `DiagramTypeService.list_supported_types`, `DiagramValidationService.validate`) so MCP and the browser-facing API return identical results from one core. The MCP entry point now configures Django (`django.setup()` plus a backend-root `sys.path` shim) so the services can read settings when the server is launched as a script. `diagram_validate` returns the shared `ValidationResult` via `to_dict()`, and `diagram_get_schema` returns the common error shape for unsupported types. Added `backend/tests/mcp_server/test_mcp_server.py` (9 tests).

Decisions/deviations: `diagram_validate` implements the **inline JSON** input mode only for MVP; path-based validation (`diagramPath`) is deferred to the file-backed flows in later epics (it requires `WorkspaceStorageService` + workspace path safety, which those epics own). The architecture doc allows choosing one mode first. Recorded in `docs/02-design-and-features/decision-decisions.md`. The existing `health`/`echo` connectivity tools were retained.

Verification: `python manage.py test` from `backend/` — 111 tests pass (9 in `test_mcp_server.py`); tool registration confirms `diagram_get_schema`, `diagram_list_types`, and `diagram_validate` are exposed. Follow-up: Slice 07 (smoke test + READMEs).