# Slice 01: Browser Load and Display

## Purpose

Deliver the first browser-facing vertical slice by loading a saved GraphPilot diagram through Django and rendering it in a display-first React UI.

## Included Work

- implement the minimal browser-facing load route, including `GET /api/diagrams/load`
- derive the workspace root from the absolute `diagramPath` (parent of the `.graphpilot` folder) when constructing `WorkspaceStorageService`
- handle the `/editor` route in the frontend without adding a router dependency (read `pathname` + `diagramPath` via `window.location` / `URLSearchParams`)
- read the `diagramPath` query parameter
- call the Django load API
- adapt GraphPilot JSON to React Flow display state
- render the diagram in display-first mode
- handle missing-path and load-error states clearly
- provide one sample diagram to prove the load flow, placed in a local example/test workspace at `<workspace>/.graphpilot/<name>.gp.json`

This sample mirrors the real storage model: `.graphpilot/` is created inside the **end-user's project workspace** (the directory the MCP server is pointed at, e.g. the folder open in the IDE), not inside the GraphPilot app repo. The Slice 01 sample is therefore a diagram living in such a workspace, not a `frontend/` asset. It is a throwaway demo fixture and is not the canonical sample; the canonical per-type samples are authored and finalized in Slice 04 under `backend/assets/blueprints/<type>/examples/sample.gp.json`.

## Not In Scope

- editing, the reverse adapter, and the save flow (Slice 03)
- the save/validate backend routes (Slice 02)
- finalizing canonical sample fixtures (Slice 04)
- export flows
- autosave
- frontend-to-MCP communication

## Target Areas

- `frontend/`
- `frontend/README.md`
- backend API entry points needed for the minimal browser flow
- a local example/test workspace containing `.graphpilot/<name>.gp.json` for the load demo (not committed as a frontend asset)
- frontend architecture or mapping docs if implementation clarifies them

## Exit Criteria

- a sample diagram can be loaded through Django and displayed in the browser
- the frontend uses GraphPilot JSON as the source of truth
- the UI does not persist React Flow runtime-only fields into canonical GraphPilot JSON
- the browser flow proves the editor foundation before save is completed

## Next Slice

- `02-save-and-validate-api.md`

## Outcome

✅ Completed as planned. Implemented the browser-facing load + display vertical slice.

**Delivered.**

- Backend: added `GET /api/diagrams/load` as a thin handler over shared services. Added `WorkspaceStorageService.for_diagram_path()` (derives the workspace root from the parent of the `.graphpilot` folder) plus a `WorkspaceResolutionError`, and a `DiagramErrorResponse` common error shape (`{code, message}`). Errors map to `missing_path`/`invalid_path` (400), `unsafe_path` (400), `not_found` (404), and `invalid_json` (422).
- Frontend: added `types/diagram.ts`, `api/diagrams.ts` (`loadDiagram` + `DiagramApiError`), `adapters/reactFlow.ts` (forward-only adapter), and `editor/EditorPage.tsx`. `App.tsx` routes `/editor` (via `window.location`/`URLSearchParams`, no router) and renders the diagram display-first with `@xyflow/react`, handling missing-path/loading/error states.
- Sample/fixture: per a planning clarification, `.graphpilot/` is the **end-user project workspace** folder (where the MCP server is pointed), so it is now gitignored as local scratch; a committed seed sample lived at `samples/diagrams/activity_diagram.gp.json` with `samples/README.md` documenting the copy-to-workspace step. Canonical per-type samples remain a Slice 04 deliverable. *(Update: the repo-root `samples/` folder was retired in Slice 07; the demo seed now copies directly from a backend `examples/<name>/output.gp.json` — see `frontend/README.md`.)*

**Deviations.** (1) sample location/git handling clarified with the team (gitignored repo-root `.graphpilot/` + committed seed under `samples/`) rather than a committed `frontend/` asset. (2) Nodes render with React Flow's built-in `default` node; custom per-type node renderers are deferred to a later slice. No SVG render placeholder was added (render is owned by Epic 3; the optional seam belongs to Slice 02's `DiagramPersistenceService`).

**Verification.** backend `python manage.py test` → 119 tests pass (7 new in `tests/api/test_api.py`); frontend `npm run build` and `npm run lint` pass; a live `runserver` load of the seeded sample returned `200` with the expected diagram (4 nodes / 3 edges) and resolved `diagramPath`.

**Follow-up.** Slice 02 — `DiagramPersistenceService` + `POST /api/diagrams/save` (validate-then-overwrite), where the optional SVG-refresh seam can be introduced.