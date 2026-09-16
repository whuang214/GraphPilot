# The Draft, in Both Directions

`graphpilot.draft.v1` is the only document a host ever writes, and the only one it ever
reads back. There is no separate edit document and no version fork: the same schema serves
create and edit, and the same schema is what a projection emits.

The contract as a whole belongs to
[`../01-generation/01-draft.md`](../01-generation/01-draft.md). This page owns what
editing requires of it.

## The envelope

| Field | Required | Rule |
| --- | --- | --- |
| `schemaVersion` | ● | const `graphpilot.draft.v1` |
| `kind` | ● | const `diagramDraft` |
| `diagramName` | ● | slug, ≤64 characters; names the file |
| `diagramType` | ● | `activity_diagram`, `use_case_diagram`, `bdd_diagram` |
| `authority` | ● | `as_implemented` or `conceptual` |
| `requests` | ● | every ask made of this diagram, oldest first. See below |
| `evidence[]` | conditional | required when `as_implemented`, refused when `conceptual` |
| `elements[]` | ● | 1–256 |
| `relationships[]` | ● | 0–512 |
| `assumptions[]` | conditional | required when any item is `assumed` |

`diagramType` and `authority` sit at the top level because they are facts about the
diagram, not about the ask.

The envelope above is the current one, not a proposal. What it dropped on the way here,
and why, is recorded by its owner:
[`../01-generation/01-draft.md`](../01-generation/01-draft.md).

## A crossed diagram cannot be edited from the IDE

`diagramType` is fixed when a diagram is created, and the draft's enum is
`activity_diagram | use_case_diagram | bdd_diagram`. The canonical schema has a fourth
value, `custom`, and the draft has no way to say it.

That is the lock, and it is already how the system behaves. Every browser save runs
`conforms_to_type`: if any element falls outside the declared type's vocabulary, the
diagram flips to `custom` and stays there. A host then has no way to write a draft for it
at all.

| A person does this | Result |
| --- | --- |
| Adds a note, drags boxes, renames, retypes within the vocabulary | stays its type; the host can still edit |
| Brings in an element from another diagram type | flips to `custom`; **the IDE can no longer edit it** |

Notes and comment links are in all three vocabularies, so annotating a diagram never
crosses it. The vocabularies are otherwise tight — a BDD diagram permits two node types —
so crossing one is a deliberate act on a canvas that offers everything, not an accident.

The refusal has to say so plainly: *"this diagram was mixed with elements from another
diagram type in the editor, so it can no longer be edited from here. Edit it in the
browser."* Falling through to a schema error would leave a host guessing at a rule nothing
told it about.

The flip is one-way. A `custom` diagram does not return to its type when the foreign
element is deleted, because the escape hatch is deliberate and a board that has been mixed
once is not reliably a use-case diagram again.

## `requests` — the ask, kept

An append-only list of every ask made of this diagram, **oldest first**, as plain strings.

```jsonc
"requests": [
  "Draw the actors and what each one can do.",
  "Leave the billing subsystem out.",
  "Add the reminder digest use case."
]
```

The saved diagram keeps the same list with a timestamp and author per row
([`02-diagram-document.md`](02-diagram-document.md)); the projection flattens it back to
text, so a host copies exactly what it was given.

### The append rule

A host submits the list it received with **one row added at the end**, and the validator
checks it:

```text
submitted[:n] == saved   and   len(submitted) == n + 1
```

On a create `n` is zero, so the rule reads "exactly one row".

Nothing else is accepted. A host cannot reword row 2, cannot drop row 1, and cannot add
two rows at once. Rejecting a tampered list rather than quietly ignoring it matters:
accepting a field and discarding it is the failure mode `faithfulness.py` exists to
catch, and a silently-ignored history is worse than no history.

The refusal must name the offending row and say to copy it verbatim. The risk this rule
carries is that a language model asked to echo an array back will reword it, and a host
that cannot see *which* row it changed has hit a wall it cannot diagnose.

### Why it is in the draft at all

Two jobs, and both need it in the document rather than beside it.

The host needs to **read** it, because it is now the only place the reasoning survives. A
host that cannot see *"leave the billing subsystem out"* from three edits ago will
helpfully add billing back in.

