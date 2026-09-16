# Slice 04: Integration Parity

## Purpose

Integrate both namespace migrations, update current canonical owners, run complete repository gates, and prove exact compatible Block 1 behavior/performance parity before Block 3 begins.

## Design

Run only after S02 and S03 have independent verified commits. First audit their combined diff and update the current implementation maps in `backend/services/README.md`, the project layout and command navigation in `backend/README.md`, the module-shape and evaluation-ownership sections of `docs/01-architecture/01-backend-architecture.md`, and the mirrored test map in `docs/03-development-and-delivery/01-testing-strategy.md`. Record the accepted asymmetric namespace decision in `docs/02-design-and-features/decision-decisions.md`, then update parent roadmap/epic/docs navigation, slice Outcomes, and current-state. Historical Block 1/S15 slice Outcomes retain their original paths as point-in-time evidence.

The parity run uses a new immutable identity against a tracked-clean commit, the unchanged complete 19-observation schedule, built-preview browser proof on isolated ports, and zero Azure. It appends one accepted baseline entry only if the report is complete and compatible. Compare output outcomes, call role/order/count, quality, recovery/no-rerun, diagram/browser identity, complete-wall domains, cold/warm timing, report completeness, and compatibility key to the accepted Block 1 authority. Timing differences are reported, not selectively rerun; a material unexplained regression returns to the owning move.

## Execution Contract

- **Depends on / inputs:** passed committed S02/S03, accepted Block 1 baseline/report/ledger/key, clean integration worktree.
- **Outputs:** synchronized canonical docs/status, full verification evidence, new immutable compatible baseline package/ledger entry, completed Outcomes, Block 3 starting seam, and integration commit.
- **Exclusive write ownership:** shared current docs/status/Outcomes, generated gitignored parity run and ledger, integration-only corrections.
- **Forbidden/shared ownership:** behavior/schema/prompt/rubric/example/provider changes, S15 identities/artifacts, old baseline mutation, unrelated user files, `.env`, push/deploy.
- **Resources:** one worktree; ports `15173`/`18080`; unique Playwright session/profile; unique control/evaluated roots and run/baseline/observation identities; sequential cold/warm order; no concurrent measurement.
- **Cancellation:** any failed full gate, incompatible key, output/quality/recovery drift, unresolved browser issue, or material performance regression returns to S02/S03 and blocks Block 3.

## Included Work

- Combined source/import/dynamic-entry/security/secret/compatibility audit and correction.
- Update `backend/services/README.md`, `backend/README.md`, `docs/01-architecture/01-backend-architecture.md`, `docs/03-development-and-delivery/01-testing-strategy.md`, and `docs/02-design-and-features/decision-decisions.md`, plus parent navigation/status owners.
- Run complete backend, Django, stdio, compile, frontend, browser, diff, and stale-reference checks.
- Commit a clean pre-measurement integration candidate.
- Execute one new provider-free Block 1 baseline and idempotent no-rerun reuse check.
- Validate manifest/report/browser/ledger/observation/terminal digests and identities.
- Compare against the exact accepted baseline only when compatibility keys match.
- Run independent block implementation/exit audit and resolve every material finding.
- Record final Outcomes, current-state, handoff, commits, and Block 3 transition.

## Not In Scope

- Azure calls, S15 execution, Stage C, readiness diagnosis/correction, optimization, live anchor, certification, or promotion.
- Favorable reruns after a valid candidate measurement.
- Forcing percentages when compatibility differs.

## Target Areas

- `backend/services/README.md` and `backend/README.md`
- `docs/01-architecture/01-backend-architecture.md`
- `docs/03-development-and-delivery/01-testing-strategy.md`
- `docs/02-design-and-features/decision-decisions.md`
- this Block 2 group and slice Outcomes
- parent workflow-roadmap and Epic 3 navigation
- current-state board
- `.graphpilot/evaluation/workflow-audit/` generated parity run and ledger

## Integration Verification

```powershell
cd backend
uv run python manage.py test
uv run python manage.py check
uv run python mcp_server/smoke_test.py
uv run python -m compileall -q api mcp_server services tests
cd ..\frontend
npm run verify
cd ..
git diff --check
```

