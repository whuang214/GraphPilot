# Slice 01: Render Service + `diagram_render`

## Purpose

Render a saved diagram to a sibling SVG, honoring its saved coordinates, and expose it via the `diagram_render` MCP tool. Design: `docs/02-design-and-features/03-rendering-design.md`.

## Included Work

- implement `DiagramRenderService` with a pure `to_svg(diagram)` core and a `render(path)` file wrapper, built on `drawsvg`
- mirror the editor's per-`semanticType` shapes; honor the canonical `style` subset; draw orthogonal edges with UML markers; render containment (containers behind their children)
- add the `drawsvg` dependency (pinned)
- implement the `diagram_render` MCP tool + a smoke-test check, going through `WorkspaceStorageService` for path safety
- tests: render the answer-key examples to valid SVG; cover the error cases (missing / unsafe / malformed)

## Not In Scope

- diagram generation (Slices 03–04)
- finished PNG/PDF export (a documented future path only — see the design doc)
- re-layout (rendering trusts the saved coordinates; layout is Slice 02)

## Target Areas

- backend render service + MCP tool + tests
- `requirements.txt`
- rendering design + MCP-tools docs

## Exit Criteria

- `render(path)` writes a sibling `<name>.svg`; `to_svg` returns a well-formed SVG with no I/O
- the answer-key examples render to valid SVG matching the editor's shapes
- `diagram_render` returns `svgPath`; missing / unsafe / malformed inputs return the common error shape
- `python manage.py test` + the MCP smoke test pass

## Previous Slice

- Start of Epic 3.

## Next Slice

- `02-layout.md`

## Outcome

✅ Completed.

**Delivered.** `DiagramRenderService` renders a saved canonical diagram to SVG, mirroring the editor's per-`semanticType` shapes and honoring the saved coordinates (no re-layout), exposed via the `diagram_render` MCP tool.

- **Service** (`backend/services/diagrams/rendering/diagram_render_service.py`): pure `to_svg(diagram)` core (no I/O) + `render(path)` file wrapper, built on `drawsvg`. Resolves `parentId` children to absolute positions (containers drawn behind contents), draws orthogonal connectors with UML-style ends (plain arrow for flow/association/reference, dashed for include/extend, hollow triangle for generalization, filled diamond at the source for composition), honors the canonical `style` subset (incl. dashed/dotted borders), and centers labels. Markers are drawn as oriented polygons (the orthogonal route always ends axis-aligned), so no SVG marker-defs are needed.
- **Shapes:** activity start/end = pill, action = rounded box, decision/merge = diamond; use-case actor = stick figure, useCase = ellipse, systemBoundary = transparent container box; BDD = titled «stereotype» compartment box; note = folded sticky note (shared across types).
- **File I/O stays in `WorkspaceStorageService`:** added an atomic `write_text(path, text)` primitive (path-safe, temp-file + `os.replace`); `render` writes the sibling `<name>.svg` beside the source.
- **MCP tool** (`mcp_server/server.py`): `diagram_render(diagramPath) -> {svgPath}`; maps missing / malformed / outside-workspace / unsafe / render failures to the common `{error:{code,message}}` shape. Smoke test extended with a render success + missing-file case.
- **Dependency:** `drawsvg==2.4.0` pinned in `requirements.txt`.

**Verification.** `python manage.py test` → 168 tests OK (was 151; +17 render tests, all 12 answer-key examples render to valid SVG). `python mcp_server/smoke_test.py` → all checks PASS.

**Deviations.** "Unsafe path" for this flow is realistically the *outside-`.graphpilot`* case (`workspace_resolution_error`), since `render()` derives the workspace from the path's `.graphpilot` ancestor; `UnsafePathError` is still mapped defensively. drawsvg 2.4.0 uses SVG-native (y-down) coordinates, matching React Flow positions directly. PNG/PDF remain a documented future path (drawsvg → cairo), out of scope here.

**Follow-ups.** None blocking. Visual fidelity vs the editor is "close, not pixel-perfect" by design; layout for *generated* (coordinate-less) diagrams arrives in Slice 02.

**Post-slice additions (verification aids, by request).** To make it easy to confirm the backend render matches the editor's shapes:

- **Path-free `POST /api/diagrams/render`** (`api/views.py`): inline `{diagram}` → `{svg}`, no file write — mirrors the existing path-free `validate` route. Backs an editor **"Preview render"** toolbar button + modal that posts the same canonical JSON a save would and shows the backend SVG for a 1:1 comparison against the React Flow canvas. (`frontend`: `renderDiagram()` client, `Toolbar` button, a wider `Modal` `size` option.) This is a small, intentional deviation from the epic's "browser routes out of scope (Epic 2)" line — it's a verification companion to the MCP tool, justified and logged in `decision-decisions.md`.
- **Render-on-save** (`api/views.py` `POST /api/diagrams/save`): a successful save now also writes the sibling `<name>.svg` via `DiagramRenderService` (best-effort — the save still succeeds if render fails) and returns `svgPath`; the editor toast reports the rendered file. This realizes the render-on-save that Epic 2 deferred to Epic 3. Applies to the path-based workspace save; the File-System-Access "open any file" save path does not write a sibling SVG (no `.graphpilot` root).
- **Cline MCP wiring**: a `graphpilot` server merged into the user's `cline_mcp_settings.json` so `diagram_render` (and the Epic 1 tools) can be exercised from the IDE agent.
- **In-chat image preview is deferred**: MCP image blocks need a raster (PNG), which requires a native SVG→PNG rasterizer (cairo) — the same dependency deferred for PNG/PDF export. For now the MCP `diagram_render` returns `svgPath`; open the `.svg` (e.g. VS Code's built-in SVG preview).

Verification after the additions: `python manage.py test` → 172 OK; frontend `npm run lint` clean, 89 unit tests pass, `npm run build` (typecheck) OK.
