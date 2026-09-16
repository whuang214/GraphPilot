# Block 4 Slice Group: Readiness Correction and Proof

## Goal

Implement only the Block 3 `focused_implementation_correction` owned by `readiness_prompt_projection_validator_contract`, prove the exact E1/E2 trigger classes are removed without weakening readiness authority, and run one bounded new-identity live proof before deciding whether Block 5 is safe.

## Authority and Inputs

- The [Block 4 owner](../05-block-04-readiness-correction-and-proof.md) owns correction/proof and the Block 5 gate.
- Block 3 root decision commit `4243d26` and [`root-decision.json`](../03-readiness-diagnosis-and-architecture/mechanical-probe/root-decision.json) authorize only the focused contract correction.
- E0, E1 high, E2 medium, and provider-free root proof are immutable evidence; E1/E2 identities never rerun.
- Accepted Block 2 code, parity evidence, identities, and artifacts remain read-only.
- Cumulative Azure budget is 4/1000 used, 996 remaining.

## Selected Correction

1. State explicitly that non-applicable or uncertain coverage requires `rating:null`, empty `supportingClaimRefs`, and empty `assumptionRefs`.
2. Add `unselectedIndexedClaimRefs` to the private readiness projection, computed deterministically as indexed minus selected and emitted as an explicit empty array when none exist.
3. Restrict raw `recommendedSelections` validation and reviewer instructions to that explicit allowlist.
4. Tell repair to emit no recommendations when the list is empty and to preserve deterministic action-policy constraints.

The validator policy, rubric, status/blocker authority, response schema, provenance, persistence, call ceiling, and no-rerun lifecycle do not change.

## Non-Goals

- No readiness-component/complete-input-repair redesign unless the focused correction fails and Block 3 is reopened.
- No effort-default change; medium remains a separately measured optimization candidate.
- No generation or semantic-review Azure call.
- No calibration, certification, promotion, representative matrix, S15, or Stage C.
- No public MCP/REST/request/schema identity change and no dependency addition.

## Execution Topology

```text
S01 Contract Correction and Offline Proof
  failing E1/E2 regressions → focused implementation → audit/full verification → commit
  ↓
S02 Live Proof and Exit
  new medium manifest → independent audit → readiness + natural repair maximum → result audit → Block 5 decision
```

The slices are sequential because S02 must bind the clean S01 implementation commit and exact corrected assets. No parallel live work is permitted.

## Slice Ownership and Gates

| Slice | Depends on | Outputs | Exclusive write ownership | Forbidden/shared ownership | Gate |
| --- | --- | --- | --- | --- | --- |
| S01 | Block 3 exit `4243d26` | exact failing regressions, prompt/projection/validator/repair correction, canonical docs, offline report | readiness prompts, `context_readiness_service.py`, `readiness_review_validator.py`, focused readiness tests, readiness design docs | validator policy/rubric/result schema, generation/review runtime, Block 2, provider, S15 | failing-before proof, implementation audit, focused/full backend, packet/digest/security/compatibility |
| S02 | committed S01 | one audited medium live manifest, immutable result, before/after report, Block 4 Outcome and Block 5 decision | new Block 4 diagnosis identities/result evidence, this group/Outcome/status, ignored supervisor reports | further correction before result audit, generation/review, effort promotion, calibration/certification, S15/Stage C | manifest audit, max-two-call execution, terminal/evidence audit, complete regression/security/compatibility gate |

## Proof Contract

### Offline

- Exact E1/E2 `invalid_coverage_combination` and `invalid_recommendation_ref` witnesses fail before correction.
- Corrected prompt text and projection packet expose every required rule/allowlist directly.
- Corrected fake first response passes without repair for the exact case.
- Natural repair remains bounded and can produce a valid result when independently scripted invalid-first/valid-second.
- Completed-invalid repair, provider failure, capture failure, interruption, terminal resume/no-rerun, path/secret bounds, and manifest identity remain exact.
- Existing ready/blocked/non-overrideable blocker and all broader backend tests pass.

### Live

After S01 commits and an independent package audit, run one new-identity same-case medium manifest:

- one `readiness` call;
- optional `readiness_response_repair` only if naturally reached;
- call 3 impossible;
- no generation or semantic review;
- checkpoint before dispatch and immutable terminal/no-rerun;
- safe metadata and exact validation `{code,path}` only.

A valid first response is a clean mechanical pass. A naturally repaired valid result is repair-dependent evidence. Another invalid terminal triggers result audit and either a bounded same-root correction or return to Block 3 if the responsible boundary changed.

## Risks and Rollback

- Prompt changes may affect other cases; focused and full readiness tests are mandatory.
- The private projection field changes packet bytes/digest; every consumer and test fixture must update atomically.
- Repair may expose another policy error; do not broaden into component redesign silently.
- Rollback is one forward revert of S01 while all Block 3/4 live artifacts remain immutable.

## Slice Plan

| Slice | Plan | Status |
| --- | --- | --- |
| 01 · Contract Correction | [`01-contract-correction.md`](01-contract-correction.md) | Complete · `3b9bcbd` |
| 02 · Live Proof and Exit | [`02-live-proof-and-exit.md`](02-live-proof-and-exit.md) | Complete · clean pass, Block 5 authorized |

## Plan Audit

Independent review initially conflated future implementation absence with plan defects, then identified real specification gaps: exact regression method/path signatures, repair action-policy rules, private projection consumers, E1/E2 reuse prohibition, live identity pattern, design owners, and repair-dependent acceptance authority. All were corrected. A fresh reviewer found one medium request for explicit E1/E2 `{code,path}` tuples; S01 now lists every exact tuple, including E2's action-policy characterization. Focused re-audit passed with zero critical, high, or medium finding.

## Acceptance Criteria

- The exact selected root—not a broader redesign—is implemented.
- Failing-before and passing-after evidence proves both E1/E2 trigger classes.
- Readiness authority and all safety/quality invariants remain unchanged.
- All provider calls are new-identity, audited, terminal, counted, and never rerun.
- Independent implementation and live-result audits retain no critical/high/medium finding.
- Block 5 starts after a clean proof or a repair-dependent proof accepted by the independent Block 4 exit audit under this approved contract and recorded in S02 Outcome; otherwise return to Block 3 or remain in Block 4.

## Related Docs

- [`../05-block-04-readiness-correction-and-proof.md`](../05-block-04-readiness-correction-and-proof.md)
- [`../01-success-contract.md`](../01-success-contract.md)
- [`../11-block-execution-and-parallelism.md`](../11-block-execution-and-parallelism.md)
- [`../03-readiness-diagnosis-and-architecture/mechanical-probe/root-decision.md`](../03-readiness-diagnosis-and-architecture/mechanical-probe/root-decision.md)
- [`../../../../../02-design-and-features/08-context-backed-generation/01-readiness/README.md`](../../../../../03-design/01-context-generation/01-readiness/README.md)
