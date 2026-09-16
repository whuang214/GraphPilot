# Slice 01: Relationship Tools and Diamond Targets

## Purpose

Put every active relationship choice in one predictable palette location, make that tray edit a selected edge, and remove exact-cardinal gaps from diamond connection targets.

## Background

Browser diagnosis found that Activity's Comment Link appears under Shared while Control Flow appears under Activity, so relationship choices can be separated by the entire shape list. The same diagnosis confirmed that a palette click updates only the next-edge state even when an edge is selected. Diamond mid-slope bands work, but exact right and bottom vertices can miss every handle and start a node drag instead.

## Design

- Render one catalog-derived Relationships tray directly below the palette controls; shape groups render shapes only.
- Preserve Current/All scope, unified search, relationship ordering, selected-tool state, and bounded authorability.
- When an edge is selected, derive the tray's active identity from that edge. A relationship click applies `applyRelationshipSemantic` through the existing edge updater and also updates the remembered next-edge identity.
- When no edge is selected, relationship clicks retain their current next-edge-only behavior.
- Add zoom-stable top/right/bottom/left diamond vertex hit targets that overlap the existing four diagonal bands.
- Keep exact pointer projection, soft cardinal aim-lock, valid-target decoration, source/target direction, canonical side/offset storage, and canvas/SVG attachment geometry unchanged.

## Included Work

- Refactor `NodePalette` presentation without duplicating catalog filtering logic.
- Wire selected-edge relationship actions through `EditorPage` and the existing semantic cleanup/marker derivation path.
- Add explicit diamond cardinal target metadata and hit geometry.
- Add focused palette/component tests and browser coverage for selected-edge transitions, all four diamond vertices, no accidental node movement, and save/reload.
- Update the active palette, interaction, mapping, and decision owners plus this slice's `## Outcome`.

## Not In Scope

- Straight/orthogonal route modes; Slice 02 owns them.
- New relationships, endpoint semantic validation during gestures, or Note inference changes.
- Reorganizing shape groups, palette scope, notation categories, or the New Diagram chooser.
- Changing diamond notation or canonical anchor fields.

## Target Areas

- `frontend/src/editor/components/NodePalette.tsx`
- `frontend/src/editor/EditorPage.tsx`
- `frontend/src/editor/canvas/customNodes.tsx`
- `frontend/src/editor/components/components.test.tsx`
- `frontend/e2e/smoke.spec.ts`
- Active frontend/editor/mapping/decision docs

## Exit Criteria

- Activity, Use Case, BDD, and Custom each show their active relationship choices once in one tray.
- Scope and search filter relationships while Diagram/Notation organization continues to organize shapes.
- A selected edge changes identity from a palette click, clears incompatible data, updates markers/dashing immediately, remains undoable, and persists after save/reload.
- With no selected edge, the same click only changes the next-edge identity.
- Exact cardinal vertices on both decision and merge diamonds are valid source/target areas at 50%, 100%, and 200% zoom.
- Starting from any diamond cardinal vertex cannot move the node.
- Focused tests and `npm run verify` pass.

## Previous Slice

- [`../07-editor-usability/06-new-diagram-chooser.md`](../07-editor-usability/06-new-diagram-chooser.md)

## Next Slice

- [`02-straight-and-orthogonal-routing.md`](02-straight-and-orthogonal-routing.md)

## Outcome

**Completion:** Consolidated every scoped relationship into one tray above the shape groups. The tray retains Current/All filtering and unified search, reflects a selected edge's identity, and applies clicks through the existing semantic transition while also retaining the next-edge choice. Added separate zoom-stable cardinal source/target handles at all four diamond vertices while preserving the four sloped bands, exact boundary projection, legacy handle IDs, and keyboard focus only on cardinal points.

**Deviation:** Cardinal reliability uses overlapping 16-screen-pixel circular handles rather than widening the clipped quadrant polygons; this keeps the slope bands unchanged and closes the CSS right/bottom boundary seams directly. Relationship-only search intentionally hides empty shape-group headers while leaving the matching tray result visible. The implementation audit's repeated cardinal predicate and no-op selected-edge edit findings were corrected before verification.

**Verification:** `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build/typecheck, 407 unit/component tests, and 41 Chromium E2E tests. Browser coverage proves decision/merge top/right/bottom/left vertex hits at 50%, 100%, and 200%, four saved/reloaded cardinal connections without node movement, retained sloped-edge behavior, one relationship tray across scope/organization/search, and an explicitly selected Extend edge changed to Generalization through the tray with stale condition cleanup and live marker/dash updates. A separate Playwright CLI check observed one tray, Association → Comment Link selected-edge application, retained pressed next-edge state, and zero console errors. A read-only implementation audit found no unresolved material defect.

**Follow-up:** Slice 02 adds persisted Straight/Orthogonal routing to the connector tray and selected-edge inspector while retaining the Slice 01 relationship and diamond behavior.
