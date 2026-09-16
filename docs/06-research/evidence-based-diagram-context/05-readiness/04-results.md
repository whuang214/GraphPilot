# Final Readiness Result

> **Status:** Historical final-result snapshot. Current intended behavior is owned by
> [`04-results.md`](../../../03-design/01-context-generation/01-readiness/05-results.md);
> runtime implementation has not started.
>
> **Scope of this doc.** This file is the single owner of the final backend-to-host
> `contextReadinessResult` JSON shape. The private LLM response lives in
> [`03-reviewer-json.md`](03-reviewer-json.md); deterministic calculation lives in
> [`02-policy-and-calculation.md`](02-policy-and-calculation.md); the overall flow and host loop live in
> [`01-readiness-reviewer.md`](01-readiness-reviewer.md).

## Purpose

Return one deterministic, validated readiness result containing grades, findings, consequences, actions,
score, and authoritative status. The host never receives the private LLM review as authoritative output.

## Complete result JSON

```json
{
  "schemaVersion": "graphpilot.context-readiness.v1",
  "kind": "contextReadinessResult",
  "requestId": "request-frontend-use-cases",
  "requestDigest": "sha256:exact-json-2-assessed",
  "manifestDigest": "sha256:current-manifest-digest",
  "diagramType": "use_case_diagram",
  "rubricVersion": "graphpilot.readiness.use_case.v1",
  "status": "needs_context",
  "readinessScore": 73,
  "canGenerate": false,
  "canOverride": false,
  "summary": "The request has a clear subject, actor, and goal but lacks a supported actor-to-goal association.",
  "coverage": [
    {
      "facet": "subjectBoundary",
      "applicability": "applicable",
      "status": "strong",
      "rating": 4,
      "weight": 3,
      "supportingClaimRefs": [
        {
          "id": "claim-frontend-boundary",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "The selected boundary claim clearly defines the frontend as the modeled subject."
    },
    {
      "facet": "actors",
      "applicability": "applicable",
      "status": "strong",
      "rating": 4,
      "weight": 4,
      "supportingClaimRefs": [
        {
          "id": "claim-customer",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "Customer is an active selected external-role claim."
    },
    {
      "facet": "actorGoals",
      "applicability": "applicable",
      "status": "strong",
      "rating": 4,
      "weight": 4,
      "supportingClaimRefs": [
        {
          "id": "claim-submit-order",
          "version": 1
        }
      ],
      "assumptionRefs": [],
      "rationale": "Submit Order is an explicit in-scope user-visible goal."
    },
    {
      "facet": "actorGoalAssociations",
      "applicability": "applicable",
      "status": "missing",
      "rating": 0,
      "weight": 4,
      "supportingClaimRefs": [],
      "assumptionRefs": [],
      "rationale": "No selected claim establishes participation between Customer and Submit Order."
    },
    {
      "facet": "useCaseRelationships",
      "applicability": "not_applicable",
      "weight": 2,
      "supportingClaimRefs": [],
      "assumptionRefs": [],
      "rationale": "No request, scope, selected/indexed claim, uncertainty, or accepted assumption indicates include, extend, generalization, or named extension-point meaning."
    }
  ],
  "recommendedSelections": [
    {
      "claimRef": {
        "id": "claim-customer-submits-order",
        "version": 1
      },
      "role": "primary",
      "reason": "Provides the missing in-scope actor-goal association.",
      "supportsFacets": [
        "actorGoalAssociations"
      ]
    }
  ],
  "removeSelections": [],
  "missingContext": [],
  "relevantUncertainties": [],
  "blockers": [
    {
      "id": "finding-required_facet_below_minimum-actorGoalAssociations",
      "code": "required_facet_below_minimum",
      "category": "coverage",
      "severity": "blocking",
      "facet": "actorGoalAssociations",
      "overrideable": false,
      "message": "No selected claim connects the Customer actor to the Submit Order goal.",
      "consequence": "Generation cannot create a grounded actor-to-use-case association and would have to guess participation.",
      "relatedClaimRefs": [],
      "relatedUncertaintyRefs": [],
      "relatedAssumptionRefs": [],
      "recommendedAction": {
        "kind": "select_existing_claim",
        "description": "Add the existing Customer-to-Submit-Order association claim.",
        "claimRefs": [
          {
            "id": "claim-customer-submits-order",
            "version": 1
          }
        ]
      }
    }
  ],
  "warnings": [],
  "questions": []
}
```

