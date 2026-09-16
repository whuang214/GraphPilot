# Slice 11: Diagnostics and Release Gate

## Purpose

Add opt-in safe diagnostics and prove deterministic correctness, semantic calibration, repeated-run stability,
compatibility, and complete documentation before declaring the context-backed workflow release-ready.

## Background

This is the group hardening/release slice. It does not add a new semantic path or make debug artifacts
canonical.

## Design

Diagnostics are local, opt-in, bounded, disposable, and non-authoritative. Release requires deterministic
fixtures, human-labeled semantic calibration, repeated-run stability, direct/context compatibility, path and
frontend follow-through, and complete active documentation.

## Plan Audit

- **Truthful gate states:** distinguish implementation verification from semantic release certification. Offline
  tests and a check-only operator run can prove code, schemas, fixture integrity, metrics, and failure handling;
  they cannot claim the live calibration targets. The machine report uses exact `pass|fail|not_run` release
  status. `pass` requires an adjudicated holdout label set, two distinct human reviewer labels per case, the full
  configured holdout set, and ten live unchanged-input runs per case against one fixed deployment. Missing labels,
  credentials, user authorization for provider calls, or live runs remain `not_run`, never synthetic success.
- **Diagnostics boundary:** harden `ReadinessDiagnosticsService` to validate the complete final result against the
  registered final-result schema, enforce the 2 MiB result bound and a bounded nonblank model identifier, then
  exclusively write the exact safe wrapper. Replace the race-prone cross-directory run-ID scan with one safe global
  debug-only run-owner marker claimed by exclusive create, then exclusively number attempts; concurrent requests
  cannot claim the same run ID. Debug records remain outside canonical loading/fingerprinting and no deletion API
  is added; tests delete the complete debug root and prove canonical readiness/generation is unchanged.
- **Generation-final-gate transport:** add the same strict optional `{persistReadinessResults, runId}` argument to
  `diagram_generate_from_context`. Keep persistence in the MCP adapter, matching standalone readiness; the context
  orchestrator remains unaware of debug files and exposes only its final readiness result plus reviewer-model
  identity. Persist non-error `generated`, `blocked`, and `partial_success` outcomes with trigger
  `generation_final_gate`; downstream generation operation errors retain their existing error-only contract.
- **Diagnostics result matrix:** every non-error context-generation payload adds `diagnostics`, null when disabled
  or failed and the persisted descriptor when successful. A diagnostics-only failure adds
  `warning.code: diagnostics_write_failed`; `blocked` may carry both its independent `blocker` and that warning.
  If rendering and diagnostics both fail, preserve the outcome-defining singular `render_failed` warning and use
  `diagnostics: null`; do not add a warning array or replace the render recovery signal. All cases keep MCP
  `isError: false`, and diagnostics failure never changes or retries readiness/generation.
- **Shared argument parsing:** extract one private MCP diagnostics-options parser so standalone readiness and
  context generation reject unknown fields, wrong types, and empty/unsafe/overlong run IDs identically while
  preserving the existing optional-field semantics. No new public diagnostics tool or application DTO is introduced.
- **Fixture coverage:** consolidate the active deterministic release matrix in table-driven offline tests over the
  real rubric/policy/review validator/result assembler. Cover every facet at ratings `0..4`, conditional N/A and
  uncertain branches, assumption caps/replacement, decision factuality, exact finding policy/action shapes,
  invented refs/policy fields, invalid-output exhaustion, and invalid preflight. Add one fake-reviewer end-to-end
  semantic case per diagram type and cross-cutting Layer 3 positive/near-negative cases without treating model-authored
  expected output as human calibration evidence.
