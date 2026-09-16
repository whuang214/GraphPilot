# The GraphPilot Diagram Standard — JSON Schema and Semantic Vocabulary

> **Design authority:** This document defines the intended canonical diagram contract.
> Implementation status belongs only to
> [`01-current-state.md`](../../05-delivery/01-current-state.md).

## Summary

GraphPilot persists every editable diagram as `graphpilot.diagram.v1`. The JSON envelope mirrors the useful React Flow node/edge shape while keeping the three MVP vocabularies deliberately small enough for reliable generation and manual editing.

The model has four distinct layers:

1. **Normative research inventory** — the clause-traced UML/SysML extraction in `../../research/uml-sysml-vocabulary/vocabulary.md`; it informs GraphPilot but does not make every metamodel class authorable.
2. **Supported catalog** — render/load knowledge for core elements, custom elements, and retained legacy semantics in `backend/services/diagrams/catalog/element_catalog.py`.
3. **Core per-type profile** — the bounded semantic subset exposed to generation, palettes, and semantic selectors in `backend/services/diagrams/catalog/diagram_types.py`.
4. **Render primitives** — reusable canvas/SVG drawing implementations shared by core and compatibility elements.

## Canonical identity rules

- `node.type` is always the React Flow renderer family `gpNode`.
- `node.data.semanticType` is the GraphPilot node identity selected from the diagram's core profile.
- `edge.type` is always the React Flow edge renderer family `default`.
- `edge.data.semanticType` is the GraphPilot relationship identity selected from the diagram's core profile.
- A BDD definition uses `semanticType: "block"`; optional `data.stereotype` controls its primary visible `«heading»` and may be custom.
- `data.appliedStereotypes` stores additional domain/profile stereotype applications independently of the BDD primary heading.
- `part`, `reference`, `value`, `constraint`, and `flow` are structured Block property kinds, not node types.
- BDD `composition` is a first-class GraphPilot edge identity with canonical part-to-whole direction; relationship roles and multiplicities remain structured end data.
- Use-case `include` and `extend`, activity decision/merge, and activity fork/join remain distinct because their behavior differs even when they share a primitive.

## Diagram types

The schema accepts:

- `activity_diagram` — UML 2.5.1 Activities/Actions
- `use_case_diagram` — UML 2.5.1 UseCases
- `bdd_diagram` — compact SysML-style block definitions, structured features, and core relationships
- `custom` — save/validate-only canvas for generic or compatibility catalog elements

The first three are generatable. `custom` is intentionally not generated.

## Implemented render primitives

| Primitive | Canonical shape family |
| --- | --- |
| `rounded-rect` | ordinary activity actions |
| `initial`, `final` | initial disc and activity-final bull's-eye |
| `diamond`, `bar` | decision/merge and fork/join |
| `actor`, `ellipse`, `container`, `note` | actor, use case, system boundary, and folded-corner comment |
| `classifier-box` | BDD Block with a primary stereotype heading and derived feature compartments |

Other primitives may remain available only to load/render existing or custom documents; they are not part of the three core generation/palette profiles.

## Per-type semantic subsets

### Activity

- nodes: `initialNode`, `opaqueAction`, `decisionNode`, `mergeNode`, `forkNode`, `joinNode`, `activityFinalNode`, `note`
- edges: `controlFlow`, `commentLink`
- action labels carry domain behavior; specialist Action metaclasses, object/pin nodes, partitions, regions, object flow, and exception-handler edges are not authorable core vocabulary
- guards remain structured edge data, and a non-default join condition remains structured node data

### Use case

- nodes: `actor`, `useCase`, `subject`, `note`; the editor labels `subject` as **System Boundary**
- edges: `association`, `generalization`, `include`, `extend`, `commentLink`
- use-case extension points are structured node data
- extend conditions and extension locations are structured edge data

### BDD

- nodes: `block`, `note`
- primary Block heading: optional `data.stereotype`, defaulting visually to `block`; editor suggestions are `valueType`, `constraint`, `interfaceBlock`, and `enumeration`, plus custom text
- structured Block property kinds: `part`, `reference`, `value`, `constraint`, `flow`
- edges: `association`, `composition`, `generalization`, `dependency`, `commentLink`
- `composition` is directed part (`source`) to whole (`target`) and renders a filled diamond at the target; swapping ends reverses endpoints and their end/route data together
- a separately drawn property type is another Block connected by `composition` for ownership or `association` for reference; it is not a separate property-node semantic type

