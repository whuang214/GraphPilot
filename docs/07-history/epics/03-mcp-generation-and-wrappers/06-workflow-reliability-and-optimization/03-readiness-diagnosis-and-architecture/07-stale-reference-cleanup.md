# Slice 07: Stale Reference Cleanup

> Cleanup implementation record. Deleted paths named below are historical targets of this slice and are not active repository locations.

## Purpose

Remove the dead review package and close every active path, command, schema identity, ownership list, and navigation reference made stale by the Block 2 moves or corrected Block 3 design without rewriting historical records.

## Design

Classify each match before editing:

- **retain:** historical Block 2 old-to-new path tables, historical slice Outcomes, removed-entry regression tests, genuine calibration/certification review requirements, and Git history;
- **mark superseded:** historical S03/S04 and initial S05/S06 Outcomes whose claims were true at their commits;
- **fix/remove:** active plans, contracts, schemas, services, tests, status, navigation, runnable commands, Target Areas, ownership lists, and comments that name dead paths, v2 diagnosis IDs, the old human gate, or the deleted review package.

Use `mechanical-probe` as the single active diagnosis evidence location. Do not add tombstones or archive copies for deleted review artifacts.

## Execution Contract

- **Depends on / inputs:** committed S06 correction, exact stale-reference inventory, user-authorized review-package deletion, and unchanged historical authority.
- **Outputs:** complete dead-package deletion, corrected active docs/commands/path lists/schema inventory, stale-reference evidence, and updated current-state.
- **Exclusive write ownership:** listed review-package paths; exact stale docs/tests/comments discovered by audit; navigation/status owners; this Outcome.
- **Forbidden/shared ownership:** historical Outcome facts and Block 2 migration tables, production redesign, public commands/MCP/REST names, schema identities outside readiness diagnosis, S15 identities, provider calls, `.env`.
- **Resources:** read-only searches plus offline documented commands/tests; no Azure/browser/server unless a touched documented command itself requires a safe local process.
- **Cancellation:** ambiguous historical/active classification, material audit finding, or a documented command requiring credentials/provider access blocks that item and records it explicitly.

## Included Work

- Delete the full `review-package/` contents: both HTML files, old diagnostic case, both delivery schemas, and `OBSOLETE.md`.
- Delete superseded `07-controlled-diagnosis.md` after its live-diagnosis obligations are incorporated into S08; Git records the rename/replan history.
- Remove every active obsolete review/eligibility requirement unrelated to genuine calibration or certification.
- Remove every active superseded diagnosis identity and split-contract reference.
- Correct Block 1 runnable test commands and current Target Areas/exclusive-ownership paths after the Block 2 namespace move.
- Preserve Block 2 migration tables and removed-entry regression tests explicitly as history/guards.
- Confirm `backend/README.md`, `backend/services/README.md`, backend architecture, testing strategy, schema registry inventory, decision index, current-state, docs/epics navigation, and comments are current.
- Execute every documented command touched or record why it was not run.
- Run independent cleanup audit, stale/security/link/diff checks, and relevant backend verification.
- Commit the coherent cleanup.

## Not In Scope

Diagnosis behavior changes, schema redesign, public rename, provider calls, calibration/certification changes, S15, Stage C, Block 4, dependency changes, or history rewrite.

## Target Areas

- `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/03-readiness-diagnosis-and-architecture/review-package/` (delete all files)
- `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/03-readiness-diagnosis-and-architecture/07-controlled-diagnosis.md` (delete after replacement)
- active Block 1/Block 3 slice plans and runnable commands
- `backend/README.md`
- `backend/services/README.md`
- `docs/01-architecture/01-backend-architecture.md`
- `docs/03-development-and-delivery/01-testing-strategy.md`
- `docs/02-design-and-features/decision-decisions.md`
- `docs/03-development-and-delivery/epics/00-current-state.md`
- `docs/03-development-and-delivery/epics/README.md`
- `docs/README.md`
- schema registry inventory/tests and exact stale comments/tests

## Exit Criteria

- No active dead path, obsolete review gate, package-schema reference, or v2 diagnosis identity remains.
- Historical Outcomes/migration tables remain truthful and clearly non-active.
- Genuine calibration/certification review requirements remain intact.
- Every touched runnable command has a recorded execution result or explicit non-run reason.
- `mechanical-probe` is the only active diagnosis evidence location.
- Independent cleanup audit has no unresolved critical/high/medium finding.
- Relevant tests, links, secret scan, and `git diff --check` pass.

## Previous Slice

[`06-durable-probe-enablement.md`](06-durable-probe-enablement.md)

## Next Slice

[`08-root-decision-and-transition.md`](08-root-decision-and-transition.md) after cleanup commits and the repository returns clean.

## Outcome

**Status:** Complete. The entire obsolete review package and superseded controlled-diagnosis draft were deleted with no tombstone/archive; commits `7d17ff8`, `1bcdd81`, and `5e96af7` retain history. Active Block 1 ownership/Target Areas and runnable test/compile commands now use `services.workflow_audit` and `tests.evaluation.workflow_audit`. Active Block 3 authority uses v1 manifest-bound contracts and `mechanical-probe/` as its sole tracked evidence location.

**Classification:** Block 2 migration tables, historical marked S03/S04 and initial S05/S06 Outcomes, removed-entry regression tests, genuine calibration/certification review requirements, research records, and Git history remain untouched. Active status/navigation/backend/architecture/testing owners contain no old human gate, dead package location, split contract, superseded diagnosis identity, or pre-move runtime path.

**Verification:** From `backend/`, the corrected S01 command `uv run python manage.py test tests.support.test_schema_registry tests.evaluation.workflow_audit.test_scenario_service` passed 23 tests; the corrected S02 command `uv run python manage.py test tests.evaluation.workflow_audit.test_scenario_service tests.evaluation.workflow_audit.test_client tests.evaluation.workflow_audit.test_capture_service tests.evaluation.workflow_audit.test_instrumentation_equivalence` passed 40 tests; and `uv run python -m compileall -q services/workflow_audit/scenario_service.py tests/evaluation/workflow_audit/test_scenario_service.py` passed. No documented command touched requires provider credentials.

**Audit:** Initial cleanup audit confirmed all deletion, history, calibration, navigation, scope, and naming classifications. It found one active testing-strategy “V2/package” line and the not-yet-written Outcome command record; both are corrected here. Focused re-audit passed with zero critical, high, or medium finding. No Azure call, `.env` access/change, dependency, production/public/MCP/REST/S15 identity change, Stage C, push, or deployment occurred.
