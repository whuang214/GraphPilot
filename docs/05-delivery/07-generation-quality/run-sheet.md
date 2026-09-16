# Corpus runs

**Scaffolding.** This dies with the Generation Quality program. It records what each run
measured, so two runs can be compared.

**The procedure and the nine frozen prompts live in
[`04-reviewing-diagrams.md`](../../04-development/04-reviewing-diagrams.md)**, which outlives
this program because the gallery does. The `corpus-run` skill automates the commands and
points at that document rather than restating it.

They were in the skill alone until run 3, and the skill directory is **not in version
control** — so the one artifact that makes two runs comparable existed in a single untracked
file. The prompts were recoverable only because every committed draft records its own in
`request.original`.

This file is the results table and nothing else: a procedure recorded twice is a procedure
that drifts.

## Results

| Run | Date | Prompt | Diagrams | `diagram_create` calls | Attempts each | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-08-03 | **specified** — type, name and subject given | 9 of 9 accepted | 18 | 2.0 | Self-reported in prose; the draft log did not exist. Type selection never exercised. Drafts were not stored, so these nine cannot be regenerated |
| 2 | 2026-08-04 | **vague** — the host chooses type and scope | see below | — | **void** | **The contract changed underneath it.** Findings valid, number is not |
| 3 | 2026-08-04 | vague, unchanged | 9 of 9 accepted, **0 refusals** | 9 (self-reported) | **void** | **The draft log never wired**, so nothing was counted. And the number would have been meaningless anyway — see below |
| **4** | 2026-08-04 | vague, unchanged | 9 of 9 | **12 logged** | **1.33** | **The first measured run.** 12 calls for 9 delivered diagrams; every call was accepted, so no draft was ever refused on its merits. Two hosts spent the extra three on legibility they could not fix in place |
| 3c | 2026-08-04 | reworded wrapper, same nine subjects | 9 of 9 accepted | from the hosts' reports | — | Run after a large round of tool and contract work. The log was empty again; **it is now deleted** and the reports are the source |
| **5** | 2026-08-05 | vague; one line changed, see below | 9 of 9 | **13**, corroborated | **1.44** — and **1.00** of authoring | **The first run against the reduced draft envelope.** Zero drafts refused on their merits: all four calls above nine were `hard_to_read` retries, so the contract itself cost nothing. kitepay 6, shelfmark 4, tickbox 3. All three chose the right type unprompted; all nine are `as_implemented` with every element grounded and no assumptions authored |

Run 5 is the first whose count is **corroborated** rather than self-reported — each host's
number matched its repository's `attempts.jsonl` exactly. Run 4's 12 is known to have
undercounted (`a5.f8`), so 1.44 against 1.33 compares an honest number to a flattering one.

**The four extra calls are the finding, and they were ours.** A host cleared its label
collisions by flattening every guard to `yes`/`no` and demoting a real decision to a note
— three of its six creates spent making the diagram say less to fix how it looked. Both
the advice and `diagram_delete` were removed afterwards; `hard_to_read` is now reported to
the user and never handed to the host as work.

**One prompt line changed**, recorded here because comparability depends on it: the brief
said the three requests were *"what belongs in `request.original`"*, a field the envelope
cut removed. It now reads *"each is one diagram's ask, to be carried verbatim"* —
field-agnostic, so it cannot go stale the next time the schema moves. The nine subjects
are untouched.

**Three contract defects it caught**, all introduced by the envelope cut and all fixed:
the contract told hosts to record things in `uncertainties` (a field that no longer
exists — reported independently by **all three**), the `bdd_diagram` warning leaked into
every type's `diagramType` note, and the 30–35 KB contract payload truncated in two of
three hosts' clients.

**Isolation was imperfect.** Two hosts reported that GraphPilot's own `AGENTS.md` and
`.devin/rules/` were auto-injected into their context. Both say they authored only from
the tools, and their tool sequences support that, but a future run should suppress it.

### Run 2 was contaminated, and the cause is worth keeping

Three hosts authored between 15:12:31 and 15:13:40. Two commits landed inside that window —
`327c63f`, which rewrote the authoring contract, and `a4469af`, which rewrote the workflow.
The server is spawned per call, so some drafts were authored against the old contract and
some against the new.

**Its call count measures nothing.** Its *findings* stand: the hosts hit real gaps and
reported them, and a gap found under either version of the contract is still a gap.

The lesson is now a rule in the `corpus-run` skill: **freeze the contract for the duration
of a run.** It is obvious in hindsight and was not obvious while working in parallel on
what looked like an unrelated package.

Run 1's figure is **also not comparable** — counted by hand from prose, against a prompt
that named the type, the name and the subject.