The host needs to **write** to it, because the reason for an edit is worth exactly as much
as the reason for the original diagram, and it is unrecoverable from anything else. What
happened can be derived by diffing two versions; what was *asked* cannot.

`requests[]` text is scanned by the secret screen in `draft_safety.py`. A verbatim user
prompt is the most likely place in the whole document for a pasted credential to appear,
and draft prose reaches a file people commit.

## Assurance, with `user`

| Class | Requires | Legal when `authority` is | Who may author it |
| --- | --- | --- | --- |
| `grounded` | ≥1 `evidenceRefs` | `as_implemented` | host |
| `assumed` | an `assumptionRef` | `as_implemented` | host |
| `conceptual` | nothing | `conceptual` | host |
| `user` | nothing | either | **the editor only** |

`user` means *a person drew this*. It exists so that an element created on the canvas has
somewhere to live in a draft — without it, a projection of any hand-edited diagram is
impossible, and the element simply cannot be expressed.

**A host may not author it.** If it could, `user` would be a way out of the entire honesty
model: mark every element `user`, cite nothing, and `as_implemented` stops meaning
anything. So:

> A draft may carry `assurance: "user"` on an element **only if a diagram of that name
> already exists and already carries that id as `user`.** On create it is refused
> outright — nothing has been drawn yet.

The edit path holds the saved file already, so the check costs nothing.

### Editing an element does not change its assurance

A person renames a `grounded` element in the editor. Its citation now backs a label nobody
re-checked, and the element stays `grounded`.

The alternative — degrade anything a person touches to `user` — sounds more honest and is
worse. A few sessions of ordinary editing would bleach a fully evidenced diagram to
unevidenced, and the citations would still be sitting there, correct, describing code that
did not move. Assurance follows **identity**, not content.

`user` is not a fourth degree of confidence. It is what an element says when **nobody ever
made a claim about it** — drawn from nothing, citing nothing. A grounded element somebody
renamed is still grounded; what changed is the label, and the diagram records who has
worked on it through `metadata.authoring`, not by rewriting provenance.

## The draft is a file on disk, not a payload

The read writes the projected draft to `.graphpilot/drafts/<diagramName>.draft.json` and
returns **the path plus a summary** — counts, the request log, any stale-evidence warning.
The host edits that file. The write reads it back.

```text
read    overwrite .graphpilot/drafts/<name>.draft.json from the current diagram
        return the path, not the document
host    edit the file with its own editing tools
write   read it, validate, merge, save — then delete it
```

### Why not inline

`diagram_create` takes its draft inline and never a path, because a host authoring from
scratch has no file to read. An edit does, and the difference matters.

Returned inline, a host adding one element has to **re-emit all the others**, and a model
asked to echo a large document back will occasionally drop or reword part of it. A dropped
element is a deletion. Editing a file touches one line and leaves the rest byte-identical,
which is the thing these hosts are actually good at.

It is also cheaper: a summary and a path instead of several kilobytes of JSON in the host's
context on every read.

This is the one part of the design that is testable rather than arguable. If hosts rewrite
the file wholesale instead of editing it, the benefit evaporates — though nothing is worse
than the inline version, so the fallback is free.

### Lifecycle

| | |
| --- | --- |
| Written by | the read, every time, always overwriting whatever was there |
| Read by | the write, and nothing else |
| Deleted by | a successful write |
| Kept after | a refused write, so the host can fix it and call again |
| Present means | an edit is in flight |

`diagram_create` **writes no draft trace.** It used to, as a debugging record of what the
host claimed, and that record is now reconstructible: the projection reproduces every
class-1 field from the diagram, and the ask itself is in `metadata.requests`. Keeping it
would also give one path two meanings — a leftover trace predates any browser edits, so a
host that edited it instead of calling the read would submit a document that deletes
whatever a person added since.

Two hosts editing one diagram name at the same time would share the file and clobber each
other. That is **deferred, not solved**: this is a local, single-user product, and because
the write already takes a path, giving the read a unique filename later is a one-line
change rather than a redesign.

### `basis` — the read stamps what it was based on

