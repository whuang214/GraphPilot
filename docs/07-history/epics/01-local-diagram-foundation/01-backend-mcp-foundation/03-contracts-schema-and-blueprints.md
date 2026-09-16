# Slice 03: Contracts, Schema & Blueprints

## Purpose

Define the stable shared payload shapes, schema artifact, and provisional blueprints that later backend and MCP slices will build against. The canonical sample diagrams are intentionally deferred to Epic 2, when the React Flow round-trip will confirm the real persisted shape.

## Included Work

- define the supported diagram type registry used in Epic 1
- define a lightweight per-type type profile for advisory validation warnings
- define where schema artifacts live and how they are looked up
- define the structured validation result shape used by API and MCP callers
- define the load and save request and response shapes needed by Epic 2 entry points
- create provisional blueprints for:
  - `activity_diagram`
  - `use_case_diagram`
  - `bdd_diagram`
- document where schema artifacts and blueprints live

## Not In Scope

- canonical sample diagrams (deferred to Epic 2)
- `DiagramSchemaService`, `DiagramTypeService`, or `WorkspaceStorageService` implementation (Slice 04)
- `DiagramValidationService` implementation (Slice 05)
- MCP tool implementation (Slice 06)
- full frontend editor behavior
- SVG rendering as a completed workflow
- generation or update flows beyond Epic 1 scope

## Target Areas

- backend schema and blueprint areas
- shared contract dataclasses in `services/`
- active docs that describe the canonical schema and blueprint shape
- tests that lock the contracts and provisional blueprints

## Exit Criteria

- supported types are defined from one documented location
- each supported type has a lightweight type profile
- schema lookup rules are documented clearly enough for implementation
- the validation result shape is defined for both API and MCP callers
- the load and save request/response shapes are defined for Epic 2
- all three Epic 1 provisional blueprints exist and parse against the blueprint schema
- backend and MCP implementation can use the same type, schema, and contract assumptions

## Next Slice

- `04-core-services-type-schema-file.md`

## Outcome

✅ Completed as planned. Re-scoped Slice 03 to "Contracts, Schema & Blueprints": removed sample diagrams (deferred to Epic 2), added provisional blueprints for the three MVP types, created the canonical schema artifact, and defined the type registry, type profiles, validation result, and load/save contracts in `backend/services/`. All contract and blueprint tests pass. Follow-up: implement the service wrappers in Slice 04.