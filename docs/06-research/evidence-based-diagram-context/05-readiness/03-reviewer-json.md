# Readiness Findings and Structured Reviewer Output

> **Status:** Historical reviewer-output snapshot. Current intended behavior is owned by
> [`03-reviewer-json.md`](../../../03-design/01-context-generation/01-readiness/04-reviewer-json.md);
> runtime implementation has not started.
>
> **Scope of this doc.** This file is the single owner of Layer 3 finding categories/codes,
> severity/overrideability, structured action kinds, the raw Layer 2/3 reviewer JSON contract, and
> deterministic validation/canonicalization of that raw output. Common rating/calculation policy lives in
> [`02-policy-and-calculation.md`](02-policy-and-calculation.md); the final host-facing readiness-result
> envelope remains owned by [`04-results.md`](04-results.md).

## Purpose

Constrain the one Layer 2/3 LLM call to semantic judgments and exact references. The raw response is not
trusted policy: deterministic Layer 4 validates it, injects registry metadata, calculates status/score, and
assembles the final `04-results.md` contract.

## Simple complete example

```json
{
  "schemaVersion": "graphpilot.context-readiness-review.v1",
  "kind": "contextReadinessReview",
  "rubricVersion": "graphpilot.readiness.use_case.v1",
  "coverage": [
    {
      "facet": "subjectBoundary",
      "applicability": "applicable",
      "rating": 4,
      "supportingClaimRefs": [
        {
          "id": "claim-order-platform-boundary",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "The selected boundary claim explicitly identifies the Order Platform and its external participants."
    },
    {
      "facet": "actors",
      "applicability": "applicable",
      "rating": 4,
      "supportingClaimRefs": [
        {
          "id": "claim-customer-actor",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "Customer is an explicit external human role."
    },
    {
      "facet": "actorGoals",
      "applicability": "applicable",
      "rating": 3,
      "supportingClaimRefs": [
        {
          "id": "claim-customer-places-order",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "Place Order is a supported user-visible goal at the requested level."
    },
    {
      "facet": "actorGoalAssociations",
      "applicability": "applicable",
      "rating": 3,
      "supportingClaimRefs": [
        {
          "id": "claim-customer-places-order",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "The actor-goal claim explicitly connects Customer to Place Order."
    },
    {
      "facet": "useCaseRelationships",
      "applicability": "not_applicable",
      "supportingClaimRefs": [],
      "assumptionRefs": [],
      "rationale": "No request, scope, selected/indexed claim, uncertainty, or accepted assumption indicates include, extend, generalization, or named extension-point meaning."
    }
  ],
  "holisticFindings": [
    {
      "code": "secondary_claim_omitted",
      "facet": "actorGoals",
      "message": "An existing active claim establishes order tracking as a secondary in-scope customer goal.",
      "consequence": "If generated now, the use-case diagram may omit the supported Track Order goal.",
      "relatedClaimRefs": [
        {
          "id": "claim-customer-tracks-order",
          "version": 1
        }
      ],
      "relatedUncertaintyRefs": [],
      "relatedAssumptionRefs": [],
      "recommendedAction": {
        "kind": "select_existing_claim",
        "description": "Add the existing Track Order claim as a primary selection.",
        "claimRefs": [
          {
            "id": "claim-customer-tracks-order",
            "version": 1
          }
        ]
      }
    }
  ],
  "recommendedSelections": [
    {
      "claimRef": {
        "id": "claim-customer-tracks-order",
        "version": 1
      },
      "role": "primary",
      "reason": "Adds the existing supported secondary goal.",
      "supportsFacets": [
        "actorGoals",
        "actorGoalAssociations"
      ]
    }
  ],
  "removeSelections": [],
  "missingContext": [],
  "relevantUncertainties": [],
  "questions": []
}
```

## Output sections

The complete example above is the one private LLM output shape owned here. Its sections mean:

| Section | Plain-language question it answers |
| --- | --- |
| envelope | Which private structured-review contract and rubric produced this response? |
| `coverage` | How does selected context cover every exact per-type facet? |
| `holisticFindings` | Which whole-selection conditions, consequences, and next actions apply? |
| `recommendedSelections` | Which existing active claims should JSON 2 add? |
| `removeSelections` | Which current selections should JSON 2 remove? |
| `missingContext` | Which required facts genuinely do not exist in JSON 1? |
| `relevantUncertainties` | Which open JSON 1 gaps affect this request and how might JSON 2 treat them? |
| `questions` | Which focused user clarification is still required? |

## 1. Envelope

