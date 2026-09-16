# Slice 12: Semantic Retry Decision

## Purpose

Retain or revert the semantic retry from exact terminal evidence, run the provider-free guard, and hand the resulting Lane B baseline to Lane A integration/rebaseline.

## Execution Contract

- **Inputs:** audited S11 terminal/browser evidence and retained g2 baseline.
- **Outputs:** retain/revert decision, guard, lane-specific ledger evidence, rollback and Lane A dependency handoff.
- **Exclusive ownership:** semantic retry decision evidence and S12 Outcome; shared integration docs remain reserved.
- **Forbidden:** next-wave implementation, provider calls, evidence mutation, cross-case overclaim, promotion/certification, S15/Stage C.
- **Integration gate:** correction retains only if incremental measured benefit over g2 exceeds noise/risk/complexity and all guards pass; otherwise revert S10 while preserving evidence.

## Included Work

- Compare complete wall, semantic role validity/duration/tokens/bytes/cache, total calls, generation control, quality, browser, and reliability.
- Attribute only changes supported by the semantic correction; do not credit stochastic provider variation.
- Retain or revert; run a new provider-free baseline/guard on the final behavior.
- Update controlled/aggregate accounting and provide the exact Lane A integration dependency.

## Not In Scope

Lane A merge/rebaseline, packet/cache/readiness/local implementation, representative validation, promotion/certification.

## Target Areas

S12 Outcome and `evidence/semantic-review-retry-wave/` only.

## Exit Criteria

- Decision follows the strict incremental gate and independent audit.
- Missing/non-causal effects are labeled observational or not measured.
- Final behavior passes provider-free guard and has exact rollback/accounting.
- Lane A dependency handoff is precise; no shared-file integration occurs here.

## Previous Slice

[`11-semantic-review-retry-proof.md`](11-semantic-review-retry-proof.md)

## Next Slice

Lane A integration and complete rebaseline, or a precise dependency stop.

## Outcome

**Status:** Complete · REVERT S10 behavior; RETAIN generation correction/B0; final guard PASS.

The sole s1 candidate failed non-retryable `semantic_repair_failed` after five completed calls: readiness, generation, semantic review, semantic candidate repair, semantic review. Both semantic responses were response-contract valid and no response-repair call occurred, but reviewed quality, persistence, browser, and synthesis gates did not pass. Candidate pre-browser wall was 267,553.0795 ms versus g2 139,960.6107 ms, with five calls versus three. Because g2 already used zero semantic response repair, contract coherence alone was not incremental benefit and the strict gate required rollback.

Rollback commit `a6e7ad0779e36c636efb17394d8161d5ea3f338e` restores every S10 behavior file exactly to pre-S10 `5ec80b7` while preserving S09/S10 provider-free evidence, authorization/request, immutable package/run, and S11 terminal evidence. Retained generation correction `a17bc40` and B0 are unchanged. No retry or candidate identity reuse is allowed.

Post-revert guard `run-workflow-audit-b6s1-guard-01` passed with 19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake/0 Azure calls, browser pass, and compatibility `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`. Controlled/aggregate accounting is 18/1000 and 19/1000. Machine decision is [`evidence/semantic-review-retry-wave/wave-decision.json`](../../lane-b/evidence/semantic-review-retry-wave/wave-decision.json). The next mandatory dependency is Lane A integration and complete rebaseline before packet/cache or readiness work.
