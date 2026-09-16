# Slice 01: Contract Correction

## Purpose

Add exact failing regressions for the E1/E2 trigger classes, implement the narrow prompt/projection/validator/repair correction, and prove readiness behavior and lifecycle safety offline before any new live call.

## Design

Keep the existing private readiness response schema and deterministic policy. Make currently implicit contract rules explicit in the provider packet:

- prompt: null rating and both support arrays empty for non-applicable/uncertain coverage;
- projection: `unselectedIndexedClaimRefs = indexedClaimRefs - selectedClaimRefs` in deterministic order, including `[]`;
- validator: raw recommendations must resolve to this explicit list;
- repair prompt: no recommendations when the list is empty; preserve exact action policies—selection uses explicit unselected refs, removal uses selected refs, search uses allowlisted uncertainties, ask uses existing question IDs, replacement uses paired allowlisted assumption/uncertainty/claim refs, and every action agrees with its finding refs.

## Execution Contract

- **Depends on / inputs:** Block 3 exit commit `4243d26`, exact E1/E2/root-proof signatures, current readiness source/tests/design.
- **Outputs:** failing-before regressions, focused production correction, passing-after evidence, docs, and one coherent implementation commit.
- **Exclusive write ownership:** `backend/assets/prompts/readiness-review*.md`, `backend/services/readiness/context_readiness_service.py`, `backend/services/readiness/readiness_review_validator.py`, focused readiness tests, readiness design docs, this Outcome.
- **Forbidden/shared ownership:** readiness rubric/policy/result/response schemas, generation/semantic review, Block 2, diagnosis lifecycle schemas/service/command, provider calls, `.env`, S15, Stage C.
- **Resources:** fake clients and temporary workspaces only; no Azure/browser/ports.
- **Cancellation:** a required broader contract/schema/policy change, weakened authority, dependency, or material audit/check failure returns to Block 3.

## Included Work

- In `backend/tests/readiness/test_semantic_readiness_service.py`, add `test_e1_invalid_coverage_combination_signature`, asserting exactly `invalid_coverage_combination` at `$.coverage[3]`, `$.coverage[6]`, and `$.coverage[7]`; add `test_e2_invalid_recommendation_ref_signature`, asserting exactly `invalid_recommendation_ref` at `$.recommendedSelections[0].claimRef` through `[3].claimRef` plus the E2 `action_not_permitted @ $.holisticFindings[0].recommendedAction.kind` characterization.
- Add failing packet tests `test_prompt_exposes_non_applicable_empty_support_contract` and `test_repair_prompt_exposes_empty_recommendation_and_action_contract` in that module.
- In `backend/tests/readiness/test_context_readiness_service.py`, add failing `test_projection_exposes_unselected_indexed_claim_refs`, asserting deterministic indexed-minus-selected order and explicit `[]`.
- Add validator coverage proving raw recommendations resolve only through `unselectedIndexedClaimRefs`.
- Implement the smallest prompt/projection/validator/repair edits.
- Update all direct private-projection consumers atomically: `ContextReadinessService` writes the field; `ReadinessReviewValidator` reads it; `test_context_readiness_service.py`, `test_readiness_release_fixtures.py`, and `test_live_readiness_reviewer.py` fixtures/assertions include it.
- Prove first-valid and invalid-first/valid-repair paths plus completed-invalid, provider failure, interruption, capture, terminal, no-rerun, and secret/path boundaries.
- Update canonical readiness design and backend/testing owners without changing public contracts.
- Run independent implementation audit, focused/full backend, schema/digest/security/compatibility, and Block 2 unchanged checks.
- Commit the verified correction.

## Not In Scope

Live calls, repair architecture redesign, reasoning-effort defaults, response-schema/rubric/policy changes, generation/review, calibration/certification/promotion, S15, Stage C, dependencies, or public API changes.

## Target Areas

- `backend/assets/prompts/readiness-review.md`
- `backend/assets/prompts/readiness-review-repair.md`
- `backend/services/readiness/context_readiness_service.py`
- `backend/services/readiness/readiness_review_validator.py`
- `backend/tests/readiness/test_context_readiness_service.py`
- `backend/tests/readiness/test_semantic_readiness_service.py`
- `backend/tests/readiness/test_readiness_release_fixtures.py`
- `backend/tests/readiness/test_live_readiness_reviewer.py`
- diagnosis regression tests only where exact lifecycle proof is reused
- `docs/02-design-and-features/08-context-backed-generation/01-readiness/01-readiness-reviewer.md`
- `docs/02-design-and-features/08-context-backed-generation/01-readiness/04-reviewer-json.md`
- this Outcome

## Exit Criteria

- Exact E1/E2 witnesses fail before and pass after correction.
- Prompt, projection, validator, and repair share one explicit allowlist/rule contract.
- The exact case can produce a valid fake first response without repair.
- Bounded repair/failure/interruption/no-rerun behavior remains intact.
- No policy, rubric, blocker, schema, provenance, persistence, public, or Block 2 behavior changes.
- Independent audit and required checks have no material failure.

## Previous Slice

[`../03-readiness-diagnosis-and-architecture/08-root-decision-and-transition.md`](../03-readiness-diagnosis-and-architecture/08-root-decision-and-transition.md)

## Next Slice

[`02-live-proof-and-exit.md`](02-live-proof-and-exit.md) after implementation commits and the repository is clean.

## Outcome

**Status:** Complete. Exact provider-free characterization tests reproduce E1's three `invalid_coverage_combination` paths and E2's four `invalid_recommendation_ref` paths plus action-policy error. Four packet/contract tests failed before implementation for the missing prompt rule, repair rule, explicit allowlist, and validator use; all six focused before/characterization tests pass after correction.

**Implementation:** The first prompt now requires null rating plus empty claim/assumption support for non-applicable/uncertain facets and distinguishes recommendation/action refs from broader finding refs. The private projection emits deterministic `unselectedIndexedClaimRefs = indexed - selected`, including `[]`; recommendations and `select_existing_claim` actions validate against that exact list. Repair prohibits impossible recommendations and states each existing action-policy allowlist. All direct fixtures/consumers and the canonical readiness reviewer/JSON owners were updated atomically; validator policy, rubric, blocker/status authority, response schema, provenance, persistence, diagnosis lifecycle, public contracts, and Block 2 are unchanged.

**Audit and deviations:** Independent implementation audit found no critical/high issue and two medium concerns: private-v1 versioning and prompt findings/recommendations ambiguity. The additive private digest-bound v1 policy is now canonical and decision-logged; prompt roles are separated. An explicit empty-list edge assertion was added, and the remaining low documentation wording was made exact. Focused re-audit passed with zero critical, high, or medium finding. No scope deviation or dependency occurred.

**Verification:** Failing-before gate produced 3 failures + 1 error with two exact-signature tests passing. Passing-after exact gate passed 6 tests. Focused readiness ran 45 tests (44 passed, 1 opt-in live skipped); broader readiness/diagnosis/management ran 125 (124 passed, 1 skipped); full backend ran 1,020 (1,015 passed, 5 skipped). Django check, compileall, `git diff --check`, secret scan, consumer inventory, and Block 2 unchanged-path checks passed. No Azure call, `.env` access/change, browser, port, S15/Stage C access, push, or deployment occurred.
