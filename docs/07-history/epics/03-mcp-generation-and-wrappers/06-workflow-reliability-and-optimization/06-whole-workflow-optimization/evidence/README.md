# Block 6 Combined Evidence

Evidence that belongs to **both lanes or to the integration itself**. Per-lane wave
evidence lives with its lane, in [`../lane-a/evidence/`](../lane-a/evidence/) and
[`../lane-b/evidence/`](../lane-b/evidence/).

## Contents

| Path | What it is |
| --- | --- |
| [`lane-b-exit/`](lane-b-exit/) | The Lane B exit handoff. Binds the retained and reverted commits, the terminal `g2`/`s1` results, the call accounting, the rollback map, and the exact immutable local artifact paths. Authority for what the integration had to preserve. |
| [`block6-integration-preservation.json`](block6-integration-preservation.json) | Byte-for-byte preservation manifest for the Lane B local artifacts copied into this worktree: path, size, and SHA-256 per file, plus the copy/verify action taken. |

## Local runtime artifacts

The `.graphpilot/evaluation/` trees these manifests describe are **untracked runtime
state**, not repository content. They are preserved in the working tree, never
rewritten, and never deleted. The preservation manifest is how their integrity is
checked after any move or copy.

Master's baseline ledger at
`.graphpilot/evaluation/workflow-audit/baseline-ledger.json` is append-only. The
Lane B checkpoint ledger was preserved separately as
`baseline-ledger-lane-b-checkpoint.json` rather than overwriting it, and its two
accepted guard baselines were appended to master's ledger through
`WorkflowAuditLedgerService` with stale-write checks.

## Adding evidence here

Only add evidence that no single lane owns — integration runs, rebaselines, and
cross-lane handoffs. Anything produced by one lane's package belongs to that lane.
Never edit a self-digested artifact in place; its digest is its identity.
