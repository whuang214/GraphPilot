# Group: Editor UI + UX (Epic 2 phase)

> **Folded into Epic 2 (React Diagram Editor + Export).** This comprehensive editor UI/UX work now
> lives as the `04-editor-ui-ux/` group of Epic 2 rather than a standalone epic. Its slices keep their
> original `01`–`15` numbering. (References below use the `04-editor-ui-ux` group name.)

> Epic 2's `04-editor-ui-ux` group evolves the functional-but-minimal React editor into a comprehensive, polished diagramming surface: a Tailwind-based design system, a real app shell, canvas quality-of-life, richer editing interactions, and a better save/inspector experience. Everything here is **additive** over the existing load → edit → save flow — GraphPilot JSON stays the source of truth, and the save contract and canonical schema do **not** change (the only backend additions are two **additive** endpoints: the read-only listing endpoint in Slice 06 and the path-free, write-free `validate` endpoint in Slice 07). This epic promotes the backlog "Robust editor (draw.io/Lucidchart-style)" theme and the "UI styling / polish" item into scheduled slices.  The editor's target look/feel, interaction model, and bounded (draw.io-like, not freeform) north star are defined in `../../../../02-design-and-features/editor-ui-design.md`; remaining editor polish is tracked in that doc's feature list (one refinement slice, 08, was built).

## Goal

Transform the display-first `/editor` (functional, but styled almost entirely with ad-hoc inline styles) into a comprehensive editor UI that both *looks* polished and *feels* capable — without turning GraphPilot into a general-purpose drawing tool. Introduce a Tailwind design system, a proper app shell/layout, canvas polish (minimap, snapping, zoom, dark mode), richer interactions (toolbar, undo/redo, multi-select, inline label editing, keyboard shortcuts), and an improved inspector + save experience. The canonical diagram JSON, the supported style subset, and the `/api/diagrams/load` + `/api/diagrams/save` contracts are preserved throughout.

## User Scenario

A user opens a diagram in `/editor` and lands in a coherent, themed workspace: a top app bar with the diagram name, a `diagramType` badge, and the save state; a tidy shape palette; a canvas with a minimap, snapping/alignment guides, and zoom controls; and an organized inspector panel. They can undo/redo, duplicate and multi-select nodes, rename a node by double-clicking it, use keyboard shortcuts, switch to dark mode, and get clear toast + inline feedback on save and validation. A workspace browser lets them pick a diagram without hand-editing the `?diagramPath=` URL, and an export control produces an image of the diagram.

## Scope

- Tailwind v4 styling layer + design tokens + a small set of in-house UI primitives; migrate the existing inline styles with no behavior change.
- App shell: top bar, collapsible/resizable palette + inspector rails, status bar, and redesigned home / empty / loading / error states.
- Canvas polish: `MiniMap`, restyled `Controls`, snapping + alignment guides, zoom-to-fit and a live zoom %, and dark mode via React Flow v12 `colorMode`.
- Editor interactions: a floating toolbar, an undo/redo history stack, duplicate, copy/paste, multi-select bulk actions, inline label editing, and keyboard shortcuts + a shortcuts help modal.
- Inspector + save UX: grouped/collapsible sections, style presets (within the supported subset), inline validation markers tied to the offending node/edge, toast notifications, accessible modal confirms (replacing `window.confirm`), and an optional autosave toggle.
- Workspace browser / open dialog (requires a new additive backend listing endpoint) + export entry points.
- Open **any** `.gp.json` file from a native OS picker (File System Access API) with a coherent Save / Save As model — default Save back to where the file was opened (path for MCP files, file handle for picker-opened files), Save As to copy anywhere — backed by a path-free, write-free `validate` endpoint so files outside a `.graphpilot/` workspace are still validated before write.

## Out of Scope

- Any change to the canonical diagram schema, the supported style subset, or the existing `load`/`save` API contract (the Slice 06 listing and Slice 07 `validate` endpoints are additive — read-only / write-free).
- New diagram types beyond `activity_diagram`, `use_case_diagram`, `bdd_diagram`.
- General freeform drawing (arbitrary shapes / images / free text), multi-page canvases, or a templates marketplace.
- Real-time multi-user collaboration and conflict detection (separate backlog themes).
- The in-UI AI generate flow / frontend chatbot (backlog).
- Custom per-type node renderers and the both-direction adapter work (owned by Epic 2); Epic 2's `04-editor-ui-ux` group only adds the inline-label-edit hook on top of the renderers Epic 2 produces.
- Server packaging / installer / desktop distribution (the local internal distribution theme).
- Brand-new blank-canvas diagram creation / save-new file allocation (deferred per Epic 2).

