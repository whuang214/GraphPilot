# Semantic Review Retry Provider-Free Correction

- Machine authority: [`provider-free-correction.json`](provider-free-correction.json)
- Source commit: `5ec80b7ed4cd5eb24fbced0532079cb737ad58c4`
- Version policy: current private V1 in place only
- Provider calls: **0**
- Commit: **none**

## Failing-Before Capture

The eight S09-named regressions were added before any production, prompt, schema, or runtime-doc correction and run together:

```powershell
cd backend
uv run python manage.py test tests.generation.test_semantic_review_service.SemanticReviewServiceTests.test_review_input_exposes_finding_codes_for_every_rubric_facet tests.generation.test_semantic_review_service.SemanticReviewServiceTests.test_current_v1_review_input_schema_requires_finding_codes_by_facet_in_both_modes tests.generation.test_semantic_review_service.SemanticReviewServiceTests.test_facet_code_contract_is_consistent_for_all_six_cells tests.llm.test_prompt_service.RealTemplatesExistTests.test_review_prompt_exposes_finding_conditional_contract tests.llm.test_prompt_service.RealTemplatesExistTests.test_review_prompt_requires_below_minimum_rating_for_findings tests.llm.test_prompt_service.RealTemplatesExistTests.test_review_repair_prompt_exposes_finding_conditional_contract tests.llm.test_prompt_service.RealTemplatesExistTests.test_review_repair_prompt_requires_below_minimum_rating_for_findings tests.generation.test_semantic_review_service.SemanticReviewServiceTests.test_invalid_private_response_repair_reuses_current_v1_finding_contract --verbosity 2
```

Exact summary:

```text
Ran 8 tests in 3.326s
FAILED (failures=18)
System check identified no issues (0 silenced).
```

| Named regression | Exact failing-before result |
| --- | --- |
| `test_review_input_exposes_finding_codes_for_every_rubric_facet` | `AssertionError: None != [{'facet': 'goalFidelity', 'codes': ['goa[2117 chars]a']}]` |
| `test_current_v1_review_input_schema_requires_finding_codes_by_facet_in_both_modes` | Direct: `AssertionError: 'findingCodesByFacet' not found in ['elementIds', 'requirementRefs', 'assumptionRefs']`; context: `AssertionError: 'findingCodesByFacet' not found in ['elementIds', 'claimRefs', 'assumptionRefs', 'schemaRules']` |
| `test_facet_code_contract_is_consistent_for_all_six_cells` | All six direct/context × diagram-type subcases: `AssertionError: unexpectedly None` |
| `test_review_prompt_exposes_finding_conditional_contract` | Both modes: `AssertionError: 'must equal its containing rubric facet `id`' not found in <current V1 initial prompt>`; the machine authority preserves each complete prompt-bearing assertion. |
| `test_review_prompt_requires_below_minimum_rating_for_findings` | Both modes: `AssertionError: 'below its rubric `minimumRating`' not found in <current V1 initial prompt>`; the machine authority preserves each complete prompt-bearing assertion. |
| `test_review_repair_prompt_exposes_finding_conditional_contract` | Both modes: `AssertionError: 'must equal its containing rubric facet `id`' not found in <current V1 response-repair prompt>`; the machine authority preserves each complete prompt-bearing assertion. |
| `test_review_repair_prompt_requires_below_minimum_rating_for_findings` | Both modes: `AssertionError: 'below its rubric `minimumRating`' not found in <current V1 response-repair prompt>`; the machine authority preserves each complete prompt-bearing assertion. |
| `test_invalid_private_response_repair_reuses_current_v1_finding_contract` | `AssertionError: None != [{'facet': 'goalFidelity', 'codes': ['goa[2117 chars]a']}]` |

The complete prompt-bearing assertion payloads were:

