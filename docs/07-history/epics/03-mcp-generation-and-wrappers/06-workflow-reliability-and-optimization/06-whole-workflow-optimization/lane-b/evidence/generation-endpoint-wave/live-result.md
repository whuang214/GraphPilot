# Generation Endpoint Live Result

- Machine authority: [`live-result.json`](live-result.json)
- Digest: `sha256:a3ee176b9eb431c0c19120e403562e7ab64160d2569599e306c2a93796c954e5`
- Candidate: `run-live-workflow-anchor-g`
- Decision: **RETAIN S06**
- Provider calls: **3 completed, 0 failed, 0 uncertain**

## Result

The one authorized short package passed B0 with 88 roles and an exact 259-unit longest diagnostics path. Its manifest, 36 compatibility assets, short source/evidence/request, authorization, budget, and clean source were independently audited before dispatch.

The candidate generated successfully with only `readiness`, `generation`, and `semantic_review` calls. Generation was first-response valid and used no `generation_repair`. Semantic review also happened to be first-response valid with unchanged baseline code/assets; no semantic response or candidate repair occurred. Readiness remained 91/ready, reviewed quality was 100/pass, diagnostics were complete, and no operation warning was emitted.

The persisted four-node/four-edge BDD contains the exact controller/probe/relay definitions, ownership roles/multiplicities, Integer sample interval plus attached default-30 note, probe-relay association ends, and exact claim provenance. Forbidden cloud/network/heating/alarm/deployment/runtime meaning is absent. JSON, SVG, compact trace, diagnostics, API load, and browser identity all bind and pass; browser API returned 200 with zero console/page/network errors.

## Comparison

| Metric | Block 5 | Candidate | Delta |
| --- | ---: | ---: | ---: |
| Complete wall ms | 186,759.6726 | 140,007.6107 | -46,752.0619 (-25.0333%) |
| Azure ms | 180,843.1247 | 133,409.3706 | -47,433.7541 |
| Calls | 5 | 3 | -2 |
| Input tokens | 38,710 | 24,033 | -14,677 |
| Output tokens | 20,546 | 13,526 | -7,020 |
| Reasoning tokens | 9,754 | 7,504 | -2,250 |
| Request bytes | 193,171 | 119,899 | -73,272 |

Only the **26,052.5176 ms generation-repair removal** is attributed causally to S06. The semantic response-repair call did not occur, but semantic code/assets were unchanged; its absence and the remaining wall difference are observational, not credited to the generation correction.

## Guard and Audit

Post-retention provider-free guard `run-workflow-audit-b6g1-guard-01` passed after supplying the isolated worktree's existing interpreter through a temporary ignored junction: 19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake calls, zero Azure, browser pass, and unchanged compatibility `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`. The junction and all owned browser/server processes were removed.

Independent terminal audit rebuilt every digest/binding, call ledger, checklist/provenance result, browser evidence, path plan, and comparison and found zero critical/high/medium issue. Controlled calls are now 13/1000; aggregate calls are 14/1000.

The earlier wave-01 package was rejected before freeze at 313 path units, made zero calls, and remains non-dispatchable. The g2 identity is immutable terminal and must never rerun.
