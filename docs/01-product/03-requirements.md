# Requirements

These requirements define GraphPilot's final intended product behavior across the unified generation workflow, both
authority modes, and the shared browser/IDE refinement loop. Runtime availability and delivery progress live only on
the [current-state board](../05-delivery/01-current-state.md).

## Core product acceptance criteria

The product satisfies its core design when all of the following are true:

1. A host can learn the whole authoring surface from three read-only calls —
   `diagram_workflow`, `diagram_list_types`, `diagram_get_authoring_contract` — and the
   contract is derived from the draft schema and type profile, never written beside them.
2. Every rule that can refuse a draft is stated in the contract **before** a host trips it.
3. `diagram_check_draft` reports exactly what `diagram_create` would refuse, writes
   nothing, and can be called any number of times.
4. `diagram_create` accepts one inline `graphpilot.draft.v1` document. There is no request
   file, no path argument, and no second generation surface.
5. **No model is called anywhere in the product.** The same draft always produces the same
   diagram.
6. `authority: as_implemented` requires evidence; `authority: conceptual` forbids it. Both
   directions are enforced.
7. Every cited region is read at create time, checked to contain the symbol it names, and
   digested. A citation that points at the wrong lines is refused, not saved.
8. An element the source does not establish is `assumed`, carries the assumption's
   statement, reason and acceptor inside the saved diagram, and is marked in the editor.
9. A refusal writes nothing at all, including the diagram name.
10. Nothing overwrites a saved diagram, which may carry browser edits the draft cannot know
    about.
11. Canonical persistence defines success. A later render failure leaves the diagram saved,
    returns `svgPath: null`, and adds `render_failed` to `operationWarnings`.
12. The accepted draft is kept beside the diagram as a trace. Nothing reads it back.
13. A user can open canonical JSON in the browser, refine it, validate it, and save it back
    without losing `origin`, evidence, or assurance.
14. Invalid JSON — authored, browser-edited, or hand-edited — never replaces a valid
    canonical diagram.
15. A user or host can render the latest canonical JSON to SVG and optionally PNG without
    re-layout.
16. Every path stays inside the selected local workspace, and no product database is
    required.

## User requirements

| ID | Requirement | Scenario |
| --- | --- | --- |
| UR-1 | The user needs one entry point that teaches the whole authoring surface. | US-01, US-02 |
| UR-2 | The user needs a diagram of current repository behaviour whose claims can be checked line by line. | US-01 |
| UR-3 | The user needs an editable conceptual diagram that visibly claims nothing about the code. | US-02 |
| UR-4 | The user needs to see which elements the source establishes and which somebody inferred. | US-01 |
| UR-5 | The user needs to be told what the host was unsure about, assumed, and decided. | US-01, US-02 |
| UR-6 | The user needs a refusal to explain the rule it is enforcing, not merely that something failed. | US-01, US-02 |
| UR-7 | The user needs to open any saved diagram in a visual editor. | US-01 through US-04 |
| UR-8 | The user needs to move, resize, relabel, recolour, connect and reconnect elements by hand. | US-03 |
| UR-9 | The user needs manual changes to validate and save without corrupting the prior file. | US-03 |
| UR-10 | The user needs SVG and optional PNG artifacts from the latest canonical diagram. | US-04 |
| UR-11 | The user needs to know when a diagram came out hard to read. | US-01, US-02 |

## Functional requirements

### FR-1 Local operating model and canonical artifacts

The system shall:

- run as a local-first, database-free product with no authentication requirement for the local product loop;
- expose IDE workflows through MCP and browser workflows through the Django API, with both entry points using shared
  backend services;
- persist every editable diagram as canonical `graphpilot.diagram.v1` JSON rather than raw React Flow JSON;
- treat canonical `.gp.json` as authoritative and SVG/PNG as derived artifacts;
- keep all managed paths within the caller's resolved workspace and reject traversal or link escape;
- use validated atomic replacement for authoritative evidence, request, and diagram writes; and
- use this managed layout for newly created artifacts:

