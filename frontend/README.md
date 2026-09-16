# Frontend

The GraphPilot frontend is a React 19 + TypeScript + Vite editor built on React Flow. It treats GraphPilot JSON
as canonical, uses the Django API for workspace persistence and rendering, and uses the browser File System
Access API only for explicitly picker-opened local files.

- **Stack:** React 19.2, `@xyflow/react` 12.6, Vite 8.1, TypeScript ~6.0, and Tailwind v4.
- **Runtime:** no routing library; every URL renders the editor and optional `?diagramPath=` selects a workspace
  file. `VITE_API_BASE_URL` defaults to `http://localhost:8000`.
- **Design owners:** practical runtime behavior belongs to
  [`02-frontend-architecture.md`](../docs/02-architecture/04-frontend.md); editor look, interaction
  intent, and UX boundaries belong to
  [`editor-ui-design.md`](../docs/03-design/06-editor-ui.md).

## Major capabilities

- Open IDE-linked path diagrams directly, or use the standalone searchable New Diagram chooser/Open/drop/reopenable-Recents landing page; path and writable-file revision checks refresh clean sources and block stale writes.
- Edit bounded core nodes and relationships with scope/organization-aware shape groups plus one catalog-driven connector tray, a Content/Appearance/Advanced inspector, move/connect/reconnect,
  persisted straight or manual-first orthogonal routing, per-type next-edge defaults, primitive-aligned full-boundary and parallel same-pair connections, exact diamond cardinal targets, valid-target guidance, soft visual-cardinal aim-lock, movable anchors/segments/labels, safe corner-pair deletion/route straightening, one-Block BDD stereotypes, palette-to-selected-edge identity/mode changes, Content-tab edge identity, duplicate,
  copy/paste/delete, inline rename, undo/redo, theme, minimap, guides, container-behind-content layering, larger node-resize grabbers, and resizable shell rails.
- Round-trip canonical diagram data through the React Flow adapter and save through Django, with blocking
  validation surfaced inline and optional debounced autosave.
- Preview server-rendered SVG, inspect the JSON diff since the last save, and export SVG or PNG from the same
  canonical server render.
- Render core and retained compatibility elements through the shared `gpNode` family while preserving Block headings, Composition markers, Comment Links, Note dog-ears, and canvas/SVG parity.

Exact editor flows, adapter rules, save/error handling, and component behavior are intentionally not duplicated
here; use the two design owners above and the API contract in
[`04-api-routes.md`](../docs/02-architecture/05-api-routes.md).

## Setup

```text
cd frontend
npm install
cp .env.example .env   # Windows: copy .env.example .env
npm run dev            # http://localhost:5173
```

The backend must be running at the configured API base for load/save/list/validate/render operations. See
[`backend/README.md`](../backend/README.md).

### Scripts

| Script | Purpose |
| --- | --- |
| `npm run dev` | Start the Vite development server |
| `npm run build` | Type-check and build with `tsc -b && vite build` |
| `npm run lint` | Run `oxlint` |
| `npm run test` | Run the Vitest unit suite |
| `npm run e2e` | Run the Playwright browser suite |
| `npm run verify` | Run lint, build, unit tests, and e2e |
| `npm run preview` | Preview a production build |

## Project layout

```text
frontend/
  package.json
  vite.config.ts
  vitest.config.ts
  playwright.config.ts
  src/
    main.tsx, App.tsx, index.css
    types/                 canonical GraphPilot JSON types
    api/diagrams.ts        load/save/list/validate/render client
    adapters/reactFlow.ts  GraphPilot JSON <-> React Flow mapping
    editor/
      EditorPage.tsx       composition root
      components/          palette, inspector, menus, browser, toolbar
      canvas/              React Flow nodes, edges, overlays, minimap
      shell/               top/status bars and resizable rails
      lib/                 pure editor helpers
      hooks/               editor hooks and contexts
    ui/                    in-house UI primitives
  e2e/                     Playwright smoke suite
  .env.example
```

Use [`src/editor/README.md`](src/editor/README.md) for the editor file map. Cross-folder imports use the `@/`
alias (`@` → `src/`); same-folder imports remain relative. The alias is configured consistently in TypeScript,
Vite, and Vitest.

## Testing

Unit tests use Vitest, React Testing Library, and `jsdom`:

```text
npm run test
```

End-to-end tests use Playwright with Chromium and start Django plus Vite:

```text
npx playwright install chromium   # one-time
npm run e2e
npm run e2e -- --headed
```

Playwright starts dedicated test servers on `127.0.0.1:15173` (Vite) and `127.0.0.1:18080` (Django), never reusing the development ports. Override them with `GRAPHPILOT_E2E_FRONTEND_PORT` and `GRAPHPILOT_E2E_BACKEND_PORT` when needed.

The comprehensive 17-node movement smoke waits for the viewport to settle and has a 60-second budget to include traced browser teardown.

Run the full local gate with:

```text
npm run verify
```

Native file-picker operations (`Open file…` and `Save As`) cannot be automated reliably and remain manual
checks. There is no CI for the MVP; testing policy is owned by
[`01-testing-strategy.md`](../docs/04-development/02-testing-strategy.md).

## Boundaries

- The frontend never calls MCP and never directly writes workspace paths; it calls Django API routes.
- Picker-opened file handles are Chromium-only and session-owned; persistent Recents contain only backend paths GraphPilot can actually reopen.
- GraphPilot JSON remains canonical; React Flow state, `gpStyle`, and calculated automatic routes are derived editor/runtime state.
- The planned context-backed extension adds no context-authoring UI; frontend work is limited to optional
  trace/provenance preservation and the coordinated canonical diagram-path cutover until separately designed.
- Current implementation claims belong to the frontend architecture owner; live delivery status belongs only
  to the [current-state board](../docs/05-delivery/01-current-state.md).

## Read next

1. [`docs/README.md`](../docs/README.md)
2. [`02-frontend-architecture.md`](../docs/02-architecture/04-frontend.md)
3. [`editor-ui-design.md`](../docs/03-design/06-editor-ui.md)
4. [`04-api-routes.md`](../docs/02-architecture/05-api-routes.md)
5. [`01-diagram-json-mapping-design.md`](../docs/02-architecture/06-diagram-json-mapping.md)
