# Slice 02: Live Harness

## Purpose

Extend the existing workflow-audit capture/browser/report seams with one concrete live-anchor executor that can run the approved request through real stdio MCP and production generation while preserving exact budgets, checkpoints, safe events, terminalization, and no-rerun.

## Design

Add an evaluation-only live adapter rather than changing `run_workflow_audit`, whose command remains provider-free. The adapter injects the production `DiagramGenerationService` with `AzureLLMClient` wrapped by `WorkflowAuditCapturingClient`, the existing validation callback and `WorkflowAuditObserver`, and a durable bounded metric sink. A specialized stdio MCP entry point uses this factory without altering public tools or production defaults.

This is the minimal evidence-complete option: adding live mode to `run_workflow_audit` would weaken its zero-Azure invariant; invoking the normal MCP server without injection would lose durable per-role capture/checkpoint control; cloning the audit framework would duplicate normalization/browser/report code. The adapter adds only manifest/lifecycle ownership and a live factory while reusing existing capture, metric, browser, and report primitives.

Before Django imports settings for this command, `manage.py` forces `graphpilot.live_anchor_settings` and rejects any conflicting `--settings`; that evaluation-only module disables `dotenv.load_dotenv` before importing base settings. Before importing `mcp_server.server`, `live_anchor_server.py` applies the same no-op defense but does not blank Azure variables. The audited parent passes only an allowlisted inherited environment containing required runtime/Azure settings and unique anchor controls. Neither parent nor child reads, logs, copies, or changes `.env`; missing inherited configuration blocks before dispatch.

One manifest binds source commit/assets, approved anchor/approval digests, evaluated/control workspaces, role ceilings, medium control, browser ports, output identity, cumulative budget, and rollback. The service checkpoints before dispatch, persists safe lifecycle events around every call, and terminalizes generated/blocked/failed/uncertain outcomes without rerun.

## Execution Contract

- **Depends on / inputs:** audited Block 5 plan, frozen anchor contract shape, existing workflow-audit capture/contracts/browser/report/storage, production MCP/generation seams.
- **Outputs:** live-anchor schemas/service/artifact store/command/MCP adapter/tests/docs and S02 implementation commit.
- **Exclusive write ownership:** new `live_anchor_*` evaluation modules/schemas/command/tests, `mcp_server/live_anchor_server.py`, named backend docs, S02 Outcome.
- **Forbidden/shared ownership:** `run_workflow_audit` provider-free semantics, anchor content/approval, generation/readiness policy, public MCP tools/routes, existing baseline artifacts, provider calls, `.env`, S15/Stage C.
- **Parallelism/resources:** parallel-safe with S01 in a separate worktree; temporary control/evaluated workspaces; no live provider/browser port.
- **Cancellation:** production behavior change outside injected evaluation seam, dependency addition, unbounded/raw capture, no-rerun weakness, schema conflict, or material audit/check failure returns for review.

## Included Work

- Define strict v1 live-anchor manifest, observation, terminal, and safe result/report contracts with canonical examples/digests.
- Reuse workflow-audit measurement/capture/browser primitives; do not duplicate LLM metadata normalization.
- Add explicit `run_live_workflow_anchor` command requiring `--live`, manifest path+digest, clean HEAD/assets/approval, configured provider, absent identities, and exact budget before Azure construction.
- Add real stdio MCP adapter with injected audited live generation service.
- Bound roles to 1/1/1/1/2/2/1 and maximum 9; reject unknown/extra/duplicate/out-of-order roles.
- Persist checkpoint before MCP dispatch, started/completed/failed events durably, complete generated/blocked/failure observations, and uncertain terminal on interrupted checkpoint resume.
- Add provider-free fake tests for generated first-valid, every natural repair lane, blocked, provider failure, capture failure, process interruption, collision, terminal resume/no-rerun, secret/path/size, role/budget, and compatibility.
- Add API/browser adapter dry proof over a generated fake diagram on unique temporary ports.
- Independently audit implementation and run focused/full backend/frontend/security/compatibility gates before commit.

## Not In Scope

Anchor approval, live execution, production generation changes, Block 1 baseline mutation, optimization, effort promotion, calibration/certification, representative matrix, S15, or Stage C.

## Target Areas

- `backend/assets/schemas/live-workflow-anchor-*.json`
- `backend/services/workflow_audit/live_anchor_*.py`
- `backend/operations/management/commands/run_live_workflow_anchor.py`
- `backend/mcp_server/live_anchor_server.py`
- matching evaluation/management/MCP tests
- backend/service/architecture/testing docs
- this Outcome

## Exit Criteria

- One explicit-live, manifest-bound, max-nine executor reaches production seams only after every local gate.
- Safe capture covers host/MCP/provider/local/browser boundaries without influencing provider calls.
- Failure/interruption/collision/terminal resume can never rerun a started identity.
- Existing provider-free workflow audit, public APIs, generation/readiness behavior, and Block 1/2 artifacts remain unchanged.
- Independent audit and required tests have no material finding.

## Previous Slice

None after plan; may run in parallel with S01 in a separate worktree.

## Next Slice

[`03-live-anchor.md`](03-live-anchor.md) after S01 approval and S02 commit.

## Outcome

**Status:** Complete.

**Implementation:** The working tree now contains six strict digest-valid `graphpilot.evaluation.live-workflow-anchor-*.v1` contracts, immutable compatibility/workspace-bound artifact storage, an exact max-nine natural-role guard, shared safe provider/generation capture, exact source staging, allowlisted no-dotenv stdio injection, checkpoint-before-dispatch execution, generated/blocked/failed/interrupted terminalization, pre-browser complete-wall accounting, and an exact API/browser evidence adapter. The public MCP surface, provider-free `run_workflow_audit`, production generation policy, and accepted artifacts remain unchanged.

**Verification:** Provider-free gates passed 35 focused schema/live-harness/command tests, 144 workflow-audit/readiness/live-command/public-MCP integration tests, and the full backend suite of 1,045 tests with 5 skipped. Six schemas meta-validate with valid canonical/digest examples; dedicated no-dotenv settings check, command bootstrap/help/conflicting-settings proof, Python compilation, Django check, `git diff --check`, secret scan, and protected production/Block 1–2 path checks pass. Real stdio fake coverage reached clean generation, every natural repair lane, readiness block, and provider failure; injected tests cover diagnostics inventory, capture failure, process interruption, checkpoint resume/no-rerun, artifact tamper/collision, secret/path/size rejection, approved-package compatibility, host accounting, and API/browser proof.

**Audit and deviations:** Initial implementation audit confirmed all core lifecycle, capture, role, stdio, browser, synthesis, compatibility, and no-drift behavior but found one critical parent-process dotenv issue plus stale test-count wording. A command-handle guard was insufficient because Django settings load first. `manage.py` now detects only `run_live_workflow_anchor`, rejects conflicting settings, and forces `graphpilot.live_anchor_settings` before Django import; that module and the child adapter disable dotenv, while all default commands remain unchanged. Source-order, subprocess-conflict, child-environment, and help tests pass. Re-audit passed with no remaining critical/high/medium finding. A real built-preview browser run belongs to S03; S02 uses injected offline runners. No live call, `.env` read/change, historical package change, S15/Stage C access, or dependency occurred.

**Follow-up:** Commit this verified harness. S03 remains blocked until the committed manifest surface receives its independent pre-dispatch audit.
