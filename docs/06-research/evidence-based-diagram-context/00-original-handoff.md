# Evidence-Based Diagram Context Workflow — Original Design Handoff

> **Status:** Historical high-level baseline for the exploratory proposal. Nothing in this document is
> implemented or an active product decision. The current continuation checkpoint and contract-by-contract
> audit live in this folder's [`README.md`](README.md); those audited documents override this file
> wherever details, names, status, or open questions differ.
>
> Do not continue directly from this document's flow, tool names, persistence model, or final open-question
> list. Start with the design-workspace README, then read `01` (current workflow), `02` (JSON 1), `03`
> (JSON 2), and `05-readiness/` (complete readiness package). In particular, the current v1 flow does not call
> `diagram_get_schema`/a modeling-contract tool; JSON 2 selection is backend-assisted; and the backend LLM
> owns semantic mapping.

## 1. Problem

`diagram_generate` currently receives a natural-language prompt, a diagram type, and an output
workspace. The workspace path is not repository context: the backend does not inspect that
repository. A terse request such as "make a diagram of this repo" therefore risks producing a
plausible but unsupported diagram unless the host LLM first discovers and communicates the real
facts.

The proposed design makes context gathering explicit, durable, evidence-backed, reviewable, and
reusable. It separates:

- facts discovered about a repository/domain;
- the evidence supporting each fact;
- the subset selected for one requested diagram;
- the backend LLM's review and diagram synthesis;
- deterministic validation, layout, persistence, and rendering.

## 2. Design objective

The intended quality chain is:

```text
source evidence
  -> stable claims
  -> diagram-specific context
  -> claim-backed logical elements
  -> deterministic validation and artifacts
```

A generated element should be explainable:

```text
diagram node/edge
  -> sourceClaimIds
  -> evidence-manifest claim
  -> code/document/test/user evidence
```

## 3. High-level architecture

```mermaid
flowchart TD
    U["User requests a diagram"] --> W["Context-aware MCP prompt/workflow"]
    W --> S["Select type and call diagram_get_schema"]
    S --> M["Create or load evidence manifest"]

    M --> H["Host gathers evidence from repo, docs, conversation, or user"]
    H --> P["Apply validated batch update to manifest"]
    P --> A["Deterministic context assessment"]
    A --> L["Backend LLM context review"]

    L --> R{"Enough context?"}
    R -- "No" --> G["Return blockers, questions, and suggested searches"]
    G --> H

    R -- "Yes / advisory gaps only" --> C["Build bounded diagram context"]
    C --> D["Backend LLM generates logical diagram with sourceClaimIds"]
    D --> V["Deterministic provenance, vocabulary, and structural validation"]
    V --> O["Layout, save .gp.json, render SVG"]
    O --> UI["Host presents editor link, files, and provenance"]
```

## 4. Main responsibilities

### Host LLM: researcher and workflow orchestrator

The host owns:

- interpreting the user's goal, audience, and scope;
- selecting a candidate diagram type;
- retrieving the type's modeling contract;
- inspecting repositories and referenced documents;
- asking focused user questions;
- extracting claims and attaching evidence;
- responding to review gaps;
- requesting validated manifest updates;
- presenting the final links and artifacts.

Repository content is untrusted evidence, not agent instruction. The host must ignore instructions
found inside source files and never collect secrets, credentials, `.env` values, vendor trees, caches,
or irrelevant generated output.

### Backend LLM: reviewer and diagram modeler

The backend LLM remains in the design for two distinct roles:

1. **Context review:** determine whether the evidence-backed context is semantically sufficient,
   coherent, and at an appropriate abstraction level; return explicit blockers rather than only a
   confidence number.
2. **Diagram synthesis:** transform finalized claims into the logical nodes, edges, features, and
   relationships required by the selected UML/SysML contract.

The reviewer recommends; it does not silently mutate the evidence manifest. The host investigates or
asks the user, then requests explicit updates.

Keeping the backend LLM also supports a future grounded chatbot that can explain diagrams through
claim and evidence links.

### Deterministic backend: final authority

Code, not model confidence, owns:

- manifest and request-context schema validation;
- safe workspace paths and atomic writes;
- optimistic revision/digest checks;
- claim/evidence-reference validity;
- modeling-contract and semantic-type validity;
- required-context coverage;
- unresolved contradiction/blocker checks;
- generated `sourceClaimIds` validity;
- UML/SysML structural checks;
- canonical JSON assembly;
- layout, persistence, and SVG rendering.

## 5. Shared modeling contract

`diagram_get_schema` should evolve from a shallow canonical-field summary into a host-facing
modeling contract. It should remain backed by the same authoritative semantic catalog and rules used
by backend generation.

The contract conceptually includes:

