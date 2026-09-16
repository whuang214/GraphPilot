# Materialization

## Purpose

Turn a validated [draft](01-draft.md) into a canonical `graphpilot.diagram.v1` document.

**Materialization is a pure function.** Same draft, same diagram — every time, with no
provider call, no randomness, and no clock beyond the timestamp stamped into metadata.
That is what makes the notation contract enforceable: the rules below are *applied*, not
*checked after a model guessed*.

```text
draft  →  logical  →  layout  →  canonical  →  validate  →  persist
          ▲                      ▲
          semantics resolved     positions, styles, markers, provenance
```

## Stage 1 — draft to logical

The logical graph is the draft with GraphPilot's vocabulary resolved and its defaults
filled. It carries no coordinates.

### Elements

| Draft | Logical / canonical node |
| --- | --- |
| `id` | `node.id` — **copied unchanged** |
| `semanticType` | `node.data.semanticType` |
| `label` | `node.data.label` |
| `stereotype` | `node.data.stereotype` |
| `features` | `node.data.features`, normalized |
| `parentId` | `node.parentId` |
| `evidenceRefs`, `assurance` | `node.origin` |
| — | `node.type` = `gpNode` |
| — | `node.style` from the element catalog |
| — | `node.width` / `node.height` from content-fit sizing |
| — | `node.position` from layout |

Feature normalization fills the compartment arrays GraphPilot's renderer and the editor
both expect: absent arrays become empty, blank names are dropped, and a property keeps
`kind`, `name`, `type`, `multiplicity`, and `default`.

### Relationships

| Draft | Logical / canonical edge |
| --- | --- |
| `id` | `edge.id` — **copied unchanged** |
| `semanticType` | `edge.data.semanticType` |
| `source`, `target` | `edge.source`, `edge.target` |
| `label` | `edge.label` |
| `sourceRole` + `sourceMultiplicity` | `edge.data.sourceEnd` — **constructed** |
| `targetRole` + `targetMultiplicity` | `edge.data.targetEnd` — **constructed** |
| `evidenceRefs`, `assurance` | `edge.origin` |
| — | `edge.type` = `default` |
| — | `edge.style`, dash pattern, markers |

## Stage 2 — the notation rules

These are the rules the retired pipeline asked a model to satisfy and then rejected it for
missing. They are now applied by construction.

### BDD

| Semantic type | Direction | Source end | Target end |
| --- | --- | --- | --- |
| `composition` | part → whole | optional — the part's role and multiplicity | optional |
| `association` | either | optional | optional |
| `generalization` | child → parent | **omitted** | **omitted** |
| `dependency` | client → supplier | **omitted** | optional |
| `commentLink` | note → element | omitted | omitted |

**The filled diamond comes from the relationship type, not from the data.** `composition`
carries `target_marker: diamond_filled` in the element catalog, so the diamond is drawn at
the whole from the type alone.

The materializer therefore **never sets `aggregation`** on a composition. `aggregation` is
how a plain `association` expresses composition; on a `composition` edge it draws a
*second* diamond at the part. A relationship end here exists only to carry a role and
multiplicity, and is emitted only when the host states one:

```json
{
  "semanticType": "composition",
  "source": "todo-service",
  "target": "todo-application",
  "data": {
    "sourceEnd": { "role": "todoService", "multiplicity": { "lower": 1, "upper": 1 } }
  }
}
```

An end with nothing in it is not emitted: the canonical schema would accept `{}`, and it
would mean nothing.

A draft that supplies a role or multiplicity on an end the notation forbids — a
generalization end, a dependency source end — is **rejected at save**, not silently
dropped. Silent dropping would hide a real modelling mistake.

### Activity

`controlFlow` carries an optional `guard`. Every branch out of a `decisionNode` must carry
one; that is a draft-validation rule, checked before materialization.

### Use case

`include` runs base → included, `extend` runs extension → base, `generalization` runs
specific → general. None of the three carries relationship ends.

## Stage 3 — layout

`DiagramLayoutService` over the pinned in-process PyGraphviz engine assigns positions and
sizes: top-level nodes get absolute positions, contained nodes get positions relative to
their parent, and per-type sizing comes from the element catalog.

Layout is the only stage with an external dependency, and it consumes the logical graph —
it never sees the draft. `parentId` containment is preserved exactly.

## Stage 4 — canonical assembly

Produces the `graphpilot.diagram.v1` document:

```json
{
  "schemaVersion": "graphpilot.diagram.v1",
  "kind": "diagram",
  "diagramType": "bdd_diagram",
  "id": "...",
  "name": "todo-structure",
  "metadata": { "...": "see 03-lifecycle.md" },
  "viewport": { "x": 0, "y": 0, "zoom": 1 },
  "nodes": [],
  "edges": []
}
```

Then the canonical validator runs. It is the same
[`DiagramValidationService`](../03-validation/02-diagram-validation.md) the editor and the public
`diagram_validate` tool use — no generation-specific bypass, and no generation-specific
leniency.

**A materializer defect surfaces here as a validation failure, not as a bad saved
diagram.** With no model in the loop, a canonical validation failure means GraphPilot has a
bug, so it returns an operation error rather than a domain outcome.

## Provenance

Each node and edge carries an `origin` recording what supports it:

```json
{
  "origin": {
    "assurance": "grounded",
    "evidenceRefs": ["ev-todo-service"],
    "assumptionRefs": [],
    "rationale": "TodoService is defined and wired at src/todo_api/services/todo_service.py:25-100."
  }
}
```

### What an element's provenance became

This section described the change as pending for long enough that the migration finished
underneath it. **It is done.** An `origin` now carries:

| Field | What it records |
| --- | --- |
| `assurance` | `grounded`, `assumed` or `conceptual` — what the diagram claims about this element |
| `evidenceRefs` | The `metadata.evidence` entries it was built from. Required when `grounded` |
| `assumptionRefs` | The assumptions it rests on, whose bodies travel in `metadata.assurance` |
| `schemaRules` | Still records a rule-derived element |
| `rationale` | Generated from the refs, so it cannot disagree with them |

`origin.claimRefs` and `metadata.generationContext` were the JSON 1 / JSON 2 model's
bindings and are gone with it. `metadata.evidence` carries the cited regions inline, which
is what makes a saved diagram checkable on its own.

Field-level detail lives with the canonical schema in
[`../02-diagram-schemas/`](../02-diagram-schemas/README.md), and
`tests/docs/test_diagram_schema_doc.py` now holds that document to what a real node
carries — because `claimRefs` survived in it until this audit.

## What materialization never does

- Call a provider.
- Invent an element, relationship, label, or multiplicity the draft did not state.
- Coerce an off-vocabulary semantic type to a default. Draft validation rejects it first.
- Repair a semantic mistake. Only mechanical shape is filled in.
- Rewrite an ID. Draft IDs reach the canonical document unchanged, because
  [editing](../05-edit/README.md) matches on them.
