# Slice 06: Durable Probe Correction

## Purpose

Correct the committed diagnosis implementation so its existing provider-free lifecycle safely executes audited live manifests using v1 contracts and no redundant package schema.

## Background

Commit `5e96af7` added durable events, repair-trigger capture, interruption retention, a thin live command, tests, and a new mechanical case. Those substantive capabilities remain. This correction reverts only unnecessary contract ceremony and aligns authorization with one strict run manifest.

## Design

Keep the case, run-manifest, and observation schema identities at v1. The run manifest is the sole authority for package ID, hypothesis, source/assets, controls, budget, scope, rollback, output identities, and digest; the command consumes it plus its bound case directly.

The case remains mechanical and non-certifying, with no obsolete review, semantic-expectation, or execution-eligibility gate fields. The observation retains bounded lifecycle events, exact validation `{code,path}`, nullable natural repair trigger, capture completeness, and interruption reconstruction. `ContextReadinessService`, prompts, rubrics, policy, and Block 2 capture behavior remain unchanged.

## Execution Contract

- **Depends on / inputs:** committed corrected S05 plan, implementation `5e96af7`, and unchanged production readiness contracts.
- **Outputs:** corrected v1 schemas/service/registry/tests/command/docs with manifest-only authority.
- **Exclusive write ownership:** `readiness_diagnosis_service.py`, diagnosis schemas/registry, focused tests, command/test, and named backend docs.
- **Forbidden/shared ownership:** Block 2 services/artifacts, readiness prompts/rubrics/policy/runtime behavior, dead review-artifact cleanup, provider calls, `.env`, S15, Stage C.
- **Resources:** fake clients and temporary roots only; no Azure/browser/ports.
- **Cancellation:** material behavior drift, weakened lifecycle evidence, unapproved dependency, or unresolved audit/check failure blocks S07.

## Included Work

- Characterize the committed version bump and split package authority before correction.
- Restore all three readiness-diagnosis identities and examples to v1 while retaining substantive mechanical fields.
- Fold every concrete authorization field into the manifest and remove the split contract/registry/test references.
- Update command preflight to validate one manifest authority and its bound case before Azure construction.
- Preserve exact repair-trigger order, bounded known-event interruption retention, capture completeness, terminalization, role ceiling, and no-rerun behavior.
- Add rejection coverage for removed gate fields and for legacy split authority.
- Run independent implementation audit, focused/full backend, schema/digest/security/compatibility, and Block 2 unchanged checks.
- Commit the verified forward correction.

## Not In Scope

Review-package deletion, repository-wide stale-reference cleanup, provider calls, readiness behavior correction, prompt/schema/rubric/policy changes, frontend work, calibration/certification, S15, or Stage C.

## Target Areas

- `backend/services/workflow_audit/readiness_diagnosis_service.py`
- `backend/assets/schemas/readiness-diagnosis-case.json`
- `backend/assets/schemas/readiness-diagnosis-run-manifest.json`
- `backend/assets/schemas/readiness-diagnosis-observation.json`
- `backend/services/shared/schema_identities.py`
- `backend/tests/evaluation/workflow_audit/test_readiness_diagnosis_service.py`
- `backend/operations/management/commands/run_readiness_diagnosis.py`
- `backend/tests/management/test_readiness_diagnosis_command.py`
- canonical backend architecture/service/testing docs

## Exit Criteria

- All three diagnosis schema identities remain v1 and are meta/example/cross-digest valid.
- The manifest alone expresses package/hypothesis/source/control/budget/scope/rollback authority.
- Explicit live construction is impossible before every local gate.
- Known events survive interrupted terminalization; uncertain facts remain uncertain.
- Exact validation and repair-trigger evidence are bounded and digest-bound.
- Checkpointed/terminal identities never rerun.
- Generation/semantic-review roles and side effects are unreachable.
- No Block 2 artifact or behavior changes.
- Independent audit and required checks have no material failure.

## Previous Slice

[`05-causal-diagnosis-plan.md`](05-causal-diagnosis-plan.md)

## Next Slice

