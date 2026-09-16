# Direct Diagram Request Contract

> **Status: core shape accepted; exact JSON Schema not yet specified.** This document records the working
> `graphpilot.direct.diagram-request.v1` contract authored by the direct branch of the unified MCP workflow.
> Fields marked open remain design questions and must not be treated as accepted implementation requirements.

## Purpose

Capture one complete, self-contained conceptual diagram request after host framing and adaptive consultation.
The direct request is persisted beside context requests at:

```text
.graphpilot/requests/<diagramName>.gp-request.json
```

It is not JSON 1, historical JSON 2, repository evidence, or a logical diagram. Direct and context requests share
storage mechanics but retain separate schemas and authority.

```text
natural-language request
  -> unified workflow direct branch
  -> complete DirectDiagramRequest
  -> diagram_request_save
  -> backend DirectGenerationInput builder
```

## Working complete example

```json
{
  "schemaVersion": "graphpilot.direct.diagram-request.v1",
  "kind": "directDiagramRequest",
  "requestId": "request-event-driven-order-platform",
  "diagramName": "event-driven-order-platform",
  "request": {
    "original": "Design an event-driven order-processing architecture.",
    "goal": "Explain service responsibilities and event interactions.",
    "diagramType": "bdd_diagram",
    "audience": "Platform and application developers",
    "detailLevel": "standard"
  },
  "scope": {
    "included": [
      "Order API",
      "Order Service",
      "Payment Service",
      "Event Bus",
      "Fulfillment Service"
    ],
    "excluded": [
      "Database schemas",
      "Deployment infrastructure"
    ]
  },
  "requirements": [
    {
      "id": "requirement-order-service",
      "kind": "entity",
      "statement": "The design contains an Order Service."
    },
    {
      "id": "requirement-order-event",
      "kind": "behaviorStep",
      "statement": "Order Service publishes an order-created event."
    },
    {
      "id": "requirement-payment-gate",
      "kind": "constraint",
      "statement": "Fulfillment begins only after successful payment."
    }
  ],
  "assumptions": [
    {
      "id": "assumption-event-delivery",
      "statement": "Event delivery is at least once.",
      "reason": "Delivery semantics affect retry and deduplication behavior.",
      "origin": "host",
      "acceptedBy": "host",
      "acceptedAt": "2026-07-16T12:00:00Z"
    }
  ],
  "decisions": [
    {
      "id": "decision-show-payment-failure",
      "kind": "emphasis",
      "statement": "Show payment failure explicitly.",
      "reason": "Failure handling is important to the audience.",
      "origin": "user",
      "acceptedBy": "user",
      "acceptedAt": "2026-07-16T12:00:00Z"
    },
    {
      "id": "decision-layout-direction",
      "kind": "presentation",
      "statement": "Prefer a readable left-to-right presentation.",
      "reason": "The component relationships are easier to scan horizontally.",
      "origin": "host",
      "acceptedBy": "host",
      "acceptedAt": "2026-07-16T12:00:00Z"
    }
  ]
}
```

## Envelope

| Field | Required | Status | Meaning |
| --- | --- | --- | --- |
| `schemaVersion` | Yes | Accepted | Exact `graphpilot.direct.diagram-request.v1` constant |
| `kind` | Yes | Accepted | Exact `directDiagramRequest` constant |
| `requestId` | Yes | Accepted | Stable immutable request identity |
| `diagramName` | Yes | Accepted | Host-owned immutable exact safe output stem |
| `request` | Yes | Accepted | Confirmed user intent |
| `scope` | Yes | Accepted | Explicit included/excluded conceptual scope |
| `requirements` | Yes | Accepted | Typed mandatory plain-language content |
| `assumptions` | Yes | Accepted | Finalized user/host assumptions; may be empty |
| `decisions` | Yes | Accepted | Non-factual emphasis/labeling/grouping/presentation guidance |

There is no top-level free-text `style`. Conceptual presentation guidance uses `decisions[kind=presentation]`.
A future typed visual-style object is deferred and would be applied deterministically rather than treated as an
unstructured generation hint.

## `request`

```json
{
  "original": "Design an event-driven order-processing architecture.",
  "goal": "Explain service responsibilities and event interactions.",
  "diagramType": "bdd_diagram",
  "audience": "Platform and application developers",
  "detailLevel": "standard"
}
```

| Field | Required | Rule |
| --- | --- | --- |
| `original` | Yes | Verbatim original request; nonblank and bounded |
| `goal` | Yes | One self-contained normalized objective |
| `diagramType` | Yes | One currently generatable concrete type |
| `audience` | Yes | Bounded human-readable audience |
| `detailLevel` | Yes | `overview`, `standard`, or `detailed` |

The host may clarify the request but cannot replace `original` with its interpretation. `goal` and other fields
carry the normalized intent.

## `scope`

```json
{
  "included": ["Order submission", "Payment", "Fulfillment"],
  "excluded": ["Database schemas"]
}
```

- `included` is nonempty after workflow framing.
- `excluded` may be empty.
- Entries remain conceptual and bounded; no source locators or repository assertions belong here.
- An excluded item cannot simultaneously be a mandatory requirement.

## `requirements`

Requirements are mandatory typed statements, not GraphPilot elements and not evidence claims.