`commentLink` is shared by all three profiles. Any newly drawn edge incident to a `note` becomes a `commentLink` automatically.

## Canonical document

```json
{
  "schemaVersion": "graphpilot.diagram.v1",
  "kind": "diagram",
  "diagramType": "bdd_diagram",
  "id": "diagram_vehicle",
  "name": "Vehicle Definition",
  "metadata": {
    "source": "mcp",
    "authoring": "generated",
    "originalType": "bdd_diagram",
    "notation": "sysml",
    "intent": "Vehicle structure and interfaces",
    "authority": "conceptual",
    "generatedBy": "graphpilot-materializer",
    "createdAt": "2026-08-04T09:00:00Z",
    "updatedAt": "2026-08-04T09:00:00Z"
  },
  "viewport": { "x": 0, "y": 0, "zoom": 1 },
  "nodes": [],
  "edges": []
}
```

Required top-level fields are `schemaVersion`, `kind`, `diagramType`, `id`, `name`, `metadata`, `viewport`, `nodes`, and `edges`. Unknown top-level fields are rejected. `metadata` stays open — a diagram somebody added a key to still loads — and the keys defined below are the ones materialization always writes. All numeric values must be finite JSON numbers (`NaN`/`Infinity` are rejected).

## Canonical node

```json
{
  "id": "vehicle",
  "type": "gpNode",
  "position": { "x": 100, "y": 100 },
  "width": 240,
  "height": 170,
  "data": {
    "label": "Vehicle",
    "semanticType": "block",
    "stereotype": "block",
    "features": {
      "properties": [
        {
          "kind": "part",
          "name": "engine",
          "type": "Engine",
          "multiplicity": { "lower": 1, "upper": 1 }
        },
        {
          "kind": "value",
          "name": "mass",
          "type": "Mass",
          "multiplicity": { "lower": 1, "upper": 1 },
          "default": 1200
        }
      ],
      "operations": [
        { "name": "start", "parameters": [], "returnType": null }
      ],
      "receptions": [],
      "constraints": [
        { "name": "range", "expression": "range >= 500 km" }
      ],
      "literals": []
    },
    "appliedStereotypes": [
      { "name": "physical" }
    ]
  },
  "style": {
    "background": "#ffffff",
    "borderColor": "#333333",
    "color": "#111111",
    "borderWidth": 1,
    "borderStyle": "solid"
  }
}
```

### Structured features

`data.features` can contain:

- `properties[]`
- `operations[]`
- `receptions[]`
- `constraints[]`
- `literals[]`

A property has a required `kind` and `name`, plus optional type, lower/upper multiplicity, default, direction, and standard modifiers. Multiplicity bounds are non-negative integers; a finite `upper` must be greater than or equal to `lower` (`"*"` remains unbounded). Supported core BDD property kinds are:

- `part`
- `reference`
- `value`
- `constraint`
- `flow`

Canvas and SVG feature compartments are derived from this data. `data.compartments` is not canonical. A property shown outside its owner is represented by another Block plus a relationship rather than a separate property node.

### Primary and applied stereotypes

BDD Block `data.stereotype` is one optional primary display string. Blank or absent values render as `«block»`; a nonblank value renders as the Block's `«heading»`. Suggested editor values are conveniences rather than additional semantic types, and custom text is allowed.

`data.appliedStereotypes[]` remains a separate list of additional domain/profile applications with optional properties. It does not choose the primary heading.

### Type-specific node fields

- BDD Block: `stereotype`, `features`, `isAbstract`, `unit`, `quantityKind`, `constraintExpression`, `constraintParameters[]`
- use case: `extensionPoints[]`
- join: `joinSpec`
- all nodes: `appliedStereotypes[]`

Port/pin fields and specialist semantic identities may remain schema-readable only for legacy/custom compatibility; core generation, palettes, All authorable, and semantic selectors do not create them.

## Canonical edge

```json
{
  "id": "engine_vehicle",
  "type": "default",
  "source": "engine",
  "target": "vehicle",
  "data": {
    "semanticType": "composition",
    "sourceEnd": {
      "role": "engine",
      "multiplicity": { "lower": 1, "upper": 1 }
    },
    "targetEnd": {
      "role": "vehicle",
      "multiplicity": { "lower": 1, "upper": 1 }
    }
  },
  "style": { "stroke": "#333333", "strokeWidth": 2 }
}
```

