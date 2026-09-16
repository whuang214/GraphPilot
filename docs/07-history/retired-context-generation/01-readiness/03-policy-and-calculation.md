# Readiness Policy and Deterministic Calculation

> **Scope of this doc.** This file is the single owner of the common rubric schema/versioning,
> required/conditional applicability, `0..4` rating anchors, weights, assumption cap, not-applicable and
> uncertain treatment, deterministic score/rounding, finding assembly order, and exact status algorithm.
> Finding codes and the raw reviewer JSON contract live in
> [`03-reviewer-json.md`](04-reviewer-json.md); each type folder under `rubrics/` contains a normative
> machine-readable `rubric.json` plus a linked explanatory `rubric.md`.

## Purpose

Define one immutable policy that all three per-type readiness rubrics use. The LLM supplies semantic
judgments; deterministic Layer 4 validates them and calculates the policy result.

## Rubric definitions

There are exactly three static `rubric.json` definitions. One is selected from `request.diagramType` for each
review; these are configuration, not runtime results. The sibling `rubric.md` explains the same contract but
cannot add, relax, or override machine-readable criteria.

| Diagram type | Rubric version | Machine contract | Explanation |
| --- | --- | --- | --- |
| `activity_diagram` | `graphpilot.context.readiness-rubric.activity.v1` | [`rubrics/activity/rubric.json`](01-rubrics/activity/rubric.json) | [`rubrics/activity/rubric.md`](01-rubrics/activity/rubric.md) |
| `use_case_diagram` | `graphpilot.context.readiness-rubric.use-case.v1` | [`rubrics/use-case/rubric.json`](01-rubrics/use-case/rubric.json) | [`rubrics/use-case/rubric.md`](01-rubrics/use-case/rubric.md) |
| `bdd_diagram` | `graphpilot.context.readiness-rubric.bdd.v1` | [`rubrics/bdd/rubric.json`](01-rubrics/bdd/rubric.json) | [`rubrics/bdd/rubric.md`](01-rubrics/bdd/rubric.md) |

The backend loads and validates these JSON files; their logical fields and values are normative.

## 1. Rubric envelope and schema fields

| Field | Required | Rule |
| --- | --- | --- |
| `schemaVersion` | Yes | Constant `graphpilot.context.readiness-rubric.v1`; versions the common rubric-document shape. |
| `kind` | Yes | Constant `contextReadinessRubric`. |
| `rubricVersion` | Yes | Immutable per-type policy identity copied into every final readiness result. |
| `diagramType` | Yes | Exactly one of `activity_diagram`, `use_case_diagram`, or `bdd_diagram`. |
| `ratingScaleVersion` | Yes | Constant `graphpilot.context.readiness-rating.v1`. |
| `facets` | Yes | Ordered, non-empty, unique and complete facet definitions for that type. |

### Initial rubric identities

| Diagram type | `rubricVersion` | Exact machine owner |
| --- | --- | --- |
| `activity_diagram` | `graphpilot.context.readiness-rubric.activity.v1` | [`rubrics/activity/rubric.json`](01-rubrics/activity/rubric.json) |
| `use_case_diagram` | `graphpilot.context.readiness-rubric.use-case.v1` | [`rubrics/use-case/rubric.json`](01-rubrics/use-case/rubric.json) |
| `bdd_diagram` | `graphpilot.context.readiness-rubric.bdd.v1` | [`rubrics/bdd/rubric.json`](01-rubrics/bdd/rubric.json) |

## 2. Facet definition fields

| Field | Required | Rule |
| --- | --- | --- |
| `id` | Yes | Stable machine ID; unique within the rubric. |
| `description` | Yes | Exact semantic question the reviewer judges. |
| `requirement` | Yes | `required` or `conditional`; there are no advisory scored facets in v1. |
| `weight` | Yes | Integer `1..4`; affects only the secondary score. |
| `minimumRating` | Yes | Constant `3` in all v1 rubrics. |
| `applicabilityRule` | Yes | `{"kind": "always"}` for required facets; conditional facets use the exact shape below. |
| `ratingAnchors` | Yes | Object with exactly the string keys `0`, `1`, `2`, `3`, and `4`; each value is the facet-specific criterion for that rating. |
| `gapPolicy` | Yes | Deterministic severity and default overrideability below `minimumRating`. |

A conditional `applicabilityRule` has exactly:

| Field | Required | Rule |
| --- | --- | --- |
| `kind` | Yes | Constant `conditional`. |
| `appliesWhenAny` | Yes | Non-empty array; one matching condition makes the facet applicable. |
| `notApplicableWhenAll` | Yes | Non-empty array; all conditions must hold before the facet may be N/A. |
| `uncertainWhen` | Yes | Non-empty array describing evidence that suggests applicability without establishing it. |

