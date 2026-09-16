# activity_diagram — authoring guidance

A **UML Activity Diagram**: behaviour. What happens, in what order, and where the flow
branches or runs in parallel.

## What to include

One coherent flow with a single entry point and at least one end. Name actions with a
verb phrase (`Validate Order`, not `Order Validation`). Model the decisions a reader needs
to understand the path, not every conditional in the source.

## Rules

- Start at exactly one `initialNode` and finish at one or more `activityFinalNode`.
- `opaqueAction` is the ordinary step. Every action needs a way in and a way out.
- `controlFlow` is the only relationship between flow nodes.
- **Choice** is `decisionNode` (one way out is taken) rejoined by `mergeNode`.
  **Concurrency** is `forkNode` (every way out is taken) rejoined by `joinNode`.
  They are not interchangeable.
- Every branch out of a `decisionNode` carries a `guard` saying when it is taken. A
  branch out of a `forkNode` carries none — all of them run.
- `commentLink` attaches a `note` and nothing else.

## Choosing the node

| The source shows | Use |
| --- | --- |
| A step that does something | `opaqueAction` |
| An `if` that picks one path | `decisionNode` + `mergeNode` |
| Work that happens at the same time | `forkNode` + `joinNode` |
| The entry point | `initialNode` |
| A terminal outcome | `activityFinalNode` |

## Layout

The flow is laid out top to bottom. You do not author positions.
