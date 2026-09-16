# bdd_diagram — authoring guidance

A **SysML Block Definition Diagram**: structure. Blocks, what they own, and how they
relate. Not behaviour-driven development, and not a behavioural view — use
`activity_diagram` for behaviour.

## What to include

Start from the composition root and work outward: the blocks a reader expects to find,
the ownership and dependency relationships between them, and the protocol seams. Include
a property or constraint only when it should actually appear on the canvas.

## Rules

- Use `block` for every definition; a diagram needs at least one.
- `part`, `reference`, `value`, `constraint`, and `flow` are **property kinds inside
  `features.properties`** — never element types.
- A property records `name`, and optionally `kind`, `type`, `multiplicity`, and `default`.
  Use `features.operations`, `features.constraints`, and `features.literals` for their
  compartments.
- A composition's part role and multiplicity go on `sourceRole` and `sourceMultiplicity`.
  The filled diamond at the whole comes from the relationship type — you never describe a
  marker.
- `commentLink` attaches a `note` and nothing else.

## Choosing the relationship

| The source shows | Use |
| --- | --- |
| One object owns another's lifecycle | `composition` |
| Two objects reference each other | `association` |
| One type specialises another | `generalization` |
| One module imports or calls another | `dependency` |

**Prefer the weaker true relationship.** If the code shows two blocks interact but not
that one owns the other, that is a `dependency`, not a `composition`.

## Layout

You do not author positions. Blocks are laid out along relationship direction, so a
composition's part is placed above the whole it belongs to.
