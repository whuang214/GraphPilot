# Block Execution and Parallelism

> **Scope.** This policy governs blocks that use the repository-default slice model.
> It does **not** apply to
> [`06-whole-workflow-optimization/`](06-whole-workflow-optimization/README.md),
> which uses the lane work-package model owned by
> [`.devin/rules/graphpilot.md`](../../../../../.devin/rules/graphpilot.md). That group
> has no `00-group.md`, so the `## Execution Topology` and slice-concurrency-table
> requirements below do not bind it; its cross-lane sequencing lives in its root
> plan. Everything here still binds every other block.

## Purpose

Require every future block agent to design an evidence-based slice execution topology that maximizes safe overnight
parallelism without weakening slice commits/tests, dependency order, measurement causality, live-call controls, or
high-level/user review gates. This policy does not predefine any block's slices or authorize implementation.

## Block and Slice Model

Roadmap blocks remain dependency-ordered high-level questions and gates. Each approved block is later decomposed into
implementation slices. A slice is the coherent commit/test/audit unit; an optimization wave is one or more tightly related
slices with one causal owner.

```text
Block plan and audit
→ approved slice DAG
→ ready slices execute sequentially or in parallel
→ each slice tests/audits/commits independently
→ integration slice/gate
→ block exit review
```

Blocks normally advance sequentially because each consumes the previous block's approved output. Parallelism is primarily
inside a block. Downstream blocks may perform explicitly assigned read-only lookahead, but they do not finalize designs,
write code, run live calls, or claim block start before their dependencies pass.

## Required Execution Topology

Every detailed block `00-group.md` must include an `## Execution Topology` section before implementation. It must show the
slice dependency DAG rather than only a numbered list.

Example:

```text
S01 Foundation
 ├── S02 Backend lane
 ├── S03 Frontend lane
 └── S04 Evaluation lane
          ↓
      S05 Integration
          ↓
      S06 Block proof
```

A linear DAG is valid only when the plan explains why every dependency is real and why no slices can execute safely in
parallel.

## Required Slice Concurrency Table

Every block plan includes a table with at least these fields:

| Slice | Depends on | Inputs | Outputs | Exclusive write ownership | Forbidden/shared ownership | Parallel with | Shared resources | Integration gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | none | approved block design | frozen contracts | declared paths | shared registration/docs | none | schema registry | contract gate |
| S02 | S01 | frozen contracts | backend component | declared backend paths | frontend/common docs | S03 | temporary workspace | focused backend gate |
| S03 | S01 | frozen contracts | frontend component | declared frontend paths | backend/common docs | S02 | isolated browser ports | focused frontend gate |
| S04 | S02, S03 | both outputs | integrated workflow | shared wiring/docs | none | none | all outputs | full block gate |

Each slice document repeats its own dependency, ownership, resource, and merge obligations so a standalone agent cannot miss
them.

## Parallel-Safe Criteria

Slices may run concurrently only when all are true:

- each consumes committed/frozen inputs rather than another slice's uncommitted output;
- neither slice's design depends on the other's result;
- write ownership is exact and non-overlapping, including tests, schemas, fixtures, docs, and generated artifacts;
- shared registration/configuration files are reserved for an integration owner;
- ports, browser sessions, temporary roots, caches, databases, run IDs, and artifact identities are isolated;
- measurements do not depend on sequential condition order, shared cache temperature, provider load, or cumulative baseline;
- each slice has focused gates that can pass independently;
- commits can be integrated in a declared order and the combined result has a separate integration gate;
- failure of one slice can prevent only its declared dependents rather than corrupt another lane.

Convenience, file count, or a desire to use more agents is not evidence of safe parallelism.

## Sequential-Only Criteria

Keep slices sequential when any is true:

- one freezes a contract, schema, fixture, baseline, or architecture consumed by the next;
- one decides behavior or scope based on the other's evidence;
- they modify overlapping runtime/public interfaces or common owners;
- they measure before/after behavior against one evolving candidate;
- they share non-isolated ports, workspaces, artifacts, caches, or external resources;
- provider calls require balanced/frozen order or concurrency would change latency/cache/rate-limit evidence;
- integration cannot distinguish which change caused a quality, reliability, or performance effect;
- a human design/live/promotion decision separates them.

Live provider schedules are sequential by default unless concurrency is itself the audited experiment and has an exact
approved budget/order/concurrency contract.

## Write Ownership and Worktrees

Concurrent write agents use separate Git worktrees or strictly disjoint file ownership. The block plan names:

- one owner per production module/package;
- one owner per schema/fixture/contract;
- one owner per test area;
- one owner per documentation/configuration/registration file;
- one integration owner for shared wiring and block status/outcomes.

Agents never stage, commit, reset, reformat, or overwrite another lane's work. Unrelated user/untracked changes remain
untouched. Read-only agents may share a workspace when they create no files/artifacts.

## Shared Resource Isolation

Parallel lanes declare unique values for applicable resources:

