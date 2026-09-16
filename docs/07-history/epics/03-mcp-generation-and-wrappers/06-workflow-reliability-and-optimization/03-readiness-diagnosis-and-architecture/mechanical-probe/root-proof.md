# Provider-Free Local Contract Proof

- Machine authority: [`root-proof.json`](root-proof.json)
- Digest: `sha256:5f93e55027d8bf80daf2e42993559561efdc09a8a920221dd3251cf7f8c43d22`
- Azure calls: **0**
- Scope: mechanical root-boundary proof only

## Exact Witnesses

| Witness | Provider schema | Full schema | Backend result |
| --- | --- | --- | --- |
| Non-applicable coverage retains support at facets 3/6/7 | pass | pass | `invalid_coverage_combination` at the exact E1/E2 paths |
| Four selected claims used as recommendations | pass | pass | `invalid_recommendation_ref` at the exact E1/E2 paths |
| Locally corrected shape | pass | pass | valid, no issue |

The corrected shape clears rating and both support arrays for non-applicable/uncertain coverage and emits no recommendations when no unselected indexed claims exist. It changes no accepted readiness meaning.

## Contract Trace

- Prompt explicitly requires `rating:null` otherwise: **yes**.
- Prompt explicitly requires empty support arrays otherwise: **no**.
- Selected claims: 4.
- Indexed claims: 4.
- Selected/indexed overlap: 4.
- Unselected indexed claims: 0.
- Explicit `unselectedIndexedClaimRefs`: absent.

The same local contract gaps explain the identical high/medium first trigger and the four shared repair failures.

## Candidate Correction Boundary

1. State null rating plus empty `supportingClaimRefs` and `assumptionRefs` for non-applicable/uncertain coverage.
2. Expose `unselectedIndexedClaimRefs` directly, including an explicit empty array.
3. Prohibit recommendations when that allowlist is empty and make repair preserve deterministic action-policy constraints.

## Block 4 Proof Required

- Add failing exact E1/E2 regressions before production correction.
- Add prompt/projection packet assertions.
- Pass corrected fake first/repair/failure/interruption/no-rerun/security tests.
- Run one new-identity same-case live proof only after offline gates.

This proof supports selection of the local contract owner; it does not claim the correction implemented or verified.
