# Activity Diagram Notation

GraphPilot's `activity_diagram` uses a deliberately small UML-style activity vocabulary for ordinary workflows. The clause-level UML research remains a reference inventory, not a requirement to expose every Action metaclass to the generator or editor.

## Common use cases

- Business and approval workflows
- Software/control behavior
- Branching and concurrent processes

## Rendering model

Every node uses the `gpNode` React Flow family. `data.semanticType` selects one of the eight core node meanings below; visually similar decision/merge and fork/join pairs stay distinct because their structural rules differ.

## Nodes

| semanticType | UI label | Notation |
| --- | --- | --- |
| `initialNode` | Initial | solid filled disc; the visible outer circle owns attachment projection and a zoom-stable pointer halo while the optional label remains outside connection geometry |
| `opaqueAction` | Action | rounded rectangle; the editable label carries the domain step |
| `decisionNode` | Decision | diamond with guarded outgoing alternatives |
| `mergeNode` | Merge | diamond recombining alternatives without synchronization |
| `forkNode` | Fork | bar splitting one flow into concurrent flows |
| `joinNode` | Join | bar synchronizing concurrent incoming flows |
| `activityFinalNode` | Activity Final | bull's-eye terminating the activity; its visible outer circle owns attachment projection |
| `note` | Note | folded-corner comment |

Specialist Action subclasses, flow-final/object/pin nodes, partitions, and structured/interruptible/expansion regions are not part of core generation, palettes, All authorable, or semantic selectors. Retained Flow Final uses the same visible-circle attachment profile as core controls; other retained legacy elements may still load and render.

## Relationships and data

| semanticType | Meaning | Structured data |
| --- | --- | --- |
| `controlFlow` | execution order | optional `guard` and `weight` |
| `commentLink` | note attachment | dashed line without an arrowhead |

The Activity connector tray exposes Control Flow and Comment Link together. New Activity relationships default to orthogonal routing; users may choose Straight for the next or selected edge. A newly drawn edge incident to a `note` becomes `commentLink` automatically regardless of the selected tool. Decision branch conditions live in `edge.data.guard`, not only in the display label. A non-default join condition remains `node.data.joinSpec`.

## Structural rules

- Exactly one `initialNode`; at least one `activityFinalNode`.
- The initial node has no incoming control flow; activity-final nodes have no outgoing control flow.
- A decision has at least two guarded outgoing flows; guarded alternatives may reconverge on the same target.
- A merge has at least two incoming flows and at most one outgoing flow; unlike a Join, its alternatives do not require distinct sources.
- A fork has exactly one incoming flow and outgoing flows to at least two distinct targets; parallel edges to one target remain editable drafts but do not satisfy the branch minimum.
- A join has incoming flows from at least two distinct sources and exactly one outgoing flow.
- Every flow-participating node is reachable from the initial node.
- Notes and comment links do not count as activity flow or reachability.

## Scope boundary

The editor is a refinement surface rather than a complete UML metamodel browser. Users model specialist detail with labels, structured fields, custom Block stereotypes where appropriate, or retained custom/legacy documents instead of expanding the core activity vocabulary.
