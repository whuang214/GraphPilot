# A5 — captain's report

**Scope:** every tracked file. 778 of them — 117 Python, 100 TypeScript, 363 Markdown.
Seven areas, **20 passes**, 24 commits. An area was called clean only when a pass over it
found nothing, which is never the pass that fixed something.

**State at the end:** 689 backend tests, 484 frontend, lint and types clean, 243 links,
48 gallery cards with 0 invalid, 0 lost, 0 miscited, and legibility at 0.8% — the best
recorded. Every diagram rebuilds from its draft unchanged.

| Slice | Passes | What it cost |
| --- | ---: | --- |
| `backend/services/` | 6 | 322 lines removed |
| surfaces | 3 | 6 findings closed, one tool added |
| `backend/tests/` | 2 | one BOM |
| `frontend/src/` | 2 | one dead export |
| `docs/01`–`05` | 3 | 4 documents rewritten |
| commands + config | 2 | one dead setting, one new reference |
| whole repository | 2 | one wrong type |

---

## What was wrong that nobody knew was wrong

**A nine-type subtree in `diagram_shapes.py`.** `GenerationContextTrace` was referenced
nowhere at all, and everything beneath it was referenced only by something else inside the
subtree. Each member had a caller. Each looked alive when checked alone. That is how a
retired pipeline's shapes survive an audit, and the only way to see it was to follow the
dead root down rather than act on the census.

**The same shape again, one level lower.** Nine storage methods:
`context_root ← evidence_root ← evidence_manifest_path ← resolve_evidence_path`, and two
more chains beside it, every leaf reached only by a test. `a5.f1` had named five of them;
the other four were the path helpers making them look alive.

**One rule with three spellings.** "Where does the SVG go" was implemented in the render
service, in the storage service, and inline in `api/views.py`. The third mattered: when a
render-on-save fails, the view told the user which file was missing by re-deriving the path
itself. It agreed with the renderer by coincidence — move artifacts into a subdirectory and
that warning names a file nothing was ever going to write, at the one moment a person
depends on the string.

**Two codes reaching callers unregistered.** `evidence_symbol_not_in_range` is a refusal a
host meets whenever a citation names a symbol outside the lines it points at. The contract
explained it; the registry did not list it, so nothing said whether retrying helps.

**The public error contract was wrong by 50 codes.** `04-operation-errors.md` documented 50
that do not exist and omitted 22 that do, with one retryability value contradicting the
code. The cost lands outside this repository: a branch written for `candidate_not_found`
waits forever.

**Three descriptions of an element's provenance, two of them wrong.** The schema said one
thing, the design document claimed a `claimRefs` field retired in `P0`, and the
`ElementOrigin` type declared that same dead field while omitting `assurance` — the field
the entire assurance model rests on.

**A setting nothing reads, offered to every operator in three places.**
`GRAPHPILOT_DEFAULT_WORKSPACE_DIR`. An operator who set it got no error and no effect, while
two documents said it was how you point GraphPilot at a workspace.

**A byte-order mark.** `AGENTS.md` has warned about this since it was written. Nothing
enforced it, and nothing breaks — Python imports a BOM'd module happily. It surfaced when a
script tried to parse the bytes instead of importing them.

---

## The two rules this audit actually produced

Both were learned by getting them wrong, which is why they are worth writing down.

### 1. A recorded finding is a lead, not a fact

Every finding acted on here needed re-measuring, and two would have caused damage taken at
face value.

**`a5.f5` said 14 of 44 error codes were never emitted. Four were.** Ten are emitted by
`api/views.py`, which that survey did not search. Deleting them as written would have
removed ten live codes from a public contract.

**`a5.f1` named five dead storage roots. The chain was nine.**

**`ClaimVersionRef` was kept in slice 1** because `ElementOrigin` referenced it. True, and
the wrong question — the referrer was wrong. **A symbol having a live caller says nothing
about whether the caller is correct**, which is the dead-subtree lesson one level up. The
final pass is what caught it, and that is what a final pass is for.

### 2. An instrument that under-reports is worse than none, because it certifies

Six checks written during this audit reported clean because they were broken:

| The check | What it missed |
| --- | --- |
| unused imports | excluded parenthesized imports by the wrong line, so they matched themselves |
| silent excepts | crashed on a file the audit had deleted, printed a traceback, reported zero |
| liveness census | walked module-level symbols only — a hole exactly the size of the finding it was meant to reproduce |
| catalog parity, v1 | matched one of two declaration syntaxes; reported 39 breaks that were not there |
| catalog parity, v2 | matched any quoted token; passed while a type was renamed out of its declaration |
| error producers | knew two of the three ways a code reaches a caller |

The pattern is the same every time: **the check was written for the case in front of it.**
Hence the working rule that came out of this — **watch a guard fail before trusting it.**
Every one of the eleven added here was.

The cheapest illustration: a file was written with PowerShell `Set-Content -Encoding UTF8`
and picked up a BOM — ten minutes after the guard forbidding exactly that went in, in the
session where the only other one was found. The guard caught it. That is the case for
guards over conventions in a single line.

---

## What is still missing

**An audit removes what is dead and fixes what is broken. It does not build what is
missing.** Three real gaps:

- **Swimlanes.** Nine primitives both renderers can draw are unauthorable. Every cold host
  has named this as its biggest loss.
- **`diagram_update`.** Designed, not built. A saved diagram can be deleted and recreated,
  not edited, from the IDE.
- **`backend/.env.example:40`** still carries `GRAPHPILOT_DEFAULT_WORKSPACE_DIR=`. Those
  files are barred to me by `AGENTS.md`; the line can go.

## What is deliberately judged by a person, and should stay that way

Two things were nearly written up as weaknesses. They are not, and the distinction matters
because chasing either would cost days of harness for a worse answer.

**Whether a diagram is legible.** `hard_to_read` is measured from the drawn SVG because
that is the only place the answer exists — two labels either overlap once placed or they do
not, and predicting it means simulating the layout. The gallery draws all 48 and badges the
ones to look at. **That is the design working**, not a gap in it. `diagram_delete` closes
the repair loop, which is the part that was genuinely broken.

**Whether a diagram is *right*.** No amount of tooling answers this. A diagram can be
valid, legible, fully cited, faithful to its draft, and still describe the system wrongly.
That judgement is a person against `_truth/<repo>.md`, and every badge exists to narrow
what that person has to look at rather than to replace them.

The corpus number sits between the two. Run 4 measured **1.33 attempts per delivered
diagram** and the attempt log now records itself, but the denominator still comes from
hosts reporting honestly. That is worth knowing and not worth building infrastructure to
harden: four runs have shown the *findings* are the yield — the dead citation check, the
`hard_to_read` trap, the wrong advice — and the number is a bonus on top.

## What now exists that did not

Eleven guards, each watched failing before being trusted: the error registry in both
directions, the operation-error document, the schema document, `ElementOrigin` against a
real node, the element-catalog mirror in two directions, source encoding, the command
reference in three, and the artifact-path rule.

They exist because every drift this audit found had the same cause — **a hand-maintained
description of a machine-readable thing, with nothing comparing the two.** The registry and
its document. The schema and its document. The catalog and its mirror. The commands and
their fragments. Each was correct on the day it was written.
