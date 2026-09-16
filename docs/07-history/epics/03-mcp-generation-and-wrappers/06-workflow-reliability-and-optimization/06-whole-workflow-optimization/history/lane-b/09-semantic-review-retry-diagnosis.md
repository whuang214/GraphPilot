# Slice 09: Semantic Retry Diagnosis

## Purpose

Refresh the historical semantic-review finding-contract diagnosis against the retained generation baseline and determine whether one current-V1 correction remains narrowly supportable despite g2's naturally valid semantic first response.

## Background

Block 5 recorded `finding_invalid @ $` and a 37,787.5872 ms response-repair call. Historical provider-free witnesses proved a prompt/projection/schema/validator mismatch, but the correction was reverted after its proof failed before provider dispatch. Retained g2 used unchanged semantic code and happened to be first-response valid with no repair, so the retry has no current repair call to claim as an incremental baseline saving.

## Execution Contract

- **Inputs:** historical S01 evidence, reverted correction history, retained generation commit `a17bc40`, g2 live result, current semantic source.
- **Outputs:** refreshed provider-free proof, exact current-V1 owner/correction boundary, regression names, and diagnosis audit.
- **Exclusive ownership:** S09 Outcome and `evidence/semantic-review-retry-diagnosis/` only.
- **Forbidden:** production/test changes, generation/B0/Lane A/shared docs, provider calls, `.env`, S15/Stage C.
- **Parallelism:** none; read-only source and fake/in-memory proof.
- **Cancellation:** non-unique root, dependence on raw provider content, or material audit finding stops S10.

## Included Work

- Re-run the three bounded finding witnesses, six mode/type facet-code matrix, and corrected witness against current source.
- Verify g2's accepted semantic response does not disprove the historical contract gap.
- Select the exact current-V1 in-place correction without V2 assets or compatibility branches.
- Record that contract correctness alone cannot satisfy retention without incremental measured benefit over g2.

## Not In Scope

Implementation, provider/live calls, scoring/status/validator weakening, generation changes, packet/cache/readiness/local work, Lane A, promotion/certification.

## Target Areas

Historical/current semantic prompt/input/schema/validator sources (read-only), S09 evidence, and this Outcome.

## Exit Criteria

- Current provider-free witnesses reproduce and a corrected witness passes.
- One current-V1 owner and exact affected files/regressions are independently audited.
- g2 first-response validity is treated as an observed control, not disconfirmation or credited saving.
- No behavior or provider usage changes.

## Previous Slice

[`08-generation-wave-decision.md`](08-generation-wave-decision.md)

## Next Slice

[`10-semantic-review-retry-correction.md`](10-semantic-review-retry-correction.md) only after audited S09.

## Outcome

**Status:** Complete · provider-free current-V1 root/audit PASS; S10 narrowly implementable with no live authorization.

**Proof:** Historical S01 safe evidence remains exact, and all 15 traced semantic prompt/input/response/repair/registry/projector/validator/test files are byte-equivalent from its proof source `043ff93` to current HEAD `c3409b8`; the reverted V2 commits leave no backend diff from pre-correction `a4f52ba` to rollback `3ccf5cf`. Current executable proof rebuilt three provider-projection/full-schema-valid finding witnesses that each naturally reach `finding_invalid @ $`, reproduced the facet/code witness in all six direct/context × diagram-type cells, bound the exact current-V1 response-repair packet, and passed a corrected `goalFidelity` / `goal_mismatch` witness in one fake call with no response repair. Machine/Markdown proof and root are canonically self-digested under [`evidence/semantic-review-retry-diagnosis/`](../../lane-b/evidence/semantic-review-retry-diagnosis/provider-free-proof.md).

**Root and g2:** The unique owner remains `semantic_review_prompt_projection_schema_validator_contract`: current V1 prompts/input expose neither `findingCodesByFacet` nor the containing-facet/applicable-below-minimum rules, while backend assembly enforces all three. Retained g2's unchanged semantic first response was valid with zero response/candidate repair; that one conforming sample does not disprove an existential contract gap, but it means there is no current repair-call saving baseline. S10 is bounded to deriving/projecting the existing map, requiring it in current V1 input schemas, and updating the four current V1 initial/repair prompts **in place**, with no V2 assets/identities/compatibility branch and no validator/scoring/repair weakening. Exact files, unchanged controls, and failing-before/preserving regression names are in [`root-decision.md`](../../lane-b/evidence/semantic-review-retry-diagnosis/root-decision.md).

**Audit and verification:** Historical independent audit plus current source-equivalence/mechanical refresh passed with zero critical/high/medium finding. The durable proof passed with 3 witnesses, 6 matrix cells, 1 corrected witness, response-repair/g2 controls, 19 fake calls, 0 provider calls, proof `sha256:af89f1f24b25457f4b5e031b431e12ead552f8108512eb0e2af127d7833033ab`, and root `sha256:5d1c483a8323062b941dbf063bdf9176b9c3f0eb4d8cd685446f96aed8a4b93d`. Focused current prompt/identity/provider-projection/semantic-review tests passed 18/18 in 6.659s with zero system-check issue. Only this Outcome and new `evidence/semantic-review-retry-diagnosis/**` were written; no production/test/prompt/schema/shared doc/provider/`.env`, generation/B0/Lane A, S15/Stage C, commit, or push occurred. Controlled/aggregate accounting remains 13/1000 and 14/1000.
