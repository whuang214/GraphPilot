# Block 3 Slice Group: Readiness Diagnosis and Architecture

## Goal

Identify the actual cause of readiness failures and excessive readiness latency, select exactly one supported corrective boundary, and hand only that correction to Block 4. Use offline evidence first and sequential, independently audited live experiments only when they discriminate a remaining hypothesis.

## Authority and Preserved Evidence

- The [Block 3 owner](../04-block-03-readiness-diagnosis-and-architecture.md) owns the diagnosis question and exit gate.
- The [shared success contract](../01-success-contract.md) owns correctness, failure, interruption, evidence, and no-rerun semantics.
- The [execution policy](../11-block-execution-and-parallelism.md) owns identity/resource isolation, sequential live execution, audits, and integration.
- Accepted Block 2 commit `e25c7797240f0bdb7da06665c15a5b815377241d`, candidate `baseline-workflow-audit-block2-parity-20260724-01`, and compatibility key `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1` remain read-only and unchanged.
- S13–S15 Outcomes, the committed provider-free diagnosis evidence, current source, existing fixtures/rubrics, deterministic validation, and safe provider metadata are engineering evidence. They are not human review, calibration, certification, or promotion evidence.

## Recovery and Supersession

Commits `643de67`, `f6552c9`, `7d17ff8`, and `b58545d` retain the first Block 3 path. Commits `1bcdd81` and `5e96af7` retain the initial causal replan and implementation. The interrupted working-tree revert contained no unique work and was discarded with `git restore --worktree -- .`; committed history was not reset or rewritten.

The obsolete review gate remains superseded. Mechanical diagnostic execution requires no human label. Historical slice Outcomes stay in place and are marked superseded where needed; active plans, contracts, schemas, commands, tests, status, and navigation must not retain the old gate.

## Current Evidence and Hypotheses

Current evidence proves that complete-projection repair is expensive, but not why the first response is invalid. The active hypotheses are:

1. prompt instruction conflicts with the strict response contract;
2. Azure strict-schema projection accepts or requires a shape that backend canonical validation rejects;
3. deterministic validation or response bounds reject otherwise usable output;
4. provider/control behavior changes validity, latency, or semantics;
5. context/projection size causes latency or invalid output;
6. readiness combines responsibilities or repair work in a structurally expensive way;
7. another boundary identified by exact captured evidence.

Repair entry, latency, and correlation are not root-cause evidence by themselves.

## Experiment Strategy

### E0 · Offline discrimination

Before Azure use:

- recompute prompt, schema, projected-schema, rubric, source, projection, and wire identities/bytes;
- measure local preparation, projection, validation, assembly, and persistence separately;
- compare projected Azure strict schema with backend canonical validation using bounded synthetic witnesses;
- trace response byte bounds and every first-response validation `{code,path}` owner;
- quantify first/repair payload overlap and the complete projection repeated in repair;
- characterize checkpoint/event/terminal behavior, including interruption after known events.

### E1 · First live causal probe

Use one new source-bound Activity case and explicit high reasoning effort because prior high evidence was repair-prone. Permit exactly one `readiness` call and one naturally reached `readiness_response_repair`. Persist safe provider metadata, exact validation events, an explicit repair trigger, checkpoint, terminal, and no-rerun evidence.

### E2+ · Smallest next discriminator

Only if E1 leaves multiple causes plausible, freeze and audit a new manifest with new identities that changes one material factor. The preferred next comparison is the same exact case under medium effort when provider/control remains plausible. Input-size, response-bound, or repair-payload experiments require direct evidence from the previous result and their own manifest audit. Failed or unfavorable outcomes are never rerun favorably.

## Diagnostic Contracts

The diagnosis contracts are v1 because they have no external consumer or persisted diagnosis artifact requiring another identity:

