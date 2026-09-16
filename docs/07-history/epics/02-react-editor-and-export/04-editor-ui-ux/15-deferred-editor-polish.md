# Slice 15: Deferred Editor Polish

## Purpose

Land the four deferred Slice 03–05 follow-ups as the lowest-priority tranche of the design doc's feature list: alignment / distance guides while dragging (#9), true in-shape inline label editing (#10), inline per-element validation markers (#11), and bulk style across a multi-selection (#12). These are the **P4** items, explicitly scheduled last.

## Background

These were knowingly deferred during the core build, with simpler behavior shipped instead:

- Only **grid snapping** ships today; distance/edge alignment guides while dragging were deferred from Slice 03 (#9).
- Double-click opens the **inspector** to rename; true in-shape inline label editing was deferred from Slice 04 (#10).
- Validation surfaces as a **toast + per-issue banner list**; inline per-element markers were deferred from Slice 05 (#11).
- Style presets apply to **one element at a time**; bulk style across a multi-selection was deferred from Slice 04 (#12).

Because these are independent, this slice may be split into 15a–15d when scheduled if any one grows large; it is documented as a single tranche to keep the plan honest about priority, not to force them into one commit.

## Design

- **#9 guides:** add distance/edge alignment helper lines while dragging (on top of the existing grid snapping), without changing saved positions beyond the snap that already occurs.
- **#10 inline label:** edit a node's label via an in-shape `<input>` on the custom nodes (double-click → edit in place), replacing the rename-via-inspector behavior; the label still maps to the same `data` field.
- **#11 inline validation:** map `validationErrors[].path` to the offending node/edge — outline it on the canvas and flag it in the inspector — reusing the existing path-free `POST /api/diagrams/validate` endpoint (**no backend change**).
- **#12 bulk style:** apply a style preset/property across the current multi-selection at once, reusing the friendly controls from Slice 11.

## Included Work

- Alignment/distance guides during drag in the canvas (`EditorPage.tsx`).
- In-shape label editing on the custom nodes (`customNodes.tsx`).
- Inline validation markers: error → node/edge outline + inspector flag (`EditorPage.tsx`, `customNodes.tsx`, `PropertyPanel.tsx`), driven by the existing validate endpoint.
- Bulk style across a multi-selection (`PropertyPanel.tsx`, `EditorPage.tsx`).
- Unit tests per item.

## Not In Scope

- Anything outside these four items; any backend change (the validate endpoint already exists).
- New style properties, shapes, or diagram types.

## Target Areas

- `frontend/src/editor/EditorPage.tsx` (guides, validation wiring, bulk apply).
- `frontend/src/editor/canvas/customNodes.tsx` (in-shape label, validation outline).
- `frontend/src/editor/components/PropertyPanel.tsx` (inspector validation flag, bulk style).
- Frontend unit tests.

## Exit Criteria

- Distance/edge alignment guides appear while dragging, in addition to grid snapping (#9).
- A node's label can be edited in place inside the shape (#10).
- Validation errors highlight the offending node/edge on the canvas and flag it in the inspector (#11), using the existing validate endpoint.
- A style change applies across a multi-selection at once (#12).
- The load → edit → save round-trip stays byte-stable; `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `14-palette-and-landing-polish.md`

## Next Slice

- End of Epic 2's `04-editor-ui-ux/` group (the former editor-UI refinement set). Any further editor work is tracked in `../../../../02-design-and-features/editor-ui-design.md` and re-sliced from there.

## Outcome

Complete on `epic-6-refinements` — delivered as four sub-slices (15a–15d), one per independent item, as anticipated.

- **15a (#10) in-shape inline label editing.** Double-click a node opens an in-shape `<input>` (`EditableLabel` in `customNodes.tsx` + a `NodeLabelEditContext`); commits on Enter/blur (only if changed), cancels on Escape, via the same `updateNode` path so undo/save are consistent. The inspector Label field still works.
- **15b (#12) bulk style.** Selecting 2+ nodes switches the inspector to a bulk-style panel (presets + colour/border controls) that applies to every selected node as one undo step (`bulkStyleNodes` + a shared `applyNodePatch` helper now used by single edits too).
- **15c (#11) inline validation markers.** A toolbar **Validate** action runs the path-free `POST /api/diagrams/validate`; each issue's `$`-rooted path is mapped to its node/edge id (`validation.ts`), outlining the element on the canvas (`gp-invalid` class) and flagging it in the inspector (`IssueFlag`). Markers clear on the next edit. No backend change.
- **15d (#9) alignment guides.** Dragging a node draws blue alignment guide lines and snaps to the nearest node edge/center (`getHelperLines` in `alignmentGuides.ts` + a `HelperLines` canvas overlay, wired through an `onNodesChange` interceptor), on top of the existing grid snapping.

All four keep the load -> edit -> save round-trip byte-stable (display-only fields like `className` are never read back by the reverse adapter).

**Verification.** npm run lint (0/0), npm run build (tsc + vite), npm run test (217 passed — added `inlineLabel`/`EditableLabel`, `nodePatch`, `validation`, and `alignmentGuides` tests). Live drag guides, in-shape rename, bulk recolour, and validate-and-outline confirmed manually.

This is the end of the planned `04-editor-ui-ux` group's refinement set (Epic 2); only the parked **#1 dark-mode legibility** remains (deferred to last, see its feature-list note).
