# Slice 01: Contract and Observer Foundation

## Purpose

Establish the redesign's exact contract, version, schema-registry, operation-code, and generation-observer foundations so every later generation and evaluation slice builds on one immutable vocabulary without changing GraphPilot's current public MCP behavior.

## Background

This is the first redesign implementation slice, but it is not the first execution gate. Phase 0A planning and Phase 0B active-design promotion are audited/committed; the current context group's Slice 12 compatibility bridge is implemented/verified at exact pre-redesign code baseline `1f14546`. No work in this slice may start from research as runtime authority: the Phase 0B product, architecture, MCP, generation, validation, schema, answer-key, evaluation, testing, environment, and decision owners govern implementation.

The foundation is intentionally internal. It makes future contracts discoverable and observable without registering `diagram_generation_workflow`, exposing new request/generation tools, switching current validators to new public IDs, invoking an LLM, or writing a user workspace.

## Design

### Dependencies and ownership

- Hard prerequisites are audited plan commit `8d0b914`, audited promotion commit `3d0fc93`, and implemented compatibility/pre-redesign baseline commit `1f14546`.
- `docs/01-architecture/01-backend-architecture.md` owns backend dependency direction, observer/service boundaries, and `OperationProblem` semantics.
- `docs/02-design-and-features/04-generation-design.md` owns generation stages, contracts, versions, and safety behavior; `07-evaluation-and-doe-design.md` owns evaluation contracts while remaining downstream of generation.
- `docs/02-design-and-features/02-validation-design.md` owns deterministic-versus-semantic validation boundaries. `docs/03-development-and-delivery/00-development-environment.md` owns configuration, and `01-testing-strategy.md` owns offline test policy.
- Research documents remain planning rationale only after Phase 0B. An implementation discovery updates the applicable active owner before this slice can complete; it is not resolved by adding a second contract description here.

### Contract and registry foundation

Use Draft 2020-12 schemas and namespace-first IDs. Every registered document has an exact registry key, file path, `$id`, `schemaVersion`, and `kind`; `$id` equals `schemaVersion`, constants agree, unknown fields are rejected unless the promoted contract explicitly permits them, and all text/array/object bounds are encoded rather than left to callers.

Land the exact formal artifacts and immutable Python values required by later slices for generation inputs and logical candidates, deterministic and semantic repair/review, generated/blocked results, compact trace, diagnostics envelopes, training examples/sets/metadata, and evaluation foundations. Later slices own runtime builders, persistence, orchestration, and evaluator behavior; they consume these identities rather than creating parallel constants or schemas. Slice 02 owns activation of persisted direct/context request schemas and lifecycle. No permissive placeholder schema is allowed: if a downstream contract is not exact in the promoted owner, stop and correct that owner before implementation.

Registry integrity is defined precisely:

- registry keys, file paths, and `$id`/`schemaVersion` values are globally unique;
- every file's declared kind agrees with the registry;
- intentional kind reuse across the three per-type direct logical schemas and the three per-type context logical schemas is allowed only with distinct schema IDs and paths;
- prompt, semantic-profile, rubric, training-set, and layout identities are immutable content identities, not interchangeable schema IDs; and
- callers cannot mutate the cached registry value used by another caller.

### Observer boundary

Add a generation-owned protocol with only these callbacks:

```text
GenerationObserver
  on_stage
  on_provider_call
  on_candidate
  on_result
```

The protocol and its event values live in neutral generation/contracts code and import no evaluation, MCP, persistence, or diagnostics implementation. Events are frozen/deeply immutable, bounded, ordered, and versioned; they carry safe stage/call/candidate/result identity, canonical digests, byte/count/timing/usage metadata, and only the bounded payload explicitly required by the promoted contract. They never carry API keys, authorization headers, `.env` values, hidden gold, unselected raw source, or unbounded provider transport.

Normal generation receives a no-op observer. This slice proves that the no-op performs no filesystem, network, provider, or logging side effect. Runtime diagnostics and offline evaluation will implement separate observers in Slices 06 and 10; generation must never import either. Callback failure policy belongs to the later adapter/orchestrator using an observer and must not be smuggled into the protocol as evaluation-specific behavior.

