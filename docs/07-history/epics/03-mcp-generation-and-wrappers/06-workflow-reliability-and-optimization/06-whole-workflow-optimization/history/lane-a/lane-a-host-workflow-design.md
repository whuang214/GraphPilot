# Lane A Host Workflow Design

## Status and Boundary

This document records the user-approved Block 6 Lane A direction for making an agent host faster and more reliable when it routes a diagram request, searches a repository, authors repository evidence and a diagram request, corrects deterministic failures, and invokes GraphPilot. The primary host is **Devin CLI**; the earlier GitHub Copilot targeting and its C/W/I benchmark cells are retired by [`lane-a-02-devin-host-transition.md`](lane-a-02-devin-host-transition.md).

The governing principle is that **the host authors meaning and GraphPilot owns mechanics**: if the backend can derive a value, the host is never asked for it.

The design is approved, and the user authorized execution through the dependency-ordered [`lane-a-00-group.md`](lane-a-00-group.md) plan. Each slice retains its plan/audit/commit gates; no approval implicitly authorizes Azure calls, provider identities, live integration, promotion, or certification beyond the exact later gate. Live status remains only in [`../../../00-current-state.md`](../../../../../../../05-delivery/01-current-state.md).

Lane A owns GraphPilot-controlled host and integration preparation. Lane B continues to own provider/runtime optimization, including semantic-review and generation endpoint waves. The lanes do not share one measurement wave or modify each other's evidence, provider identities, or exclusive files.

## Goal

Reduce user-request-to-valid-request wall time, repository search/read work, JSON authoring attempts, and deterministic validation failures while preserving repository authority, readiness, reviewed generation quality, recovery, security, and no-rerun behavior.

The first scope is deliberately narrow:

- primary host: Devin CLI;
- repository: the Todo API fixture;
- diagram type: `bdd_diagram`;
- one cold, one warm, and one integration observation per baseline/candidate condition;
- provider-free host preparation through the saved request;
- separately authorized integration only after provider-free proof and Lane B resource release.

Generalized hosts, repeated matrices, Order/Library repositories, persistent MCP, promotion, and certification remain outside this Lane A wave.

## Dependencies

- The committed Block 5 handoff supplies the controlled live anchor, provider-free audit baseline, external cold Todo observation, and ranked host opportunity.
- The Block 6 owner and current slice group preserve causal separation, retain/revert gates, no-rerun rules, and shared integration ownership.
- The A02 baseline established that cold authoring is impossible against the current interface; A03 removes that blocker and its retest scopes the contract work. Retired Copilot profiles remain read-only historical evidence.
- Canonical MCP, JSON 1, JSON 2, generation/provenance, canonical diagram, and workflow-audit owners must promote the approved contracts before production implementation consumes them.
- Provider-free contract and integration proof precede every live gate. Each provider-backed integration requires a separate exact user authorization and exclusive release of Lane B provider resources.
- The repository block-execution policy governs slice DAGs, worktree/resource isolation, integration ownership, and mandatory human stops.

## Evidence and Root

The current cold Todo profile is diagnostic evidence, not a strict baseline. It recorded 470,824 ms total wall, five searches, ten focused reads, five authoring attempts, five deterministic failures, and no source-byte telemetry. The final readiness call took 64,799.3406 ms and blocked because source-backed composition, ownership, and TodoItem relationships were not encoded explicitly.

The partial warm profile showed zero broad searches, four targeted reads, 7,391 source bytes, one JSON 1 replacement attempt, and zero validation failures through H06, but it stopped before canonical evidence save and is not baseline eligible. Neither identity may be reused.

The static host-workflow audit found two related GraphPilot-controlled causes:

1. one dense prose workflow mixes routing, both branches, artifact rules, recovery, and reporting;
2. host authoring exposes canonical bookkeeping and large schemas instead of a compact selected semantic contract.

The approved direction addresses those causes before adding broad benchmark infrastructure.

## Approved Host Architecture

```text
User request
  -> diagram_generation_workflow
  -> host selects one authority mode and diagram type
  -> diagram_generation_get_authoring_contract(mode, type)
  -> host follows only that selected recipe
  -> evidence status and optional current-snapshot replacement
  -> durable request save
  -> one generation attempt
  -> diagram/editor or actionable terminal result
```

### Stage 1: Structured Route Map

`diagram_generation_workflow` remains the call-first public name but becomes one model-callable tool rather than a dual prompt/tool surface. It returns one small structured host workflow plan and only minimal MCP text presentation.

The plan owns:

- preserving the original request;
- choosing exactly one `direct|context` authority mode;
- choosing one generatable diagram type;
- the next authoring-contract lookup and required arguments;
- high-level direct/context tool order;
- no context-to-direct fallback;
- no unsupported facts;
- no unchanged rerun;
- timeout as an unknown outcome.

The plan does not contain JSON examples, detailed evidence/request contracts, type-specific completeness checks, digest/version plumbing, or full error tables.

The replacement begins under a new V1 namespace rather than reusing the old prompt identity:

```text
graphpilot.generation.host-workflow-plan.v1
```

The old workflow prompt is removed from active runtime. Historical records retain their recorded identities; there is no compatibility mode, opt-in switch, duplicate public workflow, or second Markdown authority.

### Stage 2: Selected Authoring Contract

The new read-only tool is:

```text
diagram_generation_get_authoring_contract
```

Its required input is exactly:

```text
generationMode: direct | context
diagramType: activity_diagram | use_case_diagram | bdd_diagram
```

It receives no workspace, request, provider, trace, debug, or version-selection input. It inspects no source, writes no file, and calls no provider.

The tool returns only the selected mode/type recipe:

- ordered host steps;
- the host-authored request/evidence shape;
- compact complete validated examples;
- current/missing/stale behavior for context mode;
- fixed managed paths and backend-issued references;
- the selected type's conditional completeness checklist;
- one-attempt, recovery, and reporting rules.

Direct and context outputs retain separate strict identities behind the one tool:

```text
graphpilot.direct.generation-authoring-contract.v1
graphpilot.context.generation-authoring-contract.v1
```

`diagram_get_schema` remains the owner of final canonical diagram schema summaries and is not extended into host workflow authorship.

## Contract Ownership

| Proposed contract | Canonical owner at promotion |
| --- | --- |
| `graphpilot.generation.host-workflow-plan.v1` | MCP public-surface and host-workflow owners: [`README.md`](../../../../../../../02-architecture/01-mcp-tools/README.md) and [`03-context-workflow.md`](../../../../../../../02-architecture/01-mcp-tools/03-context-workflow.md) |
| `graphpilot.direct.generation-authoring-contract.v1` | MCP public-surface/host-workflow owners, with direct request meaning retained by [`04-generation-design.md`](../../../../../../../03-design/07-generation.md) |
| `graphpilot.context.generation-authoring-contract.v1` | MCP public-surface/host-workflow owners, derived from the [`08-context-backed-generation`](../../../../../../../03-design/01-context-generation/README.md) package without duplicating its semantic contracts |
| `graphpilot.context.evidence-snapshot-candidate.v1` and `graphpilot.context.evidence-snapshot.v1` | JSON 1 owner: [`02-evidence-manifest.md`](../../../../../../../03-design/01-context-generation/03-evidence-manifest.md) |
| `graphpilot.context.snapshot-diagram-request.v1` | JSON 2 owner: [`03-diagram-request-context.md`](../../../../../../../03-design/01-context-generation/04-diagram-request-context.md) |
| Canonical generation receipt and generation-time origins | [`00-diagram-json-schema.md`](../../../../../../../03-design/03-diagram-json-schema.md) and [`05-generation-and-provenance.md`](../../../../../../../03-design/01-context-generation/05-generation-and-provenance.md) |
| Host-benchmark manifest/event/result companions | Workflow-audit owner: [`09-workflow-audit-design.md`](../../../../../../../03-design/11-workflow-audit.md) |

This delivery document owns sequencing, boundaries, and approval state only. The listed canonical owners define the final contract fields and behavior before implementation; links replace duplicated authority.

## Repository Evidence Snapshot

JSON 1 becomes one replaceable current repository snapshot rather than an append-only evidence and claim history.

```text
repository unchanged -> reuse canonical JSON 1
repository changed   -> rebuild the complete bounded snapshot and replace it atomically
```

### Responsibility Split

The host authors semantic content:

- source display identity and bounded scope;
- evidence locators and concise summaries;
- current supported claims and relationships;
- current unresolved uncertainties.

GraphPilot owns deterministic mechanics:

- safe-scope fingerprinting and freshness;
- source-change and concurrent-write protection;
- path, ID, reference, shape, and bounds validation;
- backend-managed capture/version metadata;
- canonicalization and atomic replacement;
- exact saved reference construction;
- successful draft cleanup.

GraphPilot never invents a source fact, relationship, assumption, or final topology.

### Candidate and Canonical Shapes

The temporary host draft uses a compact semantic candidate contract. It omits source hashes, per-evidence digests, captured-source digests, timestamps, revision, lifecycle status, and claim-version history.

