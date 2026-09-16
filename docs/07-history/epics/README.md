# Epics

This directory organizes GraphPilot delivery into stable epic definitions and executable slice documents.
Live status is deliberately excluded from this README and belongs only in
[`00-current-state.md`](../../05-delivery/01-current-state.md).

## Read order

1. [`00-current-state.md`](../../05-delivery/01-current-state.md)
2. the relevant epic's `00-epic.md`
3. that epic's numbered phase-group overview when present
4. the relevant numbered slice document

## Ownership map

| Topic | Owner |
| --- | --- |
| Live cross-epic status and next work | [`00-current-state.md`](../../05-delivery/01-current-state.md) |
| Stable epic goal, scope, acceptance criteria, and slice plan | each epic's `00-epic.md` |
| Slice execution detail and outcome history | each numbered slice document |
| Design and intended behavior | [`docs/03-design/`](../../03-design/) |
| Epic/slice document shapes and delivery workflow | [`.devin/rules/graphpilot.md`](../../../.devin/rules/graphpilot.md#epic-and-slice-document-shapes) |

## Directory and naming conventions

- Each epic has one numbered folder and one authoritative `00-epic.md`; do not create parallel flat epic
  definitions.
- Numbered phase-group folders organize related slices. A folded or independently scoped group may include a
  concise `00-group.md` entry point.
- An approved high-level program group may define roadmap blocks and a shared contract before detailed slices; blocks state
  questions, ordering, and gates but do not substitute for audited implementation slice plans or carry live status.
- Slice files are numbered within their group and use short kebab-case names. Slice titles follow the workflow
  rule linked above.
- Cross-group and cross-epic links are relative. Each slice links to its previous and next slice where useful.
- Keep each epic's `Slice Plan` synchronized with its actual slice files; code-first/backfilled slices cite the
  implementing commit.
- Design docs win when a slice and active design disagree; update the active design owner in the same change.

## Epic entry points

- [`01-local-diagram-foundation/00-epic.md`](01-local-diagram-foundation/00-epic.md)
- [`02-react-editor-and-export/00-epic.md`](02-react-editor-and-export/00-epic.md)
  - [`08-editor-connectors-and-audit/00-group.md`](02-react-editor-and-export/08-editor-connectors-and-audit/00-group.md) — connector tools, route modes, and frontend audit follow-on
- [`03-mcp-generation-and-wrappers/00-epic.md`](03-mcp-generation-and-wrappers/00-epic.md)
  - [`06-workflow-reliability-and-optimization/00-group.md`](03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/00-group.md) — approved high-level workflow audit, reliability, optimization, validation, and promotion roadmap
  - [`06-workflow-reliability-and-optimization/01-workflow-audit-and-measurement/00-group.md`](03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/01-workflow-audit-and-measurement/00-group.md) — Block 1 executable Slice 01–06 audit and fresh-baseline plan
  - [`06-workflow-reliability-and-optimization/02-repository-architecture-and-enablement/00-group.md`](03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/02-repository-architecture-and-enablement/00-group.md) — Block 2 repository inventory, namespace waves, and parity plan
  - [`06-workflow-reliability-and-optimization/03-readiness-diagnosis-and-architecture/00-group.md`](03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/03-readiness-diagnosis-and-architecture/00-group.md) — Block 3 provider-free lifecycle, causal diagnosis, stale-reference cleanup, and audited root transition
  - [`06-workflow-reliability-and-optimization/04-readiness-correction-and-proof/00-group.md`](03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/04-readiness-correction-and-proof/00-group.md) — Block 4 focused contract correction, offline proof, and bounded live exit proof
  - [`06-workflow-reliability-and-optimization/05-complete-live-anchor-and-reaudit/00-group.md`](03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/05-complete-live-anchor-and-reaudit/00-group.md) — Block 5 human-approved live anchor, visible editor proof, and current workflow re-audit
- [`04-mcp-edit-workflow-and-hardening/00-epic.md`](04-mcp-edit-workflow-and-hardening/00-epic.md)
- [`05-optional-rag-example-library/00-epic.md`](05-optional-rag-example-library/00-epic.md)

Use the [current-state board](../../05-delivery/01-current-state.md), not this folder list, to determine what is active, complete,
blocked, or next.
