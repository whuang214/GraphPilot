# Block 6 Root Plan

**Owner: Integration Captain.** Lane agents read this document; they do not edit it.
Lane-local execution state belongs to [`lane-a/plan.md`](lane-a/plan.md) and
[`lane-b/plan.md`](lane-b/plan.md), and live cross-project status belongs to
[`00-current-state.md`](../../../../../05-delivery/01-current-state.md).

## Purpose

Sequence the two lanes so no two changes share one measurement, and hold the gates
that decide when a lane may start its next package.

## Current position

Lane A and Lane B are merged on `master` and verified together provider-free.
Baseline `run-workflow-audit-block6-integrated-01` is the current integrated
reference: 19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake
calls, 0 Azure calls, built-preview browser pass, compatibility key
`sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`.

**The checkpoint is adopted** (2026-07-30, user), so both lanes may run in parallel
from it:

| Lane | Worktree | Branch |
| --- | --- | --- |
| Lane A | `C:/Users/w105098/Desktop/Projects/GraphPilot` | `master` |
| Lane B | `C:/Users/w105098/Desktop/Projects/GP-LB2` | `lane-b-post-integration` |

Neither lane edits the other's tree. Shared and Captain-owned documents change on
`master` only, and Lane B rebases or merges them rather than editing them in its
worktree. The pre-integration worktrees `GP-LB`, `GP-B0`, and `GP-S05` are retained
history and are never executed from.

**Worktree roots must be 44 characters or shorter.** The longest tracked path is 214
characters (`lane-b/evidence/semantic-review-retry-wave/provider-free-correction.json`),
so a longer root exceeds the Windows 260-character limit and produces a partial
checkout. `…/Projects/GraphPilot` is exactly 44 and `…/Projects/GP-LB2` is 40; a
descriptive name like `GraphPilot-lane-b` is 51 and fails. This is the same platform
limit that Lane B's B0 package guards for live artifacts.

Retained behavior: Lane A A03/A04, Lane B B0 Windows path safety, and the Lane B
generation endpoint correction (`a17bc40`). The Lane B semantic review retry
(`b5ef422`) remains reverted by `a6e7ad0`; semantic behavior sits at the `5ec80b7`
baseline and its failed candidate is never rerun.

Cumulative provider use is 18 controlled + 1 external host = 19 aggregate against a
1000 ceiling.

## Gates

| # | Gate | Blocks | State |
| --- | --- | --- | --- |
| G1 | Human review and adoption of this integrated checkpoint | both lanes' next package | **closed** 2026-07-30 — adopted by the user |
| G2 | Re-rank the Block 6 backlog against the integrated baseline, replacing the pre-integration ranking | Lane B packet/cache/readiness/local/MCP/browser work | **closed** — ranking in [`lane-b/plan.md`](lane-b/plan.md) |
| G3 | New explicit user authorization bound to one anchor and one attempt | any provider or live run in either lane | **open** |
| G4 | Fresh lane worktrees created from the adopted checkpoint | parallel lane execution | **closed** — Lane B worktree created; Lane A owns `master` |

No provider call may be made while G3 is open, regardless of lane. With both lanes
live again, the standing invariant binds: no host/interface change and no
provider/runtime change ever share one measurement, so each lane baselines its own
candidate separately.

## Captain responsibilities

- Own this plan, the root [`README.md`](README.md), [`history/`](history/README.md), and shared status links.
- Resolve cross-lane conflicts from coherent final behavior, not from lane preference; canonical `docs/02-design-and-features/` wins over any delivery document.
- Approve each lane's transition into `implementing` and out of `verifying`.
- Keep every terminal identity immutable and never rerun.

## Next step

Both lanes are unblocked and run in parallel. Lane B's first package (B1) targets
the largest measured local cost in the integrated baseline and is provider-free, so
it needs no G3 authorization. Lane A selects its next package on `master`; the
integrated baseline's Lane A-owned finding is `host_boundary_evidence_simulated`.

## Integration record

The one-time merge and reorganization that produced this checkpoint — including its
inputs, verification, amendments, and outcome — is archived at
[`history/shared/lane-integration-record.md`](history/shared/lane-integration-record.md).
It is history, not an active plan.
