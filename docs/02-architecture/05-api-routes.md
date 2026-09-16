# API Routes

> **Design authority:** This document defines the browser-facing HTTP contract. Runtime delivery status belongs
> only to [`epics/00-current-state.md`](../05-delivery/01-current-state.md).

## 1. Purpose

This document owns the UI-facing Django API route contracts used by the React frontend.

## 2. API Role

For GraphPilot MVP:

- the API is the browser-facing entry point
- the React frontend calls the API only
- API routes call shared backend services
- API routes should stay thin
- the core UI loop is load + save; the editor also uses list, validate, and render

## 3. Common Rules

These rules apply across the UI-facing API:

- `diagramPath` is used for MVP
- the backend validates path safety
- the workspace root is derived from the absolute `diagramPath` (the parent of the `.graphpilot` storage folder); reads and writes must stay under that derived root. See `docs/02-architecture/03-backend.md` (Workspace resolution by entry point) for the safety model.
- saves validate before overwrite
- invalid saves are rejected
- blueprint drift alone should not block a normal React UI save by default
- handled failures return `{ "error": OperationProblem }` with an appropriate non-2xx HTTP status; the shared
  problem model is owned by [backend architecture](03-backend.md#91-shared-operational-problem)
- workspace-path saves go through Django; picker-opened local files are the explicit exception and are written through the browser file handle only after path-free backend validation
- evidence/request/readiness/context generation is MCP-only; the browser API exposes no context HTTP routes
- all `/api/*` routes omit the trailing slash (e.g., `/api/health`, `/api/diagrams/save`)

## 4. Route Summary

The browser API surface lives under `/api/` with no trailing slash:

| Route | Method | Purpose | Shared service | Writes files |
| --- | --- | --- | --- | --- |
| `/api/health` | GET | Liveness check (`{ "status": "ok" }`) | — | No |
| `/api/diagrams/load?path=...` | GET | Load an existing diagram | `WorkspaceStorageService` | No |
| `/api/diagrams/save` | POST | Revision-safe validate/overwrite from the editor; render-on-save writes the sibling `<name>.svg` | `DiagramPersistenceService` + `DiagramRenderService` | Yes |
| `/api/diagrams/list?path=...` | GET | List canonical diagrams under `.graphpilot/diagrams/` (workspace browser) | `WorkspaceStorageService` | No |
| `/api/diagrams/validate` | POST | Validate inline diagram JSON and return the normalized diagram (path-free; "open any file" flow) | `DiagramValidationService` | No |
| `/api/diagrams/render` | POST | Render inline diagram JSON to an SVG string (path-free; editor preview + image export) | `DiagramRenderService` | No |

The core browser loop is load + save; list, validate and render back the workspace browser, the external-file flow, and preview/export respectively. There are **no** `/api/diagram-types` or `/api/schema` routes — schema and type lookup are MCP-only (see section 9).

There was also a `POST /api/diagrams/resolve`, which mapped a picker-opened file back to its absolute path. It was removed: nothing in the editor ever called it, and the flow it was built for was never asked for.

## 5. `GET /api/diagrams/load`

### Purpose

Load an existing saved diagram for the visual editor.

### Query params

| Param | Required | Notes |
| --- | --- | --- |
| `path` | Yes | Path to a `<name>.gp.json` diagram file |

### Success response

```json
{
  "diagramPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json",
  "diagram": {
    "schemaVersion": "graphpilot.diagram.v1",
    "kind": "diagram",
    "diagramType": "activity_diagram",
    "id": "diagram_abc123",
    "name": "Order Approval",
    "metadata": {},
    "viewport": { "x": 0, "y": 0, "zoom": 1 },
    "nodes": [
      {
        "id": "node_review",
        "type": "gpNode",
        "position": { "x": 100, "y": 100 },
        "data": { "label": "Review Order", "semanticType": "opaqueAction" }
      }
    ],
    "edges": []
  },
  "revision": "3c49d5…"
}
```

`revision` is an opaque SHA-256 content token. The editor retains it as the expected revision for the next workspace save and uses it to detect external changes.

### Error cases

| Code | HTTP | When |
| --- | --- | --- |
| `missing_path` | 400 | `path` query param is absent/empty |
| `invalid_path` | 400 | the path is not inside a `.graphpilot` workspace (workspace cannot be derived) |
| `unsafe_path` | 400 | the resolved path escapes the derived workspace root |
| `not_found` | 404 | no file at the resolved path |
| `invalid_json` | 422 | the file is not valid JSON / not a JSON object |
| `load_failed` | 422 | residual I/O error (e.g. permission denied) |

### Compact example

```text
GET /api/diagrams/load?path=C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json
```

### Companion: `GET /api/diagrams/list`

Read-only listing that backs the editor's workspace browser. Given a canonical `path` inside a workspace, it returns the named diagrams stored under `.graphpilot/diagrams/`. Path safety stays in `WorkspaceStorageService`; no files are written.

```json
{
  "diagrams": [
    { "name": "order-approval", "path": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json" }
  ]
}
```

Errors: `missing_path` (400) when `path` is absent, `invalid_path` (400) when the workspace cannot be derived, and `list_failed` (422) on a residual I/O error.

## 6. `POST /api/diagrams/save`

### Purpose

Validate and save an existing diagram from the visual editor.

This is the primary UI write route for the MVP.

This save flow should block invalid or unsafe GraphPilot JSON, not ordinary blueprint drift after manual editing.

### Request body

```json
{
  "diagramPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json",
  "expectedRevision": "3c49d5…",
  "diagram": {
    "schemaVersion": "graphpilot.diagram.v1",
    "kind": "diagram",
    "diagramType": "activity_diagram",
    "id": "diagram_abc123",
    "name": "Order Approval",
    "metadata": {},
    "viewport": { "x": 0, "y": 0, "zoom": 1 },
    "nodes": [
      {
        "id": "node_review",
        "type": "gpNode",
        "position": { "x": 100, "y": 100 },
        "data": { "label": "Review Order", "semanticType": "opaqueAction" }
      }
    ],
    "edges": []
  }
}
```

`expectedRevision` is optional for compatibility, but normal workspace sessions send the revision returned by load/save. A mismatch returns `source_changed` (`409`) and performs no validation write. Omitting it is an explicit last-write-wins overwrite decision.

### Success response

On a successful save the route also performs **render-on-save** (best-effort): it writes the sibling `<name>.svg`
beside the saved JSON via `DiagramRenderService` and returns its path as `svgPath`. If rendering fails after the
canonical save, the route remains HTTP `200`, omits `svgPath`, and returns `warning: OperationProblem` so the UI
can report stage-correct partial success without suggesting another save.

```json
{
  "saved": true,
  "diagramPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json",
  "diagram": { "...": "the normalized document that was written" },
  "revision": "91a4b7…",
  "svgPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.svg"
}
```

The editor adopts `diagram` after success so reconciled `diagramType` and provenance match disk immediately.
`svgPath` remains optional because render-on-save is best-effort. A render failure returns:

```json
{
  "saved": true,
  "diagramPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json",
  "diagram": { "...": "the normalized document that was written" },
  "revision": "91a4b7…",
  "warning": {
    "code": "render_failed",
    "message": "The diagram was saved, but SVG rendering failed.",
    "retryable": true,
    "details": {
      "diagramPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json",
      "intendedSvgPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.svg"
    }
  }
}
```

The UI may offer render/export retry but must not repeat the already successful save automatically.

### Validation failure response

Returned with HTTP `422 Unprocessable Content`. Only blocking (`error`-severity) issues appear in
`error.details.issues`; blueprint/type drift warnings do not appear and do not block the save.

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Diagram validation failed. The existing file was not overwritten.",
    "retryable": true,
    "details": {
      "issues": [
        {
          "code": "missing_edge_target",
          "message": "Edge edge_2 references a missing target node.",
          "path": "$.edges[1].target"
        }
      ]
    }
  }
}
```

### Error cases

- missing `diagramPath` (`missing_path`, 400)
- missing or non-object `diagram` (`invalid_diagram`, 400)
- `diagramPath` not inside a `.graphpilot` workspace (`invalid_path`, 400)
- path escapes the workspace root (`unsafe_path`, 400)
- a valid save targets a file that does not exist (`not_found`, 404); creation goes through a generation tool / `DiagramPersistenceService.create`
- loaded source revision no longer matches `expectedRevision` (`source_changed`, 409); the file remains untouched
- diagram fails validation (`validation_failed`, 422)
- residual I/O error while writing (`save_failed`, 422)

### File overwrite behavior

- save uses the shared `DiagramPersistenceService` validation and file save flow
- before validating, the route **reconciles `diagramType`** (flips it to `custom` when the board uses elements outside its declared type's vocabulary) and stamps the informational `metadata.authoring = "custom"`, so a hand-edited diagram is saved in one canonical form — strictness follows `diagramType`, not `authoring`
- validate before overwrite
- reject invalid saves
- do not overwrite the source JSON when invalid
- blueprint-related warnings do not block save by default
- normal editor saves are compare-and-save through `expectedRevision`; an explicitly confirmed conflict overwrite omits that token

### Notes

- this is the main write route for the browser MVP
- save owns its validation; the separate path-free `POST /api/diagrams/validate` route exists for the open-any-file flow, not for path-based saves
- save refreshes the sibling SVG after a successful write (best-effort render-on-save) and returns
  `warning: OperationProblem` if only that derived stage fails; the path-free `POST /api/diagrams/render` route
  backs preview/export and does not write files

### Compact example

```text
POST /api/diagrams/save
```

## 7. `POST /api/diagrams/validate`

### Purpose

Validate **inline** diagram JSON, with no path and no write. This is the verification half of the editor's **open-any-file** flow: a diagram opened from anywhere on disk (File System Access API, possibly outside a `.graphpilot` workspace) is validated here before the browser writes it back through a file handle. The route normalizes the diagram (reconciling `diagramType` — flipping it to `custom` when the board is off-vocabulary — and stamping the informational `metadata.authoring = "custom"`) and returns that normalized form so the client persists a single canonical shape. Backed by `DiagramValidationService` (called directly; the validate route does not go through the persistence funnel).

> This route returns a **different, simpler shape** than the MCP `diagram_validate` tool. It returns `valid` + the blocking `validationErrors` + the normalized `diagram` (the fields the open-any-file client needs), not the full `ValidationResult` (`level`/`summary`/`issues`/`stats`). For the full result shape, use the MCP tool (`03-mcp-tools/README.md`).

### Request body

Inline `diagram` only (there is no `diagramPath` mode):

```json
{
  "diagram": {
    "schemaVersion": "graphpilot.diagram.v1",
    "kind": "diagram",
    "diagramType": "activity_diagram",
    "id": "diagram_abc123",
    "name": "Order Approval",
    "metadata": {},
    "viewport": { "x": 0, "y": 0, "zoom": 1 },
    "nodes": [
      {
        "id": "node_review",
        "type": "gpNode",
        "position": { "x": 100, "y": 100 },
        "data": { "label": "Review Order", "semanticType": "opaqueAction" }
      }
    ],
    "edges": []
  }
}
```

### Success response

`valid` is `true` when there are no blocking (`error`-severity) issues; `validationErrors` lists only blocking issues (warnings are omitted). `diagram` is the normalized diagram the client should write.

```json
{
  "valid": true,
  "validationErrors": [],
  "diagram": {
    "schemaVersion": "graphpilot.diagram.v1",
    "kind": "diagram",
    "diagramType": "activity_diagram",
    "id": "diagram_abc123",
    "name": "Order Approval",
    "metadata": { "authoring": "custom" },
    "viewport": { "x": 0, "y": 0, "zoom": 1 },
    "nodes": [
      {
        "id": "node_review",
        "type": "gpNode",
        "position": { "x": 100, "y": 100 },
        "data": { "label": "Review Order", "semanticType": "opaqueAction" }
      }
    ],
    "edges": []
  }
}
```

### Validation failure response

Still HTTP `200`; `valid` is `false` and `validationErrors` carries the blocking issues (`diagram` omitted here for brevity).

```json
{
  "valid": false,
  "validationErrors": [
    {
      "code": "missing_edge_target",
      "message": "Edge edge_2 references a missing target node.",
      "path": "$.edges[1].target"
    }
  ]
}
```

### Error cases

- missing or non-object `diagram` (`invalid_diagram`, 400)

### Compact example

```text
POST /api/diagrams/validate
{ "diagram": { ... } }  ->  { "valid": true, "validationErrors": [], "diagram": { ... } }
```

## 8. `POST /api/diagrams/render`

### Purpose

Render **inline** diagram JSON to an SVG string. **Path-free and write-free** — it neither reads nor writes any file. As the verification companion to the MCP `diagram_render` tool, the editor's "Preview render" action posts the same canonical JSON a save would send and shows the returned SVG, so the server-rendered shapes can be compared against the React Flow canvas. Backed by `DiagramRenderService.to_svg`.

(The file-based render — load a saved `<name>.gp.json` and write the sibling `<name>.svg` — is the **MCP `diagram_render` tool** (`03-mcp-tools/README.md`) and is also run best-effort as render-on-save inside `POST /api/diagrams/save`. A standalone path-based browser render route remains a possible future addition.)

### Request body

```json
{
  "diagram": { "schemaVersion": "graphpilot.diagram.v1", "kind": "diagram", "...": "..." }
}
```

### Success response

```json
{
  "svg": "<?xml version=\"1.0\" ...><svg ...>...</svg>"
}
```

### Error cases

- missing or non-object `diagram` → `400 invalid_diagram`
- the diagram cannot be rendered (e.g. missing `nodes`) → `422 render_failed`

### Compact example

```text
POST /api/diagrams/render
{ "diagram": { ... } }  ->  { "svg": "<?xml ...>" }
```

## 9. Diagram-type and schema lookup (MCP only)

There are **no** `GET /api/diagram-types` or `GET /api/schema` routes. Supported-type and authoring-summary lookup are exposed only through the MCP tools `diagram_list_types` and `diagram_get_authoring_contract` (`03-mcp-tools/README.md`). The React frontend works from a fixed supported-type set and does not need either route.

The backend services exist (`DiagramTypeService`, `SchemaRegistry`) and could be surfaced as thin HTTP routes later — e.g. `{ "diagramTypes": [...] }` and a schema summary — if a UI need arises. They are documented here only as a possible future addition.

## 10. Common Error Response

Every handled HTTP failure uses an appropriate status plus the same `OperationProblem` value used by MCP:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Diagram validation failed. The existing file was not overwritten.",
    "retryable": true,
    "details": {
      "diagramPath": "C:/workspaces/sample-app/.graphpilot/diagrams/order-approval.gp.json",
      "issues": [
        {
          "code": "missing_edge_target",
          "message": "Edge edge_2 references a missing target node.",
          "path": "$.edges[1].target"
        }
      ]
    }
  }
}
```

