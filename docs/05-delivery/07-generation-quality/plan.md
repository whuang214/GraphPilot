# Generation Quality

The active program. Draft-first generation is
[complete and correct](../../07-history/completed-draft-first-generation.md) — a host
authors a draft, the backend materializes it with no provider call. What it is not yet is
**trustworthy to look at**, or **measurable**.

This program fixes both, then tunes the pipeline on evidence instead of intuition.

## The three things being improved

| | What it is | Owned by |
| --- | --- | --- |
| **f — instructions** | What we tell the host so it authors a good draft | `diagram_workflow`, the authoring contract, `authoring.md` |
| **g — transform** | Draft → canonical diagram | the materializer |
| **h — presentation** | Canonical diagram → something legible | layout + renderer |

`g` and `h` are deterministic and machine-checkable. **`f` is not** — judging whether a
host picked the right relationship needs a gold answer or a human, and gold answers are
the answer-key machinery retired in P0. So `f` is judged by review, which is why the
gallery exists.

## Five blocks

Each block answers one question and finishes before the next begins. Package IDs are
permanent — they are cited in the commit history — so they are grouped rather than
renumbered, which is why the numbering inside a block is not always in order.

| Block | Question | Packages | State |
| --- | --- | --- | --- |
| **1 · Trustworthy to look at** | Does the picture mean what it says? | `A0` `H` `A1` `H2` `A1b` | **complete** |
| **2 · Grounded in something real** | Can a cold host describe a real system? | `E1` `E2` `D1` | **complete** |
| **3 · Measurable and reviewable** | Can we tell whether it is getting better? | `A2` `E3` `E4` | **complete** — `E4` was reopened as `e17` and closed |
| **4 · Fix what the evidence found** | Close the findings the runs produced | `F` `A4` `G` `A3` | **complete** |
| **5 · Finish, audit, close** | Is the whole thing actually sound? | `P8` `D` `A5` | **complete** — [the `A5` report](a5-report.md) |

**Why block 1 comes first.** Presentation is the only category with a hard number before
the gallery exists, and every judgement about a *host* made through a bad picture is
contaminated — you cannot tell whether the author chose badly or the renderer drew badly.
It ran in two rounds because reviewing the corpus in block 2 exposed a second class of
defect: round one fixed edges *colliding*, round two fixed diagrams being unreadable at the
size they are actually looked at.

**Why block 3 sits between the evidence and the fixes.** Block 2 produced a list of
problems and no way to measure whether fixing them helped. `F`'s exit criterion is a
number, and until `E3` nothing produced one — a refused draft left no trace at all.

**An audit travels with the package it audits**, which is why `A4` (the contract, after
`F`) runs before `A3` (notation, after `G`). The numbers record when each was *added* to
the plan, not when it runs.

**Block 5 is last on purpose.** An assurance badge on a diagram that reads as the wrong
graph is worse than no badge: it lends authority to something incorrect.

## Packages

States: `planned`, `implementing`, `verifying`, `complete`, `blocked`, `reverted`.

### Block 1 · Trustworthy to look at — complete

| # | Package | Tier | Outcome |
| --- | --- | --- | --- |
| A0 | Full code audit of everything P0–P7 shipped | 1 | **11 defects**, none caught by 495 tests. Seven packages had landed fast and two design faults surfaced afterwards; finding a third then beat finding it under three phases of new work |
| H | Presentation 1: routing, container layout, endpoint collisions, labels | 1 | **88 → 0** coincident endpoints — three lines had been drawn as one |
| A1 | Audit the H changes | 1 | 6 checks, no findings |
| H2 | Presentation 2: legibility at the size a diagram is read | 1 | unreadable text **7.2% → 0%**, edges through an unrelated node **26 → 1**. `h11` and `h19`-class label collisions deferred |
| A1b | Audit the H2 changes | 1 | 1 finding: the container rule was enforced on the SVG side only |

### Block 2 · Grounded in something real — complete

| # | Package | Tier | Outcome |
| --- | --- | --- | --- |
| E1 | Build the corpus: three real applications | 1 | 3 repos, ~5,000 lines, ground truth held outside them |
| E2 | Generate and review every corpus diagram | 1 | **9 of 9 accepted** by cold hosts in 18 calls. 21 findings, and two real bugs in the corpus code itself |
| D1 | Does the saved diagram carry the host's reasoning? | 2 | **decided — B**: it does not. Report and ask instead |

### Block 3 · Measurable and reviewable — complete

| # | Package | Tier | Outcome |
| --- | --- | --- | --- |
| A2 | Is the rig earning its keep? **A gate on `E3`** | 1 | 3 findings, and its own test was the wrong one: counting files said "two files, fine" while the numbers lived in 55 uncommitted scripts |
| E3 | Make generation measurable | 2 | draft log, `diagram_check_draft`, a draft for all 36 answers, the run sheet. `e7` alone found **four unauthorable notation features** and 316 unauthorable ids |
| E4 | Make generation reviewable | 2 | **reopened as `e17`** — one card and one home, but the page re-ran layout rather than the pipeline, so it could not say whether a *generation* was good. Also found that the editor silently reorders a diagram's nodes on save |

### Block 4 · Fix what the evidence found — complete

| # | Package | Tier | State |
| --- | --- | --- | --- |
| F | Tune instructions on evidence | 1 | **complete** — 20 host-reported gaps closed; contract prose 60 lines to 276. Nearly every refusal in `E2` traced to an instruction gap rather than a transform defect, which is why this preceded `G` |
| A4 | Audit the contract for drift | 1 | **complete** — no drift, but **14 of 19 refusal codes were unlearnable** until you tripped them |
| G | Lock in the transform | 1 | **complete** - g3 trap tool retired, g5/g6/g7 fixed, and **g11 found**: a host authored parameters were accepted then silently discarded |
| A3 | Audit notation coverage | 1 | **complete** — all 26 authorable types covered; **9 primitives both renderers draw are unreachable**, one of them swimlanes |

### Block 5 · Finish, audit, close

| # | Package | Tier | State |
| --- | --- | --- | --- |
| P8 | Frontend assurance display, final gate | 2 | **complete** — an `assumed` element is marked on the canvas and gives the assumption's own statement on hover. Only `assumed`: badging every `grounded` element teaches a reader to ignore badges |
| **D** | **Audit every active document against the source, then rewrite.** | 1 | **complete** — **65 false claims in 11 documents**. `d3` guards both directions: a document naming what is absent, and the tool index omitting what is present |
| **A5** | **Full-repository audit: every line, every command. Closes the program** | 2 | planned — 7 slices, looped until a pass finds nothing |

**`D` is its own package, not a slice of the audit.** It began as one line in `A5` and
measuring it turned it into 328 lines across 20 files, including whole requirements written
for tools that were deleted. Work of that size hiding inside an audit slice is how it stays
undone — and an audit that also rewrites the documentation it is auditing cannot then check
it, which is the point of `A5` running last.

## Running this unattended

From `E4` onward this plan is executed in one continuous pass, overnight, with nobody
watching. So:

**Do not stop.** Work every package through to its exit criterion. Where two reasonable
options exist, take the better one, record the choice and the reason in this document, and
continue — an unattended run that pauses for a preference has simply stopped. Commit at each
coherent slice under the standing permission, so an interrupted night leaves readable
history rather than one unreviewable change.

**Three things still stop it**, and only these: a destructive operation not already
approved, a credentials or configuration problem, and a finding that would change the
product's contract in a direction no reading of this plan supports.

**It ends with a captain's report** — what was found, what was wrong that nobody knew was
wrong, what was deleted and why that was safe, what is still weak, and the honest state of
the repository. Not a list of files touched.

## Rules

**No provider calls.** Nothing in this program needs one. A package that wants one is a
design defect, not a budget request.

**File cap: 2.** This file plus at most one more. The workflow-optimization program
produced 61 documents for 4 shipped commits. **Audits produce rows in this file, never
audit documents.**

**Measure the artifact, not a model of it.** The first attempt at the `h` baseline modelled
the routing and reported zero collisions where there were 68. Assertions go against
rendered output.

**Judge at the size it will be looked at.** `h9` — very wide aspect ratios — was dismissed
as "not a defect, a top-down flow is tall because the notation is". That reasoning was
about the *number*. Seen in a gallery card, the same diagrams scale composition diamonds
down to about three pixels, so the notation is present in the SVG and absent from the
picture. A rendering judgement made from measurements alone is not a judgement.

**Apparatus needs a named owner and an end.** `E1` builds three full applications —
roughly 5,000 lines that are not product. That is a deliberate, user-directed decision:
synthetic code written to be diagrammable teaches nothing, and the existing
`todo-api-fixture` proved it by shipping an `architecture.md` that handed over the answer.
The corpus lives outside this repository in `GraphPilot-Test-Repos/`, so it neither counts
against this program's file cap nor ships with the product. `A2` tests whether it earned
its keep.

---

## A0 — Full code audit of P0–P7

An actual read of the code for bugs, not a process checklist. 495 tests did not catch
either defect already found.

**Surface — roughly 1,200 lines of new production Python plus contract changes:**

| | |
| --- | --- |
| New | `draft_validation_service` (405) · `materializer` (195) · `authoring_contract_service` (161) · `evidence_service` (147) · `diagram_creation_service` (147) · `draft_safety` (77) · `draft_contract` (63) |
| Changed | `canonical_assembly.py` · `diagram.json` · `diagram.ts` · `server.py` · `schema_registry.py` · `schema_identities.py` |
| Assets | `diagram-draft.json` · 3 × `authoring.md` |

**What to hunt for**, each derived from a mistake actually made:

| | Check | Origin |
| --- | --- | --- |
| A0.1 | Logic bugs: off-by-one line ranges, wrong lookups, silent `None` paths | — |
| A0.2 | Rules that trace to nothing live | `composition_part_end_missing` survived its own deletion |
| A0.3 | Assertions made against a model rather than the artifact | the zero-collision baseline |
| A0.4 | Tools returning empty for some inputs but not others | `example: None` for two of three types |
| A0.5 | Doc and docstring claims that contradict behaviour | `authoring.md` said wholes sit above parts |
| A0.6 | Parity pairs that moved apart | canvas ↔ SVG, `diagram.json` ↔ `diagram.ts` |
| A0.7 | Error paths never exercised | unreadable file mid-loop, cyclic parent, zero-element draft |
| A0.8 | Anything marked complete that is not | P7.3 held-out validation never ran |