- **Calibration bundle:** define registered `graphpilot.readiness-calibration-bundle.v1` JSON with unique
  training/holdout case IDs, exact manifest/request documents, rubric/reviewer versions, and explicit draft or
  adjudicated label status. Draft cases may omit labels; every adjudicated holdout requires two independent reviewer
  labels and one answer key. Labels cover complete applicability and acceptable per-facet rating bands,
  required-facet pass/fail, exact mandatory/forbidden findings and emitted action kinds, status/overrideability,
  mandatory non-overrideable blockers, mandatory/forbidden selection/removal recommendations, and complete allowed
  refs. Bound the bundle file at 64 MiB and 256 combined cases, validate embedded JSON 1/JSON 2 through their
  canonical schemas, and
  verify each request's exact manifest ID/path/digest binding, and bound report failures to 255 entries plus one
  omitted-count record so JSON output stays below 2 MiB. The committed
  default bundle may remain explicitly uncertified until real reviewers supply labels; tests use synthetic temporary
  bundles only to prove validation and calculation.
- **Operator command:** add `uv run python manage.py calibrate_readiness`. Default check-only mode validates the
  bundle, versions, split disjointness, every supplied label, and report plumbing without Azure; it reports label
  completeness and accepts a structurally valid draft as `not_run`. Explicit
  `--live` is the only provider-calling mode; it requires configured Azure, adjudicated labels, and a nonempty
  complete holdout covering every required matrix tag, each facet's `0..4` boundaries, conditional N/A/uncertain,
  every finding code's positive/near-negative cases, and every action kind, then exactly ten runs per case. Extend
  `AzureLLMClient` with optional calibration-only temperature/seed
  controls whose defaults preserve runtime behavior; retry without either only on an explicit unsupported-parameter
  response and record the effective controls. `--json` emits the bounded report to stdout; invalid bundles, failed
  targets, or incomplete live certification exit nonzero through `CommandError`. No report becomes runtime input.
- **Metrics and stability:** calculate zero false-ready/non-allowlisted-ref/missing-mandatory-blocker gates, exact
  status, facet-applicability, acceptable-rating-band, required-facet pass/fail, mandatory finding, forbidden finding,
  emitted action-kind, and mandatory recommendation metrics, plus per-type/detail-level false-blocking counts. A zero
  denominator reports `0.0` and never passes. Conservatively fail certification for any false-blocked case whose
  adjudicated status is `ready` or `ready_with_warnings`, while reporting every type/detail group. Per case require
  `10/10` semantic-label agreement, non-overrideable blockers/refs, and mandatory/forbidden recommendations; no
  boundary flip or invalid policy/ref; score spread at most five. Record first-response repair use separately through
  a calibration-only counting `LLMClient` proxy (call count only, never prompts/responses) and never majority-vote or
  choose a favorable run.
- **Compatibility and failures:** reuse existing Slice 10 outage/budget/conflict/race/partial-success coverage,
  adding only missing release regressions: strict debug safety/deletion, default/final-gate diagnostics symmetry,
  legacy flat/provenance-free diagram validity, context origin/trace frontend round-trip, and current MCP schema/
  old-alias absence. Do not duplicate covered scenarios or expand into the subsequent whole-backend defect audit.
- **Verification and closure:** run the deterministic calibration check, full backend tests, real stdio smoke,
  frontend lint/typecheck/unit/build/E2E gate, and a browser-backed context/legacy load-save proof. Update active
  owners and record measured offline results separately from external certification. Standing repository commit
  permission replaces the obsolete per-slice approval sentence; no live Azure run or push occurs without explicit
  user authorization.

## Included Work

- Harden and verify numbered standalone and generation-final-gate readiness debug records.
- Prove records persist only schema-valid bounded final results and safe version/digest metadata.
- Add the implementation-owned calibration bundle contract, pure metrics/stability evaluator, and safe operator command.
- Run the complete offline calculation, structured-output, per-type fake-reviewer, and Layer 3 fixture matrices.
- Verify reviewer/generator outage, oversized context, conflicts, and render partial-success behavior without duplication.
- Verify direct generation, old diagrams without provenance, path cutover, and required frontend behavior.
- Update active docs, decision index, slice outcomes, and live status with offline versus external results separated.

## Not In Scope

- Persisting prompts, raw responses, source content, secrets, hidden reasoning, or discovery-tool output.
- Consuming diagnostics as generation context.
- Provenance/readiness UI without separate design approval.

