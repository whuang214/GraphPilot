# Slice 03: Evidence and Request Schemas

## Purpose

Implement versioned machine contracts and deterministic validation for the JSON 1 evidence manifest and JSON 2
diagram request context.

## Background

The promoted active contracts established semantic fields and lifecycle rules. The Slice 03 audit has now frozen
the remaining persisted v1 choices in the JSON 1/JSON 2 owners: closed claim payloads, exact role-prefixed IDs,
bounds, direct reference rules, UTC timestamps, canonical JSON/digests, and non-destructive history policy.

## Design

JSON Schema is the runtime source for untrusted document shape validation. Python contract types represent only
validation results; they do not duplicate document schemas. The existing diagram-only loader becomes
`SchemaRegistry`, with cached `get_diagram_schema`, `get_evidence_manifest_schema`, and
`get_diagram_request_schema` access plus the existing diagram summary capability. No parallel
`ContextSchemaService`, duplicate normative schema tree, or compatibility shim is introduced.

One internal `ContextDocumentValidator` composes the registry and performs schema plus deterministic semantic
checks. It returns stable `$`-rooted issue paths/codes, validates JSON 1 on its own, and validates JSON 2 against
a supplied validated manifest. Canonical JSON helpers are pure support functions reused by Slice 04 persistence.
They do not read files, calculate repository fingerprints, mutate managed fields, or compare old/new histories.

## Plan Audit

- **Persisted compatibility:** lower-kebab role prefixes and exact closed payload field names are now explicit;
  future additive or incompatible payload changes require a new schema version.
- **Reference boundary:** only relationship/property/constraint payloads carry exact claim-version refs; targets
  may be any claim kind, and population remains nonrecursive. No unused graph-depth abstraction is added.
- **Validation boundary:** schema, complete-document invariants, and JSON 2 → JSON 1 binding land here. Historical
  immutability comparison, optimistic concurrency, path I/O, and backend-managed revision/timestamp replacement
  remain Slice 04 persistence responsibilities.
- **Digest boundary:** canonical object serialization and digest verification land here; source file enumeration
  and raw file hashing remain Slice 04.
- **Size boundary:** schema count/text limits land here; raw 50 MiB/5 MiB read limits require Slice 04's file
  boundary and are not guessed from an in-memory object.
- **Service shape:** `SchemaRegistry` is the only schema loader, and `ContextDocumentValidator` is an internal
  deterministic component rather than another application capability.

## Included Work

- Add strict `evidence-manifest.json` and `diagram-request.json` Draft 2020-12 artifacts.
- Rename `DiagramSchemaService` to `SchemaRegistry`; update diagram validation, MCP schema lookup, imports, and
  tests atomically.
- Add a context-validation result/issue contract and stable schema/semantic issue-code registry.
- Add `ContextDocumentValidator` for JSON 1 invariants and manifest-bound JSON 2 invariants.
- Add canonical JSON bytes and SHA-256 helpers, including JSON 1's top-level `digest` omission rule.
- Add complete valid fixtures covering all eight claim payloads and focused invalid fixtures/tests for references,
  lifecycle combinations, bounds, IDs, digests, and deterministic issue order.
- Keep discovery-tool extraction provenance absent from JSON 1 v1 and update active owners for implementation
  discoveries.

## Not In Scope

- Repository fingerprint calculation or file writes.
- Manifest reconciliation execution.
- Readiness reviewer calls or MCP tools.

## Target Areas

- `backend/assets/schemas/evidence-manifest.json`
- `backend/assets/schemas/diagram-request.json`
- `backend/services/shared/schema_registry.py`
- `backend/services/shared/canonical_json.py`
- `backend/services/context/context_validation_contract.py`
- `backend/services/context/context_document_validator.py`
- `backend/services/diagrams/validation/diagram_validation_service.py`
- `backend/mcp_server/` schema lookup consumer
- `backend/tests/fixtures/context/`
- `backend/tests/contracts/`, `backend/tests/shared/`, `backend/tests/core/`, and affected MCP tests

## Exit Criteria

- Every complete fixture validates against the intended versioned schema.
- Invalid references, bounds, IDs, enums, and lifecycle combinations fail deterministically.
- Canonical serialization/digest fixtures are stable.
- Active contracts contain every implementation-level decision needed by slice `04`.
- Full backend tests pass offline.

## Previous Slice

- [`02-readiness-rubric-and-policy.md`](02-readiness-rubric-and-policy.md)

## Next Slice

- [`04-context-persistence.md`](04-context-persistence.md)

## Outcome

**Completed.**

- **Implementation:** added strict Draft 2020-12 JSON 1/JSON 2 schemas, complete valid/invalid fixtures, canonical
  JSON/digest helpers, frozen validation result types, and deterministic schema/reference/lifecycle validation.
  `DiagramSchemaService` became the shared cached `SchemaRegistry`; diagram validation and MCP schema lookup moved
  atomically with no compatibility shim.
- **Verification:** 34 focused Slice 03 tests, 155 Slice 03 plus affected registry/diagram/MCP regressions, and all
  461 tests in the isolated Slice 03 commit pass offline. Schema meta-validation, all eight payload kinds, canonical fixture digests,
  deterministic issue ordering, bounds, IDs, references, assumptions, authority, and timestamp rules are covered.
- **Deviations:** none. Raw 50 MiB/5 MiB read limits, old/new immutability comparison, repository fingerprinting,
  backend-managed revision/timestamp replacement, optimistic concurrency, and writes remain assigned to Slice 04.
- **Follow-up:** Slice 04 composes `SchemaRegistry`, `ContextDocumentValidator`, and canonical helpers behind
  workspace-safe, digest-bound context persistence.