## Top-level fields

| Field | Required | Meaning |
| --- | --- | --- |
| `schemaVersion` | Yes | Constant `graphpilot.context-readiness.v1`. |
| `kind` | Yes | Constant `contextReadinessResult`. |
| `requestId` | Yes | JSON 2 request ID assessed. |
| `requestDigest` | Yes | Exact canonical JSON 2 digest assessed; binds attempt policies and debug records. |
| `manifestDigest` | Yes | Exact JSON 1 digest assessed. |
| `diagramType` | Yes | Concrete rubric/type assessed. |
| `rubricVersion` | Yes | Exact immutable selected rubric. |
| `status` | Yes | Authoritative readiness status. |
| `readinessScore` | Yes | Deterministic integer `0..100`; `null` only for `invalid`. |
| `canGenerate` | Yes | Whether current accepted generation policy may proceed. |
| `canOverride` | Yes | Whether all remaining blockers permit explicit user override. |
| `summary` | Yes | Concise human/host-readable result. |
| `coverage` | Yes | One validated assessment per selected-rubric facet; empty only for `invalid`. |
| `recommendedSelections` | Yes | Existing active claims recommended for JSON 2 addition. |
| `removeSelections` | Yes | Current selections recommended for removal. |
| `missingContext` | Yes | Required facts absent from JSON 1. |
| `relevantUncertainties` | Yes | Relevant uncertainty details and suggested disposition. |
| `blockers` | Yes | Blocking final findings. |
| `warnings` | Yes | Non-blocking final findings. |
| `questions` | Yes | Focused question items with stable result-local IDs used by typed `ask_user` actions; empty when none. |

## Coverage item

A coverage item contains:

- exact `facet` and `applicability`;
- backend-derived `status` and rubric `weight`;
- rating when applicable;
- exact selected supporting claim refs;
- accepted assumption refs;
- bounded rationale.

For `not_applicable` and `uncertain`, rating/status are absent. Exact score treatment belongs to
`02-policy-and-calculation.md`.

## Finding item

Every blocker/warning contains:

| Field | Meaning |
| --- | --- |
| `id` | Deterministic final finding identity. |
| `code`, `category`, `severity`, `overrideable` | Policy injected from the exact registry. |
| `facet` | Affected facet or `null` for selection-wide findings. |
| `message` | What is wrong or incomplete. |
| `consequence` | What generation would omit, simplify, assume, or risk. |
| related claim/uncertainty/assumption refs | Exact allowlisted context involved. |
| `recommendedAction` | Exact discriminated action payload from `03-reviewer-json.md`; the host decides and performs it. |

## Status behavior

| Status | Final-result behavior |
| --- | --- |
| `invalid` | Null score, empty coverage, no generation or override. |
| `needs_context` | One or more blockers; host follows actions and reassesses after actual context change. |
| `ready_with_warnings` | No blockers; host resolves or accepts warnings under 01 policy. |
| `ready` | No blocker or warning; generation may proceed. |

A reviewer/tool operation failure is not serialized as one of these statuses.

## Validation invariants

1. Envelope constants and request ID/digest, manifest digest, type, and rubric identities are exact.
2. Status/score/coverage combinations obey deterministic policy.
3. Coverage exactly matches the selected rubric in canonical order.
4. Final findings contain only registered policy fields and allowlisted refs.
5. Every final action preserves its validated discriminated shape and exact allowlisted references.
6. Recommendations/actions cross-reference the same exact claims, uncertainties, assumptions, and question IDs.
7. `canGenerate` and `canOverride` follow the 01 reviewer policy and cannot be chosen by the LLM.
8. The final result is returned to the host but not embedded into JSON 1 or JSON 2.

### Final definition

> `contextReadinessResult` is the one authoritative backend-to-host readiness JSON: a deterministically
> validated and calculated result assembled from the private semantic review plus immutable policy.
