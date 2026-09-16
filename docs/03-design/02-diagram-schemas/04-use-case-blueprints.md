# Use-Case Diagram Notation

GraphPilot's `use_case_diagram` follows UML 2.5.1 clause 18. Generation is LLM-backed; the runtime subset is defined by the shared element catalog and type profile.

## Common use cases

- Identify external roles and system goals
- Define a subject's behavioral scope
- Show mandatory reuse, optional extension, and specialization

## Nodes and structured features

| semanticType | UML element | Notation |
| --- | --- | --- |
| `actor` | Actor | stick figure; label below |
| `useCase` | UseCase | ellipse |
| `subject` | subject classifier | **System Boundary** containing rectangle; its editable label is the system name |
| `note` | Comment | folded-corner note |

A classifier-style non-human actor may use an applied `actor` presentation while retaining actor semantics. Actor connection gestures follow a tight curved envelope around the visible stick figure and exclude its label; use-case gestures remain on the complete visible ellipse. Canvas and SVG project both profiles identically without resizing either node. A use case's named extension points live in `data.extensionPoints` and render in its extension-points compartment.

When a subject is displayed, each contained use case has `parentId` set to that subject. UML permits a subject boundary to be omitted, so subject containment is enforced only when the diagram displays one.

## Relationships

| semanticType | UML relationship | Direction and data |
| --- | --- | --- |
| `association` | actor/use-case communication | actor ↔ use case; no required arrowhead |
| `generalization` | specialization | specialized actor/use case → parent of the same kind; hollow triangle |
| `include` | Include | including/base use case → included use case; dashed open arrow labeled `«include»` |
| `extend` | Extend | extending use case → extended/base use case; dashed open arrow labeled `«extend»` |
| `commentLink` | comment attachment | note → annotated element; dashed, no arrowhead |

The Use Case connector tray exposes Association, Generalization, Include, Extend, and Comment Link together. New Use Case relationships default to `route.mode: "straight"`; users may choose Orthogonal for the next or selected edge. Existing edges with no route mode remain orthogonal. `include` and `extend` remain distinct relationship identities. A newly drawn edge incident to a `note` becomes `commentLink` automatically regardless of the selected tool.

An `extend` edge carries:

- `data.condition` — the Boolean extension condition
- `data.extensionLocations` — names declared by the target use case's `extensionPoints`

## Structural rules

- Include at least one actor and one use case.
- Associations connect an actor and a use case.
- Include/extend connect two use cases.
- Generalization connects two actors or two use cases.
- Extend names a target extension point.
- If a subject is shown, its use cases are contained through `parentId`.

## Layout

- Subjects and use cases occupy the center/right.
- Actors remain outside the subject.
- Generalization arrows point toward the parent.
- Include and extend direction follows their UML semantics rather than visual convenience.
