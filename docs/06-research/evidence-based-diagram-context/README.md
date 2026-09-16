# Evidence-Based Diagram Context

This is the historical research workspace that produced GraphPilot's planned repository-evidence workflow for
trustworthy diagram generation. Its accepted contracts were promoted into active owners by Epic 3 context-backed
generation Slice 01; runtime implementation has **not** started.

> **Historical authority warning:** do not implement from this folder or treat it as current product behavior.
> Current intended feature behavior lives in
> [`docs/02-design-and-features/08-context-backed-generation/`](../../03-design/01-context-generation/README.md),
> public MCP contracts live in [`docs/01-architecture/03-mcp-tools/`](../../02-architecture/01-mcp-tools/README.md),
> decisions live in [`decision-decisions.md`](../../05-delivery/04-decisions.md), and delivery
> status lives in [`epics/00-current-state.md`](../../05-delivery/01-current-state.md).

## Read order

1. [`01-workflows-and-prompts.md`](01-workflows-and-prompts.md) — workflow and artifact-lifecycle map.
2. [`02-evidence-manifest.md`](02-evidence-manifest.md) — JSON 1 evidence/claim/uncertainty contract.
3. [`03-diagram-request-context.md`](03-diagram-request-context.md) — JSON 2 request-context contract.
4. [`05-readiness/README.md`](05-readiness/README.md) — readiness-package navigation and ownership.
5. [`06-context-backed-generation-and-provenance.md`](06-context-backed-generation-and-provenance.md) —
   generation population, provenance, trace, persistence, and rendering.
6. [`07-mcp-prompts-and-tool-contracts.md`](07-mcp-prompts-and-tool-contracts.md) — MCP surface, host prompt,
   transport, attempt policy, and diagnostics.
7. [`08-implementation-and-promotion.md`](08-implementation-and-promotion.md) — research-to-implementation and
   active-doc promotion planning; not implementation authority.
8. [`00-original-handoff.md`](00-original-handoff.md) — historical baseline only; audited numbered owners win.

Start with repository [`AGENTS.md`](../../../AGENTS.md) and the canonical [`docs` index](../../README.md) before
using this package.

## Historical ownership map

| Historical topic | Research snapshot | Active owner |
| --- | --- | --- |
| Overall workflow and lifecycle | [`01-workflows-and-prompts.md`](01-workflows-and-prompts.md) | [`01-workflow.md`](../../03-design/01-context-generation/02-workflow.md) |
| JSON 1 evidence manifest | [`02-evidence-manifest.md`](02-evidence-manifest.md) | [`02-evidence-manifest.md`](../../03-design/01-context-generation/03-evidence-manifest.md) |
| JSON 2 request context | [`03-diagram-request-context.md`](03-diagram-request-context.md) | [`03-diagram-request-context.md`](../../03-design/01-context-generation/04-diagram-request-context.md) |
| Readiness, rubrics, results, and calibration | [`05-readiness/README.md`](05-readiness/README.md) | [`01-readiness/`](../../03-design/01-context-generation/01-readiness/README.md) |
| Context generation and provenance | [`06-context-backed-generation-and-provenance.md`](06-context-backed-generation-and-provenance.md) | [`05-generation-and-provenance.md`](../../03-design/01-context-generation/05-generation-and-provenance.md) |
| MCP tools and host workflow | [`07-mcp-prompts-and-tool-contracts.md`](07-mcp-prompts-and-tool-contracts.md) | [`03-mcp-tools/`](../../02-architecture/01-mcp-tools/README.md) |
| Promotion record | [`08-implementation-and-promotion.md`](08-implementation-and-promotion.md) | Epic 3 [`04-context-backed-generation/`](../../07-history/epics/03-mcp-generation-and-wrappers/04-context-backed-generation/00-group.md) |
| Original proposal | [`00-original-handoff.md`](00-original-handoff.md) | Historical only |

## Critical boundaries

- JSON 1 owns reusable supported facts; JSON 2 owns one diagram's intent, selections, assumptions, and
  decisions. Neither owns final UML/SysML topology.
- The backend remains responsible for semantic mapping, deterministic validation, layout, persistence, and
  rendering; detailed behavior belongs to the numbered owner above.
- Extraction provenance is out of JSON 1 v1. Discovery/search tools are host-only accelerators and their
  output is not evidence until the host verifies and records supported source observations.
- Research files do not override active architecture, feature design, decisions, API/MCP contracts, or live
  delivery status.

## Agent rules

- Use the active owner column above for all current design and implementation work.
- Change this folder only to correct historical links or explain the original rationale; never synchronize it
  forward with later implementation discoveries.
- Keep live product status only in
  [`epics/00-current-state.md`](../../05-delivery/01-current-state.md).
- Preserve unrelated working-tree changes and do not rewrite the historical handoff as current authority.
