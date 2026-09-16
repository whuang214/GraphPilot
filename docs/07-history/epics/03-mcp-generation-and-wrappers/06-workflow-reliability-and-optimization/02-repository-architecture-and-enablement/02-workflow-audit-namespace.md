# Slice 02: Workflow Audit Namespace

## Purpose

Move the complete reusable Block 1 operational-audit implementation and mirrored tests into one owned namespace without changing behavior, contracts, artifacts, or evidence.

## Design

Use `services/workflow_audit/` for the eleven modules named in the group migration table and `tests/evaluation/workflow_audit/` for the nine focused tests. Drop redundant filename prefixes inside the owned package; rename only the stale facade file to `service.py`, retaining the canonical `WorkflowAuditService` symbol.

Update all internal absolute imports, the `run_workflow_audit` command, the audit stdio server's explicit dynamic import string, management/focused test imports, mock patch targets, and source-inspection checks in the same slice. In particular, preserve the S15-separation assertion in the current runner test while changing its three inspected-module imports to the new paths. Create `services/workflow_audit/__init__.py` and `tests/evaluation/workflow_audit/__init__.py` with package docstrings and no re-exports. Do not add compatibility shims under old paths. Schema keys, schema files, scenario bundle, command/tool names, frontend audit harness, artifact roots, identities, and serialized output remain exact.

## Execution Contract

- **Depends on / inputs:** committed S01 inventory/design, clean worktree, accepted Block 1 baseline.
- **Outputs:** one coherent source/test namespace migration and focused verification commit.
- **Exclusive write ownership:** the eleven current workflow-audit modules and nine matching tests; new package `__init__.py`; `operations/management/commands/run_workflow_audit.py`; `mcp_server/workflow_audit_server.py`; `tests/management/test_workflow_audit_command.py` only where its import/patch path changes.
- **Forbidden/shared ownership:** all active generation-evaluation and S15 source/tests/commands, schemas, scenarios, frontend, canonical docs, current-state, generated artifacts, and `.env` are forbidden; shared docs/status remain S04-owned.
- **Parallelism/resources:** parallel-safe with S03 only in separate worktrees. In one worktree execute sequentially. No Azure, browser, development port, shared cache, or accepted run-root use.
- **Merge/integration:** S02 may commit independently after focused audit/gates; S04 consumes it before parity.
- **Cancellation:** an incomplete move, stale import, dynamic-load failure, test-discovery failure, or behavior drift blocks S02 and S04, not isolated S03.

## Included Work

- Perform the exact source/test moves from `00-group.md` and create both required docstring-only `__init__.py` package markers.
- Update every tracked direct/dynamic import and patch/source-inspection reference, including the runner test's inspected-module imports while retaining its no-S15 assertion.
- Add or adjust characterization only if existing discovery/dynamic-import coverage cannot prove the path cutover.
- Run focused tests and compilation.
- Run independent read-only implementation audit and correct every material finding.
- Commit only after the focused broader gate passes.

## Not In Scope

- Schema/scenario/frontend move or content change.
- Capture bounds, role maps, accounting, checkpoint/terminal/report/ledger behavior changes.
- Provider-event unification, new generic infrastructure, live calls, or performance claims.
- S15 or active generation-evaluation changes.

## Target Areas

- `backend/services/workflow_audit_*.py`
- `backend/services/evaluation/full_workflow_audit_service.py`
- `backend/services/workflow_audit/`
- `backend/tests/evaluation/test_workflow_audit_*.py`
- `backend/tests/evaluation/workflow_audit/`
- `backend/operations/management/commands/run_workflow_audit.py`
- `backend/mcp_server/workflow_audit_server.py`
- `backend/tests/management/test_workflow_audit_command.py`

## Focused Verification

```powershell
cd backend
uv run python manage.py test tests.evaluation.workflow_audit tests.management.test_workflow_audit_command
uv run python manage.py check
uv run python -c "import importlib; importlib.import_module('services.workflow_audit.fake_client')"
uv run python -m compileall -q services/workflow_audit operations/management/commands/run_workflow_audit.py mcp_server/workflow_audit_server.py tests/evaluation/workflow_audit tests/management/test_workflow_audit_command.py
```

Also require zero old workflow-audit implementation imports/paths outside historical slice Outcome text, successful import of the dynamic audit module, `git diff --check`, and an independent diff audit.

## Exit Criteria

- All eleven modules and nine tests have exactly one new path and no old source path remains.
- Django focused discovery and the explicit stdio audit adapter import pass.
- Existing characterization proves call/result/JSON/SVG/write equivalence remains unchanged.
- No schema, scenario, artifact, command name, public transport, provider, or S15 change exists.
- Independent audit has no unresolved critical, high, or medium finding.

## Previous Slice

[`01-repository-responsibility-audit.md`](01-repository-responsibility-audit.md)

## Next Slice

[`04-integration-parity.md`](04-integration-parity.md) after S03 also passes.

## Outcome

**Status:** Complete. Eleven workflow-audit source modules now live under `services/workflow_audit/`; nine focused tests mirror them under `tests/evaluation/workflow_audit/`. Both package markers are docstring-only. The command, stdio adapter, internal imports, mock targets, cross-test helper, and source-inspection assertions use the new paths; no old module or compatibility shim remains.

**Deviation and correction:** The first command was issued from the repository root, so `manage.py` was not found and no test ran. The first real focused run then exposed 27 deterministic path errors because three moved `__file__` roots still used the old depth. Updating the run-service backend root, browser-service repository root, and scenario-test backend root by one directory fixed the root cause. Direct assertions prove the resolved paths are exact.

**Audit:** Independent implementation review verified the 11/9 moves, all direct/dynamic consumers, package discovery, symbols/comments, no-S15 separation, and unchanged schemas/scenarios/artifacts/public behavior. Its initial off-by-one `Path.parents` finding was disproved with direct zero-indexed path assertions; re-audit passed with no critical, high, or medium finding.

**Verification:** `uv run python manage.py test tests.evaluation.workflow_audit tests.management.test_workflow_audit_command` passed 79 tests; `manage.py check`, dynamic import of `services.workflow_audit.fake_client`, focused `compileall`, direct path-root assertions, stale-reference searches, and `git diff --check` passed. No Azure call, S15 identity access, schema/scenario/frontend change, dependency, deletion, push, or deployment occurred.