| Field | Required | Rule |
| --- | --- | --- |
| `schemaVersion` | Yes | Constant `graphpilot.context-readiness-review.v1`. |
| `kind` | Yes | Constant `contextReadinessReview`. |
| `rubricVersion` | Yes | Exact backend-selected immutable rubric version. |

These fields version the private backend-to-reviewer contract independently of the final public readiness
result and per-type rubric.

The raw reviewer does not return `status`, `readinessScore`, `canGenerate`, `canOverride`, facet `weight`,
derived facet `status`, finding `id`, category, severity, or overrideability. Layer 4 owns those fields.

## 2. Coverage items

Each `coverage` item contains:

| Field | Required | Rule |
| --- | --- | --- |
| `facet` | Yes | Exact facet ID from the selected per-type rubric. |
| `applicability` | Yes | `applicable`, `not_applicable`, or `uncertain`. |
| `rating` | When applicable | Integer `0..4`; omitted otherwise. |
| `supportingClaimRefs` | Yes | Unique exact selected claim refs; unselected index claims cannot support a rating. |
| `assumptionRefs` | Yes | Unique exact accepted JSON 2 assumption IDs. |
| `rationale` | Yes | Bounded explanation applying the facet criteria to cited inputs. |

Valid applicability/rating/ref combinations and assumption capping belong to
[`02-policy-and-calculation.md`](02-policy-and-calculation.md). `coverage` contains every rubric facet exactly
once in canonical rubric order.

## 3. Layer 3 finding registry

Layer 3 checks the selection as a whole rather than re-scoring scope, alignment, abstraction, or noise as
facets. The LLM returns a registered code and semantic details; Layer 4 injects category, severity, and
overrideability.

### Category enum

`alignment`, `coverage`, `scope`, `omission`, `coherence`, `ambiguity`, `contradiction`, `abstraction`,
`assumption`, `decision`, `redundancy`, and `uncertainty` are the only readiness-finding categories. Binding,
reference, path, schema, safety, and hard bounds remain Layer 1 invalidity/errors.

### Deterministically synthesized codes

| Code | Category | Severity | Overrideable | When Layer 4 creates it | Recommended-action derivation |
| --- | --- | --- | --- | --- | --- |
| `required_facet_below_minimum` | `coverage` | `blocking` | No | Required applicable facet has effective rating `0..2`. | Prefer matching `select_existing_claim`; otherwise `search_source` or `ask_user`. |
| `conditional_facet_below_minimum` | `coverage` | `blocking` | Yes | Conditional applicable facet has effective rating `0..2`. | Prefer matching `select_existing_claim`; otherwise `search_source` or `ask_user`. |
| `facet_applicability_uncertain` | `coverage` | `blocking` | Yes | Conditional facet applicability is `uncertain`. | `search_source` or `ask_user` from matching uncertainty/gap/question detail. |
| `selection_closure_missing` | `omission` | `blocking` | No | A required payload claim reference is not selected. | `select_existing_claim` for the exact referenced version. |
| `assumption_backed_coverage` | `assumption` | `warning` | No | A facet rating `1..3` cites an accepted assumption. | `search_source` when support may replace it; warning acceptance otherwise follows 04. |

A conditional coverage blocker may be overridden only by omitting unsupported secondary meaning. A separate
non-overrideable holistic finding wins when the same omission would defeat the goal or make the selection
non-modelable.

### LLM-selected holistic codes