**Findings — 11, all fixed in `fa8cc1b`.** None was a crash or a type error. Every one was
a rule that quietly accepted something it should have refused, and every one passed the
495-test suite. Nine came from probing edge cases rather than reading; two came from
calling the tools over the real stdio transport instead of in-process.

| | Finding | Class |
| --- | --- | --- |
| 1 | A block could be its own part, a class its own parent — `composition`, `generalization`, `include`, `extend`, `commentLink` self-loops all accepted. `association`/`dependency` still may, since an employee who manages an employee is legitimate | A0.1 |
| 2 | A self-parent reported `cyclic_parent` twice: the explicit check and the cycle walker both fired on the same path | A0.1 |
| 3 | Uncited evidence was persisted into `metadata.evidence`, which means *the regions the diagram was built from* — refused now, with uncited assumptions | A0.1 |
| 4 | An empty file could back a `grounded` claim: `"".split("\n")` is `[""]`, so line 1 resolved and digested nothing | A0.1 |
| 5 | Unsupported-type errors advertised `custom`, which cannot be authored as a draft, sending hosts where `diagram_create` refuses | A0.4 |
| 6 | `unsupported_diagram_type` was marked retryable; the same identifier fails identically | A0.7 |
| 7 | The retryability registry listed 25 codes from the deleted pipeline (`llm_*`, `semantic_*`, `readiness_*`) | A0.2 |
| 8 | …and none of the new draft codes. They worked only because every call site happened to pass `retryable` explicitly; the path that omits it would have raised | A0.7 |
| 9 | `mcp_server/smoke_test.py` survived P0 — 524 lines, 30 references to tools that no longer exist. Removed from the docs but not from disk | A0.8 |
| 10 | The lifecycle error table documented 7 of 19 codes | A0.5 |
| 11 | Pre-existing codes were nearly flipped wholesale while fixing 6–8. Caught in review: that is a public contract change, not an audit fix, and was reverted to original values | A0.8 |

Tests 495 → 507. Regressions are grouped in one file so the class stays visible: these
were found by probing, not by reading.

---

## H — Make the picture trustworthy

**The stated baseline was wrong, and the correction matters more than the number.** It
regexed closed paths out of the SVG and counted shared start points, which conflated node
shapes with edge markers: an arrowhead landing on a decision node's top vertex shares a
coordinate with the diamond itself, which is correct drawing. The honest question is
whether two *edges* terminate at the same point, asked through the real renderer:

```text
        before   after
  88 / 598  →  0 / 598   edge endpoints drawn on top of another
    24 / 36  →  0 / 36   examples affected
```

The true baseline was worse than the flawed one reported (88 vs 68, 24 examples vs 21).
This is the second time in this program that a metric flattered itself; see *Rules*.

| | Work | Outcome |
| --- | --- | --- |
| h1 | Stamp `straight` routing at creation | Done — `use_case` **and BDD**, see below |
| h2 | Container children inherit the diagram's direction | Done — `"TB"` was hardcoded while `use_case` is `"LR"`, so unconnected use cases spread four abreast instead of stacking |
| h3 | Distribute edge endpoints along the boundary | Done — `_fan_out_anchors`, grouped by (node, side), which took the residual to zero |
| h4 | Rendered-geometry regression tests | Done — including a corpus-wide endpoint check and a shared canvas/SVG fan-out fixture |
| h5 | Edge label drawn inside a node | **No work needed** — the routing change moved the `«extend»` label out of the oval |
| h6 | End label collides with its node | Done — worse than described: `driver 1` printed *inside* the Driver block over its own label. Both renderers now place end labels along the outward direction from one shared formula |
| h7 | Note lands far from its subject with a wire across the page | Done — placed adjacent to its subject. First attempt silently did nothing: a child's position is parent-relative |
| h8 | `forkNode` label crammed under a thin bar | **No work needed** — legible once fan-out separated the flows either side of it |
| h9 | Aspect ratios run very wide | **Judged wrong — reopened as `h13`.** Dismissed from the number alone; at viewing scale it is the root of the invisible-notation defect |

**BDD routing reverses an earlier decision, on evidence.** The call was to keep BDD
orthogonal "for now". Rendered side by side, orthogonal drew Heart Sensor — Battery —
Display as a *chain* when all three compose into Smart Watch: orthogonal routing has no
obstacle avoidance, so its edges run through the nodes between and invent relationships
that are not there. Activity keeps orthogonal — its branches diverge rather than converge,
and right angles are the conventional notation. One line in `constants.py` reverts it.

**A hand-arranged reference** for `09-hospital-portal` established that **actor placement
was already correct**. Without it, a bespoke actor strategy would have been built for a
problem that does not exist.

**Exit — met:** endpoint collisions at 0; galleries regenerated; use-case output matches
the reference shape. The 36 committed examples were re-laid-out, since their positions
were always machine-produced and had gone stale; verified across all 36 that only geometry
changed.

**A1 — complete, no findings.** Layout is idempotent (0 of 36 move on a second pass);
rendering is deterministic; an edge with one authored anchor is skipped entirely and keeps
it; `route.mode` is stamped only on the two types that need it; no anchor falls outside
`(0,1)`; all 36 still validate.

---

## D1 — Does the saved diagram carry the host's reasoning?

**Blocked. This is a contract decision, not an implementation choice.**

All three cold hosts independently named the same thing as the worst problem in the surface,
and each called it out unprompted as their single most important finding.

The workflow's strongest instruction is *"Put what the source does not establish in
`uncertainties` rather than resolving it silently."* Hosts obeyed it: **21 uncertainties, 19
decisions**, and a full `scope` and `request.goal` across nine drafts. `diagram_create`
validates all of it strictly — one host was refused three times over a single assumption
field, and once for an assumption that nothing referenced.

**None of it reaches the saved diagram.** The persisted `metadata` keys are `assurance`,
`authoring`, `authority`, `createdAt`, `evidence`, `generatedBy`, `intent`, `notation`,
`originalType`, `source`, `updatedAt`. `intent` is the diagram's *name*, not the goal.

One host put the cost concretely: it found that `payments/legacy_transfer.py` can create a
`Payment` with no ledger entries, breaking the invariant the whole of `kitepay` rests on.
*"That is the single most valuable sentence I wrote about this codebase, the contract told
me exactly where to put it, and it exists nowhere in the artifact a reader opens."*

Evidence **is** persisted, with digests, and all three praised it. The gap is specifically
the reasoning: scope, uncertainties, decisions, and assumption bodies.

| Option | For | Against |
| --- | --- | --- |
| **A — persist into `metadata`** | The artifact becomes self-describing; a reader can recover what was assumed and why; `g5`'s dangling reference resolves; the editor can surface it | Canonical schema change reaching `diagram.ts` and its parity test; larger files; the reasoning ages while the diagram is edited |
| **B — say plainly that it is author-time discipline** | No schema change; keeps the artifact lean; the discipline still works, because writing an uncertainty is what stops a host silently resolving it | Throws away the most valuable prose the host produced; leaves `g5` to fix by *removing* the reference; the workflow's wording currently implies persistence |
| **C — persist only what is referenced** | Assumption bodies land next to the elements citing them, closing `g5`; scope and uncertainties stay out | Half a mechanism; uncertainties are the part hosts most wanted a reader to see |

**Recommendation: A, narrowed.** Persist `scope`, `uncertainties`, `decisions`, and
assumption bodies under one `metadata.provenance` object, and add the missing
`metadata.request` from `g4` at the same time, since both are the same schema change and
`g4` is already a written commitment. Option B is defensible and cheaper, but it means
deleting instructions the hosts followed well — the honesty apparatus is the best-performing
part of the contract, and B is the option that makes it pointless.

Not started pending a decision. Everything after it is unaffected.

---

## H2 — Legibility at viewing scale

Round 1 asked *do edges land on top of each other?* and drove it to zero. This asks a
different question — **is the diagram readable at the size someone actually looks at it?**
— and it has no number yet. Finding one is the first task.

Raised from a gallery review, and **not blocking**: the notation is present and correct, so
a reviewer can still judge a diagram, just with more effort. Fixed after `E2` so the corpus
review can add to the list first.

| | Finding | Evidence |
| --- | --- | --- |
| h10 | Activity forks: parallel branches leaving one bar run down the same corridor and overlap | `05-cicd-pipeline`, `09-trade-settlement`, `11-order-processing`, `12-expense-approval` — all four have forks |
| h11 | Use-case actors sit on one side, so their edges cross each other to reach use cases spread down the boundary | `08-iot-platform`. Two options: reorder actors to minimise crossings, or split them either side of the boundary by which use cases they reach |
| h12 | Composition diamonds are invisible in the gallery | Verified present — spacecraft draws 6 diamonds for 6 composition edges — but at **12–16px on a 1540px canvas**, which is ~3px in a review card |
| h13 | Canvas is far larger than the content needs, forcing heavy downscaling | Activity examples measure 385×1430, 578×1592. This is `h9`, reopened |

**h12 and h13 are the same defect.** A marker is not too small in absolute terms; the
canvas is too large for its content, so everything shrinks past the point where notation
survives. Fixing density is likely to fix visibility without touching marker sizes —
which is worth testing before scaling markers up, since larger markers on a sane canvas
would then be too big.

### Added by the E2 corpus run

| | Finding | Evidence |
| --- | --- | --- |
| h14 | **A compartment clips its text instead of growing.** `currentLoan()`, `display()`, `copiesAvailable()`, `email is unique`, `slug is unique` are all cut off mid-line | `shelfmark-domain`, `tickbox-domain`. **The worst of the set** — a field the host supplied, the validator accepted and the file stores is silently absent from the picture |
| h15 | Note text clips the same way | `shelfmark-borrow` loses *"renewals and holds."* and *"interchangeable."* |
| h16 | Several edges leaving one region pile their end labels on one another | `shelfmark-domain`: `finePayments 0..*`, `finesTaken 0..*`, `payments 0..*` overlap. `tickbox-domain`: `memberships 0..*` twice |
| h17 | A guard on a long edge is placed at its midpoint, landing on top of whatever is there | `shelfmark-borrow`: `[no such membership number or barcode]` sits across the *"Is any open loan past its due date?"* diamond and hides half of it |

