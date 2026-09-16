# Semantic Review Retry Live Result

- Machine authority: [`live-result.json`](live-result.json)
- Digest: `sha256:ed441b6895f12b09ac5c201b194064b4e72a16299d25bf1208c58e677127e84e`
- Candidate: `run-live-workflow-anchor-s`
- Terminal: **FAILED · `semantic_repair_failed` · non-retryable**
- Decision gate: **REVERT S10**

## Terminal Path

The sole authorized s1 candidate passed all pre-dispatch package, authorization, clean-source, budget, security, and 90-role B0 path gates. It then made exactly five completed calls with zero failed/uncertain provider calls:

1. readiness — first-response valid, 30,812.4006 ms;
2. generation — first-response valid, 36,813.0786 ms, no generation repair;
3. semantic review — response-contract valid, 70,810.3072 ms;
4. semantic candidate repair — 37,427.0195 ms;
5. semantic review — response-contract valid, 78,945.7297 ms, then terminal `semantic_repair_failed`.

No semantic-review response-repair call occurred. Capture is complete. Canonical persistence, SVG, final provenance/meaning evaluation, browser, and synthesis were correctly not reached after terminal failure. No retry or second candidate is allowed.

## Comparison and Decision

| Metric | Retained g2 | s1 | Delta |
| --- | ---: | ---: | ---: |
| Calls | 3 | 5 | +2 |
| Pre-browser ms | 139,960.6107 | 267,553.0795 | +127,592.4688 |
| Azure ms | 133,409.3706 | 254,808.5356 | +121,399.1650 |
| Request bytes | 119,899 | 176,715 | +56,816 |
| Response bytes | 25,178 | 46,073 | +20,895 |
| Input tokens | 24,033 | 35,635 | +11,602 |
| Output tokens | 13,526 | 25,755 | +12,229 |
| Reasoning tokens | 7,504 | 14,833 | +7,329 |

The strict retention gate fails: quality did not pass, delivery/browser gates were not reached, and no incremental benefit exists over g2. S10 must revert while all diagnosis/provider/live evidence, authorization, request, B0, and retained generation correction remain.

## Causal Boundary

S10 made the current V1 provider-visible finding contract coherent, and both semantic responses traversed without response-contract repair. The later semantic candidate-repair path is a separate quality path. The run does **not** prove that S10 caused semantic defects, improved reliability, or changed speed; g2 already had zero semantic response repair. The historical Block 5 repair duration receives no credit.

Independent terminal audit recomputed package/frozen manifest/result/observation/terminal/event/diagnostics bindings and found zero critical/high/medium evidence issue. Controlled accounting is now 18/1000; aggregate accounting is 19/1000.
