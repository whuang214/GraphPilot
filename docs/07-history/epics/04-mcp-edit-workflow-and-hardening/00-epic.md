# Epic 4: MCP Edit Workflow + MVP Hardening

## Goal

Complete the end-to-end IDE-to-editor-to-IDE loop by implementing `diagram_update` so that the IDE agent can replace an existing saved diagram with a validated updated version, then harden the MVP with automated tests, a demo script, and finalized setup and documentation.

## User Scenario

A user asks the IDE agent to edit an existing diagram with a follow-up prompt. The IDE agent reads the latest saved `<name>.gp.json`, builds a full updated diagram JSON using the user prompt and the diagram schema, and calls `diagram_update` with the diagram path and updated JSON. GraphPilot validates the updated JSON; if valid it overwrites the file and returns success. If invalid it returns structured errors and leaves the existing file unchanged. The user can then open the diagram in the React editor or continue prompting from the latest saved version.

## Scope

- `diagram_update` MCP tool implemented
  - inputs: `diagramPath`, full updated `diagram` JSON
  - outputs: `updated`, `diagramPath`
  - optional: `svgPath` when SVG is refreshed after a successful update
  - preserves existing node IDs, edge IDs, layout, and styles unless the requested edit requires changes
  - **re-locks** the diagram to a concrete, caller-chosen `diagramType`, conforms the result to that type's vocabulary, and stamps `metadata.authoring = "generated"` (informational provenance). Strictness is decided by `diagramType`, not `authoring`: a freeform board is `diagramType: "custom"` (the UI save path flips to `custom` when a board goes off-vocabulary), and `diagram_update` retypes it back to a concrete type. The shared `DiagramValidationService` runs the structural critic as advisory Layer 4 warnings for every diagram; like the generation pipelines, the update flow escalates residual findings to a hard block
- reuses `DiagramPersistenceService` (built in Epic 2) for the validate-then-overwrite flow:
  - validates the updated JSON using `DiagramValidationService` before any write
  - saves only when validation succeeds
  - never overwrites the existing file when validation fails
  - returns structured validation errors when the update is rejected
  - optionally calls `DiagramRenderService` to refresh `diagram.svg` after a successful save
- reuses Epic 1 and Epic 3 shared services: `WorkspaceStorageService`, `DiagramValidationService`, `DiagramRenderService`
- MVP hardening deliverables:
  - end-to-end demo script covering the full IDE → editor → IDE loop
  - clean sample prompts for the three MVP diagram types
  - clean sample output folder with confirmed example files
  - basic automated tests covering the core save-and-validate workflow
  - documented known limitations
  - finalized setup instructions for all three runtimes (Django, React, MCP)

## Out of Scope

- `diagram_apply_patch` and structured patch operations (deferred post-MVP)
- new diagram types beyond the three MVP types
- AI agent inside the React UI
- RAG example lookup (Epic 5)
- eval framework
- repair or autofix flows
- database persistence
- auth
- Docker

## Slice Plan

Slices are not yet planned. Epic 4 is authored at the epic level; numbered slice docs will be added when work begins.

## Dependencies

- **Depends on:** Epic 1 (shared services), Epic 2 (`DiagramPersistenceService` validate-then-overwrite), and Epic 3 (`DiagramRenderService` for the optional SVG refresh after a successful update).
- **Unblocks:** nothing further — Epic 4 closes the MVP loop (`diagram_update` + hardening).

## Research / Inputs

- `docs/02-design-and-features/05-edit-design.md` — active edit-workflow design stub (`diagram_update`; detailed request/response and conform behavior remain to be completed when Epic 4 is sliced; patch ops deferred)
- `docs/01-architecture/03-mcp-tools/01-diagram-tools.md` — `diagram_update` tool contract
- `docs/01-architecture/01-backend-architecture.md` — `DiagramPersistenceService` responsibilities and use case service flow for `diagram_update`
- `docs/00-product-and-requirements/02-requirements.md` — FR-9 (IDE-based updates), FR-10 (patch operations deferred)

## Acceptance Criteria

- `diagram_update` can be called from an IDE MCP client with an existing diagram path and a full updated JSON payload
- the updated JSON is validated before any write occurs
- a valid updated JSON overwrites the existing `<name>.gp.json`
- an invalid updated JSON does not overwrite the existing file and returns structured validation errors
- the returned response indicates whether the update was saved
- existing node IDs, edge IDs, layout, and styles are preserved unless the edit requires changes
- the end-to-end loop (IDE generate → editor edit → IDE update) works from a demo script
- basic automated tests covering the validate-then-save workflow pass
- setup instructions for Django, React, and MCP are finalized and accurate

## Related Docs

- `../README.md`
- `../00-current-state.md`
- `../../00-development-environment.md`
- `../../../01-architecture/00-system-design.md`
- `../../../01-architecture/01-backend-architecture.md`
- `../../../01-architecture/03-mcp-tools/01-diagram-tools.md`
- `../../../00-product-and-requirements/02-requirements.md`
- `../../../02-design-and-features/00-diagram-json-schema.md`
- `../../../02-design-and-features/02-validation-design.md`
- `../../../02-design-and-features/05-edit-design.md` *(stub; full write-up pending Epic 4)*
- `../../../02-design-and-features/decision-decisions.md`