```text
<workspace>/.graphpilot/
  diagrams/
    <diagramName>.gp.json
    <diagramName>.svg
    <diagramName>.png              # optional derived artifact
  drafts/
    <diagramName>.draft.json       # the accepted draft, for debugging
  attempts.jsonl                   # one line per diagram_create attempt
```

`.graphpilot/` shall remain outside repository-source fingerprinting so GraphPilot's own artifacts do not make JSON 1
stale. Unsupported old artifacts shall never be silently migrated, rewritten, or deleted.

### FR-2 Diagram type and schema discovery

The MCP surface shall:

- expose supported generation types through `diagram_list_types`;
- expose the per-type authoring contract through `diagram_get_authoring_contract`. The
  canonical schema is deliberately **not** offered to an author: it describes the saved
  document, which a host must never write, and the tool that used to return it was
  reported as a trap by every host that met it; and
- generate `activity_diagram`, `use_case_diagram`, and `bdd_diagram`.

The canonical schema owner defines save/validate-only compatibility vocabulary beyond those generated profiles.

### FR-3 Workflow and authoring contract

The system shall:

- expose `diagram_workflow` as instructions only — it reads nothing, writes nothing, and
  calls no model;
- expose `diagram_get_authoring_contract` per diagram type, **derived** from the draft
  schema, the type profile and the end-policy tables, so the contract cannot drift from
  the validator;
- state in that contract every rule that can refuse a draft, before a host trips one; and
- include a worked example per type that the validator accepts.

### FR-4 The draft is the only input

The system shall:

- accept one inline `graphpilot.draft.v1` document at `diagram_create`;
- provide `diagram_check_draft`, which applies exactly the same rules, writes nothing, and
  may be called any number of times; and
- **not** accept a path, a saved request, or any second generation surface.

### FR-5 Authority and assurance

The system shall:

- require evidence when `authority` is `as_implemented`, and forbid it when
  `conceptual`;
- require `evidenceRefs` on a `grounded` element and an `assumptionRef` on an `assumed`
  one, and permit `conceptual` only inside a conceptual diagram, where it is mandatory;
- refuse rather than downgrade a draft that cannot meet the authority it declares; and
- carry each `assumed` element's assumption — statement, reason and acceptor — inside the
  saved diagram, so a reader without the draft can still see what was assumed.

### FR-6 Evidence is checked, not trusted

The system shall, at create time:

- resolve every cited path inside the workspace, rejecting anything outside it;
- read each cited line range, rejecting an empty file, a reversed range, or one past the
  end of the file;
- verify that a cited `symbol` appears within the lines given, so a citation cannot name
  one thing and point at another;
- record a content digest per region; and
- require every evidence entry to be cited by some element or relationship.

### FR-7 Deterministic materialization

The system shall:

- derive every notational detail — markers, dashing, relationship ends, route mode,
  containment, `origin` — from the semantic type, never from the host;
- **call no model at any point**, so the same draft always produces the same diagram; and
- treat a failure after draft validation as a GraphPilot defect, reported as an operation
  error rather than persisted.

### FR-8 Layout and legibility

The system shall:

- use pinned PyGraphviz as the sole layout engine, with no fallback algorithm;
- measure the rendered SVG for text that is clipped, buried under a foreign element, or
  overlapping other text; and
- report that measurement to the author as a warning, never as a refusal — how many
  elements belong in one picture is the author's call.

### FR-9 Results and failure

The system shall:

- write nothing when a draft is refused, including leaving the diagram name free;
- refuse to overwrite an existing diagram, which may carry edits the draft cannot know
  about;
- treat canonical persistence as success — a later render failure returns the saved
  diagram with `svgPath: null` and `render_failed` in `operationWarnings`; and
- report a refusal with the code of the rule broken, and `draft_invalid` only when the
  document does not match the schema at all.

### FR-10 The draft trace

The system shall write the accepted draft to
`.graphpilot/drafts/<diagramName>.draft.json` beside the diagram it produced, so that when
a diagram turns out to be wrong there is a record of what was actually claimed. Nothing
reads it back.

### FR-11 What the diagram carries