**h17 explains the "overlapping lines in the middle" report.** It is not forks as such. It
is **many long edges converging on one node** — five refusal paths into a single `Refused`
merge — each carrying a label at its own midpoint, so the labels stack in the same corridor
the lines run down.

### Outcome — the legibility measure, and what it cost

A measure was needed before anything could be judged, and it took three corrections before
it was worth trusting. It first counted an edge label landing on a block as *the block
clipping*; then counted wrapped fragments of a node's own label as foreign text; then
counted a `«block»` heading as an intruder. Each inflated the number. The honest figure:

| | curated | generated | total |
| --- | --- | --- | --- |
| before | 11 / 535 | 76 / 666 | **87 / 1201 — 7.2%** |
| after | **0 / 535** | 9 / 675 | **9 / 1210 — 0.7%** |

`h14`, `h15`, `h16`, `h17` are closed. `h12` is closed in the review tool rather than the
renderer: 18 of 45 diagrams put a 16px marker under 6px in a card, so anything wider than
700px now scrolls at full size instead of shrinking past the point its notation reads.

**`h10` is not fixed, and the attempt is worth recording.** The fork case is worse than
untidy — on `05-cicd-pipeline` the edges from the fork to the outer two branches route
*down through* the middle branch and exit its sides, so the picture says `Run Lint` feeds
`Run Unit Tests` and `Security Scan`. That is a false claim, not a cosmetic defect.

Three fixes were tried and **all three were reverted**, each on its own measurement:

| Attempt | Result |
| --- | --- |
| Prefer whichever of the two L-shaped paths crosses no node | Avoided **0** crossings. The anchor faces determine the path so completely that there is never a choice between a crossing L and a clean one |
| Add dog-leg candidates that turn in the gap between ranks | Made it **worse by one**, and changed 55 of 299 routes to do it |
| Choose the anchor faces obstacle-aware, before fan-out spreads the offsets | Works, and collides with two existing contracts: the shared `fanOutCases` fixture defines overrides as *changes from the natural anchor*, and the canvas mirrors `fanOutAnchors` but would not mirror the face search |

So the real fix is obstacle-aware **anchor selection**, and it is a change to the fan-out
contract and its frontend mirror rather than a routing tweak. That is `h18`, and it is
deliberately not being done at the end of a long round: 17 of 299 edges cross something, of
which the fork case is the one that misleads.

**Known divergence introduced here:** the canvas mirrors the endpoint fan-out and the
end-label formula, but not the label-collision search. A label may sit differently in the
editor than in the export.

### Incident — the corpus lost its provenance to a convenience script

Re-laying the 9 corpus diagrams out after the sizing fix, a throwaway script projected each
one down to a logical graph and reassembled it. The projection listed the keys it thought
mattered. **`origin` was not among them**, so every node and edge lost the evidence and
assurance behind it: 407 origins deleted, all 9 diagrams invalid with *"'origin' is a
required property"*, and the fact went unnoticed until the gallery was looked at.

The program is about provenance. It was destroyed by a helper written to move some
rectangles.

Three things it changed:

- **Never rebuild an artifact to alter its geometry.** The replacement runs layout over the
  existing document and writes back `position`, `width`, `height` and nothing else. A
  rebuild is lossy by default; an in-place edit is lossy only where it is told to be.
- **Assert what must survive.** It now counts origins before and after and refuses to
  write if the number moved, and validates before saving rather than after.
- **The generated diagrams are committed** inside each corpus repo. They were untracked, so
  there was nothing to restore from — recovery only worked because copies happened to exist
  from an earlier rendering step.

**Also carried in:** in a container-heavy use-case diagram the parent graph ranks actors
without knowing where the children sit, so an actor can be placed far from the use cases it
reaches. Same family as h11.

`kitepay-actors` measured **1128 × 2954** — 22 use cases in one column inside the subject.
That is h2 working as designed and then overshooting: stacking is right for four use cases
and wrong for twenty-two. Column count should follow the child count.

**Exit:** a stated measure for legibility, the four findings closed against it, and the
galleries regenerated.

**A1b** — audit, including: did any of this change a saved diagram it should not have?

---

## E — The evaluation loop

Reuses `render_example_gallery`, which already exists and already works.

- **Corpus A — conceptual.** The 36 existing prompt + answer-key pairs. Free. The host
  authors from the prompt; the gallery shows its output beside the curated key. Tests
  notation judgement: composition vs association, decision vs fork, include/extend
  direction.
- **Corpus B — grounded.** Real applications with a frozen written request each. No answer
  key is possible; the output is judged against a ground-truth description a human wrote.
  Tests evidence selection, grounding honesty, and scope.

**No dummy repos.** Synthetic code is written to be diagrammable, so the host aces it and
we learn nothing. `todo-api-fixture` proved the point: its `docs/architecture.md` listed the
layers, the external systems, and all four actors by name, which is why the P7 run produced
a perfect BDD on the first attempt. That was not the pipeline working, it was an open-book
exam.

### E1 — the corpus

Three working applications in `GraphPilot-Test-Repos/`, each runnable, tested, and seeded
into an interesting state. Ground truth lives in `_truth/<repo>.md`, **outside** the repo,
so the host can never read it.

| Repo | Stack | What it tests | State |
| --- | --- | --- | --- |
| `kitepay` | Django + SQLite, server-rendered | Money and double-entry; a payment flow spanning five files; `CASCADE` that is *not* composition | **done** — 1,809 lines, 25 tests, audit clean |
| `shelfmark` | Django + SQLite, server-rendered | Nothing is declared: loan state, fine amount and account lock are all computed. The lock rule is implemented three times and the copies disagree | **done** — 1,464 lines, 35 tests, audit clean |
| `tickbox` | FastAPI + React + SQLite | Scope across a two-tier boundary; permissions implemented twice and drifted | **done** — 1,205 py + 589 ts, 16 tests, audit clean |

`tickbox` was **built fresh rather than refactored** from `todo-api-fixture`. The intent was
to evolve it, but the fixture narrates its own architecture in docstrings as well as in
`architecture.md` — *"Nothing here touches storage… a model knows its own invariants"*,
*"the only place that chooses concrete implementations"* — so little survived removing that.
It keeps the fixture's FastAPI choice, which is what gives the corpus three framework shapes
instead of two Djangos and a clone. The fixture stays on disk, unused, as the worked example
of what not to build.

Every repo is audited before use against **R1–R8**, which asks whether it fails at *being a
test*: does it run, do the tests assert behaviour, is there a giveaway document, is every
claimed trap actually present, is it accidentally easy, does the ground truth match the
code, is the dead code genuinely dead but plausibly alive, does the seed data show an
interesting state.

That audit has already earned itself. It caught a `Loan` docstring reading *"There is no
status column — state follows from returned_at and due_on"*, which handed over the single
hardest thing in `shelfmark`, and it caught dead code that nothing imported and so fooled
nobody.

**No scoring, no judge, no run manifests, no authorization gates.** That apparatus existed
because the old pipeline cost money per run. Nothing here does.

**Exit:** one command produces a gallery reviewable in a sitting.
`render_example_gallery --from <dir>` reviews generated diagrams through the same page,
renderer and validator as the curated pool. One flag on the existing rig, not a second rig.

### What the two galleries are, and when each runs

They look alike and answer different questions. Confusing them wastes a review.

| | **Curated examples** — 36 | **Generated diagrams** — 9 |
| --- | --- | --- |
| Where | `backend/assets/blueprints/<type>/examples/answers/<name>/` | `<corpus repo>/.graphpilot/diagrams/` |
| What they are | Hand-written **answer keys**. A person wrote the prompt and the diagram | **Host output.** A cold agent read a real codebase and authored a draft; `diagram_create` did the rest |
| They answer | *Does the renderer draw the notation correctly?* | *Does the contract let a host describe a real system correctly?* |
| Count | 12 per type × 3 types | 3 repos × 3 types |
| Command | `render_example_gallery` | `render_example_gallery --from <dir>` |
| Cost | seconds, offline | three subagent sessions |
| When | after any layout or rendering change — it is a regression check | after an `F` change, because `F` is what it measures |

Neither scores anything, and that is deliberate: **no judge, no run manifests, no gates.**
That apparatus existed when a run cost provider money. Nothing here does, so the output is
a page a person looks at.

**The generated run is not yet one command.** It took three subagents driven by hand. That
is the honest gap in the rig: `F`'s exit criterion is *"measured improvement in host
authoring"*, and the baseline to beat is **18 `diagram_create` calls for 9 diagrams** —
re-running it means orchestrating three agents again.

### E2 — the run

**Three fresh subagents, one per repo, acting as the host.** Each was given the codebase
path, the MCP transport, three requests, and told to start at `diagram_workflow`. None had
seen the repo before, none could read `_truth/`, and none was told how to author a draft.
That makes this the **cold-host run** `f2` asks for as well as the corpus run.

**Result: 9 of 9 diagrams accepted, in 18 `diagram_create` calls.**

| Repo | BDD | Activity | Use case |
| --- | --- | --- | --- |
| kitepay | 2 attempts | 1 | 1 |
| shelfmark | 2 | 4 | 1 |
| tickbox | 2 | 4 | 1 |

Every use-case diagram was clean, and in both repos that took four attempts it was the
*third* diagram authored — clean only because the first two had paid for the lessons. As
one host put it: *"authored first it would have taken 4 attempts too."*

**The semantics were consistently good, and that is the real result.** Judged against the
ground truth the hosts could not see:

- `shelfmark-domain` kept `Book` and `BookCopy` separate — the classic library modelling
  error — and **invented no `Fine` entity**, noting instead that *"a fine is never stored…
  only payments are rows"*. That is the hardest thing in that repo.
- `tickbox-domain` drew `Membership` as its own block carrying `role`, and found the
  `after_update` roll-up hidden at the bottom of `models.py`, **including** the un-tick
  asymmetry.
- `shelfmark-borrow` found all five refusal gates and noted that the overdue test runs
  twice with only the second weighing the balance — trap 3, stated precisely.

