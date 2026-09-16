# Lane A · Host and Integration Preparation

**Status: active on `master`.** A04 is complete, and gates G1–G2 are now closed, so
Lane A may open its next package from the re-ranked backlog. Lane A owns the
`master` worktree; Lane B runs in parallel in its own worktree.

**No provider or live work is authorized in this lane.** Any provider, LLM, or live
call requires a new explicit user authorization (root gate G3), regardless of how
small the candidate looks.

The [root plan](../plan.md) and the group [`README.md`](../README.md) are
**Integration Captain-owned**: read them, never edit them. Lane A edits only this
folder.

## Scope

GraphPilot-owned host and integration surface only:

- host benchmark contracts and backend-derived evidence values;
- validation feedback quality and authoring discoverability;
- examples, templates, and workflow instructions;
- MCP and session guidance; reuse and read minimization.

The host agent's model, index, and cache are **external**. Lane A never claims them
as GraphPilot improvements, and external host wall time is never merged into the
controlled GraphPilot denominator.

Lane A does not touch generation, semantic review, or provider runtime behavior —
those belong to [Lane B](../lane-b/README.md).

## What is done

A01–A04 are complete. A04 delivered authoring discoverability: named allowed
properties on rejection and stopped truncation from hiding sibling defects. The
measured cause came from host observation `r1`, not from the pre-measurement plan.

Retired slice documents are read-only in
[`../history/lane-a/`](../history/lane-a/); the Lane A evidence they cite is in
[`evidence/`](evidence/).

## Layout

| Path | Owns |
| --- | --- |
| [`plan.md`](plan.md) | Lane A package state and next steps. |
| `work/` | One `<nn>-<name>.md` per substantial package, holding its whole lifecycle. Empty while Lane A is paused. |
| `evidence/` | Lane A evidence, currently the `lane-a-reference-host` cold/warm host observations. |

## Blocking condition

The remaining Lane A candidates were scoped against a pre-integration baseline. Any
measured host claim made now would use stale attribution. Wait for the adopted
checkpoint and the re-ranked backlog before planning the next package.

Measured host claims additionally require strict external cold **and** warm
observations; the missing warm profile blocks measured host claims but not
independently evidenced work.
