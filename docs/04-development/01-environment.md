# Development Environment

## Purpose

This document owns GraphPilot's local environment, runtime configuration, generation defaults, and fixed provider-safety
bounds. Setup instructions and sections labeled **Current runtime** describe code that can be run today. Sections labeled
**Final intended redesign** describe the promoted Epic 3 contract implemented through the audited redesign slices; use
the [current-state board](../05-delivery/01-current-state.md) for delivery status.

GraphPilot MVP runs locally with:

- Django backend
- Django REST Framework API
- MCP server under the backend
- React frontend with Vite
- React Flow for diagram display/editing
- Local file storage in the user project workspace

## Local Services

```text
Django API:
  http://localhost:8000

React Vite app:
  http://localhost:5173

MCP server:
  launched locally through IDE MCP configuration
```

## Repository Structure

```text
graphpilot/
  .venv/
  .gitignore
  requirements.txt

  backend/
    manage.py
    graphpilot/
    api/
    mcp_server/
    services/
    tests/

  frontend/
    package.json
    vite.config.*
    src/

  docs/
```

- `.venv/` should be created at the GraphPilot repo root.
- `.gitignore` should live at the GraphPilot repo root.
- Root `.gitignore` should ignore `.venv/`, Python cache files, local env files, frontend build artifacts, dependency folders, and generated local artifacts as needed.
- `.python-version` (repo root) pins **Python 3.14** and is read automatically by `uv` (and pyenv); commit it — do **not** gitignore it. Create/manage the backend env with `uv` (`uv venv` + `uv pip install -r requirements.txt`).

## User Workspace Storage

Generated diagrams are stored in the user project workspace, not necessarily inside the GraphPilot app repo.

### Current runtime

```text
<user-project-workspace>/
  .graphpilot/
    context/
      evidence/repository.gp-evidence.json
      requests/<name>.gp-request.json
      drafts/<name>.gp-evidence.candidate.json
      debug/readiness/                 # optional
    diagrams/
      order-approval.gp.json
      order-approval.svg
```

The implemented context workflow still stores JSON 2 beneath `context/requests/`. Existing explicit flat
`.graphpilot/<name>.*` diagram paths remain readable/editable, but current new allocation/listing does not dual-write,
migrate, or delete them.

### Final intended redesign

```text
<user-project-workspace>/
  .graphpilot/
    context/
      evidence/repository.gp-evidence.json
      drafts/<candidate>.json
    requests/<diagramName>.gp-request.json
    diagrams/
      <diagramName>.gp.json
      <diagramName>.gp.trace.json       # optional
      <diagramName>.svg
      <diagramName>.png                 # optional
    diagnostics/generation/<request-id>/<run-id>/
    evaluation/runs/<run-id>/
```

- `.graphpilot/` remains the workspace-local storage root.
- Direct and context requests use separate strict schemas but share `.graphpilot/requests/` and one validated request
  lifecycle; old request paths are not silently migrated, rewritten, or deleted.
- `<diagramName>.gp.json` is canonical; SVG/PNG, compact trace, diagnostics, and evaluation runs are derived,
  non-canonical artifacts with purpose-specific bounds.
- Path containment and atomic writes remain owned by `WorkspaceStorageService`.

## Backend

Currently implemented backend tools/libraries:

- Python
- Django
- Django REST Framework
- MCP Python SDK
- local file storage
- validation services
- rendering support for SVG

Current backend setup:

```text
uv venv
uv pip install -r requirements.txt
cd backend
copy .env.example .env   # macOS/Linux: cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver 8000
```

- `migrate` bootstraps Django's default internal tables (sessions, auth, etc.) but is not used for diagram persistence.
- Diagram data stays in the workspace `.graphpilot/` folders as local files.

### Generation layout

