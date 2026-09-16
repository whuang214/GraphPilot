# use_case_diagram — authoring guidance

A **UML Use Case Diagram**: who uses the system and what they can do with it. Goals, not
steps — use `activity_diagram` for how a goal is achieved.

## What to include

The actors outside the boundary and the goals they pursue inside it. Name a use case with
a verb phrase from the actor's point of view (`Book a Flight`, not `Booking Module`).

## Rules

- `subject` is the system boundary; place use cases inside it with `parentId`.
- Actors stay **outside** the subject. An actor with a `parentId` is a modelling mistake.
- `association` connects an `actor` to a `useCase`, and is the only relationship that
  crosses the boundary.
- `include` runs **base → included**: the base use case always performs the included one.
- `extend` runs **extension → base**: the extension conditionally adds to the base. Note
  the direction is the opposite of `include`.
- `generalization` is between two actors or two use cases.
- `commentLink` attaches a `note` and nothing else.

## Choosing the relationship

| The source shows | Use |
| --- | --- |
| An actor performs a goal | `association` |
| A goal always performs a shared sub-goal | `include` |
| An optional behaviour adds to a goal | `extend` |
| One actor or goal is a special case of another | `generalization` |

`include` and `extend` are the two most commonly reversed relationships in this notation.
Read the direction rule again before authoring either.

## Layout

Actors are placed beside the subject, use cases inside it. You do not author positions.
