# Slice 04: Recommendation and Handoff

> Historical S04 plan/Outcome only. Its human-dependency stop was superseded by the active S05 causal diagnosis authorization; it does not govern current execution or Block 4 transition.

## Purpose

Integrate provider-free diagnosis and review-package state, issue exactly one evidence-supported Block 3 recommendation, and record the truthful proceed/stop boundary for Block 4.

## Design

Apply the Block 3 recommendation enum exactly once:

- `focused_implementation_correction`
- `readiness_component_redesign`
- `broader_context_workflow_redesign`
- `provider_control_response`
- `additional_evidence`

Evidence thresholds are:

| Recommendation | Minimum evidence |
| --- | --- |
| `focused_implementation_correction` | Repeated exact validation `{code,path}` owner plus a provider-free reproduction showing one local correction removes the defect without changing accepted meaning; material alternatives are disconfirmed. |
| `readiness_component_redesign` | Multiple reviewed cases show failures caused by the response/repair responsibility split itself, and bounded local corrections cannot preserve the contract; provider/control and broader host ownership are disconfirmed. |
| `broader_context_workflow_redesign` | Reviewed evidence shows the missing/duplicated responsibility originates before readiness or crosses host/readiness/generation authority; local/component/provider corrections cannot resolve it. |
| `provider_control_response` | Same frozen reviewed cases/contracts are valid offline and reproducibly differ by provider/control with semantic parity gates; GraphPilot prompt/schema/validator/workflow causes are disconfirmed. |
| `additional_evidence` | No unique owner meets a threshold above, a decisive validation event is missing, or required reviewed/live authority is absent. |

Do not choose among corrective directions when the decisive validation trigger remains unknown. While the review package lacks two genuine reviews and adjudication, the expected recommendation is `additional_evidence`; S04 records `blocked_dependency`, the exact missing human evidence, and the safe resume action. It does not mark Block 3 passed or authorize Block 4.

If S02 unexpectedly proves one root offline, pause and re-audit the plan before selecting a corrective recommendation; do not widen silently. A completed review package still requires a newly frozen live package and independent package audit before any Azure call.

## Execution Contract

- **Depends on / inputs:** passed S02/S03 outputs and exact review state.
- **Outputs:** one recommendation, Block 3 Outcome/handoff, current-state, durable weekend checkpoint/report.
- **Exclusive write ownership:** this Outcome, group status, current-state, decision index only if intended design changes, weekend state/handoff.
- **Forbidden/shared ownership:** readiness code/prompts/schemas/policy, review answers, provider calls, S15, Block 4 implementation.
- **Resources:** no provider/browser/server; final read-only audit only.
- **Cancellation:** missing human review or unsupported root keeps Block 3 blocked; no alternate recommendation is added.

## Included Work

- Reconcile diagnosis report, case package, and actual review/adjudication state.
- Record exactly one recommendation with owner/confidence, strongest alternative, decisive trade-off, affected consumers/contracts, compatibility/security, rollback, smallest offline proof, required live proof, and non-goals.
- Run independent Block 3 evidence/package/handoff audit and resolve every material finding.
- Update current-state and durable weekend files truthfully.
- Commit all executable safe work before stopping.

## Not In Scope

- Live package execution, human-review fabrication, Block 4 plan/implementation, promotion, certification, push, or deploy.

## Target Areas

- this group and Outcome
- `docs/03-development-and-delivery/epics/00-current-state.md`
- `docs/02-design-and-features/decision-decisions.md` only when a corrective design is actually selected
- `.devin/weekend-state.json` and `.devin/weekend-handoff.md`

## Exit Criteria

- Exactly one recommendation exists and follows the evidence.
- Proposal/documentation/implementation/verification/approval states are distinct.
- Missing human/live evidence is explicit and agent review is not called human review.
- Block 4 starts only if Block 3's root-cause exit gate truly passes; otherwise state is `blocked_dependency` with exact resume instructions.
- Independent audit has no unresolved critical/high/medium finding.

## Previous Slice

[`02-provider-free-diagnosis.md`](02-provider-free-diagnosis.md) and [`03-human-review-package.md`](03-human-review-package.md)

## Next Slice

[Block 4: Readiness Correction and Proof](../05-block-04-readiness-correction-and-proof.md) only if Block 3 passes; otherwise remain in Block 3.

## Outcome

**Status:** `blocked_dependency`. S02 exhausted current provider-free evidence and S03 prepared/audited/browser-tested the exact visible bridge package, but case `case-readiness-diagnostic-block3-activity-return-authorization-01` remains `pending_two_human_reviews_and_adjudication`, `expected: null`, and `liveEligible: false`. No genuine review, adjudication, newly frozen live package, or live validation event exists. Block 3 therefore does not pass its root-cause exit gate, and Block 4 is not authorized.

**Selected recommendation (exactly one):** `additional_evidence`.

- **Owner / confidence:** `block3_readiness_diagnosis` / high confidence that stopping is required; no corrective root is assigned.
- **Reason:** the decisive real first-response validation trigger and genuine reviewed-case authority are both absent. Full-projection repair is a proven cost amplifier, not the trigger.
- **Strongest unselected alternative:** readiness-component redesign for targeted repair. It may reduce repair cost, but acting now could optimize the wrong defect or conceal semantic invalidity; exact repeated validation `{code,path}` evidence must come first.
- **Affected consumers/contracts:** the S02 diagnostic contracts/service and S03 package remain additive and unchanged; readiness runtime, prompt, schema, rubric, policy, MCP/REST, calibration, generation certification, and Block 2 compatibility are unaffected.
- **Smallest offline proof:** obtain two distinct genuine human-review exports and one distinct adjudication for the exact case/digest; validate all three against the package-local schemas; then freeze and independently audit one new readiness-only package with new identities, current source/assets, maximum two roles, checkpoint/terminal ordering, no-rerun, zero generation/review reachability, and budget closure.
- **Required live proof:** execute only that newly authorized package and retain exact first/repair validation `{code,path}` events plus safe provider metadata. Use the result to test the existing hypotheses against S04's thresholds; do not infer a correction from repair entry alone.
- **Rollback / security / compatibility:** S04 changes documentation and supervisor state only; revert its commits to remove the handoff. No migration, dependency, secret access, public/runtime change, provider call, push, or deployment occurred.
- **Non-goals:** no human-answer fabrication, S15 reuse, Stage C, Azure construction/authentication probe, correction design, Block 4 work, calibration/certification claim, promotion, or provider/default change.

**State distinctions:** the recommendation is documented and provider-free verified; the review package is implemented and browser verified; human approval is incomplete; live-package proposal/freeze/audit/execution are `not_run`; corrective design/implementation/verification are `not_run`; Block 4 remains `blocked_dependency`. Agent/subagent audits are not human review.

**Audit and verification:** Independent handoff audit confirmed the sole selected recommendation, evidence threshold, state distinctions, missing dependencies, compatibility/security/rollback, and Block 4 stop. Its only medium finding was the missing/stale durable supervisor state and Captain report; both were corrected. Focused re-audit returned no critical, high, or medium finding. JSON/recommendation/case parity, the mandated report title plus nine ordered sections, 500-word current-state limit, secret and diff checks, and browser/process/port cleanup passed.

**Safe resume:** two independent humans review the exact S03 package as Reviewer A and Reviewer B, then a distinct human adjudicates their exports. After those records validate and the case is explicitly adjudicated, return to Block 3—not Block 4—to create and audit a new maximum-two-call live package. Never resume or rerun S15 identities.
