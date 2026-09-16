# Layer 2/3 Readiness — Agent Navigation

> **Status:** Historical readiness-design snapshot. The contract was promoted to the active
> [`01-readiness/`](../../../03-design/01-context-generation/01-readiness/README.md)
> package; runtime implementation has not started.
>
> **Historical agent entry point only.** This README navigates the original reviewed sources. Use the active
> package for current intended behavior.

## Read order

1. [`01-readiness-reviewer.md`](01-readiness-reviewer.md) — overall JSON flow, four review layers, status-first
   gate, bounded host loop, and override architecture.
2. [`02-policy-and-calculation.md`](02-policy-and-calculation.md) — common schema/versioning, applicability,
   rating anchors, assumption cap, score/rounding/N/A treatment, and exact status calculation.
3. [`03-reviewer-json.md`](03-reviewer-json.md) — finding/action registry, the private Layer 2/3 review JSON,
   and deterministic validation.
4. [`rubrics/overview.md`](rubrics/overview.md), then the selected type's machine contract + explanation:
   - [`rubrics/activity/rubric.json`](rubrics/activity/rubric.json) + [`rubrics/activity/rubric.md`](rubrics/activity/rubric.md)
   - [`rubrics/use-case/rubric.json`](rubrics/use-case/rubric.json) + [`rubrics/use-case/rubric.md`](rubrics/use-case/rubric.md)
   - [`rubrics/bdd/rubric.json`](rubrics/bdd/rubric.json) + [`rubrics/bdd/rubric.md`](rubrics/bdd/rubric.md)
5. [`04-results.md`](04-results.md) — final backend-to-host readiness result JSON and field contract.
6. [`05-fixtures-calibration-and-stability.md`](05-fixtures-calibration-and-stability.md) — fixtures,
   calibration targets, and repeated-run acceptance.

## Ownership map

| Topic | Single owner |
| --- | --- |
| Overall JSON flow, four layers, status-first gate, bounded loop, override architecture | `01-readiness-reviewer.md` |
| Common rubric schema/versioning, applicability, anchors, weights, assumption cap, score, rounding, N/A, status algorithm | `02-policy-and-calculation.md` |
| Finding categories/codes/severity/overrideability/actions, private review JSON, structured validation | `03-reviewer-json.md` |
| Overall rubric selection/navigation | `rubrics/overview.md` |
| Exact activity rubric data / explanation | `rubrics/activity/rubric.json` / `rubrics/activity/rubric.md` |
| Exact use-case rubric data / explanation | `rubrics/use-case/rubric.json` / `rubrics/use-case/rubric.md` |
| Exact BDD rubric data / explanation | `rubrics/bdd/rubric.json` / `rubrics/bdd/rubric.md` |
| Final backend-to-host readiness result JSON and fields | `04-results.md` |
| Fixtures, human labels, calibration, release targets, repeated-run stability | `05-fixtures-calibration-and-stability.md` |
| Context-backed final-gate consumption and canonical trace | [`../06-context-backed-generation-and-provenance.md`](../06-context-backed-generation-and-provenance.md) |
| Exact MCP arguments/results/errors and host/client UX | [`../07-mcp-prompts-and-tool-contracts.md`](../07-mcp-prompts-and-tool-contracts.md) |
| Implementation slicing and active-doc promotion | [`../08-implementation-and-promotion.md`](../08-implementation-and-promotion.md) |

## Agent rules

- Use the active [`01-readiness/`](../../../03-design/01-context-generation/01-readiness/README.md)
  owner before changing readiness behavior.
- Preserve this package as historical rationale; do not synchronize it with implementation discoveries.
- Correct historical links here only when needed, and keep live status in the active delivery board.
