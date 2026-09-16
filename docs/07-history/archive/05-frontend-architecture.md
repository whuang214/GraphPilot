# 05 Frontend Architecture

## Frontend Responsibilities

The frontend owns:

- preview rendering in React Flow
- manual diagram editing
- GraphPilot-to-React-Flow adapter logic
- agent panel requests for generate, edit, and convert
- browser-based JSON export
- browser-based PNG, JPG, and SVG export if practical

The frontend is UI-only and must not contain Azure OpenAI secrets.

## Suggested Frontend Folder Structure

**This is the suggested structure for the MVP. It can change if implementation needs require it.**

```text
frontend/
  README.md
  .env.example
  package.json
  src/
    main.tsx
    App.tsx
    routes/
    components/
    features/
    services/
    types/
    utils/
```

## Main Routes

- `/`
- `/preview/:previewId`
- `/import`

## Frontend Component Diagram

```mermaid
flowchart TD
    App[React App] --> Routes[Routes]
    Routes --> Editor[Editor Route]
    Routes --> Preview[Preview Route]
    Routes --> Import[Import Route]

    Editor --> Canvas[React Flow Canvas]
    Editor --> Agent[Agent Panel]
    Editor --> Properties[Properties Panel]
    Editor --> Export[Export Controls]

    Canvas --> AdapterA[GraphPilot to React Flow Adapter]
    Canvas --> AdapterB[React Flow to GraphPilot Adapter]

    Agent --> APIClient[Local API Client]
    Preview --> APIClient
    APIClient --> Backend[Local HTTP API]
```

## React Flow Editor

React Flow is the live canvas layer used for:

- preview display
- node movement and resizing
- manual edge creation and deletion
- properties editing
- visual export from the browser

## GraphPilot JSON Adapters

The frontend maintains two local adapters:

- GraphPilot JSON -> React Flow state
- React Flow state -> GraphPilot JSON

These adapters keep live editing local for performance.

## Agent Panel

The agent panel is the UI surface for:

- generate requests
- edit requests
- convert requests
- clarification prompts returned by the backend

## Import and Export

Import and export responsibilities include:

- importing `.graphpilot.json`
- exporting `.graphpilot.json`
- exporting browser-rendered PNG and JPG
- exporting SVG if practical in the browser
- converting to Mermaid through backend `POST /api/convert`

## Preview Route

The preview route loads temporary diagrams by `previewId`.

## Preview Load Sequence

```mermaid
sequenceDiagram
    participant User as User
    participant UI as React UI
    participant API as Local API
    participant Cache as Preview Cache

    User->>UI: Open /preview/:previewId
    UI->>API: GET /api/previews/{previewId}
    API->>Cache: Load preview diagram
    Cache->>API: Diagram JSON
    API->>UI: Diagram JSON
    UI->>UI: Convert GraphPilot JSON to React Flow
    UI->>User: Render editable diagram
```

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
