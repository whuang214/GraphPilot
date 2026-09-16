# Generation

GraphPilot turns a **diagram draft** into a canonical diagram. The draft is authored by
the host — the IDE agent that already read the repository. GraphPilot materializes it
deterministically: no provider call, no readiness gate, no repair round.

```text
host reads source  →  authors draft  →  diagram_create  →  .gp.json + .svg + editor link
                                        ├─ validate draft
                                        ├─ materialize
                                        ├─ layout
                                        ├─ validate canonical
                                        ├─ persist
                                        └─ render
```

## The ownership boundary

This is the decision everything else follows from.

| Host owns — *semantics* | GraphPilot owns — *notation and mechanics* |
| --- | --- |
| Which elements exist | Canonical node/edge JSON shape |
| What relates to what | Complete relationship-end objects |
| Relationship kind | Direction rules, markers, line style |
| Labels, roles, multiplicities | Feature compartment normalization |
| Which features are visible | Provenance encoding |
| Evidence citations | Positions and sizes |
| Assumptions and uncertainties | Canonical validation |
| Presentation intent | Persistence, SVG, editor URL |

**Rule of thumb:** if getting it wrong is a *judgement* error, the host owns it. If getting
it wrong is a *notation* error, GraphPilot owns it.

A host says `composition, source: api-layer, target: application, sourceRole: apiLayer`.
It never authors the relationship-end object, the marker, or the dash pattern. That is
why a whole class of malformed-notation failure cannot occur.

## Authority is a field, not a pipeline

There is one path. What differs is what the draft claims:

| `authority` | Elements cite | Freshness checked |
| --- | --- | --- |
| `as_implemented` | evidence in the workspace | yes, per cited region |
| `conceptual` | nothing | no |

A conceptual diagram is the same document with no evidence and no freshness contract. It
is not a separate tool, schema, or code path.

## Read order

1. [`01-draft.md`](01-draft.md) — the draft contract and how to author one
2. [`02-materialization.md`](02-materialization.md) — draft → canonical, per diagram type
3. [`03-lifecycle.md`](03-lifecycle.md) — create, assurance, freshness, and what survives

## Ownership

| Topic | Owner |
| --- | --- |
| Draft document contract, per-type authoring guidance | [`01-draft.md`](01-draft.md) |
| Draft → logical → canonical mapping, layout, notation rules | [`02-materialization.md`](02-materialization.md) |
| `diagram_create`, assurance classes, evidence freshness, provenance | [`03-lifecycle.md`](03-lifecycle.md) |
| Canonical diagram field contract | [`../02-diagram-schemas/`](../02-diagram-schemas/README.md) |
| Canonical validation boundaries | [`../03-validation/`](../03-validation/README.md) |
| Rendering | [`../04-rendering.md`](../04-rendering.md) |
| Editing an existing diagram | [`../05-edit.md`](../05-edit/README.md) |
| Exact MCP arguments, results, errors | [`../../02-architecture/01-mcp-tools/`](../../02-architecture/01-mcp-tools/README.md) |

## Why it is built this way

The previous design sent host-authored *claims* to a generation model, gated them behind a
paid readiness reviewer, and repaired the model's notation mistakes. Across thirteen
measured runs it produced **no diagram** on a repository we controlled, failing at
readiness, the size gate, provider availability, and deterministic SysML validation.

The host is already a capable model with repository access. Asking a second model to
re-derive semantics the first one had established bought nothing and cost three to five
provider calls and several minutes per attempt. Findings:
[`retired-workflow-optimization.md`](../../07-history/retired-workflow-optimization.md).
