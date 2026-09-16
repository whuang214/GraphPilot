# Context-Backed Generation

> **Design authority:** This package defines the context branch of GraphPilot's final intended unified generation workflow: local evidence manifest → shared persisted request → readiness → grounded generation → reviewed candidate → provenance-validated canonical diagram. Runtime delivery status is tracked only on the [current-state board](../../05-delivery/01-current-state.md).

## Core boundaries

- `diagram_generation_workflow` is the one public routed workflow. Repository/source-truth requests use its context branch; conceptual/proposed/user-specified requests use its direct branch.
- JSON 1 remains the reusable repository evidence/claim artifact at `.graphpilot/context/evidence/repository.gp-evidence.json`.
- Context JSON 2 and direct requests use separate schemas but share `.graphpilot/requests/<diagramName>.gp-request.json` and `diagram_request_save`.
- Context readiness remains a mandatory four-layer, status-first pre-generation gate. It never becomes save-blocking canonical validation.
- Context generation requires exact selected-claim/accepted-assumption origins, then applies the shared reviewed semantic-candidate gate before layout and persistence.
- Canonical `.gp.json` keeps minimal request/manifest ownership and element origins. Complete quality/readiness detail lives in results; model/contract/example/review/layout/usage detail lives only in the optional digest-bound `.gp.trace.json` sidecar.

## Namespace-first contract identities

| Artifact | Schema identity | Kind |
| --- | --- | --- |
| Evidence manifest | `graphpilot.context.evidence-manifest.v1` | `evidenceManifest` |
| Context request (JSON 2) | `graphpilot.context.diagram-request.v1` | `contextDiagramRequest` |
| Transient resolved request | `graphpilot.context.resolved-request.v1` | `resolvedDiagramRequest` |
| Readiness input | `graphpilot.context.readiness-input.v1` | `contextReadinessInput` |
| Private readiness review | `graphpilot.context.readiness-review.v1` | `contextReadinessReview` |
| Final readiness result | `graphpilot.context.readiness-result.v1` | `contextReadinessResult` |
| Readiness repair input | `graphpilot.context.readiness-repair-input.v1` | `contextReadinessRepairInput` |
| Readiness diagnostics | `graphpilot.context.readiness-debug.v1` | `contextReadinessDebug` |
| Generation input | `graphpilot.context.generation-input.v1` | `contextGenerationInput` |
| Logical outputs | `graphpilot.context.logical-diagram.activity.v1`; `.use-case.v1`; `.bdd.v1` | `contextLogicalDiagram` |
| Generation repair input | `graphpilot.context.generation-repair-input.v1` | `contextGenerationRepairInput` |
| Semantic review input | `graphpilot.context.semantic-review-input.v1` | `contextSemanticReviewInput` |
| Private semantic review response | `graphpilot.context.semantic-review-response.v1` | `contextSemanticReviewResponse` |
| Semantic review-response repair input | `graphpilot.context.semantic-review-repair-input.v1` | `contextSemanticReviewRepairInput` |
| Deterministic semantic review result | `graphpilot.context.semantic-review-result.v1` | `contextSemanticReviewResult` |
| Semantic candidate repair input | `graphpilot.context.semantic-repair-input.v1` | `contextSemanticRepairInput` |
| Context generation example | `graphpilot.context.generation-example.v1` | `contextGenerationExample` |
| Generation result | `graphpilot.context.generation-result.v1` | `contextGenerationResult` |
| Compact cross-mode trace | `graphpilot.generation.trace.v1` | `generationTrace` |
| Cross-mode debug run/result | `graphpilot.generation.debug-run.v1`; `graphpilot.generation.debug-result.v1` | `generationDebugRun`; `generationDebugResult` |

The canonical diagram remains `graphpilot.diagram.v1` / `diagram`. Runtime enum values such as `use_case_diagram` retain underscores; compound words in contract identities use hyphens. Old pre-namespace IDs are unsupported rather than aliased or silently migrated.

## Managed storage and observability

```text
.graphpilot/
├── context/evidence/repository.gp-evidence.json
├── requests/<diagramName>.gp-request.json
├── diagrams/
│   ├── <diagramName>.gp.json
│   ├── <diagramName>.gp.trace.json          # optional; successful generation only
│   └── <diagramName>.svg
└── diagnostics/generation/<request-id>/<run-id>/  # optional numbered debug run
```

JSON 1, the saved request, and canonical diagram/origins retain authority. The compact trace is bound to the exact diagram digest and contains only model/contract/example/review/layout/usage summaries; it is never canonical authority or future model input. Numbered diagnostics may capture bounded stage packets for generated, blocked, or failed attempts, but remain optional non-authority observability. No legacy root-level diagram path, retired request subdirectory under `context/`, dual write, fallback, or silent migration is supported. Exact storage, result, trace, and diagnostics semantics are owned by [`05-generation-and-provenance.md`](05-generation-and-provenance.md).

## Read order and ownership

| Owner | Responsibility |
| --- | --- |
| [`01-workflow.md`](02-workflow.md) | Unified-workflow routing into the context branch, artifact lifecycle, actor boundaries, gap resolution, and result reporting |
| [`02-evidence-manifest.md`](03-evidence-manifest.md) | JSON 1 source fingerprint, evidence, claims, immutable versions, uncertainties, and validation invariants |
| [`03-diagram-request-context.md`](04-diagram-request-context.md) | JSON 2 request framing, shared request persistence/lifecycle, exact selections, uncertainty dispositions, accepted assumptions, decisions, and reconciliation |
| [`01-readiness/`](01-readiness/README.md) | Four-layer readiness review, namespace-first rubrics/results, typed findings/actions, policy, fixtures, calibration, and stability |
| [`05-generation-and-provenance.md`](05-generation-and-provenance.md) | Context population, final readiness, strict generation/repair, semantic review, provenance, results, canonical ownership, optional trace/debug, persistence, and rendering semantics |

## Related owners

- [MCP tools and unified host workflow](../../02-architecture/01-mcp-tools/README.md) own public names, arguments, transport results/errors, and prompt/tool discovery.
- [Backend architecture](../../02-architecture/03-backend.md) owns runtime service and storage boundaries.
- [Canonical diagram schema](../03-diagram-json-schema.md) owns the additive diagram ownership/origin shape.
- [Validation](../05-validation.md), [generation](../07-generation.md), and [rendering](../06-rendering.md) own shared canonical-diagram behavior.
- [Training fixtures](../09-answer-key-generation.md) own the exact context-native examples and leakage boundary.
- [Evaluation](../../07-history/retired-evaluation-and-doe-design.md) owns independent capture, matching, judging, gates, reports, calibration, and hidden-gold certification.
- [Design decisions](../../05-delivery/04-decisions.md) is the only active decision/open-question index.
- Repository agents start with [`AGENTS.md`](../../../AGENTS.md); the complete documentation index is [`docs/README.md`](../../README.md).
