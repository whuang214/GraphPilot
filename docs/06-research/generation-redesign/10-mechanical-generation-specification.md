# Mechanical Generation Specification

> **Status: mechanically specified under the user-approved generation-contract design; fresh-reader audit passed
> 2026-07-17.** The approved behavior is recorded in `generation-contract-approval.json`. This document converts it
> into implementation-facing schemas, prompts, bounds, errors, traces, fixture contracts, and proof gates. It is
> research authority only until reconciled and promoted into active GraphPilot owners together with evaluation design.

## Scope

This document specifies:

- persisted direct-request and shared request-save mechanics;
- direct/context LLM packets and six strict logical outputs;
- deterministic generation repair;
- semantic-review request, private response, deterministic result, and semantic repair;
- MCP generated/blocked/error results;
- optional compact trace sidecar and full numbered diagnostics;
- strict-provider and transport-safety behavior;
- PyGraphviz layout migration contract;
- training fixture/set metadata and verification gates.

It does not specify the held-out semantic matcher, evaluation decision report, implementation slices, or production
promotion. Those follow in the evaluation and migration blocks.

## Normative conventions

- JSON Schema draft is 2020-12 for persisted/backend contracts.
- `$id` equals document `schemaVersion` exactly.
- Every object rejects unknown fields unless explicitly stated otherwise.
- Every array and text field is bounded.
- Digests use lowercase `sha256:<64 lowercase hex>`.
- Timestamps use UTC RFC 3339 with `Z` and optional 1–6 fractional digits.
- Stable IDs use lowercase kebab case with typed prefixes and max length 128.
- LLM response schemas use Azure strict `json_schema`; all declared properties are required and optional values use
  nullable types or bounded empty arrays. Persisted/backend-only schemas are separate artifacts and may use ordinary
  optional fields; callers never pass those broader schemas to Azure.
- A provider/deployment that rejects strict structured output returns `structured_output_unsupported`; there is no
  `json_object` fallback.
- Canonical serialization uses UTF-8, sorted object keys, no insignificant whitespace, and a trailing newline only
  for persisted files.

## Shared lexical bounds

| Value | Contract |
| --- | --- |
| Diagram name | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, `1..64` |
| Request ID | `^request-[a-z0-9]+(?:-[a-z0-9]+)*$`, max 128 |
| Evidence ID | `^evidence-[a-z0-9]+(?:-[a-z0-9]+)*$`, max 128 |
| Claim ID | `^claim-[a-z0-9]+(?:-[a-z0-9]+)*$`, max 128 |
| Assumption ID | `^assumption-[a-z0-9]+(?:-[a-z0-9]+)*$`, max 128 |
| Decision ID | `^decision-[a-z0-9]+(?:-[a-z0-9]+)*$`, max 128 |
| Logical element ID | `^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$` |
| Nonblank contract text | `1..2,000`, contains non-whitespace |
| Original user request | `1..8,000`, contains non-whitespace |
| Logical label | `0..256`; nonblank for domain-bearing nodes |
| Model/prompt/schema/rubric ID | `1..128`, safe identifier characters |
| Operation code | lowercase snake case, `1..128` |
| Operation message | `1..2,000`, contains non-whitespace |

## Contract and file registry

### Persisted/domain contracts

| Artifact | Schema ID | Kind | Target file |
| --- | --- | --- | --- |
| Canonical diagram | `graphpilot.diagram.v1` | `diagram` | `schemas/diagram.json` |
| Context evidence manifest | `graphpilot.context.evidence-manifest.v1` | `evidenceManifest` | `schemas/context-evidence-manifest.json` |
| Context request (JSON 2) | `graphpilot.context.diagram-request.v1` | `contextDiagramRequest` | `schemas/context-diagram-request.json` |
| Direct request | `graphpilot.direct.diagram-request.v1` | `directDiagramRequest` | `schemas/direct-diagram-request.json` |

### Generation packets

| Artifact | Schema ID | Kind | Target file |
| --- | --- | --- | --- |
| Direct input | `graphpilot.direct.generation-input.v1` | `directGenerationInput` | `schemas/direct-generation-input.json` |
| Context input | `graphpilot.context.generation-input.v1` | `contextGenerationInput` | `schemas/context-generation-input.json` |
| Direct generation repair | `graphpilot.direct.generation-repair-input.v1` | `directGenerationRepairInput` | `schemas/direct-generation-repair-input.json` |
| Context generation repair | `graphpilot.context.generation-repair-input.v1` | `contextGenerationRepairInput` | `schemas/context-generation-repair-input.json` |

### Strict logical outputs

| Mode/type | Schema ID | Kind | Target file |
| --- | --- | --- | --- |
| Direct activity | `graphpilot.direct.logical-diagram.activity.v1` | `directLogicalDiagram` | `schemas/direct-logical-diagram-activity.json` |
| Direct use case | `graphpilot.direct.logical-diagram.use-case.v1` | `directLogicalDiagram` | `schemas/direct-logical-diagram-use-case.json` |
| Direct BDD | `graphpilot.direct.logical-diagram.bdd.v1` | `directLogicalDiagram` | `schemas/direct-logical-diagram-bdd.json` |
| Context activity | `graphpilot.context.logical-diagram.activity.v1` | `contextLogicalDiagram` | `schemas/context-logical-diagram-activity.json` |
| Context use case | `graphpilot.context.logical-diagram.use-case.v1` | `contextLogicalDiagram` | `schemas/context-logical-diagram-use-case.json` |
| Context BDD | `graphpilot.context.logical-diagram.bdd.v1` | `contextLogicalDiagram` | `schemas/context-logical-diagram-bdd.json` |

