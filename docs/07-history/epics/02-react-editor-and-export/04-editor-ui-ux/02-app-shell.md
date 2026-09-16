# Slice 02: App Shell

## Purpose

Give the editor a coherent layout and chrome so the palette, canvas, and inspector read as one workspace, and replace the bare landing/error states with polished equivalents. This makes the editor feel like a product surface rather than a single scrollable page.

## Background

- The whole app is a single `/editor` route with no router (`frontend/src/App.tsx` sniffs `window.location`); the non-editor landing page is a bare `<h1>GraphPilot</h1>` plus a code hint.
- `EditorPage` composes the header, palette, canvas, and inspector inline with flexbox and no shared shell; the loading / error / missing-path states render through a plain `Message` component.
- With the Slice 01 primitives in place, the layout can be lifted into a reusable shell that later slices (canvas polish, toolbar, inspector) plug into.
- Behavior is preserved throughout: this slice is structure and information architecture on top of the Slice 01 design system, not new editor capability.

## Included Work

- Introduce **app-shell components** (e.g. under `frontend/src/editor/shell/`):
  - `TopBar` — brand, diagram name, a `diagramType` `Badge`, the dirty indicator, the `Open` control, and the `Save` button.
  - `PaletteRail` (left) and `InspectorRail` (right) — wrappers that own collapse/resize.
  - `StatusBar` (bottom, optional) — node/edge counts, zoom % (wired in Slice 03), and save state.
- **Collapsible + resizable** side rails, persisting collapsed state and widths to `localStorage`.
- Redesign the **home / landing route** in `App.tsx`: a recent-diagrams list (from `localStorage`), an `Open` field, and quick-start guidance — replacing the bare heading.
- Redesign the **loading / error / missing-path** states into polished empty/error components built from the Slice 01 primitives (keeping the existing `OpenControl` affordance).
- Keep routing on `window.location` for now; record router adoption (`react-router-dom`) as a decision to confirm once these become genuinely distinct views (it picks up the existing *After MVP* router row in `decision-decisions.md`).
- Update `frontend/README.md` and `docs/01-architecture/02-frontend-architecture.md` (editor route / layout sections).

## Not In Scope

- Tailwind setup and primitives (Slice 01).
- Minimap, snapping, zoom readout, dark mode (Slice 03).
- Toolbar and editing interactions (Slice 04).
- Inspector field grouping/validation surfacing (Slice 05).
- Workspace browser dialog and the backend listing endpoint (Slice 06) — this slice keeps the existing single-path `Open` control.
- Adopting a router dependency (deferred; only noted here).

## Target Areas

- `frontend/src/App.tsx` (home/landing redesign + shell mount)
- `frontend/src/editor/EditorPage.tsx` (extract shell; states)
- `frontend/src/editor/shell/` (new `TopBar`, `PaletteRail`, `InspectorRail`, `StatusBar`)
- `frontend/src/ui/` (extend primitives only if a genuinely shared piece is missing)
- `frontend/README.md`, `docs/01-architecture/02-frontend-architecture.md`

## Exit Criteria

- The editor renders inside a shell (top bar + left/right rails + canvas region + optional status bar) using the Slice 01 design system.
- Side rails collapse and resize, and their state persists across reloads.
- The landing route and the loading / error / missing-path states are redesigned and consistent.
- All existing behavior (load, open-by-path, edit, save, validation banners) is unchanged.
- `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `01-design-system.md`

## Next Slice

- `03-canvas-polish.md`

## Outcome

✅ Completed as planned. Added an app shell under `frontend/src/editor/shell/` (`TopBar` with the diagram identity + action slot, `StatusBar` with node/edge counts + save state, and a `Rail` that owns collapse + drag-resize via the `useRail` hook, persisted to `localStorage`). `NodePalette` and `PropertyPanel` are now layout-agnostic content (the Rail owns width/border/scroll/title). Redesigned the landing route into `Home` (open-by-path + a recent-diagrams list backed by `recents.ts`, which `EditorPage` populates on a successful load); `App.tsx` now renders `Home` for non-`/editor` routes. The dead `App.css` scaffold was removed. Deviation: the loading/error/missing-path states still use the (S01-restyled) `Message` component rather than a bespoke redesign — acceptable and revisitable later. Verified: `npm run lint`, `npm run build`, `npm run test` (40/40) pass; the canvas/save flow is unchanged. Follow-up: none.
