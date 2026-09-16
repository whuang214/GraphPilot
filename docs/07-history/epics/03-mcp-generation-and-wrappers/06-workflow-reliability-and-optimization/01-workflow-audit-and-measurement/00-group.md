# Block 1 Slice Group: Workflow Audit and Measurement

## Goal

Deliver the reusable, versioned, provider-free workflow audit and fresh pre-Block 2 baseline required by the approved
[Block 1 owner](../02-block-01-workflow-audit-and-measurement.md), without promoting or rerunning S15's frozen H/M package.

## User Scenario

An operator runs one documented provider-free command against approved versioned scenarios. GraphPilot exercises the current
request-to-visible-editor workflow through real MCP stdio, fake provider responses, production backend services, and a built
frontend; records every W01–W22 boundary as measured, derived, simulated, imported, not reached/applicable, or explicitly
`not_measured`; writes a bounded report; and records a compatibility-gated baseline that a later block can rerun safely.

## Authority and Boundaries

- The parent [Block 1 document](../02-block-01-workflow-audit-and-measurement.md) owns the question, audit boundary, outputs,
  rerun triggers, and exit gate.
- The [shared success contract](../01-success-contract.md) owns generated, blocked, failed, interrupted, performance, quality,
  and change-evidence semantics.
- This group owns only Block 1's executable Slice 01–06 plan and outcomes.
- S13–S15 remain prior evidence. Their cases, H/M conditions, manifests, checkpoints, stopped identities, budgets, and live
  authorization state are not inputs to the reusable audit or its baseline ledger.
- Live status remains exclusively in the [current-state board](../../../../../05-delivery/01-current-state.md).

## Design Summary

The implementation refactors the current `full_workflow_audit_service.py` foundation rather than rebuilding or generalizing
the complete S15 `full_effort_*` stack. It retains W01–W22, real stdio, service wrappers, generation-observer stages,
cold/warm orchestration, and recovery mechanics while replacing fixed S15 dependencies with a versioned scenario provider and
evaluation-only capturing client.

Audit evidence keeps host, Azure, MCP, local deterministic work, browser completion, and residual time non-overlapping.
Unavailable values remain null with a reason. Fake-provider duration is local harness time, never Azure evidence. Baseline
comparison requires an exact compatibility key; incompatible runs never produce before/after percentages.

## Execution Topology

```text
S01 Contracts and Scenarios (passed)
  ↓ freezes schemas, scenarios, and compatibility inputs
S02 Capture and Evidence Adapters (passed)
  ↓ freezes measurement, client-capture, and accounting behavior
S03 Audit Runner and Recovery
  ↓ produces exact immutable observations and generated artifact identities
S04 Browser Completion Proof
  ↓ produces digest-bound W22 evidence for an exact S03 observation
S05 Reports and Baseline Ledger
  ↓ integrates runner/browser evidence into the operator command and baseline package
S06 Fresh Provider-Free Baseline
  ↓ runs the complete integration/block-exit gate and hands parity evidence to Block 2
```

The maximum safe write concurrency is **one slice**. Every slice consumes a committed contract or artifact from its predecessor:
S02 consumes S01 schemas/scenarios; S03 consumes S02 capture behavior; S04 requires S03's exact generated observation; S05
requires S03 observations plus S04 browser evidence; and S06 measures one integrated candidate after all implementation is
committed. Parallel write execution would consume uncommitted interfaces, share run/output identities, or destroy measurement
causality. Independent read-only audits and disjoint investigations may run concurrently, but the primary integration owner
alone updates shared registration, canonical docs/status, stages, and commits.

The **Block 1 primary agent** is the named integration owner for shared registration/wiring/configuration, cross-slice docs and
current-state updates, integration audits/checks, commits, and the final handoff. Merge order is strictly
`S01 → S02 → S03 → S04 → S05 → S06`; S06 is the block integration gate proving the combined result. Failure, uncertainty, or
interruption in any slice blocks every downstream slice in this linear chain; the integration owner stops, preserves exact
worktree/artifact/commit state, and diagnoses before any resume. Sequential execution uses one worktree, so concurrent-write
worktree isolation is not applicable; exclusive ownership still changes by slice as declared below. Any approved intra-slice
write delegation must use a separate worktree or strictly disjoint files/resources and return to the primary integration owner
before staging or committing.

## Slice Concurrency and Ownership

| Slice | Depends on | Inputs | Outputs | Exclusive write ownership | Forbidden/shared ownership | Parallel with | Shared resources | Integration gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | none | approved Block 1 design and existing context fixtures | schemas, scenario bundle/service, canonical audit design | workflow-audit schemas/scenario assets/service/tests and audit design owner | generation behavior, S15 package; shared schema registry/decision/index only by primary integrator | none | schema inventory and approved training fixtures | schema/scenario/design gate; passed in `0333a62` |
| S02 | S01 | committed schemas/scenarios | measurement/accounting, capture store/observer/client, host adapters | workflow-audit capture/client/contracts/tests | runner/browser/report code; shared service/architecture/status docs only by primary integrator | none | temporary workspaces and provider-free fake clients | equivalence/security/full-backend gate; passed in `ea0cd8e` |
| S03 | S02 | committed scenarios and capture APIs | immutable manifest/observations, real-stdio runner, guard/recovery/no-rerun evidence | workflow-audit runner/artifact-store/fake-client modules, audit server, focused tests | frontend/browser/report/ledger; management-command removal and shared docs reserved for S05/integrator | none | unique temporary control/evaluated roots, scenario/run/observation IDs, MCP subprocesses | all provider-free runner/terminal/recovery gates |
| S04 | S03 | exact generated S03 observation/path/digests | built-preview browser evidence | dedicated Playwright audit config/spec, browser adapter/tests | runner/report/ledger/shared docs; no development ports or shared browser session | none | ports `15173`/`18080`, unique Playwright session/profile and browser-evidence path | W22 identity/network/console gate |
| S05 | S03, S04 | immutable observations plus browser evidence | reports, findings, compatibility ledger, independent command | workflow-audit report/analysis/ledger modules, management command/tests, command/docs migration | scenario/capture/runner/frontend behavior; S15 staged operations remain shared but unchanged except old audit entry removal | none | one control output root, report/ledger IDs, schema registry | report/ledger/command/full integration gate |
| S06 | S05 | complete committed command/package and clean commit identity | fresh baseline report/ledger entry and Block 2 handoff | generated gitignored run package plus Slice 06/group/current-state outcomes | all production behavior and live/S15 identities | none | one new run/baseline identity, exact cold/warm cache order, isolated browser ports | final backend/frontend/MCP/browser/security/block-exit gate |

