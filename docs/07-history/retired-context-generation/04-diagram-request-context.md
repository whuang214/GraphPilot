# JSON 2 — Diagram Request Context

## Purpose

The diagram request context is a bounded packet for one repository-backed diagram: what the user wants shown, which exact JSON 1 claim versions to use, how relevant uncertainty is handled, and which accepted diagram-only assumptions or non-factual decisions guide generation.

The host owns request framing and writes every JSON 2 entry from user intent and repository context. It may provide an initial claim selection or an empty one. The readiness reviewer may recommend validated additions/removals from JSON 1, but the host decides, applies, and persists every change; the backend never silently mutates JSON 2.

JSON 2 is not a second knowledge base. It references exact claim versions in the persistent [JSON 1 manifest](03-evidence-manifest.md) without copying statements, payloads, support objects, or evidence and binds to one exact manifest digest.

It persists beside direct requests at the shared request path:

```text
.graphpilot/requests/<diagramName>.gp-request.json
```

The host saves the complete packet through `diagram_request_save` with expected-digest concurrency control. Before successful generation, the same mode, `requestId`, and `diagramName` may be replaced while the host resolves readiness findings. Successful generation finalizes the V1 request; post-generation request editing or regeneration requires the future edit workflow and does not mutate this request in place. It is not internally versioned and has no persisted generation-snapshot companion. The canonical diagram retains minimal request/manifest ownership plus element origins; an optional digest-bound generation trace is a separate sidecar. Lifecycle belongs to the [workflow](02-workflow.md), and result/trace/provenance behavior belongs to [generation and provenance](05-generation-and-provenance.md).

## Simple complete example

