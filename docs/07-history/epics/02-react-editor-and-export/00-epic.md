# Epic 2: React Diagram Editor + Export

## Goal

Build the browser-facing React editor that loads a saved GraphPilot diagram, lets the user make light visual edits, and saves changes back through the Django API. Confirm the canonical diagram JSON against the real React Flow round-trip.

## User Scenario

A user opens the editor URL for a saved diagram, sees it rendered, moves/resizes/relables elements, and saves. The saved JSON remains valid and usable by later IDE prompts.

## Scope

- React frontend runs locally
- Django backend runs locally (browser-facing API routes)
- `/editor` route with `diagramPath` query parameter
- load a saved `<name>.gp.json` through `GET /api/diagrams/load`
- render the diagram with React Flow
- light editing: move, resize, relabel, recolor, reconnect
- save edited JSON through `POST /api/diagrams/save`
- validate before overwrite
- confirm the canonical diagram JSON against the React Flow `toObject()` round-trip
- author or finalize the three canonical sample diagrams:
  - `activity_diagram`
  - `use_case_diagram`
  - `bdd_diagram`

## Out of Scope

- MCP tool implementation (Epic 3)
- diagram generation (Epic 3)
- diagram update via IDE (Epic 4)
- SVG/PNG/PDF export as a finished feature
- database persistence
- auth
- Docker

## Research / Inputs

- `docs/00-product-and-requirements/02-requirements.md` — active product requirements and Epic 2 scope.
- The research doc's original Epic 2 included MCP-side `diagram_render` and SVG export. In the current plan, `diagram_render` moved to Epic 3 alongside generation. Browser SVG/PNG/PDF export remains deferred as a finished frontend feature.
- The research doc's original Epic 1 included React display and browser save (`POST /api/diagrams/save`). In the current plan, these were moved into Epic 2 so that Epic 1 can focus on the backend + MCP foundation. This is a deliberate restructure recorded in `docs/02-design-and-features/decision-decisions.md`.

## Slice Plan

Epic 2's slices live in group folders. Groups `01`–`03` are the original editor charter plus the folded-in "Epic 2.5" work; group `04-editor-ui-ux/` is the comprehensive editor UI/UX phase, folded in from the former standalone editor-UI epic. Groups `05`–`08` capture later refinement, simplification, observed usability, and connector/audit follow-ons.

**`01-browser-load-edit-save/`** (S01–S04) — the original editor charter:

1. `01-browser-load-edit-save/01-browser-load-and-display.md` - `GET /api/diagrams/load` + display-first React Flow render of a loaded diagram.
2. `01-browser-load-edit-save/02-save-and-validate-api.md` - `DiagramPersistenceService` + `POST /api/diagrams/save` (validate-then-overwrite). Required `load` + `save` route set only; no render-on-save.
3. `01-browser-load-edit-save/03-frontend-editing-and-save.md` - light editing (move/resize/relabel/recolor/reconnect), the reverse adapter that strips React Flow runtime fields, and the end-to-end save flow.
4. `01-browser-load-edit-save/04-canonical-samples.md` - author and confirm the three canonical sample diagrams against the real React Flow round-trip.

**`02-renderers-and-samples/`** (S05–S08, ex-"Epic 2.5") — faithful renderers + the answer-key sample library:

5. `02-renderers-and-samples/05-node-shapes.md` - type-specific React Flow node/edge renderers + `parentId` containment (replaces display-first default rectangles).
6. `02-renderers-and-samples/06-canvas-authoring.md` - confirm the React Flow -> GraphPilot (reverse) direction with minimal drag-from-palette node creation.
7. `02-renderers-and-samples/07-sample-layout.md` - per-example `examples/<name>/{prompt.md, output.gp.json}` answer-key layout + `default.json` blueprint retirement.
8. `02-renderers-and-samples/08-sample-library.md` - 4-6 comprehensive answer-key examples per MVP type (~12 total), authored against the new renderers.

**`03-comprehensive-shapes/`** (S09–S10) — the common-tier UML/SysML shapes on the canvas + SVG:

9. `03-comprehensive-shapes/09-comprehensive-node-and-edge-shapes.md` - render the common-tier UML 2.5.1 / SysML 1.6 vocabulary on the canvas + SVG export (activity initial/final/fork/join; use-case `generalization` + include/extend dashing; BDD `enumeration` + `aggregation`/`association`). Pairs with Epic 1's `02-notation-vocabulary/` (vocabulary).
10. `03-comprehensive-shapes/10-bdd-block-compartments.md` - faithful BDD block **feature compartments** (parts/values/operations/constraints; enumeration literals) rendered identically on the canvas + SVG export and **editable in the property panel**, stored additively under `data.compartments`. Phase A+B (render + edit) delivered; generation support (Phase C) follows.