## Slice Plan

| Slice | Plan | Status | Completion outcome |
| --- | --- | --- | --- |
| 01 · Audit Contracts and Scenarios | [`01-audit-contracts-and-scenarios.md`](01-audit-contracts-and-scenarios.md) | Complete | Canonical design, strict contracts, and an independent bounded default scenario bundle |
| 02 · Capture and Evidence Adapters | [`02-capture-and-evidence-adapters.md`](02-capture-and-evidence-adapters.md) | Complete | Normalized W01–W22 capture with truthful host/provider/MCP/local evidence and observational equivalence |
| 03 · Audit Runner and Recovery | [`03-audit-runner-and-recovery.md`](03-audit-runner-and-recovery.md) | Complete | Immutable provider-free cold/warm and guard observations with terminal recovery/no-rerun proof |
| 04 · Browser Completion Proof | [`04-browser-completion-proof.md`](04-browser-completion-proof.md) | Complete | Built-preview W22 evidence bound to the exact generated observation |
| 05 · Reports and Baseline Ledger | [`05-reports-and-baseline-ledger.md`](05-reports-and-baseline-ledger.md) | Complete | Versioned JSON/Markdown report, ranked findings, compatibility ledger, and independent command |
| 06 · Fresh Provider-Free Baseline | [`06-fresh-provider-free-baseline.md`](06-fresh-provider-free-baseline.md) | Complete | Fresh current pre-Block 2 baseline and exact parity handoff |

## Dependencies

1. Slice 01 freezes the input/output and storage semantics before implementation depends on them.
2. Slice 02 depends on Slice 01's evidence contracts and scenario provider.
3. Slice 03 depends on the scenarios and normalized capture adapters.
4. Slice 04 consumes an exact completed runner observation and produces browser evidence.
5. Slice 05 aggregates runner and browser evidence into reports and the ledger.
6. Slice 06 runs only after all provider-free, failure, recovery, security, and browser-safe gates pass.

## Shared Verification

- Focused schema/scenario/capture/runner/browser/report/ledger/command tests.
- Instrumented-versus-uninstrumented provider-call/result/JSON/SVG/write equivalence.
- Failure isolation, bounds, path safety, redaction, null-versus-zero, terminal identity, and no-rerun tests.
- `cd backend; uv run python manage.py test`
- `cd backend; uv run python manage.py check`
- `cd backend; uv run python mcp_server/smoke_test.py`
- `cd backend; uv run python -m compileall -q api mcp_server services`
- `cd frontend; npm run verify`
- Dedicated built-preview browser audit and `git diff --check`.

## Plan Audit

Result: **Pass after execution-policy amendment (2026-07-23).** The original Slice 01–06 plan passed independent audit after
clarifying the Slice 01 design owner as an output. Execution-policy commit `1324f74` later added mandatory DAG, concurrency,
ownership, resource-isolation, and integration-gate requirements while S02 was already executing. This amendment records the
honestly linear topology and maximum safe write concurrency of one, exact slice ownership/resources, strict merge order, named
integration owner, dependent cancellation, single-worktree policy, S06 integration gate, and standalone execution contracts.
The first amendment audit requested those four explicit orchestration statements; re-audit found no remaining critical, high,
or medium defect.

## Acceptance Criteria

- The default audit has no runtime dependency on S15 case/manifest/runner/report services or identities.
- Every material W01–W22 boundary has explicit evidence status, source, confidence, and reason where unavailable.
- Complete-wall accounting is non-overlapping and fake-provider work never becomes Azure evidence.
- Success, blocked, repair, failure/interruption, recovery, and no-rerun paths are covered provider-free.
- A baseline requires exact browser completion evidence and a complete compatible run.
- Reports and ledger entries are bounded, versioned, secret-safe, immutable by identity, and concurrency-protected.
- One documented provider-free command produces the fresh pre-Block 2 baseline without constructing Azure.

## Related Docs

- [`../00-group.md`](../00-group.md)
- [`../01-success-contract.md`](../01-success-contract.md)
- [`../02-block-01-workflow-audit-and-measurement.md`](../02-block-01-workflow-audit-and-measurement.md)
- [`../../04-context-backed-generation/15-full-effort-evaluation.md`](../../04-context-backed-generation/15-full-effort-evaluation.md)
- [`../../../../../02-design-and-features/07-evaluation-and-doe-design.md`](../../../../retired-evaluation-and-doe-design.md)
- [`../../../../../02-design-and-features/08-context-backed-generation/README.md`](../../../../../03-design/01-context-generation/README.md)