No `groupRules` field exists in v1. Cross-facet adequacy is judged through request alignment, detail, and
modelability findings rather than a generic rule engine.

Facet order is canonical. Reviewer input, raw reviewer output, final `coverage`, fixtures, and diagnostics use
that order.

Weights express relative progress value, not gates:

- `4` — the diagram type's defining semantic core;
- `3` — a major boundary, control, or structural concern;
- `2` — a conditional refinement.

Required/conditional rules and findings—not weight—decide readiness. Calibration may change a weight only
through a new rubric version.

## 3. Versioning rules

Released rubric versions are immutable. Create the next per-type version when any of these changes:

- facet ID, description, tracked meaning, requirement, applicability trigger, or order;
- weight, minimum rating, assumption policy, or gap overrideability;
- any facet-specific `0..4` rating anchor or applicability condition;
- score inclusion, rounding, status, or synthesized-finding behavior;
- a finding code's category, severity, overrideability, or allowed action semantics.

Editorial corrections and additional examples that cannot change an assessment do not require a new rubric
version. Reviewer prompt wording, raw structured-output schema, model/deployment, and generator prompt are
separately versioned; changing one requires recalibration even when the rubric identity is unchanged.
Historical rubric definitions remain readable for interpreting readiness results and optional trace sidecars, but new reviews use
the configured current version for the requested type.

## 4. Applicability and requirement rules

### Required facets

A `required` facet:

- is always `applicable`;
- must have an integer rating and reach at least `3`;
- cannot be returned as `not_applicable` or `uncertain`;
- produces non-overrideable `required_facet_below_minimum` at rating `0..2`.

### Conditional facets

A conditional facet becomes `applicable` when at least one of its exact `appliesWhenAny` conditions is
established by the original request/goal/scope/detail/decisions, selected claim meaning/support, relevant
active-claim index entries, open uncertainties/dispositions, or accepted assumptions.

Once applicable, a conditional facet also requires rating `3`. Rating `0..2` produces
`conditional_facet_below_minimum`; that blocker is overrideable by omission. A separate non-overrideable
holistic finding still prevents override when omission would defeat the goal, conflict with scope, or make
the selection non-modelable.

A conditional facet is `not_applicable` only when every `notApplicableWhenAll` condition is positively
established. Absence of selected evidence alone is never proof of non-applicability. A scope exclusion permits
`not_applicable` only when Layer 3 finds the exclusion coherent with the goal and relevant indexed claims.

A conditional facet is `uncertain` when one of its `uncertainWhen` conditions is established. `uncertain` has
no rating, remains in the score denominator with zero contribution, and produces
`facet_applicability_uncertain`. It must also identify matching uncertainty, missing-context, or question
detail.

### Valid coverage combinations

| Applicability | `rating` | Derived facet status | Ref rule |
| --- | --- | --- | --- |
| `applicable` | `0` | `missing` | `supportingClaimRefs` and `assumptionRefs` empty. |
| `applicable` | `1` | `weak` | At least one exact selected claim or accepted assumption ref. |
| `applicable` | `2` | `partial` | At least one exact selected claim or accepted assumption ref. |
| `applicable` | `3` | `sufficient` | At least one exact selected claim or accepted assumption ref. |
| `applicable` | `4` | `strong` | At least one exact selected claim ref and no assumption refs. |
| `not_applicable` | `null` in raw review; absent from final coverage | absent | Both ref arrays empty; positive rationale required. |
| `uncertain` | `null` in raw review; absent from final coverage | absent | Rationale plus matching gap/finding required; trigger refs may be cited there. |

Only JSON 2 selected claims can support a positive rating. An unselected active-index claim can establish
applicability or produce a recommendation, but contributes no coverage until selected and persisted.

## 5. Common `0..4` rating anchors

| Rating | Derived status | Exact common anchor |
| ---: | --- | --- |
| `0` | `missing` | No selected claim or accepted assumption establishes any usable part of the facet's required meaning. |
| `1` | `weak` | A selected input hints at the facet, but the core proposition, participants, endpoints, ordering, condition, or ownership cannot be modeled reliably. |
| `2` | `partial` | The core proposition is present, but at least one material connection, endpoint, ordering fact, condition, qualifier, outcome, or responsibility required by the facet is absent or ambiguous. |
| `3` | `sufficient` | Every material item in the facet's sufficient criterion is established for confirmed scope/detail; only non-material detail may be absent. |
| `4` | `strong` | The sufficient criterion is met without assumptions, and all material meaning is explicit, complete, precise, and unambiguous under the strong criterion. |

These shared anchors give the LLM one consistent scale; the selected rubric's exact `ratingAnchors` then
specialize all five values for each facet. Facet status is distinct from the overall readiness status.

Direct and inferred JSON 1 claims may both support ratings. An inferred claim is not automatically weaker;
its support rationale is part of the review projection. A rating reflects fitness for this request, not a
percentage confidence in repository truth.

