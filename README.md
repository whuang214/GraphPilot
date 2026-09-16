# GraphPilot

GraphPilot is an internal, local-first AI diagramming tool built around two
connected workflows:

1. **IDE-driven** diagram generation, rendering, and validation through MCP
2. **Browser-based** manual editing and export through a React web UI

Both paths read and write the same local GraphPilot JSON file
(`.graphpilot/diagrams/<name>.gp.json`), so a user can move between the IDE and the visual editor without format drift.
The MVP is local-first, database-free, and requires no authentication.

> **AI coding agents:** start with [`AGENTS.md`](AGENTS.md) (the agent entry point), then
> follow its read order. This README is the human-facing front door.

## Current status

The backend and frontend are both substantially implemented. **Live delivery status and next steps:**
`docs/05-delivery/01-current-state.md`.

This README's quickstart and integration list describe the **current runnable repository**. Active design docs describe
the coherent intended system; passing offline implementation gates does not imply visible provider calibration, freeze,
hidden certification, or production promotion.

- **`docs/`** is the source of truth; **`docs/README.md`** is the reading index.
- **`backend/`** — a runnable Django + DRF service with the shared core logic:
  diagram file storage, validation, SVG rendering, layout, and deterministic
  materialization of a host-authored draft. It exposes both the MCP tool
  surface and the browser-facing REST API.
- **`frontend/`** — a React 19 + React Flow editor (Vite, TypeScript, Tailwind v4)
  with a single catalog-driven node renderer (`gpNode`), bounded per-type palettes, undo/redo, dark mode,
  standalone blank/open/recent entry, drag-to-create, and SVG/PNG export.
- **`requirements.txt`** (backend Python deps) and `backend/.env.example` /
  `frontend/.env.example` are provided. Local tooling folders and real environment
  files are excluded from Git.

## Repo layout

```text
GraphPilot/
  README.md
  requirements.txt           # backend Python dependencies
  docs/                      # active documentation set (source of truth)
  backend/
    manage.py
    graphpilot/              # Django project config only (settings, urls, wsgi)
    assets/                  # runtime data: schemas/, blueprints/
    api/                     # browser-facing REST API
    operations/              # operator management commands
    mcp_server/              # MCP server (stdio) for IDE workflows
    services/                # one folder per domain: diagrams/, drafts/,
                             #   materialization/, shared/
    .env.example
    tests/                   # backend test suite, mirrors services/
  frontend/
    package.json
    vite.config.ts
    src/                     # React + React Flow editor (editor/, adapters/,
                             #   api/, ui/, types/)
    e2e/                     # Playwright smoke suite
    .env.example
```

## Quickstart

**Prerequisites** — two tools; everything else is installed by the commands below.

| Need | Why | Check |
| --- | --- | --- |
| [`uv`](https://docs.astral.sh/uv/) | Creates the venv and installs the backend. It also fetches the Python in `.python-version` (3.14), so you do not need one already | `uv --version` |
| Node **20.19+** or **22.12+** | Vite 8 and oxlint require it; the repo is developed on Node 24 | `node --version` |

Nothing else. **No Graphviz install** — PyGraphviz 2.0 bundles its own. **No API key** —
GraphPilot calls no model.

### Just run it

```powershell
python run.py          # or double-click dev.bat  (macOS/Linux: ./dev.sh)
```

Starts both halves in one window, opens your browser, and stops both on Ctrl+C. It takes
its **own ports** — `8010` and `5210`, scanning upward if those are busy — so you can
double-click it while dev servers are running and neither disturbs the other.

You still need the one-time install below first.

### Or run the two halves yourself

**Backend** (from the repo root):

```powershell
uv venv
uv pip install -r requirements.txt
cd backend
copy .env.example .env          # macOS/Linux: cp .env.example .env
uv run python manage.py migrate        # bootstraps Django's internal SQLite tables only
uv run python manage.py runserver 8000
```

**Frontend** (in a second terminal):

```powershell
cd frontend
npm install
copy .env.example .env          # macOS/Linux: cp .env.example .env
npm run dev                     # http://localhost:5173
```

Open http://localhost:5173 with both running. That is the whole setup for *using*
GraphPilot. **You do not need Playwright** — it is only for the end-to-end suite, and its
browsers are a separate one-time download (`npx playwright install chromium`), documented
in [`frontend/README.md`](frontend/README.md).

**There is no provider to configure.** GraphPilot calls no model: a host authors a diagram
draft and the backend materializes it deterministically, so there is no endpoint, no API key,
and `openai` is not a dependency. `backend/.env` covers Django, CORS, storage and the editor
base URL — six variables in total, listed in `backend/.env.example`.
See `docs/04-development/01-environment.md` for the full reference and the PyGraphviz layout
boundary.

## Integration surface

GraphPilot exposes two thin entry points over the same shared services:

- **MCP tools (IDE), 11:** `diagram_workflow` (instructions only, start here),
  `diagram_list_types`, `diagram_get_authoring_contract`, `diagram_check_draft`,
  `diagram_create`, `diagram_read`, `diagram_update`, `diagram_validate`,
  `diagram_render`, plus `health` / `echo`.
- **REST API (browser), 6:** `GET /api/health`, `GET /api/diagrams/load`,
  `POST /api/diagrams/save`, `GET /api/diagrams/list`,
  `POST /api/diagrams/validate`, `POST /api/diagrams/render`.

**A host authors a draft; GraphPilot materializes it.** No model runs on GraphPilot's
side, so a diagram is deterministic given its draft. Exact MCP contracts live in
`docs/02-architecture/01-mcp-tools/`; browser contracts in
`docs/02-architecture/05-api-routes.md`. MVP diagram types are `activity_diagram`,
`use_case_diagram`, and `bdd_diagram`; live progress is owned by
`docs/05-delivery/01-current-state.md`.

## Start here

- **AI agents:** [`AGENTS.md`](AGENTS.md) — the read order and the *Source of truth
  per topic* table.
- **Humans:** `docs/README.md` is the documentation index + reading paths;
  `docs/05-delivery/01-current-state.md` is the live status board.

## Documentation rules

The authoritative working conventions live in [`AGENTS.md`](AGENTS.md).
`docs/01-product` through `docs/05-delivery`
are the active set and must match code; design docs
under `docs/03-design/` are the source of truth (they win over delivery docs); live
status lives only in `docs/05-delivery/01-current-state.md`; decisions only in
`docs/05-delivery/04-decisions.md`; `docs/07-history/` is frozen and never updated.

## Notes

- The `backend/` and `frontend/` README files are the detailed entry points for
  each side; defer to the active docs for cross-cutting scope and architecture.
- Delivery planning lives under `docs/05-delivery/`; each active program has one
  `plan.md` listing its packages.
