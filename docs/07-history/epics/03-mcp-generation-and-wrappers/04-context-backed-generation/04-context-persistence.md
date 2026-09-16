# Slice 04: Context Persistence

## Purpose

Add path-safe canonical storage, source fingerprinting, digest-bound replacement, and reconciliation support for
context artifacts while cutting diagrams over to the approved directory layout.

## Background

`WorkspaceStorageService` is the single low-level workspace-contained `.graphpilot` storage owner. It serves
both diagram and context artifact paths rather than creating a second file service; context business rules remain
in validation/persistence/application logic.

## Design

`WorkspaceStorageService` is the sole low-level workspace boundary. It owns containment, canonical roots, bounded
JSON/text/byte reads, and sibling-temp + `os.replace` writes, but no schema, fingerprint, lifecycle, or conflict
policy. New diagram allocation/listing uses `.graphpilot/diagrams/`; explicit legacy flat paths remain safely
readable/editable so existing files are not stranded, but no new flow creates, lists, moves, deletes, or dual-writes
a legacy flat artifact.

`ContextPersistenceService` composes storage, `ContextDocumentValidator`, canonical digest helpers, and an injected
UTC clock. Its public service operations are:

- `fingerprint_source(included_paths, excluded_paths)`;
- `evidence_status(manifest_path)`;
- `promote_evidence_candidate(candidate_path, manifest_path, expected_manifest_digest,
  expected_source_digest, retain_candidate)`;
- `save_diagram_request(request_path, candidate, expected_request_digest)`;
- validated `load_evidence_manifest`, `load_diagram_request`, and bound request+manifest loading; and
- canonical digest reads used by later generation-time stability checks.

JSON 1 promotion parses the bounded draft, computes the candidate scope's current fingerprint, checks source and
target preconditions, replaces backend-managed snapshot/revision/digest/timestamps, validates the normalized full
document, checks append-only history, and rechecks conflicts immediately before atomic write. JSON 2 save loads
canonical JSON 1, checks target preconditions and stable request identity, validates the complete binding, and
writes canonical latest intent. Neither operation repairs host-authored semantic content.

## Plan Audit

- **Source fingerprint:** enumerate each included root in stable workspace-relative POSIX order; include regular
  non-symlink files only; never traverse symlinks; apply the recorded mandatory/configured v1 exclusions before
  reading; deduplicate overlapping roots; hash raw bytes; fail the whole operation on an eligible-file read error.
- **First creation and scope changes:** promotion fingerprints the draft's declared scope. A mismatched
  `expectedSourceDigest` returns the current digest and writes nothing, giving the host a safe baseline for a full
  regather without weakening the precondition. Missing-manifest status uses the default whole-workspace safe scope.
- **Managed JSON 1 fields:** creation sets revision `1` and one UTC timestamp; updates preserve `createdAt`, advance
  revision exactly once, and change `updatedAt` only for a real write. Snapshot `capturedAt` changes only when its
  digest/file count changes. Candidate values for these fields are ignored rather than trusted.
- **History:** evidence records and claim containers remain in existing order; evidence content and existing claim
  versions are byte-semantically immutable; only evidence lifecycle status and claim status/current pointer may
  change in place; new evidence/claims/versions append; evidence/claims never disappear. Open uncertainties may be
  added, retained unchanged, or removed when resolved.
- **No-op:** after managed-field normalization, content identical to canonical state performs no write and changes
  no revision/digest/timestamp. A successful no-op consumes the draft unless retained. Identical JSON 2 likewise
  performs no write.
- **Concurrency:** null expected digest is creation-only; updates require an exact canonical digest. The service
  checks immediately before replacement but adds no long-lived lock, patch API, retry loop, or silent rebase.
- **Reconciliation:** a request whose manifest ID/digest differs raises a typed reconciliation result/error and is
  never silently rebound or partially rewritten.
- **Layering:** no context MCP tool lands here; Slice 07 adapts these typed outcomes. Frontend changes are limited to
  the canonical diagram-directory cutover because browser context authoring remains out of scope.

## Included Work

- Complete the approved `WorkspaceStorageService` module/class/base-error cutover; update every import, test,
  entry point, and active owner atomically without an alias.
- Add grouped evidence, request, diagram, draft, and diagnostic roots/path/read/write helpers and bounded JSON
  reads for the 50 MiB JSON 1 and 5 MiB JSON 2 limits.
- Cut new diagram/list/artifact allocation over to `.graphpilot/diagrams/` while preserving explicit legacy-path
  access without migration or dual-write behavior.
- Add deterministic safe-scope source fingerprinting and typed persistence result/error contracts.
- Add JSON 1 draft promotion, managed-field normalization, append-only history checks, cleanup warning, and
  expected source/manifest digest handling.
- Add manifest-bound inline JSON 2 complete replacement, identity protection, no-op behavior, and validated bound
  loads/digest reads for later readiness/generation slices.
- Coordinate backend, API, MCP, affected frontend path tests, docs, and examples for the path cutover.

## Not In Scope

- Semantic readiness, LLM calls, context generation, or provenance.
- Silent movement/deletion of existing flat files.
- A patch API or long-lived file locks.

## Target Areas

- `backend/services/shared/workspace_storage_service.py`
- `backend/services/context/context_persistence_contract.py`
- `backend/services/context/context_persistence_service.py`
- `backend/services/diagrams/persistence/diagram_persistence_service.py`
- `backend/api/`, `backend/mcp_server/`, and all storage import consumers
- `backend/tests/shared/`, `backend/tests/core/`, and affected API/MCP/generation tests
- frontend path fixtures/e2e assertions where the canonical directory is observable
- active storage, API, workflow, testing, setup, and service-navigation owners

## Exit Criteria

- All paths remain beneath the workspace under symlinks and traversal attempts.
- Writes are validated, canonical, atomic, and conflict-safe.
- No-op checks do not change revisions, digests, or timestamps.
- Diagram and derived-artifact paths use the new canonical layout consistently.
- Existing files are not moved or deleted automatically.
- Backend and affected frontend verification pass.

## Previous Slice

- [`03-evidence-and-request-schemas.md`](03-evidence-and-request-schemas.md)

## Next Slice

- [`05-readiness-preflight-and-projection.md`](05-readiness-preflight-and-projection.md)

## Outcome

**Completed.**

- **Implementation:** renamed the low-level file boundary to `WorkspaceStorageService`, cut new diagram/list/render
  allocation over to `.graphpilot/diagrams/`, added canonical context roots plus bounded canonical JSON I/O, and
  preserved explicit legacy flat-path access without migration or dual writes. Added typed persistence DTOs and
  `ContextPersistenceService` with deterministic safe-scope fingerprints, managed JSON 1 promotion, immutable
  history checks, cleanup warnings, manifest-bound JSON 2 replacement, validated bound loads, no-op stability, and
  immediate source/target conflict rechecks.
- **Verification:** 30 focused persistence/storage/contract tests pass; the complete backend passes 499 tests
  offline. Affected frontend API/component tests pass 40/40, and the canonical seed/load plus workspace-listing
  Playwright proof passes 2/2.
- **Deviations:** the full frontend gate was also attempted, but the concurrent Epic 2 refinement working tree still
  has one unrelated lint warning, three unrelated E2E TypeScript errors, and five unrelated browser failures. No
  Slice 04 path/persistence failure remains. Stable JSON 1 identity, final no-op rechecks, and normalized persisted
  byte-limit enforcement were added during audit because the approved contracts require them.
- **Follow-up:** Slice 05 consumes validated bound context and canonical digest reads for deterministic readiness
  preflight and bounded projection.
