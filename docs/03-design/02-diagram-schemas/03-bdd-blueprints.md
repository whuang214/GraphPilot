# Block Definition Diagram Notation

GraphPilot's `bdd_diagram` uses one reusable Block definition shape plus structured features and five core relationships. The editor keeps object-oriented modeling explicit without presenting every SysML metamodel specialization as a separate node type.

## Common use cases

- System and subsystem definitions
- Whole/part and reference structure
- Values, constraints, interfaces, and operations as Block content
- Type specialization and dependency

## Nodes

| semanticType | UI label | Notation |
| --- | --- | --- |
| `block` | Block | classifier box with primary stereotype/name header and derived feature compartments |
| `note` | Note | folded-corner comment |

`block` is the only BDD definition semantic type. Optional `data.stereotype` controls its visible `«heading»`; blank or absent values render as `«block»`. The editor suggests `valueType`, `constraint`, `interfaceBlock`, and `enumeration`, while allowing custom text. Suggestions are presentation/modeling conveniences rather than additional node semantic types.

`data.appliedStereotypes` remains separate additional domain/profile data and does not choose the primary heading.

## Structured Block features

Block `data.features` may contain properties, operations, receptions, constraints, and literals. Core property kinds are:

- `part`
- `reference`
- `value`
- `constraint`
- `flow`

A property remains a structured row when shown inside its owner:

```json
{
  "kind": "part",
  "name": "engine",
  "type": "Engine",
  "multiplicity": { "lower": 1, "upper": 1 }
}
```

Canvas and SVG compartments are derived from this data. `data.compartments` is not canonical. A Block with no visible feature rows renders as one compact stereotype/name section without an empty divider.

If a property's type is shown as a separate box, that box is another `block`. Use `composition` when the first Block is an owned part of the second, or `association` for a reference/association. Users may apply a custom primary stereotype to the separate Block, but GraphPilot does not create standalone `part`, `reference`, `value`, `constraint`, or `flow` node types.

Definition-detail fields such as `isAbstract`, `unit`, `quantityKind`, `constraintExpression`, and `constraintParameters` remain optional Block data. Literal rows support an `enumeration` primary stereotype without a separate Enumeration node type.

## Relationships

| semanticType | Meaning | Direction / notation |
| --- | --- | --- |
| `association` | plain or reference relationship | solid line; roles, multiplicities, and navigability are end data |
| `composition` | owned whole/part relationship | part `source` → whole `target`; filled diamond at target |
| `generalization` | specialization | child → parent; hollow triangle at target |
| `dependency` | client depends on supplier | client → supplier; dashed open arrow |
| `commentLink` | note attachment | dashed line without an arrowhead |

The BDD connector tray exposes exactly Association, Composition, Generalization, Dependency, and Comment Link together. New BDD relationships default to orthogonal routing; users may choose Straight for the next or selected edge. Composition is a first-class GraphPilot edge type rather than association-end aggregation. New composition edges always use part-to-whole direction. The inspector's **Swap ends** action swaps source/target, corresponding end data, endpoint handles/anchors, and authored route direction together. Users may also delete and redraw an incorrectly directed edge.

A newly drawn edge incident to a `note` becomes `commentLink` automatically. Shared aggregation, namespace containment, participant-property links, connector-property links, and port relationships are not core palette or generation choices.

## Relationship ends

Association and composition ends may carry role, type, multiplicity, navigability, ordering/uniqueness, qualifiers, and property path. Composition ownership comes from its fixed direction, not an `aggregation` field. Legacy association aggregation may remain readable for compatibility but is not created by core authoring or generation.

## Structural rules

- Include at least one `block`.
- Generalization points from child to parent.
- Composition points from part to whole and places the filled diamond at the target.
- Association and composition endpoints reference existing Blocks.
- Properties are structured Block content or are represented by a related Block, never separate property semantic types.
- Notes and comment links do not establish structural ownership.

## Scope boundary

Ports, proxy/full-port distinctions, association blocks, property-specific types, instances, units/quantity-kind nodes, containment, and connector callouts are outside the core BDD vocabulary. Retained legacy elements may load and render, but core generation, palettes, All authorable, and semantic selectors do not create them. Internal connector networks remain the responsibility of a future internal-block diagram type.
