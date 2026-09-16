# 8-Week Plan

## Week 0: Architecture and design confirmation

Goal:
Confirm the project direction and lock the MVP scope.

Deliverables:
- Project architecture confirmed
- Database-free MVP direction confirmed
- MCP-first workflow confirmed
- Backend and frontend responsibility split confirmed
- GraphPilot JSON format confirmed
- Blueprint format confirmed
- Validation approach confirmed
- Eval framework approach confirmed
- React Flow mapping approach confirmed
- Active docs organized under `docs/`
- No users, auth, or database in MVP confirmed

Exit criteria:
- Team agrees on architecture
- MVP scope is clear
- Main docs are good enough to start implementation
- Initial diagram types are selected:
  - `use_case_diagram`
  - `class_diagram`
  - `erd`
  - `sequence_diagram`
  - `flowchart`
  - `system_architecture`
  - `generic_diagram`

## Week 1: Project skeleton, schemas, and foundation

Goal:
Create the monorepo structure and core type and schema foundation.

Deliverables:
- `backend/` structure created
- `frontend/` structure created
- `docs/` structure cleaned up
- `backend/.env.example` created
- `frontend/.env.example` created
- Basic FastAPI or Starlette app created
- Basic MCP server skeleton created
- Basic React, Vite, and TypeScript app created
- React Flow installed and rendering a placeholder canvas
- GraphPilot diagram Pydantic models created
- Blueprint Pydantic models created
- Tool input and output schemas created
- Validation result schemas created
- TypeScript diagram and blueprint types created
- Initial GraphPilot-to-React Flow adapter stubs created
- Initial React Flow-to-GraphPilot adapter stubs created

Exit criteria:
- Backend starts locally
- Frontend starts locally
- Health check or simple backend route works
- React Flow canvas renders
- Core schemas compile
- No database code or database configuration exists

## Week 2: Backend generate path and runtime validation

Goal:
Build the backend core for the generate workflow and runtime validation.

Deliverables:
- `blueprint_service.py`
- `blueprint_router.py`
- `prompt_builder.py`
- `generation_service.py`
- `validation_service.py`
- `preview_service.py`
- `cost_service.py` if practical
- Azure OpenAI client wrapper
- Initial `blueprint.json` files for selected diagram types
- `generic_diagram` fallback blueprint
- `GET /api/blueprints`
- `POST /api/generate`
- `GET /api/previews/{previewId}`
- `graphpilot_generate` MCP tool
- Shared response envelope implemented
- Runtime validation layers implemented for generate:
  - request validation
  - blueprint selection validation
  - raw AI output validation
  - GraphPilot schema validation
  - structural graph validation
  - blueprint rule validation
  - response envelope validation
- Basic deterministic repair:
  - strip Markdown fences
  - extract JSON
  - fill safe defaults where practical
  - one repair attempt if practical

Exit criteria:
- `POST /api/generate` can return valid GraphPilot JSON
- `graphpilot_generate` can return valid GraphPilot JSON
- Invalid generated output fails with a useful validation result
- Preview cache can store and fetch generated diagrams
- At least one blueprint can generate a valid diagram end to end from backend only

Stretch goals:
- Basic LLM blueprint routing
- Clarification response when routing confidence is below threshold
- Usage and cost tracking

## Week 3: Frontend preview and editor path

Goal:
Build the frontend path to open, render, edit lightly, and export generated diagrams.

Deliverables:
- Preview route
- Editor route
- GraphPilot-to-React Flow adapter
- React Flow-to-GraphPilot adapter
- Basic custom or default node rendering
- Basic edge rendering
- Preview API client
- Diagram editor Zustand store
- Import `.graphpilot.json`
- Export `.graphpilot.json` in browser
- Open preview URL from backend
- Manual node movement
- Basic label editing
- Basic toolbar and layout shell
- Graceful error handling for missing or expired previews

Exit criteria:
- User can open a generated preview URL in the UI
- React Flow renders GraphPilot nodes and edges
- User can move nodes
- User can edit basic labels
- User can export a `.graphpilot.json` file
- Frontend does not require Azure OpenAI keys

Stretch goals:
- Basic visual styling by node type
- PNG or JPG export if simple
- SVG export if practical

## Week 4: First end-to-end MVP demo and basic validation testing

Goal:
Prove the first complete product loop works from MCP to UI.

Demo loop:
Cursor or MCP client -> `graphpilot_generate` -> backend core -> Azure OpenAI -> runtime validation -> preview cache -> preview URL -> React UI -> export JSON

Deliverables:
- First working end-to-end demo
- Runtime validation refined based on real generated outputs
- `backend/tests/unit/` created
- `backend/tests/integration/` created
- `backend/tests/fixtures/` created
- `backend/tests/evals/` created
- Unit tests for validation service
- Unit tests for blueprint service
- Basic integration tests with mocked AI
- Basic generate eval cases
- Basic routing eval cases
- README instructions updated for local demo

Exit criteria:
- At least one diagram can be generated from MCP and opened in React UI
- Runtime validation catches broken diagrams
- Preview URL works
- Generated diagram can be exported from frontend as `.graphpilot.json`
- Basic unit tests pass
- Basic eval runner can score generate cases or is scaffolded with sample cases

