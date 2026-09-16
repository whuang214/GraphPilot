# Slice 01: Semantic Review Diagnosis

## Purpose

Identify the exact provider-free prompt–projection–schema–validator mismatch that caused the controlled anchor's first semantic-review response to fail `finding_invalid @ $`, without changing behavior or conflating generation, host, or runtime performance.

## Background

Block 5 recorded a first semantic-review call of 42,267.6134 ms followed by a 37,787.5872 ms semantic-review response-repair call. The repaired response passed and final reviewed quality was 75/pass with no semantic candidate repair. Safe capture retained the role, response digest, validation code/path, request/response bytes, tokens, and timing, but intentionally did not retain raw provider text. Diagnosis therefore must not claim the original private response shape; it must prove the smallest mismatch class using exact projection/backend-validator witnesses tied to the recorded code/path.

## Included Work

- Trace semantic-review prompt, provider strict-schema projection, backend response schema, finding allowlist/conditional rules, validator, response-repair input, and final result assembly.
- Recover all safe Block 5 facts for the semantic-review and response-repair calls without reading secret/provider raw content.
- Enumerate bounded candidate shapes that pass the provider projection but fail backend validation with `finding_invalid @ $`.
- Reproduce the recorded failure class provider-free and contrast a minimally corrected shape that passes backend validation.
- Determine whether the missing contract is an explicit finding rule, allowlist, conditional/endpoint rule, or bounded repair instruction.
- Keep the separate generation `bdd_relationship_endpoints_invalid @ $.edges[3]` event as a control only; do not diagnose or change it here.
- Produce a root decision with exact owner, evidence, limitation, correction boundary, regression names, live-proof expectation, and rollback.
- Independently audit the diagnosis before authorizing S02.

## Not In Scope

Production/test/prompt/schema edits; provider calls; host-interface changes; generation diagnosis; validator weakening; packet/cache/effort/MCP/local/browser optimization; calibration/certification/promotion; S15/Stage C.

## Target Areas

- immutable Block 5 event/trace/result evidence (read-only)
- `backend/services/generation/review/semantic_review_service.py`
- `backend/services/generation/review/semantic_review_rubric.py`
- context semantic-review prompt/response/repair schemas
- Azure structured-output projection and backend schema registry/validators
- this group's `evidence/semantic-review-diagnosis/`

## Exit Criteria

- Recorded safe facts and missing-raw limitation are explicit.
- At least one exact bounded witness passes provider projection and produces backend `finding_invalid @ $`; a minimal corrected witness passes.
- Root owner is unique enough for one narrow S02 correction, or S02 stops for a design decision.
- Proposed regressions fail before the correction and cover prompt/projection/validator parity without overfitting the cold-room answer.
- Independent audit has no unresolved critical/high/medium finding.
- No tracked runtime behavior changed and no provider call occurred.

## Previous Slice

[Block 5 Re-Audit and Handoff](../../../05-complete-live-anchor-and-reaudit/04-reaudit-and-handoff.md)

## Next Slice

[`02-semantic-review-correction.md`](02-semantic-review-correction.md) only after an audited focused root.

## Outcome

**Status:** Complete · independently audited PASS to S02.

**Evidence:** Immutable Block 5 safe events bind the 42,267.6134 ms semantic-review call, `finding_invalid @ $`, and 37,787.5872 ms response-repair call without retaining or accessing provider text. Three bounded context-BDD shapes pass Azure's projected strict schema and the complete backend response schema, then reproduce the exact runtime signature: facet/code mismatch, a finding on a sufficient facet, and a finding whose facet differs from its container. The facet/code witness reproduces in all six mode/type cells. A smallest corrected `goalFidelity` / `goal_mismatch` witness passes backend assembly without response repair. Machine and human evidence live under [`evidence/semantic-review-diagnosis/`](../../lane-b/evidence/semantic-review-diagnosis/provider-free-proof.md).

**Root:** The unique owner is `semantic_review_prompt_projection_schema_validator_contract`: prompts and provider-visible input expose no per-facet finding-code allowlist or complete finding conditionals, while backend assembly enforces the facet/code map, containing-facet equality, and below-minimum ownership. The original private response variant remains unknowable and is not claimed. S02 is bounded to projecting the existing allowlist, making those rules exact in initial/repair prompts, bumping changed prompt identities while retaining old assets, and preserving validator/repair/rubric/public authority. Generation's separate endpoint failure remains an unchanged control.

**Audit and verification:** Independent read-only audit found one medium regression-naming ambiguity; dedicated initial- and repair-prompt below-minimum tests resolved it, and focused re-audit passed with zero critical/high/medium finding. Inline fake-client proof created no files, changed no runtime/test source, and made zero provider calls. Controlled accounting remains 10/1000; the distinct external host call keeps aggregate accounting at 11/1000. No `.env`, raw provider content, S15/Stage C, host/generation optimization, calibration, certification, promotion, deployment, or push occurred.