The canonical snapshot contains the same semantic content plus GraphPilot-managed source identity, file count, capture time, and opaque version token. All evidence and claims in one snapshot are current by definition. Claim references use claim IDs rather than `{id, version}` pairs because the saved request binds one exact snapshot.

The intended identities are:

```text
graphpilot.context.evidence-snapshot-candidate.v1
graphpilot.context.evidence-snapshot.v1
```

### Draft Lifecycle

The normal draft path is one direct child under `.graphpilot/context/drafts/`. On successful canonical promotion GraphPilot:

1. commits the canonical snapshot;
2. deletes only the submitted draft;
3. removes the drafts directory only when empty.

Failed validation, freshness, conflict, or write leaves the draft for correction. Other drafts are never deleted. Cleanup failure does not undo the canonical save or authorize repetition; it returns a nonfatal warning.

## Backend-Issued Version References

GraphPilot retains internal source, evidence, request, output, trace, and evaluation digests where they enforce freshness, concurrency, ownership, recovery, or evidence integrity. The host does not calculate or route digest fields.

Instead:

```text
status missing|stale -> returns one save precondition
host passes the precondition unchanged to evidence save
evidence save         -> returns one evidence reference
host copies the evidence reference unchanged into JSON 2
request save          -> returns one request reference
host uses the request reference for generation/recovery
```

The references may use canonical hashes internally but are opaque host version handles. Removing these backend checks is not part of the design.

Per-evidence `contentDigest` is removed from the host snapshot contract because the current backend does not verify or consume it and the complete source fingerprint already forces a full refresh. Historical `capturedInSourceDigest`, claim versions, and evidence lifecycle status disappear with the current-only snapshot model.

## Durable Diagram Request

JSON 2 remains a durable saved request. It records:

- immutable request/output identity;
- exact evidence snapshot reference;
- original request and normalized goal;
- diagram type, audience, and detail;
- included/excluded scope;
- selected current claim IDs;
- relevant uncertainty dispositions;
- accepted assumptions and presentation decisions.

The context request uses a new snapshot-oriented identity rather than reusing the old versioned-claim contract:

```text
graphpilot.context.snapshot-diagram-request.v1
```

The request path derives from validated `diagramName`; the host does not supply a competing filename. Request save remains provider-free, returns one complete request reference, supports validated replacement before generation, and finalizes on successful owned generation.

Keeping JSON 2 preserves reviewable user intent, a provider-free host benchmark terminal, exact output ownership, and finalized-output timeout recovery.

## Direct and Context Flows

### Direct

```text
route as direct
-> get selected direct/type authoring contract
-> author and save one direct request
-> call diagram_generate_direct once
-> report generated|blocked|error
```

Direct mode performs no source inspection, JSON 1 work, readiness call, or context origin handling.

### Context: Current Evidence

```text
route as context
-> get selected context/type authoring contract
-> evidence status = current
-> read canonical JSON 1 once
-> perform no source search/read and no JSON 1 rewrite
-> author/save a new durable JSON 2
-> call diagram_generate_from_context once
```

Reading canonical `.graphpilot` JSON 1 is an artifact read, not a source read.

### Context: Missing Evidence

```text
evidence status = missing + save precondition
-> bounded source search and decisive reads
-> author semantic JSON 1 draft
-> run selected type checklist
-> promote canonical snapshot
-> copy returned evidence reference into JSON 2
-> save JSON 2
-> generate once
```

### Context: Stale Evidence

```text
evidence status = stale + canonical scope + save precondition
-> complete same-scope regather
-> atomically replace current JSON 1 snapshot
-> rebuild any unfinalized JSON 2 against the new evidence reference
-> generate once
```

GraphPilot never silently rebinds an old request to new evidence.

## Conditional BDD Checklist

The context/BDD authoring contract helps the host verify, without pre-building GraphPilot topology:

- each requested in-scope definition has a claim;
- every requested or directly supported relationship is explicit;
- relationship source/target claims exist;
- composition and ownership are covered when applicable;
- interface-to-implementation relationships are explicit when supported;
- requested dependency paths connect across scope;
- domain storage/use relationships are explicit when requested or needed for the requested structure;
- requested properties, interfaces, multiplicities, and constraints are covered only when supported;
- unsupported facets and relationships are not invented;
- internal connector networks are not invented as BDD edges;
- the host does not author final semantic types, node/edge IDs, coordinates, layout, or style.

For Todo, this check must surface the source-backed application-to-in-memory-repository composition and TodoItem storage/use relationships that the cold profile omitted. The checklist remains conditional: one supported definition may still be sufficient for a genuinely single-definition request.

## Examples and Size