| Code | Category | Severity | Overrideable | Exact meaning | Permitted action kinds |
| --- | --- | --- | --- | --- | --- |
| `request_scope_ambiguous` | `scope` | `blocking` | No | Goal/included scope permits materially different diagrams and context cannot choose safely. | `ask_user`, `revise_request` |
| `selection_misses_goal` | `alignment` | `blocking` | No | The selection cannot answer a material part of the confirmed goal. | `select_existing_claim`, `search_source`, `ask_user`, `revise_request` |
| `scope_conflicts_with_goal` | `scope` | `blocking` | No | An inclusion/exclusion or disposition contradicts the confirmed goal. | `ask_user`, `revise_request` |
| `material_claim_omitted` | `omission` | `blocking` | No | An existing active claim is necessary for required in-scope meaning but is unselected. | `select_existing_claim` |
| `secondary_claim_omitted` | `omission` | `warning` | No | An existing active claim would improve a non-blocking secondary detail. | `select_existing_claim` |
| `selection_not_modelable` | `coherence` | `blocking` | No | Selected facts cannot form one meaningful diagram at requested type/scope. | `select_existing_claim`, `search_source`, `ask_user`, `revise_request` |
| `material_meaning_ambiguous` | `ambiguity` | `blocking` | No | A core relationship, ordering, ownership, guard, multiplicity, or responsibility has incompatible interpretations. | `search_source`, `ask_user` |
| `secondary_context_incomplete` | `ambiguity` | `blocking` | Yes | A secondary applicable detail is incomplete but may be truthfully omitted. | `select_existing_claim`, `search_source`, `ask_user` |
| `selected_claims_conflict` | `contradiction` | `blocking` | No | Current selected claims make incompatible v1 `as_implemented` assertions. | `search_source`, `ask_user` |
| `relevant_uncertainty_undisposed` | `uncertainty` | `blocking` | No | A request-relevant open uncertainty lacks coherent JSON 2 disposition. | `search_source`, `ask_user`, `revise_request` |
| `deferred_uncertainty` | `uncertainty` | `warning` | No | A coherently deferred secondary uncertainty remains and unsupported meaning must be omitted. | `search_source`, `ask_user` |
| `exclude_disposition_incoherent` | `scope` | `blocking` | No | An `exclude` disposition conflicts with included scope or goal. | `ask_user`, `revise_request` |
| `assumption_supported_by_claim` | `assumption` | `blocking` | No | A current active claim supports the proposition, so weaker assumption provenance is incorrect. | `replace_assumption_with_claim` |
| `assumption_conflicts_with_context` | `assumption` | `blocking` | No | An assumption contradicts a selected/current claim or another accepted assumption. | `ask_user`, `revise_assumption` |
| `assumption_too_broad` | `assumption` | `blocking` | No | An assumption substitutes for the central supported subject rather than filling a narrow gap. | `ask_user`, `revise_assumption` |
| `decision_asserts_unsupported_fact` | `decision` | `blocking` | No | A decision attempts to establish factual meaning instead of non-factual guidance. | `select_existing_claim`, `search_source`, `ask_user`, `revise_request` |
| `out_of_scope_selection` | `scope` | `warning` | No | A selected claim is outside confirmed scope without making the remaining model untrustworthy. | `remove_selection` |
| `abstraction_levels_mixed` | `abstraction` | `warning` | No | Selection mixes materially inconsistent levels. | `remove_selection`, `revise_request` |
| `selection_redundant` | `redundancy` | `warning` | No | Selected claims duplicate meaning without necessary support/context. | `remove_selection` |
| `detail_below_request` | `abstraction` | `blocking` | Yes | Context supports a truthful smaller diagram but not requested detail. | `select_existing_claim`, `search_source`, `ask_user`, `revise_request` |

Warnings are non-blocking by definition: core required meaning is sufficient, and generation can remain
truthful while visibly omitting/simplifying secondary meaning. Core correctness problems use blocking codes.

## 4. Recommended-action kind registry

| Kind | Exact host-directed meaning |
| --- | --- |
| `select_existing_claim` | Add validated active/current claim versions to JSON 2; no source search is needed. |
| `remove_selection` | Remove a redundant/out-of-scope selection without changing confirmed goal. |
| `replace_assumption_with_claim` | Select the exact replacement claim and remove the equivalent assumption plus `assume` disposition together; the backend never mutates JSON 2 silently. |
| `search_source` | Perform focused repository search; only verified source may update JSON 1. |
| `ask_user` | Ask one focused question because repository context cannot settle fact or intent. |
| `revise_request` | Ask the user to clarify/change JSON 2 goal, scope, detail, decision, or disposition. |
| `revise_assumption` | Narrow, replace, or withdraw an already-accepted assumption through the host workflow. |

These are typed semantic action payloads, not MCP calls. The backend returns them; the host decides whether
and how to execute them. [`../07-mcp-prompts-and-tool-contracts.md`](../07-mcp-prompts-and-tool-contracts.md)
owns transport/presentation and the host prompt owns orchestration.

Every action has exactly `kind` and a non-empty `description`, plus only the fields allowed below:

| `kind` | Additional required fields | Exact rules |
| --- | --- | --- |
| `select_existing_claim` | `claimRefs` | Non-empty active/current unselected refs; no other payload fields. |
| `remove_selection` | `claimRefs` | Non-empty currently selected refs; no other payload fields. |
| `replace_assumption_with_claim` | `assumptionRef`, `uncertaintyRef`, `claimRefs` | One paired assumption/open uncertainty plus non-empty active/current replacement refs. |
| `search_source` | `suggestedSearches`, `uncertaintyRefs` | Searches non-empty; uncertainty refs required but may be empty when no JSON 1 uncertainty exists yet. |
| `ask_user` | `questionRefs` | Non-empty IDs resolving to companion `questions[]`; no other payload fields. |
| `revise_request` | `requestFields` | Non-empty unique values from `goal`, `scope.included`, `scope.excluded`, `detailLevel`, `decisions`, `uncertaintyDispositions`. |
| `revise_assumption` | `assumptionRefs` | Non-empty accepted assumption IDs; no other payload fields. |