```text
AssertionError: 'must equal its containing rubric facet `id`' not found in 'Review the supplied direct logical candidate against every composed rubric facet and the exact conceptual authority.\n\nReturn every facet exactly once in rubric order. Propose only allowlisted findings, references, and direct resolution kinds. Do not assign severity, score, status, or pass/fail; backend policy owns those values. Do not rewrite the candidate, add authority, expose hidden reasoning, or return prose outside the strict response schema.\n'
AssertionError: 'must equal its containing rubric facet `id`' not found in 'Review the supplied context logical candidate against every composed rubric facet and the exact selected-claim/accepted-assumption authority.\n\nReturn every facet exactly once in rubric order. Check viewpoint fidelity, grounding completeness, and origin relevance/minimality. Propose only allowlisted findings, references, and context resolution kinds. Do not assign severity, score, status, or pass/fail; backend policy owns those values. Do not rewrite authority, expose hidden reasoning, or return prose outside the strict response schema.\n'
AssertionError: 'below its rubric `minimumRating`' not found in 'Review the supplied direct logical candidate against every composed rubric facet and the exact conceptual authority.\n\nReturn every facet exactly once in rubric order. Propose only allowlisted findings, references, and direct resolution kinds. Do not assign severity, score, status, or pass/fail; backend policy owns those values. Do not rewrite the candidate, add authority, expose hidden reasoning, or return prose outside the strict response schema.\n'
AssertionError: 'below its rubric `minimumRating`' not found in 'Review the supplied context logical candidate against every composed rubric facet and the exact selected-claim/accepted-assumption authority.\n\nReturn every facet exactly once in rubric order. Check viewpoint fidelity, grounding completeness, and origin relevance/minimality. Propose only allowlisted findings, references, and context resolution kinds. Do not assign severity, score, status, or pass/fail; backend policy owns those values. Do not rewrite authority, expose hidden reasoning, or return prose outside the strict response schema.\n'
AssertionError: 'must equal its containing rubric facet `id`' not found in 'Repair only the shape and allowlisted references of the rejected direct semantic-review response.\n\nPreserve the attempted assessment; do not re-evaluate the candidate or change ratings to improve the result. Return every required facet exactly once and only the strict private response schema. Do not return severity, score, status, prose, or hidden reasoning.\n'
AssertionError: 'must equal its containing rubric facet `id`' not found in 'Repair only the shape and allowlisted references of the rejected context semantic-review response.\n\nPreserve the attempted assessment; do not re-evaluate the candidate or change ratings to improve the result. Return every required facet exactly once and only the strict private response schema. Do not return severity, score, status, prose, or hidden reasoning.\n'
AssertionError: 'below its rubric `minimumRating`' not found in 'Repair only the shape and allowlisted references of the rejected direct semantic-review response.\n\nPreserve the attempted assessment; do not re-evaluate the candidate or change ratings to improve the result. Return every required facet exactly once and only the strict private response schema. Do not return severity, score, status, prose, or hidden reasoning.\n'
AssertionError: 'below its rubric `minimumRating`' not found in 'Repair only the shape and allowlisted references of the rejected context semantic-review response.\n\nPreserve the attempted assessment; do not re-evaluate the candidate or change ratings to improve the result. Return every required facet exactly once and only the strict private response schema. Do not return severity, score, status, prose, or hidden reasoning.\n'
```

The first test attempt could not import Django because this clean worktree had no virtual environment. `uv venv` and `uv pip install -r requirements.txt` installed the pinned dependencies without changing project dependency files; the recorded failing run above is the first executable regression result.

## Preservation Baseline

Before implementation, the three finding-contract witnesses, corrected witness, current-V1/no-V2 guard, six-cell clean path, fail-closed reference/order checks, and semantic candidate repair all passed:

```text
Ran 7 tests in 4.363s
OK
System check identified no issues (0 silenced).
```

## Implementation

`SemanticReviewService` now derives `findingCodesByFacet` in composed rubric order from the existing
`FACET_FINDING_CODES` registry and includes it in direct and context review input. Both current V1 review-input schemas
require a bounded facet/code map. The existing response-repair schemas still reference those V1 inputs, so their nested
`semanticReviewInput` requires the identical map; all four input/repair examples include it.

All four existing current V1 initial/response-repair prompts now require:

1. a finding's `facet` equals its containing rubric facet `id`;
2. its `code` belongs to that facet's projected `findingCodesByFacet` entry;
3. findings identify insufficient or unsupported meaning only when applicability is `applicable` and rating is below
   `minimumRating`; and
4. sufficient and not-applicable facets return empty `findings`.

No V2 asset/identity or compatibility branch exists. The response/result schemas and generic schema projector were not
changed. Backend validation and score/status/severity authority, one response-contract repair, and bounded semantic
candidate repair remain unchanged.

## Provider-Free Verification

| Gate | Result |
| --- | --- |
| Eight failing-before regressions after implementation plus seven preservation regressions | **15/15 passed** in 8.756s; system check clean |
| Focused semantic service/rubric, prompt, identity, and schema registry | **62/62 passed** in 24.476s; system check clean |
| Full backend | **1080 passed**, 5 skipped, in 1283.513s |
| Frontend lint/build/unit | 0 lint findings; build succeeded; **419/419 unit passed** |
| Frontend e2e | **43/43 passed** on the complete rerun |
| Diff/evidence | `git diff --check` clean; evidence JSON parses |

The first frontend `npm run verify` was run concurrently with the 1283-second backend gate. Its unit/build/lint stages
passed, but one e2e test exceeded its 30-second limit (`e2e/smoke.spec.ts:53`, “moves and reloads every authorable node
without starting connections”): 42 passed and 1 failed. After backend completion, that exact test passed alone in 27.7s
(33.3s command wall), and a fresh complete `npm run verify` passed all 43 e2e tests. No frontend source changed.

## Scope and Audit

Provider calls remained **0**. No generation correction, B0, Lane A, current board, epic/shared integration,
environment/provider/live, S15, or Stage C asset changed. Self-review and independent read-only audit
`independent-read-only-subagent-0c074fc6` found 0 critical/high/medium findings. Machine evidence self-digest is
`sha256:fa23ae51ca8999dea406a868713eb4477baee4e91054c1da4b4166488cb285ce`.
