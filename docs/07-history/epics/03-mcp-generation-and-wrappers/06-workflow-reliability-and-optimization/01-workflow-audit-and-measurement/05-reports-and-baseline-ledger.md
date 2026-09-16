# Slice 05: Reports and Baseline Ledger

## Purpose

Produce bounded machine/human workflow-audit reports, deterministic ranked findings, compatibility-gated cumulative baselines,
and one independent provider-free operator command.

## Design

`report.json` is machine authority; `report.md` presents the same identities, completeness, coverage, accounting, quality,
recovery, browser, and ranked findings. Ranking prioritizes failures/reliability/quality, then measured complete-wall
contribution, then material unknowns that block attribution. A W01–W22 catalog supplies owner and safe diagnostic defaults;
when root cause is unproven, the smallest action is a diagnostic proof rather than a behavioral fix.

The baseline ledger has append-only semantics with bounded entries and atomic expected-digest replacement. Entries contain
baseline/run identity, report path/digest, compatibility key, and summary—not full observations. Comparison requires an exact
compatibility key; incompatible runs are explicitly incomparable.

Add `run_workflow_audit` as the canonical independent provider-free command. Remove only `audit_offline` and its import from
`run_full_effort_evaluation`; retain S15 `offline|prepare|stage_b|stage_c`. Migrate existing workflow-audit tests and docs rather
than dropping coverage.

## Execution Contract

- **Depends on / inputs:** committed S03 immutable observations/runner and S04 digest-bound browser evidence.
- **Outputs:** authoritative JSON/Markdown, ranked findings, compatibility ledger, independent command, and complete integrated
  package consumed by S06.
- **Exclusive write ownership:** workflow-audit report/analysis/ledger services and tests, `run_workflow_audit`, removal of only
  the old `audit_offline` entry, and command/current documentation migration.
- **Forbidden/shared ownership:** scenario/capture/runner/frontend behavior and S15 `offline|prepare|stage_b|stage_c` are
  forbidden; schema registry and canonical docs/status are integration-owner files.
- **Parallelism/resources:** no parallel write slice because report eligibility/command behavior requires committed S04 evidence;
  use one unique control output root and report/ledger/run IDs with expected-digest updates.
- **Merge/integration gate:** report/Markdown parity, ranking, compatibility, ledger concurrency, no-Azure command, migrated
  coverage, and combined backend/frontend/MCP/browser gates must pass before S06.

## Included Work

- Implement deterministic report aggregation, completeness/coverage, non-overlapping accounting, quality/recovery/browser
  summaries, and ranked findings.
- Write schema-valid bounded immutable `report.json` and deterministic `report.md`.
- Implement compatibility-key calculation and strict comparison rejection for differing inputs/environments.
- Implement path-safe baseline ledger load/append with unique IDs, expected-digest concurrency, and entry bounds.
- Implement the provider-free `run_workflow_audit` management command with explicit run identity, diagnostic/baseline mode,
  scenario selection, browser requirement, output paths, and JSON stdout summary.
- Remove the old S15-named `audit_offline` entry and update tests, backend architecture, testing strategy, READMEs, and S15's
  historical command note atomically.
- Add report, ranking, Markdown parity, ledger atomicity/stale-writer, compatibility, command/no-Azure, and migration tests.

## Not In Scope

- Automatic behavioral changes from ranked findings.
- Importing S13–S15 observations into the baseline ledger.
- Live provider flags or authorizations, promotion, or certification.
- Repository reorganization beyond the internal class rename and command ownership correction.

## Target Areas

- workflow-audit `report_service.py`, `artifact_store.py`, and `ledger_service.py` under `backend/services/workflow_audit/`
- `backend/operations/management/commands/run_workflow_audit.py`
- `backend/operations/management/commands/run_full_effort_evaluation.py`
- focused evaluation/management/schema tests
- `backend/README.md`, `backend/services/README.md`, backend architecture, testing strategy, S15 outcome note, and navigation

## Exit Criteria

- JSON and Markdown report the same run identity, completeness, evidence limitations, accounting, quality, browser, and
  findings without unsupported values.
- Every ranked row has evidence refs, owner/confidence, smallest fix or diagnostic proof, alternative, trade-off, benefit
  ceiling, offline/live proof, and disposition.
- Report/ledger artifacts are bounded, secret-safe, path-safe, immutable by identity, and reject stale/concurrent writes.
- Comparison occurs only for exact compatibility keys; incompatible runs produce no percentages.
- Baseline append requires complete successful provider-free, failure/recovery/security, and browser-safe gates.
- `run_workflow_audit` constructs/calls no Azure client; the old command retains only S15 operations.
- Migrated focused tests, full backend tests, Django check, stdio smoke, compile check, frontend verify, and `git diff --check`
  pass.

## Previous Slice

[`04-browser-completion-proof.md`](04-browser-completion-proof.md)

## Next Slice

[`06-fresh-provider-free-baseline.md`](06-fresh-provider-free-baseline.md)

## Outcome

**Status:** Complete. Slice 05 added immutable schema-valid `report.json` and deterministic parity `report.md`, complete
W01–W22 coverage/accounting/quality/recovery/browser aggregation, expected-guard gate evaluation, deterministic ranked findings,
and exact compatibility keys/comparison. The append-only baseline ledger binds accepted eligible reports to immutable
manifests/scenarios/keys with canonical digest, unique identities, expected-digest stale-writer rejection, in-process path locks,
and atomic persistence.

**Command migration:** `run_workflow_audit diagnostic|baseline` now owns the independent provider-free workflow. Baseline mode
requires a fully clean tracked/untracked worktree, exact default 19-observation schedule, `built_preview` manifest identity,
mandatory browser proof, complete eligible report, and ledger append; diagnostic permits bounded subsets and optional browser
proof. The S15-named `audit_offline` operation/import was removed atomically while `offline|prepare|stage_b|stage_c` remain
unchanged. The command has no Azure client or live-authorization argument.

**Audit and corrections:** Implementation audit documentation findings were resolved across backend/testing/S15 history and
current slice outcomes. Markdown parity was already explicitly tested; a new regression verifies that baseline clean-tree
validation includes untracked files. Reports treat expected blocked/provider-failure guards as proof rather than product defects,
label browser timing as a representative pair, preserve unavailable values, and emit no comparison percentages when keys differ.
Independent re-audit passed with no critical, high, or medium finding.

**Verification:** Focused report/ledger/command/runner/S15-command tests passed 31 tests after final corrections. The complete
backend suite passed 991 tests with 5 skipped; Django check, stdio smoke, compileall, and `git diff --check` passed. No provider/network call, dependency, schema change, `.env` access,
file deletion, or frontend behavior change occurred.

**Follow-up:** Slice 06 runs the committed baseline command from a clean exact HEAD, validates the immutable report/ledger and
compatibility key, performs the block integration audit/gates, and records the Block 2 parity handoff.