Unknown fields and fields belonging to another action kind are invalid. Related finding refs may provide
additional context but never substitute for the action's required payload.

## 5. Raw supporting array shapes

| Array | Required item fields |
| --- | --- |
| `recommendedSelections` | `claimRef`, JSON 2 `role`, non-empty `reason`, non-empty valid `supportsFacets`. |
| `removeSelections` | selected `claimRef`, non-empty `reason`, non-empty registered `findingCodes`. |
| `missingContext` | non-empty `description`, valid non-empty `affectedFacets`, non-empty `reason`, bounded `suggestedSearches`. |
| `relevantUncertainties` | allowlisted `uncertaintyRef`, valid non-empty `affectedFacets`, non-empty `reason`, `suggestedDisposition` in `block|exclude|assume|defer`. |
| `questions` | unique non-empty `id`, focused `question`, non-empty `reason`, valid non-empty `affectedFacets`; no answer is fabricated. |

## 6. Structured finding shape

Every raw holistic finding returns together:

- registered `code`;
- one valid affected `facet` or `null` for selection-wide findings;
- self-contained `message` stating the issue;
- self-contained `consequence` stating what generation would omit, simplify, assume, or risk;
- exact related selected/indexed claim, uncertainty, and assumption refs;
- one `recommendedAction` containing permitted `kind`, non-empty `description`, exact allowlisted refs, and
  bounded focused searches when source investigation is recommended.

The backend adds deterministic finding ID and registry policy fields when assembling the final result owned by
[`04-results.md`](04-results.md).
The host therefore consumes one result instead of separate grade, warning, and action calls. Exact host
wording belongs to [`../07-mcp-prompts-and-tool-contracts.md`](../07-mcp-prompts-and-tool-contracts.md).

## 7. Deterministic structured-output validation

Layer 4 rejects raw output and uses at most one repair call unless every rule passes:

1. object matches strict schema with no unknown fields;
2. envelope constants match exactly;
3. `rubricVersion` matches the backend-selected rubric;
4. `coverage` contains every facet once in canonical order;
5. no unknown/duplicate facet appears;
6. required facets are applicable with integer rating;
7. conditional combinations match common policy;
8. ratings are integers `0..4`; Layer 4 derives textual status;
9. every rating `1..4` cites selected claim or accepted assumption;
10. rating `4` cites no assumption; refs are unique/allowlisted;
11. unselected index claims never support ratings;
12. all semantic text fields are non-empty and bounded;
13. recommendations identify active/current unselected claims and valid roles;
14. removal refs are currently selected;
15. uncertainty refs are open/allowlisted and dispositions valid;
16. finding codes and all refs exist;
17. every action matches its exact discriminated shape, contains all required payload fields, and contains no fields owned by another kind;
18. action refs are allowlisted and agree with related refs/companion arrays;
19. omission findings have matching selection recommendations;
20. redundancy/out-of-scope findings have matching removals;
21. `assumption_supported_by_claim` pairs one assumption/uncertainty with active replacement claim(s);
22. `ask_user` actions resolve non-empty companion question IDs;
23. uncertain applicability has matching gap/uncertainty/question detail;
24. no Layer 4 policy field appears in raw output;
25. configured item/text limits are respected.

The repair prompt receives only diagnostics and identical canonical review input. A second invalid response
returns the reviewer operation error owned by `01-readiness-reviewer.md`. A valid but unfavorable judgment is never retried.

After validation, Layer 4 canonicalizes arrays, de-duplicates exact semantic duplicates, derives facet
statuses, injects weights/finding policy, synthesizes deterministic findings, and assembles the final
`04-results.md` readiness contract.

## 8. Validation invariants

- Every code appears exactly once in the registry.
- Category, severity, overrideability, and permitted actions are immutable within a released rubric version.
- Every action kind has one exact discriminated shape and bounded meaning.
- Final result policy fields come only from deterministic registries.
- Related refs and companion recommendations remain allowlisted and cross-consistent.
- Binding/path/schema/safety failures never masquerade as semantic findings.
- Raw reviewer output is never returned directly as authoritative host output.

### Final definition

> The structured review contract is one strict JSON assessment containing complete facet coverage,
> registered semantic findings, exact references, consequences, and bounded actions; deterministic Layer 4
> validates it and injects every policy field before the final `contextReadinessResult` is exposed.