### Semantic review and repair

| Artifact | Schema ID | Kind | Target file |
| --- | --- | --- | --- |
| Direct review input | `graphpilot.direct.semantic-review-input.v1` | `directSemanticReviewInput` | `schemas/direct-semantic-review-input.json` |
| Context review input | `graphpilot.context.semantic-review-input.v1` | `contextSemanticReviewInput` | `schemas/context-semantic-review-input.json` |
| Direct private response | `graphpilot.direct.semantic-review-response.v1` | `directSemanticReviewResponse` | `schemas/direct-semantic-review-response.json` |
| Context private response | `graphpilot.context.semantic-review-response.v1` | `contextSemanticReviewResponse` | `schemas/context-semantic-review-response.json` |
| Direct review-response repair | `graphpilot.direct.semantic-review-repair-input.v1` | `directSemanticReviewRepairInput` | `schemas/direct-semantic-review-repair-input.json` |
| Context review-response repair | `graphpilot.context.semantic-review-repair-input.v1` | `contextSemanticReviewRepairInput` | `schemas/context-semantic-review-repair-input.json` |
| Direct deterministic result | `graphpilot.direct.semantic-review-result.v1` | `directSemanticReviewResult` | `schemas/direct-semantic-review-result.json` |
| Context deterministic result | `graphpilot.context.semantic-review-result.v1` | `contextSemanticReviewResult` | `schemas/context-semantic-review-result.json` |
| Direct semantic repair | `graphpilot.direct.semantic-repair-input.v1` | `directSemanticRepairInput` | `schemas/direct-semantic-repair-input.json` |
| Context semantic repair | `graphpilot.context.semantic-repair-input.v1` | `contextSemanticRepairInput` | `schemas/context-semantic-repair-input.json` |

### Results, trace, and diagnostics

| Artifact | Schema ID | Kind | Target file |
| --- | --- | --- | --- |
| Direct MCP result | `graphpilot.direct.generation-result.v1` | `directGenerationResult` | `schemas/direct-generation-result.json` |
| Context MCP result | `graphpilot.context.generation-result.v1` | `contextGenerationResult` | `schemas/context-generation-result.json` |
| Compact sidecar | `graphpilot.generation.trace.v1` | `generationTrace` | `schemas/generation-trace.json` |
| Debug run envelope | `graphpilot.generation.debug-run.v1` | `generationDebugRun` | `schemas/generation-debug-run.json` |
| Debug final result | `graphpilot.generation.debug-result.v1` | `generationDebugResult` | `schemas/generation-debug-result.json` |

### Examples and set manifests

| Artifact | Schema ID | Kind | Target file |
| --- | --- | --- | --- |
| Direct example | `graphpilot.direct.generation-example.v1` | `directGenerationExample` | `schemas/direct-generation-example.json` |
| Context example | `graphpilot.context.generation-example.v1` | `contextGenerationExample` | `schemas/context-generation-example.json` |
| Training set manifest | `graphpilot.generation.training-example-set.v1` | `generationTrainingExampleSet` | `schemas/generation-training-example-set.json` |
| Training fixture metadata | `graphpilot.generation.training-fixture-metadata.v1` | `generationTrainingFixtureMetadata` | `schemas/generation-training-fixture-metadata.json` |

### Versioned policy/configuration identities

These are immutable content identities recorded in packets/traces, not standalone runtime document schemas:

```text
graphpilot.generation.semantic-profile.activity.v1
graphpilot.generation.semantic-profile.use-case.v1
graphpilot.generation.semantic-profile.bdd.v1

graphpilot.generation.layout.activity.v1
graphpilot.generation.layout.use-case.v1
graphpilot.generation.layout.bdd.v1
```

A profile identity covers the exact ordered authorable vocabulary, semantic guidance, and deterministic structural
rules injected into both modes. A layout identity covers exact direction, node/rank gaps, node-sizing constants,
container padding/header, coordinate convention, and PyGraphviz engine configuration. Content change bumps only its
own identity; neither is a JSON Schema ID.

## Direct request

`graphpilot.direct.diagram-request.v1` requires:

```text
schemaVersion, kind, requestId, diagramName,
request, scope, requirements, assumptions, decisions
```

Bounds:

```text
request.original: 1..8,000
request.goal: 1..2,000
request.audience: 1..2,000
request.detailLevel: overview|standard|detailed
scope.included: 1..64 unique nonblank texts
scope.excluded: 0..64 unique nonblank texts
requirements: 1..256
assumptions: 0..32
decisions: 0..64
```

Requirement kinds are exactly:

```text
boundary, entity, capability, actorGoal,
relationship, behaviorStep, property, constraint
```

Every assumption/decision records typed ID, statement, nonblank reason, `origin=user|host`,
`acceptedBy=user|host`, and accepted UTC timestamp. Decision kinds are exactly
`emphasis|labeling|grouping|presentation`. No evidence/claim/provenance/style/logical fields are permitted.

