# Backend

The GraphPilot backend is a Django + Django REST Framework service containing the shared
core used by the React API and the IDE-facing MCP server. Both entry points stay thin and
delegate diagram storage, validation, layout, rendering, and materialization to `services/`.

**The backend makes no provider calls.** The host authors a diagram
[draft](../docs/03-design/01-generation/01-draft.md); the backend materializes it
deterministically. There is no API key to configure.

> **Runtime boundary:** commands, capability names, dependencies, and file maps here
> describe the **currently implemented backend**. Canonical contracts live in
> [`01-generation/`](../docs/03-design/01-generation/README.md); delivery status lives on
> the [current-state board](../docs/05-delivery/01-current-state.md).

- **Stack:** Django 6.0.6, Django REST Framework 3.17.1, `django-cors-headers`,
  `jsonschema`, `mcp`, `drawsvg`, `resvg-py`, `pygraphviz==2.0` (pinned in the repository
  `requirements.txt`).
- **Storage:** local diagrams and sibling SVG/optional PNG artifacts under a workspace's
  `.graphpilot/diagrams/`. Django's SQLite file is for framework internals only.
- **Diagram types:** `activity_diagram`, `use_case_diagram`, and `bdd_diagram`; schema
  validation and save also accept the universal `custom` canvas.

## Capability boundaries

- **Browser API (`api/`):** health plus diagram load, save, list, validate, and render.
  Routes, payloads, path rules, and responses are owned by
  [`05-api-routes.md`](../docs/02-architecture/05-api-routes.md).
- **IDE MCP (`mcp_server/`):** connectivity, type and schema lookup, the authoring
  contract, diagram creation from a draft, validation, and rendering over stdio. Tool
  contracts are owned by
  [`01-mcp-tools/`](../docs/02-architecture/01-mcp-tools/README.md).
- **Shared services (`services/`):** role-grouped backend logic with absolute imports.
  See [`services/README.md`](services/README.md) for the file map and
  [`03-backend.md`](../docs/02-architecture/03-backend.md) for dependency boundaries.

## Setup

From the GraphPilot repository root:

```text
uv venv
uv pip install -r requirements.txt
cd backend
cp .env.example .env          # Windows: copy .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver 8000
```

`.env` carries workspace and CORS settings only. The MCP server is a separate stdio
process normally launched by an IDE client:

```text
uv run python mcp_server/server.py
```

Full environment and MCP wiring guidance lives in
[`01-environment.md`](../docs/04-development/01-environment.md).

## Management commands

Run from `backend/`:

```text
uv run python manage.py render_example_gallery
```

`render_example_gallery` creates an offline HTML review sheet of the curated examples under
the gitignored `review_galleries/`; use `--types`, `--pools`, and `--open` as needed.

That is the complete set; `manage.py help` is the check. The readiness-calibration,
effort-benchmark, deployment-listing, and evaluation rigs were retired with the
provider-backed pipeline.

## Project layout

```text
backend/
  manage.py
  graphpilot/          Django project config only: settings, urls, asgi, wsgi
  assets/              runtime data read by the services
    schemas/           diagram.json and the draft contract
    blueprints/        per-type notation guidance and curated examples
  api/                 browser-facing views, URLs, and HTTP DTOs
  operations/          installed app holding the operator management commands
  mcp_server/          stdio MCP entry point
  services/
    shared/            schema registry, identities, canonical JSON, file I/O
    diagrams/          catalog/ validation/ layout/ persistence/ rendering/
    drafts/            draft validation, evidence, authoring contract
    materialization/   draft -> logical -> canonical
  tests/               mirrors services/
  .env.example
```

`PyGraphvizLayoutEngine` is the sole implementation behind the flat layout seam.
Cross-service imports are absolute and modules are imported from the file that defines
them; there are no re-export shims. See [`services/README.md`](services/README.md) before
editing that package.

## Testing

Run from `backend/`:

```text
uv run python manage.py test --parallel 24
```

The suite is fully offline and deterministic. **There is no provider seam to fake** — the
LLM client, readiness, and semantic review were removed, and their fake clients and
call-budget fixtures went with them. Testing policy is owned by
[`02-testing-strategy.md`](../docs/04-development/02-testing-strategy.md).

## Scope and limitations

- Persistence is local-file only; there are no application database models or authentication.
- Standalone validation is inline-only; file-backed operations own path resolution and
  safety. MCP rendering supports inline SVG and path-backed SVG/PNG modes.
- `diagram_create` refuses to overwrite an existing diagram.
- `diagram_get_semantic_view` and `diagram_update` are planned with
  [editing](../docs/03-design/05-edit/README.md), not implemented.
- Pinned PyGraphviz 2.0 is the only layout runtime. Missing wheel or plugin support and
  native layout failure are explicit non-retryable errors; no alternate engine or local
  executable path is attempted.

## Read next

1. [`docs/README.md`](../docs/README.md)
2. [`03-backend.md`](../docs/02-architecture/03-backend.md)
3. [`01-mcp-tools/`](../docs/02-architecture/01-mcp-tools/README.md)
4. [`05-api-routes.md`](../docs/02-architecture/05-api-routes.md)
5. [`03-validation/`](../docs/03-design/03-validation/README.md)