- `backend/assets/schemas/readiness-diagnosis-case.json` contains only visible mechanical source/provider/scope authority;
- `backend/assets/schemas/readiness-diagnosis-run-manifest.json` is the complete auditable package: it binds package ID, hypothesis, exact clean commit/assets/case, `fake|live` provider mode, reasoning effort, new run/observation IDs, ordered roles, call ceiling 2, budget, output root, scope, rollback, canonical digest, and `never_rerun_checkpointed_or_terminal_identity`;
- `backend/assets/schemas/readiness-diagnosis-observation.json` binds durable lifecycle events, provider calls, validation events, capture completeness/failures, readiness summary, terminal state, and nullable `repairTrigger`;
- a natural repair trigger records the first invalid readiness `{code,path}` set before repair dispatch;
- interrupted terminalization reads the bounded durable event ledger, preserves every known completed/failed call and validation/repair-trigger event, and marks only the last unmatched started call uncertain;
- no separate package contract remains;
- `backend/operations/management/commands/run_readiness_diagnosis.py` is the only live entry point and constructs Azure only after explicit `--live` plus manifest, HEAD, identity, budget, source, and configuration gates;
- no generation, semantic review, calibration, certification, diagram persistence, render, browser, S15, or Stage C path is reachable.

The existing effort benchmark remains separate and is not the durable executor.

## Root-Cause Thresholds

### Focused implementation correction

Select only when an exact live validation signature identifies one local owner; a bounded provider-free witness reproduces it; a locally corrected witness preserves accepted readiness meaning; and component/provider alternatives are disconfirmed. Block 4 owns failing-before tests, production implementation, and passing-after proof.

### Readiness-component redesign

Select only when evidence places the defect in the readiness responsibility split, response contract, or repair architecture; bounded local corrections cannot preserve accepted meaning; an offline prototype removes the failure across relevant fixtures; and provider/control causation is disconfirmed.

### Provider/control response

Select only when typed provider metadata or an explicit requested/effective control, strict-output, context-limit, deployment, or service-tier boundary explains the result while local prompt/schema/projection/validator parity passes offline. One condition cannot establish comparative reasoning-effort causality.

### Additional evidence

Retain when provider state is uncertain, critical capture is incomplete, the failure does not reproduce, multiple boundaries remain plausible, a comparison needs another audited manifest, or any manifest/result/exit audit retains a critical/high/medium finding. Missing human review never blocks mechanical evidence; claims requiring semantic judgment remain explicitly limited.

## Live Safety Envelope

- Cumulative maximum: 1000 GraphPilot Azure calls; current use: 0.
- Every manifest has one hypothesis, exact new identities, frozen source/assets/controls/order/roles, finite ceiling, rollback, and an independent audit.
- Checkpoint precedes dispatch; completed, failed, and uncertain states terminalize; checkpointed or terminal identities never rerun.
- Persist only bounded safe metadata and validation `{code,path}`; never raw responses, prompts, reasoning, secrets, or source dumps.
- Experiments are sequential and change one material factor at a time.
- No result may claim calibration, certification, promotion, or representative semantic quality.

## Execution Topology

```text
S05 Corrected Causal Plan
  ↓ independent audit + forward plan-correction commit
S06 Durable Probe Correction
  ↓ implementation audit + full verification + forward commit
S07 Stale Reference Cleanup
  ↓ documented-command execution + stale-reference audit + forward commit
S08 Controlled Diagnosis and Transition
  ↺ E0 → audited manifest → one live experiment → evidence audit
  ↓ exactly one supported root + Captain Progress Report + exit audit
Block 4 plan/audit/implementation
```

S08 may iterate only through newly frozen one-factor manifests. It stops only for the program stop conditions, including unterminalizable uncertainty, exhausted budget, missing credentials/permissions, material audit/security conflict, destructive work, or an unapproved dependency.

## Slice Ownership and Gates