Deterministic validation additionally enforces unique IDs, no included/excluded collision, no mandatory requirement
inside excluded scope, and mode/request/name immutability against any existing target.

## Generation input envelope

Direct and context inputs share this section order:

```text
contract identity
request/output identity
request and scope
mode-specific authority
assumptions and decisions
diagram model
mode-specific constraints
exact two examples
versions
```

### Direct generation input

Required fields:

```text
schemaVersion, kind, requestId, diagramName, diagramType,
request, scope, requirements, assumptions, decisions,
diagramModel, examples, versions
```

### Context generation input

Required fields:

```text
schemaVersion, kind, requestId, diagramName, diagramType,
request, scope, uncertaintyDispositions, selectedClaims,
assumptions, decisions, diagramModel, allowlists, examples, versions
```

The context input contains only selected exact claim meaning and required context roles, not raw source, complete
manifest, absolute paths, unselected claims, evidence records, or raw readiness output.

`diagramModel` requires exact profile version, ordered node/edge vocabulary, ordered semantic guidance, and ordered
structural rules. `examples` has exactly two validated objects in manifest order. `versions` requires exact prompt,
logical schema, semantic profile, example-set version, and example-set digest.

## Six logical outputs

All six strict outputs require exactly:

```text
schemaVersion, kind, nodes, edges
```

Shared generation-only bounds:

```text
nodes: 1..256
edges: 0..512
IDs: max 128
labels: max 256
use-case extension points: max 32
BDD properties/operations/receptions/constraints/literals: max 64 each
```

Activity permits only the approved eight node and two edge identities. Use case permits only actor/useCase/subject/
note and the five approved relationships. BDD permits only block/note and the five approved relationships. Each
schema excludes fields irrelevant to its type.

Context variants require an origin on every node and edge:

```text
claimRefs: 0..16
assumptionRefs: 0..8
schemaRules: 0..8
rationale: 1..2,000
```

At least one grounding source must validate deterministically. The only schema-rule ID is `activity.initial-node`,
valid only for a neutral initial node with label empty/Initial/Start and no domain-bearing fields. Unknown/duplicate/
mismatched rules or schema-only domain meaning produce the existing deterministic provenance issue codes
`unknown_schema_rule`, `duplicate_schema_rule`, `schema_rule_mismatch`, or `schema_only_domain_meaning`. They enter
context generation repair; if unresolved after budget, the operation returns `generation_provenance_failed`.

## Exact logical field matrices

Every property named below is required in the Azure strict LLM response object. Semantically optional scalars use
`null`; optional collections use bounded empty arrays. After strict decoding, GraphPilot projects into separately
versioned backend/persisted contracts, where ordinary optional fields may be omitted when their owner schema permits;
those broader schemas are never sent as Azure response formats. Unsupported Azure strict keywords (cross-item uniqueness by ID, endpoint membership, origin
at-least-one grounding, and graph topology) remain deterministic post-response validation.

### Activity logical node and edge

Node fields:

```text
id: logical ID
semanticType: exact activity node enum
label: string 0..256
joinSpec: string 1..256 or null; non-null only for joinNode
```

Edge fields:

```text
id, source, target: logical IDs
semanticType: controlFlow|commentLink
label: string 0..256 or null
guard: string 1..2,000 or null; required non-null on decision outgoing controlFlow
weight: finite number > 0 or null
```

Deterministic rules require one initial node, at least one activity final, valid reachability, distinct guarded
decision targets as allowed by current rules, correct merge/fork/join degrees, and comment links excluded from flow.

### Use-case logical node and edge

Node fields:

```text
id, semanticType, label
parentId: logical ID or null
extensionPoints: 0..32 unique nonblank strings
```

Edge fields:

```text
id, source, target
semanticType: association|generalization|include|extend|commentLink
label: string 0..256 or null
condition: string 1..2,000 or null
extensionLocations: 0..32 unique nonblank strings
```

Association endpoints must be actor/useCase; include/extend endpoints useCase/useCase; generalization connects same
node kinds specialized → parent. Extend source is extending use case, target is base, condition is non-null, and every
extension location exists on the target. Subject-contained use cases carry subject `parentId`; actors do not.

### BDD logical node and edge

Node fields:

```text
id
semanticType: block|note
label
stereotype: string 1..128 or null
features: {properties, operations, receptions, constraints, literals}
isAbstract: boolean or null
unit: string 1..128 or null
quantityKind: string 1..128 or null
constraintExpression: string 1..2,000 or null
constraintParameters: 0..64 parameters
```

All five feature arrays are required and each has max 64. Property kind is
`part|reference|value|constraint|flow`; name is nonblank max 256; type is max 256 or null; multiplicity is null or
`{lower: integer >=0, upper: integer >=lower | "*"}` where `"*"` is the exact JSON string literal for unbounded;
default is JSON scalar/null; direction is
`in|out|inout|null` and non-null only for flow. Operations have name, up to 64 parameters, nullable return type, and
nullable abstract/static/query flags. Constraints are `{name, expression}`; receptions/literals are nonblank text.

Edge fields:

```text
id, source, target
semanticType: association|composition|generalization|dependency|commentLink
label: string 0..256 or null
sourceEnd: relationship end or null
targetEnd: relationship end or null
```