[`07-stale-reference-cleanup.md`](07-stale-reference-cleanup.md) after the corrected implementation commit.

## Outcome

> **Historical `5e96af7` record — superseded only where the correction above says so; retained verbatim below.**

**Status:** Complete pending implementation commit. The provider-free lifecycle now consumes a strict v2 mechanical case plus one v1 experiment package; freezes a v2 package/hypothesis/commit/control-bound manifest; records bounded lifecycle events, exact validation `{code,path}`, natural repair trigger, capture completeness, and v2 observation; preserves known ledger events on interrupted terminalization while marking only an unmatched start uncertain; and retains checkpoint/terminal no-rerun behavior. The new `run_readiness_diagnosis` command requires explicit `--live`, authorized package digest, clean exact HEAD, raw asset closure, live mode, budget, case/source binding, and configuration before constructing Azure, then delegates only to `ContextReadinessService` through the injected diagnosis service.

**Cleanup and compatibility:** Only the user-approved `review.html` and `adjudicate.html` were deleted. The old package case and two delivery schemas remain tracked, carry obsolete/deprecated notices, and have no active consumer. The new active mechanical case is `case-readiness-diagnostic-block3-mechanical-return-authorization-01`. Block 2 services, scenarios, captures, accepted artifacts, compatibility evidence, prompts, rubrics, readiness behavior, and public MCP/REST contracts are unchanged. The existing effort benchmark remains separate.

**Audit and deviations:** Independent implementation audit confirmed package/HEAD/asset/budget/role gates, no forbidden reachability, safe capture, repair-trigger order, interruption/no-rerun truthfulness, schema closure, and authorized cleanup. Its three medium findings—bounded full JSON-path grammar, explicit rejection tests for legacy human fields, and in-package obsolete markings—were corrected; focused re-audit passed. Final review also caused interrupted observations to mark capture completeness unknown and exposed an old repository test that incorrectly required every schema ID to end in `.v1`; the guard now enforces namespace-first positive `.vN` identities and accepts the intentionally breaking diagnosis v2 contracts. Final re-audit passed with no material finding.

**Verification:** The final post-audit focused gate passed 16 tests; the S06 module/command gate passed 15 tests; Django check, compileall, four-schema meta/example/cross-digest closure, approved deletion/retention checks, secret/raw-content scan, `git diff --check`, and Block 2 unchanged-path checks passed. The full backend suite passed 1006 tests with 5 skipped. No Azure call, `.env` access/change, dependency, generated/S15 identity, Stage C, browser, push, or deployment occurred.

**Correction:** Complete. The case, run-manifest, and observation contracts are restored in place to v1 while retaining mechanical scope, live/fake mode, reasoning effort, durable lifecycle events, exact validation `{code,path}`, natural repair trigger, capture completeness, interrupted known-event retention, terminalization, and no-rerun. The manifest now owns package ID, hypothesis, case path/digest, source commit/assets, provider controls/roles/ceiling, cumulative budget, non-certifying scope, rollback, output identity, policy, and canonical digest. The redundant package schema/registry/service path is deleted; the command now requires `--manifest` plus exact digest and validates every local gate before Azure construction.

**Correction audit:** Independent review's initial registry finding was reclassified after source confirmation: `SchemaRegistry` is the repository's existing unified inventory and no diagnosis runtime imports `generation_contracts`. Actionable test findings were corrected with explicit artifact key/ID checks, v2 rejection, fake/live injected mode, asset escape, 998/999/1000 budget edges, terminal digest mismatch, and input-limit coverage. Focused re-audit passed with zero critical, high, or medium finding.

**Correction verification:** The diagnosis/command/identity gate passes 24 tests; the wider readiness/workflow-audit gate passes 94 tests; full backend passes 1,014 tests with 5 skipped. Three v1 schemas are meta/example/cross-digest valid, the tracked mechanical case digest matches, package schema is absent, command help, Django check, compileall, secret/raw-content scan, Block 2 unchanged-path check, and `git diff --check` pass. No Azure call, `.env` access/change, dependency, live identity, S15/Stage C access, browser, push, or deployment occurred.
