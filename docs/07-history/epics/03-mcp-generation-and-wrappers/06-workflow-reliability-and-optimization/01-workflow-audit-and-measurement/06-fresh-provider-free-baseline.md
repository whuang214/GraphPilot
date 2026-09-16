# Slice 06: Fresh Provider-Free Baseline

## Purpose

Run the completed reusable audit against the exact current repository, record the fresh pre-Block 2 provider-free baseline,
and hand Block 2 a truthful parity authority.

## Design

Run only after Slices 01–05 and every provider-free/failure/recovery/security/browser-safe gate pass. Use new run, scenario,
observation, and baseline identities. The run records exact commit, scenario/schedule/assets/dependencies/platform/browser mode,
outputs, cold/warm state, W01–W22 coverage, non-overlapping accounting, quality, recovery, browser completion, ranked findings,
and compatibility key.

The fresh baseline replaces no historical evidence. S13–S15 remain prior observations and the stopped S15 identities are never
loaded, migrated, resumed, or rerun. No Azure client is constructed and no live budget is opened.

## Execution Contract

- **Depends on / inputs:** all committed S01–S05 outputs, a tracked-clean exact commit, and the complete provider-free command.
- **Outputs:** one immutable fresh run/report/ledger entry, compatibility key, ranked handoff, and Block 1 exit evidence for
  Block 2 planning.
- **Exclusive write ownership:** one gitignored workflow-audit run package and Slice 06/group/current-state Outcome updates.
- **Forbidden/shared ownership:** production code/configuration, live/S15 identities, and unrelated user artifacts are forbidden;
  all canonical docs/status and final commit belong to the primary integration owner.
- **Parallelism/resources:** no parallel measurement or write slice; use one new run/baseline identity, exact sequential
  cold/warm cache order, isolated control/evaluated roots, ports `15173`/`18080`, and a unique browser session/profile.
- **Merge/integration gate:** S06 is the block integration gate and reruns complete backend/frontend/MCP/browser/security/diff
  checks, validates report/ledger identity, audits the combined implementation, and only then hands parity evidence to Block 2.

## Included Work

- Audit the final run command, default scenarios, manifest, call ceilings, output path, and zero-provider boundary before run.
- Run focused schema/scenario/capture/runner/browser/report/ledger/command gates.
- Run the complete backend, Django, stdio, compile, frontend, browser, diff, and security gates.
- Execute one complete baseline run with a new exact identity and mandatory built-preview browser proof.
- Validate the immutable report and ledger entry, including digest, compatibility key, completeness, and no-secret scan.
- Review ranked findings for evidence quality and route each to Block 2, a later owning block, or defer.
- Update this Outcome, the Block 1 group plan, parent roadmap/epic navigation, current-state board, test counts, and relevant
  current commands/results.
- Commit the verified baseline handoff without committing generated local audit artifacts.

## Not In Scope

- Azure/provider-backed calls, H/M screening, Stage C, readiness/generation certification, or promotion.
- Implementing any ranked optimization or beginning Block 2 before the handoff is audited.
- Treating provider-free fixture quality/timing as live provider or representative evidence.
- Deleting or rewriting S13–S15 evidence or local canonical user artifacts.

## Target Areas

- `.graphpilot/evaluation/workflow-audit/` local generated run package (gitignored)
- this slice/group and parent roadmap/epic/current-state owners
- backend/frontend/testing READMEs only where current commands/results change

## Exit Criteria

- The baseline run is complete, immutable, schema-valid, secret-safe, and recorded exactly once with new identities.
- Every material W01–W22 boundary is measured, derived, or explicitly unavailable with reason/confidence.
- Complete-wall accounting is non-overlapping; fake-provider work is local and Azure is exactly not called.
- All normal/guard scenario quality, failure, recovery, no-rerun, and browser gates pass.
- The report and ledger entry share exact report digest and compatibility key and are valid Block 2 parity authority.
- Exact verification commands/results and generated artifact locations/digests are recorded in Outcome.
- Block 1 is implementation-audited with no unresolved material finding before the implementation commit.

## Previous Slice

[`05-reports-and-baseline-ledger.md`](05-reports-and-baseline-ledger.md)

## Next Slice

Audit and plan [Block 2: Repository Architecture and Enablement](../03-block-02-repository-architecture-and-enablement.md)
using this slice's exact compatibility key and baseline report.

