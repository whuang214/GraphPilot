# Diagram Tools

This document owns every public GraphPilot MCP tool contract: diagnostics, discovery,
diagram creation from a draft, canonical validation, and rendering. Shared MCP boundaries
and the surface index live in [`README.md`](README.md). Implementation status belongs only
to the delivery board.

## Common rules

- `workspaceDir` is required for tools that create managed files.
- `diagramPath` is required for tools that operate on existing diagram files.
- Paths stay within the workspace resolved for the MCP call.
- Invalid input never overwrites existing JSON.
- Returned diagram and artifact paths may be absolute local paths for the local-first
  product; paths inside structured payloads are workspace-relative POSIX-style paths.
- Handled failures use `error: OperationProblem` with MCP `isError: true`, as defined by
  [`04-operation-errors.md`](04-operation-errors.md).
- Successful results use `isError: false`.

## Tool summary

| Tool | Purpose | Shared service | Writes files |
| --- | --- | --- | --- |
| `health` | Connectivity/health check | — | No |
| `echo` | Connectivity echo | — | No |
| `diagram_workflow` | Return host instructions; executes nothing | — | No |
| `diagram_list_types` | Return supported diagram types and their meanings | `DiagramTypeService` | No |
| `diagram_get_authoring_contract` | Return the draft authoring recipe for a type | `AuthoringContractService` | No |
| `diagram_check_draft` | Check a draft without creating anything | `DraftValidationService` | No |
| `diagram_create` | Materialize one draft into a new diagram | draft, materialization, layout, persistence, rendering | Canonical JSON + SVG |
| `diagram_read` | Project a saved diagram into an editable draft file | `DiagramEditService`, draft projection | The draft working file |
| `diagram_update` | Merge an edited draft back over the saved diagram | draft, materialization, merge, geometry, persistence | Canonical JSON + history |
| `diagram_validate` | Validate inline canonical diagram JSON | `DiagramValidationService` | No |
| `diagram_render` | Render SVG (inline/file) or save PNG | `DiagramRenderService` | Path mode only |

## Diagnostics

### `health`

`health` takes no arguments, writes nothing, and returns:

```json
{
  "status": "ok"
}
```

### `echo`

`echo` takes exactly one required string argument, `message`, writes nothing, and returns that string unchanged.

## `diagram_workflow`

### Purpose

Return the host instructions for authoring a draft and creating a diagram: the four steps,
the ownership boundary, what `authority` means, and the honesty rules.

Takes no arguments. **Instructions only** — reads no source, writes no file, executes
nothing, and calls no provider. It returns the same text every time.

It is the "call this first" path, so it states the two things a host most often gets
wrong: that `bdd_diagram` is a SysML Block Definition Diagram rather than
behaviour-driven development, and that relationship-end objects are never authored by
hand.

## `diagram_get_authoring_contract`

### Purpose

Return how to author a draft for **one** diagram type: every top-level field, the element
and relationship vocabulary, the direction each relationship runs, which ends it carries,
what may contain what, every rule that can refuse a draft, and a worked example.

### Inputs

| Field | Required | Rule |
| --- | --- | --- |
| `diagramType` | Yes | `activity_diagram`, `use_case_diagram`, or `bdd_diagram` |

### Behaviour

`structuredContent` has these 10 top-level keys, captured from the running server:

| Key | What it carries |
| --- | --- |
| `contractFor` | The diagram type this contract is for |
| `schemaVersion`, `kind` | The two constants every draft copies verbatim |
| `meaning` | What the type is, in one sentence — `bdd_diagram` is a Block Definition Diagram |
| `topLevelFields` | Every field a draft may carry at the top level, with required and array |
| `envelope` | Each authorable object and its fields, **filtered to this type** |
| `vocabulary` | The element and relationship types allowed, with the direction each runs |
| `guidance` | Sectioned prose: rules, idiom, and what to do when the source is unclear |
| `refusals` | Every meaning-stage rule that can refuse a draft, stated before it does |
| `example` | One complete draft `diagram_create` accepts exactly as written |

The envelope is filtered per type rather than shared: an activity contract no longer
describes BDD block compartments, which was 18% of what it sent.


Read-only. The contract is **derived** rather than written out: the vocabulary comes from
the type profile, the shape and example from `graphpilot.draft.v1`, and the relationship
rules from the same table the draft validator enforces. It therefore cannot advertise a
vocabulary that `diagram_create` then refuses.

**Scoped to the requested type.** An element field owned by another diagram type
(`stereotype`, `features`, `extensionPoints`) is neither documented nor accepted, and an
envelope section nothing can reach is not sent — an `activity_diagram` contract carries no
block compartments and no `multiplicity`, because no activity relationship has an end and
no activity element has properties. `TYPE_SCOPED_ELEMENT_FIELDS` is read by both the
validator and the contract, so the two cannot disagree.

