# 03 System Architecture

## Architecture Overview

GraphPilot is an MCP-first, database-free, local-file-based system with two request entry points feeding a shared backend core.

Major components:

- React UI
- Local HTTP API
- MCP Server
- GraphPilot Core
- Azure OpenAI
- Local blueprint files
- Temporary preview cache

## High-Level Architecture Diagram

```mermaid
flowchart LR
    Cursor[Cursor / IDE] --> MCP[MCP Server]
    React[React UI] --> API[Local HTTP API]

    MCP --> Core[GraphPilot Core]
    API --> Core

    Core --> Blueprints[backend/blueprints]
    Core --> Azure[Azure OpenAI]
    Core --> PreviewCache[Temporary Preview Cache]
    Core --> Outputs[Optional Local Outputs]
```

## High-Level Request Flow

```mermaid
flowchart TD
    A[User asks for diagram] --> B{Entry point}
    B -->|Cursor / IDE| C[MCP Tool]
    B -->|React UI| D[Local API Route]
    C --> E[GraphPilot Core]
    D --> E
    E --> F[Route or load blueprint]
    F --> G[Generate/Edit/Convert]
    G --> H[Validate result]
    H --> I[Return JSON, preview URL, or converted output]
```

## Request Entry Points

### Cursor / IDE

Cursor or another IDE uses MCP tools for backend generation, edit, and conversion workflows.

### React UI

The React UI uses the local HTTP API to preview diagrams, edit them visually, and request backend conversion where needed.

## High-Level Flows

### Generate

- route request if `blueprintKey` is missing
- load the selected blueprint
- generate GraphPilot JSON
- validate the result
- return diagram JSON and optional preview URL

### Edit

- load the current diagram context and blueprint
- request edits from the backend
- validate the edited result or patch
- return patch operations or updated diagram JSON

### Convert

- accept semantic or text-based source input
- run deterministic, LLM, or hybrid conversion
- validate against source semantics when appropriate
- return converted output and validation results

## Where Detailed Design Lives

- see `docs/04-backend-architecture.md` for backend flow and service detail
- see `docs/05-frontend-architecture.md` for frontend routes, editor flows, and export detail
- see `docs/06-mcp-tools.md` for MCP tool behavior and clarification flow
- see `docs/07-api-routes.md` for local API route contracts
- see `docs/10-preview-export-conversion.md` for preview, convert, and export details
