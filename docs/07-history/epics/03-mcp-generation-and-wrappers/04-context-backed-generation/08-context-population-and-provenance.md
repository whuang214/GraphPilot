# Slice 08: Context Population and Provenance

## Purpose

Resolve canonical JSON 1/JSON 2 into the transient prepared generation input and add deterministic element
origins, provenance validation, and canonical trace metadata.

## Background

This slice bridges persisted context and generation without assigning final diagram topology or semantic types
during evidence gathering.

## Design

`GenerationContextResolver` is a focused internal generation component that resolves selected claim versions,
uncertainty dispositions, accepted assumptions, and decisions without mutating canonical context.
`ContextProvenanceValidator` is a focused deterministic validator for evidence-backed semantics, accepted
assumptions, and schema-required notation scaffolding. Neither is an application-level service; canonical trace
fields remain optional and backward-compatible.

## Plan Audit

- **Contract boundary:** add one data-only `generation_context_contract.py`. `GenerationContextContributor`
  carries `path`/conservative `estimatedTokens`; `ResolvedGenerationContext` carries the resolved document,
  canonical bytes/digest, loaded request/manifest values, total estimate, top contributors, selected-claim
  allowlist, and accepted-assumption allowlist. `ProvenanceValidationIssue` is exact `code/message/path`, and
  `ProvenanceValidationResult` is `valid` plus an immutable issue tuple. Do not reuse canonical
  `ValidationResult`: provenance is a separate generation acceptance boundary, and all v1 findings are errors.
- **Resolver input:** `GenerationContextResolver.resolve()` consumes already validated `BoundContextDocuments`;
  `ContextPersistenceService` remains the only loader/binding owner. Slice 10 supplies the loaded pair so
  readiness, population, stability checks, and generation share one immutable baseline rather than rereading files.
- **Exact population:** preserve JSON 2 selection/disposition/assumption/decision order; resolve every selected
  claim by exact `(id, version)`, deep-copy its complete version and claim kind/status, resolve direct support
  evidence only, deduplicate evidence by ID, and serialize deduplicated evidence in ID order. Never follow payload
  claim refs recursively, include unselected claims/history, read source, or mutate loaded context.
- **Resolved value:** return the exact transient document shape identified as
  `graphpilot.resolved-diagram-request.v1` plus canonical bytes/digest, loaded request/manifest paths and digests,
  exact selected-claim and accepted-assumption allowlists, total compact-byte estimate, and the ten largest
  per-section/per-item contributors sorted size-descending then
  path. This slice records accounting only; the deployment-aware generator projection and hard limit belong to
  Slice 10 because the complete resolved evidence view is never sent wholesale to Azure. The transient version
  marker is validated by resolver contract tests rather than another persisted JSON Schema asset.
- **Resolver failure policy:** missing refs after validated loading are violated internal invariants and raise one
  typed resolution error with bounded sorted issues; they are not silently skipped or repaired. No persisted
  resolved-context schema/file or cache is introduced.
- **Origin schema:** add optional strict node/edge `origin` with all four required fields: unique exact
  `claimRefs` (max 256), unique `assumptionRefs` (max 32), unique `schemaRules` (max 16), and nonblank
  `rationale` (max 2000). At least one grounding array must be nonempty. Reuse v1 ID/version grammars and keep
  diagrams with no origin backward-compatible.
- **Schema-rule registry:** start with only the already-published `activity.initial-node` rule. It permits a node
  whose semantic type is `initialNode`; when it is the sole authority, the normalized label must be empty,
  `Initial`, or `Start` and canonical `data` may contain only `label`/`semanticType`. Edges and other domain-bearing
  fields receive no schema-only exemption. The validator owns one immutable rule-to-element mapping rather than a
  new service/config layer. New rules are additive only after a demonstrated generated scaffold requires them.
- **Provenance validation:** validate every context-generated node/edge against the resolved allowlists; reject
  missing/malformed origin, duplicate/unknown claim or assumption refs, duplicate/unknown/mismatched schema rules,
  empty grounding, schema-only domain meaning, and invalid rationale. Decision/evidence/discovery IDs are never
  origin authorities because the strict shape has no such fields. Sort by path/code/message and cap at 256 issues.
- **Trace schema:** type optional `metadata.generationMode` as `prompt|context`; `generationContext` is strict and
  allowed only with context mode. It contains exact request/manifest artifact refs, the complete selected-claim
  set, final readiness summary, generator identifiers, complete copied assumption/decision arrays, and the exact
  accepted `generationPolicy` receipt. `require_ready` stores mode only; warning/override modes retain actor/time,
  reviewed digests, and exact acknowledged finding IDs, with `force_with_gaps` requiring `acceptedBy: user`.
  This replaces the older lossy `acceptedWarningCodes` example and matches the frozen MCP policy contract.