**They also found two real defects nobody planted**: `/api/v1/todos/{id}/complete` calls
`require_member` instead of `require_writer`, so a **viewer can complete a task**; and
`payments/legacy_transfer.py` can create a `Payment` with no ledger entries, so the
double-entry invariant the whole of `kitepay` rests on is not actually guaranteed. The
corpus is doing its job.

**Presentation was consistently poor at viewing scale**, which is what `H2` is for, and the
run added four findings to it. **The contract was the weak point**: three independent hosts
produced overlapping lists of gaps, folded into `F` and `G` below.

**A2** — is the rig earning its keep, and does it tell the truth?

### A2 — outcome

The original test was *"count files added against product changed"*, and counting turned
out to be the wrong question. By file count the rig is **two files** — one management
command and its test — with the corpus living outside the product repository entirely. That
bound held easily and told us nothing.

Three findings, none of which a file count would have surfaced.

| | Finding | Fixed |
| --- | --- | --- |
| a2.1 | **The review page disagreed with the product.** `_relayout` passed each node's *saved* size, but a BDD classifier is sized from its compartments at materialization — so a block committed before a sizing change kept a stale height and clipped text the real pipeline fits. The page under-reported the product it reviews | yes |
| a2.2 | **The numbers could not be reproduced.** Every figure quoted during `H2` came from throwaway scripts in `%TEMP%` — **55 of them, none committed**. When the session ended the metrics would have evaporated and only the prose claims survived. Legibility is now computed by the gallery and shown on the page | yes |
| a2.3 | **`h18` had no regression test.** Faces are now chosen obstacle-aware, and nothing would have caught that being undone. `test_no_committed_example_routes_an_edge_through_a_node` guards it | yes |

The measure disagreed with itself twice while being moved into the product — once over
container nodes, once over use-case extension points. The committed version now reproduces
the review figures exactly: **0 of 535** on the curated set, **9 of 675** on the generated
one. That the two implementations differed at all is the argument for having one.

### Does `E3` proceed?

**Yes.** The rig is small, it has caught real defects — the origin deletion, the clipping,
the misleading fork routes — and its worst problem was the opposite of bloat: measurements
that existed nowhere. `E3` mostly adds *product* (a draft log, a dry-run tool, worked
examples the contract serves) with one scaffolding item, the run sheet, which dies at close.

**The gate that replaces the file count**, for anything E3 adds:

1. **Does each piece name an owner and an end?** Scaffolding must say which package it dies with.
2. **Can someone else reproduce the numbers?** A figure that only its author can regenerate is not a measurement.
3. **Is anything a second rig?** One review path. That rule has held.

---

## E3 — Make generation measurable

The charter says the pipeline is not yet *"trustworthy to look at, or **measurable**"*. `h`
fixed the first. **Nothing has fixed the second.** `E1` built a corpus and `E2` ran it once
by hand; a corpus and a run are not a framework. This is the half that was named on line one
and never given a package.

### The state it is in

There is **one** management command in the repository, `render_example_gallery`. There is no
debug, verbose or trace option anywhere in drafts, materialization or the MCP server, and
the whole generation path contains a single logger call — an error handler. `diagram_create`
states plainly that *"the draft is not stored"*.

So a refused draft leaves **no trace at all**: not the draft, not the findings, not the fact
that it happened.

| Question | Answerable today |
| --- | --- |
| How many attempts did that diagram take? | no |
| Which field caused the refusals? | no |
| What did the host actually submit? | no |
| Has authoring got easier since last month? | no |

**`F` is gated on a number nothing produces.** "18 `diagram_create` calls for 9 diagrams" is
known only because three subagents said so in prose. `A0` missed this because it audited
correctness, not observability.

### The distinction that makes it tractable

"Better authoring" is two things, and conflating them is why this stayed vague:

| | | Judged by |
| --- | --- | --- |
| **Friction** | how hard the contract is to satisfy — attempts, refusal codes, which field | a machine |
| **Correctness** | whether it is the *right* diagram | a person, against ground truth |

**`F` is gated on friction.** That is where the 17 known defects are, it moves when
instructions change, and it costs nothing to measure. Correctness barely moved in `E2` — the
hosts got the semantics right *despite* the contract, so it is a poor signal for instruction
work and an expensive one to collect.

### Work

| | Work | Tier |
| --- | --- | --- |
| e5 | **A draft log**, opt-in and off by default: one appended record per `diagram_create` — name, type, accepted, finding codes, element and evidence counts. The metric `F` needs, and the answer to "why does it keep refusing me" | 1 |
| e6 | **`diagram_validate_draft`** — the dry run `g8` asks for. A host cannot currently test a draft without attempting a real write, which is also why attempt counts are inflated | 2 |
| e7 | **Move `g1` here**: give each of the 36 examples a `draft.json` and assert `materialize(draft) == output.gp.json`. It belongs with measurement, not with the transform — it is what turns the corpus from a rendering check into a pipeline check | 1 |
| e8 | **Rename `examples/eval/` → `examples/answers/`.** Nothing evaluates it; it is the renderer's regression corpus. The name is debris from the retired scoring pipeline and it misleads on sight | 1 |
| e9 | **A run sheet**: the three repos and the exact prompts, version-controlled, so two runs are comparable. **Vague prompts this time** — `E2` told each host the type, the name *and* the subject, so type selection was never tested. → [`run-sheet.md`](run-sheet.md), the program's second and last file | 1 |
| e10 | **Mark which examples are taught, and show them.** A tag promotes an example to *training*: its draft is what `diagram_get_authoring_contract` serves as the worked example. The gallery gains a third section for exactly those, so what a host is taught is visible and reviewable | 1 |

### e10 — the third section, and why the gallery needs one

The gallery answers *"is the output good?"* twice — once for the renderer, once for the
contract. It cannot answer **"is what we teach good?"**, and that is the question behind the
single worst finding of the corpus run: `diagram_get_authoring_contract` returns
`"example": null` for `activity_diagram` and `use_case_diagram`, and the example is the only
place the draft envelope is defined anywhere. A host asked for an activity diagram alone
**cannot author a valid draft**.

Once `e7` gives every example a draft, the fix is nearly free — a curated example already
*is* a worked example, in the right shape. What is missing is a way to say *which* ones, and
any way to look at them.

| | | Answers |
| --- | --- | --- |
| **Answers** — 36 | hand-written; the renderer's regression corpus | does the renderer draw notation correctly? |
| **Training** — a tagged subset | the drafts the contract serves to hosts | is what we teach any good? |
| **Generated** — 9 | cold-host output from real repositories | does the contract work on a real system? |

Training is a **subset of answers, not a fourth artifact** — promoted by a tag in
`prompt.md`, so there is one file to maintain and a promoted example is provably one that
already passes every regression assertion. It also cannot silently rot: the same tests that
guard the corpus guard whatever the contract is serving.

Choose for readability rather than coverage. A regression example should be varied and
awkward; a worked example should be small enough to read in one go and show the whole
envelope — `request`, `scope`, `evidence`, `uncertainties`, `assumptions`, `decisions`.
Expect one or two per type, not twelve.

**`e10` builds the surface; `f1` uses it.** Marking and showing is measurement and belongs
here. Changing what the contract *returns* is an instruction change and belongs in `F`.

### Constraints

This package builds apparatus, which is what the rules were written to restrain. So:

- **It must not add more files than it changes.** If it does, stop and report.
- **The draft log is product, not scaffolding** — "why was my draft refused" is a real user
  question — and stays. **The run sheet is scaffolding** and is deleted at close.
- No scoring, no judge, no pass/fail thresholds. It reports numbers; a person decides.

**`A2` runs first and is a real gate.** It asks whether the corpus is earning its keep — and
if the answer is no, `E3` does not happen and `F` proceeds on the prose baseline. Ordering
`A2` before the package it governs is the point; the previous ordering had it rubber-stamping
work already done.

**Exit:** re-running the corpus produces a friction number without anyone writing prose, and
the same number exists for the run before it.

---

## E4 — Make generation reviewable

`E3` made authoring measurable — a number that exists before and after. This makes the
output **reviewable**: one page where a person decides whether a generation was any good,
and can tell *which stage* went wrong when it was not.

The surface built so far grew a section per idea — curated, training, generated — a tag to
promote an example, a `prompt.md` reader, and a 1,280-line command. That is structure where
a distinction would do, and it actively misled: showing a draft and a diagram side by side
with nothing saying the first is discarded led a reviewer to believe uncertainties were
being persisted when they never are.

### One card, four buttons, one marker

Every diagram in `assets/` is a card of the same shape:

> **Prompt · Draft JSON · Diagram JSON · Open** — and a marker saying **from a repo** or not.

No sections per idea. The one distinction that carries meaning is **how far back it can be
regenerated**:

| | prompt → draft | draft → diagram → SVG |
| --- | --- | --- |
| **answers** — conceptual | never ran | **deterministic**, re-runs identically |
| **generated** — from a repo | an agent did it once | deterministic |

That is why `prompt.md` goes. `prompt → draft` needs a model, so it can never be
reproducible, and a file pretending to be that stage invites a regeneration that would
differ every run. The request is not lost: it already lives in the draft as
`request.original`, so the Prompt button reads *from the draft*.

### Work

| | Work | Tier |
| --- | --- | --- |
| e11 | **Store the draft** at `.graphpilot/drafts/<name>.draft.json`, beside the diagram it produced. A traceline: when a generation is wrong, the draft says what the host actually claimed. **This does not reverse `D1`** — that decided what goes *inside* the `.gp.json`, and the answer is still nothing. `diagram_create`'s description currently says "the draft is not stored", so this is a contract change | 2 |
| e12 | **Delete `prompt.md`.** Its request duplicates `draft.request.original`; its remaining tags — `paraphraseSet`, `register`, `complexity`, `reviewer` — are debris from the retired scoring pipeline, the same leftovers as the `eval` folder name | 1 |
| e13 | **Three pools, one structure**: `answers/` (36), `generated/` (the 9, moved into `assets/` so review has one home), `training/` (what the contract serves) | 1 |
| e14 | **One card shape** and one marker. Delete the training tag, the promoted-subset mechanism, and the per-section special cases | 1 |
| e15 | **Replace the training examples.** The `todo-*` set goes. Authored fresh **in the same change** — `diagram_get_authoring_contract` must return something or `f5` reopens and a host cannot author at all | 1 |
| e16 | **One command.** `review_gallery` is what a person types; `render_example_gallery` is 1,280 lines because every idea was added to it, and one card shape should shrink it | 1 |
| e17 | **The draft becomes the only source** — see below. Reopened the package | 2 |

