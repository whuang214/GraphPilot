# Slice 10: Context Generation and Workflow

## Purpose

Implement readiness-gated context-backed generation, expose symmetric direct/context generation tools, and
register the public host workflow prompt.

## Background

All context, readiness, provenance, and shared generation dependencies now exist. This slice composes them; it
does not duplicate their contracts in MCP handlers.

## Design

`ContextDiagramGenerationService` loads canonical context by path, runs mandatory final readiness through
`ContextReadinessService`, resolves transient input through `GenerationContextResolver`, invokes internal shared
generation phases, validates through `ContextProvenanceValidator`, rechecks context stability, persists, renders,
and returns typed `generated`/`blocked`/`partial_success` outcomes. `PromptDiagramGenerationService` remains the
separate direct-mode orchestrator, while its public tool is renamed atomically to `diagram_generate_from_prompt`
with no alias.

## Plan Audit

- **Application contract:** add frozen policy/projection/target/outcome DTOs under
  `generation_context_contract.py` and one request-scoped `ContextDiagramGenerationService`. Actual failures raise
  one typed context-generation operation error carrying stable code/message/retryability/details; a successfully
  executed but unaccepted final readiness gate returns `blocked`, and only a post-JSON render failure returns
  `partial_success`.
- **Attempt policy:** implement the already-frozen three exact modes—no score thresholds or environment-selected
  policy. `require_ready` accepts only `ready`; `allow_warnings` accepts only `ready_with_warnings` when reviewed
  request/manifest digests match and acknowledged IDs equal every current warning ID; `force_with_gaps` accepts only
  `needs_context` when every blocker is overrideable, digests match, `acceptedBy` is `user`, and acknowledged IDs
  equal every current blocker ID. Malformed policy is `invalid_arguments`; a well-formed policy that the final result
  does not satisfy returns `blocked` with full readiness and `readiness_blocked`.
- **Single baseline:** load validated bound JSON 2/JSON 1 once through `ContextPersistenceService`; add a
  behavior-preserving readiness entry point that accepts the same `BoundContextDocuments`. Preflight target,
  resolve exact generation context, build/check the generator projection, and verify generator configuration before
  spending a reviewer call; then run mandatory final readiness over that baseline. Immediately before persistence,
  reload both artifacts and recheck their exact digests plus target
  identity/revision; changed context/target writes nothing and is never automatically rerun.
- **Target ownership:** JSON 2 `diagramName` selects one exact canonical target. No JSON/rendered siblings permits
  exclusive creation; existing canonical JSON permits regeneration only when
  `metadata.generationContext.request.id` equals the current `requestId`; another/missing owner or JSON-absent
  orphan SVG/PNG returns `diagram_name_conflict` with exact target fields. Use optimistic revisions/exclusive create,
  not lockfiles or a database. The host may intentionally move a request to a new name after resolving a conflict.
- **Validated publication:** add an exact exclusive-create method to the existing validated persistence funnel;
  same-request regeneration uses validated save after the target recheck. On regeneration, remove old SVG and PNG
  after all preconditions pass but before JSON replacement; cleanup failure aborts before the new JSON write. Then
  persist canonical JSON atomically and render SVG. Render failure leaves valid JSON, no stale SVG/PNG, and returns
  retryable partial success; direct prompt rendering is migrated to the same non-error partial-success contract.
- **Generator projection:** build transient `graphpilot.context-generation-input.v1` from request/scope/dispositions,
  exact selected claim ID/version/kind/statement/payload/applicability/role/reason/support basis/derivation,
  assumptions, decisions, type vocabulary/rules, exact claim/assumption allowlists, prompt/schema versions, and
  bounded structural examples. Exclude resolved evidence records/summaries, unselected claims, readiness findings,
  source, discovery output, prompts/raw responses, credentials, and local absolute source paths. Compact canonical
  bytes use a positive `GRAPHPILOT_CONTEXT_GENERATION_INPUT_LIMIT` (default `65536`) after fixed reserves; overflow
  returns existing `context_too_large` details with phase `generation_projection` and stable top contributors.
- **Strict logical output:** derive a separate `graphpilot.logical-diagram.context.v1` strict schema from the full
  direct logical vocabulary and require strict Slice 08 origin on every node/edge. Runtime claim/assumption/schema
  allowlists remain prompt instructions plus deterministic `ContextProvenanceValidator` checks rather than dynamic
  schema enums. Direct `LOGICAL_SCHEMA` stays origin-free and cannot masquerade as grounded output.
- **Prompt and repair:** add external `context-generation.md` and `context-generation-repair.md` assets. The initial
  call gets only the bounded generator projection and fixed GraphPilot assets. One bounded repair round receives
  the identical projection, previous logical JSON, canonical/structural/provenance issues, and no new facts; final
  canonical or provenance failure maps to its exact stage/code and writes nothing. Readiness is not rerun inside
  repair.
- **Trace:** assemble the exact Slice 08 context metadata from immutable loaded paths/digests, complete selected
  refs, final readiness, exact accepted policy receipt, generator identifiers, and complete copied assumptions/
  decisions. Azure supplies element origins only; it never authors trace records. Pipeline canonical validation and
  provenance validation both pass before stability/persistence.
