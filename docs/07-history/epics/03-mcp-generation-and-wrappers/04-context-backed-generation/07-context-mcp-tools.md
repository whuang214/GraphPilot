# Slice 07: Context MCP Tools

## Purpose

Expose evidence freshness/promotion, request persistence, and standalone readiness assessment through thin,
one-shot MCP tools over the shared services.

## Background

Context schemas, persistence, preflight, reviewer, and deterministic policy are complete. MCP owns transport
and protocol adaptation only; semantic authorship remains with the host.

## Design

Implement the audited `context_evidence_status`, `context_evidence_save`, `context_request_save`, and
`context_readiness_assess` contracts. Introduce the shared `OperationProblem` value, require its
`code`/`message`/`retryable` fields, keep `details` optional and code-specific, and migrate handled MCP/API
failures atomically to their final envelopes. This slice also implements the already-published opt-in readiness
snapshot transport so the tool never advertises an accepted diagnostics input it cannot honor; Slice 11 owns
calibration, repeated-run proof, retention/deletion safety, and release hardening rather than a second implementation.

## Plan Audit

- **Shared problem model:** add frozen `OperationProblem(code,message,retryable,details?)` plus one additive
  retryability registry covering every current MCP/API handled code. `to_dict()` deep-copies bounded details and
  omits them when absent. MCP `_error()` always returns one `CallToolResult` with safe text,
  `structuredContent.error`, and `isError: true`; successful dict/status/validation results and
  `_markdown_result()` explicitly remain `isError: false`. Unexpected exceptions are logged and sanitized to
  non-retryable `internal_error` with no details.
- **HTTP migration:** every non-2xx Django error becomes `{error: OperationProblem}`. Validation failure details are
  exactly `issues[]`; render-after-save becomes successful save plus `warning: OperationProblem` and intended paths.
  Remove the duplicate diagram error/failure models. Frontend `OperationProblem` parsing requires
  code/message/retryable, retains optional details, projects `details.issues` to the existing editor validation
  display, and treats malformed non-2xx bodies as `invalid_response` rather than branching on legacy fields.
- **Tool construction:** each context call validates a nonempty absolute existing workspace directory, constructs
  request-scoped `WorkspaceStorageService`/`ContextPersistenceService`, and constructs readiness only for assess.
  The net readiness projection limit comes from positive setting `GRAPHPILOT_READINESS_INPUT_LIMIT` (default
  `65536` conservative byte/token upper bound); adapters never cache workspace-bound services globally.
- **`context_evidence_status`:** optional manifest path defaults canonically; missing is successful `status: missing`.
  Results expose workspace-relative POSIX paths and exact status/digest/file-count fields. Invalid canonical JSON,
  fingerprint I/O, path, and workspace failures map to their contracted codes without writes or LLM calls.
- **`context_evidence_save`:** JSON 1 uses only a durable canonical-drafts candidate path; expected manifest digest
  is required but nullable only for creation, expected source digest is required, and retain defaults false. Adapter
  omits internal `written`, consumes/retains drafts per service outcome, maps history/validation issues, source and
  manifest conflicts exactly, and converts cleanup failure to nonfatal `warning: OperationProblem` with
  `candidatePath`/`safeToOverwrite` while keeping `isError: false`.
- **`context_request_save`:** JSON 2 candidate is inline and complete; expected request digest is required but
  nullable only for creation. Adapter returns canonical request baseline and workspace-relative path, maps stable
  identity as `request_conflict` using exact expected/current digests, and returns reconciliation details without
  silent rewriting.
- **`context_readiness_assess`:** request path plus optional strict diagnostics object executes one full assessment.
  All readiness statuses, including `invalid`/`needs_context`, return under `readiness` with `isError: false`.
  Unavailable/review failure/oversize/reconciliation/load errors map typed details; no reviewer fallback or retry loop.
- **Diagnostics:** `diagnostics` accepts only `persistReadinessResults:boolean` (default false) and
  `runId:string|null`; unknown fields/types fail `invalid_arguments`. Enabled snapshots use
  `.graphpilot/context/debug/readiness/<requestId>/<runId>/attempt-NNN.json`, run IDs
  `^run-[a-z0-9]+(?:-[a-z0-9]+)*$` (max 128), generated UUID-backed IDs when null, UTC `Z`, exclusive creation,
  and the exact safe wrapper in the host-workflow owner. The result returns
  `{persisted:true,runId,path,attempt}` with workspace-relative path; disabled returns `null`. A post-assessment
  snapshot failure is a successful readiness result with `warning: OperationProblem`, never a repeated review.
