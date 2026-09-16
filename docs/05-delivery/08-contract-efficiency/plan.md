# Contract Efficiency

`diagram_get_authoring_contract` returns **43,701 characters**. This program removes what a
host cannot act on, without removing anything it needs.

**File cap: 1.** This file. Audits produce rows here, never audit documents.

## What the measurement found

| | chars | share |
| --- | --- | --- |
| `content` (Markdown) | 17,425 | 39.9% |
| `structuredContent` | 25,857 | 59.2% |
| — `envelope` | 12,594 | 48.7% of structured |
| — `example` | 6,017 | 23.3% |
| — `refusals` | 3,045 | 11.8% |
| — `guidance` | 2,171 | 8.4% |
| — `vocabulary` | 1,315 | 5.1% |
| — everything else | 715 | 2.8% |

Two facts drive the whole program:

1. **`envelope` is byte-identical for all three diagram types.** There is no per-type
   filtering. An `activity_diagram` contract ships 2,199 characters (18% of its envelope)
   the host cannot use — including a section whose own purpose text reads *"A block's
   compartments. **BDD only.**"*
2. **Everything except `example` is sent twice** — once as Markdown in `content`, once as
   JSON in `structuredContent`. `example` is in the machine channel only, which is the
   inverse of what the evidence says matters.

## The defect underneath the trim

`stereotype` is gated per type — a non-BDD draft carrying one is refused
`stereotype_unsupported`. **`features` and `extensionPoints` are not.** A host can author
compartments on an activity node, pass validation, have them persisted, and never see them
drawn: only a `classifier-box` primitive renders compartments.

That is the `g6` class — *"a field can be valid, persisted, and undrawable"* — and it is
why the envelope trim is a correctness fix before it is a size fix. Documenting a field for
a type that silently discards it is worse than not documenting it.

All 48 stored drafts were scanned: **zero off-type usage** of `features`,
`extensionPoints` or `stereotype`. Gating them breaks nothing.

## Packages

States: `planned`, `implementing`, `verifying`, `complete`, `blocked`, `reverted`.

| # | Package | Tier | State |
| --- | --- | --- | --- |
| C1 | Gate the type-scoped element fields, then filter the envelope per type | 2 | **complete** |
| C2 | Close the three derivation gaps | 1 | **complete** |
| C3 | The channel decision — **blocked on Gate 0** | 2 | blocked |
| C4 | Small deletions and the top-level field gap | 2 | **complete** |
| C5 | Are all 19 refusals reachable for all three types? | 1 | **declined** |

**`C5` is declined, and the reason is worth keeping.** The idea was that the 19-row
refusal table is identical for all three types and probably should not be. Checking
reachability mechanically, **two of three first guesses were wrong**:
`containment_unsupported` and `cyclic_parent` are *more* reachable in `bdd_diagram`, not
less — a type with no container refuses **every** `parentId`. Only `guard_required` is
confidently unreachable outside activity: one row of nineteen, weighed against a host
meeting a refusal no contract explains, which is precisely the defect `A4` closed. The
error rate on the analysis is the argument against doing it.

### Gate 0 — asked properly, and answered a better way

The original question was *what does a real IDE MCP client put in the model's context?*
Two investigations went looking:

- **Client archaeology: inconclusive.** The bundled `@modelcontextprotocol` SDKs — the
  TypeScript copy under Cursor, the Python copy here — only validate `structuredContent`
  against `outputSchema`, and ours declares none, so nothing is validated and the full
  `CallToolResult` is handed to the application layer. **Every client's message-building
  code is minified**, and no evidence was found either way. Recorded as undetermined
  rather than guessed.
- **The experiment settled it instead.** A cold agent was given the Markdown channel and
  nothing else, and asked to author a draft. That reproduces the worst case exactly,
  whatever clients do.

**Result: the Markdown channel alone was not sufficient.** It got roughly 90% of the way
and then invented two values on the critical path — `kind`, whose literal value appeared
in no channel a host reads, and the shape of `lineRange`, cross-referenced by `locator`
and defined nowhere. Both fail closed as `draft_invalid`, which suppresses every other
finding, so the single refusal it would have received could not say which guess was wrong.