### Operation problems and public boundary

Register the approved generation codes and retryability metadata, including strict-output, packet/response bound, provider, invalid response, deterministic/provenance exhaustion, semantic review/repair, layout, request conflict, context change, name conflict, and atomic-write failures. Valid semantic blockers remain successful typed results, not `OperationProblem`s; trace, diagnostics, and render failures remain warnings when their owning slices activate them.

Where a code is already emitted by the current public path with different legacy retryability, this slice adds the final internal contract without changing the currently emitted payload. The atomic public remap/removal belongs to Slice 09. Tests must characterize the existing MCP prompt/tool names, argument schemas, and result/error payloads before and after this slice.

Rollback is an ordinary revert of the Slice 01 implementation commit. Because the new foundation has no public caller and writes no workspace artifact, rollback requires no file migration or deletion and must leave the compatibility bridge and recorded baseline intact.

## Plan Audit

The plan audit must verify:

- **Sequence:** both Phase 0 commits, compatibility Slice 12 implementation, and baseline recording are explicit hard gates.
- **Canonical authority:** every behavior links to one promoted active owner; research is not treated as implementation authority after promotion.
- **Schema ownership:** Slice 01 establishes exact artifacts/registry/values, while request lifecycle, model-packet execution, fixtures, review, and evaluation behavior remain assigned to their later slices.
- **Registry integrity:** tests distinguish prohibited duplicate IDs/paths/keys from the intentional repeated logical `kind` values and reject schema/constant drift.
- **Dependency direction:** generation owns the observer protocol; no generation module imports evaluation, MCP, diagnostics persistence, or frontend code.
- **Safety:** event payloads are immutable and bounded, exclude secrets/source/gold, and the no-op observer has zero side effects.
- **Failure semantics:** final code/retryability metadata is complete without changing current public error payloads or turning blockers into errors.
- **Public compatibility:** no MCP registration, current schema acceptance, request path, provider call, persistence behavior, canonical diagram shape, or frontend contract changes.
- **Reversibility:** one ordinary revert removes only the new internal foundation; no local artifact cleanup or destructive Git action is needed.
- **Verification:** add failing focused schema/registry/contract/observer tests first, then require current MCP characterization, the complete offline backend suite, stale/duplicate searches, and `git diff --check`; live Azure and frontend work are excluded.

Plan audit result: **Pass.** The audit confirmed internal-only activation, exact registry uniqueness, generation-owned observer independence, bounded immutable events, current-surface characterization, and ordinary-revert safety. Phase 0 promotion, compatibility implementation, and baseline recording remain explicit execution gates rather than plan defects.

## Included Work

- Add the exact approved schema/contract inventory assigned to this foundation and register each artifact once.
- Add immutable Python constants/value types for schema, kind, prompt, semantic-profile, rubric, training-set, layout, trace/debug, and evaluation-foundation identities.
- Extend `SchemaRegistry` with typed accessors and inventory validation while preserving current accessors and cache isolation.
- Add valid/invalid worked fixtures and schema meta-validation for every foundation artifact.
- Add the frozen `GenerationObserver` protocol, bounded event values, and no-op implementation.
- Add the approved internal operation-code/retryability registry entries without changing currently emitted public payloads.
- Add import-boundary tests proving generation is independent of evaluation and protocol adapters.
- Add characterization tests proving the current MCP prompt/tool discovery and current direct/context result/error contracts are unchanged.
- Update a promoted canonical owner only when implementation evidence requires a correction, then keep runtime status in the current-state board and this slice's eventual Outcome.

## Not In Scope

- Persisting direct or renamed context requests; that is Slice 02.
- Building generation packets, loading prompts, or calling a strict provider; that is Slice 03.
- Authoring or activating training fixtures; that is Slice 04.
- Deterministic candidate repair, semantic review/repair, trace/debug persistence, layout changes, or evaluation execution.
- Registering, renaming, or removing any MCP prompt or tool.
- Accepting old and new public IDs through an alias, migrating local artifacts, or deleting any user file.
- Frontend changes, hidden-gold content, live provider calls, `.env` access, production promotion, or push.

