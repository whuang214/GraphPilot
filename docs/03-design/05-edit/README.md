# Editing an Existing Diagram

> **Status: built.** `diagram_read` → edit the file → `diagram_update`, with the merge,
> the R1–R5 geometry and history. Live status is on the
> [board](../../05-delivery/01-current-state.md); what is still open is at the bottom of
> this page.

## The problem

A diagram is created from a [draft](../01-generation/01-draft.md), then opened in the
editor. A person moves blocks, renames one, adds a note. Later they return to the IDE:

> Also add the caching layer.

The host cannot re-author its draft and re-create. `diagram_create` refuses to overwrite,
and even if it did not, re-materializing recomputes every position — which the person
experiences as their work being destroyed.

There used to be a second, sharper version of the same problem: a host that created a
*wrong* diagram could not repair it. All three hosts in corpus run 4 hit that wall and
each paid differently — one shipped the collisions, one left a superseded diagram behind,
one left the tool surface and deleted files from the shell three times.

**All three of those were `hard_to_read`, and that is no longer the host's problem to
solve.** GraphPilot places every node and every end label, so a collision is a limit of
its layout rather than a mistake in the draft — the host reports it and the person moves a
label in the editor. A tool was briefly added to let hosts delete and retry; run 5 showed
what that costs, with one host flattening every guard to `yes`/`no` and demoting a
decision to a note to clear a warning, so both the tool and the loop are gone.

What remains is the case a rebuild cannot serve: a diagram somebody has **arranged**,
where starting over destroys their work. That is the problem below, and it is worth being
honest that no host has hit it yet — the corpus creates diagrams and never returns to one.

## Two writers, one file

The editor is not a box-mover. A person can add nodes, delete them, retype an edge and
rename a label, so **the saved diagram has two authors of semantics**, not one author of
semantics and one of geometry.

That single fact decides the design. Any second copy of the semantics — a durable draft
on disk, a draft embedded in the diagram's metadata, a layout sidecar — goes stale the
moment a person deletes a node, and nothing detects it. The only consistent options are to
derive the semantic view from the saved file on demand, to partition the file so both
writers share one copy, or to take semantic editing away from the person.

**GraphPilot derives it.** The saved `.gp.json` is the only durable store, and the draft
is computed from it when a host asks and thrown away afterwards.

```text
create   host authors draft ──► materialize ──► <name>.gp.json ◄──► browser editor
                                                      │
edit     read ◄───────────────────────────────────────┘
           └─► .graphpilot/drafts/<name>.draft.json   (projected: no geometry)
                          │
                    host edits the file
                          │
         write ───────────┴──► materialize + merge ──► <name>.gp.json
                                                  └──► history/<name>/<stamp>.gp.json
```

## Every field is one of three kinds

This is the whole mechanism. Each field in the saved diagram belongs to exactly one class,
and each class has one rule.

| | Class | Rule |
| --- | --- | --- |
| **1** | **Host-owned** — appears in the draft | The draft is the truth; overwrite it |
| **2** | **Carried** — absent from the draft | If the id existed, copy the saved value. If it is new, compute one |
| **3** | **Derived** — absent from the draft | Recompute on every write, always |

The draft does not need to express everything the diagram holds, because anything it
cannot express is handled by rule 2 or 3 — and neither of those needs the draft.

A person's dragged position and a person's typed `description` are both class 2. They are
preserved by the same mechanism, for the same reason: the host did not write them and must
not lose them.

The exact membership of each class is in
[`03-geometry-and-merge.md`](03-geometry-and-merge.md).

## Create and edit submit the same document, through different tools

The host sends one `graphpilot.draft.v1` document either way. Internally there is one
write path: on a create nothing existed, so every element takes the "compute it" branch of
rule 2. Create is the edit where the file was empty.

The **surface** keeps them apart. Creating refuses when the name is taken; updating
refuses when it is free. A host that did not know a diagram was already there finds out
immediately and for free — which matters because it submits a *whole* element list, so a
write it did not know was an overwrite would omit everything already in the file, and
omission deletes.

One tool inferring the intent would make that mistake recoverable
([history](02-diagram-document.md#history--the-previous-three) holds the previous version
and the result names what it removed) rather than impossible. Two tools make the host say
what it means, and cost one refused call when it guesses wrong.

## Read order

1. [`01-draft-document.md`](01-draft-document.md) — the draft, in both directions
2. [`02-diagram-document.md`](02-diagram-document.md) — what the saved diagram gains
3. [`03-geometry-and-merge.md`](03-geometry-and-merge.md) — the three field classes and the layout rules

## Ownership

| Topic | Owner |
| --- | --- |
| The edit round trip, the three field classes, geometry | **this folder** |
| The draft contract as a whole, per-type authoring guidance | [`../01-generation/01-draft.md`](../01-generation/01-draft.md) |
| Draft → canonical mapping, notation rules | [`../01-generation/02-materialization.md`](../01-generation/02-materialization.md) |
| Assurance classes, evidence freshness, provenance | [`../01-generation/03-lifecycle.md`](../01-generation/03-lifecycle.md) |
| Canonical diagram field contract | [`../02-diagram-schemas/`](../02-diagram-schemas/README.md) |
| Exact MCP arguments, results, errors | [`../../02-architecture/01-mcp-tools/`](../../02-architecture/01-mcp-tools/README.md) |

The draft and canonical changes this design requires are specified here and belong to the
owners above once built. When they ship, those documents absorb them and these two pages
shrink to the edit-specific rules.

## Boundaries

- An edit is **semantic**. The host never submits, hints at, or requests geometry.
- Layout quality is the editor's job. When the complaint is *"these lines are messy"*, the
  answer is the canvas — the host is the one participant that cannot see the picture.
- No patch language, and no natural-language edit interpreted in the backend.
- Nothing persists unvalidated; `DiagramPersistenceService` stays the single funnel.
- The browser save path may share persistence and reconciliation, and keeps its HTTP
  contract.
- `.graphpilot/drafts/<name>.draft.json` is the **edit working file**: written by the read,
  read by the write, deleted on success. `diagram_create` no longer writes a trace there.

## Settled since

| | |
| --- | --- |
| **The two tools** | `diagram_read` and `diagram_update`, alongside an unchanged `diagram_create` |
| **A stale basis refuses** | The host reads again and re-applies. Mirrors the browser's `expectedRevision` 409 rather than inventing a second concurrency model, and refuses rather than merging, because a whole-state write from a stale read deletes what it never saw |
| **Rollback needs no tool** | History is files in `.graphpilot/history/<name>/`; restoring one is copying it back. A third tool for a case nobody has hit is the argument that removed `diagram_delete` |
| **New codes** | `basis_stale`, `diagram_crossed`. `requests_invalid`, `diagram_not_found` and `evidence_unreadable` are reused |

## Still open

| | Question |
| --- | --- |
| Two hosts, one diagram | They would share the working file and clobber each other. Deferred, not solved — this is a local, single-user product, and giving the read a unique filename is a one-line change if it ever matters |
| Nobody has needed this yet | The corpus creates diagrams and never returns to one, so the journey this serves is still unevidenced. A corpus run with an edit leg is the next real test |
