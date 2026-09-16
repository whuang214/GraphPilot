# B1 · Local Cost Attribution

**State: implementing (diagnosis).** Provider-free; root gate G3 is not required.
Lane B package state: [`../plan.md`](../plan.md).

## Purpose

Separate **per-process initialisation** from **per-request cost** in the integrated
baseline, so the Lane B backlog is ranked against a denominator that reflects what a
user actually pays. Until that split exists, every ranking in this lane is measured
against a cold-start tax that production does not pay.

## Background: why this package changed shape

It opened as *Example Loading Cost* — remove the `example_loading` stage cost that is
54.0% of nested generation-stage time in
`run-workflow-audit-block6-integrated-01`. That framing did not survive its own
measurement and was corrected before any code changed.

The original root cause was real and is confirmed:
`TrainingFixtureService.load_example_set()` calls `derive()` per example, which runs
`_canonical_output()` (a full generation-pipeline prepare), validates that output,
and runs `_verify_pygraphviz()` — then uses only `runtime_example` and **discards
`canonical_output` entirely**
(<ref_snippet file="backend/services/generation/requests/training_fixture_service.py" lines="303-322" />).
That is genuinely unconsumed work on the request path.

What failed was the **expected benefit**, not the observation.

## Diagnosis

### Evidence 1 — the stage is cold-start, not per-call

Measured today against this worktree, provider-free:

| Condition | `load_example_set` |
| --- | ---: |
| Warm, same process | 76.3 ms mean over 6 sets |
| Cold, fresh process | 501.6 / 776.2 / 867.5 / 948.6 ms |
| Cold, with the discarded work bypassed | 54.3 / 51.4 / 59.3 ms |

The baseline's 920.2 ms mean is the **cold** figure. A warm call is ~12× cheaper.

### Evidence 2 — the cost is one-time native init

| Component | First call | Second call | Init |
| --- | ---: | ---: | ---: |
| `_verify_pygraphviz` | 527.8 ms | 1.0 ms | **526.8 ms** |
| `_canonical_output` | 701.4 ms | 5.6 ms | **695.8 ms** |
| `_validation.validate` | 3.4 ms | 3.4 ms | 0.1 ms |

### Evidence 3 — every observation pays it

Per-workspace `example_loading` values from the frozen run:

```text
scenario-e070c7f2d823604   1656.0, 356.9
scenario-eeec7e861ac4928   1666.1, 457.0
scenario-ff0d350bb37bdea    827.3, 405.0
scenario-245c60eca4b1207   1529.1, 397.8
```

The second observation in a pair is always cheaper but **never** the ~76 ms of a warm
in-process call, so observations do not share a warm process; the residual saving is
consistent with OS-level caching of native libraries across separate processes.

### Evidence 4 — the harness process model, verified in code

The audit spawns one OS process per **scenario**, not per observation
(`backend/services/workflow_audit/run_service.py:396-401`), and runs that
scenario's observations sequentially inside it (`:419`). That explains the pairs
exactly: the first observation pays full process init, the second runs warm.

Within a process, a **new `DiagramGenerationService` is constructed per generation**,
each building its own `TrainingFixtureService`
(`backend/services/generation/pipeline/diagram_generation_service.py:228`). There is no
process-wide cache on that path.

Production has the same shape: the MCP server process is long-lived with
module-level registries, but `diagram_generate_direct` and
`diagram_generate_from_context` construct a **new service per tool call**
(`backend/mcp_server/server.py:936` and `:995`, factory at `:124`).

### Finding: three cost tiers, only two of them real

| Tier | Cost | Paid in production |
| --- | ---: | --- |
| Process init — imports, pygraphviz native (526.8 ms), pipeline (695.8 ms) | ~1,300 ms | **Once** per server start |
| Per-request service construction | ~220 ms | **Every** request |
| Per-request `example_loading` | 119.4 ms | **Every** request |

The baseline's 920.2 ms `example_loading` conflates tier 1 with tier 3. Tier 1 is a
harness artifact: the audit spawns 12 scenario processes, so it pays init 12 times
where a real server pays it once. That inflation sits inside the `local` total of
51,034.4 ms and is not optimisable product cost.

Measured production-shaped — long-lived process, fresh service per request, 8
iterations per set — `example_loading` costs **119.4 ms** per request, and bypassing
the discarded canonical-output / validation / pygraphviz work reduces it to
**41.6 ms**, a saving of **77.8 ms (65.2%)**, ranging 43.5%–82.9% by set.

So the original B1 change **is** worth making, at roughly a twelfth of the benefit
first claimed: 77.8 ms per request rather than ~900 ms. It removes genuinely
unconsumed work from every production generation, adds no cache or invalidation
semantics, and keeps every per-request digest check.

The larger per-request cost is tier 2: **~220 ms of service construction on every
request**, which no stage in the baseline attributes because it happens before the
first stage opens. That is now the strongest per-request candidate in this lane and
is recorded for the corrected ranking. The unmerged `perf-test-speedup` branch
(`8733022`, "share parsed schemas and the ref registry process-wide") may already
address part of it and must be assessed before any new work duplicates it.

## Plan

1. Confirm from code whether the audit executes each observation in a fresh OS
   process, or identify what else makes every observation pay init.
2. Build a provider-free, in-process measurement that performs repeated generations
   in one long-lived process, emitting the **same** stage names as the baseline.
3. Produce a per-stage split of per-process init versus steady-state per-request
   cost, over the same scenario set.
4. Re-rank the Lane B backlog on the per-request column only, and record the init
   column as harness characterisation rather than as optimisable product cost.
5. Decide the next package from that corrected ranking. Deciding *not* to optimise a
   stage is a valid outcome.

## Not in scope

Changing the audit harness or the scenario set; any provider or live call (G3 remains
open); reintroducing the reverted S10 semantic behaviour; Lane A's host boundary.

## Verification

Every measurement is provider-free with zero Azure calls. Frozen run identities are
read only and never re-executed; any new audit run would take a new short identity.
Temporary instrumentation is deleted before commit.

## Plan audit

🔄 Pending.

## Implementation

🔄 Pending.

## Implementation audit

🔄 Pending.

## Outcome

🔄 In progress. The original *Example Loading Cost* framing was corrected to cost
attribution before any production code changed; no behaviour has been modified.
