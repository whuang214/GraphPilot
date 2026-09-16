# Block 5 Slice Group: Complete Live Anchor and Re-Audit

## Goal

Prove one newly identified, genuinely ready, human-reviewed repository-grounded request from user intent through a correct visible editable diagram, then rerun the complete Block 1 audit and produce the measured Block 6 optimization backlog.

## Authority and Inputs

- The [Block 5 owner](../06-block-05-complete-live-anchor-and-reaudit.md) owns the complete anchor and re-audit gate.
- The [shared success contract](../01-success-contract.md) defines generated, blocked, failure, evidence, quality, and performance success.
- Block 4 exit-evidence commit `6276ab3` authorizes Block 5 planning; its proof binds live source `77fc7cb` and correction commit `3b9bcbd` after a first-valid readiness clean pass.
- Cumulative GraphPilot Azure use is 10/1000; 990 remain after the successful five-call anchor.
- E1, E2, and Block 4 proof identities are immutable terminal and never rerun.
- Accepted Block 1/2 baselines remain read-only; re-audit uses new identities.

## Anchor Contract

The anchor is a new visible BDD request, `cold-room-climate-controller`, authored specifically for Block 5 and disjoint from training fixtures, calibration/hidden cases, RepoBench gold, and S13–S15 identities. It binds:

- a small source workspace with a documented controller, temperature probes, cooling relays, ownership multiplicities, sample interval, and probe-relay relationship;
- canonical evidence manifest and diagram request with no unresolved uncertainty or assumption;
- evaluator-only required/forbidden semantic checklist and expected provenance/delivery invariants;
- one accountable product-owner approval of readiness, scope, checklist, and exact live budget.

Agent review is advisory and never counts as human approval. The expected checklist is never sent to the provider.

## Live Schedule and Budget

One manifest authorizes at most 9 sequential Azure calls:

| Role | Ceiling |
| --- | ---: |
| `readiness` | 1 |
| `readiness_response_repair` | 1 |
| `generation` | 1 |
| `generation_repair` | 1 |
| `semantic_review` | 2 |
| `semantic_review_response_repair` | 2 |
| `semantic_repair` | 1 |
| **Maximum** | **9** |

Medium effort is the frozen anchor condition, not a promoted default. Worst-case cumulative use is 14/1000. Calls occur only when naturally reached; no unchanged reroll, favorable retry, parallel provider schedule, or call 10 exists.

## Evidence Versioning and Compatibility

New strict persisted contracts use namespace-first `graphpilot.evaluation.live-workflow-anchor-*.v1` identities for manifest, observation, terminal, safe result, browser evidence, and synthesis. Their schemas reject unknown fields and examples are canonical/digest-valid. After the first live artifact, no field or meaning changes in place: a breaking or additive strict-contract change creates a new `.vN` schema/key/reader while old schema files/readers remain available for immutable runs; no run artifact is migrated or rewritten. Every manifest binds exact schema IDs and runtime assets. A compatibility key binds anchor/approval/source digests, schema IDs, role ceilings/control, production/MCP/browser asset versions, and generated-output contract; S04 compares that key explicitly rather than inferring compatibility from filenames.

## Execution Topology

The slice dependency DAG is:

```text
                 ┌─ S01 Anchor Package and Human Approval ─┐
Audited plan ────┤                                          ├─ S03 Live Anchor
                 └─ S02 Live Harness and Offline Proof ────┘       ↓
                                                        S04 Re-Audit and Handoff
```

S01 and S02 may run in parallel only in separate worktrees with disjoint ownership. S03 waits for both committed S02 harness proof and genuine S01 human approval. S04 waits for a successful S03 anchor. In one worktree, execute sequentially.

## Slice Concurrency and Gates

| Slice | Depends on | Inputs | Outputs | Exclusive write ownership | Forbidden/shared ownership | Parallel with | Shared resources | Integration gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | audited Block 5 plan | anchor contract, canonical fixture patterns, human gate | new source/evidence/request/checklist package, tested review UI, human approval | anchor fixture/package/UI/approval and S01 Outcome | runtime harness, provider, existing fixtures/labels, shared status before integration | S02 in separate worktree | browser profile `block5-anchor-review`; no ports/provider | package/schema/digest/leakage audit, Playwright UI proof, genuine product-owner approval |
| S02 | audited Block 5 plan | frozen anchor contract shape, existing workflow-audit capture/browser/report seams | live-anchor schemas/service/command/MCP adapter, fake/failure/interruption/no-rerun proof | new live-anchor backend/evaluation modules/schemas/tests/docs and S02 Outcome | anchor semantic content/approval, production behavior outside injected seam, provider, S15 | S01 in separate worktree | temp workspaces only; no browser/provider | implementation audit, focused/full backend, stdio/fake/security/compatibility |
| S03 | committed S01+S02 | human-approved anchor, clean exact commit, audited manifest, 995 remaining | one immutable request-to-visible-editor live result | new anchor identities/artifacts, S03 Outcome/status, ignored supervisor state | code edits after manifest freeze, other live packages, E1/E2/Block4 identities, S15/Stage C | none | sequential Azure; unique ports 15174/18081; unique browser profile | pre-dispatch audit, max-9 execution, quality/provenance/browser/terminal audit |
| S04 | successful S03 | exact live anchor evidence, current Block 1 method | new provider-free baseline/report/ledger entry, combined Block 5 report, ranked Block 6 backlog | new re-audit identities/reports/ledger entry, group/parent/current-state/handoff | behavioral optimization, old baseline mutation, provider calls, promotion/certification | none | Block 1 ports 15173/18080/18991 after S03 cleanup | baseline audit, non-overlap accounting, report/backlog audit, full gates, Block 6 decision |