The parity command uses a new exact `run-workflow-audit-block2-parity-*` identity and the same complete baseline mode/control-workspace contract recorded by Block 1. Its generated report must be compared to `baseline-workflow-audit-block1-baseline-20260724-01`; all checks remain provider-free.

## Exit Criteria

- S02/S03 focused and combined audits have no unresolved material finding.
- All full backend/frontend/MCP/browser/security/reference gates pass.
- The new report and ledger entry are complete, immutable, secret-safe, and share exact identities/digests.
- The compatibility key equals `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`.
- Outcomes, provider call schedule, quality, recovery/no-rerun, canonical outputs, and representative browser identity match; timing has no material unexplained regression.
- Active behavior/public contracts remain unchanged and Block 3 has a clear reusable workflow-audit capture/checkpoint seam.
- Canonical docs/status and durable weekend handoff are current; nothing is pushed or deployed.

## Previous Slice

[`02-workflow-audit-namespace.md`](02-workflow-audit-namespace.md) and [`03-historical-full-effort.md`](03-historical-full-effort.md)

## Next Slice

Audit and plan [Block 3: Readiness Diagnosis and Architecture Decision](../04-block-03-readiness-diagnosis-and-architecture.md) only after this slice passes.

## Outcome

**Status:** Complete. The clean integrated candidate is commit `0b0b21903e293f6ab36aa61bb38d7ce9b97098bd`, after plan `0012602`, workflow-audit move `a5d6ffe`, and historical-S15 move `2f57eca`. Current backend architecture, service, command, testing, decision, navigation, and status owners describe the lifecycle namespaces; public names, schemas, prompts, fixtures, artifacts, provider policy, and behavior remain unchanged.

**Verification:** `cd backend; uv run python manage.py test` passed 991 tests with 5 skipped; `manage.py check`, the real-stdio 13-tool/one-prompt smoke test, and `compileall -q api mcp_server services tests` passed. `cd frontend; npm run verify` passed lint/build, 419 unit/component tests, and 43 Chromium E2E tests. Stale-reference, dynamic-entry, dependency-direction, secret, diff, browser-session, and port-cleanup checks passed.

**Provider-free parity:** Baseline `baseline-workflow-audit-block2-parity-20260724-01` from run `run-workflow-audit-block2-parity-20260724-01` completed 19/19 observations: 16 generated, one expected block, two expected errors, 56 fake calls, and zero Azure calls. Manifest `sha256:688e6377965e108b7ea9866add349d45871d9bcdf9d83aa28abdb68775101813`, report `sha256:c9be2395cda3a4498f3d409bc03173ea72e476b4e1ba675da1d628685612e7d0`, browser aggregate `sha256:0b97d6e364e0361b85fcb9069e30425cff0bee59ef70dea90ab4faf275afb5b0`, and ledger `sha256:1a603588ae26282cc32cab8bda75c1ae90af4168e37d6a6d23d97da804dbd9eb` are accepted. Idempotent reuse returned all four digests unchanged with observation/browser/report/ledger reuse and no work reissue.

**Comparison:** The compatibility key exactly remains `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`. All 19 normalized observation structures, two browser structures, 16 canonical diagrams after removing only timestamps and newly materialized request/manifest digests, and 16 SVG byte streams match. Quality has zero failures; recovery is 4/4 with two finalized-output reuses, two terminal no-reruns, and zero post-recovery calls. Both browser loads retain exact 8-node/7-edge identity and no console/page/network errors. Complete wall improved from 25,772.9598 to 23,717.6998 ms (`-2,055.26 ms`, `-7.974482%`); every measured non-Azure domain decreased and Azure remained zero.

**Audit and handoff:** Independent exit review recomputed manifest/report/browser/ledger/observation/terminal closure and every comparison above. It found no source, behavior, security, compatibility, or performance defect; its sole medium finding was this pending docs/status closure. Block 3 may now reuse `workflow_audit/client.py`, `capture_service.py`, `artifact_store.py`, and `run_service.py` for bounded provider/validation/checkpoint/no-rerun evidence. It must create and audit a new diagnosis plan and use new identities; S15 remains untouched and Stage C closed.