Both are now fixed, so the question is no longer load-bearing for correctness — only for
size. `C3` remains open on the dedupe alone.

### C1 — one gate, then the filter

`TYPE_SCOPED_ELEMENT_FIELDS` in `draft_contract.py` names each element field, the diagram
type that owns it, and the code that refuses it elsewhere. The validator loops over that
table; the contract filters on the same table. One source, both sides — which is the rule
the contract service already states in its own docstring.

`stereotype` keeps its existing code and message. `features` and `extensionPoints` refuse
under `notation_invalid` rather than gaining two new codes: this program exists to shrink
the contract, and every new code is a row in all three of them. The path
(`$.elements[3].features`) and message name the field precisely, which is what a host acts
on.

Envelope sections then filter per type:

- **universal** — `request`, `scope`, `evidence`, `locator`, `element`, `relationship`,
  `uncertainty`, `assumption`, `decision`
- **owned by `features`** — `features`, `property`, `operation`, `constraint`
- **`multiplicity`** — derived, not listed: included when any allowed relationship has an
  optional end, or when `features` is included. `activity_diagram` has neither, so it
  drops.

Element field rows filter on the same table, so an activity contract stops documenting
`stereotype` and `extensionPoints`.

### C2 — close the derivation gaps

Three surfaces are hand-written where everything around them is derived:

| | Now | After |
| --- | --- | --- |
| `meaning` | **two** independent dicts — `DIAGRAM_TYPE_MEANINGS` and `_DIAGRAM_TYPE_MEANING` — with different wording | one, single-sourced |
| `direction` | hand-written `_DIRECTION`, guarded by nothing | a test fails if a relationship gains an `END_POLICY` entry without one |
| `guidance` | four BDD rules restate what `vocabulary` derives from `END_POLICY` | the four go; the judgement half stays |

`direction` is the sharpest of the three. Rank the contract by cost of error and it is
first — a `composition` authored backwards validates cleanly and asserts the opposite
ownership. Rank by machine backing and it is last: unverifiable by construction, typed by
hand twice, guarded nowhere.

### C4 — small deletions, one gap closed

- **`notation`** — returns `"sysml"`. No draft field accepts it; the backend stamps it
  itself. Deleted.
- **`diagramType`** → **`contractFor`**. The value is the argument the host just passed.
  At the top level beside `schemaVersion` and `kind` it reads as a draft field, a host
  copied it, and the fix was a permanent apology paragraph in every response. Renaming
  removes the confusion and the paragraph while keeping the correlation.
- **`required` → `topLevelFields`**, now listing the optional top-level arrays too.
  `uncertainties`, `assumptions` and `decisions` are currently named **only inside
  `example`** — the one part of the contract absent from the Markdown channel. A host
  reading `content` alone cannot learn that `assumptions` is a top-level array, while
  `orphan_assumption` refuses a draft that fails to reference one.

## Verification — the trim must be provably lossless

One test, run in both directions, per type:

> Every field the validator **accepts** for a type appears in that type's contract, and
> every field the contract documents for a type is one the validator accepts.

That is the whole safety argument. It is the same shape as
`test_every_refusal_code_is_explained_before_a_host_trips_it`, which already reads codes
out of the services rather than from a list beside them.

Plus: all 48 stored drafts still validate, and `manage.py test --parallel 24` passes.

## Not in scope

**Shrinking `envelope` itself.** It is 48.7% of the payload, it is derived from the schema
the validator enforces, and removing it makes authoring impossible for two of three types
— that is `f5`, the worst single finding of the corpus. The trimmable mass is the
unguarded hand-written surfaces and the duplication, not the load-bearing derived tables.

## Where it stands — one decision left

Both channels, against the start of this program:

| Type | Before | Now | Markdown alone |
| --- | --- | --- | --- |
| `bdd_diagram` | 43,282 | 51,862 | 26,042 |
| `activity_diagram` | 43,067 | 46,652 | 23,641 |
| `use_case_diagram` | 41,948 | 46,769 | 23,141 |
| **all three** | **128,297** | **145,283** (+13%) | **72,824 (-43%)** |