## Outcome

**Status:** Complete. The committed S01–S05 package at HEAD `c1ea9d85fbcb043e014306894fa42d0bcacb52d2` produced and
accepted baseline `baseline-workflow-audit-block1-baseline-20260724-01` through run
`run-workflow-audit-block1-baseline-20260724-01`. The exact clean-tree command was:

```powershell
cd backend; uv run python manage.py run_workflow_audit baseline --run-id run-workflow-audit-block1-baseline-20260724-01 --control-workspace "C:\Users\w105098\Desktop\Projects\GraphPilot" --json
```

It completed 19/19 observations: 16 generated anchors/repair guards, one expected readiness block, two expected provider-failure
errors, zero interruptions, 56 fake calls, and zero Azure calls. All observations contain W01–W22, exact terminal state, expected
provider role/order, and zero quality failures. Recovery exercised two exact finalized-output reuses and two terminal no-reruns
with zero calls after recovery.

**Browser and accounting:** Built-preview browser proof passed for the representative cold/warm pair with exact 8-node/7-edge
identity and empty console/page/failed-response evidence. The accepted report records 426 ms representative browser time,
25,772.9598 ms total declared accounting scope, 808.3462 ms simulated host, 0 Azure, 1,003.4041 ms MCP, 23,419.1337 ms
local, and 116.0758 ms residual. Browser coverage is explicitly representative 2/19, not full-schedule coverage.

**Durable local artifacts:** Generated files are gitignored and remain under:

- manifest: `.graphpilot/evaluation/workflow-audit/runs/run-workflow-audit-block1-baseline-20260724-01/manifest.json`
- report JSON/Markdown: the same run root's `report.json` and `report.md`
- browser evidence: `browser-evidence/<observation-id>.json` under the run root
- ledger: `.graphpilot/evaluation/workflow-audit/baseline-ledger.json`

Exact identities/digests:

| Evidence | Identity / digest |
| --- | --- |
| Manifest | `sha256:52e031f957133ed142bd16706bca80f4ab7eb00ae3301818f7b6a25b7f87cdc8` |
| Report | `sha256:c3e3dedaf412bf413c9bb517aadd5125b95f73f7c3771ad0beb7153ed4031b9e` |
| Browser aggregate | `sha256:89b4b656a9760d92681d878cf4285228e8fd770347be4fe6a3472fdccc47a831` |
| Ledger | `sha256:c696d9a2ba3a482558943381cba18d531ea2eee26f7d6265fd3e32dd0f3720fe` |
| Compatibility key | `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1` |

A second invocation reused all 19 observations, both browser artifacts, report, and ledger entry with identical digests and no
provider/browser rerun.

**Ranked handoff:** The report records information-only findings: profile the 23,419.1337 ms local contributor before proposing
change; retain/diagnose the 1,003.4041 ms MCP contributor; retain representative browser and residual evidence; and separately
capture/import W01–W03 real host evidence. These are ceilings/coverage gaps, not promised savings or live-provider claims.

**Audit and deviations:** The first read-only exit agent could not access gitignored files and returned a false
`blocked_dependency`. A second general-profile audit was constrained to read-only tools, recomputed every manifest/report/
browser/ledger/observation/terminal digest, verified HEAD and security, and passed runtime integration with no critical, high,
or medium defect. It identified only tracked closure plus two low documentation path/vocabulary drifts, corrected in this
commit. No S15 identity was loaded, migrated, resumed, or rerun; no Stage C or provider budget opened.

**Verification:** The baseline command and an idempotent resume passed with identical five digests and reused observations,
browser evidence, report, and ledger. Final post-baseline gates passed:

- `cd backend; uv run python manage.py test` — 991 passed, 5 skipped;
- `cd backend; uv run python manage.py check` — no issues;
- `cd backend; uv run python mcp_server/smoke_test.py` — all real-stdio checks passed;
- `cd backend; uv run python -m compileall -q api mcp_server services tests` — passed;
- `cd frontend; npm run verify` — lint/build passed, 419 unit/component and 43 Chromium E2E passed;
- built-preview baseline browser proof — exact cold/warm identity, empty console/page/network failures, no leftover ports/sessions;
- `git diff --check` — passed.

The final handoff uses the compatibility key above as Block 2 parity authority.
