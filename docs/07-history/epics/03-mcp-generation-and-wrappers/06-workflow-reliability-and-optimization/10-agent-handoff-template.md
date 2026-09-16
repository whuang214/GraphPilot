# Block-Agent Handoff Template

## Purpose

Give each block agent one consistent start and return contract while preserving user/high-level review authority. This is a
template, not live status or approval to execute a block.

## Required Start Context

A block agent reads, in order:

1. repository `AGENTS.md` and `.devin/rules/graphpilot.md`;
2. root/docs and nearest backend/frontend/delivery README files;
3. the current-state board;
4. Epic 3 `00-epic.md`;
5. this roadmap group's `00-group.md`;
6. `01-success-contract.md`;
7. the assigned block document;
8. [`11-block-execution-and-parallelism.md`](11-block-execution-and-parallelism.md);
9. canonical product/architecture/MCP/feature owners relevant to the block;
10. prior block outcomes and exact committed evidence named by the high-level reviewer.

Historical reports and generated relationships are navigation evidence, not substitutes for current source and canonical
owners.

## Assignment Contract

```text
Block:
Approved question:
Current baseline commit/artifacts:
Owned scope:
Forbidden scope:
Inputs and dependencies:
Execution topology / slice DAG:
Critical path and justified sequential dependencies:
Parallel lanes and exclusive write ownership:
Forbidden/shared files and integration owner:
Worktree and shared-resource isolation:
Merge order and integration gate:
Required outputs:
Offline verification:
Potential live gate and maximum:
Overnight auto-advance boundary:
Stop/return conditions:
High-level review checkpoints:
```

The agent does not infer approval for implementation, live calls, promotion, destructive actions, or adjacent blocks.

## Planning Handoff

Before implementation, return:

- interpreted goal and user scenario;
- current evidence/code/doc audit;
- root assumptions and unresolved material choices;
- recommended design and strongest alternative;
- decisive trade-off and unresolved risk;
- intended slice DAG, critical path, parallel lanes, and justified sequential dependencies;
- exact exclusive/forbidden/shared file and resource ownership plus integration owner/gate;
- worktree/merge/overnight auto-advance and failure-cancellation plan;
- exact contracts/owners affected;
- rollback/reversibility;
- smallest offline proof;
- proposed live package/schedule/budget/stop rules when applicable;
- docs/status owners to update;
- plan-audit findings and disposition.

The user/high-level reviewer approves, revises, or stops the plan. Understanding does not equal approval.

## Implementation Handoff

After approved implementation and audit, return in this order:

1. **High level:** what changed and why, tied to the approved block question.
2. **Evidence:** expected versus observed behavior and key measurements/quality results.
3. **Changes:** files/areas by backend/frontend/docs/configuration.
4. **Verification:** exact PowerShell commands, counts, results, browser/live evidence, and unresolved failures.
5. **Live usage:** authorized maximum, actual calls by role/state, tokens/durations/IDs when available, stops/resume/no-rerun.
6. **Security/compatibility:** authority, secrets, raw content, paths, migrations, public contracts, rollback.
7. **Decisions/deviations:** approved direction, strongest alternative, material deviation, and why.
8. **Commits:** plan and implementation hashes; nothing pushed unless explicitly requested.
9. **Next recommendation:** proceed, return to an earlier block, rerun Block 1, start another optimization wave, or stop.

## Mandatory Evidence Hygiene

- Do not synthesize missing metrics, identities, outcomes, quality, or root cause.
- Separate host, Azure, MCP, local, and browser evidence.
- Label fake/provider-free evidence explicitly.
- Preserve stopped/failed/uncertain identities and no-rerun policy.
- Keep raw responses, prompts, reasoning, source dumps, secrets, and hidden golds out of reports/checkpoints/logs.
- Distinguish documented, implemented, verified, promoted, and certified states.

## High-Level Reviewer Checklist

The high-level reviewer checks:

- block scope and shared contract alignment;
- whether evidence supports the chosen root-cause boundary;
- cross-block dependencies and stale baselines;
- architecture/ownership and repository-structure consequences;
- whether the slice DAG maximizes safe parallelism with exclusive ownership/resource isolation and a valid integration gate;
- quality/security/compatibility/rollback;
- live schedule/budget/no-rerun integrity;
- implementation audit and required checks;
- whether Block 1 must be rerun;
- proceed/return/stop decision and next block assignment.