**Up 13% is the expected midpoint, not a regression.** The worked example now ships in
both channels, which is what makes the Markdown self-sufficient — and what makes
`structuredContent` 100% redundant. Every byte of it is now carried by `content`.

So the program's entire payoff sits behind `C3`: drop `structuredContent` and the three
contracts fall 43% below where they started. Keep it and they are 13% above.

That is a product call, not a technical one, which is why it is not being taken here.

## Outstanding — the MCP docs describe the old surface

This program changed the tool contracts after `D`, the documentation rewrite in
[`07-generation-quality`](../07-generation-quality/plan.md), had already closed. Every
JSON response example under `docs/02-architecture/01-mcp-tools/` should be assumed wrong
until checked against a live call.

It is **deliberately not fixed here**. `a5.7` is a full documentation-versus-code sweep
that has to open these files anyway, and doing it twice — once now, once there — is how a
document ends up with two half-corrections. The changes are enumerated in that slice so
the sweep is not a rediscovery.

The one exception, taken now because it is not a docs question: `AGENTS.md` gained a
source-of-truth row for `04-reviewing-diagrams.md`, which was reachable only from
`docs/README.md`. An agent following the documented read order got the review command and
never the document that explains it.

## Open finding — nothing can repair a created diagram

`diagram_create` refuses to overwrite, and the planned update tool does not exist. So a
diagram that is *accepted* and *wrong* is terminal: the only route is a second name, which
leaves the good version not holding the natural one.

This is not theoretical. In the A/B below, the host that reached a legibility warning
chose to ship the bad diagram:

> *"I deliberately did **not** re-create under a second name to fix this: `diagram_create`
> will not overwrite, so the fix would leave two diagrams with the good one not holding
> the natural name."*

That is the correct decision under the current surface, which is the problem. Note the
asymmetry it creates with the refusal path now that the cost lie is gone: **a refused
draft costs nothing and an accepted one cannot be revised**, so all of the risk sits on
the far side of a call the tools no longer warn about. Whatever replaces this — an
`overwrite` flag, a real update tool, or a delete — is a Tier 2 contract change and
belongs to its own package.

## Open findings — the tool-by-tool audit

Walking all nine tools turned up three things that are not defects today and will be if
left. None is fixed here; each is recorded so it is a decision rather than a discovery.

**The channel split is inherited, not chosen.** Three conventions exist on one surface,
and which one a tool gets is decided entirely by its return annotation: `-> str`
duplicates the payload into `{"result": ...}`; a bare `-> dict` is serialised to text with
**no** structured channel at all; only `-> CallToolResult` is a choice. So
`diagram_validate` and `diagram_render` hand a host structured results as prose, while
`diagram_check_draft` — their sibling — populates both. `diagram_workflow` was fixed
(`5f0ce33`); `echo` is the last duplicator and costs 16 characters, which is precisely why
it should go: one leftover instance is what makes the next reader unable to tell which
convention was intended. The coherent version is every tool returning `CallToolResult`
explicitly.

**`diagram_check_draft` under-reports its own coverage.** `checked` is a hardcoded
five-item literal in `server.py` while `validate()` runs ten stages. Missing: the size
bound, the secret scan, identity, and **authority** — and `evidence_required` is one of
the most common refusals a host meets, so a host asking "did it check my citations were
required?" cannot tell. The error direction is safe, but the entire value of
`checked`/`notChecked` is being an honest coverage statement, and it is a second source
maintained by hand: add a stage to the validator and nothing here updates. Same defect
shape as the duplicated type meanings this program removed.

**The prose and the data disagree about the staging.** `_WORKFLOW` explains three honest
bands — shape, meaning, evidence — which is the right abstraction for a host and matches
the validator. `checked` names five stages of nine. The document undersells nothing; the
structured channel does.

## Open finding — qualified symbols are unchecked, by design

A single-host audit probed `evidence_symbol_not_in_range` with negative controls and found
that only the last dotted segment of a `symbol` is matched. In a file with two `to_dict`
methods, citing `DraftFinding.to_dict` against `DraftValidationResult.to_dict`'s lines
passes; so does `ThisClassDoesNotExist.to_dict`.

