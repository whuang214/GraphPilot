# Slice 07: Open Any File

## Purpose

Today the only ways to open a diagram are hand-typing its absolute `?diagramPath=` (`OpenControl`) or the workspace browser (Slice 06), both of which require the file to live under a derivable `.graphpilot/` workspace so the backend can read/write it **by path**. Users want to open a diagram file from anywhere on disk via the native file picker and save it back in place. This slice adds that "open any file" capability and a coherent **Save / Save As** model that coexists with the existing path-based, MCP-driven flow.

## Background

- `frontend/src/api/diagrams.ts` `loadDiagram()`/`saveDiagram()` are keyed on an **absolute path**; the backend (`backend/api/views.py`) derives the workspace root from that path and reads/writes the file (`GET /api/diagrams/load`, `POST /api/diagrams/save`). The frontend never touches files directly.
- A standard `<input type="file">` OS dialog deliberately **hides the file's absolute path** from the browser, so it cannot drive "save back to where you opened it" through the path-based endpoints.
- The **File System Access API** (`window.showOpenFilePicker` / `showSaveFilePicker`) hands the page a writable `FileSystemFileHandle`, so the browser can open **and** write back to a file at its picked location without ever learning the absolute path. This is the only browser mechanism that satisfies "open any file" + "save back in place" + "save a copy elsewhere".
- Validation in the backend is **workspace-independent** — `DiagramValidationService.validate(diagram)` takes only the diagram, not a path (see `backend/services/diagrams/persistence/diagram_persistence_service.py`). That is the seam that lets a file opened from *anywhere* still be validated by the backend before it is written.
- This slice is backend-dependent: it adds one additive, path-free `POST /api/diagrams/validate` so validation always runs on the backend first and only the *write* differs by source, leaving the canonical schema and the `load`/`save` contract unchanged.

## Design

### Save sources

A diagram in the editor has exactly one **save source**:

| Source  | Opened via                       | Default Save target                  | Save As |
|---------|----------------------------------|--------------------------------------|---------|
| `mcp`   | `?diagramPath=<abs path>`        | **Locked** to that path (path-based) | ✅       |
| `local` | `showOpenFilePicker()`           | The picked `FileSystemFileHandle`    | ✅       |

- **`mcp`** is the existing flow: a file produced/opened through the MCP path-based workflow. Its default Save is locked back to the original path for a simple, predictable round-trip.
- **`local`** is the new flow: any file picked from disk. Its default Save writes to the handle it was opened from.
- **Save As** is available for **all** sources: it picks a new location (`showSaveFilePicker()`), writes a copy there, and then **adopts** that new handle as the current `local` source (subsequent Saves go to the copy; the original is untouched).

### Save flow (unified validation, split write)

1. Build canonical GraphPilot JSON from the React Flow state (existing `reactFlowToGraphPilot`).
2. **Always validate via the backend first** — `POST /api/diagrams/validate` (path-free). It reuses `DiagramValidationService`, applies the `metadata.authoring='custom'` normalization (today inline in the save view), performs **no write**, and returns `{ valid, validationErrors, diagram }` where `diagram` is the normalized diagram the client should write (single source of truth for normalization).
3. If **invalid** → surface the per-issue errors (reusing the Slice 05 inline-validation UX); write nothing. Same guarantee as today: an invalid diagram never overwrites a file.
4. If **valid** → write, by source:
   - **`mcp` default Save** → existing `POST /api/diagrams/save` (it validates + does the atomic, path-safe write by path). The backend stays the owner of path-based writes.
   - **`local` default Save** → write the normalized diagram to the current `FileSystemFileHandle` via `createWritable()`.
   - **Save As (any source)** → `showSaveFilePicker()` → write the normalized diagram to the new handle → adopt it as the current `local` source.

### Browser support + reload

- File System Access API is **Chromium-only** (Chrome/Edge). This is accepted (see Decisions). On non-Chromium browsers the "Open file…" / `local` Save / Save As affordances are disabled with a clear message; the path-based `OpenControl` + workspace browser (Slice 06) + MCP Save keep working.
- File handles **do not survive a page refresh** (MVP): a `local`-opened file must be re-opened via the picker after reload. `mcp` files re-load automatically from `?diagramPath=`. No IndexedDB handle persistence in this slice.

## Included Work

