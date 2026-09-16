# E2 Medium-Effort Readiness Diagnosis

- Machine authority: [`e2-result.json`](e2-result.json)
- Digest: `sha256:32ff890695b635e7ed40337a88031758a793a4f809db6bd4957dbbd226394733`
- Source commit: `6c33e3c5fd7f157c84a26eb96012b77673a1d39f`
- Manifest: `sha256:26f826a5824974ef17a724e9be1f93baa998ba8a4cec5424fd7eb47b2801a51b`
- Observation: `sha256:523fe3aa0b4d5dbcb28c7678cde34a1d263ae921d5350070ad2e76a3cf8ba549`
- Provider control: requested/effective `medium`; service tier `default`
- Scope: diagnostic mechanical/provider/performance evidence only

## Terminal Result

E2 used the identical case and 16 frozen assets as E1 and changed only reasoning effort materially. It terminalized `error` with `readiness_reviewer_validation`; both calls completed, capture is complete, and no state is uncertain.

| Role | State | Valid | Duration ms | Input | Output | Reasoning | Cached |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `readiness` | completed | false | 46,883.1366 | 6,280 | 4,030 | 2,833 | 0 |
| `readiness_response_repair` | completed | false | 57,038.0910 | 6,264 | 3,983 | 2,680 | 0 |
| **Total** | — | — | **103,921.2276** | **12,544** | **8,013** | **5,513** | **0** |

Cumulative budget after E2: **4 used / 996 remaining**.

## Trigger Reproduction

The first response reproduced E1's exact three issues and paths:

- `invalid_coverage_combination @ $.coverage[3]` — `responsibility`
- `invalid_coverage_combination @ $.coverage[6]` — `concurrency`
- `invalid_coverage_combination @ $.coverage[7]` — `exceptionPaths`

The trigger therefore persists across high and medium effort on the same case and frozen assets.

Repair reproduced E1's four invalid recommendation refs and added one action-policy error:

- `action_not_permitted @ $.holisticFindings[0].recommendedAction.kind`
- `invalid_recommendation_ref @ $.recommendedSelections[0..3].claimRef`

## High versus Medium

| Metric | High | Medium | Medium delta |
| --- | ---: | ---: | ---: |
| Total provider duration | 203,552.1495 ms | 103,921.2276 ms | **-99,630.9219 ms (-48.95%)** |
| First-call duration | 86,530.4834 ms | 46,883.1366 ms | **-45.82%** |
| Repair duration | 117,021.6661 ms | 57,038.0910 ms | **-51.26%** |
| Input tokens | 12,544 | 12,544 | 0 |
| Output tokens | 17,602 | 8,013 | **-54.48%** |
| Reasoning tokens | 15,032 | 5,513 | **-63.32%** |
| Request bytes | 65,376 | 65,376 | 0 |
| Response bytes | 11,497 | 11,670 | +1.50% |

Reasoning effort materially affects latency and token usage, but it is not the first-response invalidity root for this case.

## Candidate Root

`focused_implementation_correction` at `readiness_prompt_projection_validator_contract` is the narrowest supported candidate:

1. E0 reproduces provider-schema/backend-validator gaps offline.
2. E1 and E2 reproduce the same exact first semantic trigger across controls.
3. The prompt omits the support-array half of the non-applicable coverage rule.
4. The projection supplies no explicit unselected-claim allowlist; selected and indexed lists completely overlap.
5. Both generic repairs produce the same four invalid recommendation refs.

The strongest alternative is `readiness_component_redesign`: generic complete-input repair is expensive and unreliable. It remains an amplifier/alternative, but a focused prompt/projection correction is the smaller first remedy for the repeated trigger.

Medium is a latency optimization candidate, not a correctness fix. Targeted repair is deferred until correctness is restored and repair remains necessary.

## Proposed Block 4 Boundary

- Make non-applicable/uncertain coverage requirements explicit: null rating and empty support arrays.
- Expose an explicit unselected indexed-claim allowlist or state that it is empty.
- Prohibit recommendations when that allowlist is empty and make repair preserve deterministic action policies.
- Add exact E1/E2 witness regressions and packet assertions.
- Prove first/repair/failure/interruption/no-rerun/security/compatibility offline.
- Use a new-identity same-case live proof only after offline correction passes; never rerun E1 or E2.

No root is final until independent Block 3 exit audit passes.