Relationship ends contain nullable role/type/multiplicity/navigable/ordered/unique plus bounded qualifiers/property
path. Composition is part source → whole target; generalization child → parent; dependency client → supplier.

### Context origin addition

Every context node/edge adds required:

```text
origin.claimRefs: 0..16 unique exact {id, version}
origin.assumptionRefs: 0..8 unique assumption IDs
origin.schemaRules: 0..8 unique IDs
origin.rationale: nonblank 1..2,000
```

Deterministic validation requires at least one grounding array nonempty and all refs allowlisted. Only
`activity.initial-node` exists in V1 and only permits neutral initial label empty/Initial/Start with no domain-bearing
fields. Direct schemas reject `origin` entirely.

## Deterministic validation and generation repair

Strict schemas prevent wrong shape/vocabulary. Deterministic validation owns unique IDs, endpoints, containment,
type topology, multiplicities, and context reference allowlists. It never silently reverses, coerces, or drops
semantic elements.

Direct generation-repair input requires:

```text
schemaVersion, kind, originalGenerationInputDigest,
authority, previousLogicalDiagram,
validationIssues, structuralIssues,
repairRound, versions
```

Context additionally requires `provenanceIssues`. Issue arrays are ordered, unique by stable issue identity, and
bounded to 256. `repairRound` is `1..2`. Repair input omits examples and contains the same authority plus exact
previous candidate. Default budget is one round; unresolved defects return `generation_validation_failed` and no
canonical write.

## Semantic review contracts

Review input requires request ID, diagram type, generation-input/candidate digests, mode authority, normalized
candidate, final composed rubric, exact allowlists, and versions.

The private strict LLM response contains one ordered result for every rubric facet:

```text
facet, applicability, rating, rationale,
elementIds, requirementRefs or claimRefs,
assumptionRefs, findings
```

The response never contains severity, score, overall status, or acceptance. Backend validation rejects missing/
duplicate/unknown facets and references, validates conditional N/A, and bounds rationales/findings.

If the private response fails strict local facet/reference/cross-field validation, one contract-repair call receives
the identical semantic-review input, rejected response, and bounded ordered validation issues under the mode-specific
`semantic-review-repair-input.v1` contract. It must return the same private response schema. A second invalid response
returns `semantic_review_invalid`; an unfavorable but valid response is never contract-retried.

The deterministic result adds effective ratings, facet outcomes, severity, weighted score, clean|warnings|blocked,
validated actions, exact rubric version/digest, and candidate/input digests.

Semantic repair receives only same authority, previous normalized candidate, validated `repair_candidate` findings,
round, and exact versions. It omits examples and host-owned actions. Default budget is one round (`0..2`). Warnings
may persist after budget; blockers may not.

### Semantic finding and action registry

Reviewer-proposed finding codes are exactly:

```text
goal_mismatch
scope_violation
required_content_missing
authority_contradiction
authority_ambiguous
unsupported_addition
abstraction_mismatch
internal_incoherence
incorrect_element_meaning
incorrect_relationship_meaning
incorrect_topology
incorrect_structured_data
origin_not_relevant
origin_not_minimal
viewpoint_mismatch
```

Every proposed finding contains code, facet, `0..64` element IDs, mode-specific authority refs, bounded message, and
one resolution. The backend rejects a code unrelated to the rated facet, unknown/duplicate refs, or a finding without
a below-minimum facet. It assigns final IDs deterministically in rubric/finding canonical order:
`finding-<three digits>-<code>`.

Resolution kinds are:

```text
shared: repair_candidate, ask_user, report_warning
direct: revise_request
context: select_existing_claim, remove_selection, revise_context,
         replace_assumption_with_claim, search_source
```

Only `repair_candidate` enters semantic repair. `report_warning` is valid only for a deterministic warning. All other
resolutions return to the host. The private response has max 64 proposed findings; deterministic result/host actions
are deduplicated and bounded to 64/32 respectively.

## MCP result and error transport

Direct/context result schemas are discriminated by `outcome=generated|blocked`.

Generated results require diagram path, nullable SVG path, edit URL, request reference, compact generation summary,
quality summary, nullable trace path, nullable diagnostics descriptor, and ordered `operationWarnings`.

Blocked results require no diagram/SVG/edit/trace path and contain complete bounded quality findings plus typed host
`nextActions` and nullable diagnostics. Every block returns to the unified host workflow.

Operation errors remain the shared `OperationProblem` under top-level `error` with MCP `isError=true`. Enabled saved
diagnostics appear as a nullable sibling `diagnostics`, never inside code-specific details.

## Provider and transport safety

```text
outbound packet max: 16 MiB
raw response max: 8 MiB
debug artifact max: 16 MiB
debug run max: 128 MiB
```

Azure enforces token/context capacity. Provider context rejection maps to `llm_context_limit_exceeded`. GraphPilot
does not configure tokenizers/capacities/prices and never truncates authority/examples. Provider-reported token usage
is recorded when available.

Strict output support is mandatory. `structured_output_unsupported` is non-retryable until deployment configuration
changes. Transient timeout/rate/service errors are retryable; unchanged invalid candidates are never blind-rerolled.

### Generation operation code registry