`contractFor` names the type the response describes. It is deliberately not called
`diagramType`: at the top level beside `schemaVersion` and `kind`, which *are* draft
fields, a host read it as one and copied it into a draft.

`content` is a short orientation summary — around 1,100 characters. **The contract itself is `structuredContent`**, around 31,000. Rendering both was the most expensive shape the protocol allows, and `content` cannot simply be dropped because the specification marks it required while `structuredContent` is optional. The summary therefore states how many keys should have arrived and tells a host to stop and say so if it sees fewer: a client that does not surface `structuredContent` leaves a host holding orientation and nothing to author from, and the realistic failure is partial visibility rather than total. `structuredContent` carries
data, plus a worked example that is itself a valid draft. The example is currently in
`structuredContent` only.

## `diagram_check_draft`

### Purpose

Run a draft through the same validator `diagram_create` uses, and write nothing.

`diagram_validate` takes a **canonical** diagram, which a host never authors — so without
this the only way to test a draft was to attempt a real create. Every typo cost a write
attempt, and the diagram's name was spent whether or not the draft was any good.

It reports what it did and did not check. Evidence locators are resolved against the
workspace at create time, and the name is only known to be free when the file is written,
so a clean check is not a guarantee of a clean create — `structuredContent.notChecked`
says exactly that.

## `diagram_create`

### Purpose

Materialize one host-authored [draft](../../03-design/01-generation/01-draft.md) into a new
canonical diagram, then lay it out, validate it, persist it, and render its sibling SVG.

**No provider call.** The host supplies the semantics; GraphPilot supplies the notation.

### Arguments

| Field | Required | Rule |
| --- | --- | --- |
| `workspaceDir` | Yes | Absolute existing local directory. All reads and writes stay beneath it. |
| `draft` | Yes | Complete inline `graphpilot.draft.v1` document. Never a path: the caller submits it, and GraphPilot keeps its own copy as a trace (below). |

### Operation

1. Validate the draft: schema, unique IDs, endpoint resolution, evidence references,
   assurance pairing, and per-type notation legality.
2. Resolve each evidence locator, read the cited region, and record its content digest.
3. Materialize the draft into a logical graph, then a canonical diagram.
4. Lay out through PyGraphviz.
5. Validate the canonical document with `DiagramValidationService`.
6. Persist atomically through `DiagramPersistenceService`.
7. Write the accepted draft to `.graphpilot/drafts/<diagramName>.draft.json`.
8. Render the sibling SVG.

Steps 1–2 report caller mistakes. A failure at step 3 or later is a GraphPilot defect and
returns an operation error rather than persisting a malformed diagram.

`diagram_create` **refuses to overwrite** an existing
`.graphpilot/diagrams/<diagramName>.gp.json`. The file may carry edits the draft knows
nothing about, so replacing it is an update and starting over is an explicit delete.

### The draft trace

Step 7 keeps the draft that produced the diagram, at
`.graphpilot/drafts/<diagramName>.draft.json`.

The diagram carries evidence and per-element assurance and **never the host's prose** —
its uncertainties, its decisions, the reasoning behind an assumption. That is deliberate:
a reader of a diagram needs the citation, not the essay. But when a diagram turns out to
be wrong, the question is exactly *what did the host claim*, and without a trace the only
place that answer lived was an agent session that has ended.

So the trace is a debugging record, not an input. Nothing reads it back; `diagram_create`
never accepts a path. Writing it **cannot fail a create** — the diagram is the product, and
losing its trace is a worse log rather than a worse diagram, so `draftPath` comes back
`null` if the write failed. A **refused** draft leaves no trace at all, because no diagram
was produced for it to explain — the findings are returned to the caller and nothing is
written. There used to be an attempt log for counting them; it is gone, having produced a
usable measurement zero times across four corpus runs.

### Result contract

```json
{
  "outcome": "created",
  "diagramName": "todo-structure",
  "diagramPath": "C:/workspaces/todo-api/.graphpilot/diagrams/todo-structure.gp.json",
  "svgPath": "C:/workspaces/todo-api/.graphpilot/diagrams/todo-structure.svg",
  "draftPath": "C:/workspaces/todo-api/.graphpilot/drafts/todo-structure.draft.json",
  "editUrl": "http://localhost:5173/editor?diagramPath=C%3A%2Fworkspaces%2F...",
  "diagramType": "bdd_diagram",
  "nodeCount": 14,
  "edgeCount": 19,
  "assurance": {
    "authority": "as_implemented",
    "assumedElementIds": []
  },
  "operationWarnings": []
}
```

- `editUrl` is presented as a clickable **Open in the GraphPilot editor** link.
- Canonical JSON persisted with a failed SVG is still `created`: `svgPath` is null and
  `operationWarnings` carries `render_failed`. The host re-renders from the saved file
  rather than re-creating.

