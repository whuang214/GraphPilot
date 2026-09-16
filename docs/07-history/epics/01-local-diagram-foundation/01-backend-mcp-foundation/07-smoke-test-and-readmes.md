# Slice 07: Smoke Test and READMEs

## Purpose

Make Epic 1 understandable and runnable end-to-end for a developer.

## Included Work

- document backend startup
- document MCP startup
- document schema and blueprint artifact locations
- add a manual Epic 1 smoke-test checklist
- document known Epic 1 limitations
- update README files that became inaccurate during Epic 1 implementation

## Not In Scope

- frontend startup or browser UI flows (deferred to Epic 2)
- broad project-wide docs unrelated to Epic 1
- future-epic setup instructions

## Target Areas

- root README if needed
- `docs/README.md`
- `backend/README.md`
- Epic 1 doc set and current-state tracking

## Exit Criteria

- a developer can follow the docs and run the Epic 1 backend and MCP foundation without guessing
- the smoke test covers backend and MCP startup plus the key Epic 1 flows
- README navigation remains accurate

## Previous Slice

- `06-mcp-tool-surface.md`

## Outcome

✅ Completed as planned. Documented how to run the two Epic 1 runtimes (Django API + stdio MCP server), added an Epic 1 smoke-test checklist, and documented known Epic 1 limitations in `backend/README.md`. Added `backend/mcp_server/smoke_test.py`: a real MCP client that launches the server over stdio and exercises `diagram_list_types`, `diagram_get_schema` (success plus the unsupported-type error shape), and `diagram_validate` (a valid diagram passes; an invalid one fails with issues), asserting each result and exiting non-zero on failure. Updated `../../00-current-state.md` to mark Epic 1 complete and set Epic 2 as the active epic.

Deviation: the slice planned a "manual" smoke-test checklist; it was delivered as both a manual checklist and an automated client script, which is a superset of the planned scope. Verification: `python manage.py test` from `backend/` — 111 tests pass; `python mcp_server/smoke_test.py` — all checks pass, exit code 0. Follow-up: none for Epic 1; next work is Epic 2 Slice 01 (browser load + display).