## Relationship to Epic 2 (coordination)

Epic 2 (S05-S08, formerly Epic 2.5) owns `frontend/src/editor/canvas/customNodes.tsx`, the adapters (`frontend/src/adapters/reactFlow.ts`), and the sample library. To avoid collisions:

- Slices 01–02 are isolated to **new files + the app shell + CSS** and can proceed independently of that work.
- Slices 03–04 touch the `EditorPage` canvas region and (for inline label editing) `customNodes.tsx`, so they are sequenced to start **after the Epic 2 renderer slices (S05-S08) land**.
- No slice changes the reverse adapter's whitelist behavior; the save round-trip must stay byte-stable.

## Slice Plan

Epic 2's `04-editor-ui-ux` group is delivered as seven slices, ordered foundation-first so the design system exists before the shell, the shell before canvas/interaction polish, and the backend-dependent work last:

1. `01-design-system.md` — add Tailwind v4 + design tokens + UI primitives, and migrate the existing inline styles (no behavior change).
2. `02-app-shell.md` — top bar, collapsible/resizable rails, status bar, and redesigned home / empty / error states.
3. `03-canvas-polish.md` — minimap, restyled controls, snapping/alignment guides, zoom-to-fit + zoom %, and dark mode (`colorMode`).
4. `04-toolbar-and-editing.md` — floating toolbar, undo/redo, duplicate, copy/paste, multi-select bulk actions, inline label editing, and keyboard shortcuts + help.
5. `05-inspector-and-save.md` — grouped inspector sections, style presets, inline validation markers, toasts, modal confirms, and an optional autosave toggle.
6. `06-browse-and-export.md` — additive backend listing endpoint + a workspace browser / open dialog, plus export entry points (backend-dependent; scheduled last).
7. `07-open-any-file.md` — open any `.gp.json` from a native OS picker (File System Access API) + a Save / Save As model (default Save back to the opened location), backed by an additive path-free `POST /api/diagrams/validate` endpoint (backend-dependent).

### Refinement slices (re-planned against the editor UI design)

