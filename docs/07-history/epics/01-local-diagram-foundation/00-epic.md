# Epic 1: Local Diagram Foundation

## Goal

Build the local backend and MCP foundation for validating GraphPilot diagrams and exposing the schema/type contracts that later browser and IDE workflows will use.

## User Scenario

An IDE agent can ask the GraphPilot MCP server for the schema, list supported diagram types, and validate a diagram JSON file before it is saved or edited.

## Scope

- Django backend runs locally
- MCP server runs locally
- canonical GraphPilot JSON schema draft exists (provisional, confirmed in Epic 2)
- lightweight per-type type profile exists for the three MVP types
- provisional blueprints exist for:
  - `activity_diagram`
  - `use_case_diagram`
  - `bdd_diagram`
- file-based workspace structure is defined
- `DiagramTypeService`, `SchemaRegistry`, and `WorkspaceStorageService` foundations exist
- `DiagramValidationService` validates diagram JSON
- MCP tools implemented:
  - `diagram_get_schema`
  - `diagram_list_types`
  - `diagram_validate`
- basic README and setup notes exist

## Out of Scope

- React frontend display and editing (Epic 2)
- browser save API (`DiagramPersistenceService` / `POST /api/diagrams/save` is Epic 2)
- canonical sample diagrams (authored and confirmed in Epic 2)
- SVG rendering and export
- `diagram_generate_from_prompt`
- `diagram_render`
- `diagram_update`
- patch operations
- eval framework
- repair or autofix flows
- database persistence
- Docker

## Active Storage Convention

- workspace storage lives under `<workspace>/.graphpilot/`
- each diagram is a named file directly under `.graphpilot/` such as `order-approval.gp.json` (name chosen by the MCP server; user may rename)
- `<name>.gp.json` is the canonical saved diagram file
- `<name>.svg` is a derived artifact when rendering is in scope
- path safety is owned by `WorkspaceStorageService`

## Validation Direction

- invalid JSON is rejected by the validation path
- unsafe paths are rejected
- schema and structural errors block save
- blueprint mismatches are advisory warnings by default and do not block validation
- manual edits (including React UI saves) should not fail only because the diagram drifted from the original blueprint

## Research / Inputs

- `docs/00-product-and-requirements/02-requirements.md` — active product requirements and MVP scope.
- The research doc's original Epic 1 included React frontend display, browser save, and canonical sample JSON. In the current plan, these were deliberately moved to Epic 2 so that Epic 1 focuses on the backend + MCP foundation. This restructure is recorded in `docs/02-design-and-features/decision-decisions.md`.

## Acceptance Criteria

- Django runs locally
- MCP server runs locally
- the canonical GraphPilot JSON schema draft exists (provisional)
- provisional blueprints exist for the three MVP diagram types
- `DiagramTypeService`, `DiagramSchemaService`, and `WorkspaceStorageService` are implemented
- `DiagramValidationService` validates diagram JSON
- MCP can return schema, list diagram types, and validate a diagram
- basic setup notes exist

## Slice groups

Slices live in group folders under this epic:

- **`01-backend-mcp-foundation/`** (S01–S07) — the local backend + MCP foundation: docs/storage alignment, runtime scaffolds, contracts/schema/blueprints, core services, the validation service, the MCP tool surface, and the smoke test + READMEs.
- **`02-notation-vocabulary/`** (S08) — `02-notation-vocabulary/08-comprehensive-notation-vocabulary.md`: expands the per-type vocabulary + structural critic to the common UML 2.5.1 / SysML 1.6 tier (pairs with Epic 2's `03-comprehensive-shapes/`, which renders it). Additive; `data.semanticType` stays an open string so `custom` saves are unaffected.
- **`03-validation-hardening/`** (S09–S11) — post-review hardening of the validation subsystem (from the Epic 1 validation architecture review); all additive, with no change to what is considered valid:
  - `03-validation-hardening/09-validation-contract-hygiene.md` — prune dead `ValidationLayer` values, centralize issue codes in a `ValidationCode` registry, and correct the validation design doc.
  - `03-validation-hardening/10-validated-write-enforcement.md` — make "validate before write" structural via a validated create in `DiagramPersistenceService` (path safety is already enforced by `WorkspaceStorageService`).
  - `03-validation-hardening/11-schema-type-parity-guard.md` — a frontend parity test guarding `diagram.json` ↔ `diagram.ts` drift (no new dependency).
- **`04-universal-vocabulary/`** (S01–S13) — the shared catalog/reusable-renderer history plus the completed S12 bounded contract and S13 core-vocabulary runtime cutover. Overview + slice plan in `04-universal-vocabulary/00-group.md`.

> The notation vocabulary (S08) is later refactored into a **shared element catalog** by the `04-universal-vocabulary/` group — see `04-universal-vocabulary/00-group.md`.

## Related Docs

- `../README.md`
- `../00-current-state.md`
- `../../00-development-environment.md`
- `../../../01-architecture/00-system-design.md`
- `../../../01-architecture/01-backend-architecture.md`
- `../../../01-architecture/03-mcp-tools/README.md`
- `../../../02-design-and-features/00-diagram-json-schema.md`
- `../../../02-design-and-features/04-generation-design.md`
- `../../../02-design-and-features/decision-decisions.md`