### e17 — the page never ran the pipeline it claimed to review

`E4` was marked complete against the exit criterion below, and did not meet it. The gallery
re-ran **layout** over a saved canonical document and called that "what the code draws".
Layout never touches semantics, markers, edge dashing, route mode, ends or `origin`, so a
change to the composition-diamond rule could not have moved the page — and the page would
still have said it was current. It was marked complete because the cards looked right.

Now every card with a draft is `materialize(draft)`, built in memory by the run that drew
the page; a card without one is drawn from its saved document and badged `stored`. That is
39 and 9 respectively, the nine being the corpus diagrams generated before `e11` stored
drafts.

| | Work |
| --- | --- |
| e17a | Materialize in `_build_card`; delete `_relayout`; `provenance` replaces `fromRepository`, which was one field doing two jobs — a label *and* a behaviour switch, which is why the worked examples were never regenerated |
| e17b | `--regen {eval,generated,all}` on both commands, replacing `review_gallery --render`. It writes what a draft produces and **never a draft** |
| e17c | The `corpus-run` skill, so the host half is repeatable; `run-sheet.md` reduces to results |
| e17d | The baseline corpus run itself |

**Four defects in the committed answers**, all from one cause — the `e7` script called
`assemble_canonical` directly instead of `materialize`:

| | |
| --- | --- |
| **No `metadata.authority`** | all 36. The field saying whether a diagram claims to describe a repository was missing from every answer key, in a program about evidential honesty |
| **An unproducible name** | `"E-Commerce Checkout"` is not a legal `diagramName` — the contract requires a slug — so no host could ever have generated it. Same class as `e7`'s 316 unauthorable ids |
| **The wrong serializer** | `WorkspaceStorageService` writes `sort_keys=True, ensure_ascii=False`; these were unsorted and ASCII-escaped. Two ways of writing a diagram is the duplicate-rule defect class |
| **Non-idempotent regeneration** | timestamps are generated per materialization, so a naive `--regen` produced a diff every run and "no diff" stopped being evidence. They are carried forward now, pinned by a test |

Semantics and geometry are byte-identical across all 39 — verified by rebuilding each and
comparing ids, semantic types, labels, parents, features, positions and sizes.

**Exit:** after any generation, one page says whether it was good, and a bad draft is
distinguishable from a bad picture.

---

## G — Lock in the transform

| | Work |
| --- | --- |
| g1 | **Moved to `E3` as `e7`** — giving each example a draft is what turns the corpus from a rendering check into a pipeline check, so it belongs with measurement. The detail stays below |
| g2 | Cover the unverified surface: BDD primary stereotype heading, multiplicity on both ends, note attached to each element kind |
| g3 | Retire or rename `diagram_get_schema`. **Confirmed a trap by two hosts**: its description says *"call before building a diagram to learn its required structure"* and it returns `nodeRequiredFields: ["id","type","position","data"]` — precisely what the workflow forbids authoring. A host reading tool descriptions in order is walked into hand-authoring nodes |

### e7 (was g1) — an example should be a draft, not a picture

A curated example is two files: `prompt.md` and a **hand-written** `output.gp.json`. Nobody
ever authored a draft for one. So the corpus starts *after* materialization, and the stage
where the notation rules live — the filled diamond coming from the relationship type, edge
dashing, end policy, route mode, origin construction — is never exercised by a realistic
diagram.

It is not untested: `test_bdd_materializer` (19), `test_activity_and_use_case_materializers`
(12), `test_diagram_creation_service` (13) and `test_mcp_server` (9) cover the rules at unit
level. What is missing is **one realistic 15-node diagram going end to end**, where rules
interact.

Each example becomes three files:

| | |
| --- | --- |
| `prompt.md` | what a person asked for |
| `draft.json` | what a host should have written — the answer key moves here |
| `output.gp.json` | what materialization must produce — expected, no longer source |

and three assertions: `materialize(draft) == output`; the output still validates, lays out
and renders; every notation rule appears in at least one draft.

The drafts derive mechanically from the canonical files that already exist — nodes become
elements, edges become relationships, `authority: conceptual` because these cite no
repository.

**Keeping `output.gp.json` is the point.** A draft alone would mean a materialization bug
silently rewrites the answer with nothing to compare against; keeping both pins the
transform *and* the picture, and covers canonical → render separately from draft →
canonical.

**Deliberately not done before `F`.** It is a coverage gap, not a known defect: 53 tests
cover the rules, and three cold hosts produced nine diagrams with no materialization failure
of any kind. `F` has 17 known defects and a baseline to beat.

### Defects found by the E2 run

| | Defect | Why it is a defect and not a preference |
| --- | --- | --- |
| g4 | **`metadata.request` is specified and not implemented.** [`02-materialization.md`](../../03-design/01-generation/02-materialization.md) migrates `generationContext.requestRef` to *"`metadata.authority` and `metadata.request`"*. `metadata.request` is in neither the schema nor the materializer | A written design contradicted by the code. `A0.5` class, and `A0` missed it |
| g5 | **An assumed element persists a reference to nothing.** The node keeps `origin.assumptionRefs: ["asm-single-commit-path"]` and `rationale: "Accepted as an assumption: asm-…"` while the assumption's `statement`, `reason` and `acceptedBy` are discarded | A dangling pointer in a shipped artifact. Either persist the body or drop the reference; keeping the id alone is the one indefensible option |
| g6 | **A field can be valid, persisted, and undrawable.** `features.operations[].returnType` and `features.constraints[].name` are accepted, written to the `.gp.json`, and never rendered | *"A field that is valid, persisted, and invisible is worse than a rejected one."* Either reject it or mark it metadata-only |
| g7 | **`error.code` changes shape with the finding count** — generic `draft_invalid` for nine findings, the finding's own code (`orphan_assumption`) for one | A host keying off `error.code` sees an unstable contract |
| g8 | **No dry run.** `diagram_validate` takes the canonical artifact the host is forbidden to author, so the only draft validator is `diagram_create`, which writes files and refuses to overwrite | Every typo costs a create attempt, and a successful-but-wrong create burns the name with no update, overwrite, or delete path. A read-only `diagram_validate_draft` closes both |

### A3 — notation coverage — **complete**

Every semantic type in the catalog should appear in at least one *rendered* fixture.
Anything unreachable is either dead vocabulary or an untested path.

**The authorable vocabulary is completely covered.** All 26 authorable semantic types
across the three diagram types appear in a fixture *and* in a draft — nothing is exercised
only through a hand-written canonical file. Zero gaps.

**The catalog is another matter: 78 of 98 entries cannot be authored by anything.** Most
are harmless aliases sharing an already-exercised primitive; 34 are `rounded-rect`. But
**nine primitives have no authorable member at all**, so nothing in any fixture, test, or
corpus diagram reaches them:

| Primitive | Catalog entries |
| --- | --- |
| `partition` | `activityPartition` |
| `region` | `conditionalNode`, `expansionRegion`, `interruptibleActivityRegion`, `loopNode`, `sequenceNode`, `structuredActivityNode` |
| `pin` | `inputPin`, `outputPin`, `actionInputPin`, `expansionNode`, `valuePin` |
| `port` | `port`, `fullPort`, `proxyPort` |
| `object` | `objectNode`, `centralBufferNode`, `activityParameterNode` |
| `accept-event` | `acceptEventAction`, `acceptCallAction` |
| `send-signal` | `sendSignalAction`, `broadcastSignalAction` |
| `datastore` | `dataStoreNode` |
| `flow-final` | `flowFinalNode` |

**Both renderers implement all nine.** The SVG exporter and the canvas carry 19 primitive
branches each and are in parity — so these are nine drawing paths, in two implementations,
that no test can reach.

**`partition` is swimlanes**, which all three cold hosts named as their single biggest
loss: every flow crossed view → service → signal → ORM with no way to show the boundary.
The drawing code already exists in both renderers. Exposing it is a profile change, not a
feature build — which reframes it from "a notation we lack" to "a notation we built and
never connected".

Recorded as `g9`. Not fixed here: enabling a semantic type is an MCP-facing contract
change that belongs with `G`, and choosing *which* of the nine to expose is a product
judgement rather than an audit finding.

---

## F — Tune instructions on evidence

| | Work |
| --- | --- |
| f1 | **Done.** A worked example for every type — see below. Also closes `f5` and `f10` |
| f2 | Cold-host run. **Done in E2** — three fresh hosts, 9 of 9 accepted in 18 calls |
| f3 | Iterate instruction wording against the gallery |
| f4 | Validate the draft sizing guidance — "8–30 evidence, 5–25 elements" is currently a guess |

### f1 — a worked example that teaches, per type

`diagram_get_authoring_contract` returned `example: null` for two of three types, and the
example is the only place the draft envelope is written down. A host asked for an activity
or use case diagram **could not author a valid draft at all**. Two cold hosts reported it
independently; it was the worst single thing in the surface.

**Promoting a curated answer key was tried first and abandoned.** It was the tidier design —
one artifact, already regression-tested — and it taught nothing. An answer key is
`conceptual`: it describes a description, so it cites no evidence and carries no
uncertainty, assumption or decision. Measured across the three that were tagged:
`evidence=0 uncertainties=0 assumptions=0 decisions=0`, every one. Those are exactly the
fields hosts got wrong — three of one host's four refusals came from `assumptions` alone.
A worked example that demonstrates only the easy half is worse than none, because it looks
complete.

So the three are purpose-written, all `as_implemented` against one fictional service, and
each one uses the whole envelope. Seven assertions keep them honest, including that
between them they show **every** `decisions[].kind` — a field nobody demonstrates is a
field hosts guess at.

**Two defects surfaced while writing them**, which is the argument for writing them at all:

