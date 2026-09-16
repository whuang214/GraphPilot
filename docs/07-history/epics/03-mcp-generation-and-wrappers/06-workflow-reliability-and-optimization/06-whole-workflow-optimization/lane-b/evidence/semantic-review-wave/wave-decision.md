# Semantic Review Wave Decision

- Machine authority: [`wave-decision.json`](wave-decision.json)
- Decision digest: `sha256:2efe25f7c686182518efee385a96dcb385ed653a5de1a6518d4df8ad9efe5a19`
- Decision: **REVERTED**
- Claim state: `unmeasured_candidate_reverted`

## Comparison

Block 5 remains the accepted controlled live baseline: 186,759.6726 ms complete wall, five calls, one 37,787.5872 ms semantic-review response-repair call, and quality/browser pass.

The only authorized candidate failed before checkpoint, MCP, provider, quality, or browser work because its derived Windows evidence path exceeded the active limit. Its zero calls are not an optimization benefit. It has no compatible complete-wall denominator, so absolute/percentage wall, call, token, cache, repair, quality, and reliability effects are all `not_measured`.

## Revert

S04 restored every S02 production/test/prompt/schema/trace/canonical-design file exactly to baseline `a4f52ba` and removed the four unpromoted prompt assets. Rollback commit `3ccf5cf` passed independent audit, 117 focused tests, and the full backend suite of 1,047 tests with 5 skipped. S01 diagnosis, authorization, ignored manifest/package terminal, and tracked S03 evidence remain immutable.

Per the user's clarification, future authorized private-contract work changes the current V1 in place; no compatibility obligation remains for the reverted V2 layer.

## Provider-Free Guard

`run-workflow-audit-block6-semantic-review-revert-20260729-01` passed on `3ccf5cf`:

- 19 observations: 16 generated, 1 blocked, 2 expected errors, 0 interrupted;
- 56 fake calls, zero Azure calls;
- all quality failures zero;
- recovery 4/4 with two finalized-output reuse and two terminal no-rerun proofs;
- built-preview browser pass;
- accepted compatibility key unchanged at `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`;
- manifest `sha256:b58245bb88ab320e8913f699734b0fb22d53d423dc2060ab5881344872cac5cc`;
- report `sha256:fdfcbc928ac87e2dab6afa2efbd4467601f9362ade83e5cfcb1beb612c4aa639`;
- browser `sha256:becacf084db0ebae1bfbf85f3145157eacc9faca49e64ca0c8a0bbe3a4333294`;
- four-entry append-only ledger `sha256:a00573f9f787614dbcf52e5a677347977de6b9e84d6d15e4e20f67022321994c`.

Its 27,126.6787 ms complete wall is fake-provider orchestration evidence, not a live speed denominator.

## Accounting and Safety

Controlled calls remain 10 completed, 0 failed, 0 uncertain; aggregate remains 11 completed, 0 failed, 0 uncertain. No raw provider content, secret, S15 identity, Stage C, calibration, certification, promotion, deployment, or push occurred.

## Audit

Independent local-filesystem audit rebuilt the manifest/report/browser/ledger evidence, verified all 19 terminal observations, append-only ledger prefix, zero Azure, quality/recovery/browser results, exact baseline restoration, candidate no-call state, and resource cleanup. It found zero critical, high, or medium issue; five report findings remain informational contributors only.

## Next

The next measured owner is the separate generation endpoint contract (`bdd_relationship_endpoints_invalid @ $.edges[3]`, 26,052.5176 ms repair). Its S05–S08 plan is independently audited and S05 provider-free diagnosis is ready; the live-harness identity-path preflight remains mandatory before any future authorization, and S07 has no live authority. The semantic-review root remains diagnosed but is deferred after this reverted one-attempt wave.
