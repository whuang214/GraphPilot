# Validation

## Purpose

GraphPilot needs validation for two reasons:

- **Product/runtime safety**: make sure outputs are valid and safe to return to Cursor/MCP or the React UI.
- **Development evaluation**: measure whether GraphPilot produces good results on repeatable prompt and answer-key test cases.

GraphPilot is a database-free, MCP-first local tool. The backend owns MCP tools, local API, GraphPilot Core, blueprints, Azure OpenAI calls, validation, conversion, preview cache, and backend config. The frontend owns React Flow editing, preview, import/export, and browser visual export.

GraphPilot JSON is the source of truth. Image and PDF rendering validation is deferred. OCR validation is not part of this document.

## Validation overview

GraphPilot uses two validation tracks:

1. **Runtime validation service**
2. **Eval framework**

Runtime validation asks: **"Is this output safe, valid, and usable?"**

Eval framework asks: **"How good is GraphPilot on known test cases?"**

Runtime validation is product safety validation used during generate, edit, and convert. The eval framework is development-time quality measurement using prompts, answer keys, rubrics, and reports.

## Runtime validation service

The runtime validator is used by:

- `graphpilot_generate`
- `graphpilot_edit`
- `graphpilot_convert`
- `POST /api/generate`
- `POST /api/edit`
- `POST /api/convert`

Runtime validation must run before GraphPilot returns generated, edited, or converted results. It should be deterministic. AI output can vary, but validation of a given output should always be stable.

### Layer 0: Request validation

Validate tool and API inputs before doing work.

Checks include:

- `prompt` exists
- `prompt` is not empty
- `blueprintKey` exists if provided
- `diagram` exists for edit and convert
- source and target conversion formats are supported
- conversion mode is valid
- `outputPath` is only used where allowed

### Layer 1: Blueprint selection validation

Ensure GraphPilot has a valid blueprint.

Behavior:

- If `blueprintKey` is provided, load and validate it.
- If `blueprintKey` is missing, route using the classifier.
- If confidence is `>= 0.80`, use the recommended blueprint.
- If confidence is `< 0.80`, return `needs_clarification`.
- `generic_diagram` must exist as a fallback.

Checks include:

- blueprint exists
- blueprint JSON parses
- required blueprint fields exist
- `nodeTypes` and `edgeTypes` exist
- routing metadata exists

### Layer 2: Raw AI output validation

Validate Azure OpenAI output before treating it as a diagram or patch.

Checks include:

- response exists
- response is not empty
- JSON can be extracted if JSON is expected
- Markdown fences can be stripped
- JSON can be parsed
- parsed value is the expected object or array type

### Layer 3: GraphPilot schema validation

Validate `graphpilot.diagram.v1` with Pydantic.

Top-level checks include:

- `schemaVersion`
- `kind`
- `diagramType`
- `id`
- `name`
- `metadata`
- `canvas`
- `nodes`
- `edges`
- `groups`

Node checks include:

- `id`
- `type`
- `label`
- `position`
- `data`
- `style`

Edge checks include:

- `id`
- `type`
- `source`
- `target`
- `label`
- `data`
- `style`

### Layer 4: Structural graph validation

Check internal graph consistency.

Required checks:

- diagram has at least one node
- node IDs are unique
- edge IDs are unique
- group IDs are unique
- every edge source exists
- every edge target exists
- group `nodeIds` point to existing nodes
- node labels are not empty
- positions are finite numbers

Warnings:

- diagram has no edges
- disconnected nodes
- very long labels
- high node and edge count
- overlapping positions

### Layer 5: Blueprint rule validation

Ensure the diagram follows the selected blueprint.

Checks include:

- `diagramType` matches `blueprint.diagramType`
- `metadata.blueprintKey` matches `blueprint.key`
- node types are allowed
- edge types are allowed
- node and edge counts are within limits
- required node types are present if configured
- required node or edge data fields are present if configured

Examples:

- **ERD**: entity and table nodes should have fields or columns.
- **Sequence diagram**: message edges should have order or sequence metadata.
- **Flowchart**: decision nodes should have meaningful outgoing branches.
- **UML class diagram**: class nodes should have attributes and or methods.
- **UML use case diagram**: actors and use cases should exist.
- **System architecture**: apps, services, databases, users, queues, external systems, and integrations should use allowed types.

### Layer 6: Feature-specific validation

#### Generate

- generated diagram validates
- selected blueprint is recorded in metadata
- source is recorded as `mcp` or `ui`
- preview cache entry can be created
- usage object is available when a model was called

