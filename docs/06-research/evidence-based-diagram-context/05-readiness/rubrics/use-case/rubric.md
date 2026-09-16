# Use-Case-Diagram Readiness Rubric

> **Status:** Historical use-case-rubric snapshot. Current intended machine/human owners live under
> `docs/02-design-and-features/08-context-backed-generation/01-readiness/01-rubrics/use-case/`; runtime
> implementation has not started.
>
> **Scope of these sibling files.** [`rubric.json`](rubric.json) is the single normative machine-readable
> `use_case_diagram` rubric contract. Its facet descriptions, applicability rules, rating anchors, weights,
> minimum ratings, and gap policies govern assessment. This `rubric.md` owns explanation, the human-readable
> summary, semantic boundaries, claim-kind guidance, and validation invariants without redefining the contract.
> Common policy lives in [`../../02-policy-and-calculation.md`](../../02-policy-and-calculation.md); final notation
> lives in [`use-case-diagram-blueprints.md`](../../../../../03-design/02-diagram-schemas/03-use-case-blueprints.md).

## Purpose

Determine whether selected JSON 1 claims and accepted JSON 2 assumptions establish a trustworthy subject,
external actors, user-visible goals, participation, and any in-scope include, extend, actor/use-case
generalization, or named extension-point meaning.

## Normative machine-readable contract

The complete normative contract is [`rubric.json`](rubric.json).

## Human-readable facet summary

The linked [`rubric.json`](rubric.json) is the normative source for every `0..4` boundary. This table is
navigation only and does not add criteria or applicability triggers.

| Facet | Mode | Weight | Applicability | Concept judged |
| --- | --- | ---: | --- | --- |
| `subjectBoundary` | Required | 3 | Always. | Modeled subject and semantic inside/outside classification; no visible subject box is required. |
| `actors` | Required | 4 | Always. | External human roles and systems participating in confirmed in-scope goals, distinct from internal components. |
| `actorGoals` | Required | 4 | Always. | Bounded user-visible outcomes or capabilities at the requested abstraction level. |
| `actorGoalAssociations` | Required | 4 | Always. | Explicit supported participation between external actors and in-scope goals. |
| `useCaseRelationships` | Conditional | 2 | The JSON `appliesWhenAny`, `notApplicableWhenAll`, and `uncertainWhen` rules decide. | Include, extend, actor/use-case generalization, and named extension points, including standalone extension-point requests. |

## Semantic boundary rules

- The machine-readable contract in [`rubric.json`](rubric.json) is normative; prose and claim-kind guidance
  cannot add, remove, or relax a criterion.
- Facets remain concept-based semantic questions rather than mandates for host-selected UML or GraphPilot
  element types.
- `subjectBoundary` is semantic coverage, not a visible-node mandate.
- Actors are external relative to the selected subject; internal controllers and repositories do not become
  actors.
- Goals are user-visible outcomes, not implementation steps or incidental UI actions.
- Actor and goal existence do not imply participation; `actorGoalAssociations` requires a supported
  connection.
- Named extension points are assessed under `useCaseRelationships`, including standalone extension-point
  requests; they do not create a separate facet, and a standalone request does not imply an extend
  relationship.
- Include, extend, actor/use-case generalization, and named extension points are assessed only under the exact
  applicability boundaries in `useCaseRelationships`; complexity alone is not a trigger.
- Scope/alignment and abstraction/noise remain Layer 3 findings, not duplicate scored facets.

## Claim-kind guidance

| Facet | Commonly relevant JSON 1 claim kinds |
| --- | --- |
| `subjectBoundary` | `boundary`, `entity`, `capability`, `relationship` |
| `actors` | `entity`, `actorGoal`, `relationship` |
| `actorGoals` | `actorGoal`, `capability`, `behaviorStep` |
| `actorGoalAssociations` | `actorGoal`, `relationship`, `capability` |
| `useCaseRelationships` | `relationship`, `actorGoal`, `constraint` |

Claim kind alone never establishes coverage; selected meaning must satisfy the exact normative
[`rubric.json`](rubric.json) anchor.

## Validation invariants

1. The complete normative rubric in [`rubric.json`](rubric.json) parses and has the exact use-case
   envelope/version defined there.
2. The envelope ends with `facets`; it does not contain `groupRules`.
3. All five facets appear once in canonical order with IDs and weights `subjectBoundary:3`, `actors:4`,
   `actorGoals:4`, `actorGoalAssociations:4`, and `useCaseRelationships:2`.
4. Every facet has a `description`, `requirement`, `weight`, `minimumRating`, `applicabilityRule`, exact
   `ratingAnchors` for `0` through `4`, and `gapPolicy`.
5. The four required facets use only `applicabilityRule.kind: always`, require rating `3`, and are blocking and
   non-overrideable below minimum.
6. `useCaseRelationships` is conditional, requires rating `3` when applicable, is blocking and overrideable
   below minimum, and defines `appliesWhenAny`, `notApplicableWhenAll`, and `uncertainWhen` explicitly.
7. Named extension points, including standalone extension-point requests, are assessed only under
   `useCaseRelationships`; no extension-point facet is added and no extend relationship is inferred from a
   standalone request.
8. A visible subject node is never required by readiness alone.
9. The rubric never requires host-selected UML semantic types or edges.

### Final definition

> Use-case readiness means supported context identifies the subject, external actors, user-visible goals, and
> participation, plus complete include, extend, actor/use-case generalization, and named extension-point
> meaning whenever the normative applicability rule makes `useCaseRelationships` applicable.