Edge identity is `id`, not the endpoint pair. Multiple edges may share the same `source` and `target`; typed structural validation determines whether their semantics/cardinality are meaningful, while `custom` preserves them without typed cardinality rules.

### Optional route geometry

A relationship may carry authored presentation overrides without changing its semantic identity:

```json
{
  "route": {
    "mode": "orthogonal",
    "sourceAnchor": { "side": "right", "offset": 0.25 },
    "targetAnchor": { "side": "top", "offset": 0.6 },
    "waypoints": [
      { "x": 310, "y": 42 },
      { "x": 510, "y": 42 }
    ],
    "labelOffset": { "x": 12, "y": -24 }
  }
}
```

Every route member is optional, but an empty route object is not canonical. Optional `mode` is `orthogonal` or `straight`; absence means orthogonal so existing diagrams need no migration. Straight mode contains no `waypoints` and draws exactly one primitive-boundary segment. Orthogonal waypoints are finite ordered root-diagram routing coordinates, bounded to 32, which the resolver joins and simplifies. Anchor side is `top`, `right`, `bottom`, or `left`; offset is normalized to `0..1`. `labelOffset` moves the central path label in diagram units. Missing anchors select deterministic automatic boundary positions, and calculated paths are never saved. An authored route anchor takes precedence over a legacy midpoint `sourceHandle`/`targetHandle`; editing or resetting anchors clears the superseded handle.

### Relationship ends

`sourceEnd` and `targetEnd` can carry:

- role and type
- lower/upper multiplicity (`upper` may be `"*"`)
- navigability
- ordering/uniqueness
- qualifiers
- nested property path

For core BDD composition, `source` is always the part and `target` is always the whole; the renderer places the filled diamond at the target. The inspector's **Swap ends** action swaps endpoints, end data, endpoint handles/anchors, and authored route direction atomically. New core documents do not encode composition through an `aggregation` field, although retained legacy documents may still contain one.

### Other relationship data

- use-case extend: `condition`, `extensionLocations[]`
- activity control flow: `guard`, `weight`
- all edges: `appliedStereotypes[]`

## The metadata a materialized diagram carries

Canonical `.gp.json` stores diagram meaning and edit geometry, not a run log. Every diagram
the backend writes carries exactly this, taken from a real committed example:

```json
{
  "metadata": {
    "authoring": "generated",
    "authority": "as_implemented",
    "createdAt": "2026-08-04T21:56:58.465714+00:00",
    "generatedBy": "graphpilot-materializer",
    "intent": "kitepay-data-model",
    "notation": "sysml",
    "originalType": "bdd_diagram",
    "source": "mcp",
    "updatedAt": "2026-08-04T21:56:58.465714+00:00"
  }
}
```

Two more appear conditionally: `evidence` when the diagram cites source, and `assurance`
when some element is `assumed`.

| Field | Canonical rule |
| --- | --- |
| `metadata.assurance` | The assumptions any `assumed` element rests on, carried with the diagram rather than left in the draft. |
| `metadata.authoring` | How the diagram came to exist. `generated` means a host authored a draft and the backend materialized it. |
| `metadata.authority` | `as_implemented` cites evidence; `conceptual` makes no claim about this repository. Enforced: `as_implemented` requires `evidence`, and evidence requires an authority. |
| `metadata.createdAt` | When the diagram was first written. |
| `metadata.evidence` | The cited source regions the diagram was built from, carried inline so the file is self-contained. Every entry is referenced by some element. |
| `metadata.generatedBy` | The component that produced it, `graphpilot-materializer`. |
| `metadata.intent` | The diagram's name, carried so an exported file still says what it was for. |
| `metadata.notation` | The notation family its rules came from. |
| `metadata.originalType` | The diagram type the draft requested, kept separate from the top-level `diagramType` so a later conversion cannot erase what was asked for. |
| `metadata.requests` | Every ask made of this diagram, oldest first, each stamped when it arrived. Append-only, and the only durable record of why the diagram looks the way it does — the draft that carried the ask is not kept as an authority. |
| `metadata.source` | How it arrived — `mcp` for a host, or the editor. |
| `metadata.updatedAt` | When it was last written. |

**`additionalProperties` is `true` and nothing is `required`.** That is deliberate: a
diagram somebody added a key to still loads, and the frontend type is open for the same
reason. A declared field is still type-checked, so `authority: 12345` is refused.

