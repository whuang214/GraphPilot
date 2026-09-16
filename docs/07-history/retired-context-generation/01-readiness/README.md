# Context Readiness

This README owns navigation and topic ownership only; the linked files own the contracts.

## Contract boundary

Readiness uses namespace-first context identities: `graphpilot.context.readiness-input.v1`, `graphpilot.context.readiness-review.v1`, `graphpilot.context.readiness-repair-input.v1`, `graphpilot.context.readiness-result.v1`, and `graphpilot.context.readiness-debug.v1`. The three normative rubric documents use `graphpilot.context.readiness-rubric.v1`, per-type `graphpilot.context.readiness-rubric.<type>.v1` identities, and `graphpilot.context.readiness-rating.v1`.

The final readiness result is complete and host-actionable but is not embedded in JSON 1, JSON 2, or canonical diagram metadata. Context generation returns the complete result when final readiness blocks, a compact accepted-readiness summary when it proceeds, and may record only a compact rubric/status/score summary in the optional digest-bound generation trace. Readiness debug output remains optional non-authority diagnostics.

## Read order

1. [`01-readiness-reviewer.md`](02-reviewer.md) — JSON flow, four review layers, status-first gate,
   bounded host loop, and override boundary.
2. [`02-policy-and-calculation.md`](03-policy-and-calculation.md) — common schema/versioning, applicability,
   rating anchors, assumption cap, score/rounding/N/A treatment, finding order, and status calculation.
3. [`03-reviewer-json.md`](04-reviewer-json.md) — finding/action registries, private Layer 2/3 review JSON, typed
   actions, and deterministic validation.
4. [`rubrics/overview.md`](01-rubrics/overview.md), then the selected type's normative machine contract and
   explanation:
   - [`rubrics/activity/rubric.json`](01-rubrics/activity/rubric.json) + [`rubrics/activity/rubric.md`](01-rubrics/activity/rubric.md)
   - [`rubrics/use-case/rubric.json`](01-rubrics/use-case/rubric.json) + [`rubrics/use-case/rubric.md`](01-rubrics/use-case/rubric.md)
   - [`rubrics/bdd/rubric.json`](01-rubrics/bdd/rubric.json) + [`rubrics/bdd/rubric.md`](01-rubrics/bdd/rubric.md)
5. [`04-results.md`](05-results.md) — final backend-to-host readiness result JSON and field contract.
6. [`05-fixtures-calibration-and-stability.md`](06-fixtures-calibration-and-stability.md) — fixtures,
   calibration targets, release gates, and repeated-run stability.

## Ownership

| Topic | Owner |
| --- | --- |
| Four-layer architecture, reviewer projection, status-first gate, bounded loop, override boundary | [`01-readiness-reviewer.md`](02-reviewer.md) |
| Common rubric policy, applicability, anchors, weights, assumption cap, score, rounding, finding order, status | [`02-policy-and-calculation.md`](03-policy-and-calculation.md) |
| Finding codes/policy, typed actions, private reviewer JSON, structured validation | [`03-reviewer-json.md`](04-reviewer-json.md) |
| Per-type facet definitions and rubric navigation | [`rubrics/overview.md`](01-rubrics/overview.md) and matching `rubrics/<type>/rubric.json` / `rubric.md` |
| Final `contextReadinessResult` JSON and invariants | [`04-results.md`](05-results.md) |
| Fixtures, human labels, calibration, release targets, repeated-run stability | [`05-fixtures-calibration-and-stability.md`](06-fixtures-calibration-and-stability.md) |
| End-to-end artifact flow | [`../01-workflow.md`](../02-workflow.md) |
| JSON 1 and JSON 2 | [`../02-evidence-manifest.md`](../03-evidence-manifest.md) and [`../03-diagram-request-context.md`](../04-diagram-request-context.md) |
| Final-gate consumption, grounded generation, provenance, and trace | [`../05-generation-and-provenance.md`](../05-generation-and-provenance.md) |
| Exact MCP arguments, results, and errors | [`../../../01-architecture/03-mcp-tools/02-context-tools.md`](../../../02-architecture/01-mcp-tools/02-context-tools.md) |
| Host orchestration, typed-action execution, warning/override UX | [`../../../01-architecture/03-mcp-tools/README.md`](../../../02-architecture/01-mcp-tools/README.md) |

## Maintenance rules

- Change the single owner above and link from other docs rather than duplicating detail.
- A rubric change must not silently change JSON 1 or JSON 2.
- Keep MCP transport and host UX in the MCP package; keep readiness semantics here.