**This is deliberate and documented**, not a defect — `evidence_service.py` states that a
qualifier is *"the author's way of saying where, not a string in the file"*, and that the
check is conservative because *"a false refusal here teaches a host to stop giving symbols
at all."*

It is recorded anyway, because the audit is right that the gap is larger than the prose
implies: `g10` was closed on the claim that a citation naming one thing and pointing at
another is caught, and for a qualified name it is not. Two options, neither taken here:

- **Cheap half** — refuse when the qualifier is identifier-shaped and appears *nowhere in
  the file*. Catches an invented qualifier; cannot catch a real one pointed at the wrong
  class.
- **Full fix** — resolve which class owns the cited lines. Language-specific, and well
  outside a contract-efficiency program.

Changing it alters refusal behaviour against the module's own stated trade-off, so it is a
decision for whoever owns evidence, not a slice of this program.

## Outcome

`C1`, `C2` and `C4` shipped. **-5.8% across the three contracts**, and the honest split
matters more than the total:

| Type | Before | After | |
| --- | --- | --- | --- |
| `bdd_diagram` | 43,282 | 43,766 | **+1.1%** |
| `activity_diagram` | 43,067 | 37,648 | **-12.6%** |
| `use_case_diagram` | 41,948 | 39,344 | **-6.2%** |
| all three | 128,297 | 120,758 | -5.9% |

**BDD grew, and that is the right trade.** It authors every section, so it had nothing to
shed, and it absorbed the four optional top-level arrays plus the `lineRange` section the
contract had been promising and never defining. Paying 484 characters to stop a host
guessing the shape of every citation it writes is not a cost worth avoiding.

The saving is entirely the two types that were being sent another type's vocabulary.

**The 40% is still on the table and still gated.** Duplication between `content` and
`structuredContent` is untouched, because which channel to keep depends on Gate 0 and
nothing in the repository can answer it.

### What the cold-host experiment found — all fixed

Four defects, none of which any existing test caught. Two were pre-existing, two were
introduced by this program's own first commit:

| | Defect | Origin |
| --- | --- | --- |
| **`lineRange`** | `locator` said *"object — see `lineRange`"* and no such section existed. The shape was undefined in the Markdown channel, and it is needed by every citation | pre-existing — the `f6` dangling-pointer class, reopened |
| **`kind`** | Its literal value `diagramDraft` appeared in no channel a host reads. The prose said *"the two constants above"*, pointing at nothing | value pre-existing; the false referent was **mine** |
| **`evidence`** | Reported `Required: no` while `evidence_required` refuses an `as_implemented` draft that cites nothing | **mine** — the column was schema-accurate and misleading |
| **`features` on a `note`** | The new gate checked `diagramType` and not `semanticType`, so a note in a BDD diagram could carry compartments, validate, persist, and draw nothing | **mine** — the same `g6` hole one level down, in the fix for `g6` |

A regression test now covers each. The strongest of them is generic: **every
`object — see X` cross-reference must resolve to a section in the same channel.** That is
what would have caught `lineRange` before a host ever met it.

Found while implementing, both recorded rather than fixed:

- **`features` and `extensionPoints` were never validator-gated** — only `stereotype` was.
  A host could author compartments on an activity node, pass validation, have them
  persisted, and never see them drawn. Now refused. This was the `g6` class, still live
  after `G` closed.
- **`C5`** — the refusal table is identical for all three types and some codes are
  unreachable per type.

Verification: `cd backend; uv run python manage.py test --parallel 24` — **612 → 621**,
`OK (skipped=1)`. Baseline re-measured at `HEAD` by stashing the change, because an
earlier reading of 600 did not reconcile; 612 is the true figure. The contract was also
called over the real stdio transport for all three types.

**The experiment is the reusable part.** Handing a cold agent one channel and asking it to
author beats reasoning about what clients render: it found four defects in an afternoon,
two of them introduced by the commit it was auditing, and it needs no provider call and no
corpus reset. Worth repeating whenever the contract changes shape.