*(Two generation-context fields were documented here as canonical, with required `request`
and `manifest` sub-objects. The provider pipeline they belonged to was retired in `P0` and
they were never removed from this document — the one someone reads to understand the file
GraphPilot writes. `a5.f2` found the same drift from the other side, with the schema silent
about four fields it does write. Both directions are now checked by
`tests/docs/test_diagram_schema_doc.py`.)*

Canonical nodes and edges use one strict top-level `origin` sibling to `data`:

```json
{
  "origin": {
    "assurance": "grounded",
    "evidenceRefs": ["ev-user"],
    "assumptionRefs": [],
    "schemaRules": [],
    "rationale": "Established by cited evidence: ev-user."
  }
}
```

Captured from a committed diagram. `rationale` is generated from the refs rather than
authored — a host states the assurance and cites the lines; the sentence explaining it is
built from what it cited, so the two cannot disagree.

| Field | Canonical meaning and bound |
| --- | --- |
| `assurance` | `grounded`, `assumed` or `conceptual`. What the diagram claims about this element, and the only field a reader needs to know how much to trust it |
| `evidenceRefs[]` | The `evidence` entries this element was built from. Required for `grounded`; every id resolves to a record in `metadata.evidence` |
| `rationale` | One sentence saying why the element carries that assurance, generated from the refs rather than authored |
| `assumptionRefs[]` | `0..8` unique smallest-sufficient explicitly accepted context-request assumption IDs |
| `schemaRules[]` | `0..8` unique allowlisted GraphPilot rule IDs for non-factual notation scaffolding |
| `rationale` | Required nonblank user-facing mapping explanation, `1..2,000`; never hidden reasoning |

All four fields are required and at least one grounding array is nonempty. Claim/assumption references must belong to
the exact persisted authority identified by metadata. The only V1 schema rule is `activity.initial-node`, valid only for
a domain-neutral `initialNode` with an empty, `Initial`, or `Start` label and no domain-bearing fields. Schema-only
origin can never authorize unsupported domain meaning.

Context generation preserves the model's smallest-sufficient validated origins through layout and canonical assembly;
it never assigns claims to unsupported meaning. Frontend adapters preserve origins as nonvisual canonical data, and
rendering ignores them visually.

Canonical metadata never contains model/deployment identity, prompt or logical-schema versions, example IDs, readiness
result/policy, semantic-review rubric/score/findings/actions, repair counts, layout-engine identity, token/latency usage,
full requests/claims/evidence, raw candidates, diagnostics, credentials, or hidden reasoning. Compact run facts belong
to the optional digest-bound trace sidecar, and full reached-stage data belongs to optional numbered diagnostics, both
owned by [Generation](../01-generation/README.md). Exact authority and origin-support semantics live in
[`01-generation/03-lifecycle.md`](../01-generation/03-lifecycle.md).

## Strictness and custom authoring

A concrete `diagramType` validates against its core per-type subset and structural critic. `custom` accepts supported generic/compatibility catalog elements and has no per-type structural critic. `metadata.authoring` is provenance only; strictness is controlled by `diagramType`.

Core generation, palettes, All authorable, and semantic selectors expose only bounded authorable entries. Retained specialist identities may load and render for compatibility but cannot be newly authored. UI save reconciliation may change a concrete type to `custom` when edited content leaves the declared subset. [Validation](../03-validation/02-diagram-validation.md) owns warning/block policy; [Generation](../01-generation/README.md) owns draft acceptance and its no-write failures.

## Contract parity surfaces

- Normative vocabulary: `docs/06-research/uml-sysml-vocabulary/vocabulary.md`
- Runtime semantic catalog: `backend/services/diagrams/catalog/element_catalog.py`
- Per-type subsets/defaults: `backend/services/diagrams/catalog/diagram_types.py`
- JSON envelope/structured fields: `backend/assets/schemas/diagram.json`
- Context authority and origin-support semantics: `08-context-backed-generation/05-generation-and-provenance.md`
- Generation pipeline, trace, and diagnostics: `04-generation-design.md`
- Canvas renderer: `frontend/src/editor/canvas/customNodes.tsx`
- SVG renderer: `backend/services/diagrams/rendering/diagram_render_service.py`
- Per-type notation: `diagram-schemas/`

Keep these consumers in parity whenever canonical semantics or notation changes.