#### Edit

- current diagram validates
- patch operations validate if patch mode is used
- patch applies cleanly
- resulting diagram validates
- unrelated correct content is preserved where practical

#### Convert

- source input validates
- target format is supported
- converted output validates enough for the target
- for Mermaid, output is not empty and starts with the expected diagram keyword

### Layer 7: Repair validation

- At most one repair attempt.
- Repair only when the issue is repairable.
- Validate again after repair.
- Track attempted and successful.

Good deterministic repairs include:

- strip Markdown fences
- extract JSON
- fill missing canvas defaults
- fill missing metadata defaults
- fill missing `data` and `style` objects
- normalize `groups` to `[]`

LLM repair can be used for malformed JSON or schema-close output. Do not repair vague prompts, ambiguous routing, or conceptually wrong diagrams.

### Layer 8: Response envelope validation

Ensure all MCP tools and local API routes return the shared envelope:

```json
{
  "status": "success | needs_clarification | error",
  "data": {},
  "clarification": {},
  "error": {},
  "usage": {},
  "validation": {}
}
```

### Generate runtime flow

1. Validate generate request.
2. Select or route blueprint.
3. If routing is unclear, return `needs_clarification`.
4. Build prompt.
5. Call Azure OpenAI.
6. Validate raw AI output.
7. Parse GraphPilot JSON.
8. Validate schema.
9. Validate structure.
10. Validate blueprint rules.
11. Repair once if needed and allowed.
12. Validate repaired diagram.
13. Create preview cache entry.
14. Return shared response envelope.

### Edit runtime flow

1. Validate edit request.
2. Validate current diagram.
3. Build edit prompt with current diagram context.
4. Call Azure OpenAI.
5. Validate raw AI output.
6. If patch mode, validate patch operations and apply patch to a copy.
7. If full diagram mode, validate returned diagram.
8. Validate resulting diagram.
9. Repair once if needed and allowed.
10. Return shared response envelope.

### Convert runtime flow

1. Validate convert request.
2. Validate source diagram if the source is GraphPilot JSON.
3. Run deterministic, LLM, or hybrid conversion.
4. Validate converted output.
5. Repair once if needed and allowed.
6. Return shared response envelope.

## Runtime pass/fail policy

- Return success when schema, structure, and blueprint validation pass.
- Return success with warnings when only warning or info issues exist.
- Return error when JSON cannot be parsed or repaired, schema validation fails, structural errors remain, or blueprint rules are violated.
- Use one repair attempt only.
- Do not use answer-key checks in runtime validation.

## Validation result format

```json
{
  "valid": true,
  "level": "pass",
  "summary": "Diagram passed validation.",
  "issues": [],
  "stats": {
    "nodeCount": 5,
    "edgeCount": 4,
    "groupCount": 0
  },
  "repair": {
    "attempted": false,
    "successful": false
  }
}
```

Issue shape:

```json
{
  "severity": "error",
  "code": "missing_edge_target",
  "message": "Edge edge_2 targets missing node node_database.",
  "path": "$.edges[1].target",
  "details": {
    "edgeId": "edge_2",
    "target": "node_database"
  }
}
```

Severity levels:

- `error`: blocks success
- `warning`: can return but should be surfaced and logged
- `info`: informational only

Validation levels:

- `pass`
- `pass_with_warnings`
- `fail`

## Eval framework

The eval framework is development-time validation for quality measurement. It is not used to block normal user requests. It may call Azure OpenAI, so it can be non-deterministic. However, its scoring and comparison logic should be deterministic.

It should reuse runtime validation, then add answer-key scoring.

Eval framework layers:

- Eval case loading
- Eval case schema validation
- Execution
- Runtime validation reuse
- Answer-key comparison
- Feature-specific scoring
- Metrics collection
- Report generation
- Regression comparison
- Optional LLM judge later

### Eval folder structure

```text
backend/tests/evals/
  generate/
    use_case_diagram/
    class_diagram/
    erd/
    sequence_diagram/
    flowchart/
    system_architecture/
    generic_diagram/
  routing/
    cases.jsonl
  edit/
  convert/
    mermaid/
  runners/
    run_generate_evals.py
    run_routing_evals.py
    run_edit_evals.py
    run_convert_evals.py
    run_all_evals.py
  reports/
```

Deterministic tests live separately:

```text
backend/tests/unit/
backend/tests/integration/
backend/tests/fixtures/
```

### Generate eval cases

Each generate eval case should have:

- `prompt.txt`
- `answer_key.json`
- `rubric.json`

Suggested folder pattern:

```text
backend/tests/evals/generate/{blueprint_key}/{case_name}/
```

Example answer key:

```json
{
  "expectedBlueprintKey": "system_architecture",
  "requiredNodes": [
    {
      "label": "User",
      "type": "user",
      "aliases": ["users", "operator", "employee"]
    },
    {
      "label": "Frontend",
      "type": "application",
      "aliases": ["React app", "UI", "web app"]
    },
    {
      "label": "API",
      "type": "service",
      "aliases": ["backend", "FastAPI backend"]
    },
    {
      "label": "Database",
      "type": "database",
      "aliases": ["SQL Server", "DB"]
    }
  ],
  "requiredEdges": [
    {
      "source": "User",
      "target": "Frontend",
      "type": "uses",
      "aliases": ["accesses", "opens"]
    },
    {
      "source": "Frontend",
      "target": "API",
      "type": "http",
      "aliases": ["calls", "requests"]
    },
    {
      "source": "API",
      "target": "Database",
      "type": "data_flow",
      "aliases": ["reads/writes", "queries"]
    }
  ],
  "forbiddenNodes": []
}
```

Example rubric:

```json
{
  "passThreshold": 80,
  "scoring": {
    "validJson": 10,
    "schemaValid": 10,
    "structuralValid": 15,
    "blueprintValid": 15,
    "expectedBlueprint": 10,
    "requiredNodesPresent": 25,
    "requiredEdgesPresent": 15
  }
}
```

### Flexible answer-key matching

- Do not use exact JSON equality.
- Do not require exact IDs, positions, style, or ordering.
- Match nodes by normalized label, aliases, and type.
- Match edges by source label or alias, target label or alias, and optional type.
- Normalize labels by lowercasing, trimming whitespace, and collapsing repeated spaces.

### Routing evals

Routing evals should use:

```text
backend/tests/evals/routing/cases.jsonl
```

Example:

```json
{
  "caseId": "login_sequence",
  "prompt": "Show the login flow between user, frontend, API, and identity provider.",
  "expectedBlueprintKey": "sequence_diagram",
  "acceptableBlueprintKeys": ["sequence_diagram", "flowchart"],
  "shouldClarify": false
}
```

Ambiguous example:

```json
{
  "caseId": "ambiguous_login",
  "prompt": "Make a diagram for login.",
  "expectedBlueprintKey": null,
  "acceptableBlueprintKeys": ["sequence_diagram", "flowchart", "generic_diagram"],
  "shouldClarify": true
}
```

### Edit evals

Each edit eval case should have:

- `input_diagram.graphpilot.json`
- `edit_prompt.txt`
- `answer_key.json`
- `rubric.json`

Edit evals should measure:

- current diagram validates
- patch validates
- resulting diagram validates
- requested change was applied
- important existing nodes and edges were preserved

### Convert evals

For MVP, focus on GraphPilot JSON to Mermaid Markdown.

Convert evals should measure:

- source diagram validates
- output is not empty
- Mermaid starts with the expected type
- required labels appear
- required relationships appear
- no obvious syntax issues

### Metrics collected

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

### Report outputs

- `backend/tests/evals/reports/latest.json`
- `backend/tests/evals/reports/latest.md`
- `backend/tests/evals/reports/history.jsonl`

## Deterministic vs non-deterministic tests

- Unit tests should be deterministic and should not call Azure OpenAI.
- Integration tests should mostly be deterministic and should mock Azure OpenAI.
- Runtime validation should be deterministic.
- Eval runs may be non-deterministic if they call Azure OpenAI.
- Eval scoring and answer-key comparison should remain deterministic.

Suggested structure:

```text
backend/tests/unit/
backend/tests/integration/
backend/tests/fixtures/
backend/tests/evals/
```

## Recommended implementation order

1. `ValidationIssue` and `ValidationResult` schemas
2. `GraphPilotDiagram` Pydantic schema
3. `validate_diagram()`
4. Structural validator
5. Blueprint validator
6. `validate_raw_ai_output()`
7. Generate runtime validation integration
8. Edit runtime validation integration
9. Convert runtime validation integration
10. Basic repair once
11. Generate eval runner
12. Routing eval runner
13. Edit eval runner
14. Convert eval runner
15. Optional LLM judge later

## Future work

- larger eval set
- edit and convert eval expansion
- optional LLM judge
- regression reporting
- future model and prompt comparison in a separate experimentation document