# Slice 03: Historical Full Effort

## Purpose

Place the complete S15 full-effort implementation and mirrored tests under an explicit historical namespace while preserving offline reproducibility and never touching terminal run identities or generated artifacts.

## Design

Move the five `full_effort_*` modules into `services/workflow_audit/full_effort/` with concise filenames and move the three focused test modules into the mirrored test package. Create docstring-only `__init__.py` markers at `services/workflow_audit/`, `services/workflow_audit/full_effort/`, `tests/evaluation/historical/`, and `tests/evaluation/historical/full_effort/`; they export no compatibility aliases. Keep every canonical class, constant, schema identity/digest, case/schedule rule, command name/argument, output path, checkpoint/terminal behavior, and test assertion unchanged except import/patch/source paths.

`run_full_effort_evaluation.py` remains in Django's required command directory and imports the historical package directly. The five `full-effort-*.json` schemas remain in `graphpilot/schemas/`; no local `.graphpilot/evaluation/full-effort/` root is read or modified. No alias remains at the old Python paths.

## Execution Contract

- **Depends on / inputs:** committed S01 inventory/design, clean worktree, tracked S15 source/tests and canonical S15 Outcome only.
- **Outputs:** one coherent historical source/test namespace migration and focused verification commit.
- **Exclusive write ownership:** five current `full_effort_*` modules; three matching evaluation tests; new historical package `__init__.py` files; `run_full_effort_evaluation.py`; its command test only where import/patch paths change.
- **Forbidden/shared ownership:** generated S15 manifests/runs/checkpoints/terminals, all workflow-audit and generation-evaluation source/tests, schemas/cases/labels, frontend, canonical shared docs/status, `.env`, and any provider resource are forbidden.
- **Parallelism/resources:** parallel-safe with S02 only in a separate worktree. In one worktree execute sequentially. Focused tests use temporary roots and fake clients; no historical identity, live call, browser, or port.
- **Merge/integration:** S03 may commit independently after focused audit/gates; merge order follows S02 when integrating both.
- **Cancellation:** an incomplete move, stale import, test-discovery failure, or changed S15 contract blocks S03 and S04; S02 may remain valid.

## Included Work

- Perform the exact five source and three test moves from `00-group.md` and create all four required docstring-only package markers.
- Update direct/lazy imports and test patch targets atomically.
- Preserve command discovery and provider-free test coverage.
- Run independent read-only implementation audit and correct every material finding.
- Commit only after the focused broader gate passes.

## Not In Scope

- Executing `prepare`, `stage_b`, `stage_c`, resume, or any frozen S15 identity.
- Deleting/archiving source, command, schema, tests, cases, or evidence.
- Changing S15 call ceilings, schedules, outcomes, labels, reports, or stop policy.
- Sharing S15 stores/runners with active audit/certification code.

## Target Areas

- `backend/services/evaluation/full_effort_*.py`
- `backend/services/workflow_audit/full_effort/`
- `backend/tests/evaluation/test_full_effort_*.py`
- `backend/tests/evaluation/historical/full_effort/`
- `backend/operations/management/commands/run_full_effort_evaluation.py`
- `backend/tests/management/test_full_effort_evaluation_command.py`

## Focused Verification

```powershell
cd backend
uv run python manage.py test tests.evaluation.historical.full_effort tests.management.test_full_effort_evaluation_command
uv run python manage.py check
uv run python -m compileall -q services/workflow_audit/full_effort operations/management/commands/run_full_effort_evaluation.py tests/evaluation/historical/full_effort tests/management/test_full_effort_evaluation_command.py
```

Also require zero old `services.evaluation.full_effort_*` imports, unchanged schema/case digests, `git diff --check`, and an independent diff audit. Do not invoke the historical management command during this weekend slice.

## Exit Criteria

- All five modules and three tests have exactly one historical path and no old source path remains.
- Focused Django discovery, import, and compile gates pass provider-free in temporary workspaces.
- The command remains discoverable with unchanged arguments but is not executed against a historical run.
- No schema/case/identity/artifact/provider behavior changes.
- Independent audit has no unresolved critical, high, or medium finding.

## Previous Slice

[`01-repository-responsibility-audit.md`](01-repository-responsibility-audit.md)

## Next Slice

[`04-integration-parity.md`](04-integration-parity.md) after S02 also passes.

## Outcome

**Status:** Complete. Five full-effort source modules now live under `services/workflow_audit/full_effort/`; three focused tests mirror them under `tests/evaluation/historical/full_effort/`. The four package markers are docstring-only. All direct and lazy imports plus the Django command consumer use the historical path; no old module or compatibility shim remains.

**Compatibility and safety:** The five S15 schemas, visible case definitions/digest, 144/432 call ceilings, command name/arguments, output roots, checkpoint/terminal/no-rerun behavior, and stop rules are unchanged. No operator command or historical manifest/run/checkpoint/terminal identity was loaded or executed. Command tests used only new synthetic identities in temporary workspaces and proved Azure was never constructed.

**Audit:** Independent implementation review verified the exact 5/3 moves, four initializers, direct/lazy/patch consumers, active-root dependency direction, immutable S15 contracts, authorization behavior, no artifact access, preserved comments, and no unrelated change. It passed with no critical, high, medium, or low finding.

**Verification:** `uv run python manage.py test tests.evaluation.historical.full_effort tests.management.test_full_effort_evaluation_command` passed 24 tests; `manage.py check`, focused `compileall`, old-path searches, unchanged schema/case diff, untouched historical run-root check, and `git diff --check` passed. No Azure call, `.env` access, dependency, deletion, push, or deployment occurred.
