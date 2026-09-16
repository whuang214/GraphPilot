# Slice 02: Readiness Rubric and Policy

## Purpose

Turn the promoted exact per-type readiness rubrics and deterministic Layer 4 policy into executable, offline
backend assets and pure policy code.

## Background

This is the first code slice. It starts only after slice `01` makes the active readiness package authoritative.
It deliberately avoids JSON 1/JSON 2 persistence and every LLM boundary.

## Design

Normative machine rubric JSON remains the design owner. `ReadinessRubricService` loads/validates backend assets
protected by parity tests. `ReadinessPolicyService` owns pure deterministic applicability, included facets,
assumption cap, score, finding order, overrideability, and authoritative status.

## Included Work

- Add one versioned rubric asset for each generatable MVP type and none for `custom`.
- Add rubric identity, facet, applicability, anchor, weight, minimum, and gap-policy validation.
- Add readiness contract types needed by deterministic calculation.
- Implement included-facet/denominator, effective rating, assumption cap, weighted score/rounding, stable
  finding order, and status precedence.
- Add deterministic fixtures for ready, warning, blocking, not-applicable, uncertain, and invalid cases.

## Not In Scope

- JSON 1/JSON 2 schemas or files.
- Layer 1 preflight or reviewer projection.
- LLM reviewer calls, MCP tools, context generation, provenance, or frontend work.

## Target Areas

- `backend/assets/readiness/rubrics/`
- `backend/services/readiness/readiness_rubric_service.py`
- `backend/services/readiness/readiness_contract.py`
- `backend/services/readiness/readiness_policy_service.py`
- `backend/tests/readiness/test_readiness_rubric_service.py`
- `backend/tests/readiness/test_readiness_policy_service.py`

## Exit Criteria

- Rubric assets exactly match the promoted normative JSON.
- Assumption cap, score, status, and ordering fixtures pass deterministically.
- Invalid rubric/result inputs fail without guessing or repair.
- Targeted and full backend suites pass offline without Azure credentials.

## Previous Slice

- [`01-active-design-promotion.md`](01-active-design-promotion.md)

## Next Slice

- [`03-evidence-and-request-schemas.md`](03-evidence-and-request-schemas.md)

## Outcome

Completed the deterministic, offline readiness foundation. Added three runtime rubric assets under
`backend/assets/readiness/rubrics/`, byte-identical to the approved activity, use-case, and BDD normative JSON;
`custom` intentionally has no rubric. Added frozen rubric/coverage/finding/status/policy contracts,
`ReadinessRubricService` with strict v1 invariant validation and per-type caching, and `ReadinessPolicyService` for
canonical coverage order, applicability handling, assumption cap, weighted round-half-up score, synthesized
coverage/assumption findings, stage ordering/de-duplication, authoritative status, and overrideability.

Implementation followed red-green testing: the two new test modules first failed on missing readiness contracts,
then passed after implementation. Independent review found that raw rating `4` plus assumption refs must be
rejected before calculation while the assumption cap remains as defense-in-depth; the implementation and tests
were corrected accordingly. The rubric accessor lives in `services/shared/` rather than the passive
`services/diagrams/catalog/` package because it performs cached file access, matching the existing schema-access pattern;
this changes no service responsibility.

Verification: 19 targeted readiness tests pass; the complete offline backend suite passes 427 tests; service
bytecode compilation and `git diff --check` pass. No JSON 1/JSON 2 schema, persistence, preflight/reviewer, LLM,
MCP, `OperationProblem` migration, context generation, frontend behavior, commit, or push was included.

Follow-up: [`03-evidence-and-request-schemas.md`](03-evidence-and-request-schemas.md).