- **`f10` confirmed by hitting it.** The first `scope` decision drafted was refused —
  `'scope' is not one of ['labeling', 'grouping', 'presentation']`. The honesty rules are
  largely about what you left out and the vocabulary had no way to say so. `scope` added.
- **`h19` — a use case's extension points were drawn outside it.** `extensionPoints` became
  authorable in `E3` and the renderer had always drawn them 30px below the centre; nothing
  sized the ellipse to hold them, so the first diagram to use the field spilled the
  compartment out of the bottom. Exactly the drawer/sizer disagreement H2 found in BDD
  blocks, in a diagram we were about to teach from.

**Still wrong in `todo-actors`, deferred:** the `«extend»` label is drawn across the use
case beside it, because the two sit closer than the label is wide. Same family as `h11`,
and a label-placement fix rather than an example fix.

### What the cold hosts actually hit

Every row below was reported independently by **two or three** of the three hosts. Ordered
by how much it cost them.

| | Gap | Consequence |
| --- | --- | --- |
| f5 | **`example` is `null` for activity and use case, and the example is the *only* definition of the draft envelope.** `request`, `scope`, `evidence`, `uncertainties`, `assumptions`, `decisions` are described field-by-field nowhere else | *"A host that asks only for the activity contract cannot author a valid draft at all."* All three got through only by fetching the BDD contract first and copying its envelope |
| f6 | **`required` points at a document that does not exist** — *"See the `request` section of the draft contract"*. No tool returns it | `request.authority` and `request.detailLevel` enums are unobtainable; all three guessed |
| f7 | **`assumptions[]` is undocumented in every respect that matters** — requires `id`, `statement`, `reason`, `acceptedBy`; `acceptedBy` ∈ `host \| user`; must be referenced or it is refused | Three of one host's four refusals were this single field, in three separate rounds |
| f8 | **Nothing lists the permitted element keys** | One unknown key (`description`) produced 12 of 13 findings in a single refusal |
| f9 | **Multiplicity has no documented encoding for "many"** — the only example is `1..1`, `null` is rejected, `"*"` works | Cost two hosts a refusal each. The honesty rule *"an absent multiplicity is honest"* gives no hint that "many" is expressible at all |
| f10 | **`decisions[].kind` appears only in a rejection message** — and a *scope* decision has no home in `labeling \| grouping \| presentation` | Hosts filed scope judgements under `presentation`, which misdescribes them. The honesty rules are mostly about scope; the decision vocabulary has no scope kind |
| f11 | **`features.literals` is `string[]` while `properties` and `constraints` are object arrays** — named together in one sentence, neither shape defined | Refusal, then a guess |
| f12 | The contract response puts `diagramType` at the top level, beside `schemaVersion` and `kind`, which *are* top-level draft fields | A host mirroring the envelope gets `additionalProperties`. One sentence closes it |
| f13 | Other enums shown by example only: `evidence[].kind`, `request.detailLevel` | `"test"` was accepted; the host still does not know whether it means anything |
| f14 | `assurance` / `evidenceRefs` on **relationships** are used in the example but documented only for elements | One host supplied them on all 75 edges without knowing it was allowed |
| f15 | *"Every reason comes back at once"* is **false across stages** — schema findings gate semantic ones | Sets the expectation of one retry. Assumptions took three rounds: missing field → bad enum in that field → orphan reference |
| f16 | `locator.path` is never stated to be relative to `workspaceDir` | Inferred from the example. Getting it wrong would silently mis-digest |
| f17 | Guards are auto-bracketed; undocumented | An author may ship `"[owner or editor]"` and get double brackets |

### What the second corpus run found

17 diagrams from three cold agents, all accepted. The **number is void** — the contract
changed mid-run, see [`run-sheet.md`](run-sheet.md) — but the reports stand.

**`diagram_check_draft` paid for itself immediately.** Two of three hosts had **zero**
`diagram_create` refusals, and both said plainly that this was the dry run's doing, not
their own accuracy: tickbox caught three problems across nine checks, kitepay two. Without
it those would have been five refused creates and five spent names.

| | Found | Status |
| --- | --- | --- |
| **g10** | **`symbol` was never checked against the lines it points at.** Fixed — and rebuilding the 17 shows **7 miscite**, including `CheckoutForm` cited as `desk/forms.py` lines 1–5 when it is at line 7, and a test cited 17 lines above itself | **fixed** |
| f18 | The workflow claimed `diagram_check_draft` returns the "same findings". It never did — the tool's own reply said `notChecked: [evidence locators resolve]`. One host trusted the workflow, got "this draft would be accepted", and was refused twice | **fixed** |
| f19 | `diagram_check_draft` could not check citations, the one class of error that is unrecoverable: the name is spent and nothing overwrites it. It now takes an optional `workspaceDir`. **Both hosts asked for this independently** | **fixed** |
| f20 | **`features.constraints` cost every host two to six probe rounds.** One sentence names `operations`, `constraints` and `literals` together; the example shows two of the three, with different shapes, and never `constraints`. The word `expression` appeared nowhere | open |
| f21 | **`orphan_evidence` is a real rule stated in no contract.** All three tripped it. The message itself is the best in the set | open |
| f22 | **`conceptual` is an undocumented third `assurance` value.** The honesty rules name two. A host's first conceptual diagram fails on every element at once | open |
| f23 | **The contract orders a guess.** Composition says *"the part's role and multiplicity — state them"*, the validator does not enforce it, and the honesty rule says *"prefer omission to a guess"*. A host reported this as **the only place in six diagrams it knowingly invented something** | open |
| f24 | `schema_maxLength` states neither the limit nor the actual length. A host binary-searched `diagram_check_draft` to discover 256. `schema_pattern` quotes its rule; this does not | open |
| f25 | Nothing says when a diagram is too big, and nothing reports it. `operationWarnings: []` came back on a 26-node diagram. Legibility is measured in the gallery and never returned to the author | open |
| f26 | `diagram_create` writes into the repository under study and nothing says so. One host had to infer that its own output was exempt from "do not modify the codebase" | open |
| g3 | `diagram_get_schema` is a trap — **all three hosts**, now five reports across two runs | open |

### Notation the hosts wanted and could not reach

Not necessarily work — but the same absences came up in all three reports, so they are
evidence about the vocabulary rather than opinion.

**Swimlanes / partitions** was named by all three as the biggest loss: every flow crossed
view → service → signal → ORM, and `tickbox` crossed two languages, with no way to show the
boundary. Then: a **derived** marker (`/balance`) for the many computed properties; a
**deprecated** marker for dead code, which all three found and none could express; an
**element-level description**, forcing a `note` plus a `commentLink` for every remark; a
**precondition** on a use-case association; and **cross-diagram references**, so three
diagrams of one system need not stay three unrelated files.

**Exit:** measured improvement in host authoring across corpus B.

### A4 — contract drift — **complete**

Does the authoring contract still derive everything from the schema, profile, and
end-policy tables, or has hand-written prose crept in that can drift from the validator?

**On drift, clean — and that is the weaker half of the audit.** The advertised vocabulary
equals the profile the validator enforces for all three types; all 23 envelope sections
match the schema's own `properties` and `required`; each worked example is a draft the
validator accepts; the prose names no tool that is not registered.

**Then it asked a better question and found fourteen.** Not *"does the prose contradict a
rule"* but *"is there a rule with no prose at all"* — which is the shape `orphan_evidence`
had, a hard refusal all three cold hosts discovered by being refused.

Enumerating every code the draft path can emit: **14 of 19 could only be learned by
tripping them.** `guard_required`, `containment_unsupported`, `notation_invalid`,
`evidence_required`, `evidence_unexpected`, `stereotype_unsupported` and the rest were
enforced, and explained nowhere a host reads.

The contract now publishes all 19 as *What will get a draft refused*, and
`test_every_refusal_code_is_explained_before_a_host_trips_it` **reads the codes out of the
services** rather than from a list beside them — so adding a refusal without explaining it
fails in the suite rather than in front of a host. Transport failures are excluded and
named: a malformed call or a bug on our side is not something a host can author around.

Contract prose: 60 lines before `F`, **276 after `F` and `A4`**.

---

## P8 — Assurance display, final gate

Carried over from the draft-first program and deliberately placed last: a correct diagram
that reads as the wrong graph is a worse problem than a missing badge. Mark `assumed`
elements in the editor, surface the evidence behind a `grounded` one, take the final gate.

---

## D — Rewrite the documentation to describe the system that exists

**20 of the 30 active documents describe a pipeline that was deleted.** 328 lines reference
JSON 1 / JSON 2, evidence manifests, readiness assessment, `generationContext`, or the six
MCP tools removed in `P0`. Six of them are the documents that say what GraphPilot *is*.

This is the same failure the whole program is about. A diagram that looks right and is
wrong is worse than no diagram, because someone acts on it — and a requirement written in
the present tense for a tool that does not exist is worse than no requirement, for exactly
the same reason. `FR-6`, `FR-7` and `FR-8` are not out of date; they are fiction.

**Why it happened, and why it will again.** The rules say documentation is part of the
change. `P0` removed the provider pipeline from the code and left it in the docs, and
nothing anywhere compares a document to the source. The rule was not enough on its own.

### Audit first, then rewrite

The 328 lines above came from grepping for **vocabulary I already knew was retired**. That
finds what is obviously dead and nothing else. A document can be wrong in ways no keyword
search reaches: a behaviour that changed, a path that moved, a flag renamed, a schema field
dropped, a promise written and never built — `A0` found `metadata.request` documented as a
migration and never implemented, and it survived three audits because nobody was comparing
claims to code.

So `D` is two halves, and the first one finishes before the second starts.

| | Work |
| --- | --- |
| d1 | **Audit all 30 active documents.** Every claim checked against the source, not only the six that grep caught. Findings recorded in this file as a table — no audit document |
| d2 | **Rewrite.** Fix everything `d1` found, document by document, committed one at a time |
| d3 | **A guard, so it cannot drift again.** The rule "documentation is part of the change" already existed and did not hold; something has to fail when a document and the code disagree |

### What `d1` checks, claim by claim

A document makes a small number of kinds of claim, and each kind is mechanically checkable.