### Run 3 has no number either, for two independent reasons

**The log never wired.** `GRAPHPILOT_DRAFT_LOG` was set in the parent shell and then at user
level; neither reached the subagents, because a Windows process inherits its environment
from its parent as that parent was created, and the CLI had started long before. Nine
diagrams, nothing counted. The fix is in
[`04-reviewing-diagrams.md`](../../04-development/04-reviewing-diagrams.md): set it in
`backend/.env`, which every spawned server loads, and **verify the file exists after the
first create** rather than discovering afterwards.

**And the figure would have been meaningless.** All three hosts hit
`NameError: EvidenceService` on every `diagram_check_draft` call carrying `workspaceDir` —
the citation check the workflow is most emphatic about was dead code. Each of them wrote
its **own** citation checker and verified 57, 58 and 51 citations by hand-rolled script.
Zero refusals and zero miscited diagrams are that effort, not the product's. A number
measuring "what happens when the host does GraphPilot's job for it" compares to nothing.

**What run 3 did produce is worth more than the number would have been:** a blocking defect
in the one tool package `F` spent the most words on, found because three independent hosts
hit it and said so precisely. Fixed in `16b217b`, with the test that should have existed —
608 tests had missed it because not one of them called the tool.

Three runs, three unusable measurements, and each failure was in the **apparatus**, never in
the product: self-reporting, then a contract change mid-run, then an unwired log.

### Run 4 — what 1.33 actually measures

**12 calls, 9 diagrams delivered, zero drafts refused on their merits.** Against run 1's
self-counted 2.00 — and that run's prompt named the diagram type, the name *and* the
subject, so this is a better figure on a harder exam.

**Per accepted create it is 1.00, and that number is a lie.** Every call succeeded, so the
naive ratio says authoring is free. Two hosts nonetheless made twelve calls for nine
diagrams: `shelfmark` re-authored under a second name and `tickbox` created the same
diagram three times, deleting its own output from the shell in between. The denominator has
to be **diagrams delivered**, not creates accepted, or a host that discards its work looks
more efficient than one that gets it right first time.

**And 12 is itself short by one.** `tickbox` hit `diagram_exists` and that refusal was never
logged, because it raises before the attempt is recorded. Reported 13, logged 12 — the
error is in the flattering direction, which is the worst direction for a measurement.

### All three hosts hit the same wall, and it is the run's real finding

`hard_to_read` arrives **only** after the write, and `diagram_exists` means a saved diagram
is **never** overwritten. So the one defect class that escapes `diagram_check_draft` is the
one class that cannot be repaired. Each half is documented; the consequence of the pair is
documented nowhere, and every host paid a different price:

| Host | What it did |
| --- | --- |
| `kitepay` | Shipped 2 collisions out of 138 labels rather than litter a second name |
| `shelfmark` | Re-authored under a near-identical name, leaving the flawed diagram behind |
| `tickbox` | Left the tool surface entirely, deleted files from the shell, three times |

**The advice in the warning was disproved twice.** It reads *"no field moves them apart —
fewer elements in one diagram is the lever left."* `shelfmark` shortened two guards from 45
and 24 characters to 6 and 14, changed nothing structural — same 18 nodes, same 20 edges —
and the collision cleared. `tickbox` followed the advice literally, removed a node, and
watched the collision move to the next adjacent pair; its real lever was fewer edges
converging on one merge node. Both levers exist and the message names neither.

### Type selection, unprompted, for the fourth run running

Nine diagrams: three `bdd_diagram`, three `use_case_diagram`, three `activity_diagram`.
Every host chose against `chooseWhen` and every host chose correctly, and two quoted the
same near-verbatim match back. Whatever else is unfinished, the type-selection guidance is
doing its job.

**A run is good when it needs fewer calls than the one before it, against the same prompt.**
Refusals are the signal — each is a place the contract failed to tell a competent host
something it needed.

## What each run must record

| | Where from |
| --- | --- |
| attempts per accepted diagram | **the hosts' reports** — the brief asks each for its `diagram_create` count |
| which rule caused each refusal | the hosts' reports, with its code and path |
| whether the contract warned them of that rule first | the hosts' reports, and the most valuable line in them |
| diagrams produced, and of what type | the gallery, or the drafts on disk |
| correctness | **by eye**, in the gallery, against `_truth/<repo>.md` |

**All of it is self-reported now.** The attempt log was deleted after four runs in which it
produced a usable measurement zero times; the reports were doing the work anyway, and they
carry something it never could — whether a rule was discoverable before it fired.

The weakness is real and worth stating: an agent counting its own retries can be wrong and
has no incentive to be right. Weigh the findings above the figure.

Findings go into [`plan.md`](plan.md), not here.
