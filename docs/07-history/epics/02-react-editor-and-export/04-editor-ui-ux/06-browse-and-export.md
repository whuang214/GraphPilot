# Slice 06: Browse and Export

## Purpose

Remove the two remaining "raw" rough edges of the editor: opening a diagram requires knowing its full `.gp.json` path, and there is no way to export the diagram as an image. This slice adds a workspace browser backed by a listing endpoint and an export control.

## Background

- Opening today goes through `OpenControl` in `frontend/src/editor/EditorPage.tsx`, which needs the full `diagramPath`; there is no way to enumerate the diagrams in a workspace.
- `WorkspaceStorageService` already exposes `list_diagram_names` (named-file storage under `.graphpilot/`), so a listing endpoint is a thin, path-safe wrapper rather than new storage logic.
- This promotes the backlog "Load diagram from directory" item; export relates to the SVG-render work owned by Epic 3 (`diagram_render`).
- This slice is backend-dependent and scheduled last; it adds the only new backend surface in the `04-editor-ui-ux` group (Epic 2) — a small additive, read-only listing endpoint — and leaves the `load`/`save` contract and canonical schema unchanged.

## Included Work

- **Backend listing endpoint (additive, read-only)**: e.g. `GET /api/diagrams/list` taking a workspace (the `.graphpilot` parent, consistent with how `load`/`save` derive the workspace) and returning the available `<name>.gp.json` diagrams. Reuse `WorkspaceStorageService.list_diagram_names`; keep path safety in the service. Follow the camelCase response + no-trailing-slash route conventions, and add backend tests.
- **Frontend workspace browser / open dialog**: list diagrams (name + path), search/filter, and open in place — keeping `?diagramPath=` in sync and honoring the existing unsaved-changes guard. Replaces hand-typing a path as the primary open affordance (the raw-path `Open` control can remain as a fallback).
- **Export entry points**: a client-side PNG/SVG export of the current canvas as an interim, with a clear path to wire the **Epic 3 `diagram_render` SVG** when available. The dependency is flagged in the UI (e.g. server-rendered SVG disabled until Epic 3).
- Update `docs/01-architecture/04-api-routes.md` (new listing route), `docs/01-architecture/02-frontend-architecture.md` (open flow), `frontend/README.md`, and record the listing-endpoint contract + export-ownership decisions in `docs/02-design-and-features/decision-decisions.md`.

## Not In Scope

- Brand-new / blank-canvas diagram creation and save-new file allocation (deferred per Epic 2 out-of-scope).
- A `diagramId` indirection model (stays raw `diagramPath` for the local MVP; *After MVP*).
- PDF export (backlog) and the full `diagram_render` implementation (Epic 3).
- Auth / multi-user workspace concerns.

## Target Areas

- `backend/api/` (new `GET /api/diagrams/list` view + URL) and `backend/tests/` (endpoint tests)
- `backend/services/` — reuse `WorkspaceStorageService.list_diagram_names` (no new storage logic)
- `frontend/src/api/diagrams.ts` (`listDiagrams()`), workspace-browser dialog (new), `frontend/src/editor/EditorPage.tsx` (open flow + export control)
- `docs/01-architecture/04-api-routes.md`, `docs/01-architecture/02-frontend-architecture.md`, `frontend/README.md`, `docs/02-design-and-features/decision-decisions.md`

## Exit Criteria

- `GET /api/diagrams/list` returns the workspace's diagrams with path safety enforced by `WorkspaceStorageService`, covered by backend tests.
- The workspace browser lists and opens diagrams in place, syncing `?diagramPath=` and guarding unsaved edits.
- An export control produces an image of the current diagram (client-side now; ready to switch to Epic 3 server SVG later).
- `python manage.py test`, `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `05-inspector-and-save.md`

## Next Slice

- `07-open-any-file.md`

## Outcome

✅ Completed as planned. Backend: added an additive, read-only `GET /api/diagrams/list` view (`backend/api/views.py` + URL) that derives the workspace from a `path` via `WorkspaceStorageService.for_diagram_path` and returns `{ diagrams: [{ name, path }] }` from `list_diagram_names`/`diagram_file_path`; path safety stays in the service. Covered by 4 new `DiagramListRouteTests` (sorted listing, empty workspace, missing path → 400, outside-`.graphpilot` → 400). Frontend: `listDiagrams()` in `api/diagrams.ts` (+ `DiagramSummary`/`DiagramListResponse` types), a `WorkspaceBrowser` modal (filterable list, opens in place through the existing dirty-guarded `requestOpen`), and a **Browse** control in the TopBar. Export: added `html-to-image` (pinned) + `exportCanvasPng` and an **Export** button — a client-side PNG of the current view, with the export path documented as source-aware (defers to the Epic 3 server `diagram_render` once it exists). Docs: `04-api-routes.md` documents the `list` route. Verified: backend `manage.py test` (22 API tests) OK; frontend `npm run lint` (0/0), `build`, `test` (52/52) pass. Deviation: client-side PNG captures the React Flow viewport (best framed after Fit); full-fidelity SVG/PNG/JPG remain the Epic 3 server-render concern. Follow-up: wire server-rendered export when Epic 3 lands.
