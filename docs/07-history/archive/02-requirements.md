# Requirements

## Purpose

This document defines the functional and non-functional requirements for GraphPilot.

The requirements here are derived from the current user-facing use cases in `docs/01-use-cases.md` and are scoped to the MVP architecture.

## Requirement Sources

- `docs/01-use-cases.md`
- MCP-first, local-file-based MVP architecture assumptions
- shared GraphPilot Core behavior used by both the IDE / MCP Client path and the UI / React App path

## Use Case Traceability

| Use case | Requirement section |
| --- | --- |
| UC-01 Generate diagram from prompt | FR-01 Shared generation requirements |
| UC-02 Edit diagram using prompt | FR-02 Shared edit requirements |
| UC-03 Preview diagram in chat | FR-03 IDE preview requirements |
| UC-04 Open diagram in UI | FR-04 IDE open-in-UI requirements |
| UC-05 Convert diagram to Markdown | FR-05 IDE markdown conversion requirements |
| UC-06 Export diagram to file | FR-06 UI export requirements |
| UC-07 Manually edit diagram in UI | FR-07 UI manual editing requirements |
| UC-08 Import diagram | FR-08 UI import requirements |

## Functional Requirements

### FR-01 Shared generation requirements

GraphPilot must:

1. accept natural-language diagram-generation prompts from the **IDE / MCP Client** and the **UI / React App**
2. generate GraphPilot JSON as the canonical diagram output
3. use the requested `blueprintKey` when one is explicitly provided
4. run blueprint routing when `blueprintKey` is missing
5. support generation outcomes for:
   - Class Diagram
   - ERD
   - UML Use Case Diagram
   - Sequence Diagram
   - Generic Diagram fallback
6. return clarification instead of generating immediately when routing confidence is not high
7. restrict clarification options to only:
   1. Use recommended
   2. Use Generic Diagram
   3. I will clarify my prompt
8. avoid showing a giant list of all supported blueprints during clarification
9. validate generated diagrams before returning them
10. return diagram data and, when available, preview information appropriate to the calling channel

### FR-02 Shared edit requirements

GraphPilot must:

1. accept edit-by-prompt requests from the **IDE / MCP Client** and the **UI / React App**
2. use the current GraphPilot JSON diagram as edit context
3. support returning patch operations or updated GraphPilot JSON
4. validate edited results before returning them
5. support UI-driven review of proposed changes so the user can accept or reject them

### FR-03 IDE preview requirements

For the **IDE / MCP Client** path, GraphPilot must:

1. return a preview summary for a generated or edited diagram
2. return a preview URL when preview output is available
3. support the preview flow without requiring the user to switch immediately to the UI

### FR-04 IDE open-in-UI requirements

For the **IDE / MCP Client** path, GraphPilot must:

1. return a link that opens the current diagram in the React UI
2. allow the UI to load the linked diagram for viewing or continued editing

### FR-05 IDE markdown conversion requirements

For the **IDE / MCP Client** path, GraphPilot must:

1. support conversion of a diagram or source content into Markdown-friendly output
2. support Mermaid / flowchart markdown as the primary Markdown conversion target
3. return output suitable for pasting into an `.md` file

### FR-06 UI export requirements

For the **UI / React App** path, GraphPilot must:

1. allow the user to export the current diagram to:
   - JSON
   - PNG
   - JPG
   - SVG
2. preserve the current diagram state when exporting

### FR-07 UI manual editing requirements

For the **UI / React App** path, GraphPilot must support direct visual editing actions, including:

1. move nodes
2. add nodes
3. delete nodes
4. connect nodes
5. edit labels and properties

### FR-08 UI import requirements

For the **UI / React App** path, GraphPilot must:

1. allow the user to import an existing `.graphpilot.json` file
2. render the imported diagram for continued editing
3. support continued manual editing after import

## Non-Functional Requirements

### NFR-01 Security boundary

- the frontend must never receive Azure OpenAI keys or equivalent backend-only secrets

### NFR-02 Validation and correctness

- the backend must validate generated and edited GraphPilot JSON before returning results
- conversion output should be structurally valid for its target format when returned to the caller

### NFR-03 Local-first MVP operation

- GraphPilot must operate without a database in the MVP
- local files and temporary local preview cache are the primary persistence mechanisms for MVP workflows

### NFR-04 Deployability

- frontend and backend must remain separately deployable

### NFR-05 Preview cache lifecycle

- preview cache entries must be temporary and should be cleaned up after they are no longer needed

### NFR-06 Export fidelity

- browser-based visual export should match what the user sees in the UI as closely as practical

### NFR-07 Cross-entry-point consistency

- IDE / MCP Client and UI / React App flows must use the same GraphPilot Core behavior for shared generation and edit logic

## Constraints

- GraphPilot is MCP-first
- GraphPilot is local-file-based
- GraphPilot is database-free for MVP
- GraphPilot has no users/auth for MVP
- GraphPilot JSON is the semantic source of truth for diagrams
- browser-based visual export is the MVP export path for PNG, JPG, and SVG where practical
- backend conversion is the MVP path for Mermaid / flowchart markdown output

## Assumptions

- Azure OpenAI is available to the backend runtime
- blueprints are stored locally under `backend/blueprints/`
- preview cache is temporary and local
- React Flow is the visual editing layer
- the IDE / MCP Client can handle clarification loops and returned preview/open links

## Out of Scope

- database persistence
- users and auth
- collaboration
- full draw.io or Lucidchart parity
- backend image or PDF rendering for MVP
