# Slice 09: Server Rendered Export

## Purpose

Make the editor's image export use the **server-side renderer** (`DiagramRenderService` → SVG) as the canonical path instead of the interim `html-to-image` DOM screenshot, and align the MCP `diagram_render` tool to the same payload-based (inline-JSON) workflow so the editor and agents share one render path. Closes the export-fidelity defect (feature-list #13) and adopts the remote-MCP-ready render contract.

## Background

- Export today is `exportCanvasPng` in `frontend/src/editor/lib/exportImage.ts` — a client-side `html-to-image` (`toPng`) snapshot of the `.react-flow__viewport` DOM. It is a DOM screenshot, not a render of the model, so it is low-fidelity and blacks out edge labels (feature-list #13).
- The server renderer already exists: `DiagramRenderService.to_svg(diagram)` is a pure function (canonical JSON → SVG) that honors the saved coordinates and mirrors the editor's shapes, and it is already exposed as the path-free `POST /api/diagrams/render` (inline JSON → `{ svg }`) — documented as the editor's "Preview render".
- The MCP `diagram_render(diagramPath)` tool is **path-based** (reads a file, writes a sibling `.svg`, returns the path). The agreed direction (decision log, *export* row; `03-rendering-design.md`) is **one canonical renderer** shared by editor + preview + agents, payload-based, with SVG primary and PNG derived from it.
- Decision: SVG is rendered **server-side** (pure Python, no native dependency); the editor's **PNG is rasterized from the returned SVG client-side** (no native dependency, works on Windows). A server-side PNG for agents and PDF are explicitly later (cairo is non-trivial on Windows).

## Design

### Editor export (frontend)

- On Export, build the canonical JSON the editor would save (`reactFlowToGraphPilot(...)`, the same call `performSave` uses), `POST` it to `/api/diagrams/render`, and use the returned SVG.
- Offer **SVG** (download the returned SVG directly) and **PNG** (rasterize the returned SVG: load it into an `Image` via a Blob URL, draw to a `<canvas>` at a fixed scale, `toBlob('image/png')`, download). No new dependency; rasterizing clean SVG avoids the DOM-screenshot black-label bug.
- Remove `html-to-image` as the primary path. Keep a minimal offline fallback only if the render endpoint is unreachable (rasterize a client-built SVG, or disable with a clear message) — **never a DOM screenshot**. Drop the `html-to-image` dependency if no fallback retains it.
- Optional: a small "Preview render" affordance that shows the server SVG inline (same endpoint), since it is the canonical output.

### MCP tool alignment (backend, coordinated with Epic 3)

- Give the MCP `diagram_render` tool an **inline-JSON workflow**: accept the diagram object and return its SVG (mirroring `diagram_validate(diagram: dict)` and the HTTP `render` endpoint), reusing `DiagramRenderService.to_svg`, so the editor and agents share one workflow and it is remote-ready (no filesystem needed).
- Keep the existing **path-based file mode** (read `<name>.gp.json`, write the sibling `<name>.svg`, return the path) for the local file-beside artifact and render-on-save.

## Included Work

- **Frontend:** rewire the Export control in `EditorPage.tsx` to call `/api/diagrams/render`; add an `exportImage.ts` SVG download + client-side SVG→PNG rasterizer; remove `html-to-image` as the primary path (drop the dependency if the fallback is unneeded). Add/adjust unit tests.
- **Backend (MCP):** add the inline-JSON mode to the `diagram_render` MCP tool returning `{ svg }` (reusing `DiagramRenderService.to_svg`), keeping the path mode; cover with smoke/unit tests.
- **Docs:** update `docs/01-architecture/03-mcp-tools/01-diagram-tools.md` (the inline `diagram_render` workflow) and `frontend/README.md` (export flow). `docs/02-design-and-features/03-rendering-design.md` and the export decision in `decision-decisions.md` are already updated; mark feature-list #13 as addressed.

## Not In Scope

- **Server-side PNG/JPG raster for agents** and **PDF** — deferred (the "other formats later" path; needs a native backend — cairo / resvg / headless).
- A `format=png` parameter on the HTTP render endpoint (the editor rasterizes client-side; server raster is the deferred agent path).
- Switching the MCP transport (stdio → HTTP) and the remote server itself; the file-storage model for a remote deployment.
- Editor-canvas vs. render **parity** fixes (e.g. edge routing #14) — export already uses the clean server render; canvas alignment is a separate, tracked item.

## Target Areas

- `frontend/src/editor/lib/exportImage.ts` (SVG download + SVG→PNG raster), `frontend/src/editor/EditorPage.tsx` (Export control), `frontend/src/api/diagrams.ts` (render client), `frontend/package.json` (drop `html-to-image` if unused), frontend tests.
- `backend/mcp_server/server.py` (`diagram_render` inline mode), `backend/mcp_server/smoke_test.py` / backend tests.
- `docs/01-architecture/03-mcp-tools/01-diagram-tools.md`, `frontend/README.md`.

## Exit Criteria

- The editor's Export produces an **SVG** and a **PNG** from the server render (`/api/diagrams/render`), for both `mcp`- and `local`-sourced diagrams; edge labels render correctly (feature-list #13 closed).
- `html-to-image` is no longer the primary export path (and the dependency is removed unless a fallback retains it).
- The MCP `diagram_render` tool renders from **inline JSON** (returns `{ svg }`) as well as the existing path mode, covered by tests.
- The load → edit → save round-trip stays byte-stable (export is read-only; no adapter/schema change).
- `python manage.py test`, `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `08-open-and-landing.md`

## Next Slice

- `10-node-fidelity.md` — the **P1** node-fidelity pass (dark-mode legibility, note fold, on-canvas resize), the first of the prioritized (P1–P4) feature-list slices 10–15 re-sliced from `../../../../02-design-and-features/editor-ui-design.md`.

## Outcome

Complete. The editor's image export now renders **server-side** and the MCP `diagram_render` tool gained a matching inline-JSON mode, so the editor and agents share one render path.

**What was delivered**
- Frontend: the `Export` control is now a small inline menu (`ExportMenu`) offering **SVG** and **PNG**. Both build the canonical JSON (`reactFlowToGraphPilot`) and `POST` it to `/api/diagrams/render`; `exportImage.ts` downloads the returned SVG directly, or rasterizes it to a PNG client-side (`Image` -> `<canvas>` on a white background -> `toBlob('image/png')`). The `html-to-image` DOM-screenshot path and dependency were removed, fixing the blacked-out edge labels (feature-list #13).
- Refactor (per review): a shared `getServerSvg` helper in `EditorPage` is reused by both the existing "Preview render" and the new export, so they render identically.
- Backend (MCP): `diagram_render` now accepts inline `diagram` (returns `{ svg }`, no file I/O) in addition to `diagramPath` (returns `{ svgPath }`, unchanged); providing neither/both yields `invalid_arguments`.

**Deviations from the plan**
- Export-format UI: built as a small inline popover menu (user's choice) rather than two buttons or a modal; added as an editor-local `ExportMenu` component (no new `ui/` primitive, keeping the change focused).
- No server-side PNG/JPG/PDF (still deferred — needs a native backend).

**Verification**
- Frontend: `npm run lint` (0 warnings), `npm run build` (clean), `npm run test` (196 vitest tests pass, incl. new `exportImage` + `ExportMenu` suites). The two Playwright export specs were updated to drive the menu (PNG + SVG); run with `npm run e2e`.
- Backend: `python manage.py test` (263 tests, OK) incl. new inline-render tool tests; the stdio MCP `smoke_test.py` passes incl. the new inline `diagram_render` check.
- Load -> edit -> save round-trip stays byte-stable (export is read-only).

**Follow-ups**
- Next Phase 2 item: **#6 on-canvas resize** (the deferred Slice 10 rider).
- Server-side raster for **agents is now delivered** (a later follow-on to this slice): `DiagramRenderService.to_png` / `render_png` rasterize the same SVG via `resvg-py` (a prebuilt wheel — no native cairo), powering `diagram_render` `format="png"` (an explicit `<name>.png` **file** save; requires `diagramPath`). The MCP tools return a Markdown summary + links, **not** an inline image (an `ImageContent` block was tried and reverted — agent-loop clients don't render it cleanly); a true **inline preview** and **PDF** remain later follow-ons. See the PNG-raster row in `../../../../02-design-and-features/decision-decisions.md`.
