# Semantic Review Retry Decision

- Machine authority: [`wave-decision.json`](wave-decision.json)
- Digest: `sha256:a3ef61b896bbbf928e45e32b8690a79723776ceb1614f0c94ba0f2bbe8e39106`
- Decision: **REVERT S10; RETAIN generation correction and B0**

The current-V1 semantic finding contract was correctly implemented and provider-free audited, but the sole authorized live candidate failed the approved retention gate. It used five calls, reached one semantic candidate-repair round, and ended non-retryable `semantic_repair_failed`. It was 127,592.4688 ms slower pre-browser than g2 and never reached canonical persistence, final meaning/provenance, browser, or synthesis gates. g2 already had zero semantic response repair, so no historical repair saving is eligible.

Commit `a6e7ad0779e36c636efb17394d8161d5ea3f338e` restores all 17 S10 behavior files exactly to pre-S10 `5ec80b7` content. S10's Outcome and provider-free evidence, S09 diagnosis, authorization/request, immutable s1 package/run, and S11 terminal evidence remain. Generation correction `a17bc40` and B0 are unchanged.

Post-revert provider-free guard `run-workflow-audit-b6s1-guard-01` passed: 19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake/0 Azure calls, built-preview browser pass, and retained compatibility `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`.

Controlled accounting is 18/1000; aggregate accounting is 19/1000. Failed/uncertain provider-call accounting remains zero because all five provider calls completed and the workflow failed at semantic quality. No retry or identity reuse is allowed.

Erratum: the committed S11 `live-result.json` summary omitted the final `0` from its event-ledger digest. The immutable observation and recomputed 30-event ledger bind the correct `sha256:91076eaa150cc962f75c64f1ff2b73c7f1f7e7a45c3c2b89f8c4707ee6d4a2e0`; result/observation/terminal and this decision are unaffected.

The next dependency is the Lane A integration checkpoint and complete rebaseline. Packet/cache or readiness work must not start before that dependency is resolved.

Reserved ports are free and no managed browser/provider worker remains. A guard-created ignored `C:\Users\w105098\GP-LB\.venv` directory remains pending explicit deletion confirmation because it materialized as a non-empty directory rather than a removable junction.