```json
{
  "schemaVersion": "graphpilot.context.diagram-request.v1",
  "kind": "contextDiagramRequest",
  "requestId": "request-order-processing",
  "diagramName": "order-processing",
  "manifestRef": {
    "path": ".graphpilot/context/evidence/repository.gp-evidence.json",
    "id": "evidence-order-service",
    "digest": "sha256:47a52f748ddc29477df0c435b6dfafcb2dbacd19f96dc177f6cbc9f6a6d1223d"
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
  "schemaVersion": "graphpilot.context.diagram-request.v1",
  "kind": "contextDiagramRequest",
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

| Section | Question it answers |
| --- | --- |
| document envelope | Which request contract and stable request own this packet, and what output stem does it use? |
| `manifestRef` | Which exact JSON 1 manifest must GraphPilot resolve? |
| `request` | What diagram did the user ask for and for whom? |
| `scope` | What should the diagram include and deliberately omit? |
| `selectedClaims` | Which exact supported fact versions should readiness and generation consider? |
| `uncertaintyDispositions` | How does each relevant unresolved JSON 1 question affect this diagram? |
| `assumptions` | Which narrow unsupported propositions were accepted, and who originated/accepted them? |
| `decisions` | Which non-factual emphasis, labeling, grouping, or presentation choices guide modeling? |

## 1. Document envelope

```json
{
  "schemaVersion": "graphpilot.context.diagram-request.v1",
  "kind": "contextDiagramRequest",
  "requestId": "request-order-processing",
  "diagramName": "order-processing"
}
```

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `schemaVersion` | Yes | Constant identifying the packet format. | Selects deterministic validation and future migration. |
| `kind` | Yes | Constant identifying diagram request context. | Distinguishes JSON 2 from JSON 1, transient resolved context, and diagrams. |
| `requestId` | Yes | Stable identity tying the packet to one diagram. | Correlates assessment/generation and authorizes identity-aware canonical replacement. |
| `diagramName` | Yes | Host-proposed, backend-validated safe filename stem. | Deterministically names `.graphpilot/diagrams/<diagramName>.gp.json` and siblings without accepting an Azure rename. |

Constants:

| Field/value | Meaning |
| --- | --- |
| `schemaVersion: graphpilot.context.diagram-request.v1` | First GraphPilot request-context contract. |
| `kind: contextDiagramRequest` | Selects JSON 1 facts for one diagram; it is neither evidence nor a diagram. |

`requestId` is stable and immutable for the request. `diagram_request_save` may replace a pre-generation packet only when mode, request ID, and diagram name match and the caller supplies the exact current digest. Successful V1 generation finalizes the request; a later revised diagram starts from a new request under the future edit/regeneration design. Request identity also protects diagram persistence: no operation may replace `.graphpilot/diagrams/<diagramName>.gp.json` unless its stored request identity matches.

`requestId` uses `^request-[a-z0-9]+(?:-[a-z0-9]+)*$` and is at most 128 characters. `diagramName` is authoritative, uses `^[a-z0-9]+(?:-[a-z0-9]+)*$`, and is at most 64 characters. It contains no path or extension and is already a validated filename stem rather than input to a lossy sanitizer. A request filename normally mirrors it for readability, but identity is not inferred from that filename and Azure cannot rename it.

## 2. `manifestRef`

```json
{
  "manifestRef": {
    "path": ".graphpilot/context/evidence/repository.gp-evidence.json",
    "id": "evidence-order-service",
    "digest": "sha256:47a52f748ddc29477df0c435b6dfafcb2dbacd19f96dc177f6cbc9f6a6d1223d"
  }
}
```

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `manifestRef.path` | Yes | Workspace-relative path to JSON 1. | Lets GraphPilot load it through the path-safe file boundary. |
| `manifestRef.id` | Yes | Expected stable JSON 1 identity. | Detects a path resolving to the wrong manifest. |
| `manifestRef.digest` | Yes | Expected exact JSON 1 digest. | Prevents assessment/generation from using another knowledge state. |

Manifest revision is omitted because digest supplies the exact binding; diagnostics may report revision separately. Canonical metadata records the exact manifest path, ID, and digest used without copying manifest content.

The digest is checked at two moments:

- **On load:** if current JSON 1 differs, reconcile rather than discard. Reverify selected exact claim versions and every uncertainty disposition; flag claims that became inactive or changed and uncertainty refs that are no longer open. The host must update the packet before rebinding. A stale `assume` pair is never silently promoted: replace it with a verified active claim supporting the same proposition or restore/record an open uncertainty if still unsupported. Ambiguous replacements require user confirmation.
- **Immediately before generation:** GraphPilot re-resolves and revalidates JSON 1 and requires JSON 2's manifest ID/digest to match. Generation refuses another knowledge state, and success copies the exact binding into minimal canonical ownership metadata and the optional trace sidecar.

## 3. `request`

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

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `original` | Yes | User's original wording without semantic rewrite. | Retains intent for review, generation, and reconciliation. |
| `goal` | Yes | Concise normalized desired outcome. | Gives review/generation one clear objective. |
| `diagramType` | Yes | Confirmed generatable GraphPilot type. | Selects readiness rubric and generation profile. |
| `audience` | Yes | Bounded intended-reader description. | Guides abstraction, terminology, and sufficiency. |
| `detailLevel` | Yes | Requested abstraction/detail level. | Bounds selection and avoids code-level inventories. |

### Diagram-type enum

| Value | Meaning |
| --- | --- |
| `activity_diagram` | Model a bounded behavior or workflow. |
| `use_case_diagram` | Model actors, system boundaries, and user-visible goals. |
| `bdd_diagram` | Model SysML block/domain structure, properties, and relationships. |

`custom` is excluded because context-backed generation requires a concrete per-type readiness rubric and generation profile. `custom` remains a save/edit canvas, not a generated type.

### V1 viewpoint

JSON 2 has no `viewpoint` field. Repository-derived v1 diagrams depict `as_implemented`. Support for `as_designed` and `as_required` request viewpoints is deferred to later request versions; JSON 1 retains claim `appliesToViewpoints` as latent metadata so that extension does not change JSON 1. An accepted assumption is not a viewpoint switch; it is an unsupported diagram-only proposition, not evidence of intended design.

### Detail-level enum

| Value | Meaning |
| --- | --- |
| `overview` | Main boundary, actors/components, and principal relationships or steps only. |
| `standard` | Enough structure/behavior to explain the requested subject without private implementation detail. |
| `detailed` | Supported secondary paths/features relevant to confirmed scope, still excluding incidental helpers. |

## 4. `scope`

```json
{
  "scope": {
    "included": ["Order submission through event publication"],
    "excluded": [
      "Frontend behavior",
      "Background consumer processing"
    ]
  }
}
```

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `scope.included` | Yes; non-empty | Bounded subjects, flows, boundaries, or structures to cover. | Defines the semantic boundary for selection and readiness. |
| `scope.excluded` | Yes; may be empty | Explicitly omitted subjects that could appear relevant. | Prevents scope expansion and records deliberate omission. |

Scope statements are request-specific and may use user language. They never become JSON 1 claims. Excluding a known fact from this diagram does not dispute or retire it. This top-level section is the sole v1 semantic scope authority: the host may propose it, the user confirms it, and later scope changes edit this section rather than creating a second scope instruction in `decisions`.

## 5. `selectedClaims`

Selection is backend-assisted, not host-only. The host may submit an informed first pass or an empty array. Readiness loads complete JSON 1 locally, reviews a bounded active-claim index, and returns validated add/remove recommendations. The host applies accepted changes and persists them. The reviewer never silently mutates JSON 2, and the generator never receives the full manifest.

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

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `claimRef.id` | Yes | Stable JSON 1 claim ID. | Identifies the reusable fact. |
| `claimRef.version` | Yes | Exact immutable claim version. | Prevents manifest updates changing packet meaning. |
| `role` | Yes | Selection role in this request. | Distinguishes facts driving the model from supporting context. |
| `reason` | Yes | Concise relevance explanation. | Lets readiness detect over-selection, omission, and abstraction errors. |

### Selection-role enum

| Value | Meaning |
| --- | --- |
| `primary` | Directly describes something the diagram should communicate. |
| `supporting` | Connects, constrains, or disambiguates primary facts. |
| `context` | Supplies terminology, purpose, or boundary context without necessarily becoming an element. |

Normal v1 requests select only an `active` claim's `currentVersion`. Historical selection is deferred. Because v1 depicts `as_implemented`, selection has no request viewpoint filter. `as_designed`/`as_required` claims are retained but are not normally selected.

The set must be semantically closed enough to interpret structured payload references. Readiness returns every required unselected payload claim reference as a deterministic `context` selection recommendation; GraphPilot never silently adds it. Exact closure behavior belongs to [readiness](01-readiness/02-reviewer.md).

## 6. `uncertaintyDispositions`

JSON 1 retains only currently open uncertainties. JSON 2 records how the relevant subset affects this diagram.

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

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `uncertaintyRef` | Yes | ID of a currently open JSON 1 uncertainty. | Connects request handling to the reusable gap. |
| `disposition` | Yes | How this diagram treats it. | Makes omission, blocking, assumption, and deferral explicit. |
| `reason` | Yes | Request-specific rationale. | Lets readiness judge acceptability. |
| `assumptionRef` | When `assume` | Corresponding packet assumption ID. | Prevents “handled” without an explicitly accepted proposition. |

### Disposition enum

| Value | Meaning | Generation consequence |
| --- | --- | --- |
| `block` | Must be resolved before a trustworthy diagram. | Always blocks. |
| `exclude` | Uncertain subject is outside confirmed scope. | Allowed only when scope and readiness make exclusion coherent. |
| `assume` | An accepted diagram-only proposition fills the gap. | May proceed with visible assumption provenance and readiness limits. |
| `defer` | Advisory gap does not affect required in-scope content. | May proceed only when readiness classifies it non-blocking. |

Not every manifest uncertainty must appear—only relevant ones. Readiness may identify an omitted relevant uncertainty. `uncertaintyRef`s are unique. An `assume` disposition and assumption form a one-to-one pair; other dispositions cannot carry `assumptionRef`.

## 7. `assumptions`

An assumption is one exact, narrow, unsupported factual proposition formulated from user intent and/or incomplete context and accepted for this diagram to resolve one open JSON 1 uncertainty. It is not omission, scope, a presentation default, or a weakly supported claim; those belong to `exclude`/`defer`, `scope`, `decisions`, or JSON 1. Assumptions never become evidence or claims.

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

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `id` | Yes | Packet-local stable assumption ID. | Supports readiness and element provenance. |
| `statement` | Yes | Exact unsupported diagram-only proposition. | Makes unsupported content visible and bounded. |
| `reason` | Yes | Why it is needed. | Makes acceptability reviewable. |
| `origin` | Yes | Actor whose input principally produced the exact proposition: `user` or `host`. | Distinguishes user input from host formulation. |
| `acceptedBy` | Yes | Actor accepting use: `user` or `host`. | Separates semantic source from authority. |
| `acceptedAt` | Yes | UTC time the host recorded acceptance. | Preserves the authority event in the persisted request. |

The host is always the writer, so `recordedBy` is omitted. `origin` describes semantic source. `origin: "user"` requires `acceptedBy: "user"`; a host-formulated assumption may be accepted by host or user. A bounded self-accepted assumption records `origin: "host"`, `acceptedBy: "host"`, and acceptance time.

Every assumption is referenced by exactly one `assume` disposition; standalone or shared assumptions are invalid. Evidence may motivate the linked uncertainty but does not support the assumption. JSON 2 contains accepted assumptions only. Readiness validates the shape/provenance but does not re-evaluate consultation that occurred before persistence. If evidence later supports the proposition, the host selects the claim and removes the paired assumption/disposition. Generated elements affected by the assumption retain its ID rather than a fabricated claim ref.

## 8. `decisions`

Decisions guide non-factual emphasis and presentation without claiming repository truth or filling uncertainty.

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

| Field | Required | Meaning | Why it exists |
| --- | --- | --- | --- |
| `id` | Yes | Packet-local stable decision ID. | Keeps guidance traceable when copied into canonical metadata. |
| `kind` | Yes | Request-specific guidance category. | Keeps decisions bounded and reviewable. |
| `statement` | Yes | Concise assessment/modeling instruction. | Communicates choice without pre-building topology. |
| `reason` | Yes | Why the choice helps. | Detects arbitrary/conflicting guidance. |
| `origin` | Yes | Actor principally producing the exact decision: `user` or `host`. | Separates semantic origin from acceptance. |
| `acceptedBy` | Yes | Actor accepting it: `user` or `host`. | Prevents a host default masquerading as user intent. |
| `acceptedAt` | Yes | UTC time acceptance was recorded. | Preserves the authority event in the persisted request. |

### Decision kind and authority

| Kind | Meaning | Allowed `acceptedBy` |
| --- | --- | --- |
| `emphasis` | Make a supported fact/path/relationship prominent. | `user` |
| `labeling` | Guide terminology while remaining traceable to facts. | `user`, or `host` for a reversible fact-preserving default |
| `grouping` | Request conceptual grouping without final UML/SysML types. | `user` |
| `presentation` | Non-semantic visual guidance such as orientation or density. | `user`, or `host` for a reversible default |

`origin` may be either actor for every kind. A host-formulated choice requiring user authority records `origin: "host"`, `acceptedBy: "user"`. The reviewer/backend may recommend an action but is never a persisted accepting actor. `scope` is not a decision kind; scope changes update top-level `scope`.

A host-accepted decision must be reversible, compatible with the request, and unable to add factual meaning. A user-accepted decision overrides a conflicting host default. Decisions must not contain unsupported facts, final node/edge IDs, coordinates, GraphPilot `semanticType`s, or a complete topology. Backend modeling remains authoritative.

## 9. Assessment and generation boundary

JSON 2 embeds no readiness result. [Readiness](01-readiness/README.md) owns review and policy. Assessment and generation treat the loaded packet as immutable. Generation deterministically populates exact selected JSON 1 claim versions and evidence in memory only. Canonical output stores minimal request/manifest ownership and element origins; complete readiness and quality summaries remain in the tool result, and optional version/model/usage detail belongs to the separate trace sidecar. The full behavior is [generation and provenance](05-generation-and-provenance.md).

The packet must revalidate against the current JSON 1 ID/digest before assessment and before any generation call. GraphPilot derives the canonical request digest for expected-digest saves, mid-call stability, results, and trace binding; it does not create packet-internal revision history.

## 10. Validation invariants

The schema and services enforce:

1. envelope constants are exact and `requestId` obeys its role prefix, grammar, and bound;
2. `diagramName` obeys its exact kebab grammar and 64-character bound and contains no path or extension;
3. `manifestRef.path` is the exact canonical v1 evidence path;
4. referenced JSON 1 exists, validates, and matches both `id` and canonical `digest`;
5. `diagramType` is one of the three generatable concrete types;
6. request goal, audience, included scope, and detail level are present and bounded;
7. selected claim refs are unique and identify existing immutable versions;
8. normal v1 selection uses active claims at `currentVersion`;
9. every selection has a valid role and non-empty relevance reason;
10. uncertainty disposition refs are unique and identify currently open JSON 1 uncertainties;
11. every `assume` disposition references exactly one existing packet assumption, while `assumptionRef` is forbidden for every other disposition;
12. every assumption is referenced by exactly one `assume` disposition; standalone/shared assumptions are invalid;
13. assumption/decision `origin` and `acceptedBy` are `user` or `host`, and `origin: "user"` requires `acceptedBy: "user"`;
14. no assumption duplicates meaning already supported by a current active claim; readiness performs this semantic check;
15. origin/acceptance actors are provenance only; readiness validates shape without re-approving prior consultation;
16. `block` dispositions prevent generation;
17. assumption and decision IDs are unique within the packet;
18. decisions use only bounded kinds, actors, and kind/authority combinations;
19. host-accepted decisions are reversible and fact-preserving and never fill uncertainty or authorize unsupported facts;
20. top-level `scope` is the only v1 semantic scope authority, and `scope` is not a decision kind;
21. JSON 1 evidence/claim bodies are not duplicated into persisted JSON 2;
22. raw repository content and discovery output never appear;
23. GraphPilot semantic types, logical/canonical nodes and edges, coordinates, and rendering data never appear;
24. assessment, population, and generation do not mutate the loaded packet;
25. changed manifest digest on load triggers claim/disposition reconciliation; a stale assumption pair is removed only through explicit claim replacement or renewed uncertainty, and generation refuses a still-mismatched packet;
26. context generation receives this packet through the canonical workspace/path transport while runtime population remains transient;
27. every timestamp is a valid UTC `Z` instant and every string, array, integer, and decoded file stays within the
    v1 bounds;
28. the derived request digest matches the shared canonical JSON v1 algorithm;
29. `diagram_request_save` complete replacement is validation-gated, expected-digest checked, and atomic;
30. mode, `requestId`, and `diagramName` are immutable, and successful generation finalizes the request against further V1 replacement; and
31. any permitted diagram replacement requires the same stored request identity.

## 11. User-answer routing

The [workflow routing table](02-workflow.md#user-answer-routing) is authoritative for whether a response becomes factual JSON 1 clarification or JSON 2 scope, disposition, assumption, or decision.

## 12. Deliberately not stored in JSON 2

- evidence records or raw source;
- duplicated claim statements, payloads, or support objects;
- repository source fingerprints or discovery indexes;
- manifest or claim history;
- unresolved facts promoted into claims;
- final GraphPilot node/edge semantic types;
- logical or canonical nodes and edges;
- coordinates, sizes, styles, or rendering data;
- embedded readiness results;
- an internal revision chain, resolved/populated claim bodies, or per-attempt history;
- generated names supplied by Azure in place of authoritative `diagramName`; or
- secrets, credentials, `.env` values, or unbounded excerpts.

## 13. V1 machine contract

JSON 2 reuses the JSON 1 owner's [canonical JSON, digest, path, and timestamp rules](03-evidence-manifest.md#14-v1-machine-contract).
Its canonical digest covers the complete packet because JSON 2 has no internal `digest` field. The persisted file
uses the same two-space UTF-8/LF/final-newline format. `manifestRef.digest` and every calculated request digest
use `^sha256:[0-9a-f]{64}$`; `manifestRef.path` is the exact v1 canonical path
`.graphpilot/context/evidence/repository.gp-evidence.json`.

Packet-local identifiers are at most 128 characters and use exact role prefixes:

| Role | Pattern |
| --- | --- |
| request | `^request-[a-z0-9]+(?:-[a-z0-9]+)*$` |
| assumption | `^assumption-[a-z0-9]+(?:-[a-z0-9]+)*$` |
| decision | `^decision-[a-z0-9]+(?:-[a-z0-9]+)*$` |

Referenced manifest, claim, and uncertainty IDs use their JSON 1 patterns. `diagramName` uses
`^[a-z0-9]+(?:-[a-z0-9]+)*$`, is at most 64 characters, and is rejected rather than normalized when invalid.

Bounds are compatibility floors and may only increase within v1:

| Value | V1 maximum |
| --- | ---: |
| `request.original` | 8,000 characters |
| goal, audience, scope item, selection/disposition reason, assumption/decision statement or reason | 2,000 characters |
| included scope items | 64 |
| excluded scope items | 64 |
| selected claims | 256 |
| uncertainty dispositions | 256 |
| accepted assumptions | 32 |
| decisions | 64 |
| decoded canonical JSON 2 file | 5 MiB |

All arrays whose entries carry IDs or refs reject duplicates. Prose is non-empty after trimming. The schema keeps
`grouping` decisions as bounded text; it adds no topology, node/edge ID, coordinate, or semantic-type field.
Whether prose attempts to smuggle unsupported facts or a completed topology is a readiness judgment, not a
second hidden parser in schema validation.

`diagram_request_save` requires a null expected digest only for first creation and the exact current canonical digest
for update. An existing pre-generation request can be replaced only by the same context mode, `requestId`, and
`diagramName`. After validation and binding, content with the same canonical digest is a successful no-op and performs
no write. Changed content is rechecked immediately before atomic replacement. Once an owned canonical diagram has
been generated successfully, the request is finalized and further V1 replacement is rejected. On load/save, a
manifest ID/digest mismatch reports reconciliation required and never silently rewrites `manifestRef`, selections,
dispositions, assumptions, or decisions.

The on-load reconciliation result and action transport remain owned by readiness and MCP slices; they are not
persisted in JSON 2 and therefore are not part of this schema.

> The context diagram request is a per-diagram, manifest-bound JSON packet persisted through the shared request service. It names the target diagram, states one confirmed goal/scope, carries a backend-assisted exact claim selection, relevant uncertainty dispositions, accepted assumptions, and non-factual modeling/presentation decisions without copying evidence, exposing GraphPilot semantic types, or pre-building the diagram; successful generation finalizes the V1 request.
