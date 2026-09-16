# Slice 04: `diagram_generate` Tool

## Purpose

Expose generation to the IDE via the `diagram_generate` MCP tool, over `DiagramGenerationService`.

## Included Work

- implement the `diagram_generate` MCP tool: inputs `prompt` / `diagramType` / `workspaceDir` / optional `style` / **optional `name`** (the caller-supplied diagram name; highest naming priority — see Slice 03); outputs `diagramPath` / `svgPath` / `editUrl`; reject unsupported type + unsafe workspace; map failures to the common error shape
- add a `diagram_generate` smoke-test check (offline, fake client)
- docs: backend README, MCP-tools, dev-environment (how to run generation)

## Not In Scope

- the example library overhaul (Slice 05); the eval framework + DOE (removed — pending an embeddings-based rebuild)
- `diagram_update` (Epic 4)

## Target Areas

- backend MCP server + smoke test + tests
- backend README, MCP-tools + dev-environment docs

## Exit Criteria

- `diagram_generate` works over MCP for all three types, returning paths + a working `editUrl`; errors use the common shape
- the smoke test passes offline (fake client)
- `python manage.py test` + the MCP smoke test pass

## Previous Slice

- `03-generation-core.md`

## Next Slice

- `05-example-library-overhaul.md`

## Outcome

✅ Completed as planned. The `diagram_generate` MCP tool now exposes `DiagramGenerationService` over MCP — returning `diagramPath` / `svgPath` / `editUrl` — with offline test coverage and updated docs.

**Delivered.**
- `diagram_generate(prompt, diagramType, workspaceDir, style?, name?)` in `mcp_server/server.py`: a thin async handler over a new module-level `DiagramGenerationService` instance (mirrors the existing `_render_service` pattern). Returns `{diagramPath, svgPath, editUrl}`.
- `editUrl` = `<GRAPHPILOT_FRONTEND_BASE_URL>/editor?diagramPath=<path>` (default base `http://localhost:5173`). The `editUrl` path uses forward slashes (`Path.as_posix()`) so the URL is valid, while `diagramPath` / `svgPath` keep native OS separators (consistent with `diagram_render`).
- Error mapping to the common shape: `unsupported_diagram_type`, `llm_not_configured`, `workspace_resolution_error`, `unsafe_path`, `invalid_workspace`, `generation_validation_failed`, `render_failed`, plus `file_service_error` / `llm_error` / `generation_failed` catch-alls.
- Offline tests in `tests/mcp_server/test_mcp_server.py` (`DiagramGenerateToolTests`, 8 tests) using `FakeLLMClient` + the grandalf layout engine: success for all three types (asserting paths + `editUrl`), optional-name precedence, delegation to the module service, and the unsupported-type / unconfigured-LLM / invalid-workspace error paths.
- `mcp_server/smoke_test.py` extended: `diagram_generate` added to the registered-tools check; an offline-safe call that asserts either a clean `llm_not_configured` error (no key) or a real generation result (paths exist + `editUrl`) when `AZURE_OPENAI_*` is set; plus an always-offline unsupported-type check.
- Docs: backend README (tool list + Slice 04 block + smoke-test description + corrected stale limitation), `docs/01-architecture/03-mcp-tools/01-diagram-tools.md` (implementation note), `docs/03-development-and-delivery/00-development-environment.md` (Azure env vars + a "Generation (Azure OpenAI)" subsection), and `backend/.env.example` (`GRAPHPILOT_FRONTEND_BASE_URL`).

**Deviations.**
- **Smoke-test wiring (agreed):** full offline happy-path coverage lives in the in-process Django test (no test-only code in `server.py`); the subprocess smoke test covers registration + the offline `llm_not_configured` / unsupported-type error shapes (and a real generate when Azure is configured).
- **Setting name:** reused the pre-existing (documented-but-unwired) `GRAPHPILOT_FRONTEND_BASE_URL` for the `editUrl` base rather than introducing a new setting, and wired it into `settings.py` + `.env.example`.
- **Extra error code:** added `invalid_workspace`, mapping the `ValueError` that an empty/whitespace `workspaceDir` raises in `WorkspaceStorageService` (not in the original error list).

**Verification.**
- `python manage.py test` → 239 passed (8 new), exit 0.
- `python mcp_server/smoke_test.py` → all checks `[PASS]`, exit 0; with `AZURE_OPENAI_*` configured locally it performed a real end-to-end generate (Azure HTTP 200) producing `<name>.gp.json` + `<name>.svg` and a working `editUrl`.

**Follow-up.** Slice 05 (example library overhaul: re-curated + training/eval split) → Slice 06 (eval framework) → Slice 07 (model-deployment DOE). *(The eval framework + DOE were later removed — deferred post-MVP, pending an embeddings-based rebuild.)*