## 6. Assumption cap

For every applicable facet:

```text
if assumptionRefs is non-empty:
    effectiveRating = min(reportedRating, 3)
else:
    effectiveRating = reportedRating
```

Raw output with `rating: 4` and a non-empty `assumptionRefs` array is invalid and receives the one
structured-output repair attempt. Layer 4 still applies the cap defensively before calculation. The
**effective rating** is the reported `0..4` rating after this assumption cap; without assumption refs it equals
the reported rating.

Every facet rating `1..3` that cites an accepted assumption produces `assumption_backed_coverage`.
Therefore an assessment relying on an assumption can be at best `ready_with_warnings` unless a blocker also
remains. An assumption supplying only part of the required meaning may still rate `1` or `2`; acceptance
does not automatically make it sufficient. Exact assumption quality and supported-claim replacement findings
live in [`03-reviewer-json.md`](04-reviewer-json.md); readiness treats `acceptedBy` as provenance.

## 7. Included facets and weighted score

For each facet:

```text
not_applicable -> exclude weight from numerator and denominator
applicable     -> include weight and effective rating
uncertain      -> include weight with effective rating 0
```

Let:

```text
R = sum(effectiveRating * weight) over applicable and uncertain facets
W = sum(weight) over applicable and uncertain facets
D = 4 * W
```

Compute the integer informational score with round-half-up—not language-default banker's rounding:

```text
readinessScore = floor((100 * R + D / 2) / D)
```

Adding `D / 2` before integer division is equivalent to adding one half before rounding, which implements
round-half-up. `D` is a multiple of four, so `D / 2` is exact integer arithmetic. Required facets guarantee a
non-empty denominator; the result is `0..100`.

Example: use-case ratings `4/4/4/2` at weights `3/4/4/4`, with
`useCaseRelationships: not_applicable`:

```text
R = (4*3) + (4*4) + (4*4) + (2*4) = 52
D = 4 * (3+4+4+4) = 60
score = floor((100*52 + 30) / 60) = 87
```

The result is still `needs_context` because required `actorGoalAssociations` is below `3`. A high average
never compensates for a required gap.

If Layer 1 fails, no semantic review or score exists: the final `contextReadinessResult` uses `status: invalid`,
`readinessScore: null`, and empty `coverage`. Operational load/reviewer failures remain errors.

## 8. Finding assembly order

Layer 4 determines the finding set in this order:

1. deterministic selection-closure and explicit blocking-disposition findings from preflight;
2. validated Layer 2 coverage findings;
3. assumption-backed warnings;
4. validated Layer 3 holistic findings;
5. exact semantic de-duplication by code, facet, and sorted related refs.

When two findings describe the same condition, retain stricter severity/overrideability and merge
non-conflicting refs/actions. A warning never downgrades a blocker.

## 9. Authoritative status algorithm

The exact algorithm implementing the
[`01-readiness-reviewer.md`](02-reviewer.md) status-first policy is:

```text
if Layer 1 fails:
    status = invalid
else if any validated finding has severity blocking:
    status = needs_context
else if any validated finding has severity warning:
    status = ready_with_warnings
else:
    status = ready
```

The score never changes status in v1. Adding any score threshold requires a new affected rubric version and
full recalibration. `canGenerate`, warning acceptance, `canOverride`, and force behavior are derived under
[`01-readiness-reviewer.md`](02-reviewer.md) after status; no score bypasses them.

## 10. Validation invariants

A rubric definition is valid only when:

1. envelope constants and diagram type are exact;
2. rubric version matches its diagram type and is immutable once released;
3. facet IDs are unique and ordered;
4. every required facet uses `always`, minimum `3`, and blocking/non-overrideable gap policy;
5. every conditional facet has non-empty `appliesWhenAny`, `notApplicableWhenAll`, and `uncertainWhen` arrays plus minimum `3`;
6. every facet defines exactly one non-empty anchor for each rating `0..4`;
7. weights are integers `1..4`;
8. no rubric contains `groupRules` in v1;
9. all finding codes referenced by policy exist in the finding registry;
10. score and status use only the deterministic algorithms above.

## Deliberate boundaries

This file does not own per-type facets, finding definitions, the raw reviewer JSON schema, final public
readiness-result fields, host-loop orchestration, MCP UX, fixtures, or implementation classes. Host-loop and
UX behavior live in the
[unified MCP generation workflow](../../../02-architecture/01-mcp-tools/README.md); exact public transport
lives in the [MCP context-tool contract](../../../02-architecture/01-mcp-tools/02-context-tools.md).

### Final definition

> The common readiness policy is an immutable per-type rubric envelope plus one shared applicability,
> rating, assumption, score, rounding, finding-assembly, and status algorithm applied deterministically to
> validated semantic judgments.