- **Backend validate endpoint (additive, path-free)**: `POST /api/diagrams/validate` taking `{ diagram }` and returning `{ valid, validationErrors, diagram }` (normalized). Reuse `DiagramPersistenceService`/`DiagramValidationService` (no write, no workspace resolution); follow the camelCase response + no-trailing-slash route conventions; add backend tests. Extract the `metadata.authoring='custom'` stamp so `save` and `validate` share one normalization helper.
- **Frontend File System Access helper** (`frontend/src/editor/lib/fileSystem.ts`): feature detection, `openLocalDiagram()` (picker → read → JSON parse), `writeHandle(handle, diagram)`, `saveAs(diagram)` (`showSaveFilePicker`), and read/write permission handling (`queryPermission`/`requestPermission`).
- **Frontend API**: add `validateDiagram(diagram)` to `frontend/src/api/diagrams.ts` (mirrors the existing `DiagramApiError` + `validationErrors` shape; **no change** to `load`/`save`).
- **Editor wiring** (`frontend/src/editor/EditorPage.tsx`): track the active save source (`mcp` path vs `local` handle); add an **"Open file…"** affordance (picker) alongside the existing path `OpenControl` and the Slice 06 workspace browser; route **Save** / **Save As** through validate-then-write; honor the existing unsaved-changes guard; show the current target (path or file name) in the header.
- Update `docs/01-architecture/04-api-routes.md` (new `validate` route), `docs/01-architecture/02-frontend-architecture.md` (save-source model + open flow), `frontend/README.md`, and record the **File System Access API (Chromium-only)** + **`/validate` endpoint** decisions in `docs/02-design-and-features/decision-decisions.md`.

## Not In Scope

- Any change to the canonical schema, the supported style subset, or the `load`/`save` contract (the `validate` endpoint is additive and never writes).
- IndexedDB handle persistence across reloads (re-pick on reload for `local` files).
- A Firefox/Safari write path (those browsers get display + path-based flows only).
- Brand-new / blank-canvas diagram creation and save-new file allocation (deferred per Epic 2).
- A `diagramId` indirection model (stays raw `diagramPath` / file handle for the local MVP).

## Target Areas

- `backend/api/` (new `POST /api/diagrams/validate` view + URL), `backend/services/` (shared `authoring='custom'` normalization helper; reuse `DiagramPersistenceService`), `backend/tests/`
- `frontend/src/api/diagrams.ts` (`validateDiagram()`), `frontend/src/editor/lib/fileSystem.ts` (new), `frontend/src/editor/EditorPage.tsx` (save-source model + open/save/save-as wiring)
- `docs/01-architecture/04-api-routes.md`, `docs/01-architecture/02-frontend-architecture.md`, `frontend/README.md`, `docs/02-design-and-features/decision-decisions.md`

## Exit Criteria

- `POST /api/diagrams/validate` validates a diagram with no write and no workspace resolution, returns the normalized diagram + `validationErrors`, and is covered by backend tests.
- On a Chromium browser, "Open file…" opens any `.gp.json` from disk; **Save** writes back to the opened location (handle for `local`, original path for `mcp`); **Save As** writes a copy to a chosen location and adopts it as the current source.
- Validation always runs first; an invalid diagram never overwrites any file and surfaces errors via the Slice 05 inline-validation UX.
- On non-Chromium browsers the path-based open + MCP Save still work and the `local` affordances are cleanly disabled with a message.
- The save round-trip stays byte-stable (adapters/schema untouched).
- `python manage.py test`, `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `06-browse-and-export.md`

## Next Slice

- End of the **core** `04-editor-ui-ux` group (Epic 2, S01–S07, merged). One refinement slice followed — `08-open-and-landing.md` (the open/landing rework, built against `../../../../02-design-and-features/editor-ui-design.md`). Remaining editor polish is tracked in that design doc's *Feature Requests and Known Issues* list (to be re-sliced when scheduled). Follow-on UI/distribution work (single-process serve, installer, desktop app, in-UI AI generate) lives under the **local internal distribution** theme in `../../../02-backlog.md`.

## Outcome

✅ Completed as planned. Backend: added a path-free, write-free `POST /api/diagrams/validate` (`DiagramPersistenceService.validate` + a `diagram_validate` view) returning `{ valid, validationErrors, diagram }`, and extracted the `metadata.authoring='custom'` stamp into a shared `_stamp_custom_authoring` helper used by both `save` and `validate`. Added 4 `DiagramValidateRouteTests` (valid → normalized, invalid → errors, missing/non-object → 400). Frontend: `validateDiagram()` client + `DiagramValidateResponse` type; a `fileSystem.ts` helper (locally-typed, no global ambient or new dep) with feature detection + `openLocalDiagram`/`writeHandle`/`saveAsLocalDiagram`; and an editor save-source model — picker-opened files carry a `FileSystemFileHandle` and Save validates-then-writes to it, while `mcp` (path) files keep the existing path-based save. Added **Open file…** / **Save As** controls (Chromium-gated, disabled with an explanatory title elsewhere) and an Open-file affordance on the missing-path state. Verified: backend `manage.py test` (151 tests) OK incl. validate; frontend `npm run lint` (0/0), `build`, `test` (52/52) pass. Deviation: `local` file handles are not persisted across reloads (re-pick after refresh), as planned. Follow-up: none.
