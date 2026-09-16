# The Saved Diagram

`graphpilot.diagram.v1` is the only durable store. It holds the semantics, the geometry, a
person's edits, and the record of what was asked for — everything needed to project a
draft, and everything a projection deliberately drops.

The field contract as a whole belongs to
[`../02-diagram-schemas/01-diagram-json-schema.md`](../02-diagram-schemas/01-diagram-json-schema.md).
This page owns what editing requires of it.

## `metadata.requests[]`

Every ask made of this diagram, oldest first, each row stamped by the backend.

```jsonc
"metadata": {
  "authority": "as_implemented",
  "requests": [
    { "at": "2026-08-03T21:42:16Z", "text": "Draw the actors and what each one can do." },
    { "at": "2026-08-05T09:10:44Z", "text": "Leave the billing subsystem out." }
  ]
}
```

| | |
| --- | --- |
| Order | Oldest first. `at` is on every row, so order stays verifiable |
| Cap | Bounded like every other array in this schema; the cap trims from the front |
| `at` | Written by the backend, never by the host — a clock the host controls is a fact nobody can check. Stamped by `assemble_canonical`, from the same clock read as `createdAt` |
| `text` | The host's row, verbatim, and the only part it supplies |

A host submits the flattened list plus one row; the append rule and its validator are in
[`01-draft-document.md`](01-draft-document.md#the-append-rule).

An editor session adds **no row**. A person dragging a node makes no request, and inventing
an entry with no text would make the log claim something nobody said. The log is a record
of asks made of the host, not a history of the file — `git` and the diff already hold the
second.

## `origin.assurance: "user"`

The editor's reverse adapter takes provenance only from the loaded document —
`if (orig?.origin) node.origin = orig.origin` — so an element created on the canvas has
none, while the schema requires `origin` on every node and edge whenever `authority` is
`as_implemented`. Adding a node to a grounded diagram would fail validation with
`'origin' is a required property`, and the same node carrying `assurance: "user"`
validates immediately. So the editor stamps it:

```jsonc
"origin": {
  "assurance": "user",
  "evidenceRefs": [], "assumptionRefs": [], "schemaRules": [],
  "rationale": "Added in the editor by a person. Not established by the cited source."
}
```

Three consequences worth stating.

**Only in a diagram that records provenance.** One with `authority: as_implemented`, or one
whose elements already carry an `origin`. A diagram nobody drafted asks nobody how they
know — `origin` is not required in it, and stamping every element a person draws there
marks the norm rather than the exception.

**It needs a badge.** The canvas marks `assumed` and nothing else. A `user` element sitting
in an `as_implemented` diagram is exactly as misleading as an assumed one — somebody's
addition, rendered identically to cited fact. It gets the same treatment, in the canvas and
in the SVG export, in a calmer blue because it is a different admission. Neither draws it
when *every* element in the diagram carries it: see
[assurance](../01-generation/03-lifecycle.md#assurance).

**It weakens no claim it should not.** `user` is legal under either authority and requires
neither evidence nor an assumption, because a person drawing on a canvas is not making a
claim about the repository at all. What it must never become is a class a host can select.

## `metadata.updatedAt`

Written at create and never touched since: the browser save route stamps
`metadata.authoring` and reconciles `diagramType`, and leaves the timestamp alone. It is
therefore wrong on every diagram a person has saved.

Editing makes that visible rather than merely untidy, so the save path maintains it.

## `metadata.authoring`

Unchanged, and now load-bearing: `generated` means no person has saved this diagram from
the editor, `custom` means one has. It is the cheapest available answer to *"is there human
work in this file?"*, it costs the host nothing, and it is already written on both paths.

What it is used *for* — refusing a write, warning about one, or neither — is a concurrency
question this folder has not answered.

## History — the previous three

A host write that overwrites an existing diagram **moves the current file into history
first**, then writes the new one. The three most recent versions are kept; anything older
is deleted.

```text
.graphpilot/
├── diagrams/
│   ├── payments.gp.json                        the current diagram
│   └── payments.svg
└── history/
    └── payments/
        ├── 20260805T113000Z.gp.json            most recent previous
        ├── 20260804T161200Z.gp.json
        └── 20260801T091500Z.gp.json            oldest kept
```

Timestamped rather than numbered, so trimming is a sort and a delete with no renaming
shuffle. Outside `diagrams/`, so nothing that lists diagrams can pick a version up as one.

| | |
| --- | --- |
| Written by | the host write path only |
| Not written by | `diagram_create` — nothing exists to preserve — or the browser save |
| Cap | 3 versions, oldest deleted |
| Contents | the canonical JSON only; the SVG regenerates from it |
| Cost | about 51 KB per diagram at the average committed size |

**The browser save deliberately writes no history.** The editor has an autosave toggle,
and a person in a long session would churn the three slots and evict the one version worth
keeping — the state immediately before a host touched the file.

### Why this and not a write precondition

An earlier shape required the host to echo a revision token so that a write proved it had
read current state. History replaces it. The risk both address is the same one — whole
desired state submitted by a host that does not know about everything in the file, where
**omission deletes** — and the two answers differ in kind: a token prevents the write, a
version undoes it.

Recovery is enough here, and it is cheaper. The write already
[reports what it removed](01-draft-document.md#removal), so a mistake is visible in the
same breath as the change that caused it, and the previous version is on disk beside it.
Two mechanisms for one risk would be one too many.

If `.graphpilot/` is committed then git already holds every version and this duplicates
it — but gitignoring that folder is explicitly the user's call, so history is the copy
that is always there.

How a person rolls back is not yet specified. Copying the file back by hand works and
costs nothing to support; anything more is a feature rather than a safety net.

## Field classes

The saved diagram is where the three classes are realised. Which field is host-owned,
carried, or derived is specified in
[`03-geometry-and-merge.md`](03-geometry-and-merge.md), not repeated here.

## What comes out

`sourceEnd.qualifiers` and `targetEnd.qualifiers` — 20 declared field paths across the two
ends — are unreachable in three of four directions: no draft field authors them and
neither the canvas nor the SVG export draws them, though the property panel writes them
and they appear in none of the 48 committed diagrams. Removing them is a separate cleanup
from this design, because it is frontend work — the type, the panel section, and the
canonical `$def` go together or not at all.

That audit found 105 of 218 declared canonical field paths absent from every committed
diagram. Most are not dead: `waypoints`, `labelOffset`, the route anchors and the edge
handles are read by both renderers and written by the canvas, and score zero only because
no committed diagram has ever been hand-edited. **Those eleven paths are the product of
this feature**, and they look identical to dead weight in the data. A second class —
`port`, `itemFlows`, `isAbstract`, `description`, `unit`, `quantityKind` and the rest — is
authorable in the property panel and unauthorable in a draft, which is why class 2 exists.
