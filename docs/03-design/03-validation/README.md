# Validation

Two documents, because there are two documents to validate and they are checked by
different services, at different times, against different contracts.

| Document | Owner | When |
| --- | --- | --- |
| The **draft** a host submits | [`01-draft-validation.md`](01-draft-validation.md) | Before anything is written |
| The **canonical diagram** on disk | [`02-diagram-validation.md`](02-diagram-validation.md) | Before every write, and on demand |

## The difference that matters

**Draft validation asks whether the host got it right.** Every rule is one a host must be
able to predict, so every code appears in the authoring contract before it can be tripped.
Failures are refusals, and a refusal writes nothing.

**Diagram validation asks whether GraphPilot got it right.** A canonical diagram is built
by the materializer or saved by the editor, so a failure there is our defect or the
editor's — never something a host can act on. It is also the gate on the browser save
route, where the author is a person rather than an agent.

The two meet once: stage 8 of the create path runs canonical validation on a diagram the
materializer just built. If that fails, it raises rather than producing a finding, because
the draft was already accepted and the host has nothing left to fix.

## Related

- The draft contract itself — [`../01-generation/01-draft.md`](../01-generation/01-draft.md)
- What the materializer derives — [`../01-generation/02-materialization.md`](../01-generation/02-materialization.md)
- The canonical schema — [`../02-diagram-schemas/01-diagram-json-schema.md`](../02-diagram-schemas/01-diagram-json-schema.md)
- Error codes and retryability — [`../../02-architecture/01-mcp-tools/04-operation-errors.md`](../../02-architecture/01-mcp-tools/04-operation-errors.md)