- **Error detail audit:** validation issues sort path/code/message and cap at 256; `readiness_review_failed` details
  are `stage`, `attemptsUsed`, optional issues/model; conflicts/source/reconciliation/oversize/cleanup/render fields
  match the active table exactly. Messages never expose stack traces, credentials, prompts, raw provider output,
  complete context, or absolute source paths beyond caller-supplied workspace artifact paths.
- **Verification:** direct handler tests assert exact arguments, service delegation, side effects, result fields,
  `CallToolResult.isError`, all typed failures/warnings, missing/current/stale/no-op/conflict/reconciliation,
  diagnostics off/on/exclusive numbering, and zero reviewer calls for invalid preflight. Stdio smoke exercises the
  three deterministic lifecycle tools and readiness's deterministic unconfigured/invalid path without requiring
  Azure. Full backend and affected frontend unit/type/build checks must pass.

## Included Work

- Register the four context lifecycle/readiness tools with exact arguments and results.
- Enforce draft-path versus inline-candidate transport and expected digests.
- Map actual failures to `error: OperationProblem` with MCP `isError: true`; keep statuses/results at
  `isError: false` and use the same canonical problem value for nonfatal operational warnings.
- Migrate existing MCP expected failures, Django error bodies, frontend API parsing, and contract tests to the
  final problem shape in one coordinated change.
- Support opt-in readiness debug paths only when explicitly requested.
- Add handler tests and extend the stdio smoke test for deterministic operations.

## Not In Scope

- Context-backed generation or the public host workflow prompt.
- Backend-authored claims, request intent, assumptions, or decisions.
- Patch APIs, blind overwrite, or automatic repeated retries.

## Target Areas

- `backend/mcp_server/server.py`
- MCP support/prompt modules if split during implementation
- `backend/services/`, `backend/api/`, and API contract tests
- `frontend/src/api/` and affected frontend API/editor tests
- `backend/tests/mcp_server/`
- `backend/mcp_server/smoke_test.py`

## Exit Criteria

- Every tool is one bounded operation over shared services.
- Status results are not misreported as operation errors.
- Every handled MCP failure has `isError: true`; successful status/warning results have `isError: false`.
- MCP and HTTP adapters expose the same `OperationProblem` fields, and the frontend consumes the final HTTP
  envelope.
- Conflict and retry details exactly match the active MCP contract.
- Handler, backend, and affected frontend tests pass offline.

## Previous Slice

- [`06-semantic-reviewer.md`](06-semantic-reviewer.md)

## Next Slice

- [`08-context-population-and-provenance.md`](08-context-population-and-provenance.md)

## Outcome

**Completed.**

- **Implementation:** added the four request-scoped evidence/request/readiness MCP tools with strict
  workspace-relative POSIX transport paths, optimistic digests, deterministic missing/current/stale status,
  complete draft/inline replacement, typed reconciliation/conflicts, and full readiness results. Added the shared
  frozen `OperationProblem` registry/envelope, sanitized unexpected MCP failures, nonfatal cleanup/diagnostics/render
  warnings, opt-in exclusive readiness snapshots, and the positive readiness projection setting. Migrated all
  handled Django errors and the frontend parser to the same problem value without a duplicate save-failure model.
- **Verification:** all 559 backend tests pass offline with 3 expected skips; the real stdio smoke test registers and
  exercises all four tools through missing/current evidence, draft promotion, request persistence, and invalid
  preflight without an LLM call. Frontend lint/build, all 389 unit tests, and all 24 Chromium E2E tests pass; focused
  contract/API/MCP/frontend/type checks also pass.
- **Deviations:** implementation evidence required readiness's error list to include the existing
  `manifest_unreadable` and `request_validation_failed` codes, and malformed/oversized durable drafts now emit
  registered `invalid_json`/`artifact_too_large` issue details. The accepted diagnostics transport is implemented
  here so the public argument is truthful; Slice 11 retains calibration, retention/deletion safety, repeated-run
  stability, and release hardening. The E2E seed now uses one run-unique temp workspace because a fixed temp path
  could accumulate legacy copies and make identity resolution correctly ambiguous.
- **Follow-up:** Slice 08 adds deterministic generation-context resolution, provenance validation, and canonical
  trace/type parity without moving those concerns into these protocol adapters.
