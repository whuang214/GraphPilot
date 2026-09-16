# JSON 2 — Diagram Request Context Packet

> **Status:** Historical JSON 2 design snapshot. Current intended behavior is owned by
> [`03-diagram-request-context.md`](../../03-design/01-context-generation/04-diagram-request-context.md).
> Runtime JSON Schema/validation is not implemented.
>
> **Scope of this doc.** This is the JSON 2 **structure** reference: sections, fields, enums, and
> validation rules. The workflow, the packet lifecycle, the artifact map, and user-answer routing live in
> the overall flow doc, [`01-workflows-and-prompts.md`](01-workflows-and-prompts.md).

## Purpose

The diagram request context is a small packet for one context-backed diagram workflow: what the user
wants shown, which exact JSON 1 claim versions to use, how relevant uncertainty is handled, and which
accepted diagram-only assumptions or non-factual decisions guide generation. The host owns request framing,
formulates and records JSON 2 entries from user intent and repository context, and may provide an initial
claim selection; the backend readiness reviewer may complete/correct that selection from JSON 1 and returns
validated recommendations for the host to apply and persist.

It is not a second knowledge base. It references exact claim versions in the persistent JSON 1 manifest
([`02-evidence-manifest.md`](02-evidence-manifest.md)) without copying their statements, payloads, or
evidence, and binds to one JSON 1 digest.

It is **persisted per diagram** as the latest request intent at
`.graphpilot/context/requests/<request-file>.gp-request.json`: overwritten on regeneration, stamped with the
JSON 1 digest it was built against, and reconciled on load if JSON 1 has changed. It is **not internally
versioned** and has no persisted generation-snapshot companion. The canonical diagram preserves compact
trace metadata and element origins; this request context remains the natural input to a later grounded
**edit**. The full lifecycle is in [`01-workflows-and-prompts.md`](01-workflows-and-prompts.md), and the
generation/trace contract is
[`06-context-backed-generation-and-provenance.md`](06-context-backed-generation-and-provenance.md).

## Simple complete example

```json
{
  "schemaVersion": "graphpilot.diagram-request.v1",
  "kind": "diagramRequestContext",
  "requestId": "request-order-processing",
  "diagramName": "order-processing",
  "manifestRef": {
    "path": ".graphpilot/context/evidence/repository.gp-evidence.json",
    "id": "evidence-order-service",
    "digest": "sha256:current-manifest-digest"
  },
  "request": {
    "original": "Create an activity diagram of order processing.",
    "goal": "Explain the implemented order-submission flow from API entry through event publication.",
    "diagramType": "activity_diagram",
    "audience": "Backend and application developers",
    "detailLevel": "standard"
  },
  "scope": {
    "included": [
      "Order submission through validation, persistence, and event publication",
      "The validation-failure outcome"
    ],
    "excluded": [
      "Frontend behavior",
      "Private validation helper implementation",
      "Background event-consumer processing"
    ]
  },
  "selectedClaims": [
    {
      "claimRef": {
        "id": "claim-order-submission-entry",
        "version": 1
      },
      "role": "primary",
      "reason": "Establishes the trigger and public entry point for the requested flow."
    },
    {
      "claimRef": {
        "id": "claim-validate-before-save",
        "version": 2
      },
      "role": "primary",
      "reason": "Defines the central ordering and validation branch."
    },
    {
      "claimRef": {
        "id": "claim-order-event-publication",
        "version": 1
      },
      "role": "supporting",
      "reason": "Defines the final in-scope interaction after persistence."
    },
    {
      "claimRef": {
        "id": "claim-order-service-boundary",
        "version": 1
      },
      "role": "context",
      "reason": "Supplies terminology and the responsibility boundary without requiring its own step."
    }
  ],
  "uncertaintyDispositions": [
    {
      "uncertaintyRef": "uncertainty-event-publication-failure",
      "disposition": "assume",
      "reason": "The failure outcome is relevant to the flow, but the repository does not establish it.",
      "assumptionRef": "assumption-publication-failure-is-terminal"
    },
    {
      "uncertaintyRef": "uncertainty-consumer-retry-policy",
      "disposition": "exclude",
      "reason": "Consumer retry behavior is outside the confirmed diagram scope."
    }
  ],
  "assumptions": [
    {
      "id": "assumption-publication-failure-is-terminal",
      "statement": "For this diagram only, treat event-publication failure as terminating the submission flow without retry.",
      "reason": "The repository does not establish failure handling, and the user accepted this narrow fallback for the diagram.",
      "origin": "host",
      "acceptedBy": "user",
      "acceptedAt": "2026-07-13T17:00:00Z"
    }
  ],
  "decisions": [
    {
      "id": "decision-show-validation-failure",
      "kind": "emphasis",
      "statement": "Show the validation-failure branch explicitly.",
      "reason": "The audience needs to understand why invalid orders do not reach persistence.",
      "origin": "user",
      "acceptedBy": "user",
      "acceptedAt": "2026-07-13T17:00:00Z"
    },
    {
      "id": "decision-use-service-labels",
      "kind": "labeling",
      "statement": "Prefer service and operation names already established by selected claims.",
      "reason": "Keeps labels traceable and avoids invented business terminology.",
      "origin": "host",
      "acceptedBy": "host",
      "acceptedAt": "2026-07-13T17:00:00Z"
    }
  ]
}
```

