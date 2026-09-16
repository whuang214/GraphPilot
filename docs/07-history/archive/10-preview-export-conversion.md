# 10 Preview Export Conversion

## Preview URL Strategy

GraphPilot is preview-first in the MVP.

Generated diagrams are returned as JSON by default, and preview URLs are used to open editable diagrams in the UI without requiring durable persistence.

## Temporary Preview Cache

Preview URLs are backed by a temporary local preview cache.

Suggested folder:

```text
.graphpilot/cache/previews/
  preview_abc123.graphpilot.json
  preview_def456.graphpilot.json
  index.json
```

Preview entries should store normalized GraphPilot JSON and be resolved by `previewId`.

## Preview Sequence

```mermaid
sequenceDiagram
    participant Cursor as Cursor / IDE
    participant MCP as GraphPilot MCP Server
    participant Core as GraphPilot Core
    participant Cache as Preview Cache
    participant UI as React UI
    participant API as Local API

    Cursor->>MCP: graphpilot_generate(prompt)
    MCP->>Core: generate()
    Core->>Core: Generate and validate diagram JSON
    Core->>Cache: Store preview_abc123.graphpilot.json
    Core->>MCP: Return previewUrl
    MCP->>Cursor: Show clickable preview URL
    Cursor->>UI: User clicks preview URL
    UI->>API: GET /api/previews/preview_abc123
    API->>Cache: Read preview JSON
    Cache->>API: Return normalized diagram JSON
    API->>UI: Return diagram
    UI->>UI: Convert with local adapter and render with React Flow
```

## Cache Cleanup Policy

The preview cache should:

- keep recent previews
- delete previews older than the configured TTL
- enforce a max cache size
- delete oldest entries first when over the limit
- run cleanup on startup and after preview creation

## Cache Cleanup Flow

```mermaid
flowchart TD
    A[Create preview] --> B[Write preview JSON to cache]
    B --> C[Update preview index]
    C --> D[Run cleanup]
    D --> E[Delete previews older than TTL]
    E --> F{Cache size over limit?}
    F -->|No| G[Done]
    F -->|Yes| H[Sort previews by lastAccessedAt or createdAt]
    H --> I[Delete oldest previews]
    I --> F
```

## Frontend Visual Export

Frontend handles visual export in the browser for the MVP.

MVP export formats:

- JSON
- PNG
- JPG
- SVG if practical
- PDF later through browser print or export flows

## Frontend Export Flow

```mermaid
flowchart TD
    A[Current React Flow Canvas] --> B[Convert current state to GraphPilot JSON]
    B --> C[User clicks Export]
    C --> D{Format}
    D -->|JSON| E[Download .graphpilot.json]
    D -->|PNG| F[Browser captures rendered diagram as PNG]
    D -->|JPG| G[Browser captures rendered diagram as JPG]
    D -->|SVG| H[Browser exports SVG if practical]
    D -->|PDF| I[Future browser print/export]
```

## Backend Conversion

Backend handles semantic and text-based conversion through:

- `graphpilot_convert`
- `POST /api/convert`
- `conversion_service`

The first major convert target is Mermaid Markdown.

## Backend Convert Flow

```mermaid
flowchart TD
    A[GraphPilot JSON] --> B[Deterministic draft]
    A --> C[Build semantic preservation context]
    B --> D[LLM polish/conversion]
    C --> D
    D --> E[Validate against source GraphPilot JSON]
    E --> F{Valid?}
    F -->|Yes| G[Return converted content]
    F -->|No| H[LLM repair once]
    H --> I[Validate again]
    I --> J{Valid?}
    J -->|Yes| G
    J -->|No| K[Return best output with warnings]
```

## Mermaid Markdown Conversion

Recommended hybrid approach:

1. deterministic draft
2. GraphPilot semantic context
3. LLM polish
4. validation against the source GraphPilot JSON
5. one repair attempt if needed

## Future or Deferred Work

Backend image or PDF rendering is future or deferred work.

Examples:

- backend image or PDF export using Playwright
- backend SVG renderer
- Mermaid parser validation
- HTML document conversion