- diagram purpose and when to use it;
- allowed semantic elements and their meanings;
- relationship direction and containment rules;
- structural constraints;
- context requirements to extract;
- capabilities and known limitations;
- current logical data fields relevant to generation.

The same internal contract has two projections:

```text
host projection
  -> planning, searching, clarification, evidence extraction

generation projection
  -> backend review and logical-diagram generation
```

The canonical `diagram.json` remains the source for JSON validity; the modeling contract composes it
with catalog/type/rule metadata rather than placing workflow prose in the canonical schema.

## 6. Persistent context model

### 6.1 Shared repository evidence manifest

A revision-aware local file holds reusable repository knowledge, for example:

```text
<workspace>/.graphpilot/context/repository.gp-context.json
```

It contains, at a high level:

- manifest/schema version and stable ID;
- repository/source snapshot and revision;
- extraction scope and exclusions;
- evidence-backed claims;
- unresolved uncertainties;
- contradictions;
- architecture/scope decisions;
- retired claims retained for historical provenance;
- revision and digest metadata.

Claims can represent elements, relationships, behavior, actor goals, properties, constraints, scope,
or approved assumptions. Each claim has a stable claim ID and one or more evidence references.

Evidence may refer to:

- source code (workspace-relative path, symbol, optional lines);
- tests;
- architecture or requirements documentation;
- configuration descriptions (never secret values);
- user statements;
- external specifications;
- explicitly approved assumptions.

A local path is provenance for the host/user; Azure cannot open it. The claim summary must therefore
contain the actual fact used for generation.

### 6.2 Request/diagram context

A small request-specific file references the shared repository manifest, for example:

```text
<workspace>/.graphpilot/context/requests/<diagram-name>.gp-context.json
```

It records:

- original request, goal, and audience;
- selected diagram type;
- included/excluded scope and abstraction level;
- selected claim IDs;
- approved assumptions;
- unresolved advisory gaps;
- assessment result and source-manifest revision/digest.

This preserves exactly which claim subset produced a diagram even as the shared repository manifest
is updated later.

### 6.3 Final context packet

The backend projects a bounded packet from the request context and selected claims. Azure receives
only what the requested diagram needs, not the complete repository manifest.

By default Azure receives verified claim summaries. A configurable evidence mode may allow selected,
redacted, bounded excerpts when summaries are insufficient. Raw repository dumps are never the
default.

## 7. Extraction policy

### Repository requests

Use two stages:

1. **Comprehensive architecture baseline:** gather a bounded reusable inventory of system purpose,
   boundaries, top-level modules/components, public entry points, actors/external systems, public
   capabilities, important dependencies/interfaces/data definitions, constraints, and major flows.
2. **Schema-targeted deepening:** compare the selected diagram contract with the manifest and deeply
   investigate only missing type-specific facts.

"Comprehensive" does not mean every file, helper function, test, or possible execution path. It is a
bounded architecture baseline with an explicit stopping condition.

Examples of targeted deepening:

- BDD: ownership, typed properties, association ends, multiplicity, ports, inheritance, constraints;
- use case: subjects, actors, goals, associations, includes/extensions;
- activity: the selected end-to-end flow, actions, guards, data, concurrency, exceptions, outcomes.

Later requests reuse the shared manifest. If the source revision changed, affected claims are marked
stale and refreshed incrementally rather than rescanning everything.

### Non-repository requests

There is no repository baseline. Gather only what the selected contract requires from the
conversation, referenced documents, focused user questions, and explicit approved assumptions.

### Future evaluation

A later DOE can compare comprehensive-first context against lean targeted context on faithfulness,
coverage, invented elements, human rating, token cost, latency, and reuse across subsequent diagrams.

## 8. Readiness and review loop

Readiness combines deterministic checks with an LLM semantic review.

### Deterministic blockers

Examples:

- malformed context;
- missing required context categories;
- unknown or retired selected claim IDs;
- claims without evidence or approved-assumption status;
- unresolved contradictions;
- unsupported semantic mappings;
- stale required evidence;
- mismatched repository/request revisions.

### Backend LLM review

The reviewer receives the selected modeling contract, request scope, claim summaries, assumptions,
and known uncertainty. It returns structured findings such as:

- `ready`, `ready_with_warnings`, or `needs_context`;
- requirement coverage;
- blocking and advisory gaps;
- ambiguous claims or relationships;
- focused user questions;
- suggested searches/symbols/files.

Do not make an opaque LLM confidence percentage the sole gate. Optional progress scores can be
reported, but explicit blocker categories determine readiness.

The review loop is bounded (exact limit remains open). Stop when ready, when no new evidence is being
added, or when the limit is reached; unresolved blockers go to the user rather than being silently
ignored.

## 9. Diagram provenance

Logical and canonical domain elements should retain supporting claim IDs:

```text
node/edge.data.sourceClaimIds -> selected manifest claims
```