| Code | Retryable | Meaning / required recovery |
| --- | ---: | --- |
| `llm_not_configured` | `false` | Configure endpoint/key/deployment before retry |
| `structured_output_unsupported` | `false` | Select a strict-schema-capable deployment/API |
| `llm_packet_size_exceeded` | `false` | Revise authority/input; local 16 MiB safety ceiling |
| `llm_context_limit_exceeded` | `false` | Revise input or deployment; do not reroll unchanged packet |
| `llm_response_size_exceeded` | `false` | Response exceeded 8 MiB safety ceiling |
| `llm_provider_unavailable` | `true` | Transient timeout/rate/service failure |
| `llm_refusal` | `false` | Report refusal; authority change required before another attempt |
| `generation_response_invalid` | `false` | Strict response could not be decoded/validated |
| `generation_validation_failed` | `false` | Deterministic defects remain after configured repair budget |
| `generation_provenance_failed` | `false` | Context origins remain invalid after configured repair budget |
| `semantic_reviewer_unavailable` | `true` | Transient reviewer deployment failure |
| `semantic_review_invalid` | `false` | Private response remains invalid after one contract-repair attempt |
| `semantic_repair_failed` | `false` | Candidate remains semantically blocked after budget |
| `layout_engine_unavailable` | `false` | PyGraphviz wheel/plugin unavailable |
| `layout_failed` | `false` | Native output malformed/incomplete/nonfinite |
| `request_conflict` | `true` | Reload/reconcile expected digest before resubmission |
| `generation_context_changed` | `true` | Reload JSON 1/2, rerun readiness, start new attempt |
| `diagram_name_conflict` | `true` | Host chooses safe alternate identity |
| `atomic_write_failed` | `true` | Persistence failed before canonical commit |

Valid semantic blockers are not operation codes; they return normal `outcome=blocked`. `trace_write_failed`,
`diagnostics_write_failed`, and `render_failed` are post/optional-operation warnings on otherwise successful or
blocked results and never replace the primary outcome. Retryability means a stated external/input recovery can make
a later attempt useful; it never authorizes automatic unchanged rerolls.

## Compact trace sidecar

When `persistGenerationTrace=true` and canonical persistence succeeds, GraphPilot atomically writes
`.graphpilot/diagrams/<name>.gp.trace.json`. It contains diagram digest/path, request/manifest refs, generation model
and versions, ordered example identity, repair counts, semantic-review/rubric/score summary, layout identity, and
provider usage. It excludes prompts, full rubrics, candidates, source, and finding rationales. Digest mismatch after
editing marks it historical. Failure returns `trace_write_failed` without undoing the diagram.

## Numbered diagnostics

When `persistGenerationDebug=true`, one run lives under
`.graphpilot/diagnostics/generation/<request-id>/<run-id>/` with stable stages `00` through `08`. Optional stages are
absent rather than renumbered. `00-run.json` and `08-result.json` are strict envelopes; intermediate JSON uses its
own exact stage contract. One collection README explains the structure. Diagnostics failure never changes the
primary generated/blocked/error result.

## Prompt/message registry

```text
graphpilot.generation.workflow-prompt.v1
graphpilot.direct.workflow-branch-prompt.v1
graphpilot.context.workflow-branch-prompt.v1
graphpilot.direct.generation-prompt.v1
graphpilot.context.generation-prompt.v1
graphpilot.direct.generation-repair-prompt.v1
graphpilot.context.generation-repair-prompt.v1
graphpilot.direct.semantic-review-prompt.v1
graphpilot.context.semantic-review-prompt.v1
graphpilot.direct.semantic-review-response-repair-prompt.v1
graphpilot.context.semantic-review-response-repair-prompt.v1
graphpilot.direct.semantic-repair-prompt.v1
graphpilot.context.semantic-repair-prompt.v1
```

Every backend LLM call uses exactly one system message, one canonical JSON user message, and one strict out-of-band
response schema. Exact texts and assertions follow.

## Exact prompt texts

All backend LLM prompts prohibit hidden reasoning/chain-of-thought and request concise user-facing rationales only
where the output schema requires them. They never ask the model to report confidence, acceptance, severity, score,
or final status owned by deterministic code.

### Direct generation system prompt

Prompt ID: `graphpilot.direct.generation-prompt.v1`.

```text
You are GraphPilot's direct logical-diagram generator.

Return exactly one JSON object matching the supplied strict direct logical-diagram schema. The canonical direct
generation input in the user message is your complete conceptual authority.

Use only the supplied request, included/excluded scope, mandatory requirements, accepted assumptions, decisions,
semantic vocabulary, guidance, structural rules, and two ordered examples. Conventional inference is allowed only
when it is non-material, consistent with that authority, and necessary for a coherent diagram. Do not invent or
claim repository facts, evidence, provenance, source identifiers, or origins. Decisions guide presentation and do
not authorize new domain facts.

Satisfy every mandatory requirement and exclusion. Use only semantic types and structured fields admitted by the
strict response schema. Every ID must be unique. Every edge endpoint and parent reference must name an emitted
node. Follow relationship direction, containment, multiplicity, decision, fork, join, and final-node rules exactly.
Use the examples to learn request-to-structure mapping, not to copy their domain content or IDs.

Return logical nodes and edges only. Do not return a diagram name, diagram type, coordinates, dimensions, styles,
layout instructions, metadata, prose, Markdown, code fences, or hidden reasoning. GraphPilot owns deterministic
validation, semantic review, layout, canonical assembly, persistence, and rendering.
```

