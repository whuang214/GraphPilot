# Semantic Review Retry Root Decision

- Machine authority: [`root-decision.json`](root-decision.json)
- Machine self-digest: `sha256:5d1c483a8323062b941dbf063bdf9176b9c3f0eb4d8cd685446f96aed8a4b93d`
- Provider-free proof: [`provider-free-proof.md`](provider-free-proof.md)
- Proof self-digest: `sha256:af89f1f24b25457f4b5e031b431e12ead552f8108512eb0e2af127d7833033ab`
- Recommendation: `focused_current_v1_implementation_correction`
- Owner: `semantic_review_prompt_projection_schema_validator_contract`
- Confidence: high in owner; bounded/unknown historical trigger variant
- Provider calls: **0**

## Decision

S10 is narrowly implementable. Project the existing backend-owned per-facet finding-code allowlist into both current private
V1 review inputs and make the same finding rules explicit in all four current V1 initial/response-repair prompts. Keep the
validator and one response-repair fallback fail-closed. Do **not** create a V2 prompt, identity, schema layer, compatibility
branch, or trace accommodation.

This decision corrects a provider-visible contract gap; it does not establish a current speed saving. Retained g2 already had
one valid semantic first response and zero semantic response-repair calls under unchanged semantic V1. S11/S12 therefore must
measure incremental benefit over a zero-repair g2 baseline, not credit the historical 37,787.5872 ms Block 5 repair.

## Decisive Evidence

1. Historical safe evidence binds `finding_invalid @ $` and one 37,787.5872 ms response-repair call but no raw response.
2. Current initial and repair prompts expose neither `findingCodesByFacet` nor containing-facet/applicable-below-minimum rules.
3. Current V1 review inputs contain the complete rubric and reference allowlists but no per-facet finding-code map.
4. Current full response schemas/provider projections expose one global 15-code enum; provider projection retains no relevant
   conditional.
5. Current backend assembly enforces containing-facet equality, `FACET_FINDING_CODES`, and below-minimum ownership.
6. Three current provider/full-schema-valid witnesses reproduce exactly `finding_invalid @ $` through natural fake response
   repair.
7. The facet/code witness reproduces in every direct/context × diagram-type cell.
8. A policy-coherent `goalFidelity` / `goal_mismatch` witness passes with one fake call and no response repair.
9. g2 is one conforming unchanged-code draw. It proves acceptance is possible, not that every provider-visible valid shape is
   backend valid.

The original Block 5 private variant remains unknowable and is not claimed. That limitation does not prevent owner selection:
every bounded current variant lies inside the same semantic-review prompt/input/schema/validator boundary.

## Exact Current-V1 Correction Files

### Production and private assets

- `backend/services/generation/review/semantic_review_service.py`
- `backend/assets/prompts/direct-semantic-review-v1.md`
- `backend/assets/prompts/context-semantic-review-v1.md`
- `backend/assets/prompts/direct-semantic-review-response-repair-v1.md`
- `backend/assets/prompts/context-semantic-review-response-repair-v1.md`
- `backend/assets/schemas/direct-semantic-review-input.json`
- `backend/assets/schemas/context-semantic-review-input.json`
- `backend/assets/schemas/direct-semantic-review-repair-input.json`
- `backend/assets/schemas/context-semantic-review-repair-input.json`

The repair-input schema structures need no new field because they already reference the review-input V1 schemas; their embedded
examples must add the required map so schema-example guards remain valid.

### Tests

- `backend/tests/generation/test_semantic_review_service.py`
- `backend/tests/llm/test_prompt_service.py`
- `backend/tests/generation/test_generation_foundation.py`

### Runtime/design synchronization for S10

- `backend/README.md`
- `backend/services/README.md`
- `docs/01-architecture/01-backend-architecture.md`
- `docs/02-design-and-features/04-generation-design.md`
- `docs/02-design-and-features/08-context-backed-generation/05-generation-and-provenance.md`
- `10-semantic-review-retry-correction.md` Outcome/evidence only as authorized by S10

## Explicitly Unchanged

S10 must not modify:

- `backend/services/shared/schema_identities.py` — all four current prompt identities remain V1;
- `backend/services/generation/review/semantic_review_rubric.py` — registry, rubric, severity, score, and status authority remain;
- `backend/services/llm/llm_client.py` — no generic projector change;
- either semantic-review response/result schema;
- `generation-trace.json` or `diagram_generation_service.py` — no compatibility/version branch;
- generation, readiness, B0, Lane A, host/MCP, packet/cache, persistence/layout/browser, provider configuration, public contracts,
  `.env`, S15, or Stage C; or
- any `*-semantic-review-v2.md` asset or `graphpilot.*.semantic-review*-prompt.v2` identity.

## Named Regressions

### Failing before S10

1. `test_review_input_exposes_finding_codes_for_every_rubric_facet`
2. `test_current_v1_review_input_schema_requires_finding_codes_by_facet_in_both_modes`
3. `test_facet_code_contract_is_consistent_for_all_six_cells`
4. `test_review_prompt_exposes_finding_conditional_contract`
5. `test_review_prompt_requires_below_minimum_rating_for_findings`
6. `test_review_repair_prompt_exposes_finding_conditional_contract`
7. `test_review_repair_prompt_requires_below_minimum_rating_for_findings`
8. `test_invalid_private_response_repair_reuses_current_v1_finding_contract`

### Characterization/preservation

1. `test_three_finding_contract_witnesses_trigger_exact_response_repair`
2. `test_corrected_finding_contract_witness_is_first_response_valid`
3. `test_current_v1_semantic_review_contract_has_no_v2_assets_or_identities`
4. existing `test_clean_review_for_all_six_cells`
5. existing `test_finding_facet_and_context_resolution_refs_are_fail_closed`
6. existing `test_wrong_order_and_unallowlisted_refs_fail_response_contract`
7. existing `test_semantic_candidate_repair_reruns_deterministic_checks_and_review`

The first eight must be captured failing against `c3409b8` before implementation and pass afterward. The characterization tests
must preserve exact invalid/valid behavior; they do not become provider performance claims.

## Alternatives

- **Facet-specific response branches:** deferred. They duplicate the facet catalog and still cannot bind all dynamic input
  allowlists/conditions under the provider subset.
- **New V2 layer:** forbidden for this retry. The prior V2 was unpromoted and reverted; current authority requires V1 in place.
- **Treat g2 as disconfirmation:** rejected. A valid sample does not close an existential contract gap.
- **Weaken validation or suppress repair:** forbidden.
- **More provider evidence before S10:** unnecessary for owner selection and unable to recover the intentionally absent raw
  response.

## S11 Retention and Rollback

S09 authorizes no provider call. After separately audited and committed S10, S11 still requires a new short B0-safe package,
new explicit authorization, and one immutable candidate. Both generation and semantic review must be first-response valid with
no repair roles, and all existing meaning/provenance/quality/persistence/diagnostics/browser/compatibility/recovery guards must
pass. Because g2 already has zero semantic response-repair calls, contract correctness alone cannot satisfy speed retention.

Rollback reverts only the S10 current-V1 correction commit while retaining S09, Block 5, g2, and any immutable S11 evidence.

## Audit State

Historical S01's independent reviewer passed the same owner/rules/no-weakening root after its one regression-naming correction,
with zero remaining critical/high/medium finding. S09 reconstructed every mechanical witness and trace on current source and
changed only the version policy: current V1 in place, no V2. The S09 mechanical audit is
[`audit.md`](audit.md); zero material finding remains.
