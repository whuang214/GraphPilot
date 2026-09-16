# Reviewing diagrams

The test suite proves the pipeline behaves. It cannot tell you a diagram is **wrong** — a
diagram can be valid, legible, fully cited and still describe the system incorrectly. That
judgement needs a person looking at pictures, and this document owns how.

Three things live here, and they answer different questions:

| | Question | Needs | Gives you |
| --- | --- | --- | --- |
| **The review gallery** | Does the code still draw these 48 diagrams correctly? | one command | badges and pictures |
| **A single-host audit** | Can a host still get through the tools after I changed them? | one agent, minutes | findings |
| **A corpus run** | Has authoring got *easier*, measurably? | three cold agents | a comparable number |

The last two cannot be commands. A diagram is authored by a host reading source and
deciding what it means, so exercising that means **actually running agents** — there is no
way to fake it that measures anything.

The middle one is the cheap one, and it is the one most often skipped. A corpus run costs
three agent sessions and is void if the contract shifts underneath it; an audit costs one
and can be run after every change.

---

## The review gallery

```powershell
cd backend
uv run python manage.py review_gallery --regen eval
```

Serves one page at `http://127.0.0.1:8123/` and opens it. **Always give that URL to whoever
asked**, per [the working conventions](../../AGENTS.md): an agent reporting
a number about a picture is not the same as a person seeing it.

| Flag | What it does |
| --- | --- |
| *(none)* | Serves the page already on disk. Fast; says nothing about current code |
| `--regen eval` | Rebuilds every answer and training example **from its stored draft**, through the real pipeline |
| `--regen generated` | Re-syncs the nine host diagrams out of the corpus repositories |
| `--regen edited` | Replays every edit scenario and rewrites both halves of its before/after pair |
| `--regen all` | Both |
| `--no-open` | Serve without launching a browser |
| `--port` | Serve somewhere other than 8123 |

`render_example_gallery` does the same build without serving, which is what the tests use.

**`--regen eval` is the one that matters after a rendering or layout change.** It
re-materializes from drafts rather than re-rendering saved output, so a card proves the
pipeline still produces that diagram *today*. Without it you are looking at a file that
parses, which is a much weaker claim.

### What a card tells you

51 cards across four pools — 36 `answers`, 9 `generated`, 3 `training`, 3 `edited` — each
carrying its own badges, because a page total cannot tell you which diagram to open.

**`edited` is the one pool whose card is a pair.** Two diagrams side by side, the same one
before and after a host changed it, and a line under them saying how many nodes held their
position, what was added, and what was removed — including any text a person had typed on
a removed element, which no draft shows and nothing else would surface. Neither picture
answers the question on its own; what is being reviewed is what did *not* move.

The card also carries the **ask** that produced the edit, and three source buttons:
`Scenario`, `Before JSON` and `After JSON`. The pictures show that a node moved; only the
documents show that a `description` nobody mentioned came through untouched.

Six scenarios, two per diagram type, chosen so that every kind of edit is covered rather
than the two easy ones:

| Scenario | Operation |
| --- | --- |
| `checkout-refunds` | add an element, rename another |
| `onboarding-trimmed` | remove an element, and report the prose that went with it |
| `portal-export` | add a child — containment outranks proximity |
| `catalogue-ends` | change a role and a multiplicity, with nothing added or removed |
| `refund-rewired` | rewire an edge: its bend is dropped, an untouched edge keeps its own |
| `kiosk-note` | an unrelated edit, with something a person drew surviving it |

Add and remove are the obvious two and the least likely to break anything. The operations
that quietly destroy work are the ones that change something already there — which is
where the projection's dropped relationship ends hid.

### Finding the cards you want

The header filters. Click a pool or a diagram type to show only it; the chips combine, so
`training` + `bdd` is one card. Choosing nothing in a group means all of it, the name box
matches on the card's name, pool and type, and **show all** clears everything. Empty
headings disappear with their cards, so a filtered page never shows `answers · 36` above
an empty strip.

These were jump links until they were filters, and a jump still leaves thirty-six answers
between a reviewer and what they came for — which is how a newly added pool went unnoticed
by the person who had asked for it. Legibility and vocabulary coverage sit in a folded
panel above the cards for the same reason: reference, not the main event.

