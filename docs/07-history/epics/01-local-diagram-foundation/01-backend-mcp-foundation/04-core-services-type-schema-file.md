# Slice 04: Core Services - Type, Schema, and File Safety

## Purpose

Implement the low-risk shared backend services that centralize type lookup, schema lookup, workspace path safety, and file loading behavior.

## Included Work

- implement `DiagramTypeService`
- implement `DiagramSchemaService`
- implement `WorkspaceStorageService`
- centralize numbered diagram folder resolution under `.graphpilot/`
- centralize safe path handling for Epic 1 workspace reads
- implement diagram load behavior needed by later API and frontend slices

## Not In Scope

- validation and save-blocking rules beyond what is needed for basic loading
- full API route implementation
- MCP tool implementation
- frontend behavior beyond what is needed to consume load results later

## Target Areas

- backend shared service modules
- backend tests for supported type lookup, schema lookup, and safe path handling
- active docs that become inaccurate during implementation

## Exit Criteria

- supported types are returned from one backend location
- schema lookup works from one backend location
- safe workspace path handling is centralized
- numbered diagram folder resolution follows the active storage convention
- diagrams can be loaded safely from the canonical workspace structure

## Next Slice

- `05-validation-service.md`

## Outcome

✅ Completed as planned. Implemented `DiagramTypeService`, `DiagramSchemaService`, and `WorkspaceStorageService` as lightweight classes in `backend/services/`. `WorkspaceStorageService` includes safe atomic write helpers (raw primitives; validation deferred to Slice 05) and uses an explicit `workspace_dir` argument — a minor scope extension from "reads only" agreed with the team during planning. 78 tests pass (55 new in `test_services.py`, 23 existing in `test_contracts.py`). No other deviations; all exit criteria met. Follow-up: implement `DiagramValidationService` in Slice 05.