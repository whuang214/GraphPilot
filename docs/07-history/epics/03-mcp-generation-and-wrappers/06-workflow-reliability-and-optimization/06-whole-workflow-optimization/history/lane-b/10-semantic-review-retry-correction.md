# Slice 10: Semantic Retry Correction

## Purpose

Implement only the audited S09 finding-contract correction in the current private V1 and prove it provider-free without changing generation, scoring, repair policy, or public contracts.

## Execution Contract

- **Inputs:** committed audited S09 root and named failing-before regressions.
- **Outputs:** current-V1 prompt/projection/schema correction, tests, evidence, audit, full checks, one commit.
- **Exclusive ownership:** exact semantic files/tests/design named by S09 plus S10 Outcome/evidence.
- **Forbidden:** new V2 assets/identities, generation/B0/Lane A/shared docs, validator weakening, live identities/provider, `.env`, S15/Stage C.
- **Parallelism:** none.
- **Cancellation:** broader public/persisted contract need, quality weakening, or material audit/check failure returns to S09.

## Included Work

- Add exact failing-before initial/repair prompt, projection, schema, six-cell, and corrected-witness regressions.
- Project the backend-owned per-facet finding map into current-V1 private input.
- Update existing current-V1 initial/repair prompt assets in place with containing-facet, per-facet code, and applicable-below-minimum rules.
- Require the projection in current-V1 private input; preserve backend score/status/severity authority and one response repair.
- Run independent implementation audit and full backend/frontend/compatibility/security gates.

## Not In Scope

Generation, host, packet/cache, readiness, local/browser optimization; schema/public ID changes; semantic candidate repair redesign; live calls; promotion/certification.

## Target Areas

Only files named by S09, focused semantic tests, canonical generation/backend design, S10 evidence/Outcome.

## Exit Criteria

- Regressions fail before and pass after.
- Provider-visible and backend finding contracts are coherent without weakening validation.
- Current-V1-only policy is exact; no stale V2 behavior exists.
- Independent audit/full checks pass and one commit exists before S11 package creation.

## Previous Slice

[`09-semantic-review-retry-diagnosis.md`](09-semantic-review-retry-diagnosis.md)

## Next Slice

[`11-semantic-review-retry-proof.md`](11-semantic-review-retry-proof.md)

## Outcome

**Status:** Complete · S10 implemented/audited/committed at `b5ef422`, then behavior reverted after the sole S11 candidate failed the strict retention gate.

Eight named regressions failed before implementation with 18 expected failure records. The current private V1 correction derived `findingCodesByFacet` from backend authority, required it in both mode/repair inputs, and updated all four current V1 prompts in place. No V2 identity, compatibility branch, validator/scoring weakening, generation change, or provider call was introduced. Independent implementation audit found zero critical/high/medium issue.

Provider-free verification passed 15 named correction/preservation tests, 62 focused tests, the full backend suite (1080, 5 skipped), and complete frontend verify (419 unit, 43 e2e). Exact implementation evidence remains in [`evidence/semantic-review-retry-wave/provider-free-correction.md`](../../lane-b/evidence/semantic-review-retry-wave/provider-free-correction.md).

S11 proved both live semantic responses contract-valid without response repair, but required semantic candidate repair and terminalized `semantic_repair_failed`; g2 already had zero response repair. Because quality/browser gates and incremental benefit failed, S12 reverted only the production/schema/prompt/test/current-design behavior introduced by `b5ef422`. This Outcome and all diagnosis/provider/live evidence remain intentionally preserved.
