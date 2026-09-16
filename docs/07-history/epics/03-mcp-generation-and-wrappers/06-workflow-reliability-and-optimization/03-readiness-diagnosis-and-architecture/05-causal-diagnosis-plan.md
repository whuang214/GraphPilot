# Slice 05: Corrected Causal Plan

## Purpose

Correct the committed causal diagnosis plan after interrupted-session recovery so the active four-slice path uses v1 contracts, one manifest authority, an explicit stale-reference cleanup slice, and no dead review package.

## Background

Plan commit `1bcdd81` correctly superseded the obsolete review gate and introduced causal offline/live discrimination. Implementation commit `5e96af7` proved much of the durable probe lifecycle, but the user identified an unnecessary version bump, a redundant package contract, incomplete dead-package cleanup, and missing repository-wide stale-reference closure. The interrupted partial revert contained no unique work and was discarded without rewriting history.

## Design

Preserve accepted Block 2 and all historical Outcomes. Correct active planning authority only:

- edit readiness-diagnosis case/manifest/observation v1 contracts in place;
- fold package/hypothesis/authorization fields into the run manifest;
- remove the redundant split contract and complete dead review-artifact cleanup in forward commits;
- preserve durable safe events, natural repair trigger, terminalization, and no-rerun behavior;
- make S07 the dedicated stale-reference cleanup slice;
- combine controlled live diagnosis, root decision, Captain report, and conditional Block 4 transition in S08.

## Execution Contract

- **Depends on / inputs:** recovered clean `5e96af7`, parent plan `1bcdd81`, accepted Block 2, S13–S15 Outcomes, provider-free diagnosis evidence, current source/tests, and the user's correction contract.
- **Outputs:** corrected active group and S06–S08 plans, exact v1/manifest/cleanup authority, current-state and decision alignment.
- **Exclusive write ownership:** Block 3 plan/status/decision/navigation docs and ignored supervisor state.
- **Forbidden/shared ownership:** production/tests/schemas/provider, Block 2, `.env`, S15, Stage C.
- **Resources:** read-only source/LSP/search; no provider/browser/server.
- **Cancellation:** stale Block 2 evidence, unbounded live scope, unsupported deletion, or unresolved material plan finding blocks S06.

## Included Work

- Reconcile the committed plan/implementation with all user corrections.
- Define the four-slice critical path and exact cleanup classification.
- Define v1 in-place contracts, manifest-as-package authority, experiment ladder, thresholds, budget, stop rules, and rollback.
- Require documented-command execution and stale-reference closure in S07.
- Run independent plan audit and correct every critical/high/medium finding.
- Commit the audited correction before implementation changes.

## Not In Scope

Implementation, file cleanup, package/run creation, Azure calls, root selection, Block 4, calibration, certification, promotion, S15, or Stage C.

## Target Areas

- `00-group.md`
- this slice and S06–S08 plans
- Block 3 owner, decision index, docs navigation, current-state
- `.devin/weekend-state.json`

## Exit Criteria

- The plan contains exactly four active continuation slices.
- Diagnosis contracts remain v1 and no separate package schema is planned.
- Historical Outcomes and migration tables stay truthful while active stale references are assigned to S07.
- Every live experiment is finite, sequential, identity-safe, and independently audited.
- Root thresholds require reproduction or discrimination rather than correlation.
- Independent audit has no unresolved critical/high/medium finding.
- The forward plan-correction commit precedes implementation correction.

## Previous Slice

Historical S01–S04 commits through `b58545d`, initial causal plan `1bcdd81`, and implementation `5e96af7`.

## Next Slice

[`06-durable-probe-enablement.md`](06-durable-probe-enablement.md) after the corrected plan passes audit and commits.

## Outcome

> **Historical `1bcdd81` record — superseded by the correction above; retained verbatim below.**

**Status:** Complete pending plan commit. The active Block 3 plan supersedes the three-human gate with E0 offline discrimination, sequential one-factor audited packages, exact causal thresholds, and a package-bound readiness-only live surface. Accepted Block 2 and historical Block 3 commits/evidence remain unchanged inputs; only the two user-approved HTML files enter the S06 deletion boundary.

**Audit:** Independent plan audit found four medium specification gaps: exact package schema, v2 mechanical case authority, structured repair trigger, and interrupted known-event retention. The plan now names the package path/fields, removes review/expected/live eligibility from the v2 case, defines the nullable natural repair-trigger object, and requires bounded ledger reconstruction that preserves known events while marking only a nonterminal start uncertain. Focused re-audit passed with no unresolved critical, high, or medium finding.

**Verification:** Relative links, current-state limit, JSON supervisor state, decision/history separation, exact cleanup authorization, secret/diff checks, and clean `b58545d`/Block 2 identities are required immediately before commit. No production code, schema, test, HTML, provider state, `.env`, dependency, S15 identity, Stage C, push, or deployment changed in this slice.

**Correction:** Complete. Interrupted-session recovery verified exact HEAD `5e96af7`/parent `1bcdd81`, proved the partial working-tree revert contained no unique work, and restored the clean committed tree without reset or history rewrite. The corrected active plan keeps four slices, restores the unconsumed diagnosis contracts to v1 in S06, folds package authority into the manifest, assigns complete dead-package and stale-reference cleanup to S07, and combines controlled diagnosis/root transition in S08. Block 2 remains read-only; no live identity or Azure call exists.

**Correction audit:** The first audit incorrectly tested future S06 exit state against current `5e96af7`; scope-correct re-audit found one medium wording issue where active text said schemas “remain” v1. The group now explicitly distinguishes current unconsumed v2 from S06's v1 restoration. Focused re-audit passed with zero critical, high, or medium finding.

**Correction verification:** Four active slices, relative links, 482-word current-state, JSON supervisor state, zero diagnosis identities/calls, 0/1000 accounting, plan-only diff scope, and `git diff --check` pass. No production code/schema/test, provider state, `.env`, dependency, S15 identity, Stage C, push, or deployment changed.