| Slice | Depends on | Outputs | Exclusive write ownership | Forbidden/shared ownership | Gate |
| --- | --- | --- | --- | --- | --- |
| S05 | recovered clean `5e96af7` | corrected four-slice plan, v1/manifest authority, cleanup contract | Block 3 plan/status/decision docs and ignored supervisor state | production code, provider, Block 2, S15 | independent plan audit, links, diff, current-state limit |
| S06 | committed S05 correction | corrected v1 contracts/lifecycle/command/tests; split contract removed | diagnosis service/schemas/registry/tests/command and named backend docs | Block 2 code/artifacts, readiness behavior/prompts/rubrics, provider calls | characterizing tests, implementation audit, focused/full backend, schema/security/compatibility |
| S07 | committed S06 correction | dead review artifacts removed; active references and moved-path commands corrected | exact stale docs/tests/comments and authorized dead artifacts | historical Outcomes/migration tables, production redesign, provider | documented commands executed, stale-reference scan, independent cleanup audit, full relevant verification |
| S08 | committed S07 cleanup | E0 evidence, sequential audited manifests, immutable live observations, one root or next discriminator, Captain report, Block 4 boundary | new diagnosis identities/result evidence, S08 Outcome/current-state, ignored progress/state files | unsupported correction, generation/review, calibration/certification, Block 2, S15/Stage C | manifest audit before every call; terminal/evidence audit after every call; clean exit audit before Block 4 |

All slices are sequential because each consumes the prior committed contract, cleanup closure, or measured evidence. Read-only audits may run independently; the primary supervisor owns integration and commits.

## Stale-Reference Policy

S07 distinguishes history from active authority:

- keep historical Block 2 migration tables, historical slice Outcomes, removed-entry regression tests, and Git history;
- mark historical S03/S04 and initial S05/S06 Outcomes superseded without altering what they report;
- remove obsolete execution-gate fields, superseded diagnosis IDs, dead package paths, and obsolete ownership/target lists;
- correct runnable commands and execute every documented command touched, or record explicitly why one was not run;
- use `mechanical-probe` as the single active evidence location;
- confirm backend/docs/navigation owners and schema inventory contain no stale active reference.

## Cleanup

S06 removed the redundant package contract after folding its concrete authority into the manifest. S07 removed the complete dead review package and superseded draft without a tombstone or archive. Historical behavior remains available in commits `7d17ff8`, `1bcdd81`, and `5e96af7`.

## Rollback

Plan correction reverts as one forward commit. Before any live call, S06/S07 revert independently without touching Block 2. After a provider checkpoint exists, its manifest/run artifacts remain immutable and are never deleted or rerun; code may be reverted independently. A failed Block 4 candidate reverts only the correction while retaining Block 3 evidence.

## Slice Plan

| Slice | Plan | Status |
| --- | --- | --- |
| 01–04 · Historical path | commits `643de67` through `b58545d` | Superseded as active gating; Outcomes retained |
| 05 · Corrected Causal Plan | [`05-causal-diagnosis-plan.md`](05-causal-diagnosis-plan.md) | Complete · `5de21e2` |
| 06 · Durable Probe Correction | [`06-durable-probe-enablement.md`](06-durable-probe-enablement.md) | Complete · corrected v1 manifest authority |
| 07 · Stale Reference Cleanup | [`07-stale-reference-cleanup.md`](07-stale-reference-cleanup.md) | Complete · audit passed |
| 08 · Controlled Diagnosis and Transition | [`08-root-decision-and-transition.md`](08-root-decision-and-transition.md) | Complete · Block 3 exit passed |

## Acceptance Criteria

- Block 2 code, parity evidence, identities, and artifacts are unchanged.
- The diagnosis contracts remain v1 and no separate package schema remains.
- Offline evidence is exhausted before each live discriminator.
- Every live call belongs to a newly frozen/audited manifest and cumulative accounting remains exact.
- Exact validation trigger, wall-time domains, repair duplication, and capture completeness are evidence rather than assumptions.
- No active stale reference survives S07; historical records remain truthful.
- No root is selected until one threshold passes and alternatives are disconfirmed.
- The Captain Progress Report is updated after every experiment and before Block 4.
- Block 4 begins only after one root and a clean independent Block 3 exit audit.
