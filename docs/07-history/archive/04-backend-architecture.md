# 04 Backend Architecture

## Backend Responsibilities

The backend owns:

- blueprint loading and routing
- prompt construction
- Azure OpenAI calls
- generate, edit, and convert workflows
- validation
- preview cache creation and cleanup
- local config files and runtime env configuration
- examples and output folders used by backend workflows

The backend does **not** own browser image export for the MVP.

## Suggested Backend Folder Structure

**This is the suggested structure for the MVP. It can change if implementation needs require it.**

```text
backend/
  README.md
  .env.example
  requirements.txt
  blueprints/
  config/
  examples/
  outputs/
  graphpilot_core/
    services/
    schemas/
  mcp_server/
  local_api/
```

## Backend Component Diagram

```mermaid
flowchart TD
    MCP[MCP Server] --> Core[GraphPilot Core]
    API[Local HTTP API] --> Core

    Core --> BlueprintService[Blueprint Service]
    Core --> Router[Blueprint Router]
    Core --> PromptBuilder[Prompt Builder]
    Core --> Generation[Generation Service]
    Core --> Edit[Edit Service]
    Core --> Convert[Conversion Service]
    Core --> Validation[Validation Service]
    Core --> Preview[Preview Service]
    Core --> Cost[Cost Service]

    Generation --> Azure[Azure OpenAI]
    Edit --> Azure
    Convert --> Azure

    BlueprintService --> Blueprints[backend/blueprints]
    Preview --> Cache[.graphpilot/cache/previews]
```

## GraphPilot Core Services

Suggested service areas:

- blueprint service
- blueprint router
- prompt builder
- generation service
- edit service
- conversion service
- validation service
- preview service
- cost service
- file or output helper service if needed

## MCP Server

The MCP server is the IDE-facing backend entry point.

Responsibilities:

- expose `graphpilot_generate`, `graphpilot_edit`, and `graphpilot_convert`
- validate tool input
- call GraphPilot Core directly
- return structured results without blocking for user interaction

## Local HTTP API

The local HTTP API is the UI-facing backend entry point.

Responsibilities:

- expose local UI routes
- return preview JSON by `previewId`
- call GraphPilot Core directly
- return JSON responses for generate, edit, and convert workflows

## Preview Cache

The preview cache is temporary local storage used to support preview URLs.

Suggested location:

- `.graphpilot/cache/previews/`

The preview cache should:

- store normalized GraphPilot JSON
- generate preview IDs
- clean up old entries over time
- avoid exposing arbitrary file paths

## Generate Pipeline

```mermaid
sequenceDiagram
    participant Client as MCP or Local API
    participant Core as GraphPilot Core
    participant Router as Blueprint Router
    participant BP as Blueprint Service
    participant AI as Azure OpenAI
    participant Val as Validation Service
    participant Cache as Preview Cache

    Client->>Core: generate(prompt, optional blueprintKey)
    Core->>Router: select blueprint if needed
    Router->>BP: load routing catalog
    BP->>Router: blueprint metadata
    Router->>Core: selected blueprint
    Core->>BP: load full blueprint
    Core->>AI: generate GraphPilot JSON
    AI->>Core: diagram JSON
    Core->>Val: validate diagram
    Val->>Core: validation result
    Core->>Cache: create preview if requested
    Core->>Client: response with diagram, validation, usage, preview
```

## Edit Pipeline

```mermaid
sequenceDiagram
    participant Client as MCP or Local API
    participant Core as GraphPilot Core
    participant BP as Blueprint Service
    participant AI as Azure OpenAI
    participant Val as Validation Service

    Client->>Core: edit(diagram, prompt)
    Core->>BP: load blueprint from metadata or routing
    BP->>Core: blueprint
    Core->>AI: request patch operations
    AI->>Core: patch operations
    Core->>Core: apply patch to temp diagram
    Core->>Val: validate temp diagram
    Val->>Core: validation result
    Core->>Client: patch, validation, usage
```

## Convert Pipeline

```mermaid
flowchart TD
    A[Input format] --> B[Conversion Service]
    B --> C{Target format}
    C -->|GraphPilot| D[Normalize/validate GraphPilot JSON]
    C -->|Mermaid MD| E[Deterministic draft]
    E --> F[LLM polish with GraphPilot context]
    F --> G[Validate against source]
    G --> H{Valid?}
    H -->|Yes| I[Return converted content]
    H -->|No| J[Repair once]
    J --> I
```
