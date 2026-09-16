# Slice 01: Anchor Approval

## Purpose

Create one new, visible, leakage-disjoint `cold-room-climate-controller` BDD anchor package and obtain one genuine product-owner approval of its readiness, semantic checklist, and bounded live schedule.

## Design

Author a small synthetic repository workspace rather than reusing a training/S15 case. The source must independently establish:

- `ColdRoomClimateController`, `TemperatureProbe`, and `CoolingRelay` definitions;
- controller composition of probes and relays with exact bounded multiplicities;
- a typed sampling-interval property;
- the documented probe-to-relay relationship;
- no cloud/network/heating behavior or unsupported deployment topology.

Create canonical evidence/request documents with no uncertainty, assumption, or hidden gold. The evaluator-only checklist defines required/forbidden meaning and delivery/provenance invariants but never enters provider input.

Semantic completeness is a closed trace matrix, not an impression: every source-backed definition, composition end/multiplicity, typed property/value, association end/multiplicity, explicit exclusion, and smallest-sufficient provenance expectation maps to one evidence ref, one selected claim, one required/forbidden checklist row, and an expected BDD element/relationship family from [`../../../../../02-design-and-features/diagram-schemas/bdd-diagram-blueprints.md`](../../../../../03-design/02-diagram-schemas/02-bdd-blueprints.md). The review UI requires an approve/revise decision per row and overall; missing, duplicate, unbound, or uncovered rows fail package validation.

## Execution Contract

- **Depends on / inputs:** audited Block 5 plan, canonical JSON 1/2/training-fixture patterns, schema registry, clean source.
- **Outputs:** new source/evidence/request/checklist package, digest-bound local review UI/schema, one human approval record, S01 Outcome.
- **Exclusive write ownership:** `backend/assets/evaluation/live-anchor/cold-room-climate-controller/`, this group's `anchor-package/`, S01 Outcome.
- **Forbidden/shared ownership:** runtime harness/source, production prompts/services, existing training/calibration/S15/hidden fixtures, current-state/parent integration owners until slice close, provider calls, `.env`.
- **Parallelism/resources:** parallel-safe with S02 only in a separate worktree; unique Playwright profile `block5-anchor-review`; no ports/provider.
- **Cancellation:** missing human approval, requested semantic revision, leakage/identity overlap, unsafe/private content, or schema/digest/audit failure blocks S03.

## Included Work

- Build the source workspace, canonical evidence manifest, canonical request, and required/forbidden checklist.
- Prove all identities/text/digests are disjoint from training fixtures, calibration/hidden material, RepoBench, and S13–S15.
- Create `anchor.json`, approval schema, and self-contained `review.html` rendering all approval-relevant content directly.
- Provide approve/revise controls, notes, explicit non-certifying attestation, 9-call schedule acceptance, local persistence, and machine-readable export.
- Browser-test blank defaults, incomplete rejection, revise/approve, persistence/export, accessibility basics, and zero console/schema errors.
- Independently audit package semantics, readiness claim, leakage, budget, and UI.
- Present the exact package to one product owner; agent/browser test values never count as approval.
- Commit only after a genuine schema-valid approval record exists.

## Not In Scope

Provider execution, harness implementation, training fixture registration, calibration/certification, hidden evaluation, representative claims, or multi-review/adjudication ceremony.

## Target Areas

- `backend/assets/evaluation/live-anchor/cold-room-climate-controller/`
- `anchor-package/anchor.json`
- `anchor-package/approval.schema.json`
- `anchor-package/review.html`
- `anchor-package/approval.json`
- this Outcome

## Exit Criteria

- Source/evidence/request/checklist are canonical, bounded, secret-safe, mutually bound, and leakage-disjoint.
- Anchor expected state is genuinely ready under deterministic/human authority without assumptions or unresolved gaps.
- One actual human product owner approves exact required/forbidden meaning and max-nine live schedule.
- UI/browser/schema/digest and independent package audits have no material finding.
- No agent review is represented as human.

## Previous Slice

[`../04-readiness-correction-and-proof/02-live-proof-and-exit.md`](../04-readiness-correction-and-proof/02-live-proof-and-exit.md)

## Next Slice

[`03-live-anchor.md`](03-live-anchor.md) after this approval and S02 are committed.

## Outcome

**Status:** Complete. A new leakage-disjoint `cold-room-climate-controller` BDD source/evidence/request package binds five evidence rows, seven selected claims, eight required-meaning rows, four forbidden rows, five delivery checks, zero uncertainty/assumption, and exact raw/canonical/source-fingerprint digests. It is not registered as a training fixture and has no training identity/raw-digest overlap.

**Review package:** `anchor-package/anchor.json` digest `sha256:12a4528c6d717bba44d7408a78bb7f1723d0c53a55261984a252eba6f553b51b` binds one product-owner review, seven section decisions, five non-certifying/provider-separation attestations, medium effort, role ceilings totaling nine, 5/1000 current use, and 14/1000 worst case. Agent review never counts.

**Audit and browser proof:** Independent semantic/provenance review initially conflated raw file SHA-256 with GraphPilot's path+content source fingerprint; both digest domains were made explicit and recomputed, resolving the false critical. Re-audit passed with zero critical/high/medium finding. Real-browser tests covered blank rejection, test-only revise/approve exports, schema/digest validation, reload persistence, clear reset, direct content rendering, labels, and zero final console warnings/errors. Playwright blocked `file:` URLs, so an isolated temporary HTTP port 18992 was used and fully cleaned; no test-only approval is retained.

**Human decision and gate:** The user/product owner approved the exact package after clarifying that approval covers the complete input/checklist and one bounded attempt—not a future diagram. Approval `sha256:d25ffb3e5638d11e59883578d840819af7d01a935bf53450b1a24bd2dd0f3b88` uses generic ID `product-owner-user`, approves all seven sections, and affirms all five attestations. Independent final audit confirmed the genuine human decision satisfies S01 with zero critical/high/medium finding. S03 remains blocked only on S02 commit. No provider call, `.env` access/change, S15/Stage C access, training registration, push, or deployment occurred.