| Claim | Checked by |
| --- | --- |
| names a **tool or command** | it is registered, and its flags match `add_arguments` |
| names a **file or directory path** | the code writes or reads that exact path |
| names a **schema field** | it is in the schema, and something produces it |
| names an **error code** | some code path can emit it |
| names a **service, class or function** | it exists and is reachable from a caller |
| states a **behaviour** | a test asserts it, or the source plainly shows it |
| shows a **worked example** | it validates against the schema it illustrates |
| **links** somewhere | the target exists — already covered by the link check |
| **owns a topic** | `AGENTS.md`'s table agrees, and no other document restates it |

Two documents describing the same topic differently is its own defect: the rules say one
owner per topic precisely so they cannot disagree, and the README listing five deleted MCP
tools while `01-diagram-tools.md` listed the real ones is what that looks like.

### What each document has to say instead

Known before `d1` starts. The audit will add to this.

| Document | Wrong now | Should say |
| --- | --- | --- |
| `01-product/01-overview.md` | a Mermaid flow of JSON 1 → JSON 2 → readiness → generation | a host reads the repository, authors one draft, and `diagram_create` materializes it with no provider call |
| `01-product/02-user-scenarios.md` | scenarios built on manifests, request files, and reassessment | the two journeys that exist: an IDE host generating, and a person editing in the browser |
| `01-product/03-requirements.md` | `FR-6` JSON 1, `FR-7` JSON 2, `FR-8` readiness — whole requirements for deleted tools | requirements for the draft contract, materialization, assurance, and the review surface |
| `02-architecture/02-system-design.md` | a two-stage provider architecture | one stage, deterministic, provider-free |
| `02-architecture/.../04-operation-errors.md` | `manifest_not_found`, `manifest_conflict`, `evidence_validation_failed` and others nothing can emit | only codes the code can actually return, checked against the source |
| `03-design/02-diagram-schemas/01-diagram-json-schema.md` | `generationMode` and `generationContext` in its worked examples | the metadata the schema actually carries — and `a5.f2` first, because it currently constrains nothing |

**`05-delivery/04-decisions.md` is not in scope and keeps its history.** It is appended over
time and is explicitly not design canon, so a decision about a pipeline later retired is a
true record of a decision that was made.

### `d3` — the guard

"Documentation is part of the change" is already a rule and it did not hold, so `D` leaves
behind something that fails rather than something that reminds.

The cheapest honest version is a test over the active documents that asserts the
mechanically checkable claims: no retired vocabulary outside `04-decisions.md` and
`docs/07-history/`; every MCP tool named in a document is registered; every management
command named exists; every `.graphpilot/` path is one the code actually uses. It cannot
catch a wrong sentence, but it catches every class of drift found here — all of which was a
name outliving the thing it named.

**Exit:**

- `d1` has read all 30 documents and every finding is in this file
- `d2` has fixed them, and each rewritten claim traces to code
- `d3` fails if a document and the source disagree in any of the checkable ways
- one owner per topic, agreeing with `AGENTS.md`
- `A5` can then audit documentation it did not itself write

---

## A5 — Full-repository audit, and close

Every audit so far was bounded to the package before it. This one is not: **every line of
source, every document, every command.** It runs last because it is the only point at which
the system is finished enough to be judged as a whole, and it closes the program.

The case for it is the record. Six times this program found something the suite could not
see — 11 design defects in `A0`, answer keys the product could not produce, worked examples
citing files that do not exist, 407 origins deleted while every test stayed green. The
common factor is that nothing was looking at the whole.

### Scope

Roughly **16,700 lines of Python**, **14,400 of TypeScript**, and **42,900 lines of
Markdown** across 350 documents. Not a skim: every file is opened.

### What it checks

| | Check |
| --- | --- |
| a5.1 | **Dead code.** Anything the retired generation workflow left behind — unreferenced modules, unreachable branches, settings nothing reads, tests asserting removed behaviour. If nothing imports it and nothing validates against it, it goes |
| a5.2 | **Redundant logic.** Two implementations of one rule is the defect that produced the compartment clipping and the container divergence. Find them and collapse them |
| a5.3 | **Correctness.** Real bugs: wrong boundaries, unhandled shapes, silent excepts, anything that can throw where a caller assumes it cannot |
| a5.4 | **Performance.** Work repeated per node that could be done once, files re-read in a loop, an O(n²) that meets a 256-node diagram |
| a5.5 | **Convention.** The repo's own rules, applied to the repo: docstrings that say why, no restated topic owners, canvas and export in parity |
| a5.6 | **Commands.** Every management command inventoried. Anything a person would not run and no test calls is deleted |
| a5.7 | **Docs match code** — *verified here, rewritten in `D`*. `D` runs first and fixes the 328 lines describing the retired pipeline; this slice checks the result, plus every document `D` did not touch. An audit that rewrote the documentation could not then audit it. **Plus the MCP surface, which moved after `D` closed** — see below |
| a5.8 | **The command reference.** A single document listing every command a person actually runs — the server, the frontend, the tests, the review gallery — with each flag and what it means. `AGENTS.md` has fragments; nothing has all of it |
| a5.9 | **Program close.** Scaffolding named in `E3` and `E4` is deleted: the run sheet dies here. The program collapses to one summary in `docs/07-history/` |

### a5.7 carries a known backlog: the MCP surface moved after `D` closed

`D` audited every active document and rewrote 65 false claims. It was correct when it
landed and is **partly stale already**, because
[`08-contract-efficiency`](../08-contract-efficiency/plan.md) changed the tool contracts
afterwards. That is not a failure of `D` — it is what happens when a documentation sweep
and a contract change run in the same week — but the sweep does have to be redone for
this surface, and the changes are known rather than guessed:

| Moved | Was | Is |
| --- | --- | --- |
| contract response | `diagramType`, `required`, `notation` | `contractFor`, `topLevelFields`; `notation` deleted |
| `guidance` | one Markdown string | a list of `{heading, text/points/table}` sections |
| `envelope` | identical for all three types | filtered per type, fields included |
| contract `content` | the full Markdown rendering | a short orientation summary; the contract is `structuredContent` |
| `diagram_list_types` | `diagramTypes: [str]` + `diagramTypeMeanings: {}` | `howToChoose` + `diagramTypes: [{diagramType, meaning, chooseWhen}]` |
| element/relationship fields | silently dropped off-type | refused — `TYPE_SCOPED_ELEMENT_FIELDS`, `SEMANTIC_SCOPED_RELATIONSHIP_FIELDS` |
| `REFUSAL_GUIDE` | 19 codes | 20, `content_lost` added |

**Check against a real response, not against this table.** The transport is one command
(`.devin/skills/graphpilot-mcp`), and a table in a delivery document is exactly the kind
of second source that goes stale — this one included.

The surveyed list, each line confirmed against the file rather than taken on report:

| File | Line | Wrong how |
| --- | --- | --- |
| `01-mcp-tools/01-diagram-tools.md` | 221–229 | The `diagram_list_types` "exact response" is the old `diagramTypes: [str]` shape |
| `01-mcp-tools/01-diagram-tools.md` | 202 | `notation_invalid` omits compartments on a non-block |
| `01-mcp-tools/01-diagram-tools.md` | 27 | Summary row: "types and their meanings" — now `meaning` **and** `chooseWhen` |
| `01-mcp-tools/01-diagram-tools.md` | ~97 | Says `content` is "the Markdown a host reads" and the example is in `structuredContent` only. Both halves moved |
| `01-generation/03-lifecycle.md` | 151 | `notation_invalid` text predates the compartment rule; `content_lost` missing from the code table |
| `01-mcp-tools/README.md` | 52 | Surface row: "what each identifier means" |
| `02-architecture/02-system-design.md` | 252 | *"then `diagram_list_types` **if the type is not obvious**"* — the workflow now makes it unconditional |
| `01-product/02-user-scenarios.md` | 62 | Same "if the right type is not obvious" |
| `01-product/01-overview.md` | 55 | "choose a type with `diagram_list_types`" — no longer optional phrasing |
| `01-product/03-requirements.md` | 98 | "expose supported generation types" — omits the selection guidance |

**`03-design/03-validation.md` is NOT stale** despite being reported as such — it contains
no `notation_invalid` text at all. Worth stating, because the survey that produced this
list invented that file, invented replacement wording for the `diagram_list_types`
example, and missed line 202 entirely. **A delegated documentation survey is a lead, not a
finding.** Open the line before changing it.

### Then split the tool package: one document per tool

Correcting the lines above leaves the real problem, which is that
`01-diagram-tools.md` documents **nine public tools in one 310-line file** and the
attention is not distributed by anything but the order they were written in:

| Tool | Lines it gets | Has an exact response? |
| --- | --- | --- |
| `diagram_create` | 93 | yes |
| `diagram_get_authoring_contract` | 36 | no |
| `diagram_validate` | 42 | yes |
| `diagram_render` | 28 | yes |
| `diagram_list_types` | 24 | yes — the stale one |
| `diagram_workflow` | 15 | no |
| **`diagram_check_draft`** | **13** | **no** |
| `echo` | 4 | no |

`diagram_check_draft` gets thirteen lines. It is the tool a host calls most, it runs a
ten-stage validator, and its `checked`/`notChecked` coverage contract is documented
nowhere. `echo` and the tool that decides whether a diagram is honest are within one
order of magnitude of each other.

**The split:** `README.md` keeps the surface table and the common rules and becomes the
index; each tool gets its own file carrying its purpose, arguments, behaviour, errors, and
**a real captured request/response pair for every outcome it has** — accepted and refused,
not just the happy path. `diagram_check_draft` alone has four distinct responses
(clean-with-`workspaceDir`, clean-without, semantic finding, schema finding) and today
shows none of them.

Two things to get right while doing it:

- **Capture the JSON by calling the server, never by hand.** Every stale example in the
  table above was hand-written and correct on the day. `.devin/skills/graphpilot-mcp` is
  the transport; paste what it returns.
- **Renumber.** The folder is `01-` and `04-` with nothing between, so two files were
  removed and the gap was left. Close it in the same pass.

This *adds* files to a repository whose last program produced 61 documents for 4 commits,
so the distinction matters: these are **permanent reference for a public interface, one
per interface** — the same reason `02-diagram-schemas/` is per-type. The 61 were process
ceremony about work, which is what the document budget exists to stop. A tool the product
exposes and a document describing it is a one-to-one relationship; one file per tool is
the shape that stops a `diagram_check_draft` from hiding behind a `diagram_create`.

