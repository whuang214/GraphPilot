# Group: Context-Backed Generation (Epic 3 extension)

> **Extension of Epic 3.** Epic 3's original prompt-generation and rendering core remains complete. This
> group adds evidence-backed context, readiness review, provenance, and the corresponding MCP workflow as
> a separately tracked extension.

## Goal

Add a local-first, evidence-backed generation path that turns repository observations into reusable claims,
binds selected claims and accepted assumptions to one diagram request, checks semantic readiness, and generates
a canonical diagram with bounded provenance while preserving direct prompt generation.

## User Scenario

A user asks an IDE agent to diagram a repository-backed behavior or structure. The host gathers and validates
repository evidence, prepares a per-diagram request context, improves it through readiness findings, and calls
GraphPilot's context-backed generator. GraphPilot performs a final readiness gate, generates and validates the
canonical diagram, persists it with trace metadata, renders it, and returns typed results without inventing
unsupported facts or mutating context silently.

## Scope

- Active-design promotion of the reviewed evidence-context research contracts.
- JSON 1 evidence manifest and JSON 2 diagram request-context machine contracts.
- Four-layer readiness review, exact rubrics, deterministic policy, findings, actions, and final result.
- Context artifact paths, path safety, atomic replacement, fingerprints, and digest-bound concurrency.
- Context population, grounded generation, element origins, canonical trace, and provenance validation.
- Evidence, request, readiness, direct-generation, and context-generation MCP tools.
- One public host workflow prompt with adaptive consultation and a bounded improve-before-ask loop.
- Offline tests, semantic calibration, repeated-run stability, and opt-in safe diagnostics.

## Out of Scope

- Replacing direct prompt generation.
- Merging context readiness into canonical diagram validation.
- A browser UI for gathering or editing JSON 1/JSON 2, readiness overrides, or evidence inspection.
- A database, authentication, remote context service, RAG retrieval, or multi-provider routing.
- Silent migration or deletion of existing flat `.graphpilot/` files.
- Persisting prompts, raw model responses, hidden reasoning, source dumps, secrets, or discovery-tool graphs.

## Architecture Baseline

- `WorkspaceStorageService` is the one low-level workspace-contained `.graphpilot` path/read/write owner;
  context lifecycle and concurrency policy remain outside it.
- Existing `DiagramSchemaService` and the formerly planned separate context loader become one `SchemaRegistry`
  because multiple versioned schema consumers now make loading/caching a demonstrated shared concern.
- Context readiness, canonical diagram validation, and persistence validation remain separate trust boundaries.
- `ReadinessRubricService`, `ReadinessPolicyService`, and `ContextReadinessService` live together under
  `services/readiness/`; shared provider clients and prompt loading move to neutral `services/llm/` when
  readiness becomes their second consumer; generation-specific resolution/provenance remain focused internal
  collaborators.
- Existing renderer/frontend guards and API/MCP protocol adapters remain separate.
- Shared generation phases are extracted only when context generation becomes the second consumer.
- Further refactoring requires demonstrated duplication, profiling evidence, or a blocked workflow.

## Slice Plan

1. [`01-active-design-promotion.md`](01-active-design-promotion.md) — promote research into active owners,
   establish this group, reconcile architecture, and close the research workspace as historical. **Complete, verified, and user-approved.**
2. [`02-readiness-rubric-and-policy.md`](02-readiness-rubric-and-policy.md) — add exact rubric assets and pure
   deterministic readiness policy/calculation. **Complete.**
3. [`03-evidence-and-request-schemas.md`](03-evidence-and-request-schemas.md) — define JSON 1/JSON 2 machine
   schemas, cached loading, validation, and fixtures. **Complete.**
4. [`04-context-persistence.md`](04-context-persistence.md) — extend `WorkspaceStorageService` and add validated,
   digest-bound context persistence and canonical paths. **Complete.**
5. [`05-readiness-preflight-and-projection.md`](05-readiness-preflight-and-projection.md) — create the
   readiness package, move existing rubric/policy services, and implement Layer 1 plus bounded projection.
   **Complete.**
6. [`06-semantic-reviewer.md`](06-semantic-reviewer.md) — move shared LLM infrastructure to `services/llm/`,
   then add the injected semantic reviewer and final readiness assembly. **Complete.**
7. [`07-context-mcp-tools.md`](07-context-mcp-tools.md) — expose evidence, request, and readiness operations as
   thin MCP tools. **Complete.**
8. [`08-context-population-and-provenance.md`](08-context-population-and-provenance.md) — resolve context,
   validate provenance, and add canonical trace/type parity. **Complete.**
9. [`09-shared-generation-phases.md`](09-shared-generation-phases.md) — extract reusable direct/context
   generation phases without behavior changes. **Complete.**
10. [`10-context-generation-and-workflow.md`](10-context-generation-and-workflow.md) — add context generation,
    generation-tool symmetry, and the public host workflow. **Complete.**
11. [`11-diagnostics-and-release-gate.md`](11-diagnostics-and-release-gate.md) — harden safe diagnostics and add
    calibration, stability, compatibility, and release proof. **Implemented and offline-verified; live certification not run.**
12. [`12-workflow-client-compatibility.md`](12-workflow-client-compatibility.md) — expose the same public context
    workflow instructions through prompt and tool namespaces for tools-only MCP clients. **Complete, audited, and verified.**
13. [`13-context-performance-and-recovery.md`](13-context-performance-and-recovery.md) — reduce avoidable host/provider work,
    add stage-correct timeout recovery, and measure complete provider usage. **Complete, audited, and verified; one warm live attempt blocked at final readiness without generation.**
14. [`14-readiness-effort-evaluation.md`](14-readiness-effort-evaluation.md) — audit whole-workflow performance and add one
    operator-controlled reasoning-effort/final-readiness proof. **Complete, audited, and verified; medium proof was faster but not semantically promoted.**
15. [`15-full-effort-evaluation.md`](15-full-effort-evaluation.md) — audit the complete cold/warm user-visible context
    workflow, with the frozen high/medium readiness and reviewed-generation matrix retained as one subordinate experiment.
    **Offline audit complete; authorized Stage B stopped at 4/144 calls, no cells rerun, Stage C blocked; terminal accounting fixed and verified.**

Slice numbers are local to this group. Each slice updates active design owners when implementation evidence
changes the plan and records deviations and verification in its `## Outcome`.

## Dependencies

- Epic 3's existing generation, validation, persistence, layout, rendering, prompt, and fake-LLM seams.
- The reviewed transition plan in
  [`08-implementation-and-promotion.md`](../../../../06-research/evidence-based-diagram-context/08-implementation-and-promotion.md).
- The active feature and MCP packages created by slice `01`.

## Acceptance Criteria

- Direct prompt generation remains available and cannot masquerade as context-backed generation.
- Context artifacts and diagrams use path-safe, validated, atomic local persistence with explicit concurrency.
- Readiness is status-authoritative, deterministically calculated, bounded, and independently calibrated.
- Context-backed generation always performs final readiness and deterministic diagram/provenance validation.
- Every active contract has one owner; research is historical after promotion.
- Backend tests remain offline by default; live-provider checks are opt-in.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 3 goal and complete slice index.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — single live delivery-status board.
- [`08 transition plan`](../../../../06-research/evidence-based-diagram-context/08-implementation-and-promotion.md)
  — approved promotion and implementation map.
