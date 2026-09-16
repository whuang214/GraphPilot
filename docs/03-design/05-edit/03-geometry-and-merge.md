# Field Classes, the Merge, and Geometry

Two things happen on every write: fields are sorted into their class and merged, then
anything genuinely new is placed. The first is bookkeeping. The second is the only part
with judgement in it.

## The three classes

Every field in a saved diagram belongs to exactly one.

### Class 1 · Host-owned — the draft is the truth

| | Fields |
| --- | --- |
| Node | `id` · `data.label` · `data.semanticType` · `data.stereotype` · `data.features` · `data.extensionPoints` · `parentId` |
| Edge | `id` · `source` · `target` · `data.semanticType` · `label` · `data.guard` · `data.condition` · `data.extensionLocations` · `sourceEnd`/`targetEnd` role, multiplicity, navigability |
| Both | `origin.assurance` · `origin.evidenceRefs` · `origin.assumptionRefs` |
| Document | `diagramType` · `name` · `metadata.authority` · `metadata.evidence` · `metadata.assurance.assumptions` · `metadata.requests` |

### Class 2 · Carried — copied by id, or computed if the id is new

| | Fields |
| --- | --- |
| Node geometry | `position` · `width` · `height` |
| Node semantics the draft cannot express | `data.port` · `data.joinSpec` · `data.isAbstract` · `data.unit` · `data.quantityKind` · `data.constraintExpression` · `data.constraintParameters` · `data.description` · `data.metadata` · `data.appliedStereotypes` |
| Edge geometry | `route.mode` · `route.waypoints` · `route.labelOffset` · `route.sourceAnchor` · `route.targetAnchor` · `sourceHandle` · `targetHandle` |
| Edge semantics the draft cannot express | `data.weight` · `data.isInterrupting` · `data.itemFlows` · `data.description` · `data.metadata` · `data.appliedStereotypes` |
| Document | `viewport` · `metadata.createdAt` · `metadata.authoring` |

A dragged position and a typed `description` are the same kind of thing: the host did not
write it and must not lose it. Splitting them into "geometry" and "semantics" would give
one of them a preservation rule and the other nothing.

`metadata.authoring` only ratchets. Once a person has saved from the editor it is `custom`
forever; a later host write does not reset it to `generated`, because the human work it
records did not stop being true.

### Class 3 · Derived — recomputed on every write

| | Fields |
| --- | --- |
| Node | `type` · every `style` key |
| Edge | `type` · every `style` key |
| Both | `origin.rationale` · `origin.schemaRules` |
| Document | `id` · `metadata.source` · `generatedBy` · `notation` · `originalType` · `intent` · `updatedAt` · `metadata.assurance.assumedElementIds` · `metadata.evidence[].contentDigest` |

## The merge

```text
for each element in the submitted draft:
    build the class-1 fields from the draft
    if this id exists in the saved diagram:
        copy every class-2 field from it
    else:
        compute the class-2 fields — place it (R3, R4), size it, default its route
    recompute every class-3 field

drop every saved element whose id the draft does not mention
```

On a create the saved diagram is empty, so every element takes the `else` branch. There is
one write path, not two.

## Evidence follows the same rule, keyed on evidence id

A citation the host **added or changed** is resolved hard: it must read, and its `symbol`
must appear in the lines it names. Those are the create rules, unchanged.

A citation that **already existed** is carried with its digest, exactly like a position —
class 2, keyed on `evidence[].id` instead of an element id.

Carried citations are then re-checked, and a region that has moved is reported as a
**warning, never a refusal**:

```text
3 of 12 cited regions have changed since this diagram was made:
  ev-permissions   src/todo_api/services/permissions.py:17-24
  …
```

Blocking on them would put an edit at the mercy of files it never looked at: a host asked
to add one node would be refused over twelve findings about a refactor somebody else did,
with no way to act on any of them. Reporting keeps the diagram honest without making an
unrelated change impossible.