```jsonc
"basis": { "diagram": "sha256:…", "readAt": "2026-08-05T12:00:00Z" }
```

Written by the read, compared by the write, **never authored or echoed by the host** — it
rides along in a file the host is editing rather than being a token it has to carry. A
mismatch means someone saved in the browser between the read and the write, and the write
refuses with *"read it again"* rather than deleting what they added.

Absent on a create, which is based on nothing, so the field is optional.

## The projection — saved diagram to draft

Class-1 fields only, and nothing else. No inference, no matching by label, no guessing.

```text
for each node:  id, semanticType, label, stereotype, features, extensionPoints,
                parentId, assurance, evidenceRefs, assumptionRef
for each edge:  id, semanticType, source, target, label, guard, condition,
                extensionLocations, source/target role, multiplicity, navigability,
                assurance, evidenceRefs, assumptionRef
document:       diagramName, diagramType, authority, requests (flattened to text),
                evidence (minus digests), assumptions
```

Everything else — every position, size, style, route, handle, `rationale`, `schemaRules`,
viewport, and the whole of `metadata` beyond `authority` and `requests` — is not emitted,
because it is class 2 or class 3 and comes back by rule on the next write.

An edge's `label` **is** emitted, including a `«include»` or `«extend»` keyword a host
authored. An earlier version of this page claimed canonical assembly dropped those; it
does not — the label is carried at the edge's top level, and a probe that looked for it
under `data` found nothing and drew the wrong conclusion. Not emitting it would silently
delete a label on the first edit.

### One field is deliberately empty

A projection returns `requests` as the saved history and **nothing appended**. The
document is therefore a valid draft *minus exactly one row*, and that row is the thing the
host is about to do. It cannot write without saying why it is writing.

## Worked example

A saved diagram, after a person dragged a node, bent an edge, typed a description and drew
a note.

**Projected:**

```jsonc
{
  "schemaVersion": "graphpilot.draft.v1",
  "kind": "diagramDraft",
  "diagramName": "org-chart",
  "diagramType": "bdd_diagram",
  "authority": "conceptual",
  "requests": [
    "A manager is a kind of employee."
  ],
  "elements": [
    { "id": "employee", "semanticType": "block", "label": "Employee",                 "assurance": "conceptual" },
    { "id": "manager",  "semanticType": "block", "label": "Manager",                  "assurance": "conceptual" },
    { "id": "note-1",   "semanticType": "note",  "label": "Reviewed by HR, Aug 2026", "assurance": "user" }
  ],
  "relationships": [
    { "id": "rel-1", "semanticType": "generalization",
      "source": "manager", "target": "employee", "assurance": "conceptual" },
    { "id": "note-1-employee", "semanticType": "commentLink",
      "source": "note-1", "target": "employee", "assurance": "user" }
  ]
}
```

The host sees the note and the comment link, because they are semantics. It does not see
the drag, the bent edge, or the description — and cannot lose them, because they are
copied back by id.

**Submitted**, with one element added and one row appended:

```jsonc
  "requests": [
    "A manager is a kind of employee.",
    "Add a VP above director."
  ],
  "elements": [ …the three above…,
    { "id": "vp", "semanticType": "block", "label": "VP Engineering", "assurance": "conceptual" }
  ],
```

`submitted[:1] == saved` and `len == 2`, so the append is accepted and the backend stamps
the new row.

## Removal

Whole desired state means an id absent from `elements[]` is deleted. Nothing is exempt,
including an element a person drew: *"delete that note I added"* is an ordinary thing to
ask the IDE, and a rule protecting `user` elements would make it impossible.

So the protection is visibility rather than refusal. **Every write reports what it
removed**, naming person-drawn elements as such:

```jsonc
"removed": [
  { "id": "note-1", "label": "Check with Priya about refunds", "drawnBy": "user" },
  { "id": "legacy-gateway", "label": "Legacy gateway" }
]
```

A deliberate deletion reads as confirmation; an accidental one is visible in the same
breath as the change that caused it, rather than discovered a week later. The host is
expected to pass it on.

This is the reason a write must supply `expectedRevision`
([`README.md`](README.md#still-open)): whole state submitted by a host that never read the
current file omits everything it does not know about, and omission deletes.