The saved diagram shall carry generic metadata, `authority`, inline evidence with digests,
the assumptions its assumed elements rest on, and each element's `origin`. It shall **not**
carry the host's uncertainties, decisions, or narrative reasoning — delivering those to the
user is the host's responsibility, restated in the workflow.

### FR-12 Storage boundaries

The system shall keep every path inside the selected workspace under `.graphpilot/`,
require no database, and write nothing else into the repository being diagrammed.

### FR-13 Deterministic diagram validation and persistence

The system shall:

- expose inline canonical validation through `diagram_validate`;
- validate generated diagrams before create and browser/IDE replacements before overwrite;
- keep canonical validation deterministic, and separate from draft validation: the first checks a document GraphPilot built, the second checks one a host wrote;
- reject unsafe paths, malformed/schema-invalid data, broken graph references, and unrenderable input at the boundary
  that owns each check;
- save only when blocking validation succeeds;
- leave the existing file unchanged when validation or persistence fails;
- return structured issues with stable codes, paths, and useful messages; and
- reuse the shared validated-persistence service rather than implement entry-point-specific write rules.

Advisory vocabulary/structural warnings may remain visible without blocking ordinary browser or IDE saves;
generation applies its stricter acceptance gate before creating output.

### FR-14 Browser editing and save

The browser product shall:

- open a workspace diagram from `editUrl`, recent/browse selection, or another supported workspace flow;
- open a local GraphPilot file through the supported browser file-picker flow;
- adapt canonical GraphPilot JSON to canvas state and back without replacing it with raw React Flow JSON;
- allow moving, resizing, relabeling, recoloring, connecting, and reconnecting elements;
- use Django API routes, not MCP, for workspace load, save, validation, preview, and export;
- validate a complete canonical document before replacing a workspace file;
- leave the existing file unchanged and surface useful element-level issues when save validation fails;
- return and adopt the normalized canonical document after a successful workspace save;
- refresh the sibling SVG on a best-effort basis after a successful workspace save;
- preserve valid optional request ownership and context origin fields through adapters; and
- export SVG or optional PNG through the shared SVG rendering path.

The browser shall not author drafts, evidence, or assurance. It preserves each element’s origin on round-trip and marks an assumed element on the canvas, so a reader can see which parts of a diagram the source establishes.

### FR-15 Editing a saved diagram — **not implemented**

There is no MCP editing tool. A host that wants to change a saved diagram authors a new
draft under a new name; a person edits in the browser. `diagram_create` refuses an existing
name rather than merging, because the file may carry edits the draft cannot know about.

`diagram_update` is designed in [`05-edit/`](../03-design/05-edit/README.md) and **is not built**.
Nothing in this section is callable today.

### FR-16 Rendering and export

The system shall:

- expose `diagram_render` for inline or path-backed rendering;
- accept exactly one of inline canonical `diagram` or existing `diagramPath`;
- return SVG text for inline SVG mode;
- save a sibling SVG for path-backed SVG mode;
- optionally save a sibling PNG, rasterized from the same SVG, for path-backed PNG mode;
- render deterministically without a network call, LLM call, or re-layout;
- honor canonical positions, sizes, styles, semantic types, and relationship markers;
- use the same backend SVG renderer for IDE artifacts and browser preview/export;
- reject malformed or unrenderable input with a stage-appropriate error; and
- avoid a separate export tool. `diagram_export` does not exist and is a deliberate non-goal, because `diagram_render` already writes the artifact.

SVG is the required static format. PNG is an optional derivative. PDF is deferred.

### FR-17 Reviewing generation quality

There is no runtime evaluator, no observer event stream, and no scoring path. Quality is
reviewed by looking at the diagrams:

- `manage.py review_gallery --regen eval` rebuilds all 48 examples from their stored drafts
  and serves one page. Each card carries its own badges — valid, structural, legible,
  miscited, and whether this run could rebuild it — so the page names the diagram to open
  rather than reporting a total.
- The generated pool comes from cold agents diagramming three real applications through
  the MCP server against nine frozen prompts, three per repository. Freezing the count is
  what makes attempts-per-diagram comparable between runs.
- Nothing in that path influences a runtime decision. It is development apparatus, and it
  lives outside any workspace.

