# Lane B Exit and Integration Handoff

- Machine authority: [`exit-handoff.json`](exit-handoff.json)
- Digest: `sha256:880c6fce1f68a9e64fd3390a884d6920db51ccbdff42344e077a24dbb9c7958f`
- Lane B source checkpoint: `03eb8efee55424d650504142de016acce0894e94`
- Status: **STOPPED ON GENUINE LANE A DEPENDENCY**

## Final Lane B State

Lane B retains Windows path safety (`4f02b0a`), the audited generation endpoint diagnosis (`ef2361d`), and generation correction (`a17bc40`). The g2 candidate passed complete quality/browser proof with three calls and 140,007.6107 ms complete wall. Only elimination of its 26,052.5176 ms generation-repair call is credited causally.

The current-V1 semantic correction (`b5ef422`) passed provider-free implementation audit but its sole live candidate used five calls and ended non-retryable `semantic_repair_failed`. Because g2 already had zero semantic response repair, the correction had no eligible repair saving and failed quality/browser/incremental gates. `a6e7ad0` restores all S10 behavior files exactly to pre-S10 content while preserving diagnosis/provider/live evidence.

The final provider-free guard passes: 19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake/0 Azure calls, browser pass, compatibility `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`, and cumulative ledger `sha256:b1fc9b876a4cfda4cc9a9ac68272c1dd5f483d8fe6918287970e30c95554eeb0`.

## Call Ledger

| Source | Controlled | Aggregate |
| --- | ---: | ---: |
| Before retained g2 | 10 | 11 |
| g2 generation candidate | +3 | +3 |
| s1 semantic candidate | +5 | +5 |
| **Final** | **18/1000** | **19/1000** |

All eight new provider calls completed. Provider failed/uncertain accounting remains 0/0; s1 failed at workflow semantic quality, not provider transport. Aggregate remaining is 981.

## Lane A Dependency

Lane A `master` is clean at `89d66b3`; Lane B and Lane A diverge from `4bd7ba4` with 15 and 9 commits respectively. Lane A is not integration-ready:

- A03 implementation is complete, but its required independent cold-host retest is outstanding.
- A04 is blocked on that retest.
- A07 is blocked on A05/A06.
- A09 is blocked on A08.

Therefore no combined baseline exists. Packet/cache, readiness, local attribution, and MCP/browser reassessment are not valid on the stale pre-integration baseline and were not started.

## Integration Captain Sequence

1. Complete Lane A's fresh independent A03 cold-host retest.
2. Complete the Lane A dependency chain through A09 and freeze its approved checkpoint.
3. Create a dedicated integration worktree from that Lane A checkpoint; do not reuse either active lane worktree.
4. Integrate Lane B **after** Lane A. Resolve canonical-owner documentation for one coherent final behavior; do not reintroduce reverted S10 behavior.
5. Before integration, preserve/copy byte-for-byte both package trees, both run trees, both evaluated workspaces (`workspaces/run-live-workflow-anchor-g/` and `workspaces/run-live-workflow-anchor-s/`), both guard-run trees, and `.graphpilot/evaluation/workflow-audit/baseline-ledger.json` at digest `sha256:b1fc9b876a4cfda4cc9a9ac68272c1dd5f483d8fe6918287970e30c95554eeb0`. The ledger is cumulative: later accepted rebaselines append through production service; they never overwrite historical entries. Never rerun terminal identities.
6. Run a complete provider-free integrated rebaseline.
7. Only then re-rank packet/cache, readiness, local, MCP, and browser domains.
8. Update shared current-state/backlog/ledger/decision/Captain files only under integration ownership.

## Rollback Map

- **Generation endpoint (`a17bc40`)** — retained. If an integrated rebaseline fails compatibility or quality, preserve g2 evidence and revert only this commit. Keep B0 and S05 diagnosis.
- **Windows path safety (`4f02b0a`)** — retained independently; do not revert while Windows live packages rely on preflight.
- **Semantic retry (`b5ef422`)** — already reverted by `a6e7ad0`; no further behavior rollback. Preserve S09–S12 evidence and never rerun s1.

## Resource and Cleanup State

Ports `15173`, `18080`, `18991`, `15174`, and `18081` are free; no managed browser or provider/audit server remains. The guard unexpectedly materialized `C:\Users\w105098\GP-LB\.venv` as an ordinary ignored directory (9,107 files, 104,838,501 bytes). It was deleted after explicit user confirmation; the external project venv remains intact. No local cleanup item remains.
