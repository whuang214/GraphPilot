# Slice 03: Human Review Package

> Historical S03 plan/Outcome only. The three-human gate and review UI are obsolete; active Block 3 execution is owned by S05–S08. The complete dead review package is authorized for deletion in S07; commit `7d17ff8` preserves its history.

## Purpose

Prepare and browser-test one exact visible readiness-diagnostic case for two genuine independent human reviews and adjudication, without claiming approval or authorizing Azure.

## Design

Create a durable package under `review-package/` beside this plan:

```text
review-package/
  diagnostic-case.json
  readiness-diagnosis-human-review.schema.json
  readiness-diagnosis-adjudication.schema.json
  review.html
  adjudicate.html
```

`diagnostic-case.json` binds the new package/case identities to the committed `scenario-workflow-audit-activity-basic` and `return-authorization` source paths/digests, current readiness prompt/schema/rubric/projection identities, visible/non-certifying status, and future maximum-two-call boundary. It contains no provider response. This is explicitly a **diagnostic bridge**, not a readiness calibration/holdout fixture or generation-certification case; it never enters `backend/assets/readiness/calibration/bundle.json`, which remains empty until its separate human calibration program authors cases independently.

`review.html` renders all approval-relevant bounded authority and label obligations directly for one reviewer at a time: applicability/rating bands, required-facet pass/fail, mandatory/forbidden finding signatures, actions, expected status/overrideability, and notes. Reviewer A and Reviewer B use separate named browser profiles or exported files; the page stores only the active review under a reviewer-specific key and never loads a peer export. `adjudicate.html` accepts the two completed exports only after both reviews exist, validates distinct reviewer IDs/attestations, displays disagreements, and exports adjudication.

A local self-contained page cannot cryptographically prevent a reviewer from inspecting another person's file or browser storage. Independence is therefore procedural and auditable—not a security guarantee—and the UI states that limitation. Automated tests prove ordinary UI peer-hiding, separate keys/files, and adjudication gating rather than claiming adversarial confidentiality.

All defaults are unapproved. Agent-proposed examples, if shown, are labeled suggestions and never exported as human answers unless a reviewer explicitly enters/accepts them. Completing review does not authorize live execution; it only satisfies a future package input.

## Execution Contract

- **Depends on / inputs:** committed S02 diagnostic-case contract/service, exact tracked source fixture/scenario/readiness assets, canonical human-label requirements.
- **Outputs:** source/digest-bound case JSON, tested review UI, S03 Outcome.
- **Exclusive write ownership:** `review-package/` and this Outcome.
- **Forbidden/shared ownership:** S02 evidence files, production/frontend source, calibration bundle, S15, generated artifacts, current-state/decision index until S04.
- **Parallelism/resources:** sequential after S02; separate unique Playwright CLI sessions for Reviewer A, Reviewer B, and adjudication; local file URLs only; no backend ports/provider.
- **Gate:** independent package/design audit followed by real-browser approve/revise, peer-hiding, persistence, dual-submit, adjudication, export, accessibility basics, and console-error tests; mandatory cleanup.
- **Cancellation:** no completed reviews are invented during testing; automated test values use unmistakable `test-only` IDs and are cleared with the browser session.

## Included Work

- Compute exact canonical digests for source scenario, evidence, request, fixture metadata, readiness prompt/schema/rubric, and case document.
- Define closed package-local human-review/adjudication export schemas with exact IDs, bounds, order, scope, and relative resolution.
- Render complete review content and distinguish fixture generation approval from missing readiness-label approval.
- Implement two independent reviewer flows, revision notes, adjudication, local persistence, and JSON export.
- Run independent read-only package audit and correct every material finding.
- Test all flows in a real headless browser; close the named session and verify no leftovers.
- Commit the review package without an approval record.

## Not In Scope

- Collecting or asserting real human reviews in automated tests, changing the calibration bundle, Azure execution, live package freeze, hidden gold, or readiness behavior.

## Target Areas

- `review-package/diagnostic-case.json`
- `review-package/readiness-diagnosis-human-review.schema.json`
- `review-package/readiness-diagnosis-adjudication.schema.json`
- `review-package/review.html`
- `review-package/adjudicate.html`
- this slice Outcome

## Exit Criteria

- Package/case/source/asset identities and digests are exact and bounded.
- The page directly renders the complete review obligations and canonical source list.
- Ordinary UI flows keep peer answers in separate reviewer-specific profiles/exports; the stated procedural-independence limitation is visible.
- Approve/revise, notes, per-reviewer persistence/export, dual-file adjudication, and machine export work without console errors.
- No approval record or human claim is committed; package remains `pending_two_human_reviews_and_adjudication`.
- Independent audit has no unresolved critical/high/medium finding.

## Previous Slice

[`02-provider-free-diagnosis.md`](02-provider-free-diagnosis.md)

## Next Slice

[`04-recommendation-and-handoff.md`](04-recommendation-and-handoff.md) after this package passes.

## Outcome

**Status:** Complete and pending human input. Package `package-readiness-diagnostic-block3-20260724-01` contains visible case `case-readiness-diagnostic-block3-activity-return-authorization-01`, source/case digest binding, two closed export schemas, a one-reviewer-at-a-time page, and a separate adjudication page. The case validates with digest `sha256:10d0b7888e99401241135c0f7553e5ed3f6a6e0e31ac6e6634ed0c41c6f30d33`, `expected: null`, `liveEligible: false`, and state `pending_two_human_reviews_and_adjudication`.

**Authority and audit:** The bridge is explicitly visible/non-certifying and never enters calibration or generation certification. Independent package audit's only medium finding was missing export schemas; both closed package-local contracts were added. Re-audit's relative-reference finding was corrected for both reviewer slots; final pre-browser audit passed with no material issue. Completion audit identified abbreviated facet descriptions, so all eight were replaced with exact canonical rubric text and the focused re-audit passed with no unresolved material finding. No labels, approval record, live package, or human identity is committed.

**Browser proof:** Three isolated Playwright CLI sessions exercised blank defaults, incomplete-submit rejection, reviewer-specific persistence, required-facet semantic rejection, Reviewer A approve export, distinct Reviewer B revise export, peer-key isolation, duplicate reviewer/adjudicator rejection, disagreement rendering, adjudication persistence, stable machine export, download names, labels/headings, and zero-schema-error validation of both reviews plus adjudication. Every export retained `calibration:false`, `certification:false`, and `liveAuthorization:false`; test values used only `reviewer-test-only-*` IDs. All consoles ended at zero errors/warnings.

**Cleanup and safety:** File URLs were blocked before page load, so the package was served on isolated localhost port `18991`; no backend/provider port or Azure was used. All three sessions closed, Playwright reported no browsers, the surviving owned HTTP child was stopped, and port `18991` is free. Test downloads remained in session-temporary `.playwright-cli` storage; no approval/adjudication JSON was written to the review package. No `.env`, S15/generated identity, dependency, push, or deployment occurred.
