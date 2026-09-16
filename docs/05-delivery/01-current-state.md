# Current State

The cross-project status board. **This is the only doc that carries live status** — every
other doc links here rather than restating it. Completed work is frozen in
[`docs/07-history/`](../07-history/README.md).

## Active

- **Production readiness (`A6`) is closed** — a whole-repository audit through twenty
  lenses, reported in
  [`09-production-readiness/report.md`](09-production-readiness/report.md). **Generation
  quality is closed** too; `A5`'s findings are frozen in
  [`07-generation-quality/a5-report.md`](07-generation-quality/a5-report.md).
- **Contract efficiency**, see
  [`08-contract-efficiency/plan.md`](08-contract-efficiency/plan.md). The authoring
  contract is now scoped per diagram type: -10% for activity, -7.5% for use case, flat for
  BDD. `C3` (the `content`/`structuredContent` duplication, ~40%) is **blocked on Gate 0** —
  what a real IDE MCP client puts in the model's context. No corpus run has ever tested
  that: `call.py` dumps both channels.
- **Draft-first generation is complete and frozen.** The host authors a diagram draft; the
  backend materializes it deterministically. **Zero provider calls.** Summary:
  [`completed-draft-first-generation.md`](../07-history/completed-draft-first-generation.md).
- **The path works end to end for all three diagram types.**
  `diagram_workflow` → `diagram_get_authoring_contract` → `diagram_create` takes a
  `graphpilot.draft.v1` document to a validated `.gp.json`, its `.svg`, and an editor link.
  MCP surface: 11 tools. Design:
  [`03-design/01-generation/`](../03-design/01-generation/README.md).
- **Presentation round 1 is done.** No two edges are drawn on top of one another in any of
  the 36 committed examples (was 88 endpoints across 24 of them). Two findings stay open,
  `h10` and `h11`, described under **Next up**.
- **No provider configuration remains.** `backend/.env` needs no Azure settings and the
  `openai` dependency is gone.
- **Repository:** [whuang214/GraphPilot](https://github.com/whuang214/GraphPilot), default branch `main`.

## Epics

| Epic | Status | Next |
| --- | --- | --- |
| 1 · Local Diagram Foundation | ✅ complete and verified | none |
| 2 · React Editor + Export | ✅ complete and verified | none |
| 3 · MCP Generation + Wrappers | ✅ rebuilt draft-first; create path live | quality pass — [plan](07-generation-quality/plan.md) |
| 4 · MCP Edit Workflow | ✅ built — `diagram_read` → edit the file → `diagram_update`, with the merge, R1–R5 geometry and history — [`design/05-edit/`](../03-design/05-edit/README.md) | a corpus run with an edit leg |
| 5 · RAG Example Library | 💤 post-MVP | none |

## Tests (last verified)

- Backend **~780** (1 skipped) in ~16 s — `cd backend; uv run python manage.py test --parallel 24`
- Frontend **511** unit + **43** e2e + lint clean + build succeeds — `cd frontend; npm run verify`

The backend count fell from 1046 to 385 when the provider pipeline was removed, and is
climbing back. The whole suite is offline: there is no provider seam left to fake.

## Blockers

None.

Two things are known-incomplete rather than blocking: held-out validation on a second
repository never ran, and the outside-in run was not independent — the same agent wrote
the authoring contract and then the draft against it. Both are `F` package work.

## Next up

**A0, H, A1 and A5 are complete.** The audits found 11 and then 8 defects, none caught by
the suite of the day. End labels sit clear of their nodes, and notes sit beside what they
annotate.

**E1 — the grounded corpus, complete.** Three runnable applications in
`GraphPilot-Test-Repos/`, each audited against R1–R8 before use. **All three are built and
audited.** Ground truth lives outside each repo so the host cannot read it.

**E2 is complete.** Three fresh subagents acting as cold hosts produced **9 of 9 accepted
diagrams in 18 calls**, having never seen the repos or the ground truth. The semantics were
consistently good — they avoided the modelling traps and found two real defects nobody
planted. The contract was the weak point: 17 documented gaps, most reported independently
by two or three of them.

**`D1` is decided — option B.** All three hosts named the same worst problem: `scope`,
`uncertainties`, `decisions` and assumption bodies are validated strictly and then
discarded. The saved diagram does **not** carry the host's reasoning; the tools report what
was dropped and ask instead. Rationale in the plan.

**H2 — legibility, mostly closed.** A measure of the rendered output — text clipped by its
own node, buried under a foreign one, or overlapping other text — went from **87 of 1201
drawn strings (7.2%) to 9 of 1210 (0.7%)**, and the 36 curated examples are now clean.
Blocks and notes size to the text they hold, and labels move aside rather than landing on
whatever is beneath them. A wide diagram now scrolls in the review gallery instead of
shrinking until its notation stops reading.

Two findings stay open. **`h10`** — an activity fork routes its outer branches *through*
the middle one, so the picture claims the middle branch feeds the others. Three fixes were
tried and all three measured no better or worse; the real fix is obstacle-aware anchor
selection, which changes the fan-out contract and its frontend mirror. **`h11`** — actors
placed away from the use cases they reach.

Deferred to [`02-backlog.md`](02-backlog.md): a replacement performance harness.

## Where detail lives

- Active program packages → [`07-generation-quality/plan.md`](07-generation-quality/plan.md)
- Completed work → [`../07-history/`](../07-history/README.md), frozen
- Design + decisions → `../03-design/` and [`04-decisions.md`](04-decisions.md)

## Maintaining this file

- Update the **Active** line + the changed **Epics** row when work starts/finishes; keep each cell to one line.
- Keep narrative ("what shipped, how, test counts over time") in each program's `## Outcome`, not here.
- Keep **Blockers** short and actionable.
