# E1 High-Effort Readiness Diagnosis

- Machine authority: [`e1-result.json`](e1-result.json)
- Digest: `sha256:c8059f5d1d5fa1c604dc41340480e759899f364623c233c49b228c209bb83a56`
- Source commit: `bf8836116614dc676fce80feb27d8a7ed1cb856d`
- Manifest: `sha256:2a90ccbe5a0b548c4653eb564a3378a7b661a562c23fb16249d3be2f220f837d`
- Observation: `sha256:49f3332ca11141348d018dfc858700e13c6c6541fd73864aba3056c8f8917ef8`
- Provider control: requested/effective `high`; service tier `default`
- Scope: diagnostic mechanical/provider/performance evidence only

## Terminal Result

The exact new identity terminalized `error` with `readiness_reviewer_validation`. Capture is complete, both provider calls completed, no call is uncertain, and the identity must never rerun.

| Role | State | Valid | Duration ms | Input | Output | Reasoning | Cached |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `readiness` | completed | false | 86,530.4834 | 6,280 | 7,198 | 5,888 | 0 |
| `readiness_response_repair` | completed | false | 117,021.6661 | 6,264 | 10,404 | 9,144 | 0 |
| **Total** | — | — | **203,552.1495** | **12,544** | **17,602** | **15,032** | **0** |

Budget after E1: **2 used / 998 remaining**.

## Exact First-Response Trigger

The first response was structurally accepted but failed deterministic semantic validation:

- `invalid_coverage_combination @ $.coverage[3]` — `responsibility`
- `invalid_coverage_combination @ $.coverage[6]` — `concurrency`
- `invalid_coverage_combination @ $.coverage[7]` — `exceptionPaths`

The validator requires non-applicable or uncertain coverage to carry `rating:null`, no selected-claim support, and no assumption support. The prompt explicitly says rating must be null otherwise, but it does not explicitly say both support arrays must be empty.

This exact trigger naturally started repair; the event was persisted before repair dispatch.

## Repair Result

Repair eliminated the first trigger but introduced four new deterministic failures:

- `invalid_recommendation_ref @ $.recommendedSelections[0].claimRef`
- `invalid_recommendation_ref @ $.recommendedSelections[1].claimRef`
- `invalid_recommendation_ref @ $.recommendedSelections[2].claimRef`
- `invalid_recommendation_ref @ $.recommendedSelections[3].claimRef`

The prompt says to use indexed unselected claims. The exact projection contains four selected claims, four indexed claims, complete overlap, and **zero unselected indexed claims**. The model must infer a set difference that is empty because the projection exposes no explicit unselected allowlist.

## Causal Assessment

Supported:

1. The first live trigger is deterministic semantic validation—not response size or structural schema rejection.
2. Prompt/projection does not express both validator-owned rules in the most direct machine-followable form.
3. Complete-input repair is a cost amplifier and did not recover a valid review under high effort.

Not disconfirmed:

- provider/control behavior may affect compliance and latency;
- the readiness response/repair responsibility may be structurally overloaded;
- prompt-only changes may not eliminate both failure classes.

No corrective root is selected yet.

## Next Discriminator

Freeze and audit the identical case/assets at medium effort under new identities. Changing only reasoning effort determines whether the trigger classes persist across control before choosing a focused local correction, a component redesign, or continued evidence.