- MCP/Django/frontend/browser ports;
- temporary and evaluated/control workspaces;
- Playwright session/profile names;
- diagnostics/evaluation run, case, request, and observation IDs;
- output/report/ledger roots;
- caches whose temperature affects evidence;
- package-manager/build output directories;
- database or external-service access.

A resource that cannot be isolated makes the relevant slices sequential. Broad test suites that contend for the same ports or
resources run once at integration rather than redundantly in parallel.

## Slice Commit and Verification Cadence

Every slice, including a parallel slice, retains the repository cadence:

```text
approved slice plan
→ failing/characterizing proof where applicable
→ implementation
→ focused verification
→ implementation audit and corrections
→ required broader slice gate
→ coherent slice commit
```

Parallel execution never merges slices into one unreviewed commit. The integration owner reviews every candidate commit,
combines them in declared order, resolves only integration-owned conflicts, runs cross-lane tests, and creates the integration
checkpoint required by the block plan.

## Integration Gate

The block plan names an integration slice or explicit integration gate that waits for all prerequisite lanes. It owns:

- shared registration/wiring/configuration changes;
- cross-lane documentation and current-state updates;
- combined import/type/schema/fixture/reference checks;
- end-to-end behavior and security/compatibility proof;
- full backend/frontend/MCP/browser gates required by scope;
- Block 1 audit/anchor/guard reruns required by the owning block;
- cumulative baseline or parity update;
- block implementation audit and exit handoff.

No parallel lane independently declares the block complete.

## Overnight Orchestrator

An overnight block executor operates the approved DAG:

```text
load immutable block/slice plans and baseline
→ find pending slices whose dependencies passed
→ launch only parallel-safe ready slices
→ persist process/worktree/ownership/state
→ collect focused results and commits
→ stop dependents of failed/uncertain slices
→ integrate successful prerequisite commits
→ run integration/block gates
→ persist block handoff
→ stop at the next non-preapproved human gate
```

Durable slice states are:

- `pending`;
- `running`;
- `passed`;
- `failed`;
- `blocked_design`;
- `blocked_live_gate`;
- `interrupted_safe`.

Only `passed` satisfies a dependency. A lost client/process response never authorizes restarting the underlying work without
checking process/checkpoint/commit state.

## Sequential Block Pipelines

Several blocks may execute in one overnight session sequentially only when each downstream block plan/slice DAG is already
approved, predecessor exit gates are deterministic and pass, no material design choice remains, and every live budget was
explicitly authorized. Otherwise the executor may run a downstream block's approved read-only audit/preparation and then
stop for review.

Human/high-level review is mandatory before:

- approving a repository target architecture or behavior-changing redesign;
- implementing a newly selected readiness/workflow architecture;
- any live-provider package not already authorized exactly;
- accepting a complete live anchor;
- selecting/retaining material optimization waves outside preapproved rules;
- approving a representative live matrix;
- promotion, certification, deployment, push, or destructive action.

## Failure and Stop Rules

When a slice fails or becomes uncertain:

- preserve its worktree, process/checkpoint state, artifacts, and commit status;
- do not start dependent slices;
- do not rerun provider or external identities;
- distinguish introduced, pre-existing, environmental, and unknown failures;
- diagnose before fixing when the cause is unknown;
- stop for human review when correction changes design/scope/contracts, needs credentials/permissions, weakens a gate, or
  requires a new live/destructive authorization;
- allow independent lanes to finish only when their results remain valid and isolated from the failed lane.

## Block-Agent Planning Checklist

Before high-level review, every block agent answers:

1. What is the slice DAG and critical path?
2. Which dependencies are true contract/evidence dependencies?
3. Which slices can run in parallel, and why is each safe?
4. What exact files/resources does each lane own or forbid?
5. Which shared files are reserved for integration?
6. What worktrees, ports, workspaces, IDs, and caches isolate the lanes?
7. What focused gate and commit completes each slice?
8. What merge order and integrated gate prove the combined result?
9. Which failures cancel which dependents?
10. Which tasks are read-only lookahead rather than block execution?
11. Where must overnight execution stop for design, live, evidence, or promotion review?
12. Why is any proposed linear section not safely parallelizable?

A plan audit fails when it omits this topology, claims parallelism without exclusive ownership/resource isolation, or uses
sequential slices without justifying their dependencies.

## Assignment Template Addendum

```text
Execution topology / DAG:
Critical path:
Parallel lanes:
Sequential-only slices and reasons:
Slice inputs/outputs:
Exclusive write ownership per lane:
Forbidden/shared files:
Integration owner:
Worktree/branch strategy:
Ports/workspaces/sessions/run IDs/cache isolation:
Focused gate per slice:
Merge order:
Integration/block gate:
Failure cancellation map:
Overnight auto-advance boundary:
Mandatory human gates:
```

## Relationship to Other Owners

The roadmap group owns this execution policy. Each detailed block group owns its actual slice DAG. The standard slice
audit/commit workflow remains owned by `.devin/rules/graphpilot.md`. Current execution status remains only in the current-state
board. This policy does not approve any slice, file ownership, refactor, provider budget, optimization, or promotion by itself.