```json
{
  "id": "requirement-payment-gate",
  "kind": "constraint",
  "statement": "Fulfillment begins only after successful payment."
}
```

### Accepted kinds

The contract reuses the evidence model's generic fact categories without importing evidence/version/provenance
semantics:

```text
boundary
entity
capability
actorGoal
relationship
behaviorStep
property
constraint
```

### Rules

- IDs are unique and stable within one request.
- Every listed requirement is mandatory; preferences belong in decisions.
- Statements use domain language.
- No requirement assigns `semanticType`, node/edge ID, coordinates, topology, or origin.
- Requirements have no claim version, evidence support, or repository viewpoint.
- The semantic reviewer references requirement IDs when reporting omissions or misrepresentation.

## `assumptions`

Direct assumptions reuse the context request's proposal/acceptance fields:

```json
{
  "id": "assumption-event-delivery",
  "statement": "Event delivery is at least once.",
  "reason": "Delivery semantics affect retry and deduplication behavior.",
  "origin": "host",
  "acceptedBy": "host",
  "acceptedAt": "2026-07-16T12:00:00Z"
}
```

| Field | Meaning |
| --- | --- |
| `origin` | Actor who introduced the assumption (`user` or `host`) |
| `acceptedBy` | Actor who authorized it for this attempt (`user` or `host`) |
| `acceptedAt` | UTC acceptance timestamp |

This represents user statements, autonomous host choices, and host proposals accepted by the user without losing
who proposed versus approved them.

Rules:

- Only meaning-changing inferred choices are recorded.
- Host assumptions require a reasonable conventional choice and cannot contradict user authority.
- A request such as “just make a reasonable design” delegates enough authority for host assumptions.
- If no safe default exists, the workflow asks the user.
- Minor labels/layout/default notation do not become assumptions.
- Every assumption in the saved request is finalized for that generation attempt.
- Direct host assumptions never become repository facts or grounded provenance.

## `decisions`

Decisions carry non-factual guidance using the same authority fields:

```json
{
  "id": "decision-show-payment-failure",
  "kind": "emphasis",
  "statement": "Show payment failure explicitly.",
  "reason": "Failure handling is important to the audience.",
  "origin": "user",
  "acceptedBy": "user",
  "acceptedAt": "2026-07-16T12:00:00Z"
}
```

Accepted kinds:

```text
emphasis
labeling
grouping
presentation
```

- IDs are unique within the request.
- Decisions are not factual authority.
- Requirements cannot be downgraded into optional decisions.
- Actual future color/theme styling requires a typed deterministic visual-style contract; it is not free text.

## Request identity and lifecycle

- `requestId` and `diagramName` are required, globally unique for their identity, and immutable after first save.
- Authority mode/schema is immutable; direct and context requests never convert in place.
- Request path is exactly `.graphpilot/requests/<diagramName>.gp-request.json`.
- The generation LLM does not return or rename diagram identity.
- `diagram_request_save` performs complete replacement with expected-digest concurrency control.
- Before successful generation, the host may replace the request while framing/fixing it.
- After successful generation, the V1 generation workflow treats the request as finalized.
- Another diagram or authority mode creates a new request ID, name, request file, and diagram.
- Post-generation request editing/regeneration is deferred to the future edit workflow.
- Generation may create a target when absent or replace only a target owned by the same request ID.
- Name/ownership conflicts return safe alternatives and write nothing.
- Request save and diagram persistence are separate atomic operations; a failed generation leaves the saved request
  and any previous canonical diagram unchanged.
- Canonical metadata records request ID/path/digest rather than copying the complete request.

## Accepted bounds

Direct requests reuse the established context request limits:

```text
diagramName:      max 64, safe kebab-case
request.original: max 8,000
nonblank text:    max 2,000
included scope:   1..64
excluded scope:   0..64
requirements:     1..256
assumptions:      0..32
decisions:        0..64
IDs:              max 128 with typed prefixes
```

The complete generated LLM packet remains subject to a separate deployment token budget.

## `interactionPreference` exclusion

`interactionPreference` is a workflow-only argument. It affects host consultation but does not describe the
resulting design. It is not stored in this request and is not sent to the generator.

## Deterministic validation invariants — working set

1. Envelope constants match exactly.
2. Unknown top-level fields are rejected.
3. `diagramName` is an exact safe stem.
4. `request.original`, `goal`, and `audience` are nonblank and bounded.
5. `diagramType` is generatable.
6. `detailLevel` is a valid enum.
7. Included scope is nonempty; all entries are nonblank and unique.
8. Excluded entries are nonblank/unique and do not conflict with included scope.
9. Requirement IDs are unique; kinds are valid; statements are nonblank.
10. Assumption IDs are unique; authority fields/timestamps are valid; statement/reason are nonblank.
11. Decision IDs/kinds/authority fields are valid.
12. Mode, request ID, and diagram name match any existing request at the target path.
13. No evidence, claims, claim refs, provenance allowlists, source paths, or logical diagram elements appear.
14. Product bounds above are enforced.
15. A generated owned target finalizes the request against further V1 workflow replacement.

## Remaining specification work

- Formal JSON Schema and exact shared persistence validator composition.
- Exact timestamp/id regex reuse and conflict `OperationProblem` details.
- Final direct request summary/trace shape in generation results and canonical metadata.
- Future typed visual-style contract is explicitly deferred.
