# Lane B · Workflow and Business Logic

**Status: active.** The integrated checkpoint is adopted and the backlog re-ranked
against it (gates G1–G2 closed in the [root plan](../plan.md)). Lane B works in its
own worktree `C:/Users/w105098/Desktop/Projects/GP-LB2` on branch
`lane-b-post-integration`; Lane A owns `master` and the two run in parallel.

**No provider or live work is authorized in this lane** (G3 is still open). The
current package is provider-free and does not need it.

## Scope

GraphPilot workflow and business logic:

- first-response contract validity and avoidable provider calls — highest priority;
- generation packet, cache, and sequence work;
- MCP, local, and browser work only when measured contribution justifies it.

Lane B does not touch host contracts or authoring guidance — those belong to
[Lane A](../lane-a/README.md).

## What is done

Three waves completed, plus a path-safety prerequisite:

- **B0 · Windows path safety — retained** (`4f02b0a`). Every live package now proves
  its derived Windows artifact paths fit the platform limit before manifest freeze.
- **S01–S04 · Semantic review — reverted.** The candidate did not remove the
  response-repair call; correction reverted, terminal evidence retained.
- **S05–S08 · Generation endpoint — retained** (`a17bc40`). Candidate `g2` passed
  with three calls and removed the generation repair call worth 26,052.5176 ms.
- **S09–S12 · Semantic review retry — reverted.** Candidate `s1` failed
  non-retryably with `semantic_repair_failed`. Correction `b5ef422` is reverted by
  `a6e7ad0`; semantic behavior sits at the `5ec80b7` baseline.

Both failed candidate identities are terminal evidence and are **never rerun**.
Retired slice documents are read-only in [`../history/lane-b/`](../history/lane-b/);
their evidence is in [`evidence/`](evidence/), and the exit handoff that binds the
frozen artifacts is at [`../evidence/lane-b-exit/`](../evidence/lane-b-exit/).

## Layout

| Path | Owns |
| --- | --- |
| [`plan.md`](plan.md) | Lane B package state and the backlog re-ranked against the integrated baseline. |
| [`work/`](work/README.md) | One `<nn>-<name>.md` per substantial package, holding its whole lifecycle. |
| `evidence/` | Lane B wave evidence: diagnosis, wave, and path-safety proofs. |

## Accounting

18 controlled + 1 external host = 19 aggregate completed provider calls; 0 failed,
0 uncertain; 981 remaining against the 1000 ceiling. Any future live run needs a new
explicit user authorization bound to one anchor and one attempt.
