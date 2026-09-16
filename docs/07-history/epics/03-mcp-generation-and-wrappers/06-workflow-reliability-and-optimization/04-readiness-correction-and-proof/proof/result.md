# Block 4 Readiness Correction Proof

- Machine authority: [`result.json`](result.json)
- Digest: `sha256:2de690fd030610ea65bbe61fe51cb71c8e468129cafe6b3a1e8ef65d0735e2f7`
- Source commit: `77fc7cb5643d5f982d0a3172f57d4afb2139c6f7`
- Correction commit: `3b9bcbdb10c41235904a674057b560e7dde9b53a`
- Manifest: `sha256:64f0ed0ce16b6e971f02ac617e180d72fde6358410c58edee0663934f57ec1a5`
- Observation: `sha256:6201c76e1e0667f1537e252318d535ffe35c2cfc3366bd74887e36c1ff667503`
- Scope: one visible mechanical same-case proof; no calibration/certification/promotion

## Result

The corrected medium-effort packet produced a backend-valid first response:

- terminal state: `completed`;
- capture: complete, no failure code;
- calls: 1 completed, 0 failed, 0 uncertain;
- first response valid: true;
- repair: not triggered;
- E1/E2 coverage trigger: absent;
- E1/E2 recommendation trigger: absent.

The readiness result is a valid blocked outcome:

- status: `needs_context`;
- score: 72;
- blocker: `conditional_facet_below_minimum`;
- blocker policy: coverage/blocking, overrideable, actions `select_existing_claim`, `search_source`, or `ask_user`.

This is a Block 4 **clean pass**: the initial review is valid and the backend returns a mechanically coherent blocked decision without retrying for a favorable outcome.

## Provider Actuals

| Field | Actual |
| --- | ---: |
| Duration | 51,706.8551 ms |
| Request bytes | 33,079 |
| Response bytes | 3,932 |
| Input tokens | 6,369 |
| Output tokens | 3,547 |
| Reasoning tokens | 2,679 |
| Cached input tokens | 0 |
| Requested/effective effort | `medium` / `medium` |
| Service tier | `default` |

Cumulative GraphPilot Azure accounting is **5 used / 995 remaining**, with 5 completed, 0 failed, and 0 uncertain calls.

## Before and After E2

| Metric | E2 medium before | Block 4 after | Delta |
| --- | ---: | ---: | ---: |
| Calls | 2 | 1 | **-50.00%** |
| Total provider duration | 103,921.2276 ms | 51,706.8551 ms | **-50.24%** |
| Input tokens | 12,544 | 6,369 | **-49.23%** |
| Output tokens | 8,013 | 3,547 | **-55.73%** |
| Reasoning tokens | 5,513 | 2,679 | **-51.41%** |
| Request bytes | 65,376 | 33,079 | **-49.40%** |
| Response bytes | 11,670 | 3,932 | **-66.31%** |

The correction removed the invalid-first/repair path. These are single-run before/after actuals, not a stability or promotion claim.

## Offline Proof

- Failing before: 2 characterization passes, 3 failures, 1 error.
- Exact passing after: 6/6.
- Focused readiness: 44 passed, 1 opt-in live skipped.
- Broader readiness/diagnosis/management: 124 passed, 1 skipped.
- Full backend: 1,015 passed, 5 skipped.
- Implementation audit: 0 critical, 0 high, 0 medium remaining.

## Durability and Safety

Manifest, checkpoint, observation, event ledger, and terminal digests close. The run contains exactly `checkpoint.json`, `metrics.jsonl`, `observation.json`, and `terminal.json`. No raw provider response, prompt, reasoning content, secret, or source dump is retained. The identity is terminal and must never rerun. Existing development servers on ports 5173 and 8000 were untouched.

## Limits and Gate

The safe live observation retains readiness summary and validation metadata rather than the complete private review. Offline tests remain authoritative for detailed blocker/ref/action invariants. This one visible case does not calibrate, certify, or prove representative stability.

Independent Block 4 exit audit accepted this `clean_pass` and recommends `proceed_to_block5_complete_live_anchor_and_reaudit`. Its three documentation-only medium findings—pass/skip count clarity, S02 Outcome, and current-state—are corrected; focused closure passed with zero critical, high, or medium finding.
