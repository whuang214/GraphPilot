# Block 6 · Whole-Workflow Optimization

Navigation for Block 6. Two causal lanes optimize the request-to-visible-diagram
workflow one measured wave at a time; this folder holds their active plans, their
completed history, and the evidence both produced.

Live cross-project status stays in [`00-current-state.md`](../../../../../05-delivery/01-current-state.md).
This folder never restates it.

## Layout

| Path | Owns |
| --- | --- |
| [`plan.md`](plan.md) | Integration Captain only — cross-lane sequencing and the adoption/authorization gates. |
| [`lane-a/`](lane-a/README.md) | Host and integration preparation. **Active** on `master`. |
| [`lane-b/`](lane-b/README.md) | GraphPilot workflow and business logic. **Active** in the `lane-b-post-integration` worktree. |
| [`history/`](history/README.md) | Read-only completed work: the retired slice documents and the superseded cross-lane plans. |
| [`evidence/`](evidence/README.md) | Combined integration and Lane B exit evidence only. Per-lane evidence lives under its lane. |
| [`authorization/`](authorization/README.md) | **Legacy.** Frozen live-run approvals. Closed to new entries. |

## Lanes

Each lane permanently owns exactly two documents — `README.md` (navigation and
current state) and `plan.md` (bounded package state). Substantial work may add one
`work/<nn>-<name>.md` holding that package's whole lifecycle. Minor work stays as a
row in the lane plan. Conventions: [`.devin/rules/graphpilot.md`](../../../../../../.devin/rules/graphpilot.md).

- **Lane A · Host and integration preparation** — GraphPilot-owned host contracts,
  backend-derived evidence values, validation feedback quality, and MCP/session
  guidance. The host agent's model, index, and cache are external and are never
  measured as GraphPilot work.
- **Lane B · Workflow and business logic** — first-response contract validity and
  avoidable provider calls first; packet, cache, sequence, and MCP work later; local
  and browser work only when measured contribution justifies it.

No host/interface change and provider/runtime change ever share one measurement.

## Current checkpoint

Both lanes are integrated on `master` and verified provider-free. Baseline
`run-workflow-audit-block6-integrated-01`: 19 observations, 16 generated, 1 blocked,
2 expected errors, 56 fake calls, 0 Azure calls, built-preview browser pass,
compatibility key `sha256:d77f21f8…`. Retained: Lane A A03/A04, Lane B B0 Windows
path safety, and the Lane B generation endpoint correction. The Lane B semantic
review retry stays reverted.

The checkpoint is **adopted** (2026-07-30) and the backlog is re-ranked against it,
closing gates G1, G2, and G4. Both lanes are unblocked and run in parallel from it:
Lane A owns `master`, and Lane B works in its own worktree on branch
`lane-b-post-integration`. See the [root plan](plan.md) for the worktree map.

Provider and live work remains **not** authorized anywhere in this block (G3).
Lane B's current package is provider-free and does not need it.

## Related

- Final intended design: [`docs/03-design/`](../../../../../03-design/) — canonical, and it wins over any delivery document here.
- Workflow audit design: [`09-workflow-audit-design.md`](../../../../../03-design/11-workflow-audit.md)
- Block entry: [`07-block-06-whole-workflow-optimization.md`](../07-block-06-whole-workflow-optimization.md)
- Block success contract: [`01-success-contract.md`](../01-success-contract.md)