### Context generation system prompt

Prompt ID: `graphpilot.context.generation-prompt.v1`.

```text
You are GraphPilot's repository-grounded logical-diagram generator.

Return exactly one JSON object matching the supplied strict context logical-diagram schema. The canonical context
generation input in the user message is your complete factual and modeling authority.

Use only selected exact claim meaning, accepted assumptions, decisions, supplied vocabulary/guidance/rules, and the
two ordered context-native examples. Do not infer from source files, evidence locators, paths, unselected claims, or
outside knowledge. Return sparse or unfavorable structure rather than inventing missing repository behavior,
identifiers, relationships, multiplicities, conditions, or outcomes. Decisions guide presentation and never become
factual authority.

Every node and edge must contain one complete origin. Cite only exact allowlisted claim versions, accepted assumption
IDs, or permitted schema-rule IDs. Use the smallest sufficient reference set and never cite every selected claim by
default. Schema rules authorize only the neutral scaffolding stated by their allowlist. Keep each rationale concise,
user-facing, and limited to the authority-to-element mapping; do not expose hidden reasoning.

Use only semantic types and fields admitted by the strict response schema. Every ID must be unique. Every endpoint
and parent reference must name an emitted node. Follow all relationship, containment, multiplicity, decision, fork,
join, and final-node rules exactly.

Return logical nodes and edges only. Do not return a name, diagram type, coordinates, dimensions, styles, layout,
metadata, prose, Markdown, or code fences. GraphPilot owns deterministic validation, semantic review, layout,
canonical assembly, persistence, and rendering.
```

### Direct deterministic-repair system prompt

Prompt ID: `graphpilot.direct.generation-repair-prompt.v1`.

```text
You are repairing a GraphPilot direct logical diagram after deterministic graph validation failed.

Return exactly one corrected JSON object matching the supplied strict direct logical-diagram schema. The user message
contains unchanged authority, the exact previous candidate, and validated ordered issues. Fix every issue with the
smallest change that preserves already-correct semantics and requirement coverage. Do not add new facts,
requirements, assumptions, decisions, evidence, provenance, or examples. Do not rename the request-owned target.
Do not silently substitute unrelated elements for invalid ones. Use only the supplied authority, vocabulary, and
structural rules.

Return logical nodes and edges only, with no prose, Markdown, code fences, layout, or hidden reasoning.
```

### Context deterministic-repair system prompt

Prompt ID: `graphpilot.context.generation-repair-prompt.v1`.

```text
You are repairing a GraphPilot repository-grounded logical diagram after deterministic graph or provenance
validation failed.

Return exactly one corrected JSON object matching the supplied strict context logical-diagram schema. The user
message contains unchanged authority/allowlists, the exact previous candidate, and validated ordered issues. Fix
every issue with the smallest change that preserves correct semantics and grounding. Do not add or reinterpret
claims, assumptions, decisions, source content, evidence, schema rules, or examples. Every node and edge must retain
a complete smallest-sufficient origin using only allowlisted references. Remove invalid or excessive citations rather
than replacing them with invented authority. Keep rationales concise and user-facing. Do not rename the target.

Return logical nodes and edges only, with no prose, Markdown, code fences, layout, or hidden reasoning.
```

### Direct semantic-review system prompt

Prompt ID: `graphpilot.direct.semantic-review-prompt.v1`.

```text
You are GraphPilot's direct semantic-candidate reviewer.

Evaluate the supplied normalized logical candidate against its direct authority and final composed rubric. Return
exactly one JSON object matching the strict direct semantic-review-response schema.

Review every rubric facet exactly once in canonical order. Follow each facet's always or conditional applicability
rule. Use only allowlisted candidate element IDs and requirement/assumption/decision IDs. Apply the shared 0..4
rating anchors exactly. Return concise user-facing rationales and typed proposed findings/actions. Do not optimize
for a passing result. Do not invent requirements, assumptions, decisions, repository facts, source grounding, IDs,
weights, thresholds, severity, score, acceptance, or overall status. Do not expose hidden reasoning.
```

### Context semantic-review system prompt

Prompt ID: `graphpilot.context.semantic-review-prompt.v1`.

```text
You are GraphPilot's context semantic-candidate reviewer.

Evaluate the supplied normalized logical candidate against selected exact claim meaning, accepted assumptions,
decisions, candidate origins, and the final composed rubric. Return exactly one JSON object matching the strict
context semantic-review-response schema.

Review every rubric facet exactly once in canonical order. Follow each facet's applicability rule. Use only
allowlisted element IDs, claim versions, assumption IDs, decision IDs, and schema rules. Evaluate selected-claim
coverage, origin relevance/minimality, grounding completeness, viewpoint fidelity, and diagram-type meaning. Apply
the shared 0..4 anchors exactly. Return concise user-facing rationales and typed findings/actions. Do not use raw
source or evidence records, invent repository facts/IDs, or report weights, thresholds, severity, score, acceptance,
or overall status. Do not optimize for a passing result or expose hidden reasoning.
```

### Semantic-review response-repair system prompts

