# Activity-Diagram Readiness Rubric

> **Status:** Historical activity-rubric snapshot. Current intended machine/human owners live under
> `docs/02-design-and-features/08-context-backed-generation/01-readiness/01-rubrics/activity/`; runtime
> implementation has not started.
>
> **Scope of this doc.** [`rubric.json`](rubric.json) is the normative machine-readable `activity_diagram`
> rubric contract, including every facet's applicability and rating criteria. This file is its human companion
> and owns the human explanation, navigation summary, concept mapping, claim guidance, validation explanation,
> and interaction rules. Common policy lives in
> [`../../02-policy-and-calculation.md`](../../02-policy-and-calculation.md);
> final notation lives in
> [`activity-diagram-blueprints.md`](../../../../../03-design/02-diagram-schemas/01-activity-blueprints.md).

## Purpose

Determine whether selected JSON 1 claims and accepted JSON 2 assumptions contain enough supported
behavior/control meaning to generate a trustworthy bounded activity diagram. The generator—not the host or
rubric—maps that meaning to final UML nodes and edges.

## Contract navigation and human explanation

The complete normative machine-readable contract is [`rubric.json`](rubric.json). For each facet, its
`description`, `applicabilityRule`, five `ratingAnchors`, `requirement`, `weight`, `minimumRating`, and
`gapPolicy` are the exact review contract; prose in this file may explain that contract but cannot add, relax,
or replace a criterion.

All facet anchors specialize the shared scale without changing it: `0` is missing, `1` weak, `2` partial, `3`
sufficient, and `4` strong. A `4` requires selected-claim support and no assumptions under the common policy.
For a conditional facet, any `appliesWhenAny` condition makes it applicable; it is `not_applicable` only when
all `notApplicableWhenAll` conditions hold and no apply condition holds; an `uncertainWhen` condition yields
`uncertain` when applicability cannot otherwise be decided. Missing coverage never turns an applicable facet
into `not_applicable` or `uncertain`.

## Concept-to-facet mapping notes

The rubric remains concept-based. These notation terms, when present in source or request language, are
normalized into the existing facets below; they do not create facets or require the host to preselect UML
semantic types:

- `structuredActivityNode`: map contained action and ordering meaning to `behaviorSequence`; map any explicit
  tests, object/data exchange, parallel execution, or action ownership within the structure to
  `controlConditions`, `dataMovement`, `concurrency`, or `responsibility`, respectively.
- `sequenceNode`: map the contained execution order to `behaviorSequence`; map explicitly distinguished owners
  or handoffs for contained actions to `responsibility`.
- `conditionalNode`: map clause tests, alternatives, continuation, and rejoin meaning to `controlConditions`;
  map the ordering inside each clause to `behaviorSequence`, and map clause ownership to `responsibility` when
  the confirmed scope distinguishes it.
- `loopNode`: map setup/body ordering to `behaviorSequence` and test, repeat, continue, and exit meaning to
  `controlConditions`; map loop-carried objects or values to `dataMovement` and distinguished body ownership
  to `responsibility`.
- `expansionRegion`: map the repeated body to `behaviorSequence`, collection input/output and item movement to
  `dataMovement`, parallel expansion to `concurrency`, and distinguished body ownership or handoffs to
  `responsibility`.
- `expansionNode`: map collection identity, boundary direction, and input/output meaning to `dataMovement`; map
  its connection to the consuming or producing region body to `behaviorSequence`. Concurrency comes from an
  explicitly parallel expansion mode, not from an expansion node by itself.

## Interaction rules

Iteration is not a separate facet:

- loop conditions belong to `controlConditions`;
- loop body/order belongs to `behaviorSequence`;
- loop termination belongs to `completionOutcomes`.

Normal completion remains required. Failure completion becomes required only when `exceptionPaths` is
applicable. One claim may support multiple facets only when it genuinely establishes each facet's normative
meaning.

## Claim-kind guidance

| Facet | Commonly relevant JSON 1 claim kinds |
| --- | --- |
| `trigger` | `behaviorStep`, `actorGoal`, `capability`, `boundary` |
| `behaviorSequence` | `behaviorStep`, `relationship`, `constraint` |
| `completionOutcomes` | `behaviorStep`, `capability`, `constraint` |
| `responsibility` | `entity`, `actorGoal`, `behaviorStep`, `relationship` |
| `controlConditions` | `behaviorStep`, `constraint`, `relationship` |
| `dataMovement` | `behaviorStep`, `relationship`, `property`, `entity` |
| `concurrency` | `behaviorStep`, `relationship`, `constraint` |
| `exceptionPaths` | `behaviorStep`, `constraint`, `relationship` |

Claim kind alone never establishes coverage; selected meaning must satisfy the facet's normative JSON
criteria.

## Validation invariants

1. The complete [`rubric.json`](rubric.json) contract parses and has the exact activity envelope/version.
2. All eight facets appear once in canonical order with their preserved IDs, requirements, weights, minimum
   ratings, and gap policies.
3. Every facet has a description and concrete string-keyed `ratingAnchors` for `0`, `1`, `2`, `3`, and `4`.
4. `trigger`, `behaviorSequence`, and `completionOutcomes` use `kind: always` and remain required,
   blocking, and non-overrideable below `3`.
5. Every conditional facet has explicit `appliesWhenAny`, `notApplicableWhenAll`, and `uncertainWhen` arrays
   and remains blocking but overrideable below `3`.
6. The activity envelope has no `groupRules` property.
7. Structured activity, sequence, conditional, loop, and expansion concepts map only into the existing facets;
   they never introduce a facet or require host-selected UML semantic types or topology.
8. [`rubric.json`](rubric.json), rather than a prose summary, is the complete normative facet source.

### Final definition

> Activity readiness means supported context establishes a bounded start, connected in-scope behavior, and
> completion, plus sufficient responsibility, control conditions, data, concurrency, and exception meaning
> whenever the confirmed request or in-scope evidence invokes those concepts.