## Complete section map

```json
{
  "schemaVersion": "graphpilot.diagram-request.v1",
  "kind": "diagramRequestContext",
  "requestId": "request-example",
  "diagramName": "example-diagram",
  "manifestRef": {},
  "request": {},
  "scope": {},
  "selectedClaims": [],
  "uncertaintyDispositions": [],
  "assumptions": [],
  "decisions": []
}
```

| Section | Plain-language question it answers |
| --- | --- |
| document envelope | What request-packet contract is this, which stable request owns it, and what output stem should the diagram use? |
| `manifestRef` | Which exact JSON 1 manifest must the backend resolve? |
| `request` | What diagram did the user ask for and for whom? |
| `scope` | What should the diagram include and deliberately omit? |
| `selectedClaims` | Which exact supported fact versions should assessment and generation consider? |
| `uncertaintyDispositions` | How should each relevant unresolved JSON 1 question affect this diagram? |
| `assumptions` | Which narrow unsupported propositions did the host or user accept for this diagram, and who originated them? |
| `decisions` | Which non-factual emphasis, labeling, grouping, or presentation choices guide modeling? |

## 1. Document envelope

```json
{
  "schemaVersion": "graphpilot.diagram-request.v1",
  "kind": "diagramRequestContext",
  "requestId": "request-order-processing",
  "diagramName": "order-processing"
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `schemaVersion` | Yes | Constant identifying the packet format. | Selects deterministic validation and future migration. |
| `kind` | Yes | Constant identifying this as a diagram request context. | Distinguishes the packet from JSON 1, transient resolved context, and canonical diagrams. |
| `requestId` | Yes | Stable ownership identity tying the packet to one diagram. | Correlates assessment, generation errors, and identity-aware canonical replacement. |
| `diagramName` | Yes | Host-proposed, backend-validated safe filename stem. | Deterministically names `.graphpilot/diagrams/<diagramName>.gp.json` and sibling artifacts without accepting an Azure rename. |

### Envelope constants

| Field/value | Meaning |
| --- | --- |
| `schemaVersion: graphpilot.diagram-request.v1` | First diagram-request packet contract. |
| `kind: diagramRequestContext` | This value selects JSON 1 facts for one diagram; it is not evidence or a diagram. |

`requestId` is stable per diagram: regenerating that diagram overwrites the same persisted request context
rather than accumulating attempts. It also authorizes identity-aware canonical replacement: an existing
`.graphpilot/diagrams/<diagramName>.gp.json` may be replaced only when its stored request identity matches.
Whether a discarded-and-rebuilt attempt reuses the ID is an MCP-contract detail.

`diagramName` is the authoritative artifact stem proposed by the host. It contains no path or extension and
must pass backend filename validation. A request filename normally mirrors it for readability, but the
backend does not infer identity from that filename and Azure cannot rename it.

## 2. `manifestRef` section

```json
{
  "manifestRef": {
    "path": ".graphpilot/context/evidence/repository.gp-evidence.json",
    "id": "evidence-order-service",
    "digest": "sha256:current-manifest-digest"
  }
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `manifestRef.path` | Yes | Workspace-relative path to JSON 1. | Lets the backend load the manifest through its path-safe file boundary. |
| `manifestRef.id` | Yes | Expected stable JSON 1 manifest identity. | Detects a moved path resolving to the wrong manifest. |
| `manifestRef.digest` | Yes | Expected exact JSON 1 manifest digest. | Prevents assessment or generation from using a different knowledge state than the host selected from. |

A manifest revision number is deliberately omitted. The digest already provides the exact binding; the
backend may return the human-readable current revision in diagnostics. The canonical diagram records the
exact manifest path/ID/digest used in its compact generation trace metadata.

The stored `digest` is the JSON 1 state this packet was last built against, so the two are compared at
two different moments:

- **On load** (opening a persisted request context, e.g. to edit or regenerate): if the current JSON 1
  digest differs, the packet is **reconciled, not discarded**. The backend/host re-verifies selected claim
  versions and every uncertainty disposition, flags claims that became inactive or changed and uncertainty
  refs that are no longer open, and requires the host to update the packet before rebinding its digest.
  A stale `assume` pair is never silently promoted: the host either replaces it with a verified active claim
  that supports the same proposition, or restores/records an open uncertainty if the proposition is still
  unsupported. Ambiguous replacements require user confirmation.
- **Immediately before generation:** the backend re-resolves and re-validates JSON 1 and requires the
  packet's `id` + `digest` to match the reconciled state; it will not generate against a different
  knowledge state. On success the exact digest is copied into canonical diagram trace metadata.

## 3. `request` section

```json
{
  "request": {
    "original": "Create an activity diagram of order processing.",
    "goal": "Explain the implemented order-submission flow.",
    "diagramType": "activity_diagram",
    "audience": "Backend and application developers",
    "detailLevel": "standard"
  }
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `original` | Yes | The user's original diagram request, preserved without semantic rewriting. | Retains intent for assessment/generation and later request reconciliation. |
| `goal` | Yes | Concise normalized outcome the host believes the user wants. | Gives assessment and generation one clear objective. |
| `diagramType` | Yes | Confirmed generatable GraphPilot diagram type. | Selects the backend's internal readiness rubric and generation profile. |
| `audience` | Yes | Bounded human-readable description of intended readers. | Guides abstraction, terminology, and reviewer sufficiency. |
| `detailLevel` | Yes | Requested abstraction/detail level. | Helps bound selection and prevents accidental code-level inventories. |

### Diagram-type enum

| Value | Meaning |
| --- | --- |
| `activity_diagram` | Model a bounded behavior or workflow. |
| `use_case_diagram` | Model actors, system boundaries, and user-visible goals. |
| `bdd_diagram` | Model SysML block/domain structure, properties, and relationships. |

`custom` is excluded because context-backed generation requires a concrete per-type readiness rubric and
generation profile. The existing `custom` type remains a save/edit canvas, not a generated type.

> **No `viewpoint` field in v1.** A repository-derived diagram depicts the implementation the code is
> evidence for, so v1 is implicitly `as_implemented`; there is no request viewpoint knob. JSON 1 still
> records claim `appliesToViewpoints` as latent metadata (default `as_implemented`), so
> `as_designed`/`as_required` diagrams can be added later without a JSON 1 change. An accepted assumption
> is **not** a viewpoint switch — it is an unsupported diagram-only choice, not evidence of intended
> design.

### Detail-level enum

| Value | Meaning |
| --- | --- |
| `overview` | Show only the main boundary, actors/components, and principal relationships or steps. |
| `standard` | Show enough structure or behavior to explain the requested subject without private implementation detail. |
| `detailed` | Include supported secondary paths/features relevant to the confirmed scope, still excluding incidental helpers. |

## 4. `scope` section

```json
{
  "scope": {
    "included": [
      "Order submission through event publication"
    ],
    "excluded": [
      "Frontend behavior",
      "Background consumer processing"
    ]
  }
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `scope.included` | Yes; non-empty | Bounded subjects, flows, boundaries, or structures the diagram should cover. | Defines the semantic boundary for claim selection and readiness. |
| `scope.excluded` | Yes; may be empty | Explicitly omitted subjects that could otherwise be interpreted as relevant. | Prevents accidental scope expansion and documents deliberate omissions. |

Scope statements are request-specific and may use user language. They do not become JSON 1 claims.
Excluding a known fact from this diagram does not dispute or retire it in JSON 1. This top-level section is
the sole v1 semantic scope boundary: the host may propose it, but the user confirms it, and later scope
changes update this section rather than creating a second scope instruction in `decisions`.

## 5. `selectedClaims` section

`selectedClaims` is **backend-assisted**, not host-only. The host may submit an informed first pass or an
empty array. Readiness loads complete JSON 1 locally, reviews a bounded active-claim index, and returns
validated `recommendedSelections`/`removeSelections`; the host applies accepted changes and persists the
packet. The reviewer never silently mutates JSON 2, and the generator never receives the full manifest.

```json
{
  "selectedClaims": [
    {
      "claimRef": {
        "id": "claim-validate-before-save",
        "version": 2
      },
      "role": "primary",
      "reason": "Defines the central ordering and validation branch."
    }
  ]
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `claimRef.id` | Yes | Stable JSON 1 claim ID. | Identifies the reusable fact. |
| `claimRef.version` | Yes | Exact immutable claim version. | Prevents later manifest updates from changing what this packet means. |
| `role` | Yes | Selection role in this request. | Distinguishes facts that should drive the model from supporting context. |
| `reason` | Yes | Concise explanation of relevance to goal/scope. | Lets the reviewer detect over-selection, omissions, and abstraction mistakes. |

### Selection-role enum

| Value | Meaning |
| --- | --- |
| `primary` | The fact directly describes something the requested diagram should communicate. |
| `supporting` | The fact connects, constrains, or disambiguates primary facts. |
| `context` | The fact supplies terminology, purpose, or boundary context without necessarily becoming a diagram element. |

Normal v1 requests select only an `active` claim's `currentVersion`. Historical claim selection is
deferred. Because v1 diagrams depict `as_implemented`, selection does not filter on viewpoint;
`as_designed`/`as_required` claims simply are not typically selected until those diagram types exist.

The selected set must be semantically closed enough to understand structured claim references. Readiness
returns every required unselected payload claim reference as a deterministic `context` selection
recommendation; the backend never silently adds it to JSON 2. See
[`01-readiness-reviewer.md`](05-readiness/01-readiness-reviewer.md).

## 6. `uncertaintyDispositions` section

JSON 1 retains only currently open uncertainties. JSON 2 records how the relevant subset affects this one
diagram.

```json
{
  "uncertaintyDispositions": [
    {
      "uncertaintyRef": "uncertainty-event-publication-failure",
      "disposition": "assume",
      "reason": "The unknown outcome is relevant to the requested flow.",
      "assumptionRef": "assumption-publication-failure-is-terminal"
    }
  ]
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `uncertaintyRef` | Yes | ID of a currently open JSON 1 uncertainty. | Connects the request decision to the reusable unresolved question. |
| `disposition` | Yes | How this diagram treats the uncertainty. | Makes omission, blocking, assumption, and deferral explicit. |
| `reason` | Yes | Request-specific rationale. | Lets readiness judge whether the disposition is acceptable. |
| `assumptionRef` | When `assume` | ID of the corresponding packet assumption. | Prevents an uncertainty from being marked handled without an explicitly accepted assumption. |

### Disposition enum

| Value | Meaning | Generation consequence |
| --- | --- | --- |
| `block` | The uncertainty must be resolved before a trustworthy diagram can be generated. | Always blocks. |
| `exclude` | The uncertain subject is deliberately outside this diagram's confirmed scope. | Allowed only when scope and the readiness rubric/reviewer make the exclusion coherent. |
| `assume` | The host/user accepted a diagram-only assumption that fills the gap. | May proceed with visible assumption provenance and readiness limits. |
| `defer` | The uncertainty remains an advisory gap but does not affect required in-scope content. | May proceed only if readiness classifies it as non-blocking. |

Not every manifest uncertainty must appear—only uncertainties relevant to the request. The reviewer may
identify an omitted relevant uncertainty and return it as a finding. Disposition `uncertaintyRef`s are unique
within the packet. An `assume` disposition and its assumption form a one-to-one pair; non-`assume`
dispositions cannot carry `assumptionRef`.

## 7. `assumptions` section

An assumption is one exact, narrow, unsupported factual proposition that the host formulates from user
intent and/or incomplete context and accepts for this diagram to resolve one open JSON 1 uncertainty. It is
not an omission, scope choice, presentation default, or weakly supported claim. Those belong to
`exclude`/`defer`, `scope`, `decisions`, or JSON 1 respectively. Assumptions never become evidence or claims.

```json
{
  "assumptions": [
    {
      "id": "assumption-publication-failure-is-terminal",
      "statement": "For this diagram only, treat event-publication failure as terminating the submission flow without retry.",
      "reason": "The repository does not establish failure handling, and the user accepted this narrow fallback for the diagram.",
      "origin": "host",
      "acceptedBy": "user",
      "acceptedAt": "2026-07-13T17:00:00Z"
    }
  ]
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `id` | Yes | Packet-local stable assumption ID. | Supports assessment and generated-element provenance. |
| `statement` | Yes | Exact diagram-only unsupported proposition. | Makes unsupported content visible and bounded. |
| `reason` | Yes | Why the assumption is needed for this request. | Helps the user and reviewer judge its acceptability. |
| `origin` | Yes | Actor whose input principally produced the exact persisted proposition: `user` or `host`. | Distinguishes a user-supplied assumption from one the host formulated from context. |
| `acceptedBy` | Yes | Actor that accepted its use: `user` or `host`. | Separates origin from authority and makes host-made assumptions visible. |
| `acceptedAt` | Yes | UTC time the host recorded acceptance. | Preserves the authority event in canonical trace metadata. |

The host is always the JSON 2 writer, so a redundant `recordedBy` field is omitted. `origin` describes the
semantic source, not the file writer. `origin: "user"` requires `acceptedBy: "user"`; a host-formulated
assumption may be accepted by the host or user. A bounded self-accepted assumption records
`origin: "host"`, `acceptedBy: "host"`, and the acceptance time.

Each assumption is referenced by exactly one `assume` disposition; standalone or shared assumptions are
invalid. Related evidence may motivate the linked JSON 1 uncertainty, but it does not support the assumption.
JSON 2 contains accepted assumptions only: the host prompt owns consultation before persistence, while
readiness treats `origin`/`acceptedBy` as provenance and does not re-evaluate who accepted the assumption. If
current evidence later supports the proposition, the assumption object does not become a claim: the host
selects the new/existing claim and removes the paired assumption and disposition before reassessment.
Generated elements affected by an assumption retain its ID rather than a fabricated claim reference.

## 8. `decisions` section

Decisions guide non-factual emphasis and presentation without claiming repository truth or filling an
uncertainty.

```json
{
  "decisions": [
    {
      "id": "decision-show-validation-failure",
      "kind": "emphasis",
      "statement": "Show the validation-failure branch explicitly.",
      "reason": "The audience needs to understand why invalid orders do not persist.",
      "origin": "user",
      "acceptedBy": "user",
      "acceptedAt": "2026-07-13T17:00:00Z"
    }
  ]
}
```

| Field | Required | What it is | Why it exists |
| --- | --- | --- | --- |
| `id` | Yes | Packet-local stable decision ID. | Keeps generation guidance traceable when the exact decision object is copied into canonical metadata. |
| `kind` | Yes | Category of request-specific guidance. | Keeps decisions bounded and reviewable. |
| `statement` | Yes | Concise instruction to assessment/modeling. | Communicates the choice without pre-building topology. |
| `reason` | Yes | Why the choice helps this request. | Helps review detect arbitrary or conflicting guidance. |
| `origin` | Yes | Actor whose input principally produced the exact persisted decision: `user` or `host`. | Separates semantic origin from acceptance. |
| `acceptedBy` | Yes | Actor that accepted the decision for this request: `user` or `host`. | Prevents a host default from masquerading as user intent. |
| `acceptedAt` | Yes | UTC time acceptance was recorded. | Preserves the authority event in canonical trace metadata. |

### Decision-kind and authority rules

| Kind | Meaning | Allowed `acceptedBy` |
| --- | --- | --- |
| `emphasis` | Requests that a supported fact/path/relationship be visually prominent. | `user` |
| `labeling` | Guides labels or terminology while remaining traceable to selected facts. | `user`, or `host` for a fact-preserving reversible default |
| `grouping` | Requests conceptual grouping without assigning final UML/SysML element types. | `user` |
| `presentation` | Supplies non-semantic visual guidance such as orientation or density. | `user`, or `host` for a reversible default |

`origin` may be `user` or `host` for every kind; a host-formulated decision that requires user acceptance
records `origin: "host"` and `acceptedBy: "user"`. The reviewer/backend may recommend an action but never
becomes a persisted accepting actor. `scope` is deliberately not a decision kind in v1: changes belong in
the user-confirmed top-level `scope` section.

A host-accepted decision must be reversible, compatible with the request, and unable to add factual meaning.
Any user-accepted decision overrides a conflicting host default. A decision must not contain
unsupported facts, final node/edge IDs, coordinates, GraphPilot `semanticType`s, or a complete logical
topology. The backend remains responsible for UML/SysML modeling.

## 9. Assessment and generation (structural notes only)

JSON 2 does **not** embed an assessment result: the framework/result contract is
[`01-readiness-reviewer.md`](05-readiness/01-readiness-reviewer.md), and the exact rubric/calculation is
[`05-readiness/`](05-readiness/README.md). The overall sequence is
outlined in [`01-workflows-and-prompts.md`](01-workflows-and-prompts.md).
Generation deterministically populates this reference packet with exact selected JSON 1 claim versions and
evidence **in memory only**, then records compact readiness/input identifiers and element origins in the
canonical diagram; full behavior is
[`06-context-backed-generation-and-provenance.md`](06-context-backed-generation-and-provenance.md). The
structural obligations on this packet are that it stays read-only during assessment/generation and
re-validates against the current JSON 1 digest before any generation call (invariants below).

## 10. Validation invariants

The eventual packet schema/service must enforce:

1. envelope constants are exact and `requestId` is non-empty;
2. `diagramName` is present, bounded, contains only a safe filename stem, and names no path/extension;
3. `manifestRef.path` is workspace-relative and path-safe;
4. referenced JSON 1 exists, validates, and matches both `id` and `digest`;
5. `diagramType` is one of the three generatable concrete types;
6. request goal, audience, included scope, and detail level are present and bounded;
7. selected claim references are unique and identify existing immutable versions;
8. normal v1 selection uses active claims at `currentVersion`;
9. every selection has a valid role and non-empty relevance reason;
10. uncertainty disposition refs are unique and identify currently open JSON 1 uncertainties;
11. every `assume` disposition references exactly one existing packet assumption, and `assumptionRef` is forbidden for every other disposition;
12. every assumption is referenced by exactly one `assume` disposition—standalone and shared assumptions are invalid;
13. assumption and decision `origin`/`acceptedBy` values are `user` or `host`, and `origin: "user"` requires `acceptedBy: "user"`;
14. no assumption duplicates meaning already supported by a current active claim; readiness performs this semantic check;
15. `origin`/`acceptedBy` are provenance only; readiness validates their shape but does not re-evaluate the host/user consultation that occurred before persistence;
16. `block` dispositions prevent generation;
17. assumption and decision IDs are unique within the packet;
18. decisions use only the bounded kinds, actor values, and kind/`acceptedBy` combinations;
19. host-accepted decisions are reversible and fact-preserving; decisions never fill uncertainties or authorize unsupported facts;
20. top-level `scope` is the only v1 semantic scope authority, and `scope` is not a decision kind;
21. JSON 1 evidence/claim bodies are not duplicated into persisted JSON 2;
22. raw repository content and discovery-tool output never appear;
23. GraphPilot semantic types, logical nodes/edges, coordinates, and rendering data never appear;
24. assessment/population/generation do not mutate the loaded packet;
25. on load, a changed manifest digest triggers claim and uncertainty-disposition reconciliation; stale assumption pairs are removed only through an explicit claim replacement or renewed uncertainty, and generation refuses a still-mismatched packet;
26. context generation receives this packet by workspace/path, while deterministic runtime population remains transient.

## 11. User-answer routing

How a user reply lands in JSON 1 (factual clarification) versus this request packet (assumptions, scope,
emphasis, labeling) is the single routing table in
[`01-workflows-and-prompts.md`](01-workflows-and-prompts.md).

## 12. Deliberately not stored in JSON 2

- evidence records or raw source;
- duplicated claim statements, payloads, or support objects;
- repository source fingerprints or discovery indexes;
- Graphify or other discovery-tool output;
- manifest or claim history;
- unresolved facts promoted into claims;
- final GraphPilot node/edge semantic types;
- logical or canonical nodes and edges;
- coordinates, sizes, styles, or rendered data;
- an embedded readiness score/result;
- an internal revision chain, resolved/populated claim bodies, or per-attempt packet history;
- secrets, credentials, `.env` values, or unbounded excerpts.

## 13. Remaining design details

Before implementation, the contract still needs:

- exact string/array size limits, safe `diagramName` grammar, and ID formats;
- the exact on-load reconciliation result shape (which claims or uncertainty dispositions changed, which assumption pairs became stale, and how the host is prompted);
- canonical JSON 2 serialization/digest rules used for trace metadata and mid-generation stability checks;
- the boundary between `grouping` decisions and backend-owned modeling;
- final readiness consequences for `assume`/`defer` dispositions and the approved override transport
  (working design: [`01-readiness-reviewer.md`](05-readiness/01-readiness-reviewer.md));
- implementation mapping for the exact MCP error/result envelopes defined in
  [`07-mcp-prompts-and-tool-contracts.md`](07-mcp-prompts-and-tool-contracts.md).

Readiness has a framework/result draft in [`01-readiness-reviewer.md`](05-readiness/01-readiness-reviewer.md), with exact
rubric/calculation in
[`05-readiness/`](05-readiness/README.md). Runtime population,
provenance, trace metadata, and persistence are drafted in
[`06-context-backed-generation-and-provenance.md`](06-context-backed-generation-and-provenance.md).

### Final definition

> The diagram request context is a per-diagram, manifest-bound JSON packet—persisted as latest intent but
> not internally versioned—that names the target diagram, states one confirmed goal/scope, carries a
> backend-assisted exact claim selection, relevant uncertainty dispositions, accepted assumptions, and
> non-factual modeling/presentation decisions, without copying evidence, exposing GraphPilot semantic
> types, or pre-building the diagram.