- **Population boundary:** Slice 08 fully defines and validates the trace DTO/schema/frontend shape with bounded
  representative fixtures, including readiness/generator/policy fields. Slice 10 assembles real trace values from
  resolved context plus the final readiness/generator/policy result and writes them during orchestration; Slice 09/
  Slice 10 preserve logical origin through ID remapping and integrate provenance into bounded refinement.
- **Frontend parity:** add typed origin/trace interfaces, strict runtime guards for known optional fields, Python
  TypedDict origin parity, and adapter preservation from original canonical elements. Canvas-created/cloned
  elements do not inherit grounded origin accidentally, and rendering remains visually unchanged.
- **Verification:** schema meta-validation and positive/negative origin/trace fixtures; resolver determinism,
  deep-copy, exact-version, evidence-deduplication, contributor and invariant-error tests; provenance rule/ref/
  rationale/order/cap tests; frontend guard and node/edge round-trip tests; all existing provenance-free examples,
  backend tests, and frontend verification remain green.

## Included Work

- Consume validated bound context for deterministic reference resolution and the prepared-generation shape.
- Add context-size contributor accounting and stability digests.
- Add element-origin and diagram-trace schema fields.
- Add provenance validation and exact citation/rationale rules.
- Update frontend types, runtime guard, and round-trip parity to preserve optional trace metadata.
- Keep diagrams without provenance valid and editable.

## Not In Scope

- Calling the generator or adding context-generation MCP tools.
- Provenance/evidence inspection UI.
- Persisted generation snapshots or raw reviewer/generator packets.

## Target Areas

- `backend/services/generation/requests/generation_context_resolver.py`
- `backend/services/generation/review/context_provenance_validator.py`
- `backend/services/`
- `backend/assets/schemas/diagram.json`
- `frontend/src/types/diagram.ts` and affected adapter parity tests
- backend context/provenance tests

## Exit Criteria

- Prepared input resolves exact canonical references and is deterministic.
- Invalid/missing citations or origin combinations fail before persistence.
- Schema/type/runtime-guard parity passes.
- Existing no-provenance diagrams round-trip unchanged.
- Backend and relevant frontend verification pass.

## Previous Slice

- [`07-context-mcp-tools.md`](07-context-mcp-tools.md)

## Next Slice

- [`09-shared-generation-phases.md`](09-shared-generation-phases.md)

## Outcome

**Completed.**

- **Implementation:** added `GenerationContextResolver` and frozen resolved-context/contributor contracts for exact
  selected-version population, ID-sorted evidence deduplication, canonical digest/bytes, loaded stability tokens,
  allowlists, and bounded contributor accounting without another persisted packet. Added
  `ContextProvenanceValidator` with bounded sorted typed issues, exact claim/assumption allowlists, duplicate and
  unknown-ref rejection, and the narrow `activity.initial-node` schema-only rule.
- **Canonical parity:** extended `graphpilot.diagram.v1` with strict optional node/edge origin and typed context trace
  metadata, including status-consistent exact generation-policy receipts. Added Python/TypeScript trace/origin
  shapes, frontend runtime guards, schema-rule parity, and adapter preservation from original canonical IDs;
  canvas-created/cloned elements omit grounded origin while React Flow's unrelated node-anchor `origin` remains
  untouched. Existing provenance-free diagrams and all 48 examples remain valid.
- **Verification:** all 574 backend tests pass offline with 3 expected skips. Frontend lint/build, all 392 unit tests,
  and all 24 Chromium E2E tests pass; focused resolver/provenance/schema/adapter suites, TypeScript, schema
  meta-validation, and `git diff --check` also pass.
- **Deviations:** the transient resolved document keeps a tested version marker and frozen runtime contract rather
  than adding a persisted JSON Schema that no boundary consumes. The canonical trace now stores the exact accepted
  generation-policy receipt instead of the older lossy warning-code summary. Trace values are fully typed and
  fixture-validated here; Slice 10 remains responsible for assembling real final readiness/generator/policy values.
- **Follow-up:** Slice 09 extracts only proven reusable direct-generation phases and preserves origin through
  logical ID remapping; Slice 10 composes the resolver, mandatory final readiness, provenance gate, trace assembly,
  context stability, persistence, and rendering.
