# Slice 02: Request Persistence Foundation

## Purpose

Implement the internal, workspace-safe persistence and lifecycle shared by direct and context diagram requests so later generation tools consume one canonical request path, exact mode-specific validation, optimistic concurrency, immutable identity, and explicit finalization behavior.

## Background

The current context workflow stores its request beneath `.graphpilot/context/requests/` and validates the historical context-request contract. The redesign instead stores both modes at:

```text
.graphpilot/requests/<diagramName>.gp-request.json
```

with separate exact contracts:

```text
graphpilot.direct.diagram-request.v1   / directDiagramRequest
graphpilot.context.diagram-request.v1  / contextDiagramRequest
```

This slice stages that replacement internally. The current MCP request/context tools and current path remain publicly active until Slice 09; no new `diagram_request_save` registration or public dual acceptance is introduced here. The new persistence service rejects old IDs/paths explicitly and never migrates, rewrites, moves, or deletes an existing local artifact.

## Design

### Dependencies and canonical owners

- Slice 01's exact schema/ID registry, canonical serialization helpers, operation codes, and contract values are required.
- The audited Phase 0B `docs/01-architecture/01-backend-architecture.md` owns service and low-level storage boundaries.
- `docs/02-design-and-features/04-generation-design.md` owns direct-request authority/lifecycle; `docs/02-design-and-features/08-context-backed-generation/03-diagram-request-context.md` owns context-request meaning and manifest binding.
- `docs/01-architecture/03-mcp-tools/` remains the public MCP owner, but receives no runtime-surface change in this slice. Research is not runtime authority after promotion.

### Mode-specific contracts

The direct schema requires exact `schemaVersion`, `kind`, `requestId`, `diagramName`, `request`, `scope`, `requirements`, `assumptions`, and `decisions`. It enforces the promoted lexical rules and bounds, including safe kebab-case diagram names, typed IDs, `request.original` at `1..8,000`, other nonblank text at `1..2,000`, included scope `1..64`, excluded scope `0..64`, requirements `1..256`, assumptions `0..32`, and decisions `0..64`. Requirements use only the eight approved fact kinds; assumptions/decisions carry exact origin/acceptance fields; evidence, claims, provenance, source paths, style, logical elements, and interaction preference are forbidden.

The context schema keeps evidence-manifest binding, selected exact claim versions, uncertainty dispositions, accepted assumptions/decisions, and its existing deterministic semantic rules under the new namespace-first identity. It must not gain direct requirements as competing authority. Both schemas reject unknown fields and are dispatched only when `schemaVersion` and `kind` form the exact supported pair.

### Shared persistence lifecycle

One shared request-persistence component owns direct/context dispatch, canonical target resolution, complete replacement, digest concurrency, identity comparison, finalization, and result assembly. Mode validators remain separate and context validation still requires the exact canonical evidence manifest. `WorkspaceStorageService` remains the only low-level containment/atomic-write owner; it does not absorb request lifecycle policy.

Rules are:

1. Resolve only a direct child of `<workspace>/.graphpilot/requests/` with suffix `.gp-request.json`; reject traversal, absolute paths outside the workspace, nested paths, symlink/junction escape, and filename/candidate `diagramName` mismatch.
2. Validate the complete candidate and its `schemaVersion`/`kind` discriminator before any write. Enforce the existing 5 MiB request read/write ceiling in addition to field bounds.
3. Canonicalize as UTF-8, sorted keys, no insignificant whitespace, and one trailing newline for the persisted file; calculate lowercase `sha256:` digest from canonical document bytes consistently with the promoted digest owner.
4. Creation requires an absent target and no expected digest. Replacement requires the caller's exact current digest; stale/missing expected state returns `request_conflict` and writes nothing.
5. An exact idempotent candidate may return the existing digest with `written: false`; any changed replacement must preserve authority mode, `requestId`, and `diagramName`.
6. Before successful owned generation, a validated request may be replaced completely. Once a canonical diagram with matching request ownership exists, the request is finalized: an unchanged idempotent save may remain a no-op, but any changed candidate is rejected and writes nothing.
7. A diagram at the target name that is not owned by the same request is a `diagram_name_conflict`; request persistence never overwrites that diagram.
8. Request persistence and later diagram persistence are separate atomic operations. A generation failure leaves the saved request and any prior canonical diagram unchanged.

