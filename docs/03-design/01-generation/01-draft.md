# The Diagram Draft

## Purpose

One document describing one diagram: what the user asked for, which elements and
relationships should appear, and what in the repository supports each of them.

```text
graphpilot.draft.v1 / diagramDraft
```

The draft is a **submission format, not a stored artifact**. `diagram_create` consumes it
and writes a canonical diagram that carries its own evidence. There is no draft file to
fall out of sync with the diagram, and no second knowledge base to maintain.

The host authors semantics. It never authors canonical topology, relationship-end objects,
positions, styles, or markers — see [`02-materialization.md`](02-materialization.md) for
what GraphPilot derives.

## Complete example

```json
{
  "schemaVersion": "graphpilot.draft.v1",
  "kind": "diagramDraft",
  "diagramName": "todo-structure",

  "diagramType": "bdd_diagram",
  "authority": "as_implemented",

  "requests": [
    "Make a BDD diagram of the Todo API. It should reflect the code as implemented today."
  ],

  "evidence": [
    {
      "id": "ev-todo-service",
      "kind": "code",
      "locator": {
        "path": "src/todo_api/services/todo_service.py",
        "symbol": "TodoService",
        "lineRange": { "start": 25, "end": 100 }
      },
      "summary": "TodoService checks permissions and domain rules, then persists and publishes."
    },
    {
      "id": "ev-build-application",
      "kind": "code",
      "locator": {
        "path": "src/todo_api/main.py",
        "symbol": "build_application",
        "lineRange": { "start": 32, "end": 55 }
      },
      "summary": "build_application wires in-memory repositories, a system clock, and the services."
    }
  ],

  "elements": [
    {
      "id": "todo-service",
      "semanticType": "block",
      "label": "TodoService",
      "features": {
        "properties": [
          { "kind": "reference", "name": "todos", "type": "TodoRepository", "multiplicity": { "lower": 1, "upper": 1 } }
        ],
        "constraints": [
          { "name": "titleLength", "expression": "1 <= len(title) <= 120" }
        ]
      },
      "assurance": "grounded",
      "evidenceRefs": ["ev-todo-service"]
    },
    {
      "id": "todo-application",
      "semanticType": "block",
      "label": "TodoApiApplication",
      "assurance": "grounded",
      "evidenceRefs": ["ev-build-application"]
    }
  ],

  "relationships": [
    {
      "id": "todo-service-part-of-application",
      "semanticType": "composition",
      "source": "todo-service",
      "target": "todo-application",
      "sourceRole": "todoService",
      "sourceMultiplicity": { "lower": 1, "upper": 1 },
      "assurance": "grounded",
      "evidenceRefs": ["ev-build-application"]
    }
  ],


  "assumptions": [],

}
```

## Section map

| Section | Question it answers | Required |
| --- | --- | :-: |
| envelope | Which contract, what is the output stem, of what type, claiming what authority? | yes |
| `requests` | What was asked for, verbatim? | yes, exactly one on a create |
| `evidence` | What in the repository was read, exactly where? | when `as_implemented` |
| `elements` | What should appear as a node? | yes |
| `relationships` | What connects to what, and how? | yes |
| `assurance` | How is each element known — cited, assumed, or drawn by a person? | on every element |
| `assumptions` | What unsupported proposition was accepted, by whom? | when something is `assumed` |

## 1. Envelope

| Field | Rule |
| --- | --- |
| `schemaVersion` | Constant `graphpilot.draft.v1` |
| `kind` | Constant `diagramDraft` |
| `diagramName` | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, ≤64 chars. Names `.graphpilot/diagrams/<diagramName>.gp.json` and its siblings |

There is no `draftId`. The draft is never submitted by reference and never read back, so it
needs no identity of its own — `diagramName` already names everything it produces, the
accepted copy at `.graphpilot/drafts/<diagramName>.draft.json` included. That copy is a
trace for debugging a diagram that turns out to be wrong, not an artifact with a life of
its own; the diagram is still the durable thing.

