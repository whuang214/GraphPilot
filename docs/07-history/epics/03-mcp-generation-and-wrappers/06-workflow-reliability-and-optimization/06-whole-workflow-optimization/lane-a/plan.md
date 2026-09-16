# Lane A Plan

Lane A package state. Scope and background: [`README.md`](README.md). Cross-lane
gates: [root plan](../plan.md). Live cross-project status:
[`00-current-state.md`](../../../../../../05-delivery/01-current-state.md).

## State

**Paused for the repository restructure.** A04 is complete and gates G1–G2 are
closed. Package A05, the authoring-contract lookup, is planned but **deferred**: it
touches the MCP server and context validator, which the restructure relocates, so
implementing it first would mean doing the work twice. Resume A05 once the
restructure closes. **Provider and live work is not authorized (G3).**

## Packages

| # | Package | State | Note |
| --- | --- | --- | --- |
| A01 | Host benchmark contract | complete | Retired doc in [`../history/lane-a/`](../history/lane-a/lane-a-01-host-benchmark-contract.md) |
| A02 | Devin host transition | complete | [retired doc](../history/lane-a/lane-a-02-devin-host-transition.md) |
| A03 | Evidence authoring unblock | complete | Best-branch reporting; [retired doc](../history/lane-a/lane-a-03-evidence-authoring-unblock.md) |
| A04 | Authoring discoverability | complete | Named allowed properties; stopped sibling-defect truncation. [retired doc](../history/lane-a/lane-a-04-authoring-discoverability.md) |
| A05 | Authoring contract lookup | planned · deferred | Closes `r1`'s remaining cause: no tool returns the evidence or request contract. Provider-free. Deferred until the restructure closes. [`work/01-authoring-contract-lookup.md`](work/01-authoring-contract-lookup.md) |

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

## Retired plan structure

A05–A09 existed in the original slice plan as snapshot-backend, host-interface,
integration, candidate-measurement, and wave-decision slices. Host observation `r1`
retired that sequencing: it retired the proposed `evidence[]` recomposition, because
A03's best-branch reporting had already removed the opacity that change existed to
fix, and it reprioritized authoring discoverability over payload reduction. Their
documents remain in [`../history/lane-a/`](../history/lane-a/) as history. The next
Lane A package is scoped from the re-ranked backlog, not from those documents.

## Exit criteria for resuming

1. ✅ Root gate G1 closed — checkpoint adopted 2026-07-30.
2. ✅ Backlog re-ranked against `run-workflow-audit-block6-integrated-01` (G2).
3. One candidate selected with a provider-free verification path, or an explicit
   live authorization if the candidate needs one (G3, still open).

Item 3 is satisfied for A05: it is provider-free, so it needs no live authorization
and its verification path is focused tests plus the full backend suite.

The integrated baseline's Lane A-owned finding `host_boundary_evidence_simulated` is
**not** that candidate: W01–W03 stay fixture-simulated, and replacing them needs
separately bound external host evidence rather than a GraphPilot change, which this
lane cannot produce while its host is the implementing agent. A05 is scoped from
host observation `r1` instead.

## Outcome

🔄 A05 is planned and deferred pending the repository restructure; no implementation
has started.
