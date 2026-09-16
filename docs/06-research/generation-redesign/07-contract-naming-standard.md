# JSON Contract and Version Naming Standard

> **Status: accepted.** Apply once as a cold-turkey V1 migration during promotion/implementation. This research
> record does not itself rename runtime contracts.

## Grammar

```text
graphpilot.<namespace>.<artifact>.v<major>
```

- `direct` and `context` namespaces own mode-specific contracts;
- `generation` owns cross-mode workflow contracts;
- namespace components use lowercase words separated by periods;
- compound artifact/type words use hyphens;
- version suffix is `.vN`;
- no dates, environments, model names, deployments, or hashes;
- canonical final diagram keeps the shared `graphpilot.diagram.v1` ID.

Examples:

```text
graphpilot.context.generation-input.v1
graphpilot.direct.generation-input.v1

graphpilot.context.logical-diagram.activity.v1
graphpilot.direct.logical-diagram.bdd.v1
```

## Scope

Applies to persisted GraphPilot context documents, transient projections, LLM input/output contracts, repair and
review packets, diagnostics, rubrics, rating scales, prompt versions, and example-set versions. It does not rename
node/edge/claim/assumption IDs, digests, fixture names, model names, or arbitrary metadata.

## Canonical diagram

Keep unchanged:

```text
schemaVersion/$id: graphpilot.diagram.v1
kind: diagram
```

It is shared by direct, context, editor, API, MCP, and import/save workflows.

## Existing contract migration

| Current | Target |
| --- | --- |
| `graphpilot.evidence.v1` | `graphpilot.context.evidence-manifest.v1` |
| `graphpilot.diagram-request.v1` | `graphpilot.context.diagram-request.v1` |
| `graphpilot.resolved-diagram-request.v1` | `graphpilot.context.resolved-request.v1` |
| `graphpilot.readiness-input.v1` | `graphpilot.context.readiness-input.v1` |
| `graphpilot.context-readiness-review.v1` | `graphpilot.context.readiness-review.v1` |
| `graphpilot.context-readiness.v1` | `graphpilot.context.readiness-result.v1` |
| `graphpilot.readiness-debug.v1` | `graphpilot.context.readiness-debug.v1` |
| `graphpilot.context-generation-input.v1` | `graphpilot.context.generation-input.v1` |
| `graphpilot.logical-diagram.context.v1` | six per-mode/per-type logical IDs listed below |
| `graphpilot.diagram.v1` | unchanged |

## Direct contracts

| Artifact | Schema ID | Kind |
| --- | --- | --- |
| Host-authored request | `graphpilot.direct.diagram-request.v1` | `directDiagramRequest` |
| Generator input | `graphpilot.direct.generation-input.v1` | `directGenerationInput` |
| Logical outputs | `graphpilot.direct.logical-diagram.activity.v1`; `.use-case.v1`; `.bdd.v1` | `directLogicalDiagram` |
| Generation repair input | `graphpilot.direct.generation-repair-input.v1` | `directGenerationRepairInput` |
| Semantic review input | `graphpilot.direct.semantic-review-input.v1` | `directSemanticReviewInput` |
| Semantic review response | `graphpilot.direct.semantic-review-response.v1` | `directSemanticReviewResponse` |
| Semantic review-response repair input | `graphpilot.direct.semantic-review-repair-input.v1` | `directSemanticReviewRepairInput` |
| Semantic review result | `graphpilot.direct.semantic-review-result.v1` | `directSemanticReviewResult` |
| Semantic repair input | `graphpilot.direct.semantic-repair-input.v1` | `directSemanticRepairInput` |
| Generation result | `graphpilot.direct.generation-result.v1` | `directGenerationResult` |
| Generation example | `graphpilot.direct.generation-example.v1` | `directGenerationExample` |

## Context contracts