## 2. `requests`

Every ask made of this diagram, verbatim and oldest first. **A create carries exactly
one**; more or fewer is `requests_invalid`.

Unlike everything else a host reasons about, this is **kept**: it lands in
`metadata.requests` on the saved diagram, stamped with the time it arrived. It is the only
durable answer to *why does this diagram look like this*, for a reader who never saw the
conversation that produced it.

The host writes the text and never the time. Adding an entry is what editing an existing
diagram does — earlier entries come back unchanged or the write is refused, which is what
makes the list a record rather than a field.

`bdd_diagram` is a **SysML Block Definition Diagram** — structure. It is not
behaviour-driven development; use `activity_diagram` for behaviour.

## 3. `evidence`

Required when `authority` is `as_implemented`; forbidden when `conceptual`.

| Field | Rule |
| --- | --- |
| `id` | `^ev-[a-z0-9]+(?:-[a-z0-9]+)*$` |
| `kind` | `code`, `test`, `documentation`, or `configuration` |
| `locator.path` | Workspace-relative POSIX path to a readable file |
| `locator.symbol` | Optional. The class, function, or heading the region names |
| `locator.lineRange` | `{ "start": n, "end": m }`, 1-based inclusive, `end` within the file |
| `summary` | What those exact lines establish. One or two sentences |

`contentDigest` is **backend-derived** — GraphPilot hashes the cited region on save. A
draft that authors it is rejected. Freshness is per cited region, not repository-wide:
[`03-lifecycle.md`](03-lifecycle.md).

**Every record must be cited.** `metadata.evidence` in the saved diagram means *the regions
this diagram was built from*, so an evidence record no element or relationship references
is refused rather than persisted. The same holds for an assumption nobody names. An empty
file cannot back a claim.

## 4. `elements`

| Field | Rule |
| --- | --- |
| `id` | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, unique. **Becomes the canonical node ID unchanged** |
| `semanticType` | From the diagram type's vocabulary, below |
| `label` | Non-blank display text |
| `stereotype` | Optional. BDD only; selects the primary visible heading |
| `features` | Optional. `properties`, `operations`, `constraints`, `literals` |
| `parentId` | Optional. A **container** element that visually contains this one |
| `assurance` | `grounded`, `assumed`, or `conceptual` |
| `evidenceRefs` | Required when `grounded` |
| `assumptionRef` | Required when `assumed` |

Element IDs are stable and load-bearing: the canonical node keeps the same ID, which is
how a later edit matches by identity rather than by guessing from labels.

**Only a container element can be a `parentId`.** In a use-case diagram that is `subject`;
BDD and activity have none in their core vocabulary. Naming a non-container parent is
refused with the permitted set rather than flattened in silence.

## 5. `relationships`

| Field | Rule |
| --- | --- |
| `id` | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, unique across relationships |
| `semanticType` | From the diagram type's vocabulary, below |
| `source`, `target` | Element IDs that exist in this draft |
| `label` | Optional |
| `sourceRole`, `targetRole` | Optional. The part/member name at that end |
| `sourceMultiplicity`, `targetMultiplicity` | Optional. `{ "lower": n, "upper": n \| "*" }` |
| `assurance`, `evidenceRefs`, `assumptionRef` | As for elements |

The host states the *meaning* of an end — its role and multiplicity. GraphPilot builds the
relationship-end object, applies the direction rule, and derives the marker.

`composition`, `generalization`, `include`, `extend`, and `commentLink` connect two
**different** elements; pointing one at itself is refused. `association` and `dependency`
may self-loop, because an employee who manages an employee is legitimate modelling.

## 6. `assurance`, and the one value you cannot author

Every element and relationship carries one, and it follows `authority`:

| Value | Means | Requires |
| --- | --- | --- |
| `grounded` | the cited source establishes this | `evidenceRefs` |
| `assumed` | a judgement the source does not establish | an `assumptionRef` |
| `conceptual` | the diagram claims nothing about this repository | `authority: conceptual` |
| `user` | **a person drew this in the editor** | nothing — and you may not author it |