- **Diagnostics sequencing:** keep the generation tool's optional final-readiness diagnostics integration for Slice
  11, which already owns diagnostics hardening and simultaneous post-stage warning behavior. Slice 10 does not
  advertise or ignore a diagnostics argument; standalone readiness diagnostics remain fully available and the host
  prompt uses them before generation when requested.
- **MCP symmetry:** atomically rename `diagram_generate` to `diagram_generate_from_prompt` with no alias, add
  `diagram_generate_from_context`, and register `context_backed_generation_workflow` through `@mcp.prompt()` with
  exact `workspaceDir`, verbatim `request`, optional `interactionPreference`, and optional
  `persistReadinessDebug`. Update all server globals, help text, tests, smoke calls, READMEs, and active references.
- **Transport:** direct and context complete success return `outcome: generated`; saved JSON plus failed SVG returns
  `outcome: partial_success`, nullable `svgPath`, and `warning: OperationProblem`, all with MCP `isError: false`.
  Context gate refusal returns `blocker: OperationProblem` plus complete readiness with `isError: false`; only
  actual operation failures return `error: OperationProblem` and `isError: true`. Add `readiness_blocked` to the
  shared retryability registry and preserve exact conflict/context/validation/provenance detail fields.
- **Verification:** fixed fake-LLM service tests cover all policy modes, malformed/stale acceptance, zero generator
  calls before accepted final readiness, projection exclusions/budget, exact context schema/origins, one repair,
  provenance exhaustion, target create/regenerate/conflicts/races, context recheck, trace, artifact cleanup, render
  partial success, and direct behavior. MCP contract tests cover both tools/prompt and every `isError` class; stdio
  smoke proves prompt discovery/rendering, old-name absence, renamed direct generation, and deterministic blocked
  context generation without requiring Azure.

## Included Work

- Add `ContextDiagramGenerationService` as the context-generation application orchestrator with bounded attempt policy.
- Add `diagram_generate_from_context` and coordinate the direct-generation rename.
- Register `context_backed_generation_workflow` with adaptive consultation and typed-action execution.
- Preserve final readiness, deterministic diagram/provenance validation, and context-digest checks.
- Implement `error`/`blocker`/`warning` `OperationProblem` composition, warning/override UX, generation failure
  feedback, and render partial success with correct MCP `isError` values.
- Update all clients, tests, smoke flows, docs, and prompt references atomically.

## Not In Scope

- Semantic-review bypass, direct-mode fallback labeled as grounded, or hidden mutation.
- A browser context-generation flow.
- Multi-provider routing or unbounded retries.

## Target Areas

- `backend/services/generation/context_diagram_generation_service.py`
- `backend/services/generation/prompt_diagram_generation_service.py` and internal shared phases
- `backend/mcp_server/`
- backend prompt assets and MCP tests/smoke test
- active MCP/generation architecture owners

## Exit Criteria

- Context generation never invokes the generator before final readiness allows it.
- Direct and context modes cannot masquerade as each other.
- Rename and new tool contracts are synchronized across code, tests, smoke clients, and docs.
- Direct/context generation return exact `generated`/`partial_success`/`error` contracts; context generation also
  returns `blocked`; `error` alone sets MCP `isError: true`, while `blocker`/`warning` reuse `OperationProblem`.
- Full backend tests and deterministic smoke coverage pass.

## Previous Slice

- [`09-shared-generation-phases.md`](09-shared-generation-phases.md)

## Next Slice

- [`11-diagnostics-and-release-gate.md`](11-diagnostics-and-release-gate.md)

## Outcome

**Implemented.** Added the request-scoped context-generation orchestrator, frozen policy/projection/outcome DTOs,
mandatory final readiness over one loaded context baseline, bounded evidence-free generator projection, strict
origin-required logical output, one grounded repair, deterministic provenance/stability checks, exact target
ownership and exclusive creation, identity-preserving regeneration, stale SVG/PNG cleanup, canonical trace
assembly, and generated/blocked/partial-success delivery. Direct generation now uses the same post-persistence
render partial-success semantics.

**MCP and workflow.** Renamed the direct tool atomically to `diagram_generate_from_prompt` with no alias, added
`diagram_generate_from_context`, and registered the externalized `context_backed_generation_workflow` prompt.
Handlers return the specified `error`/`blocker`/`warning` shapes and MCP `isError` classes; unit and real-stdio
coverage proves both tool names, old-name absence, prompt discovery/rendering, and offline-safe failures.

**Verification.** `uv run python manage.py test` passes 617 backend tests with 3 skips; `uv run python
mcp_server/smoke_test.py` passes every real-stdio check; `git diff --check` passes. Tests remain offline and use
injected fake reviewer/generator clients.

**Deviations.** Generation-final-gate diagnostics transport remains intentionally deferred to Slice 11 rather
than advertising an ignored argument. Azure's strict structured-output subset does not support the origin
cardinality, uniqueness, identifier-pattern, or length keywords, so the strict schema owns exact required
shape/types while the existing deterministic provenance gate enforces those frozen constraints after every
candidate; a regression guard rejects unsupported strict-schema keywords.

**Follow-up.** Slice 11 adds final-gate diagnostics and completes calibration, repeated-run stability,
compatibility, and release proof.
