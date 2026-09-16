# 07 API Routes

## Purpose

The local HTTP API exists for the React UI only. It calls GraphPilot Core directly.

It is not meant to replace the MCP server, and it is not a general-purpose public cloud API surface.

## MVP Routes

```text
GET  /api/blueprints
POST /api/generate
POST /api/edit
POST /api/convert
GET  /api/previews/{previewId}
```

Do not include these as MVP routes:

- `POST /api/files/save`
- `POST /api/render`

## Design Rules

- frontend export is browser-based
- the UI does not need an API file save route for MVP
- MCP may still write `outputPath` when explicitly provided
- backend should avoid arbitrary file path reads or writes from the UI

## Shared Response Envelope

Responses should use:

- `status`
- `data`
- `clarification`
- `error`
- `usage`
- `validation`

## Route Summary

### `GET /api/blueprints`

Returns locally available blueprint metadata for the UI.

### `POST /api/generate`

Generates a new diagram from a prompt.

Typical fields:

- `prompt`
- `blueprintKey` (optional)
- `modelKey` (optional)
- `outputPath` (optional)
- `createPreview` (optional)

### `POST /api/edit`

Edits an existing diagram.

Typical fields:

- `diagram`
- `editPrompt`
- `blueprintKey` (optional)
- `modelKey` (optional)
- `returnMode`

### `POST /api/convert`

Converts between semantic and text-based formats.

Typical use cases:

- GraphPilot JSON -> Mermaid Markdown
- GraphPilot JSON -> normalized GraphPilot JSON
- React Flow JSON -> GraphPilot JSON

### `GET /api/previews/{previewId}`

Loads a temporary preview diagram from preview cache using `previewId`.

## Notes

- local API routes should remain thin wrappers around GraphPilot Core
- preview loading should never expose arbitrary raw paths
- detailed blueprint structure belongs in `docs/08-blueprint-design.md`