Prompt IDs are `graphpilot.direct.semantic-review-response-repair-prompt.v1` and
`graphpilot.context.semantic-review-response-repair-prompt.v1`.

```text
You are repairing a GraphPilot semantic-review response that failed response-contract validation.

Return exactly one corrected JSON object matching the supplied strict mode-specific semantic-review-response schema.
The user message contains the identical review input, the rejected response, and bounded ordered validation issues.
Correct only response shape, missing/duplicate facets, applicability/rating/nullability, unknown references, and
finding/action contract defects. Preserve valid unfavorable judgments. Do not reevaluate the diagram, add authority,
change rubric policy, report severity/score/status, or expose hidden reasoning.
```

A private-response contract repair is distinct from semantic candidate repair and never changes the candidate.

### Direct semantic-repair system prompt

Prompt ID: `graphpilot.direct.semantic-repair-prompt.v1`.

```text
You are repairing a GraphPilot direct logical diagram from validated semantic-review findings.

Return exactly one corrected JSON object matching the supplied strict direct logical-diagram schema. Use unchanged
direct authority, the previous normalized candidate, and only findings whose resolution is repair_candidate. Make
the smallest change that resolves every supplied finding while preserving correct structure and meaning. You may use
non-material conventional inference already permitted by the request, but must not create material assumptions or
edit request authority. Do not add examples, evidence, claims, provenance, outside facts, prose, or hidden reasoning.
```

### Context semantic-repair system prompt

Prompt ID: `graphpilot.context.semantic-repair-prompt.v1`.

```text
You are repairing a GraphPilot repository-grounded logical diagram from validated semantic-review findings.

Return exactly one corrected JSON object matching the supplied strict context logical-diagram schema. Use unchanged
selected claims, accepted assumptions, decisions, allowlists, the previous normalized candidate, and only findings
whose resolution is repair_candidate. Make the smallest change that resolves every supplied finding while preserving
correct structure and smallest-sufficient grounding. Do not invent or retrieve authority, add examples, change the
request/context, use host-action findings, or expose hidden reasoning. Every node and edge must have a complete valid
origin using only allowlisted references.
```

### Unified host workflow prompt composition

Prompt ID: `graphpilot.generation.workflow-prompt.v1`.

The public MCP prompt renders one shared header plus exactly one selected internal branch template. The shared header
preserves `workspaceDir`, the verbatim request, `interactionPreference` (default balanced),
`persistGenerationTrace` (default false), and `persistGenerationDebug` (default false). It instructs the host to:

1. decide whether the requested result claims current managed source truth;
2. ask one focused authority question only when that distinction is ambiguous;
3. select one direct or context branch before authoring artifacts;
4. never mix requirements with claims or fall back from blocked context to direct;
5. execute typed actions at the owning stage and never blind-reroll unchanged input;
6. generate once after authority/readiness acceptance;
7. report mode, assumptions/acceptances, outcome, paths, compact trace, and warnings truthfully.

The direct branch builds/saves one complete direct request and calls `diagram_generate_direct`. The context branch
refreshes JSON 1, authors/saves JSON 2, runs readiness and typed improvement actions, chooses one accepted generation
policy, and calls `diagram_generate_from_context`. Prompt tests render all three authority outcomes and assert that
no unresolved template token, contradictory branch instruction, direct fallback, or missing debug/trace propagation
remains.

### Prompt verification

For every prompt:

- exact UTF-8 text and version are snapshot-tested;
- system text contains no user-controlled interpolation;
- user content is one canonical JSON string and round-trips to its formal schema;
- initial generation contains exactly two ordered examples;
- all repair/review packets contain no generation examples unless the owning contract explicitly requires them;
- strict response schema ID matches the input's declared response-schema version;
- output contains no prose/code fences in fake/live contract tests;
- role/model/prompt/schema/example/rubric versions are captured externally without secrets.

## Training fixture/set contract

Every approved fixture contains complete authority, expected logical gold, deterministic canonical/render proof, and
metadata. Context fixtures additionally contain evidence manifest, context request, and exact origins. Runtime
`{input, output}` pairs are derived and never independently edited.

Every fixture metadata object records ID, mode/type, foundational|advanced level, domain/structure tags, author,
distinct reviewer, approval timestamp, contract/profile versions, and input/output digests. Each of six immutable set
manifests contains mode/type plus exactly two ordered IDs/digests (foundational then advanced) and set digest.

Exact authority, topology, structured-field, origin, and verification intent for all twelve fixtures is owned by
[`11-training-fixture-specification.md`](11-training-fixture-specification.md). Actual source files are authored only
under its distinct author/reviewer and automated proof gates.

## PyGraphviz contract

### Engine and critical section

The pinned dependency is `pygraphviz==2.0`; the external identity is `pygraphviz-dot`. `PyGraphvizLayoutEngine`
implements the existing flat `LayoutEngine` seam. Every call creates a directed, non-strict `AGraph` so parallel
edges remain distinct. It sets `rankdir`, `nodesep`, `ranksep`, fixed box sizes, safe node tokens, and all source/
target pairs, then runs `layout(prog="dot")` through bundled libgvc.

