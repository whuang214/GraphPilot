# Lane B Plan

Lane B package state. Scope and background: [`README.md`](README.md). Cross-lane
gates: [root plan](../plan.md). Live cross-project status:
[`00-current-state.md`](../../../../../../05-delivery/01-current-state.md).

## State

**Active in the `lane-b-post-integration` worktree.** The integrated checkpoint is
adopted (G1) and the backlog re-ranked against it (G2). Package **B1** is
`implementing` its diagnosis. **Provider and live work is still not authorized (G3);
B1 is provider-free and does not need it.**

## Packages

| # | Package | State | Note |
| --- | --- | --- | --- |
| B0 | Windows path safety | complete · retained | `4f02b0a`; [retired doc](../history/lane-b/b0-windows-path-safety.md) |
| S01–S04 | Semantic review wave | reverted | No behavior retained; terminal evidence kept |
| S05–S08 | Generation endpoint wave | complete · retained | `a17bc40`; candidate `g2` pass |
| S09–S12 | Semantic review retry wave | reverted | `b5ef422` reverted by `a6e7ad0`; candidate `s1` failed, non-retryable |
| B1 | Local cost attribution | implementing | Rank 1 rescoped after measurement; [`work/01-local-cost-attribution.md`](work/01-local-cost-attribution.md) |

Package states are `proposed`, `planned`, `implementing`, `verifying`, `complete`,
`blocked`, or `reverted`.

A substantial package gets exactly one `work/<nn>-<name>.md` holding its whole
lifecycle in this order, with no gate collapsed into another:

```text
Plan → Plan audit → resolve → Implement
→ Implementation audit → resolve → Verify → Outcome
```

Minor work stays as a row in this table instead. Full conventions:
[`.devin/rules/graphpilot.md`](../../../../../../../.devin/rules/graphpilot.md).

## Re-ranked backlog (G2)

Ranked against `run-workflow-audit-block6-integrated-01` only, replacing the
pre-integration ranking. Evidence is that run's frozen `report.md` accounting plus
its 496 per-boundary metric records; every figure is provider-free and is a measured
contribution, **not** a promised saving.

Domain accounting across 19 observations: local **51,034.4 ms**, host 1,908.6 ms
(simulated, Lane A), mcp 1,609.9 ms, browser 730.0 ms, residual 230.1 ms — local is
91.9% of the accounted wall. The 56 fake provider calls contribute at most
**417.2 ms** of that, so the local dominance is real local compute rather than
simulation overhead. The report's own rank-1 finding
`complete_wall_local_contributor` (owner `generation`) prescribes profiling its
largest non-nested sub-boundary first.

Each provider call emits two metric records — one unbound and one
boundary-attributed — so the 112 `provider_call` records reconcile to the report's
56 calls, and 417.2 ms is the boundary-attributed total rather than the 487.9 ms
naive sum over both record sets.

That profile resolves to the `generate_context` boundary (W07, 29,789.8 ms of the
37,041.3 ms of top-level local operations) and, within it, these nested stages:

| Rank | Domain | Measured | Per obs | Share of stage time | Disposition |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | `example_loading` | 14,722.4 ms | 920.2 ms | 54.0% | **B1 — open now**, provider-free |
| 2 | `context_preflight` | 4,604.7 ms | 242.4 ms | 16.9% | candidate after B1 |
| 3 | `canonical_validation` | 3,152.3 ms | 197.0 ms | 11.6% | candidate after B1 |
| 4 | Semantic candidate-repair convergence | not measurable provider-free | — | — | separate owner; diagnose only, needs G3 to prove |
| 5 | `packet_construction` (packet/cache) | 1,472.5 ms | 92.0 ms | 5.4% | **demoted** — not material |
| 6 | `mcp` domain | 1,609.9 ms | — | 2.9% of wall | **demoted** — not material |
| 7 | `browser` domain | 730.0 ms | — | 1.3% of wall | **demoted** — not material |
| 8 | `readiness` | 247.7 ms | 14.6 ms | 0.9% | **demoted** — not material |

Rank 1 fires exactly once per generated observation (16 events for 16 `generated`
outcomes; the 2 non-generating workspaces emit none), so its total is not inflated by
repeated records.

> **This ranking is under correction by B1.** Direct measurement showed the rank-1
> spread of 356.9–1,666.1 ms is **per-process initialisation**, not per-call work: the
> same call costs 76.3 ms warm, and the native init it front-loads
> (pygraphviz 526.8 ms, generation pipeline 695.8 ms) is initialisation the real
> request path needs anyway. A long-lived production MCP server pays it once, so an
> unknown but large share of the `local` total is harness cold-start tax rather than
> optimisable product cost. Ranks 1–3 and 5–8 are all measured in that inflated
> denominator and none may be opened until B1 republishes a per-request column. See
> [`work/01-local-cost-attribution.md`](work/01-local-cost-attribution.md).

The pre-integration ranking is superseded. Packet/cache, readiness, MCP, and browser
were ranked highly before integration and are each measurably minor now; none may be
opened on the old rationale. Local owner attribution is answered: the local cost is
owned by `generation`, concentrated in one stage.

Rank 4 is a reliability defect, not a latency one — `semantic_review` costs 0.0 ms
provider-free because the fake provider always returns a contract-valid response, so
the `semantic_repair_failed` non-convergence seen in the terminal `s1` candidate is
invisible to this baseline. It is a distinct owner from B1, may be diagnosed
provider-free only, must not reintroduce reverted S10 (`b5ef422`), and keeps the
one-round semantic repair budget unchanged absent a separately approved design.

## Live-run rules

Unchanged and binding:

- A new explicit user authorization is required per live run, bound to one anchor
  and one attempt (root gate G3).
- Terminal identities `run-live-workflow-anchor-g` and `run-live-workflow-anchor-s`
  are immutable and are never rerun.
- A failed, blocked, or interrupted candidate is terminal evidence, not permission
  to retry.
- Every live package proves its derived Windows artifact paths fit the platform
  limit before manifest freeze, and uses short bounded identities.
- No new folders are created under [`../authorization/`](../authorization/README.md); it is legacy and closed.

## Outcome

🔄 Lane B is active on `master`; B1 is in flight.
