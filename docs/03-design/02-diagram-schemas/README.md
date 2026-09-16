# Diagram Schemas and Per-Type Notation

This folder owns the **canonical diagram contract** and the **human-readable per-type
notation reference**: the node/edge vocabulary, the shape and marker notation (what each
`semanticType` looks like on the canvas *and* in the SVG export), edge line-style and arrow
rules, connector-mode defaults, default layout, and per-type structure.

## Contents

| Document | Owns |
| --- | --- |
| [`01-diagram-json-schema.md`](01-diagram-json-schema.md) | The canonical `graphpilot.diagram.v1` contract: envelope, nodes, edges, structured features, relationship ends, provenance |
| [`02-activity-blueprints.md`](02-activity-blueprints.md) | `activity_diagram` notation |
| [`03-bdd-blueprints.md`](03-bdd-blueprints.md) | `bdd_diagram` notation |
| [`04-use-case-blueprints.md`](04-use-case-blueprints.md) | `use_case_diagram` notation |

## How a type's vocabulary is defined

Each MVP type exposes a small core authoring subset of one shared element catalog
(`backend/services/diagrams/catalog/element_catalog.py`). All nodes render through the
single `gpNode` family; `data.semanticType` selects the core primitive, while BDD Block
`data.stereotype` selects its primary visible heading. The catalog may retain
non-authorable legacy elements for load and render compatibility, but palettes, All
authorable, semantic selectors, and materialization use only the bounded profiles owned by
`backend/services/diagrams/catalog/diagram_types.py`.

Per-type notation rules also ship as `backend/assets/blueprints/<type>/prompts.md`, which
becomes the host-facing authoring guidance in the
[draft contract](../01-generation/01-draft.md). Curated examples live beside them under
`examples/answers/`; they are review and parity fixtures, not prompt content.

## Keep these current

Update the relevant per-type document **in the same change** whenever the notation changes
— new or changed `semanticType`s, BDD primary stereotypes, shape or edge-marker rendering,
edge line-style or direction rules, layout, or per-type structure — so the human-readable
notation never drifts from the shared element catalog, the renderers
(`frontend/src/editor/canvas/customNodes.tsx` and
`backend/services/diagrams/rendering/diagram_render_service.py`), the type profile, and the
structural critic.

The contract deliberately prefers bounded core identities, structured features, and
reusable primitives over metamodel-complete palettes.

## Related

- [`01-generation/`](../01-generation/README.md) — the draft contract and how notation is materialized
- [`03-validation/`](../03-validation/README.md) — draft validation and canonical validation
- [`04-rendering.md`](../04-rendering.md) — SVG and PNG output
- [`06-diagram-json-mapping.md`](../../02-architecture/06-diagram-json-mapping.md) — canonical ↔ React Flow round-trip
- `docs/06-research/uml-sysml-vocabulary/vocabulary.md` — clause-traced neutral UML 2.5.1 / SysML 1.6 extraction
