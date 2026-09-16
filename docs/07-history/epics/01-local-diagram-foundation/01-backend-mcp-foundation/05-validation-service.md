# Slice 05: Validation Service

## Purpose

Implement the shared validation behavior that supports the `diagram_validate` MCP tool and validates diagram JSON before later save, update, and render flows.

## Included Work

- implement `DiagramValidationService`
- finalize the structured validation result shape in code
- apply schema and structural validation layers
- apply the blocking `diagramType` check via the type registry
- apply non-blocking advisory type-profile checks (never block saves)
- add targeted tests for validation behavior

## Not In Scope

- save orchestration or overwrite protection (`DiagramPersistenceService` is Epic 2)
- full browser editor behavior
- SVG rendering as a completed workflow
- diagram generation and update flows
- MCP tool implementation beyond consuming the shared validation contract later

## Target Areas

- backend shared service modules
- backend tests for validation behavior
- active docs that become inaccurate during service implementation

## Exit Criteria

- invalid JSON is rejected by the Epic 1 validation path
- unsupported `diagramType` values are rejected
- schema and structural validation failures are returned in a structured result
- blueprint/type-profile advisory warnings are returned but never block validation
- validation behavior is reusable by API and MCP entry points without duplicated logic

## Next Slice

- `06-mcp-tool-surface.md`

## Outcome

✅ Completed as planned. Implemented `DiagramValidationService` in `backend/services/diagrams/validation/diagram_validation_service.py` as a lightweight class that validates an in-memory diagram dict and returns the existing `ValidationResult` contract. It runs Layer 2 (canonical JSON schema validation via the `jsonschema` `Draft202012Validator` against `graphpilot/schemas/diagram.json`), Layer 3 (structural graph validation — blocking errors plus non-blocking warnings), Layer 4 (advisory blueprint/type-profile checks via `DiagramTypeService`, blocking only on unsupported `diagramType`), and Layer 5 (basic render-readiness). A `ValidationResult.from_issues` factory was added to `validation_contract.py` to derive `valid`/`level`/`summary` (including `pass_with_warnings`) from issue severities. Advisory warnings never set `valid=False`, satisfying the "blueprint drift must not block" rule.

Decisions/deviations: Layer 2 uses the `jsonschema` library (pinned `jsonschema==4.26.0`, already present transitively via `mcp`) rather than a hand-rolled validator, so the schema artifact stays the single source of truth. The service input is an in-memory dict only — file loading and path safety stay with `WorkspaceStorageService` and the thin entry points (wired in Slice 06). Both decisions are recorded in `docs/02-design-and-features/decision-decisions.md`.

Review fixes applied post-implementation: cache the `Draft202012Validator` on the service instance (with eager `check_schema` on first build and a documented lock-free lazy-init), sort schema errors by rendered JSON path (avoids comparing mixed str/int path segments), emit specific `schema_<validator>` issue codes, simplify the finite-number check to `math.isfinite`, and attach a `path` to `disconnected_node` issues.

Verification: `python manage.py test` from `backend/` — 102 tests pass (24 in `test_validation_service.py`). Follow-up: expose `diagram_validate`/`diagram_get_schema`/`diagram_list_types` through MCP in Slice 06.