This is the first caller `EvidenceService.recheck` has ever had. It was built with tests
and wired to nothing.

## Most operations need no geometry at all

The algorithm is small because the interesting cases are few.

| Operation | Geometric consequence |
| --- | --- |
| **Nodes** | |
| add, unconnected | needs a position — **R3** |
| add, connected | needs a position — **R3** |
| add, with a `parentId` | needs a position inside its parent — **R3 + R4** |
| remove | **none** — nothing moves |
| remove a node that is a parent | none; orphaned children are a *semantic* refusal, not a layout problem |
| relabel | size may grow, position kept — **R2** |
| change `semanticType` | shape recomputed, position kept — **R2** |
| change `features`, `stereotype`, `extensionPoints` | size may grow — **R2** |
| change `parentId` | re-expressed against the new parent, must land inside — **R4** |
| **Relationships** | |
| add | **none** — routes derive from node positions at render |
| remove | **none** |
| change `semanticType` | **none** — markers come from the type |
| rewire `source` / `target` | hand-placed waypoints are **dropped**; `route.mode` is kept — see below |
| add a role or multiplicity | none, but a new end label appears and may collide |
| **Cross-cutting** | |
| several changes in one call | ordering must be deterministic — **R3** |
| a container gains a child | the parent may have to grow — **R4** |

## R1 · Preserve by identity

Materialize the submitted semantics normally, then **discard the layout engine's answer
for every node that already existed** and restore its saved geometry, keyed on `id`.

This works only because `draft.elements[].id` becomes `canonical.nodes[].id` unchanged —
the rule the create path has enforced from the beginning, so matching is by identity and
never by comparing labels or guessing from graph shape.

Edges carry geometry too: `route.mode`, waypoints and `labelOffset` are restored the same
way. A person who dragged an edge label chose that.

> **Proven.** On the `todo-actors` example, with three nodes moved by hand and a
> simultaneous add, remove and relabel: **9/9 surviving nodes byte-identical.** Naive
> re-materialization kept only 6 of 10 — deleting one node was enough to shift an
> unrelated one, so preservation is required even for diagrams nobody has arranged.

### Rewiring drops the bend it invalidates

A person dragged an edge into a shape that avoided something on the path between two
particular nodes. Change either endpoint and that shape describes a route that no longer
exists, so the waypoints are discarded and the edge is drawn fresh. `route.mode` survives,
because a preference for orthogonal or straight is about the edge rather than the path.

This is not the host authoring geometry. It never names a waypoint; it makes a semantic
change, and the geometry that change invalidates goes with it — the same way removing a
node discards its position.

## R2 · A node never shrinks, and never clips

A node's minimum size is a pure function of its semantic content —
`bdd_block_min_size(label, features)`, `use_case_min_size(label, extensionPoints)`, or the
type's default. Its position is a human choice, and so is a size a person set by dragging
a corner.

So the size of a surviving node is:

```text
max(saved size, minimum for the current content)
```

Recomputing outright would undo a deliberate resize. Carrying the saved size blindly would
clip the text after a relabel. Taking the larger does neither: a person's oversized box
stays oversized, and a longer label grows the box that holds it.

Position is never recomputed. If the grown box now overlaps a neighbour, that is a
warning, not a licence to move anything.

## R3 · A new node is placed against the arrangement that exists

Not against the fresh layout's coordinates. Those describe a picture that was thrown away.

```text
neighbours = existing nodes this one connects to, in the CURRENT arrangement
if neighbours:
    x = centroid of their centres, minus half this node's width
    y = below the lowest of them, by one gap
else:
    park below the whole drawing's bounding box
while the box overlaps anything occupied:
    step one gap further along a fixed axis
```

Deterministic by construction: pure arithmetic over geometry already on disk, ties broken
by sorted id so a multi-node add never depends on request ordering. No graphviz call.

