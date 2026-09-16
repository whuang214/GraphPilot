# Slice 08: Open and Landing

## Purpose

Rework the editor's file-loading UX to the two-way open model in the editor UI design doc, and give the editor its own landing/empty state. This is the **one refinement slice that was actually built** after the core epic shipped; the rest of the editor polish now lives in the design doc's *Feature Requests and Known Issues* list and will be re-sliced from there when scheduled.

## What was delivered

- **Two ways to open a diagram** (replacing three overlapping ones): a native **Open file…** picker (File System Access API → `local` source, saves back to the file handle) and the MCP **`?diagramPath=`** URL link (`mcp` source, saves by path). The always-visible raw-path text field was removed.
- **Source chip** in the top bar — *From MCP* / *From file* next to the diagram name, with the full path/location in a hover tooltip.
- **Landing / empty state owned by the editor**: `App` always renders the editor; `Home` was refactored into a controlled landing (Open file + recents, no path field) reused by the missing-path and load-error states.
- **Unsaved-changes guard**: a `beforeunload` warning before refresh/close when the diagram is dirty (on top of the existing confirm before opening another diagram).
- **Bug fix**: the workspace **Browse** dialog is now disabled for picker-opened `local` files (which have no `.graphpilot` workspace), fixing the previous error.

## Files touched

- Frontend: `App.tsx`, `editor/components/Home.tsx`, `editor/shell/TopBar.tsx`, `editor/EditorPage.tsx`, `editor/components/components.test.tsx`.
- Docs: `docs/01-architecture/02-frontend-architecture.md`, `frontend/README.md`.

## Verification

`npm run lint` (0/0), `npm run test` (86 unit, +1 landing test), `npm run build`, and `npm run e2e` (9/9) all pass. Manual browser check (native picker, source chip, refresh guard) confirmed by the user.

## Previous Slice

- `07-open-any-file.md`

## Next Slice

- End of the `04-editor-ui-ux` group's refinement set (Epic 2) **for now**. The remaining editor polish (dark-mode legibility, neater landing, edge editing, friendlier property controls, container un-trapping, on-canvas resize, shape-palette previews, note-shape fold fix) is tracked in the design doc's *Feature Requests and Known Issues* list (`../../../../02-design-and-features/editor-ui-design.md`) and will be re-sliced from there.

## Outcome

✅ Delivered. Two-way open (native picker + MCP URL), source chip, editor-owned landing, unsaved- changes refresh guard, and the Browse-for-`local` fix. Verified via lint + 86 unit + build + 9 e2e, and manually by the user. The previously-planned refinement slices 09–12 (shape palette, node fidelity, bug-fix pass, editing polish) were **removed**; that work is captured in the design doc's feature list and will be re-sliced when scheduled.