## Slice Plans

| Slice | Plan | Status |
| --- | --- | --- |
| 01 · Anchor Approval | [`01-anchor-approval.md`](01-anchor-approval.md) | Complete · human approved |
| 02 · Live Harness | [`02-live-harness.md`](02-live-harness.md) | Complete · audited and verified |
| 03 · Live Anchor | [`03-live-anchor.md`](03-live-anchor.md) | Complete · generated/browser/audit pass |
| 04 · Re-Audit and Handoff | [`04-reaudit-and-handoff.md`](04-reaudit-and-handoff.md) | Complete · Block 5 exit PASS |

## Human Review Boundary

S01 prepares a self-contained local HTML review package with direct rendering of:

- source/evidence/request identity and digests;
- required and forbidden meaning;
- expected ready/generation/provenance/persistence/render/editor invariants;
- live role ceilings, 9-call maximum, rollback, and claim limits.

One product owner approves or requests revision and exports a schema-valid record. No agent, subagent, or browser automation may submit the real approval. S02 may proceed independently, but S03 stops until approval exists and its digest is bound into the live manifest.

## Live Anchor Proof

The S03 clock starts when the host accepts the exact approved request and ends at visible editor completion. The harness must measure without double counting:

- host routing, source reads, JSON 1/2 authoring, and credits/tokens when available;
- real stdio MCP startup/discovery/transport/tool calls;
- every Azure role/state/duration/bytes/token/control/request-ID/service-tier/validation/repair event;
- local readiness/generation/review/layout/validation/provenance/persistence/render stages;
- returned editor link, API load, browser navigation, console/network state, and visible diagram identity.

Checkpoint precedes MCP dispatch. Safe events persist after every call return/failure. A lost process after a started call terminalizes uncertain and never reruns that identity.

## Quality and Leakage Gate

Success requires:

- final readiness accepted under exact policy;
- generated diagram schema/provenance/context stability valid;
- required checklist meaning present and forbidden unsupported meaning absent;
- reviewed semantic quality and mandatory final review passed;
- canonical JSON/SVG owned by the exact request;
- MCP returns the backend-built editor link;
- editor visibly loads the exact diagram with no material console/network error;
- checklist/gold/approval content never enters provider messages.

A blocked, failed, or interrupted run is durable evidence but not an anchor. It stops S04 and requires an audited downstream diagnosis/new authorization; it is never favorably rerun.

## Re-Audit Contract

After anchor success, S04 runs the complete current Block 1 baseline under a new identity with browser proof and zero Azure. It retains the new live anchor as separately bound external evidence and produces a Block 5 synthesis with one complete-wall denominator, nested stage detail, missing evidence marked `not_measured`, compatibility key, and ranked Block 6 opportunities by measured contribution—not ease.

## Non-Goals

- No representative type/status/stability matrix.
- No optimization implementation or effort/prompt/runtime promotion.
- No calibration, certification, deployment, push, or Stage C.
- No reuse of training fixture content as the anchor answer, S15 identities/artifacts, or hidden gold.
- No mutation of accepted Block 1/2 artifacts.

## Risks and Rollback

- Human approval is a real dependency; stop S03 if unavailable or revised.
- New live harness code must remain evaluation-only and non-influencing; any required production redesign returns for review.
- Nine calls are a ceiling, not a target; natural failure stops downstream roles.
- Existing development servers are never reused; unique ports/profiles and mandatory cleanup apply.
- Rollback reverts Block 5 harness/fixture commits while retaining all approved packages, live events, terminal artifacts, and Block 1 re-audit evidence.

## Plan Audit

Independent review verified the four-slice DAG, exact role ceilings/budget, human gate, leakage boundary, stdio/production/browser scope, durability/no-rerun, Block 1 re-audit, ownership, and Block 6 gate. Its initial findings included one scope error—confusing the Block 4 exit-evidence commit with its bound source/correction commits—and real requests for explicit DAG terminology, strict evidence versioning, minimal-adapter rationale, semantic completeness mapping, and exact non-generated stop states. The commit chain was clarified and all real gaps were corrected, including an explicit no-`.env`-read inherited-environment design. Focused re-audit passed with zero critical, high, or medium finding.

## Acceptance Criteria

- One genuine human-approved, leakage-disjoint anchor package is committed.
- Harness offline/failure/interruption/no-rerun/security proof and full checks pass with no material audit finding.
- One new-identity live anchor reaches a correct visible editable diagram with complete critical-path evidence.
- Current Block 1 audit reruns successfully and a ranked Block 6 backlog is independently audited.
- Calls are exact, bounded, terminal, counted, and never rerun; cumulative use remains ≤1000.
- Block 6 starts only after Block 5 exit audit passes; otherwise stop at the failed owner.

## Related Docs

- [`../06-block-05-complete-live-anchor-and-reaudit.md`](../06-block-05-complete-live-anchor-and-reaudit.md)
- [`../01-success-contract.md`](../01-success-contract.md)
- [`../11-block-execution-and-parallelism.md`](../11-block-execution-and-parallelism.md)
- [`../04-readiness-correction-and-proof/proof/result.md`](../04-readiness-correction-and-proof/proof/result.md)
- [`../../../../../02-design-and-features/08-context-backed-generation/01-workflow.md`](../../../../../03-design/01-context-generation/02-workflow.md)