> **Why not graphviz.** Pinning was tested. With no `inputscale`, coordinates are read as
> inches and emitted as points — `200` became `14427`, then `1036800` on the next run.
> With `inputscale=72` the *relative* spacing survives exactly, but the whole drawing is
> translated (+128.83, then +153.45) and **the result is not idempotent**. Even the nodes
> that were pinned come back changed. Plain arithmetic makes existing nodes byte-identical
> rather than approximately preserved.

## R4 · Containment outranks proximity

A node with a `parentId` **must** land inside its parent's box. Proximity to its
neighbours is a preference; containment is not.

Where they conflict — a use case whose only connection is an actor *outside* the subject
boundary — place it inside the parent, nearest the parent edge that faces those
neighbours. If the parent has no free room, **grow the parent**; never place the child
outside it.

> **This rule exists because the first version of R3 shipped without it and was wrong.**
> The probe added `export-data` with `parentId: system`, connected to `owner` — an actor
> that lives outside the boundary by definition. Proximity dragged the use case clean out
> of its own container: `system` at `(408, 0, 907, 658)`, the new node at `(-475, 710)`.

## R5 · Nothing that already exists ever moves

Not to make room, not to resolve an overlap, not to tidy up. The only remedies available
are: place the newcomer somewhere else, grow a container, or warn.

A node that moves without the host mentioning it is indistinguishable, to the person who
arranged it, from the destruction this whole design exists to avoid.

**Reparenting is the one exception, and it is not really one.** Change a node's `parentId`
and it must move, because R4 outranks this rule and a child has to sit inside its parent.
That is a node moving *because the host mentioned it* — `parentId` is host-owned, so
changing it is a request to move, stated in the only vocabulary the host has. Nothing else
moves with it.

This is also the answer to *"the layout no longer makes sense"* — which is a real
complaint after ten nodes are added to a twelve-node diagram, and still not the host's to
act on. Coordinates are a lossy encoding of intent: they record that three actors were put
in a column, not *why*, and only the person looking at the picture can tell whether the
column still says what they meant. So the write **reports** — *"22 nodes now sit in a
layout built for 12"* — and the canvas is where it gets fixed.

## Worked example

A person drags the three actors into a column on the far left. The host then adds
**Export data**, connected to **Owner**.

| | |
| --- | --- |
| fresh layout proposes | `(24, 28)` — a coordinate in the abandoned space |
| `owner` actually sits at | `(-420, 320)` |
| **R3 places it at** | `(-475, 710)` — beside the column, clear of `scheduler` |
| legibility before / after | 2 of 15 hard to read → 2 of 16. **No new collisions** |
| existing nodes moved | **none** |

## How each rule is proven

Geometry is judged by eye and by measurement, never by assertion. The probes are throwaway
rigs, not tests to keep, but each rule needs one before it ships.

| Rule | Proof |
| --- | --- |
| R1 | every surviving id byte-identical after a simultaneous add + remove + relabel |
| R2 | a relabelled node keeps its position; a hand-resized node never shrinks; any new overlap is warned |
| R3 | the new node's centre is nearer its neighbours than anything else; running twice is identical |
| R4 | for every node with a `parentId`, its box is inside its parent's box |
| R5 | the set of `(id → position)` for pre-existing nodes is unchanged, exactly |
| class 2 | a person's `description`, waypoints and viewport survive a host edit that never mentions them |
| all | `legibility.measure` reports no *new* illegible labels, and the SVG is looked at |

## One consequence, accepted deliberately

Once a diagram has been edited, `materialize(draft)` no longer reproduces it — geometry now
depends on edit history rather than on the draft alone. **Edited diagrams leave the
regenerable set.**

This is not abstract: `regen_eval` rebuilds every answer and training example from its
draft, and `test_answers_round_trip` asserts `materialize(draft) == output.gp.json`. An
edited example would fail that test permanently. The review gallery's
`materialized` / `stored` badge already draws this line; an edited diagram is `stored`
forever.

Something has to record which diagrams are still regenerable.