## Quality and safety requirements

| ID | Requirement |
| --- | --- |
| NFR-1 | Every workspace-backed path shall be contained beneath the explicit workspace after symlink/junction-safe resolution. |
| NFR-2 | Authoritative writes shall be validated, bounded, canonicalized, and atomic; conflicts shall write nothing. |
| NFR-3 | Tools and services shall return bounded structured results and safe typed errors without secrets, raw stack traces, raw source, or hidden reasoning. |
| NFR-4 | A `retryable` operation problem shall mean a later call may succeed only after its reported condition changes; it shall never authorize unchanged automatic retry. |
| NFR-5 | No model shall be called anywhere in the product, so the whole suite is offline by construction rather than by discipline. |
| NFR-6 | The same draft shall always produce the same diagram, byte for byte. |
| NFR-7 | Every rule that can refuse a draft shall be stated in the authoring contract before a host trips it, and a test shall read those rules out of the services so one cannot be added without being explained. |
| NFR-8 | A refusal shall state the rule it enforces, not only that something failed — a length limit gives the limit, and a required shape names its keys. |
| NFR-9 | Canonical diagram JSON shall remain free of prompts, complete packets, rubrics, scores, model usage, diagnostics, and evaluator data. |
| NFR-10 | PyGraphviz native calls shall be process-locally serialized, resource-safe, deterministic within the supported contract, and have no alternate-engine fallback. |
| NFR-11 | Review apparatus — the gallery, the corpus, the drafts they are built from — shall live outside any workspace and influence no runtime decision. |
| NFR-12 | What a diagram claims shall be visible in the saved file and on the canvas: authority on the diagram, assurance on every element, and a mark on anything assumed. |
| NFR-13 | Training examples and evaluator gold shall have separate authoring/approval paths; gold shall never enter prompts or evaluated workspaces. |
| NFR-14 | Unsupported old workflow/tool/schema/path contracts shall have no aliases, dual writes, or silent migration. |

## Scenario traceability

| Scenario | Requirements |
| --- | --- |
| US-01 Conceptual direct generation | UR-1, UR-2, UR-5, UR-6; FR-2 through FR-5, FR-10 through FR-13 |
| US-02 Repository-grounded generation | UR-1, UR-3 through UR-6; FR-3, FR-4, FR-6 through FR-13 |
| US-03 Browser refinement | UR-6 through UR-9; FR-1, FR-13, FR-14 |
| US-04 IDE update | UR-6, UR-8, UR-9; FR-13, FR-15 |
| US-05 Render and export | UR-10; FR-1, FR-16 |
| US-06 Offline generation evaluation | UR-11; FR-10 through FR-12, FR-17 |

## Optional and deferred scope

### Optional within the core product

- PNG export derived from SVG.
- Compact generation trace sidecars.
- Numbered local generation diagnostics.
- Explicit environment-only standard-quality ablation; it is not a production fallback.

### Deferred

- PDF export.
- Inline image presentation guarantees across MCP hosts.
- In-browser agent or chat, and provenance inspection beyond the assumed badge on the canvas.
- Structured patch operations.
- Public per-request quality mode or best-of-N candidate selection.
- Example retrieval/RAG through a public search tool.
- Provenance-aware post-generation request editing/regeneration.
- Native Windows ARM64 PyGraphviz runtime rather than supported x64 emulation.
- Authentication, multi-user coordination, and product database persistence.

## Active contract and feature owners

- [System design](../02-architecture/02-system-design.md)
- [Backend architecture and `OperationProblem`](../02-architecture/03-backend.md)
- [MCP surface and host workflow](../02-architecture/01-mcp-tools/README.md)
- [Browser API](../02-architecture/05-api-routes.md)
- [Canonical diagram schema](../03-design/02-diagram-schemas/01-diagram-json-schema.md)
- [Generation design](../03-design/01-generation/README.md)
- [The draft contract](../03-design/01-generation/01-draft.md)
- [Validation design](../03-design/03-validation/README.md)
- [Rendering design](../03-design/04-rendering.md)
- [Browser editor design](../03-design/06-editor-ui.md)
