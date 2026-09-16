# Slice 03: Audit Runner and Recovery

## Purpose

Deliver the independent provider-free runner and immutable observation lifecycle for normal, blocked, repair, failure,
interruption, finalized-recovery, and no-rerun workflow outcomes.

## Design

Refactor `FullWorkflowAuditService` to `WorkflowAuditService` in its existing file, preserving current W01–W22, real-stdio,
production-service, cold/warm, and recovery behavior while replacing `FullEffortCaseSetService` and
`FullEffortFakeClientFactory` dependencies in both the runner and fake client.

Freeze one exact run manifest before execution. Each declared observation has unique scenario/thermal/artifact/process identities,
exclusive completion evidence, and bounded checkpoint/terminal state. A definitely started or uncertain provider call makes the
observation terminal for no-rerun purposes. Provider-free fake calls remain safe, but the lifecycle must already preserve the
stricter future-provider invariant.

## Execution Contract

- **Depends on / inputs:** committed S01 scenarios/contracts and S02 capture/client/accounting APIs.
- **Outputs:** immutable manifests/observations, independent scripted fake behavior, real-stdio runner, and exact generated/
  blocked/error/recovery identities consumed by S04 and S05.
- **Exclusive write ownership:** `workflow_audit/service.py`, workflow-audit runner/artifact-store/fake-client modules,
  `workflow_audit_server.py`, and focused runner/MCP tests.
- **Forbidden/shared ownership:** frontend/browser/report/ledger code is forbidden; removal of the old command, canonical docs,
  current state, and shared schema registration remain S05/integration-owner scope.
- **Parallelism/resources:** no parallel write slice because S04/S05 require committed S03 observation/path/digest behavior;
  each test receives unique control/evaluated temporary roots, scenario/run/observation IDs, and MCP subprocess.
- **Merge/integration gate:** all provider plans, W01–W22 coverage, immutable terminal/resume, recovery zero-call, real-stdio,
  security, and full backend/MCP gates must pass before S04.

## Included Work

- Implement scenario selection/scheduling and exact cold/warm artifact/process state.
- Implement path-safe immutable run storage for manifests, metrics, checkpoints, terminals, and completed observations.
- Refactor the existing workflow audit service/fake client off all S15 runtime imports and identities.
- Execute real MCP stdio and production JSON 1/JSON 2/readiness/generation/layout/persistence/render paths.
- Cover generated, blocked, response/candidate repair, provider failure/interruption, and recovery outcomes.
- Prove mandatory final readiness exactly once, no standalone readiness, exact call order/budgets, and zero Azure construction.
- Prove finalized-output recovery returns the owned diagram/editor link without another provider call.
- Add resume/terminal/no-rerun, immutable identity, collision, partial-write, cleanup, and user-workspace isolation tests.

## Not In Scope

- Browser navigation, W22 completion evidence, final reports, ranked findings, ledger updates, or command migration.
- Retrying terminal/uncertain identities, provider-backed execution, or behavioral fixes.
- Broad evaluation-framework or repository restructuring.

## Target Areas

- `backend/services/workflow_audit/service.py`
- `backend/services/workflow_audit/artifact_store.py` and `run_service.py`
- `backend/mcp_server/workflow_audit_server.py`
- focused evaluation/management/MCP tests and temporary workspaces

## Exit Criteria

- The runner accepts only validated approved scenarios and writes one immutable manifest before observation execution.
- The six anchors run cold/warm and guard scenarios reach their declared outcome without Azure construction/calls.
- Every W01–W22 boundary has explicit measured/derived/simulated/imported/not-reached/not-applicable/not-measured status and
  reason where required.
- Generated outputs are canonical, provenance-valid, persisted, rendered, and bound to the exact request/scenario identity.
- Blocked/failure/interrupted observations retain safe evidence and create no fabricated canonical output/link.
- Finalized recovery makes zero additional fake/provider calls; completed or uncertain identities cannot rerun.
- Instrumentation equivalence, focused runner/recovery tests, full backend tests, Django check, stdio smoke, compile check, and
  `git diff --check` pass.

## Previous Slice

[`02-capture-and-evidence-adapters.md`](02-capture-and-evidence-adapters.md)

## Next Slice

[`04-browser-completion-proof.md`](04-browser-completion-proof.md)

## Outcome

**Status:** Complete. Slice 03 replaced the S15-coupled audit implementation with the canonical `WorkflowAuditService` facade,
independent scripted fake clients, immutable manifest/observation/checkpoint/terminal storage, and a real-stdio runner covering
all 19 declared cold/warm/guard observations. The matrix produced 16 generated, one correctly blocked, and two provider-error
observations with 56 fake calls, zero Azure calls, exact repair/final-review role order, complete W01–W22 evidence, and schema-
valid terminal state.

**Reliability:** Completed runs resume with zero execution/provider calls; uncertain checkpoints become immutable interrupted
observations without rerun. Finalized-output recovery validates owned persisted output/editor link and adds zero provider calls.
Cold/warm anchors reuse one initialized MCP process per scenario while recording artifact and process state separately.

**Audit and corrections:** Initial audit correctly identified unnecessary fake-class re-exports, which were removed while
retaining the intended canonical service composition. The temporary `audit_offline` bridge was retained through S03 and then
removed atomically by S05 in favor of `run_workflow_audit`. Added completed-resume, failed-call-ceiling, and concurrent
checkpoint/terminal regressions. Self-review also corrected
browser accounting from false zero to unavailable and treated a correct readiness block as passing policy with downstream
quality not reached. Independent re-audit passed with no critical, high, or medium finding.

**Verification:** Focused artifact/runner/management tests passed 16 tests after corrections. The complete backend suite passed
965 tests with 5 skipped; `uv run python manage.py check`, `uv run python mcp_server/smoke_test.py`, compileall, and
`git diff --check` passed. No Azure/provider call, `.env` access, S15 identity load/resume, frontend change, or user artifact
write occurred.

**Follow-up:** Slice 04 binds one exact generated representative observation to built-preview W22 browser evidence; Slice 03
remains baseline-ineligible until that proof passes.