| Artifact | Schema ID | Kind |
| --- | --- | --- |
| Evidence manifest | `graphpilot.context.evidence-manifest.v1` | `evidenceManifest` |
| Diagram request | `graphpilot.context.diagram-request.v1` | `contextDiagramRequest` |
| Local resolved request | `graphpilot.context.resolved-request.v1` | `resolvedDiagramRequest` |
| Readiness input | `graphpilot.context.readiness-input.v1` | `contextReadinessInput` |
| Readiness review | `graphpilot.context.readiness-review.v1` | `contextReadinessReview` |
| Readiness result | `graphpilot.context.readiness-result.v1` | `contextReadinessResult` |
| Readiness repair input | `graphpilot.context.readiness-repair-input.v1` | `contextReadinessRepairInput` |
| Readiness diagnostics | `graphpilot.context.readiness-debug.v1` | `contextReadinessDebug` |
| Generator input | `graphpilot.context.generation-input.v1` | `contextGenerationInput` |
| Logical outputs | `graphpilot.context.logical-diagram.activity.v1`; `.use-case.v1`; `.bdd.v1` | `contextLogicalDiagram` |
| Generation repair input | `graphpilot.context.generation-repair-input.v1` | `contextGenerationRepairInput` |
| Semantic review input | `graphpilot.context.semantic-review-input.v1` | `contextSemanticReviewInput` |
| Semantic review response | `graphpilot.context.semantic-review-response.v1` | `contextSemanticReviewResponse` |
| Semantic review-response repair input | `graphpilot.context.semantic-review-repair-input.v1` | `contextSemanticReviewRepairInput` |
| Semantic review result | `graphpilot.context.semantic-review-result.v1` | `contextSemanticReviewResult` |
| Semantic repair input | `graphpilot.context.semantic-repair-input.v1` | `contextSemanticRepairInput` |
| Generation result | `graphpilot.context.generation-result.v1` | `contextGenerationResult` |
| Generation example | `graphpilot.context.generation-example.v1` | `contextGenerationExample` |

Semantic-review response/result/repair identities are accepted; exact formal fields and bounds are specified in
`10-mechanical-generation-specification.md` before promotion into schema files.

## Kind rules

- lower camel case;
- descriptive artifact identity;
- mode prefix where direct/context shapes differ;
- version does not appear in `kind`;
- `$id`/`schemaVersion` is the exact contract selector.

## Prompt versions

Prompts are versioned separately:

```text
graphpilot.<namespace>.<operation>-prompt.vN
```

| Current/purpose | Target |
| --- | --- |
| `graphpilot.context-generation.v1` | `graphpilot.context.generation-prompt.v1` |
| `graphpilot.context-readiness.v1` | `graphpilot.context.readiness-prompt.v1` |
| Unified diagram workflow | `graphpilot.generation.workflow-prompt.v1` |
| Internal direct workflow branch | `graphpilot.direct.workflow-branch-prompt.v1` |
| Internal context workflow branch | `graphpilot.context.workflow-branch-prompt.v1` |
| Direct generation | `graphpilot.direct.generation-prompt.v1` |
| Context generation | `graphpilot.context.generation-prompt.v1` |
| Direct generation repair | `graphpilot.direct.generation-repair-prompt.v1` |
| Context generation repair | `graphpilot.context.generation-repair-prompt.v1` |
| Context readiness repair | `graphpilot.context.readiness-repair-prompt.v1` |
| Direct semantic review | `graphpilot.direct.semantic-review-prompt.v1` |
| Context semantic review | `graphpilot.context.semantic-review-prompt.v1` |
| Direct semantic review-response repair | `graphpilot.direct.semantic-review-response-repair-prompt.v1` |
| Context semantic review-response repair | `graphpilot.context.semantic-review-response-repair-prompt.v1` |
| Direct semantic repair | `graphpilot.direct.semantic-repair-prompt.v1` |
| Context semantic repair | `graphpilot.context.semantic-repair-prompt.v1` |

A prompt text/behavior change bumps its prompt version, not the JSON schema unless the JSON contract also changes.

## Readiness rubric/rating versions

| Current | Target |
| --- | --- |
| `graphpilot.readiness-rubric.v1` | `graphpilot.context.readiness-rubric.v1` |
| `graphpilot.readiness.activity.v1` | `graphpilot.context.readiness-rubric.activity.v1` |
| `graphpilot.readiness.use_case.v1` | `graphpilot.context.readiness-rubric.use-case.v1` |
| `graphpilot.readiness.bdd.v1` | `graphpilot.context.readiness-rubric.bdd.v1` |
| `graphpilot.readiness-rating.v1` | `graphpilot.context.readiness-rating.v1` |

Runtime enum values such as `use_case_diagram` retain underscores; identifier compounds use hyphens.

## Semantic-review rubric versions

The shared rubric-document and rating-scale contracts are:

```text
graphpilot.generation.semantic-review-rubric.v1
graphpilot.generation.semantic-review-rating.v1
```

Reusable source layers have independent immutable versions:

```text
graphpilot.generation.semantic-review-rubric-layer.common.v1
graphpilot.direct.semantic-review-rubric-layer.authority.v1
graphpilot.context.semantic-review-rubric-layer.authority.v1
graphpilot.generation.semantic-review-rubric-layer.activity.v1
graphpilot.generation.semantic-review-rubric-layer.use-case.v1
graphpilot.generation.semantic-review-rubric-layer.bdd.v1
```