Pinned `pygraphviz==2.0` is the sole generation layout engine and invokes bundled libgvc `dot` in process. Supported
packaged wheel targets are Windows x64, macOS x64/ARM64, and Linux x64/AArch64. Windows ARM64 uses the packaged x64
GraphPilot/Python runtime under emulation; native Windows ARM64 Python and automatic source builds are unsupported.
There is no engine selector, source-build recovery, external executable path, or alternate algorithm. Existing user-owned
local Graphviz installations are untouched but unused. Missing wheel/plugin support fails with
`layout_engine_unavailable`; malformed or failed native layout returns `layout_failed` without another attempt. See the
[final generation design](../03-design/01-generation/README.md#pygraphviz-layout) for the contract.

### There is no provider to configure

**GraphPilot calls no model.** A host authors a draft, GraphPilot materializes it, and the
result is deterministic given that draft — so there is no endpoint, no key, no deployment,
and no `openai` dependency. The whole test suite is offline because there is nothing to be
online for.

This section used to instruct a reader to set `AZURE_OPENAI_ENDPOINT`, an API key and a
`gpt-5.4` deployment for two generation tools that no longer exist,
along with input limits, a quality mode and a semantic-repair round count. All of it was
removed with the provider pipeline; none of those tools, settings or commands exist.

`backend/.env` still exists for local overrides of the settings that are real — the
storage folder, and the frontend base URL. `.env.example` records them.

```text
GRAPHPILOT_FRONTEND_BASE_URL=http://localhost:5173
```

**This file describes the dev setup**, so that line names the dev origin like the CORS
line above it and `VITE_API_BASE_URL` in `frontend/.env`. You do not need to change any of
them to use the launcher: `run.py` passes its own ports to the processes it starts, and
neither `load_dotenv()` nor Vite overrides a real environment variable, so the launched
pair syncs to each other while this file keeps governing hand-started dev servers.

The one thing that cannot work that way is `editUrl`. A diagram can be edited in two
places — the dev server on `5173` or the launcher's app on `5210` — and the MCP server
that builds the link is a **third** process, started by your IDE, that knows about
neither. So it resolves rather than reads:
[`services/shared/editor_origin.py`](../../backend/services/shared/editor_origin.py)
uses a **GraphPilot** dev server if one answers on 5173, otherwise the launcher. It checks
for GraphPilot's own index page rather than an open socket, because 5173 is Vite's default
and someone else's React app may be sitting there.

Because this file is the dev template, a value that simply *is* the dev origin counts as
"unset" for that purpose. **Any other value is a deliberate pin** and skips resolution
entirely — set one only to point somewhere neither instance is, such as a reverse proxy.

That subtlety is the bug this was built out of: the line shipped as
`http://localhost:5173`, every install therefore looked "explicit", the resolver never
ran, and anyone using only the launcher got a well-formed link to a port nothing was
serving. It was found by running it; reading the resolver, it looked right.

To connect an IDE host to the MCP surface over real stdio, launch
`uv run python mcp_server/server.py` from `backend/`. The host provides tool calls; no
repository-local agent skill is required.

## Frontend

Known frontend tools/libraries:

- Node.js
- Vite
- React
- React Flow

Expected setup:

```text
cd frontend
npm install
copy .env.example .env   # macOS/Linux: cp .env.example .env
npm run dev
```

## Environment Variables

Backend copy-ready examples (matching `backend/.env.example`):

**Six variables, and `settings.py` reads exactly these.** Anything else in a `.env` is
ignored, so the list below is the whole surface.

```text
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
# DJANGO_DEBUG=false requires a strong non-example DJANGO_SECRET_KEY or startup fails.
GRAPHPILOT_CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173  # required
GRAPHPILOT_STORAGE_DIR=.graphpilot
GRAPHPILOT_FRONTEND_BASE_URL=http://localhost:5173              # dev origin = resolve it
```

All three describe **hand-started dev servers**. `run.py` passes its own values to the
processes it starts, and neither `load_dotenv()` nor Vite overrides a real environment
variable, so the launcher's ports win for its own instance without this file changing.

This list previously carried eleven more: seven `AZURE_OPENAI_*` keys, two input limits, a
generation quality mode, and a semantic-repair round count. **Nothing read any of them.**
They went with the provider pipeline, and `.env.example` had already dropped them.

The fixed 16 MiB/8 MiB provider and 16 MiB/128 MiB diagnostics ceilings are deliberately absent: they are code-owned,
not environment overrides. The final configuration likewise has no example-count or layout-engine/path setting.

Frontend examples:

```text
VITE_API_BASE_URL=http://localhost:8000
```

The MCP server needs no environment of its own. Every tool takes `workspaceDir` as an
argument, so which repository is being diagrammed is a property of the call rather than of
the deployment.

*(A `GRAPHPILOT_DEFAULT_WORKSPACE_DIR` was listed here and read by nothing. An operator who
set it got no error and no effect.)*

- Do not commit secrets.
- Local `.env` files should be ignored by git.

## Known Tooling Decisions

```text
Backend framework: Django
API framework: Django REST Framework
MCP: MCP Python SDK
Frontend: React
Frontend dev server: Vite
Diagram UI: React Flow
Storage: local files in user workspace under .graphpilot/
Diagram files: named files like order-approval.gp.json under .graphpilot/diagrams/
Source of truth: <name>.gp.json
Artifact format: SVG
Database: none for MVP (Django's default SQLite tables are kept for framework internals only; diagram persistence is local files)
Docker: not required for MVP
```
