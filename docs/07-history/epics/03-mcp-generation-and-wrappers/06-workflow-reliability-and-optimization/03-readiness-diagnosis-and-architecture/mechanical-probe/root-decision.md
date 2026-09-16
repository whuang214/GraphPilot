# Block 3 Root Decision

- Machine authority: [`root-decision.json`](root-decision.json)
- Digest: `sha256:d9cea931d5e39a9f3720ee51cda1ca53d6a50c20cfec528096c9725eadef0d7c`
- Recommendation: `focused_implementation_correction`
- Owner: `readiness_prompt_projection_validator_contract`
- Confidence: high mechanical
- Independent exit audit: pass; 0 critical, 0 high, 0 medium

## Root Evidence

- High and medium reproduced identical `invalid_coverage_combination` paths at responsibility, concurrency, and exception paths.
- Both repairs reproduced four `invalid_recommendation_ref` paths while no unselected indexed claim existed.
- The prompt omits the empty-support half of the non-applicable coverage rule.
- The projection's selected/indexed lists completely overlap and expose no explicit unselected list.
- Provider-free witnesses reproduce both live trigger classes while provider/full schemas accept them.
- A locally corrected witness passes backend validation without changing accepted readiness meaning.

## Alternatives

- `provider_control_response`: disconfirmed as the validity root; medium is a latency/token optimization candidate.
- `readiness_component_redesign`: strongest alternative because generic complete-input repair is expensive and unreliable, but not the narrowest first remedy.
- `additional_evidence`: not required for root selection after cross-control and provider-free reproduction.

## Azure Accounting

- Completed: 4.
- Failed: 0.
- Uncertain: 0.
- Used: 4 of 1000.
- Remaining: 996.
- E1 and E2 are immutable terminal and must never rerun.

## Block 4 Boundary

1. State null rating plus empty support arrays for non-applicable/uncertain coverage.
2. Expose `unselectedIndexedClaimRefs`, including explicit empty state.
3. Prohibit recommendations when that list is empty and preserve deterministic action policies in repair.
4. Add exact failing E1/E2 regressions before implementation.
5. Pass corrected packet, first/repair/failure/interruption/no-rerun/security/compatibility tests.
6. Run one new-identity same-case medium live proof only after offline gates.

## Non-Goals

- No validator-policy, rubric, blocker-authority, response-schema, provenance, or persistence weakening.
- No component redesign unless focused correction fails.
- No medium-effort promotion until correctness is restored and separately evaluated.
- No calibration, certification, semantic-quality, or promotion claim.

## Rollback

Revert the focused prompt/projection/repair changes as one commit while retaining every Block 3 evidence and terminal artifact.
