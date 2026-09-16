# Lane A Slice 05: Snapshot Backend

## Purpose

Implement the committed current-snapshot and durable-request backend contracts without changing host rendering, MCP registration, provider behavior, or Lane B contracts.

## Design

GraphPilot accepts one semantic evidence draft, validates it against an exact backend-issued save precondition, normalizes it into one current canonical snapshot, returns one opaque evidence reference, and removes the successful draft/empty directory safely. Context requests bind that exact evidence reference and select flat current claim IDs. Internal adapters preserve existing readiness/generation provider projections where possible.

## Included Work

- Candidate and canonical evidence snapshot validation.
- Safe-scope fingerprint/status and backend-issued save preconditions.
- Atomic current-snapshot create/replace/no-op behavior and concurrency checks.
- Flat evidence/claim/uncertainty reference validation.
- Backend-managed source metadata and canonical version reference construction.
- Exact successful draft removal, empty-directory cleanup, failure retention, and nonfatal cleanup warning.
- Snapshot-bound context request validation/persistence/finalization and request references.
- Internal adaptation to readiness/generation input models without provider-contract drift.
- Focused schema, freshness, conflict, concurrency, path, cleanup, request, and security tests.

## Not In Scope

- Workflow route plan, authoring-contract lookup, shared MCP tool registration, canonical diagram metadata, frontend types, provider calls, benchmark execution, or docs integration.
- Lane B prompt/projection/schema/validator/correction files.

## Target Areas

A03 must replace this paragraph with an exact committed file list before A04 begins. The ownership boundary is context validation/persistence, request validation/persistence, storage helpers, internal context-resolution adapters, and their focused tests. A04 may not modify host workflow/authoring services, example/checklist assets owned by A05, shared schema registration, `mcp_server/server.py`, canonical diagram/frontend types, integration docs, or any Lane B file.

## Exit Criteria

- Missing/current/stale and save-precondition behavior is deterministic and provider-free.
- Source/concurrent drift writes nothing and returns actionable safe errors.
- Canonical snapshots contain only current semantic records plus backend-managed metadata.
- Flat refs validate exactly; unknown/missing relationship endpoints fail before provider use.
- Successful promotion deletes only the submitted draft and removes the directory only when empty; failed promotion retains it.
- Durable requests bind exact evidence refs, finalize on owned generation, and retain provider-free recovery semantics.
- Internal adapter preserves existing provider-facing call order/shape or stops for design review.
- Focused and full backend checks plus implementation audit pass before commit.

## Previous Slice

[`lane-a-04-authoring-discoverability.md`](lane-a-04-authoring-discoverability.md)

## Next Slice

[`lane-a-07-integration.md`](lane-a-07-integration.md), after A06 also commits.

## Outcome

To be completed.