### Errors

| Code | Cause |
| --- | --- |
| `draft_invalid` | Schema, ID format, duplicate ID, or unresolved endpoint |
| `evidence_unreadable` | A locator path is missing, unsafe, or its line range runs past EOF |
| `assurance_unsupported` | `grounded` without evidence, or `assumed` without an assumption |
| `notation_invalid` | A relationship end the diagram type's notation forbids |
| `diagram_exists` | The target diagram is already present |
| `draft_too_large` | The draft exceeds the local size bound |

Every one is deterministic, free, and returned before anything is written. Exact shapes are
in [`04-operation-errors.md`](04-operation-errors.md).

## `diagram_list_types`

### Purpose

Return the concrete diagram types the generation tools accept.

### Inputs

None.

### Exact response

Captured from the running server.

```json
{
  "howToChoose": "Read `meaning` and `chooseWhen` on every entry before picking. The identifiers do not explain th…",
  "diagramTypes": [
    {
      "diagramType": "activity_diagram",
      "meaning": "UML Activity Diagram. Behavioural: ordered actions, decisions, and flow through one process.",
      "chooseWhen": "The request is about behaviour over time - what happens, in what order, where the flow branches or runs in parallel. Typical wording: 'what happens when someone...', 'the steps to...', 'how does X get handled'."
    },
    "…two more"
  ]
}
```

**There is no name-only view, deliberately.** The old shape was `diagramTypes: [str]`
beside a separate `diagramTypeMeanings` map, and a host could read three bare identifiers
and never open the explanations — which is how `bdd` was read as behaviour-driven
development twice, losing both runs. Every identifier now arrives welded to its `meaning`
and its `chooseWhen`, and `howToChoose` says what to do with them.

`chooseWhen` is the field that does the work: it describes the *request*, not the notation,
so it is the tiebreak when more than one type looks plausible. In four corpus runs every
host has chosen all three types correctly against it, unprompted.

## `diagram_validate`

### Purpose

Validate a complete inline canonical diagram without saving it.

### Inputs

| Field | Required | Rule |
| --- | --- | --- |
| `diagram` | Yes | Full inline canonical GraphPilot diagram JSON. |

Path validation belongs to file-backed flows that own workspace safety.

### Outputs and behavior

The tool returns the shared deterministic `ValidationResult`: `valid`, `level`, `summary`, `issues`, and optional
`stats`.

```json
{
  "valid": false,
  "level": "fail",
  "summary": "Diagram failed validation.",
  "issues": [
    {
      "severity": "error",
      "layer": "structure",
      "code": "missing_edge_target",
      "message": "Edge edge_2 references a missing target node.",
      "path": "$.edges[1].target",
      "details": {"edgeId": "edge_2"}
    }
  ],
  "stats": {"nodeCount": 4, "edgeCount": 3}
}
```

The tool validates canonical schema, graph/ownership integrity, advisory type-profile/structural checks, and basic
render readiness. It writes no files and calls no LLM. Missing/broken bundled schema returns
`validation_unavailable`; an invalid diagram remains a successful domain result with `isError: false`.

## `diagram_render`

### Purpose

Render canonical JSON to SVG (inline text or saved sibling) or save a PNG sibling. Rendering honors saved geometry and
never invokes generation, semantic review, PyGraphviz, or re-layout.

### Inputs

| Field | Required | Rule |
| --- | --- | --- |
| `diagram` | Exactly one of | Inline canonical JSON; supports SVG only and performs no filesystem access. |
| `diagramPath` | Exactly one of | Existing saved canonical JSON path; writes a sibling artifact. |
| `format` | No | `svg` (default) or `png`. |

### Exact result variants

| Mode | `structuredContent` |
| --- | --- |
| Inline `diagram` + SVG | `{ "svg": "<svg ...>...</svg>" }` |
| Path `diagramPath` + SVG | `{ "svgPath": "C:/.../<name>.svg" }` |
| Path `diagramPath` + PNG | `{ "pngPath": "C:/.../<name>.png" }` |

PNG is rasterized from the same SVG renderer through `resvg`; no inline image is returned.

Errors are `invalid_arguments`, workspace/path failures, `diagram_not_found`, `invalid_diagram_json`, and
`render_failed` as detailed in [`05-operation-errors.md`](04-operation-errors.md).

## `diagram_update` — planned, not implemented

Planned with [editing](../../03-design/05-edit/README.md), alongside
`diagram_get_semantic_view`. The host reads the current diagram back in draft shape and
submits desired semantic state; GraphPilot diffs it, preserves positions and user edits,
and validates before overwriting.

Browser save already crosses the same `DiagramPersistenceService` write boundary.