Each selected authoring contract returns complete, placeholder-free, schema-valid, semantic-validator-valid examples for only its mode/type. Examples use a leakage-disjoint domain rather than Todo content and are maintained as one validated asset source rather than copied independently into prompts, tools, tests, and docs.

Target static sizes are:

- structured route plan: small enough to replace the current dense workflow instruction body;
- selected authoring contract: approximately 3–5 KiB;
- combined route plan plus selected recipe: no larger than the current 8,212-byte workflow response unless a concrete validated requirement proves otherwise.

Complete 36 KiB schemas, unrelated modes/types, provider prompts, hidden implementation detail, raw source, and hidden gold are never returned.

## Provenance and Saved Diagram

Context generation still validates before persistence that every logical/canonical element is grounded in an allowed current claim, accepted assumption, or permitted neutral schema rule. The saved diagram records that grounding was validated at generation time but does not promise that an old claim can be resolved after JSON 1 is replaced.

Canonical metadata retains a compact generation receipt and each context element may retain a bounded mapping rationale. Full claim/evidence history is not copied into the diagram. Optional trace/debug may preserve deeper exact attempt information when explicitly enabled.

This is a deliberate generation-time provenance policy, not a historical certification claim.

## Recovery and No-Rerun

- One generation call is allowed per unchanged saved request.
- Internal deterministic or semantic repairs remain within that attempt.
- A later host attempt requires changed evidence, request, accepted policy, or external/configuration condition.
- A client timeout is an unknown outcome and never direct retry permission.
- Generation timeout recovery performs one exact provider-free finalized-request check.
- Render recovery starts from saved canonical diagram JSON.
- Evidence freshness/conflict requires a new status and complete current snapshot; no blind overwrite.
- Request conflict requires the current request reference and complete replacement.
- Draft/trace/debug cleanup failure never repeats completed semantic work.
- Completed, failed, invalid, interrupted, and uncertain benchmark/provider identities are never reused.

## Benchmark Boundary

The current-interface baseline is captured before candidate implementation.

### Host Preparation

```text
host receives the request
-> workflow routing
-> repository search/read
-> JSON 1 save if needed
-> JSON 2 save
-> stop before Azure
```

Observations are **reference-host characterizations**, not measured cells. Each records contract properties — response bytes, tool-call counts, authoring attempts, deterministic failure codes, artifact sizes, and relationship closure — and never wall time, because the reference host is the implementing agent and its timing is neither comparable nor uncontaminated.

The retired Copilot `C0`/`W0`/`C1`/`W1` cells and their identities are terminal and never reused. The governing gate is the cold completion criterion in [`lane-a-00-group.md`](lane-a-00-group.md).

### Integration

Integration consumes a saved request and first runs through real MCP, deterministic production services, a scripted fake provider, and browser proof. A real provider-backed observation requires a separate exact authorization, new identities, and exclusive Lane B provider-resource release. No provider calls occur during host preparation.

Only `C0<->C1`, `W0<->W1`, and `I0<->I1` receive direct comparisons. Different cells, repositories, requests, models, GraphPilot conditions, and the prepared-input Block 5 anchor never share forced percentages.

## Measurement

Machine evidence covers:

- user-visible wall under the declared human-arm boundary;
- MCP startup, initialization, discovery, call timing, bytes, and safe result codes;
- JSON 1/JSON 2 save attempts and validation failures;
- artifact sizes and version identities;
- observed zero provider calls during host preparation;
- terminal result and integration/browser state.

A host's native search and read operations are generally not exposed through a supported interface. Any self-reported search or read counts are labeled host-reported, source bytes are derived from validated relative paths and ranges, and unavailable values remain null with reasons. No raw query or source content is persisted.

The existing `graphpilot.evaluation.workflow-audit-external-evidence.v1` contract and `ExternalHostEvidenceAdapter` remain unchanged for normalized W01–W03 values that genuinely fit. A narrow companion host-benchmark manifest/event/result package owns host/model/repository/cache/request metadata, detailed counters, artifact references, validity, and compatibility rather than overloading generic workflow-audit metrics.

## Retention Gate

The Lane A candidate is retained only when:

- validation failures and authoring attempts materially decrease;
- compatible cold and warm host wall materially improve;
- searches/reads do not regress without evidence;
- warm source searches, source reads, and JSON 1 rebuilds remain zero;
- JSON 1 and JSON 2 remain complete and authority-correct;
- BDD relationship/ownership coverage passes;
- provider-free integration succeeds;
- separately authorized live I1 preserves readiness, required/forbidden meaning, reviewed quality, generation-time provenance, persistence, SVG, recovery, and visible editor completion;
- security, no-rerun, and compatibility gates pass.