| Badge | Meaning |
| --- | --- |
| `valid` / `N invalid` | Canonical schema and semantic validation |
| `structural ok` / `N structural` | Non-blocking structural warnings |
| `legible` / `N unreadable` | Strings clipped, buried under a foreign element, or overlapping, measured from the drawn SVG |
| `Nn · Ne` | Node and edge counts |
| `materialized` | This run rebuilt it from its draft — evidence about current code |
| `stored` | Read off disk; predates stored drafts and cannot be rebuilt |
| `miscited` | A citation does not resolve, or names a symbol absent from the lines it points at |

**Goal** on the card face is the draft's own statement of what the diagram set out to show.
**Draft** and **Diagram JSON** open the documents behind it. There is deliberately no
prompt view: `request.original` is not an input to anything — a diagram is materialized
from elements, relationships and evidence — so showing it implied a prompt-to-diagram stage
that does not exist. It is still recorded in every draft, one click away.

---

## A corpus run

Three cold agents read three real applications and diagram them through the MCP server. It
measures one thing: **how hard the contract makes it to describe a real system truthfully**,
as `diagram_create` calls per accepted diagram.

The former Devin environment supplied local `corpus-run` and `graphpilot-mcp` helpers.
Those helpers and their `.devin/` folder are excluded from this repository.
**This document owns the frozen prompts**, which retain their original harness commands
as a historical record. Fresh clones should connect their MCP host to
`uv run python mcp_server/server.py` from `backend/`; the legacy helper commands below
require that separate old environment. Record a harness adaptation before comparing a
new corpus run with those historical results.

### Two rules, and both have been broken

> **1. Do not change the prompt.** Not a word.

