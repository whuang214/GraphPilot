# Slice 03: Canvas Polish

## Purpose

Improve the diagramming surface with the quality-of-life canvas features users expect from a lightweight draw.io/Lucidchart-style editor, while keeping GraphPilot JSON canonical and the custom renderers unchanged.

## Background

- The canvas in `frontend/src/editor/EditorPage.tsx` currently renders only `<Background />` and `<Controls />` — there is no minimap, no snapping/alignment help, no zoom readout, and no dark mode.
- React Flow v12 provides most of these as built-ins (`MiniMap`, `Controls`, `Background`, `colorMode`, `snapToGrid`/`snapGrid`), so this is mostly configuration + light theming rather than bespoke canvas code.
- Custom per-type renderers and `parentId` containment already exist (Epic 2 S05); this slice only adds canvas chrome around them.
- This slice touches the `EditorPage` canvas region, so it is sequenced after the Epic 2 renderer slices (S05-S08) land and must not change the `customNodes.tsx` shape visuals Epic 2 owns.

## Included Work

- Add a **`MiniMap`** with node coloring derived from `data.semanticType` (read-only; no renderer changes), restyle **`Controls`** to match the design system, and refine the **`Background`** variant (dots/grid).
- **Snapping + alignment guides**: enable `snapToGrid` + `snapGrid`, and add a helper-lines overlay for alignment while dragging.
- **Zoom-to-fit** action + a **live zoom %** readout wired into the Slice 02 status bar (and/or the Slice 04 toolbar); fit-on-load is retained.
- **Dark mode** via React Flow v12 `colorMode` (`'light' | 'dark' | 'system'`) wired to a theme
  toggle in the top bar, with canvas colors driven by the Slice 01 tokens/CSS variables.
- An **empty-canvas onboarding overlay** ("drag a shape to begin") shown when a diagram has no nodes.
- Update `docs/01-architecture/02-frontend-architecture.md` (canvas/rendering section) and `frontend/README.md`.

## Not In Scope

- Any change to `customNodes.tsx` shape geometry or to the adapters (Epic 2); the minimap only *reads* `data.semanticType` for coloring.
- Toolbar buttons and editing interactions — undo/redo, duplicate, multi-select, inline label edit (Slice 04). (The zoom % readout may be surfaced in the toolbar built there.)
- Inspector and save UX (Slice 05).
- Auto-layout and orthogonal edge routing (remain backlog).

## Target Areas

- `frontend/src/editor/EditorPage.tsx` (canvas region: `MiniMap`/`Controls`/`Background`, `snapToGrid`, `colorMode`, fit/zoom)
- `frontend/src/editor/canvas/` (new helper-lines overlay, minimap color map, zoom readout)
- theme integration with `frontend/src/ui/` + tokens (light/dark)
- `docs/01-architecture/02-frontend-architecture.md`, `frontend/README.md`

## Exit Criteria

- The canvas shows a minimap, restyled controls, working snapping + alignment guides, a zoom-to-fit action, and a live zoom %.
- A light/dark theme toggle switches both the chrome and the React Flow canvas (`colorMode`) cleanly.
- The empty-canvas overlay appears only when there are no nodes.
- No canonical data changes and no `customNodes.tsx`/adapter changes; the save round-trip stays byte-stable.
- `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `02-app-shell.md`

## Next Slice

- `04-toolbar-and-editing.md`

## Outcome

✅ Completed as planned (one scoped deviation). Added a `MiniMap` (tinted by `data.semanticType` via `canvas/miniMap.ts`, read-only), a 16px grid `Background`, grid snapping (`snapToGrid` + `snapGrid={[16,16]}`), a live zoom % readout in the StatusBar (`canvas/ZoomStatus.tsx`, via the React Flow store), light/dark theming (`shell/useColorMode.ts` toggles a `.dark` class that flips the index.css tokens, and is passed to React Flow's `colorMode`; a toggle sits in the TopBar), and an empty-canvas overlay (`canvas/EmptyOverlay.tsx`). Zoom-to-fit remains available via the existing `Controls` (and `fitView`). Deviation: distance-based **alignment/helper lines** were deferred in favour of grid snapping — they are the most visually-fiddly piece and were not safe to land without visual QA; tracked as a follow-up. No change to `customNodes.tsx`, the adapters, or canonical data. Verified: `npm run lint`, `npm run build`, `npm run test` (40/40) pass. Follow-up: alignment/helper lines.