Successful internal results return canonical request path, digest, and exact kind/mode identity. Validation, unsafe-path, conflict, unsupported-old-contract, finalization, and atomic-write failures are typed and contain bounded safe details; they never include request content, source, secrets, or raw stack traces.

### Public and rollback boundaries

The current context persistence path/validator remains wired to current public handlers until Slice 09. The new service is exercised only through internal calls and tests, so this is staging, not a feature-flagged public dual runtime. No public tool may accept both old and new request IDs.

Rollback uses an ordinary revert of Slice 02 while retaining Slice 01. Tests use temporary workspaces. If a developer invoked the internal service manually, rollback leaves any new `.graphpilot/requests/` artifact untouched and unsupported; it does not silently delete or move it. No user diagram or old context artifact is changed during rollback.

## Plan Audit

The plan audit must verify:

- **Dependencies:** Slice 01 and both Phase 0 gates are complete; Slice 09 remains the only public request/tool/path cutover.
- **Authority separation:** direct requirements never acquire evidence semantics, and context claims never become direct requirements.
- **Storage ownership:** request lifecycle stays in one focused persistence component while `WorkspaceStorageService` owns only containment/read/write primitives.
- **Canonical path:** `.graphpilot/requests/<diagramName>.gp-request.json`, filename/name parity, direct-child enforcement, symlink/junction safety, and the 5 MiB boundary are exact.
- **Concurrency:** create, replace, stale digest, absent digest, no-op, atomic failure, and deterministic conflict details are covered before any write.
- **Identity/finalization:** mode, request ID, and diagram name cannot change; post-success mutation and foreign diagram ownership fail without changing either artifact.
- **Cold migration:** the new service rejects old IDs and `.graphpilot/context/requests/` paths without alias, auto-migration, deletion, or reinterpretation; current public handlers remain on their existing path until Slice 09.
- **Failure safety:** every invalid/path/conflict/finalized/unsupported/write failure is typed, bounded, deterministic, and write-free.
- **Reversibility:** reverting this internal slice needs no artifact migration and never deletes a local request or diagram.
- **Verification:** add failing schema/validator/storage/persistence tests first using temporary workspaces and no provider; then require full backend tests, current MCP characterization, stale-path/ID searches, and `git diff --check`.

Plan audit result: **Pass.** The audit confirmed mode authority separation, one lifecycle owner over low-level safe storage, exact digest/identity/finalization behavior, old-path rejection without migration, internal-only staging, and artifact-preserving rollback.

## Included Work

- Activate the exact direct-request schema and renamed context-request schema through Slice 01's registry.
- Add deterministic direct-request validation for exact fields, bounds, IDs, unique references, included/excluded conflicts, generatable type, and forbidden evidence/logical fields.
- Reuse the promoted context-request validation and manifest-binding rules under the new exact contract identity.
- Add one internal request-persistence component for discriminator dispatch, path resolution, canonical digesting, complete replacement, no-op behavior, optimistic concurrency, identity, finalization, and typed results/failures.
- Add the new `.graphpilot/requests/` low-level path primitives without rewiring current public context handlers.
- Add owned-diagram lookup sufficient to enforce finalization/name ownership without coupling canonical diagram writes into request persistence.
- Add valid/invalid direct/context fixtures and temporary-workspace create/load/no-op/replace/conflict/finalization/path-safety/atomic-failure tests.
- Characterize current public request/context tools and prove their names, arguments, old path, and payloads remain unchanged.
- Update promoted backend/generation/context owners only for evidence-backed implementation corrections.

## Not In Scope

- Registering `diagram_request_save` or either redesigned generation tool.
- Migrating current public context handlers, old request files, evidence files, or user diagrams to the new path.
- Silently accepting both old and new schema IDs or adding aliases.
- Building LLM packets, invoking generation, final readiness, semantic review, layout, persistence of a diagram, rendering, or regeneration/editing after finalization.
- Changing canonical diagram metadata; later generation/review slices own the minimal request reference consumed by finalization.
- Frontend changes, live Azure calls, hidden-gold authoring, `.env` access, database/auth work, or production promotion.