A run against different wording cannot be compared to the run before it, and comparison is
the entire reason the corpus exists. If wording genuinely must change, record it in the
results table and treat every earlier run as a different measurement. It changed once,
before run 3, and [what changed is recorded below](#what-changed-before-run-3-and-why-it-was-allowed).

> **2. Freeze the contract for the whole run.**

No commits to the authoring contract, the workflow text, the draft schema, or the MCP tool
descriptions until every host has finished. The server is spawned per call, so a commit
lands instantly and hosts still working read the new contract while their earlier drafts
were authored against the old one. **Run 2 was lost exactly this way** — two commits landed
inside a 70-second authoring window while the parent agent worked on an apparently
unrelated package.

### The three repositories

| Repo | What it is |
| --- | --- |
| `kitepay` | Django, peer-to-peer payments, server-rendered |
| `shelfmark` | Django, a lending library |
| `tickbox` | FastAPI + React, shared task boards |

Ground truth is in `_truth/<repo>.md`. **A host must never see it** — it is the reviewer's
answer key, used after the run.

### The nine frozen prompts

Three per repository, always the same three subjects. A fixed denominator is what makes two
runs comparable: if one run makes five diagrams and the next makes six, "calls per diagram"
compares different work.

**The subject is frozen; the diagram type deliberately is not**, so `diagram_list_types` and
step 1 of the workflow are still exercised. Run 1 named the type, the name *and* the
subject, which tested nothing about scoping.

| # | Prompt, verbatim | Type a competent host should pick |
| --- | --- | --- |
| 1 | `The structure of what this system stores, and how those things relate.` | `bdd_diagram` |
| 2 | `Who uses this system, and what they use it for.` | `use_case_diagram` |
| 3 · kitepay | `What happens when one person sends another a payment.` | `activity_diagram` |
| 3 · shelfmark | `What happens when a librarian issues a copy to a member.` | `activity_diagram` |
| 3 · tickbox | `What happens when someone moves a card to another column.` | `activity_diagram` |

The expected type is **never told to the host**. A run that picks differently is a finding
about the contract, not a failure. Runs 1–3 each produced three of each type unprompted,
from three agents that could not see one another.

### Before launching: reset, and wire the log

```powershell
# Derived, not hardcoded: the test repositories sit beside this one.
# Override GRAPHPILOT_CORPUS if yours live elsewhere.
$corpus = if ($env:GRAPHPILOT_CORPUS) { $env:GRAPHPILOT_CORPUS }
          else { Join-Path (Split-Path -Parent (git rev-parse --show-toplevel)) "GraphPilot-Test-Repos" }
foreach ($r in "kitepay","shelfmark","tickbox") {
  git -C "$corpus\$r" clean -fdx .graphpilot
  New-Item -ItemType Directory -Path "$corpus\$r\.graphpilot" -Force | Out-Null
}
```

**The `mkdir` is not tidiness.** `diagram_create` records every attempt to
`<workspaceDir>/.graphpilot/attempts.jsonl`, and it never creates that folder — a user
whose first draft is refused must not find one they did not ask for. So after a bare
`clean`, every refusal before a host's *first success* goes unrecorded and the run reports
fewer attempts than it made. Silently, and in the flattering direction.

This **deletes the previous run's diagrams and drafts**. They are committed, so
`git -C <repo> checkout .graphpilot` brings them back — confirm with the user first unless a
corpus run is already agreed.

### Where the refusal data comes from

**The hosts, and only the hosts.** There is no log to configure.

There used to be: a `GRAPHPILOT_DRAFT_LOG` setting appending one line per
`diagram_create`. Across four runs it produced a usable measurement **zero** times — the
variable reached the wrong process twice and held an empty value once — and every one of
those was a lost run. It is deleted rather than repaired, because the reports were doing
the work anyway and carry more than it did.

A count of attempts says a rule fired. A host says **whether the contract had warned it of
that rule in advance**, which is the finding worth having. That is why the brief below asks
for it explicitly, per refusal.

So the numbers in the results table are self-reported. That is a real weakness and worth
stating plainly: an agent counting its own retries can be wrong, and has no incentive to
be. It is nonetheless what produced every usable figure so far.

### Launching the hosts

Three subagents in **parallel**, in the background, with no sight of each other. Cold means
cold: an agent that has seen the repository, the ground truth, or a previous run's diagrams
is not a cold host and its result means nothing.

Each gets exactly this, substituting only the path and the third request:

> You are an IDE coding agent. A developer who has just joined this project has asked you
> for three diagrams while finding their way around it.
>
> THE THREE REQUESTS — this is all they said, and each is one diagram's ask, to be
> carried verbatim:
>
> >     "The structure of what this system stores, and how those things relate."
> >     "Who uses this system, and what they use it for."
> >     "<the repository's third request from the table above>"
>
> You choose the diagram type for each. Nobody is telling you which.
>
> CODEBASE: `<absolute path>` — this is also `workspaceDir`.
> Read it as closely as you like. **Do not read any file outside that directory** — in
> particular do not look in the parent folder.
>
> HOW TO CALL GRAPHPILOT. Native MCP is disabled; this script is the transport:
> ```
> $py   = "<graphpilot repo>\.venv\Scripts\python.exe"
> $call = "<graphpilot repo>\.devin\skills\graphpilot-mcp\call.py"
> & $py $call list
> & $py $call call <toolName> <argsJsonPath>
> ```
> Write argument files into a private directory of your own — parallel hosts sharing
> `$env:TEMP` have overwritten each other's drafts. PowerShell `>` writes UTF-16; use
> `cmd /c "... > file"` when you redirect, and read back with UTF-8.
>
> START HERE: call `diagram_workflow` with `{}` and follow it.
>
> ONE RESTRICTION, and it is the point of the exercise. Everything about *how to author*
> must come from the GraphPilot tools themselves. Do not open, read, grep or search
> anything under the GraphPilot repository — not `backend/assets/**`, not
> `authoring_contract_service.py`, not `draft_validation_service.py`, not the schemas, the
> docs or the tests. That is the implementation of the contract you are being handed, and a
> real user's agent would not have it. The two paths above are for running the transport,
> not for reading. If you catch yourself wanting to check how the backend validates
> something, that is the exact moment this run is measuring — call a tool instead.
>
> Say which tool you are calling, before each call.
>
> REPORT BACK
> - which diagram type you chose for each request, and why
> - **how many times you called `diagram_create`, in total and per diagram.** Count every
>   call, including the ones that were refused. This is the run's only measurement and
>   nothing records it but you, so state the number even when it is nine.
> - the tool calls you made, in order
> - every refusal: its exact code, path and message, and what you had misunderstood
> - for each refusal, the important one: **had the contract told you that rule in advance,
>   or did you only learn it by being refused?**
> - anything unclear, missing, contradictory, or that wasted your attention
> - the `diagramPath` and `svgPath` for each diagram
>
> Do not modify GraphPilot, and do not edit the codebase's own source — writing the
> diagrams under `<workspaceDir>/.graphpilot/` is the output you were asked for. Do not
> flatter the tools: a rule you had no way to predict is the most useful thing you can
> report.

### What changed before run 5, and why it was allowed

The brief told the host its three requests were "what belongs in `request.original`". That
field was removed when the draft envelope was cut, so the sentence instructed a host to
fill something that no longer exists.

It now reads "each is one diagram's ask, to be carried verbatim" — **field-agnostic on
purpose**. The brief naming a schema field is what made it go stale; the contract already
names the field, and a brief that repeats it has to be reissued every time the schema
moves. The nine subjects are untouched, so the denominator is unchanged and run 5 remains
comparable to run 4.

### What changed before run 3, and why it was allowed

Rule 1 above says do not change the prompt. This is the recorded exception, taken because
**there was nothing left to compare against**: run 1 named the type, the name and the
subject, so it measured different work, and run 2 was void from a mid-run contract commit.
Changing the wording now costs a comparison that does not exist; changing it after run 3
would cost a real one. Runs 1 and 2 are a different measurement and stay that way.

The corpus prompt had drifted behind the single-host prompt on four counts:

- **No anti-cheat restriction.** This is the serious one. The transport block hands every
  host an absolute path to the GraphPilot repository, and the only limit was on reading
  outside the *codebase* — so nothing stopped a host opening
  `authoring_contract_service.py` and learning the contract from its implementation. A run
  where that happened would report an easy authoring experience and mean nothing. It is
  not known whether any host did.
- **It announced the tool.** "asked to diagram a codebase using the GraphPilot MCP server"
  primes a host to treat the tools as the subject. A developer asks for a diagram.
- **"Produce exactly three diagrams"** is a batch instruction, and the three subjects
  arrived as a numbered list rather than as things a person said — so `request.original`
  had no verbatim sentence to carry.
- **It forbade modifying the codebase**, which contradicts the workflow: `diagram_create`
  writes under `<workspaceDir>/.graphpilot/`, and the workflow explicitly calls this out as
  the exception. A careful host obeying the prompt would have refused to finish.

The three subjects themselves are **unchanged, word for word**. They are the frozen
denominator; only the wrapper around them moved.

### Pulling the results in

```powershell
cd backend
uv run python manage.py review_gallery --regen generated
```

This copies each `.graphpilot/drafts/<name>.draft.json` into
`assets/blueprints/<type>/examples/generated/`, **regenerates** the diagram from it rather
than copying the host's, and drops anything the corpus no longer has. Regenerating is the
point: a diagram that survives only because it was saved is not evidence that the pipeline
still produces it.

Every generated card should read `materialized`. One reading `stored` means no draft was
stored — that host never got a successful `diagram_create`.

### Recording it

| Number | Where from |
| --- | --- |
| attempts per accepted diagram | draft log: total lines ÷ accepted lines |
| which rule caused each refusal | draft log: group by `findings` |
| diagrams produced, and of what type | draft log: `diagram`, `type` |
| which host wrote a line | draft log: **`workspace`** |
| correctness | **by eye**, in the gallery, against `_truth/<repo>.md` |

**The log is one file for all three hosts, and that is fine — group by `workspace`.** All
three hosts in run 3 reported the shared file as a defect and warned that a line count
over-counts; every one of them had missed the `workspace` field already in each record.
Say so in the brief rather than splitting the file: one log is what makes "total ÷
accepted" a single division.

Only `diagram_create` is logged. `diagram_check_draft` is free and unlimited by design, so
counting it would inflate the one number the corpus exists to produce — how much the hosts
leaned on it comes from their own reports.

The row goes in [`run-sheet.md`](../05-delivery/07-generation-quality/run-sheet.md); the
findings go in that program's `plan.md`.

**A good run is not "nine diagrams appeared".** It is one that needed fewer calls than the
run before it, against the same prompt. Refusals are the signal: each is a place the
contract failed to say something a competent host needed.

---

## A single-host audit

One agent, one diagram, against the tools as they are right now. Use it after changing the
authoring contract, the workflow text, or the draft schema, when you want to know whether a
host can still get through — **without spending a corpus run**.

It is deliberately not a measurement. The prompt is not frozen, so it produces no number
that compares to anything; what it produces is **findings**, and it produces them in
minutes rather than three agent sessions. Four of these caught nine defects during the
contract-efficiency program, two of them introduced by the commit being audited.

Run a corpus run when you need the number. Run this when you need to know if you broke
something.

### The prompt

Substitute the request, the codebase and the diagram name. Everything else is fixed —
particularly `START HERE` and the restriction, which are what make the result mean
anything.

> You are an IDE coding agent. A developer has asked you for a diagram.
>
> THE REQUEST — this is all they said, and it is what belongs in `requests`:
>
> >     "<one sentence, exactly as a developer would type it>"
>
> CODEBASE: `<absolute path>`
>
> HOW TO CALL GRAPHPILOT. Native MCP is disabled; this script is the transport:
> ```
> $py   = "<graphpilot repo>\.venv\Scripts\python.exe"
> $call = "<graphpilot repo>\.devin\skills\graphpilot-mcp\call.py"
> & $py $call list
> & $py $call call <toolName> <argsJsonPath>
> ```
> Write argument files into a private directory of your own. PowerShell `>` writes UTF-16 —
> use `cmd /c "... > file"` when you redirect, and read back with UTF-8.
>
> START HERE: call `diagram_workflow` with `{}` and follow it.
>
> Name the diagram `<name>`. `workspaceDir` is the codebase path above.
>
> ONE RESTRICTION, and it is the point of the exercise. Everything about *how to author*
> must come from the GraphPilot tools themselves. Do not read `backend/assets/**`,
> `authoring_contract_service.py`, or `draft_validation_service.py`: that is the
> implementation of the contract you are being handed, and a real user's agent would not
> have it. Read the file you are diagramming as closely as you like.
>
> Say which tool you are calling, before each call.
>
> REPORT BACK
> - the tool calls you made, in order
> - every refusal: its exact code, path and message, and what you had misunderstood
> - for each refusal, the important one: **had the contract told you that rule in advance,
>   or did you only learn it by being refused?**
> - anything unclear, missing, contradictory, or that wasted your attention
> - the `diagramPath` and `svgPath` you ended up with
>
> Do not modify GraphPilot. Do not flatter the tools — a rule you had no way to predict is
> the most useful thing you can report.

### Why each part is there

- **A one-sentence request.** Earlier audits used a forty-line brief, and hosts reported
  having to truncate it to fit the ask, which the contract says is verbatim. A real request
  fits the field a real request goes in.
- **The transport must serve the worktree being audited.** `call.py` resolves the backend
  from its own location, so a copy of the skill inside a feature worktree launches that
  worktree's server. It used to hardcode one absolute path, which meant an audit run on a
  branch quietly exercised `master` and cleared a contract nobody had changed.
- **`START HERE: diagram_workflow`.** Handing the contract over as a file skips
  `diagram_workflow` and `diagram_list_types` entirely — including type selection, which is
  where two whole runs were once lost to reading `bdd` as behaviour-driven development.
- **The restriction names paths, not a file count.** "Read exactly these two files" also
  bans the MCP tools, which is the opposite of what is being tested. Only the contract's
  *implementation* is off-limits; the codebase under study is not.
- **Tool narration.** Without it the report gives outcomes and not the path taken, and the
  path is where the friction is.

### Reading the result

The single most useful line in any report is the answer to *"did the contract tell you that
rule in advance?"* A refusal a host could not predict is the `A4` defect class — a rule
enforced and explained nowhere — and it is worth more than a clean run.

A host that reports no friction at all has usually skipped something; check its tool
sequence against what it claims to have read.

### Afterwards

The diagram lands in `<workspaceDir>/.graphpilot/`, which is gitignored in this repository,
so nothing needs cleaning up. Give the name a fresh value each time — `diagram_create`
refuses to overwrite, so reusing one spends a call on a `diagram_exists` refusal that
teaches nothing.

---

## Related

- [Testing strategy](02-testing-strategy.md) — what the automated suite proves
- [Run sheet](../05-delivery/07-generation-quality/run-sheet.md) — results, run by run
- [The draft contract](../03-design/01-generation/01-draft.md) — what a host is being asked to author