## Target Areas

- `backend/assets/schemas/` — exact foundation schema artifacts from the promoted registry
- `backend/services/shared/schema_registry.py`
- `backend/services/` — immutable contract/version values and operation-code registry
- `backend/services/generation/` — observer protocol/events/no-op implementation only
- `backend/tests/fixtures/` — valid/invalid contract fixtures
- `backend/tests/contracts/`, `backend/tests/shared/`, `backend/tests/generation/`, and current MCP characterization tests
- `docs/01-architecture/01-backend-architecture.md`, `docs/02-design-and-features/02-validation-design.md`, `docs/02-design-and-features/04-generation-design.md`, `docs/02-design-and-features/07-evaluation-and-doe-design.md`, and `docs/03-development-and-delivery/01-testing-strategy.md` only if implementation evidence changes their promoted design
- this slice document and the live current-state board for implementation outcome/status only

## Exit Criteria

- The prerequisite compatibility implementation commit is recorded as the pre-redesign baseline.
- Every foundation schema meta-validates and has exact passing/failing fixtures for identity, kind, unknown fields, enums, and bounds.
- Registry tests prove unique keys/paths/schema IDs, allowed logical-kind reuse only, immutable cache behavior, and no duplicate constant ownership.
- Prompt/profile/rubric/example/layout identities are exact and cannot be confused with schema IDs.
- Observer tests prove callback ordering/value immutability/bounds, a zero-side-effect no-op, safe redaction boundaries, and no generation-to-evaluation import.
- Operation-code tests prove exact retryability and warning/blocker/error classification without changing a current MCP payload.
- Current prompt/tool discovery, argument schemas, and direct/context public behavior characterization remain unchanged.
- Focused tests pass with no network or workspace side effects; `cd backend; uv run python manage.py test` passes fully offline.
- Appropriate stale/duplicate identifier searches and `git diff --check` pass; the implementation audit has no unresolved finding.
- No frontend file, `.env`, user workspace artifact, hidden gold, or live provider was read or changed.

## Previous Slice

- [`../04-context-backed-generation/12-workflow-client-compatibility.md`](../04-context-backed-generation/12-workflow-client-compatibility.md) — must be implemented and recorded as the pre-redesign baseline after both Phase 0 document commits.

## Next Slice

- [`02-request-persistence-foundation.md`](02-request-persistence-foundation.md)

## Outcome

**Completion:** Added 38 exact namespace-first generation/evaluation schemas with one validated worked example each,
making 44 registered current-plus-staged schemas. Added immutable schema/prompt/profile/rubric/training/layout identities,
copy-isolated registry access with full duplicate/drift/meta validation, the four-callback frozen bounded
`GenerationObserver` protocol and side-effect-free no-op, and the additive final generation operation-code entries.
The new contracts remain internal; current MCP names, arguments, paths, schemas, results, and provider behavior are
unchanged.

**Deviations:** Evaluation foundation schemas are registered now but remain runtime-unused until Slices 10–13, as planned.
Current pre-namespace readiness machine assets and current public retryability values remain active until Slice 09's
atomic cutover; no alias or dual public acceptance was introduced. The current and staged context evidence schemas
temporarily share exact kind `evidenceManifest` under separately unique IDs/files so S4 can author final fixtures while
the public getter remains old-only; Slice 09 removes that one transitional duplicate with the old schema.

**Verification:** Added failing-first identity/immutability, schema inventory, valid example, duplicate/path/kind/drift,
copy-isolation, observer bounds/outcome/no-op, dependency-import, and operation-code tests. Two independent implementation
audits passed. Focused foundation tests, all 697 provider-free backend tests (3 skipped), real stdio MCP characterization,
schema reference/example validation, Python compilation, and `git diff --check` pass.

**Follow-up:** Slice 02 activates the separate direct/context request contracts and shared internal persistence lifecycle;
all new public names and old-contract removal remain deferred to Slice 09.