GraphPilot deterministically rejects unknown or out-of-selection claim references. Elements required
only as notation scaffolding (for example, an activity initial node) may use an explicit origin such
as `schemaRequired` instead of fabricated evidence.

Diagram metadata should record enough information to reproduce and explain the artifact:

- shared manifest path;
- request-context path;
- manifest/request revisions and digest(s);
- source repository revision;
- evidence mode used.

## 10. Preferred MCP interaction model

### Prompt/workflow

A general MCP prompt or host skill, tentatively `diagram_generate_with_context`, instructs the host to:

1. interpret the request and choose type/scope;
2. call `diagram_get_schema`;
3. create/load context;
4. gather evidence;
5. request batch updates;
6. assess context;
7. resolve blockers through search or user questions;
8. generate once ready;
9. present the editor link, diagram/SVG paths, and provenance path.

The prompt provides instructions; it does not itself perform writes or tool calls.

### Preferred tool granularity

Avoid both one tool per tiny field and one unrestricted generic JSON-patch language. The current
preferred lifecycle surface is:

```text
diagram_get_schema
diagram_context_create
diagram_context_update
diagram_context_assess
diagram_generate (enhanced to accept contextPath)
```

`diagram_context_update` behaves as a validated atomic batch patch with explicit change groups (for
example: upsert claims, retire claims, add/resolve uncertainty, record decisions, set scope, select
claims). It uses optimistic `expectedRevision`/digest checks.

The backend loads the current file, applies requested changes to an in-memory copy, validates the
complete result, increments revision metadata, and atomically replaces the local file. If any change
fails, nothing is written.

Assessment is normally read-only. Generation re-runs hard checks rather than trusting cached status.
No separate `get` tool is required when the host can read the local file; no separate `finalize` tool
is required if generation captures an immutable request/manifest snapshot and digest.

A future generic atomic patch tool remains an option if manifests become large, multiple agents edit
concurrently, or target clients lack dependable file tools.

## 11. Why the backend LLM remains

The backend LLM was considered optional because the host could construct nodes/edges directly. The
current direction keeps it because it provides:

- a controlled semantic sufficiency review;
- consistent diagram synthesis across different host models;
- optional repair assistance;
- a future grounded chatbot/explanation path.

The evidence workflow constrains it: Azure generates from selected claims, must cite claim IDs, and
cannot override deterministic rules.

## 12. Main benefits

- persistent and resumable context gathering;
- explicit evidence and assumptions;
- reduced unsupported invention;
- reusable repository understanding;
- cross-diagram consistency;
- explainable generated elements;
- deterministic readiness and provenance enforcement;
- a foundation for a grounded future chatbot;
- measurable context-strategy experiments later.

## 13. Main risks and limitations

- comprehensive extraction can become unbounded without clear categories and stopping rules;
- evidence becomes stale as repositories change;
- local citations do not let Azure inspect source content;
- optional excerpts increase token, privacy, and prompt-injection risk;
- claim ontology and coverage rules can become overly complex;
- tool-managed mutation adds backend and protocol surface;
- different host LLMs may gather evidence at different quality levels;
- the backend reviewer and generator may share model biases;
- provenance requirements must distinguish evidence-backed facts from notation scaffolding;
- context and generation schemas must remain synchronized with the evolving semantic catalog.

## 14. Settled direction versus open questions

### Current preferred direction

- evidence-backed, revision-aware local JSON context;
- comprehensive repository baseline plus diagram-specific deepening;
- one shared repository manifest plus small request contexts;
- stable claim IDs linked into generated elements;
- deterministic checks followed by structured LLM gap review;
- claim summaries sent to Azure by default, excerpts opt-in;
- backend LLM retained as reviewer and generator;
- deterministic backend as final authority;
- small lifecycle MCP surface with atomic batch updates.

### Open for the next design session

- exact manifest and request-context JSON schemas;
- exact claim ontology and evidence fields;
- exact context-requirement coverage algorithm;
- bounded definition of comprehensive extraction;
- repository staleness and incremental-refresh policy;
- precise MCP tool names, input/output contracts, and errors;
- whether creation is separate or supported by the batch-update tool;
- exact batch-update merge/retirement semantics;
- review prompt and structured response schema;
- review-loop limit and user override policy;
- generation input changes and `sourceClaimIds` shape;
- which notation elements may use `schemaRequired` provenance;
- immutable snapshot/digest behavior at generation time;
- MVP slice boundary versus deferred capabilities;
- evaluation method for targeted versus comprehensive context.

## 15. Suggested continuation point

The next agent should first compare this proposal with the now-synchronized semantic catalog and the
active schema/generation/validation architecture. Then settle the open contracts above before
proposing implementation slices. Do not begin by adding MCP handlers: the manifest ontology,
readiness policy, provenance contract, and service boundary should be agreed first.