## Target Areas

- `backend/assets/schemas/direct-diagram-request.json`
- `backend/assets/schemas/context-diagram-request.json`
- `backend/services/shared/schema_registry.py`
- `backend/services/shared/workspace_storage_service.py`
- `backend/services/shared/canonical_json.py`
- `backend/services/context/context_document_validator.py` and the promoted shared request-persistence component under `backend/services/context/`
- `backend/services/context/context_persistence_service.py` only where extracting shared request behavior preserves the current public context path
- `backend/services/` request persistence/validation/result values and operation mappings
- `backend/tests/fixtures/context/`, new direct-request fixtures, `backend/tests/core/`, `backend/tests/shared/`, `backend/tests/contracts/`, and current MCP characterization tests
- `docs/01-architecture/01-backend-architecture.md`, `docs/02-design-and-features/04-generation-design.md`, and `docs/02-design-and-features/08-context-backed-generation/03-diagram-request-context.md` only if implementation evidence changes promoted design
- this slice document and the live current-state board for implementation outcome/status only

## Exit Criteria

- Exact valid direct/context documents pass only their own schema/validator; mismatched ID/kind, unknown fields, cross-mode fields, invalid bounds/IDs, and context binding failures are deterministic.
- Create, load, exact no-op, valid replacement, stale/missing digest, immutable mode/request/name, finalized request, foreign diagram ownership, and atomic-write failure tests all pass without partial writes.
- Path tests cover traversal, wrong root/suffix/name, nested paths, absolute escape, symlink/junction escape, oversized input, and canonical direct-child acceptance in temporary workspaces.
- Old IDs and `.graphpilot/context/requests/` are rejected by the new internal service without being rewritten, moved, or deleted.
- The current public MCP request/context surface and existing local-artifact behavior remain characterized and unchanged pending Slice 09.
- Failure payloads use stable registered codes/retryability and bounded safe details; no request content, source, secret, or raw exception leaks.
- Focused contract/storage/validator/persistence tests pass fully offline; `cd backend; uv run python manage.py test` passes.
- Relevant stale-path/ID searches and `git diff --check` pass, and the implementation audit has no unresolved finding.
- No live provider, frontend file, `.env`, hidden gold, or user workspace was used.

## Previous Slice

- [`01-contract-and-observer-foundation.md`](01-contract-and-observer-foundation.md)

## Next Slice

- [`03-strict-generation-contracts.md`](03-strict-generation-contracts.md)

## Outcome

**Completion:** Added the internal shared `.graphpilot/requests/<diagramName>.gp-request.json` lifecycle for strict direct
and namespace-first context requests. The new validator dispatches exact schema/kind pairs, enforces direct scope/ID
semantics, reuses manifest-bound context semantics, and rejects old contracts. Persistence uses compact sorted UTF-8 plus
one newline, a 5 MiB ceiling, exact digest create/replace/no-op concurrency, immutable mode/request/name identity,
process-safe create serialization, owned-diagram finalization, foreign-name conflict protection, and atomic writes. Current
public context handlers remain on `.graphpilot/context/requests/` until Slice 09.

**Deviations:** Current context schema validation was refactored to expose its deterministic semantic phase after either
old or new owning schema passes; current behavior and public path are unchanged. The shared request service is internal
only and no public dual acceptance/alias was added.

**Verification:** Added failing-first direct/context create/load/replace/no-op/conflict, old-contract/path, manifest/claim,
scope/ID, path/name, symlink, concurrent create, identity, finalization, foreign diagram, atomic failure, and size-bound
tests. The focused 61-test request/context/storage matrix passed (3 platform skips), the implementation audit passed with
no blocker/important finding, and all 711 provider-free backend tests passed (4 skipped) with `git diff --check` clean.

**Follow-up:** Slice 03 consumes canonical validated requests to build strict generation packets internally. Slice 09
alone registers `diagram_request_save`, cuts public paths/IDs over, and removes old request artifacts from active support.