## Target Areas

- `backend/services/readiness/` diagnostics and calibration components plus optional calibration controls in `services/llm/`
- `backend/assets/schemas/` plus readiness calibration bundle assets
- `backend/operations/management/commands/calibrate_readiness.py`
- readiness/generation/MCP tests and affected frontend compatibility tests
- active documentation and live status

## Exit Criteria

- All deterministic fixtures, check-only calibration validation, and full backend/frontend verification pass.
- A live semantic report can reach `pass` only when every human-label and ten-run target is measured; otherwise
  external certification remains visibly `not_run` and the extension is not called release-certified.
- Diagnostics can be deleted without affecting canonical behavior.
- Failure modes remain fail-safe and no context/reasoning leakage is present.
- Exact verification commands and results are recorded before the standing-permission slice commit.

## Previous Slice

- [`10-context-generation-and-workflow.md`](10-context-generation-and-workflow.md)

## Next Slice

- End of Epic 3's `04-context-backed-generation/` extension group.

## Outcome

**Implemented.** Hardened readiness debug persistence with final-result schema/size validation, safe model IDs,
exclusive cross-request run ownership, legacy-run claiming, and collision-safe attempt numbering. The MCP adapter
now shares one strict diagnostics parser across standalone readiness and context generation, persists
`generation_final_gate` snapshots for every non-error context outcome, and preserves the frozen blocker/warning/
`isError` matrix including render-warning precedence. The public host prompt propagates one run ID through both
assessment points.

**Calibration and proof.** Added the strict `graphpilot.readiness-calibration-bundle.v1` schema, an explicitly empty
unlabeled default bundle, bounded bundle/label validation, substantiated matrix coverage, pure calibration/stability
metrics, and `calibrate_readiness`. Check-only mode performs no provider construction and reports the truthful
`releaseStatus: "not_run"`; `--live` alone authorizes ten Azure reviews per fully adjudicated holdout case. Optional
Azure temperature/seed controls preserve default runtime behavior, fall back only for explicit unsupported-control
errors, and report the effective controls. Offline release fixtures exercise every real rubric facet/rating,
conditional applicability, finding/action registry, per-type fake-reviewer path, and representative Layer 3 cases.

**Compatibility.** Existing outage, size, conflict, race, and partial-render tests remain green. Added frontend
round-trip assertions for complete context trace/origins and legacy provenance-free diagrams. For the recorded
manual Playwright proof, temporary workspace fixtures were placed at canonical nested and legacy flat `.graphpilot`
paths; each editor URL was opened, `Save` → `Overwrite` was executed, browser requests showed GET/POST HTTP 200,
and the saved JSON was reread. The context trace/origins remained intact, the legacy file remained provenance-free,
and the browser console had zero warnings/errors. These disposable manual fixtures are not committed test assets;
the durable adapter/schema assertions cover the same preservation contract in the automated gate.

**Verification.** `uv run python manage.py test` passes 673 backend tests with 3 skips. `uv run python
mcp_server/smoke_test.py` passes all real-stdio tool/prompt checks. `npm run verify` passes lint with zero findings,
production TypeScript/Vite build, 407 frontend unit tests, and 29 Chromium E2E tests. `uv run python manage.py
calibrate_readiness --json` exits zero with `valid: true`, `certificationReady: false`, all unmeasured rates `0.0`,
and `releaseStatus: "not_run"`. `git diff --check` passes.

**Deviation / external gate.** No live Azure calibration was run and no human labels were fabricated. The default
bundle intentionally has zero cases. Therefore the implementation is fully offline-verified but the context-backed
workflow is not called semantically release-certified; that status remains `not_run`, exactly as the active gate
requires.

**Follow-up.** Two human reviewers must independently label and adjudicate a complete holdout bundle, after which an
operator may explicitly run `uv run python manage.py calibrate_readiness --live --json`. Only a measured `pass`
certifies the fixed rubric/prompt/deployment combination.
