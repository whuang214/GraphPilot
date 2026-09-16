# Delivery workflow

How work is organised here: packages, how much process each one earns, and what a
program is allowed to leave behind.

**Read this when a program starts or a package changes state.**
[`AGENTS.md`](../../AGENTS.md) owns the portable working rules and links here for
delivery details. Legacy Devin configuration is local-only and excluded from Git.

---

## Packages and programs

A **package** is one coherent, verifiable change with one owner. A **program** is an
ordered list of packages recorded in one `plan.md`.

```text
Plan (Tier 2+) → Implement → Verify → Outcome
```

Package states: `proposed`, `planned`, `implementing`, `verifying`, `complete`,
`blocked`, `reverted`. Only the parent agent changes a state, and it is recorded in
`plan.md`.

A slice number is permanent. A reverted slice keeps its number, marked `reverted`, and
the number is never reused.

Commit when a coherent, verified unit exists — not once per gate.

---

## Ceremony is proportional to cost

Process scales with what a mistake costs, not with how important the work feels.

| Tier | When | Required |
| --- | --- | --- |
| **1 · Default** | Revertible by `git revert` | Code, tests, commit. One row in `plan.md`. **No plan document, no audit document.** |
| **2 · Contract** | Changes a public tool/route, schema `$id`, persisted file format, or a documented contract | Tier 1 plus a written plan and an implementation audit before commit |
| **3 · Irreversible** | Spends model budget (a corpus run), or writes digest-bound evidence | Tier 2 plus per-run user authorization, a pre-dispatch check, and a terminal record |

Most work is Tier 1. **Choosing a higher tier "to be safe" is a defect**: it buries the
real Tier 3 gates in noise.

---

## Where a program lives, and its file cap

- An active program is **exactly one folder**, `docs/05-delivery/NN-<program>/`, and it
  is **flat**. No `README.md`, no `work/`, no `evidence/`, no `history/` while it is
  open.
- Folders are what produced the last program's **61 documents for 4 shipped commits** —
  each folder grew a `README.md`, each package grew a `work/` document, each gate grew
  an evidence file, and every one of them was locally justifiable.
- **Each program declares a file cap in its `plan.md` and stops at it.** Crossing the cap
  is a defect report, not a formality.
- A package produces **at most one** document, and only at Tier 2 or 3. It holds the
  whole lifecycle — plan, audits, verification, outcome.
- Procedural steps, handoffs and status changes never get their own document.
- **If a program's documents outnumber the source files it changed, stop and report.**
- At close, the program collapses to one summary in `docs/07-history/`.

Live status belongs only on the board, `docs/05-delivery/01-current-state.md`, kept
under ~500 words with roughly one line per cell. Narrative and history belong in the
program's `plan.md` and in git.

Record decisions in `docs/05-delivery/04-decisions.md` when a change affects scope,
behaviour or architecture — never in temporary notes.

---

## Measurement apparatus has an owner and an end

Evaluation harnesses, audit rigs, benchmark services and their schemas are
**scaffolding, not product**.

- Extend or replace the existing rig; never add a parallel one.
- Every rig names the program it serves and **dies with it** — schemas, services, tests
  and commands together, in the closing package.
- **A rig can die in halves.** One survived months after its backend was deleted: a
  closed subtree in no tsconfig project, run by no gate, still blanking environment
  variables for a provider the repository had removed.
- Retiring a rig requires a liveness proof: nothing imports it, nothing validates
  against it, and the product suite passes without it.
- A change that adds more apparatus than product stops for approval.

### Evidence: keep what you paid for

- **Paid evidence is sealed forever.** Never edit it, never rerun a terminal identity.
- **Free evidence is regenerable.** Keep the current baseline only.
- Create evidence only when it is machine-checkable proof someone will re-verify. Never
  write a narrative audit file.
- Never edit a self-digested artifact in place; its digest is its identity.
- **No new `authorization/` entries** — that folder is legacy and closed. It survives
  only under `docs/07-history/`.

---

## Reporting

After each package: (1) what and why; (2) files changed by area; (3) exact commands run
and their results; (4) decisions and deviations; (5) next step.

---

## Subagents

- The **parent agent owns all documentation edits** and all package state.
- A subagent gets a bounded scope and returns work or findings. It never creates a
  process document, plan or evidence folder, never changes package state, and never
  commits unless given an exact boundary.
- **A subagent asked to investigate returns a plausible essay unless running something
  is the only way to answer.** Three in one audit reported conclusions they had never
  tested, and one was simply wrong about a security property. Demand the file list, the
  exact commands and their output — then re-run anything load-bearing yourself.