`user` is not a weaker `grounded`. It is a claim about *who put the element there*, and
only the editor can make it true — so a host authoring one is stating a fact about the
world it is not in a position to know. Doing so is `assurance_unsupported`.

It exists because the editor needs an honest answer for a node somebody draws by hand.
`grounded` would fabricate a citation, `assumed` would invent an assumption nobody
accepted, and `conceptual` describes a whole diagram rather than one element. Before it
existed, adding a node to an `as_implemented` diagram failed the save outright.

The editor records it only in a diagram that already records provenance — one with
`authority: as_implemented`, or one whose elements carry an `origin`. A diagram nobody
drafted asks nobody how they know, so nothing there is stamped and nothing is badged.

When editing, a `user` element comes back in the projection and is written back unchanged.
That is the only way one legitimately appears in a draft.

## 7. `assumptions`

An unsupported proposition accepted for this diagram. Every element or relationship with
`assurance: "assumed"` names exactly one, and each assumption carries `statement`,
`reason`, and `acceptedBy` (`host` or `user`).

Assumptions are carried into the saved diagram in full, because an element marked
`assumed` whose statement nobody can recover is worse than one not marked at all.

Everything else a host works out on the way to a draft — what the repository failed to
establish, why one presentation was chosen over another — belongs in its reply to the
user. The diagram carries the citation, not the essay.

## Per-type vocabulary

Exactly these values are accepted. Anything else is rejected at save — never coerced.

### `bdd_diagram` — SysML, structural

```text
elements        block · note
relationships   composition · association · generalization · dependency · commentLink
```

- `composition` runs **part → whole**. Put the part's role and multiplicity on `sourceRole`
  and `sourceMultiplicity`.
- `generalization` runs **child → parent** and takes no roles or multiplicities.
- `dependency` runs **client → supplier** and takes no source end.
- `association` is the plain reference relationship; either end may carry a role.
- `part`, `reference`, `value`, `constraint`, and `flow` are **property kinds inside
  `features.properties`** — never element types.
- `commentLink` attaches a `note` and nothing else.

### `activity_diagram` — UML, behavioural

```text
elements        opaqueAction · initialNode · activityFinalNode · decisionNode ·
                mergeNode · forkNode · joinNode · note
relationships   controlFlow · commentLink
```

- A branch out of `decisionNode` carries a `guard`.
- `forkNode` and `joinNode` are concurrency; `decisionNode` and `mergeNode` are choice.

### `use_case_diagram` — UML

```text
elements        useCase · actor · subject · note
relationships   association · include · extend · generalization · commentLink
```

- `subject` is the system boundary and the only container in the core vocabulary; use
  `parentId` to place use cases inside it.
- `include` and `extend` run **base → included** and **extension → base** respectively.

## Authoring guidance

**Gather the minimum that supports what should be visible.** The draft describes one
diagram, not the repository. For a BDD that means the composition root, the blocks a reader
expects, ownership and dependency relationships, protocol seams, and only the properties
and constraints that should actually appear.

**Working budget**, not a schema limit:

```text
evidence records    8–30
elements            5–25
relationships       5–35
```

**Prefer omission to unsupported specificity.** No evidence for a multiplicity means leave
it out — an absent multiplicity is honest, a guessed `1..1` is not.

**Prefer the weaker true relationship.** If the source shows two blocks interact but not
that one owns the other, that is a `dependency` or `association`, not a `composition`.

**Mark what you inferred.** Structural conformance, an unwired alternative, or a
relationship you deduced rather than read is `assumed`, and names the assumption it
rests on. It is never silently `grounded`.

**Report contradictions rather than resolving them silently.** If documentation says
PostgreSQL and the composition root wires an in-memory repository, the code is what
`as_implemented` means — and the discrepancy is worth telling the user about, because
the diagram cannot show it.