A module-owned process-local `threading.Lock` covers the complete native lifecycle: graph creation, attribute/node/
edge mutation, `layout`, position/bounding-box reads, and `AGraph.close()` in `finally`. Input preparation and final
normalization remain outside the lock. The local-first V1 does not claim cross-process serialization; multi-process
hosting must prove native concurrency separately before support.

### Coordinate conversion

PyGraphviz node `pos` values and graph `bb` are Graphviz points with center coordinates and a bottom-left origin.
For graph bounding box `x0,y0,x1,y1`, node center `cx,cy`, and GraphPilot input size `width,height` in pixels at the
existing 72-points-per-inch convention:

```text
graphHeight = y1 - y0
x = cx - x0 - width / 2
y = graphHeight - (cy - y0) - height / 2
```

All values must be finite; every input node must have one position. The final map is normalized so its minimum corner
is `(0,0)`. The implementation must not treat PyGraphviz y as top-down or divide a point coordinate by 72 and then
multiply it back without applying the bounding-box flip.

### Containment and edges

Existing `DiagramLayoutService._position` remains the containment owner. It lays out children as flat TB graphs,
offsets them below the container header/padding, resizes the parent, remaps top-level layout edges to ancestors, and
returns child positions relative to parents. PyGraphviz never receives canonical nesting. Ports/pins remain outside
the generation core and do not expand migration scope.

Parallel edges are added with `strict=False` and remain separate layout constraints. GraphPilot still persists only
semantic source/target edges and computes its own connector routes; libgvc spline output is not canonical.

### Failure and trace behavior

Import/wheel/plugin failure returns `layout_engine_unavailable`; native layout failure, malformed/missing/nonfinite
positions, or malformed bounding box returns `layout_failed`. No other layout algorithm is attempted after cutover.
Errors expose bounded safe details without raw native stack traces or local library paths.

Compact MCP/sidecar/debug traces may record:

```text
engine: pygraphviz-dot
pygraphvizVersion
runtimePlatform: windows-x64 | macos-x64 | macos-arm64 | linux-x64 | linux-aarch64
emulation: null | windows-x64-on-arm64
layoutConfigurationVersion: graphpilot.generation.layout.<type>.v1
nodeCount
edgeCount
durationMs
```

None is copied into canonical diagram JSON.

### Platform policy

PyGraphviz 2.0 binary wheels cover Windows x64, macOS x64/ARM64, and Linux x64/AArch64 for supported Python
versions. Windows ARM64 V1 runs the packaged x64 GraphPilot/Python runtime under Windows emulation and records
`runtimePlatform=windows-x64`, `emulation=windows-x64-on-arm64`; native Windows ARM64 Python is deferred.
Source-building PyGraphviz is not an automatic fallback.

### Verification and cutover

1. Add PyGraphviz and the new engine without changing the default; unit-test graph construction, point/bounding-box
   conversion, missing nodes, malformed/nonfinite data, parallel edges, empty graphs, and guaranteed close-on-error.
2. Run deterministic repeatability, containment, direction, gap, no-overlap, 256-node boundary, parallel-edge, and
   10-thread serialization stress tests. Compare old/new with structural/geometric invariants and reviewed galleries,
   not a universal one-pixel coordinate equality claim across different Graphviz builds.
3. Run all current examples plus the twelve approved new fixtures through conform → layout → canonical validation →
   canvas/SVG render parity. Record accepted snapshot deltas and platform/wheel identities.
4. Switch the default to PyGraphviz with typed failure and no fallback. Keep the old engines in the immediately prior
   coherent commit as the rollback boundary while the full backend/frontend gates run.
5. Only after cutover verification remove `GraphvizLayoutEngine`, `GrandalfLayoutEngine`, `resolve_dot_path`,
   `GRAPHVIZ_DOT_PATH`, `backend/.graphviz/`, `grandalf`, subprocess/parser tests, old setup docs, and silent fallback.
   No `GRAPHPILOT_LAYOUT_ENGINE` environment switch is introduced.

Activity remains TB with horizontal fork/join bars. Per-diagram LR/vertical bars and mixed local orientations remain
future presentation/layout design.

## Mechanical proof gate

Before this document becomes specified:

1. Every listed schema has one exact valid and invalid worked example.
2. Every `$id`, `schemaVersion`, kind, prompt/rubric/example version, file path, and registry entry is unique.
3. Six logical schemas validate only their current authorable vocabularies.
4. Direct rejects origins; context requires/validates origins.
5. Initial packets contain exactly two manifest-ordered examples; repair packets contain none.
6. Strict-output unsupported behavior has no fallback call.
7. Deterministic and semantic repair budgets/issue order are testable and bounded.
8. Generated/blocked/error result matrices validate, including trace/debug failures.
9. PyGraphviz produces deterministic parity for approved fixtures and passes concurrency/platform gates.
10. Twelve fixture sources derive exact runtime pairs and canonical/render outputs with distinct sign-off.

## Post-promotion implementation artifacts

The behavior/interfaces in this document are specified. Implementation must create and verify:

- exact backend JSON Schema files plus valid/invalid worked artifacts;
- semantic-review calibration fixtures and measured release targets under the evaluation framework;
- twelve training source files with distinct author/reviewer sign-off under `11`;
- provider strict-schema compatibility tests and PyGraphviz platform/parity evidence.

These artifacts may reveal a local defect, but do not reopen approved behavior without user request or new conflicting
evidence.