Final composed mode/type snapshots are:

```text
graphpilot.direct.semantic-review-rubric.activity.v1
graphpilot.direct.semantic-review-rubric.use-case.v1
graphpilot.direct.semantic-review-rubric.bdd.v1

graphpilot.context.semantic-review-rubric.activity.v1
graphpilot.context.semantic-review-rubric.use-case.v1
graphpilot.context.semantic-review-rubric.bdd.v1
```

A final snapshot records its three source layer versions and canonical digest. Source and all six final combinations
are independently validated/snapshot-tested.

## Example-set versions

The exact ordered two-example runtime sets are:

```text
graphpilot.direct.training-examples.activity.v1
graphpilot.direct.training-examples.use-case.v1
graphpilot.direct.training-examples.bdd.v1

graphpilot.context.training-examples.activity.v1
graphpilot.context.training-examples.use-case.v1
graphpilot.context.training-examples.bdd.v1
```

Example changes do not bump generation-input schema versions.

## Semantic-profile and layout-configuration versions

These are immutable policy/configuration identities, not JSON Schema IDs:

```text
graphpilot.generation.semantic-profile.activity.v1
graphpilot.generation.semantic-profile.use-case.v1
graphpilot.generation.semantic-profile.bdd.v1

graphpilot.generation.layout.activity.v1
graphpilot.generation.layout.use-case.v1
graphpilot.generation.layout.bdd.v1
```

Profiles version exact ordered vocabulary/guidance/structural rules. Layout identities version exact direction,
spacing, sizing, containment, coordinate, and engine configuration. Their canonical contents/digests are captured in
packets/traces and change independently from schema/prompt/example versions.

## Generation trace and diagnostics

```text
graphpilot.generation.trace.v1
graphpilot.generation.debug-run.v1
graphpilot.generation.debug-result.v1
```

The optional compact trace sidecar is `<name>.gp.trace.json`. It is bound to the exact canonical diagram digest and
contains model/prompt/schema/example/rubric/layout/usage summaries but no prompts, full rubrics, candidates, source,
or findings/rationales. Full numbered diagnostics remain under `.graphpilot/diagnostics/generation/` and use their
own run/result envelopes plus the exact stage payload schemas.

## Formal-schema invariant

```json
{
  "$id": "graphpilot.context.generation-input.v1",
  "properties": {
    "schemaVersion": {
      "const": "graphpilot.context.generation-input.v1"
    },
    "kind": {
      "const": "contextGenerationInput"
    }
  }
}
```

- Formal `$id` equals document `schemaVersion`.
- Both are exact constants.
- Unknown fields are rejected unless the contract explicitly intends extension.

## Version-bump policy

Bump the schema major for required-field, nesting, enum, field-meaning, authority, provenance, or compatibility
changes. Do not bump it for prompt prose, model deployment, examples, layout tuning, or documentation-only
clarification; those use their own versions/metadata.

## File naming

Formal files use lowercase kebab case matching the artifact:

```text
schemas/
  diagram.json
  context-evidence-manifest.json
  context-diagram-request.json
  context-readiness-review.json
  context-readiness-result.json
  context-generation-input.json
  context-logical-diagram.json
  direct-diagram-request.json
  direct-generation-input.json
  direct-logical-diagram.json
```

Workspace artifact suffixes remain user-oriented:

```text
repository.gp-evidence.json
<name>.gp-request.json
<name>.gp.json
<name>.svg
```

## Cold-turkey V1 policy

- Update all producers, consumers, schemas, registry entries, prompts, traces, tests, fixtures, docs, and affected
  frontend types together.
- No aliases, dual acceptance, dual write, hidden migration, or fallback to old IDs.
- Do not silently rewrite/delete old local artifacts.
- Return explicit unsupported-schema errors; users regenerate pre-standard V1 research artifacts.
- Verify no old identifier remains in active code/tests/docs after promotion, except explicitly historical research.

## Migration proof

Before implementation completion:

1. inventory every GraphPilot-owned ID and kind;
2. map each to one owner under this standard;
3. update formal schemas/registry first in the implementation slice;
4. update all producers/consumers atomically;
5. run schema/context/readiness/generation/MCP/frontend tests;
6. search active code/docs for old IDs;
7. verify old artifacts fail explicitly without mutation;
8. regenerate canonical fixtures under new IDs.
