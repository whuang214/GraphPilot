# Slice 10: Validated-Write Enforcement

## Purpose

Make "validate before write" a **structural** guarantee rather than a caller convention, without
coupling validation into `WorkspaceStorageService`. A hardening follow-on from the Epic 1 validation
review.

## Background

Path safety is already enforced structurally: every `WorkspaceStorageService` write primitive
(`write_diagram`, `write_text`, `write_bytes`) calls `resolve_safe_path` internally, and tests
prove an unsafe path is rejected. **Validation** before a write, however, was only a docstring
convention — `write_diagram`/`create_diagram` don't validate, and a note asked callers to validate
first. Both current writers (`DiagramPersistenceService.save`, `DiagramGenerationService`) do, but nothing
prevents a future caller from persisting an unvalidated diagram.

## Design

Keep validation **out** of the file layer (preserving its clean separation) and route new-diagram
writes through the existing validated funnel:

- Add `DiagramPersistenceService.create(workspace_dir, name, diagram, *, deduplicate=True)` — the mirror of
  `save()` for a *new* file: it validates and, only if valid, calls `WorkspaceStorageService.create_diagram`;
  on failure it raises `DiagramValidationError` (carrying the `ValidationResult`) and writes nothing.
- `DiagramGenerationService` writes through `self._persistence.create(...)` instead of calling
  `create_diagram` directly. It shares its `DiagramValidationService` instance with the persistence service
  so the compiled schema validator is reused. Generation keeps its own pre-save validate + refine
  loop (which raises `GenerationValidationError` with the issues); the gateway re-validates as the
  guarantee (cheap; the diagram is already valid at that point).
- `WorkspaceStorageService.create_diagram`/`write_diagram` docstrings are updated to state they are
  low-level path-safe primitives and that the validated funnel is `DiagramPersistenceService`.

## Included Work

- `backend/services/diagrams/persistence/diagram_persistence_service.py` — `DiagramValidationError`, `CreateOutcome`, and the
  `create()` method; module docstring reframed as the validated-write funnel.
- `backend/services/generation/pipeline/diagram_generation_service.py` — inject a `DiagramPersistenceService`; write via
  `create()`; swap the `WorkspaceStorageService` import for `DiagramPersistenceService`.
- `backend/services/shared/workspace_storage_service.py` — docstring notes on the two write primitives.
- `backend/tests/core/test_persistence_service.py` — `create()` tests (valid write, dedupe, overwrite, invalid
  raises + writes nothing, warning still writes, non-dict).
- Docs: `01-architecture/01-backend-architecture.md`, `02-design-and-features/02-validation-design.md`,
  `decision-decisions.md`.

## Not In Scope

- Coupling validation into `WorkspaceStorageService` (explicitly avoided).
- Changing path-safety behavior (already enforced) or the React save/overwrite path.
- A `SafePath` value-object refactor (considered in the review; not needed once writes funnel
  through `DiagramPersistenceService`).

## Target Areas

- `backend/services/diagrams/persistence/diagram_persistence_service.py`, `backend/services/generation/pipeline/diagram_generation_service.py`,
  `backend/services/shared/workspace_storage_service.py`
- `backend/tests/core/test_persistence_service.py`

## Exit Criteria

- New diagrams are written only through `DiagramPersistenceService.create`; an invalid diagram raises and
  writes nothing.
- `WorkspaceStorageService` is not coupled to `DiagramValidationService`.
- Generation behavior (naming, dedupe, refine, render, error types) is unchanged.
- Backend test suite green.

## Previous Slice

- `09-validation-contract-hygiene.md`

## Next Slice

- `11-schema-type-parity-guard.md` — guard the schema ↔ frontend-type boundary.

## Outcome

✅ Completed as planned. `DiagramPersistenceService` is now the single validated-write funnel: added
`create()` (+ `CreateOutcome` / `DiagramValidationError`), routed `diagram_generate` through it, and
documented `WorkspaceStorageService`'s writes as low-level path-safe primitives. Validation stays out of
the file layer, so the separation of concerns is preserved.

**Verification.** `python manage.py test tests.core.test_persistence_service tests.generation.test_generation_service
tests.core.test_services` → 103 passed (new `create()` tests + unchanged generation behavior). Full-suite
+ frontend verification run with the S09–S11 batch.

**Follow-up.** None.