## Week 5: Eval framework and blueprint improvement

Goal:
Improve AI quality using repeatable evals and blueprint refinement.

Deliverables:
- Generate eval runner
- Routing eval runner
- Flexible answer-key matching
- Rubric scoring
- `latest.json` report
- `latest.md` report
- `history.jsonl` report
- 2 to 3 generate eval cases per blueprint
- 8 to 10 routing eval cases
- Metrics captured:
  - `caseId`
  - `feature`
  - `blueprintKey`
  - `expectedBlueprintKey`
  - `actualBlueprintKey`
  - `modelKey`
  - `status`
  - `score`
  - `passed`
  - `validJson`
  - `schemaValid`
  - `structuralValid`
  - `blueprintValid`
  - `repairAttempted`
  - `repairSuccessful`
  - `promptTokens`
  - `completionTokens`
  - `totalTokens`
  - `estimatedCost`
  - `latencyMs`
  - `issues`
- Blueprint prompts improved based on eval results
- Router prompt improved based on routing evals

Exit criteria:
- Generate evals can be run by blueprint or all together
- Routing evals can be run
- Eval reports identify failures and weak blueprints
- Cost, latency, and token usage are visible
- Blueprint changes can be measured against eval results

Stretch goals:
- Expand to 3 to 5 generate cases per blueprint
- Simple regression comparison against prior eval report

## Week 6: AI edit workflow

Goal:
Add safe AI-assisted editing for existing diagrams.

Deliverables:
- `edit_service.py`
- `POST /api/edit`
- `graphpilot_edit` MCP tool
- Edit request and response schemas
- Patch operation schemas
- Patch validation
- Patch application logic
- Resulting diagram validation
- Agent panel in frontend
- UI flow to request an edit
- UI flow to preview and accept or reject AI changes
- Basic edit eval cases

Recommended patch operations:
- `add_node`
- `update_node`
- `remove_node`
- `add_edge`
- `update_edge`
- `remove_edge`
- `add_group`
- `update_group`
- `remove_group`

Exit criteria:
- User can ask AI to edit the current diagram
- Backend returns valid patch operations or a valid updated diagram
- Backend validates the resulting diagram
- Frontend lets user accept or reject changes
- Existing correct content is preserved where practical

Stretch goals:
- Preservation scoring in edit evals
- Better visual diff for proposed changes

## Week 7: Convert, export, and polish

Goal:
Add semantic conversion and improve export support.

Deliverables:
- `conversion_service.py`
- `POST /api/convert`
- `graphpilot_convert` MCP tool
- GraphPilot JSON to Mermaid Markdown conversion
- Mermaid output validation checks
- Convert eval cases
- Frontend export improvements
- PNG or JPG export from browser if not already done
- SVG export if practical
- Conversion documentation

Mermaid mapping:
- `erd` -> `erDiagram`
- `flowchart` -> `flowchart`
- `sequence_diagram` -> `sequenceDiagram`
- `class_diagram` -> `classDiagram`
- `system_architecture` -> `flowchart`
- `generic_diagram` -> `flowchart`
- `use_case_diagram` -> `flowchart` for MVP

Exit criteria:
- User can convert GraphPilot JSON to Mermaid Markdown
- Converted Mermaid includes expected labels and relationships
- Convert route and MCP tool use the shared response envelope
- Frontend can export JSON and at least one visual format
- Convert evals can identify missing labels or relationships

Stretch goals:
- Hybrid Mermaid conversion with LLM polish
- One repair attempt for invalid Mermaid
- Better styling and layout controls in UI

## Week 8: Hardening, documentation, and demo prep

Goal:
Make the MVP reliable enough to demo and hand off.

Deliverables:
- Bug fixes
- Error handling polish
- Response envelope consistency verified
- MCP tool behavior verified
- API route behavior verified
- Preview cache cleanup verified
- Clarification flow verified
- Expired preview handling verified
- Frontend invalid diagram handling improved
- README setup instructions finalized
- `backend/.env.example` finalized
- `frontend/.env.example` finalized
- Security and privacy documentation updated
- Known limitations documented
- Backlog and risks updated
- Demo script created
- Sample prompts prepared
- Sample exported diagrams prepared

Exit criteria:
- Repeatable demo works
- New developer can follow setup docs
- Azure OpenAI keys remain backend-only
- No database references remain in MVP docs or config
- Known gaps are documented
- MVP scope is clear
- Team is ready for demo or review

## MVP checkpoint

The Week 4 MVP checkpoint is intentionally narrow:

- Generate only
- Runtime validation
- Preview URL
- React Flow rendering
- Manual position and label editing
- Export `.graphpilot.json`

Do not require these by Week 4:

- AI edit
- Mermaid conversion
- full visual export support
- full eval coverage
- perfect blueprint quality
- backend image or PDF rendering

## Implementation strategy

Use a vertical-slice approach:

1. Build one complete generate-to-preview-to-export path.
2. Add repeatable evals to improve quality.
3. Add AI edit.
4. Add conversion and visual export polish.
5. Harden for demo.