### How it runs

**This package runs unattended, overnight.** The operating instruction is therefore explicit:

> **Do not stop.** Work through every item to completion. Do not pause for confirmation, do
> not ask which of two reasonable options to take — choose the better one, record the choice
> and the reason, and keep going. Standing permission to commit after checks pass already
> applies; use it at each coherent slice so an interrupted run leaves a clean history rather
> than one enormous change.

**There are no halting conditions.** They were removed on 2026-08-04 at the user's explicit
instruction: *"i want no halting conditions. we can always git revert so im not worried."*
Every change lands as a commit with its reasoning in the message, so `git log` says why and
`git revert` undoes it cleanly — which covers every source change, every deletion inside
either repository, and every document rewrite.

So: a large finding is deleted and reported, not queued for permission. A broken test is
fixed. A disagreement with this plan is resolved in favour of the better answer, recorded.
Discovering that earlier work in this same program was wrong is treated like any other
finding. **None of these is a reason to stop and ask.**

Two things are outside the run rather than exceptions to it, because `git revert` does not
reach them: `backend/.env` is gitignored and `AGENTS.md` bars editing it, so a configuration
change is written into the report instead; and nothing outside the GraphPilot and
GraphPilot-Test-Repos trees is touched at all.

**The run finished.** All seven slices are clean at **20 passes across 24 commits**, and
the deliverable is [`a5-report.md`](a5-report.md) — what was found, what it cost, what was
wrong that nobody knew was wrong, what is still weak, and the part worth reading, which is
what the audit itself got wrong. Six of its own instruments reported clean because they
were broken, and every recorded finding it acted on was a lead rather than a fact.

### Findings, as they are confirmed

Recorded when found, fixed in the slice that owns them. Several surfaced early, while
other packages were touching the same files.

| | Finding | Slice |
| --- | --- | --- |
| a5.f1 | **Five storage roots are dead.** `context_root`, `evidence_root`, `diagram_requests_root`, `diagnostics_root` and `readiness_diagnostics_root` have **no product caller** — only tests asserting they return a path. All belong to the retired manifest pipeline. `drafts_root` is also product-dead and its name is wanted for the live purpose | **fixed** in slice 1 |
| a5.f2 | **`metadata` is unvalidated.** `additionalProperties: true` with no `required`, so four fields are written that the schema does not name — `authoring`, `intent`, `notation`, `originalType` — and two are named that are never written: `blueprintKey`, `notes`. The canonical schema therefore constrains nothing about a diagram's metadata | **fixed** in slice 1 |
| a5.f3 | **fixed in slice 5.** ~~The active documentation still describes the retired provider pipeline — at scale.** Measured across the 30 documents in `01-product`–`05-delivery`: **20 of them, on 328 lines**, reference JSON 1 / JSON 2, evidence manifests, readiness, `generationContext`, or the six MCP tools removed in `P0`. Six are substantially about it, and they are the ones that define what the product *is* | 5 |
| a5.f5 | ~~14 of 44 registered operation-error codes are never emitted~~ — **the finding was wrong and is corrected below.** Four were dead, not fourteen; ten are emitted by `api/views.py`, which the original survey did not search. Acting on it as written would have deleted ten live codes from a public contract | **fixed** in slice 2 |
| a5.f6 | **`hard_to_read` cannot be seen before the write and cannot be fixed after it.** The warning is measured from the drawn SVG, so `diagram_check_draft` cannot produce it; `diagram_exists` then refuses every overwrite, and no tool deletes. All three hosts in run 4 hit this and each paid differently — one shipped the collisions, one left a superseded diagram behind, one left the tool surface and deleted files from the shell three times. Both halves are documented and their consequence is not | **closed differently.** `diagram_delete` was added here and removed in the edit program: run 5 showed the repair loop it enabled costs more than the wound. A host cleared its collisions by flattening every guard to `yes`/`no` and demoting a decision to a note, spending three of six creates to make the diagram say less. `hard_to_read` is GraphPilot's layout and the host is now told not to act on it |
| a5.f7 | **The `hard_to_read` advice names neither real lever.** It says *"no field moves them apart — fewer elements in one diagram is the lever left."* `shelfmark` shortened two guards, 45 and 24 characters to 6 and 14, changed nothing structural, and the collision cleared. `tickbox` followed the advice, removed a node, and the collision moved to the next pair — its lever was fewer edges converging on one merge node. Written in `legibility.describe`, by me, earlier the same day | **fixed** in slice 2 |
| a5.f8 | **The attempt log undercounts and mislabels.** A `diagram_exists` refusal raises before the attempt is recorded, so run 4 logged 12 against 13 reported — short, in the flattering direction. And a create that warned logs as `accepted: true, findings: []`, so `hard_to_read` runs read as clean. Also undocumented: the workflow says GraphPilot writes the diagram, its SVG and the draft, *"Nothing else in the repository is touched"*, and `attempts.jsonl` makes that false | **fixed** in slice 2 |
| a5.f9 | **A built capability nobody wired up.** `EvidenceService.recheck` — 46 lines that re-hash cited regions and report the ones that moved — is reachable from no surface. It is not scaffolding: `03-design/03-validation.md` lists evidence freshness as a validation concern. *(Its first write here cited `source_changed` as the code it would produce; that was wrong — `source_changed` is the REST optimistic-concurrency code and is live at `views.py:145`. The doc promise stands on its own.)* | **fixed** in slice 2 — exposed on diagram_validate |
| a5.f10 | **Two codes reached a caller unregistered.** `evidence_symbol_not_in_range` — a refusal a host meets whenever a citation names a symbol outside the lines it points at, explained in `REFUSAL_GUIDE` and absent from `_RETRYABILITY`, so nothing said whether retrying helps — and `missing_identity` from the save route. Found by the guard, in the direction `a5.f5` never looked | **fixed** in slice 2 |
| a5.f4 | **The README's integration surface listed five tools that do not exist** — `diagram_request_save`, `diagram_generate_direct`, `diagram_generate_from_context`, `context_evidence_status`, `context_evidence_save` — plus a readiness tool and an "Epic 3 cutover" | **fixed** in `289d8ba` |

**The scale of a5.f3, worst first:**

| Document | Lines about the retired pipeline | Share |
| --- | --- | --- |
| `05-delivery/04-decisions.md` | 33 of 180 | 18.3% |
| `01-product/02-user-scenarios.md` | 45 of 283 | 15.9% |
| `01-product/01-overview.md` | 29 of 238 | 12.2% |
| `02-architecture/01-mcp-tools/04-operation-errors.md` | 37 of 338 | 10.9% |
| `01-product/03-requirements.md` | 51 of 517 | 9.9% |
| `02-architecture/02-system-design.md` | 37 of 404 | 9.2% |
| 14 others | 96 | under 7% each |

`04-decisions.md` is the exception: it is **appended over time and is not design canon**, so a
decision about a pipeline that was later retired is legitimate history and stays. Everything
else in that list claims the present tense about something that was deleted.

**Why it happened.** The rules say docs are part of the change, and `P0` removed the
provider pipeline from the code without removing it from the documentation. `FR-6`, `FR-7`
and `FR-8` are whole requirements for tools that no longer exist; `04-operation-errors.md`
documents error codes nothing can emit. Nothing checks a document against the code, which
is why `a5.8` adds the command reference and this slice adds the sweep.

### It repeats until a pass is clean

`A5` is a loop, not a sweep. Fixing a finding changes the code the audit just read, and the
change can carry its own defect — that is not hypothetical here: the compartment fix
introduced a note-height bug, making `extensionPoints` authorable exposed an unsized
ellipse, and a re-layout helper deleted 407 origins. Each fix earned its own finding.

So: audit an area, fix what it finds, commit, and **audit it again**. Move on only when a
pass over that area produces nothing. Then, once every area is individually clean, one final
pass over the whole repository — because collapsing a duplicated rule in one area can leave
a dangling caller in another.

The loop ends when **a complete pass finds nothing**, not when the list of known findings is
empty. Those are different, and only the first is evidence.

### Audited in slices, in this order

Committed area by area, so an interrupted run leaves complete areas rather than one
half-finished pass over everything.

| | Area |
| --- | --- |
| 1 | `backend/services/` — the product: drafts, materialization, diagrams, shared |
| 2 | `backend/mcp_server/`, `backend/api/`, `backend/operations/` — the surfaces |
| 3 | `backend/tests/` — including tests asserting behaviour that no longer exists |
| 4 | `frontend/src/` — canvas, editor, lib, types |
| 5 | `docs/01-product` – `docs/05-delivery` — every claim checked against the source |
| 6 | commands, configuration, and the command reference |
| 7 | a final pass over all of it |

### Progress — updated as each pass ends

A slice is `clean` only when a pass over it found **nothing**, which is never the pass that
fixed something. On reload, resume at the first slice not marked clean.

| Slice | Area | Passes | State |
| --- | --- | --- | --- |
| 1 | `backend/services/` | **6** | **clean** — 5 commits, 322 lines removed |
| 2 | surfaces | **3** | **clean** — 6 commits; 6 findings closed. `diagram_delete` was added here and later removed — see `a5.f6` |
| 3 | `backend/tests/` | **2** | **clean** — one BOM, and the guard for it |
| 4 | `frontend/src/` | **2** | **clean** — one dead export, catalog parity now guarded |
| 5 | `docs/01`–`05` | **3** | **clean** — 4 documents rewritten, 3 guards added |
| 6 | commands + config | **2** | **clean** — dead setting removed, command reference added and guarded |
| 7 | whole repository | **2** | **clean** — ElementOrigin corrected, 5 stranded imports |

**Pass count is itself a signal.** An area needing four passes was in worse shape than one
needing two, and that belongs in the report even after it is fixed. An area still producing
findings at pass five does not need another audit — it needs rewriting, and that is the
decision to take rather than grinding.

**Exit:** a complete pass finds nothing; docs and code agree; no command exists that nobody
runs; the scaffolding is gone; both suites pass; and the report says plainly what shape the
thing is in.