A failed candidate is reverted as one coherent host-authoring wave. The noninfluencing benchmark capability and immutable baseline/candidate evidence remain.

## Proposed Delivery Topology

```text
A01 Host Benchmark Contract
  -> A02 Devin Host Transition
  -> A03 Evidence Authoring Unblock
  -> cold-authoring retest
  -> A04 Snapshot and Interface Contracts
       |-> A05 Snapshot Backend --|
       |-> A06 Host Interface ----|-> A07 Lane A Integration
                                         -> A08 Candidate Measurement
                                         -> A09 Wave Decision and Handoff
```

| Slice | Purpose | Provider |
| --- | --- | --- |
| A01 | Freeze proportional benchmark contracts, recorder/proxy, external adapter use, validity, reporting, and provider-free proof | none |
| A02 | Retarget the host to Devin CLI, retire the Copilot cells, and record the cold-authoring baseline finding | none |
| A03 | Derive evidence values the host cannot know, report the intended schema branch's defects, and retest cold authoring | none |
| A04 | Freeze snapshot, request, route-plan, authoring-contract, example, BDD checklist, and grounding-receipt contracts | none |
| A05 | Implement current-snapshot validation/persistence, version references, draft cleanup, and internal flat-reference adaptation | none |
| A06 | Implement the router and selected authoring-contract lookup with size/parity/security tests | none |
| A07 | Wire shared MCP/schema/diagram contracts, run complete provider-free backend/frontend/MCP/browser gates, and audit integration | none |
| A08 | Capture the candidate reference observation and provider-free integration; run any provider-backed observation only under a later exact authorization | none unless separately gated |
| A09 | Compare compatible evidence, retain/revert, update cumulative handoff, and stop before the next wave | none |

A05 and A06 are the only potentially parallel write slices, after committed A04 contracts, in separate worktrees with disjoint ownership. Shared MCP/schema/diagram/docs files remain A07 integration-owner scope. All observation capture, integration, provider work, and final decisions are sequential.

## Lane Isolation

Lane A must not change Lane B semantic-review or generation-endpoint prompts, projections, response schemas, validators, correction code, live packages, terminal evidence, provider controls, or identities. Lane B must not modify Lane A host benchmark, snapshot, route-plan, authoring-contract, examples, or Todo host observations.

Shared registration, canonical diagram schema, frontend type parity, Block 6 group/status/decision files, and provider resources are integration-owned and serialized. No Lane A live proof starts while Lane B owns the provider lane.

## Risks and Strongest Alternative

The main risks are the extra Stage 2 call, snapshot/request/schema integration breadth, generation-time-only historical provenance, opaque reference debugging, example leakage, an over-eager BDD checklist, and overclaiming from one Todo observation. Each is bounded by byte measurement, provider-free proof, exact scope, safe errors, leakage-disjoint examples, conditional rubric guidance, and Block 7 deferral.

The strongest alternative is to retain the current JSON 1 history/digest/request contracts and add only the two-stage host lookup. That is a smaller implementation but explains rather than removes the demonstrated host bookkeeping burden. The approved snapshot direction is larger because it addresses the authoring root directly.

## Related Docs

- [`lane-a-00-group.md`](lane-a-00-group.md)
- [`../07-block-06-whole-workflow-optimization.md`](../../../07-block-06-whole-workflow-optimization.md)
- [`00-group.md`](../shared/00-group.md)
- [`../11-block-execution-and-parallelism.md`](../../../11-block-execution-and-parallelism.md)
- [`../05-complete-live-anchor-and-reaudit/04-reaudit-and-handoff.md`](../../../05-complete-live-anchor-and-reaudit/04-reaudit-and-handoff.md)
- [`../05-complete-live-anchor-and-reaudit/evidence/block6-backlog.md`](../../../05-complete-live-anchor-and-reaudit/evidence/block6-backlog.md)
- [`../../../../../01-architecture/03-mcp-tools/README.md`](../../../../../../../02-architecture/01-mcp-tools/README.md)
- [`../../../../../01-architecture/03-mcp-tools/03-context-workflow.md`](../../../../../../../02-architecture/01-mcp-tools/03-context-workflow.md)
- [`../../../../../02-design-and-features/08-context-backed-generation/README.md`](../../../../../../../03-design/01-context-generation/README.md)
- [`../../../../../02-design-and-features/09-workflow-audit-design.md`](../../../../../../../03-design/11-workflow-audit.md)
- [`../../../../../02-design-and-features/decision-decisions.md`](../../../../../../../05-delivery/04-decisions.md)