`code`, `message`, and `retryable` are required. `details` is optional and follows the exact code-specific schema;
paths and validation issues are never ad-hoc top-level fields. HTTP status expresses transport semantics and is
not duplicated in `OperationProblem`. Validation/reporting routes still return ordinary HTTP `200` domain results
when the requested assessment succeeds but finds invalid input.

| Code family | `retryable` | `details` |
| --- | ---: | --- |
| `missing_path`, `invalid_path`, `unsafe_path`, `not_found`, `invalid_json`, `invalid_diagram` | `true` after correcting input/local state | Omitted |
| `load_failed`, `list_failed`, `save_failed`, `render_failed` | `true` after correcting input/environment or retrying the failed stage | `render_failed` may include `diagramPath` and `intendedSvgPath`; otherwise omitted |
| `validation_failed` | `true` after correcting the complete diagram | Required `issues[]` with `code`, `message`, and nullable `path`; optional `diagramPath` |
| `internal_error` | `false` | Omitted |

No identical automatic retry is implied by `retryable: true`.

## 11. What the browser deliberately does not do

The browser is a canonical-diagram editor. It loads, validates, renders and saves
`.graphpilot/diagrams/*.gp.json`, preserving `origin` and `metadata.evidence` on documents
that carry them and working on documents that do not.

**Authoring is not a browser action.** A draft is written by a host that has read the
source and can cite it, and there is no route here that accepts one — `diagram_create` is
the MCP surface's job and the citation checking that makes a diagram trustworthy needs a
workspace to read.

*(This section previously described JSON 1/JSON 2 authoring, readiness and context
generation as living on the MCP surface. That pipeline was retired in `P0`; the boundary it
described no longer has two sides.)*