**`04-editor-ui-ux/`** (its own S01–S15) — the comprehensive editor UI/UX phase (Tailwind design system, app shell, canvas polish, toolbar + undo/redo, inspector/save, workspace browser + export, open-any-file), folded in from the former standalone editor-UI epic. Overview + slice plan in `04-editor-ui-ux/00-group.md`.

**`05-frontend-refinement/`** (its own S01–S08; complete and verified) — unified source sessions, BDD marker correctness, canonical route geometry, obstacle-aware and manual orthogonal routing, compact empty BDD blocks, relationship presets, a three-tab property panel, and integrated canvas/SVG/PNG parity. Overview + slice plan in `05-frontend-refinement/00-group.md`.

**`06-editor-simplification/`** (its own S01–S06; complete, audited, and verified) — supersedes the refinement's automatic-routing and source-chrome choices with minimal manual-first routes, full-boundary connection creation, and a standalone landing/blank/open/recent flow. Overview + slice plan in `06-editor-simplification/00-group.md`.

**`07-editor-usability/`** (its own S01–S06; complete, audited, and verified) — addresses browser-observed attachment precision, connection guidance, container layering, relationship discovery, palette organization, and scalable blank-diagram selection without expanding the semantic catalog. Overview + slice plan in `07-editor-usability/00-group.md`.

**`08-editor-connectors-and-audit/`** (its own S01–S03) — consolidates relationship tools, closes diamond cardinal hit gaps, adds persisted straight/orthogonal routing with canvas/SVG parity, and re-audits the complete frontend interaction surface. Overview + slice plan in `08-editor-connectors-and-audit/00-group.md`.

Delivery notes:

- the editor route is handled without a router dependency (`window.location` / `URLSearchParams`) for the single MVP `/editor` view.
- the required UI route set for MVP is `load` + `save`; `validate`, `schema`, and `diagram-types` routes stay optional and out of Epic 2 scope.
- SVG render-on-save is deferred because `DiagramRenderService` is owned by Epic 3.

## Follow-on scope (S05-S08, ex-Epic 2.5)

Slices S05-S08 were originally planned as a separate bridge epic ("Epic 2.5") between Epic 2 and Epic 3, then folded back into Epic 2. They extend the original Epic 2 charter (Goal / Scope above) rather than restate it:

- **Faithful rendering (S05):** each MVP diagram type previews with real semantics (decision diamonds, actors, system-boundary containers, BDD compartment boxes) and `parentId` containment, instead of identical rectangles.
- **Both-direction conversion (S06):** canonical JSON can be built *from* canvas state (not only round-tripped from a loaded file), de-risking a future blank-canvas authoring flow; full draw.io-style authoring stays in the backlog.
- **Answer-key sample library (S07-S08):** the samples become a per-type library of prompt -> expected-output pairs (the `default.json` blueprints are retired in favour of `prompts.md` + examples), giving Epic 3 generation known-good targets to generate toward and be scored against.

This work unblocks Epic 3 (MCP generation), which uses the training examples as few-shot context and reuses the faithful editor for `editUrl` verification. The held-out answer keys remain the corpus for the planned embeddings-based generation-evaluation rebuild; the former eval harness was removed.

## Acceptance Criteria

- React frontend starts locally
- Django backend starts locally
- the editor loads an existing diagram by `diagramPath`
- the user can move, resize, relabel, recolor, and reconnect diagram elements
- save updates the original `<name>.gp.json` file only when the edited JSON is valid
- invalid saves do not overwrite the existing file
- the canonical sample diagrams for the three MVP types are confirmed against the React Flow round-trip
- basic setup notes for the browser flow exist

> The catalog-driven palette + single `gpNode` are delivered in the **`04-universal-vocabulary`** group (Epic 1, Slice 02,
> `../01-local-diagram-foundation/04-universal-vocabulary/02-catalog-driven-palette-and-node.md`), not a
> further Epic 2 slice.

## Related Docs

- `../README.md`
- `../00-current-state.md`
- `../../00-development-environment.md`
- `../../../01-architecture/00-system-design.md`
- `../../../01-architecture/01-backend-architecture.md`
- `../../../01-architecture/02-frontend-architecture.md`
- `../../../01-architecture/04-api-routes.md`
- `../../../02-design-and-features/00-diagram-json-schema.md`
- `../../../02-design-and-features/01-diagram-json-mapping-design.md`
- `../../../02-design-and-features/04-generation-design.md`
- `../../../02-design-and-features/decision-decisions.md`