After the core epic shipped, a UI design pass produced `../../../../02-design-and-features/editor-ui-design.md` (the editor's target look/feel and bounded, draw.io-like north star). Of the planned post-ship refinements, **only slice 08 was built**, and the earlier speculative slices were removed. The design doc's *Feature Requests and Known Issues* list (prioritized **P1–P4**) is the running source of truth, and it has now been **re-sliced into slices 09–15** below — server-rendered export first, then the P1–P4 feature-list pass — so the plan reflects real, scheduled work rather than a speculative backlog. Slices 09–15 are **planned** (drafted, not yet built); the feature-list table tracks each item's status against its target slice.

8. `08-open-and-landing.md` — **Open and Landing** (✅ delivered): make the File System Access picker the **primary** Open affordance, drop the raw-path field for a top-bar source chip, give the editor its own landing/empty state, add a `beforeunload` guard, and fix Browse for picker-opened `local` files.
9. `09-server-rendered-export.md` — **Server Rendered Export** (📝 planned, **P2**): route the editor's export through the server renderer (`DiagramRenderService` → SVG) instead of `html-to-image`, download SVG + a client-rasterized PNG (no native dep), and align the MCP `diagram_render` tool to the same inline-JSON workflow (one renderer for editor + agents, remote-MCP-ready). Closes feature-list #13. Server-side PNG for agents and PDF are explicitly later.
10. `10-node-fidelity.md` — **Node Fidelity** (📝 planned, **P1** + a P3 rider): dark-mode legibility for the custom node renderers (#1), the note shape's folded corner re-rendered as a true SVG fold (#8), and on-canvas resize handles (#6, riding along since it touches the same renderers). Authored diagram colors stay as-authored in either theme.
11. `11-friendly-property-controls.md` — **Friendly Property Controls** (📝 planned, **P1**): replace raw inspector inputs (e.g. the `strokeDasharray` array) with friendly controls — a Solid/Dashed/Dotted dropdown, etc. — strictly within the supported style subset, no schema change (#4).
12. `12-edge-editing-and-routing.md` — **Edge Editing and Routing** (📝 planned, **P2**): edit an existing edge in place (reconnect / relabel / restyle, #3) and fix the React Flow handle/anchor selection so edges route sensibly (#14; the saved JSON is already correct, so this is presentation only).
13. `13-container-un-trapping.md` — **Container Un-trapping** (📝 planned, **P2**): let a node be dragged back out of a system-boundary container (relax `extent: 'parent'`) while keeping `parentId` containment correct on entry/exit (#5).
14. `14-palette-and-landing-polish.md` — **Palette and Landing Polish** (📝 planned, **P3**): visual shape previews + collapsible categories + search in the palette (#7), a neater landing/home (#2), and auto-dismissing the lingering "Saved." banner (#15).
15. `15-deferred-editor-polish.md` — **Deferred Editor Polish** (📝 planned, **P4**): the deferred Slice 03–05 follow-ups — alignment/distance guides while dragging (#9), true in-shape inline label editing (#10), inline per-element validation markers (#11), and bulk style across a multi-selection (#12); may split into 15a–d when scheduled.

The design doc's feature list has been **re-sliced into slices 09–15** (above), mapped by priority: #13 PNG-export labels → Slice 09 (**P2**); #1 dark-mode legibility, #8 note fold, #6 on-canvas resize → Slice 10 (**P1** + P3 rider); #4 friendly property controls → Slice 11 (**P1**); #3 edge editing + #14 edge routing → Slice 12 (**P2**); #5 container un-trapping → Slice 13 (**P2**); #7 palette previews, #2 landing, #15 save-banner → Slice 14 (**P3**); and the deferred Slice 03–05 follow-ups #9/#10/#11/#12 → Slice 15 (**P4**). The feature-list table in the design doc remains the running source of truth, with each item's status pointing at its target slice.

## Revised build order (bugs and small fixes first)

After the first refinement slices shipped, the remaining work was re-prioritized to fix bugs and small issues before adding new features; dark-mode legibility (#1) is parked until last. The slice content is unchanged - this only re-sequences it into two phases (and supersedes the earlier "Suggested slicing" note in the design doc).

Phase 1 - bugs and small fixes:

1. Edge editing and routing (#3 + #14) - top priority; edges are broken. #14 (poor handle/anchor routing) and #3 (no in-place edit) are done together since they share the edge/handle code. The server SVG render (which draws edges correctly) is used as the reference to diff against the React Flow canvas and verify the fix.
2. Container un-trapping (#5) - let nodes leave a system-boundary container.
3. Saved-banner auto-dismiss (#15) - quick fix.
4. Friendly property controls (#4) - Solid/Dashed/Dotted dropdown, etc.
5. Landing polish (#2) - tidy the landing/home.

Phase 2 - features:

6. Server-rendered export + PNG-label fix (#13) - DONE (Slice 09): server SVG export + client PNG raster; `html-to-image` removed; MCP `diagram_render` inline-JSON mode added.
7. On-canvas resize (#6) - DONE (Slice 10 rider): NodeResizer on selected nodes; size persisted via node `style` so saves stay byte-stable.
8. Palette upgrade (#7) - DONE (Slice 14): shape preview glyphs + collapsible categories + search.
9. Advanced editing (#9, #10, #11, #12) - DONE (Slice 15a-d): in-shape label edit, bulk style, inline validation markers, alignment guides.

Dark-mode legibility (#1) - DONE (pending visual confirmation): draw.io-style transparent interior + light outline/text for the DEFAULT look in dark mode; authored colors preserved. Done so far: #16 (reload), #8 (note fold), #13 (server-rendered export), #6 (on-canvas resize), #7 (palette upgrade), #10/#12/#11/#9 (advanced editing), #1 (dark mode). All feature-list items addressed.

## Handoff — current working state (for the next agent)

> Transient working context (branch / local setup), not permanent design. Update or remove as the work moves. The per-item source of truth is the feature-list table in `../../../../02-design-and-features/editor-ui-design.md`.

**Where the work is.** Refinements run on the **`epic-6-refinements`** branch in a **separate clone** at `C:/Users/w105098/Desktop/Projects/GraphPilot-epic6` (kept apart from the main workspace so concurrent agents don't collide). Commits are **local-only** (this repo's `master` was never pushed to Bitbucket). `master` (Epic 3 backend: `diagram_generate`, eval framework, example library) has been **merged into the branch**.

**Done — Phase 1 (bugs + small fixes) is complete:** #16 second-file reload, #8 note fold, #14 edge routing (floating edges), #3 edge editing (already wired, preserved), #5 container un-trapping, #15 saved-banner auto-dismiss, #4 friendly Line-style control, #2 landing polish. **#1 dark mode** was parked through Phase 2 and is now implemented last (see the *Phase 2* note below) along the draw.io-style transparent-interior direction — pending the user's visual confirmation.

**Phase 2 (features) — in progress.** Done: **#13 server-rendered export** (Slice 09, `09-server-rendered-export.md`) — the editor `Export` menu renders via the server SVG (`POST /api/diagrams/render`) and downloads SVG or a client-rasterized PNG; `html-to-image` removed; MCP `diagram_render` gained a matching inline-JSON mode. **#6 on-canvas resize** (Slice 10 rider) — selected nodes show `NodeResizer` handles; size is written into the node `style` (not measured dims) so saves stay byte-stable; `resize.ts` (`applyNodeResize` + `NodeResizeContext`) + `ResizeControls` in `customNodes.tsx`. **#7 shape-palette upgrade** (Slice 14 feature) — per-shape SVG preview glyphs, collapsible categories, and search in `NodePalette.tsx` (`groupedPaletteItems` in `palette.ts`); drag payload unchanged. **#9/#10/#11/#12 advanced editing** (Slice 15, delivered as 15a–15d): in-shape inline label editing (#10), bulk style across a multi-selection (#12), inline validation markers via a toolbar Validate action (#11), and alignment/distance guides while dragging (#9). Frontend 217 vitest + backend 263 tests green; MCP smoke passes.

**#1 dark-mode legibility** (the last, previously-parked item) is now implemented along the documented draw.io-style direction: in dark mode the DEFAULT node look gets a transparent interior + light outline/text (`nodeStyle.ts` `resolveStyle` + `EditorColorModeContext`), while authored colors are preserved. This is a different approach from the reverted token attempt and is **pending the user's visual confirmation** on a real dark canvas.

**Next:** with #1 done, the planned `04-editor-ui-ux` group's refinement set (Epic 2) is complete. Remaining ideas (server-side PNG/PDF for agents, further polish) live in the design doc's feature list and the backlog.

**Run / verify (this clone).**
- Frontend: `cd frontend; npm run dev` (its `.env` points `VITE_API_BASE_URL` at the backend on 8001).
- Backend: run with the **original folder's venv** — `C:/Users/w105098/Desktop/Projects/GraphPilot/.venv/Scripts/python.exe manage.py runserver 8001 --noreload` from `backend/` (a local `.env` was copied there). The render endpoint powers the editor's Preview-render and the SVG-vs-canvas diff.
- Test diagrams: gitignored `.graphpilot/` in this clone — `usecase-container.gp.json` (system-boundary, for #5), `activity-flow.gp.json`, `bdd-blocks.gp.json`.
- Per slice: `npm run lint` + `npm run build` + `npm run test` (190+ FE tests). Keep the load → edit → save round-trip **byte-stable** (no adapter/schema change that leaks runtime-only fields, e.g. edge `type` or measured node size).

**Gotchas.**
- The `edit` tool can hang on a file that's locked/open in the IDE (it happened repeatedly on `10-node-fidelity.md`); if an edit stalls, write the file via the shell instead.
- Keep docs **plain-text / emoji-light** (some emoji writes corrupted earlier; the user asked to avoid them).
- The original folder's `.venv` can be wiped by another agent's `git clean -x`; recreate or re-point it if the backend stops working.

## Acceptance Criteria

The criteria below are the **epic-complete** target. The core slices (S01–S07, merged) satisfy most of them; slice 08 added the open/landing rework. Items tagged with a slice (e.g. **(Slice 15)**) were deferred during the initial build and are **not yet done** — they are now mapped to the planned slices 09–15 (re-sliced from the design doc's *Feature Requests and Known Issues* list, `../../../../02-design-and-features/editor-ui-design.md`).

- The editor renders with a consistent, themed design system (Tailwind tokens), and the previously inline-styled chrome (header, palette, inspector, banners, messages) uses shared primitives.
- The app shell provides collapsible/resizable rails, a status bar, and a non-bare landing route with recents. **(delivered: Slice 08)** the loading / empty / error / missing-path states are redesigned from primitives rather than the bare `Message` fallback.
- The canvas has a minimap, grid snapping, zoom-to-fit + a live zoom %, and a working light/dark theme toggle (defaulting to the OS preference). **(Slice 15)** distance/edge alignment guides while dragging. **(Slice 10)** dark-mode legibility for the custom node renderers and on-canvas resize handles.
- Undo/redo, duplicate, copy/paste, multi-select bulk actions, and keyboard shortcuts work; new elements still convert to canonical JSON with the correct `node.type`/`data.semanticType`. **(Slice 15)** true in-shape inline label editing (the core build edits the label via the inspector on double-click). **(Slice 12)** editing an existing edge in place (reconnect / relabel / restyle).
- The inspector is grouped/collapsible; save uses accessible modals + toasts; an optional autosave toggle exists (off by default). **(Slice 15)** validation errors are surfaced inline against the offending node/edge (the core build surfaces them via a toast + the per-issue banner list). **(Slice 11)** friendly property controls within the supported style subset.
- A workspace browser lists diagrams under `.graphpilot/` via the additive listing endpoint (path-safe, tested) and opens them in place; an export control produces an image.
- On a Chromium browser, any `.gp.json` opens from a native picker and saves back to where it was opened (path for MCP files, file handle for picker-opened files), with a Save As that copies elsewhere; saving always validates via the additive path-free `validate` endpoint first, and the path-based + MCP flows degrade cleanly on non-Chromium browsers.
- After every slice, `npm run lint`, `npm run build`, and `npm run test` pass (plus `python manage.py test` for the backend-touching slices 06–07 and 09), and the load → edit → save round-trip stays byte-stable (no React Flow runtime fields leak; the adapters and schema are untouched).

## Decisions to confirm when scheduled (log in `decision-decisions.md`)

These are raised here but should be promoted into the central decision tracker when the epic becomes active (mirroring the "log when scheduled" convention used by the backlog's Robust-editor theme):

- Styling stack: **Tailwind v4 + `@tailwindcss/vite`** (vs Tailwind v3 + PostCSS). Chosen direction: Tailwind v4 with the Vite plugin (no PostCSS config), pinning an explicit, vetted version.
- Whether to adopt a headless accessibility primitive library (e.g. Radix) for modal/tooltip/select, or hand-roll the primitives in Slice 01.
- Router adoption (`react-router-dom`) once home / editor / dialog become distinct views — this picks up the existing "Frontend decisions → router" row (currently *After MVP*).
- The new backend diagram-listing endpoint contract for the workspace browser (Slice 06).
- **File System Access API for "open any file" (Slice 07)**: accepted as **Chromium-only** (Chrome/Edge); other browsers keep the path-based open + MCP Save and disable the picker-driven `local` Save / Save As. Confirmed direction: yes, Chromium-only is acceptable.
- **Additive path-free `POST /api/diagrams/validate` endpoint (Slice 07)**: validates a diagram with no write and no workspace resolution so picker-opened files (outside `.graphpilot/`) can still be validated before the browser writes them via the file handle.
- Export ownership: client-side canvas export vs. Epic 3 `diagram_render` (SVG).
- Autosave default and how far to grow the property panel — picks up the existing "Frontend decisions → autosave / richer property panel" rows (currently *After MVP*).

## Dependencies

- **Depends on:** Epic 2 (the React editor + load/save API + adapters, and the S05-S08 custom renderers + both-direction conversion, formerly Epic 2.5) for the canvas/renderer-touching slices (03–04).
- **Unblocks:** a comfortable manual editing experience for both technical and non-technical users; relates to the local internal distribution theme in `../../../02-backlog.md`.

## Related Docs

- `../../README.md`
- `../../00-current-state.md`
- `../../02-react-editor-and-export/00-epic.md`
- `../../../02-backlog.md`
- `../../../00-development-environment.md`
- `../../../../02-design-and-features/editor-ui-design.md` — the editor's target look/feel + bounded draw.io-like north star (the design this epic's refinement slices build toward)
- `../../../../01-architecture/02-frontend-architecture.md`
- `../../../../01-architecture/04-api-routes.md`
- `../../../../02-design-and-features/decision-decisions.md`
