# Slice 02: Save and Validate API

## Purpose

Complete the browser-facing backend contract for save and validation behavior while keeping route handlers thin over shared services.

## Included Work

- implement `POST /api/diagrams/save`
- implement `DiagramPersistenceService` for save orchestration (validate-then-overwrite)
- ensure browser-facing route handlers call shared services instead of duplicating validation or file logic
- add integration tests for load and save behavior where appropriate
- refine API contract docs if implementation resolves any request or response ambiguity

For MVP, Epic 2 implements the required `load` + `save` route set only. `POST /api/diagrams/validate` and `GET /api/schema` / `GET /api/diagram-types` remain optional and are not in Epic 2 scope; save owns validation internally. Save does not render `diagram.svg` in Epic 2, because `DiagramRenderService` is owned by Epic 3.

## Not In Scope

- MCP tool implementation
- full browser editor feature completeness (frontend editing UI is Slice 03)
- diagram generation, rendering, or update workflows
- SVG render-on-save (deferred; `DiagramRenderService` is Epic 3)

## Target Areas

- backend API entry points
- backend integration tests for browser-facing flows
- API route docs if contracts are refined during implementation

## Exit Criteria

- the browser-facing save route uses shared backend services
- the browser-facing validate route uses shared backend services when included
- load, save, and validate behavior is reachable through the documented API surface
- API handlers stay thin and do not duplicate core business rules

## Next Slice

- `03-frontend-editing-and-save.md`

## Outcome

✅ Completed as planned. Implemented the browser-facing save contract over shared services.

**Delivered.**

- Backend: added `DiagramPersistenceService` (`services/diagrams/persistence/diagram_persistence_service.py`) — a validate-then-overwrite orchestrator that composes `WorkspaceStorageService` (workspace resolution, path safety, atomic write) and `DiagramValidationService`, returning a `SaveOutcome`. It writes only when validation passes and leaves the existing file untouched on failure.
- API: added thin `POST /api/diagrams/save` (`api/views.py`, `api/urls.py`) over `DiagramPersistenceService`. Success returns `{saved, diagramPath}` (200); blocking validation errors return the `{code: "validation_failed", message, validationErrors}` shape (422) with only `error`-severity issues; path/request problems return the common error shape (`missing_path`/`invalid_diagram`/`invalid_path`/`unsafe_path`, 400).
- Validation gating: `ValidationResult.valid` is the gate, so blueprint/type drift (warnings) does not block a save, matching the API contract.
- Tests: added `tests/core/test_persistence_service.py` (7) and a `DiagramSaveRouteTests` class in `tests/api/test_api.py` (10) covering success, overwrite, missing/invalid request fields, unsafe path, validation-failure-without-write, and warning-only drift.
- Docs: documented the save failure HTTP status (422) and the full error-case list in `docs/01-architecture/04-api-routes.md`.

**Deviations.** the optional `POST /api/diagrams/validate` route was intentionally not added (save owns validation internally; it remains out of Epic 2 scope). No SVG render-on-save seam was added, as `DiagramRenderService` is owned by Epic 3.

**Verification.** `python manage.py test` from `backend/` → 136 tests pass (17 new).

**Follow-up.** Slice 03 — frontend editing + the reverse adapter + wiring the editor to `POST /api/diagrams/save`.