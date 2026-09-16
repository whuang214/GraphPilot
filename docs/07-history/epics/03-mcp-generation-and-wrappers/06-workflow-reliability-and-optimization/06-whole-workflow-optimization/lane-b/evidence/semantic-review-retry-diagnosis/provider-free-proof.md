# Semantic Review Retry Provider-Free Proof

- Machine evidence: [`provider-free-proof.json`](provider-free-proof.json)
- Machine self-digest: `sha256:af89f1f24b25457f4b5e031b431e12ead552f8108512eb0e2af127d7833033ab`
- Executable proof: [`verify_provider_free.py`](verify_provider_free.py)
- Executable SHA-256: `sha256:df8db5df98f0c0f44470f3977873c415e291938770e1dd2ba4c82bcd40df116e`
- Current source: `c3409b86a61c62f61ac4a59627da6b3a70db0bd9`
- Provider calls: **0**
- Production/test/prompt/schema/shared-document changes: **none**
- Root owner: `semantic_review_prompt_projection_schema_validator_contract`

## Historical Safe Fact and Current Control

Historical S01 remains the safe origin proof. Block 5 recorded a completed semantic-review call followed by
`finding_invalid @ $` and one 37,787.5872 ms semantic response-repair call. The raw provider response was intentionally
not retained and was not accessed here, so neither S01 nor S09 claims which bounded invalid finding variant occurred.

The retained g2 result is a second, different fact. Under unchanged semantic-review V1 code/assets, g2 completed only
`readiness`, `generation`, and `semantic_review`; its semantic first response was valid, reviewed quality was 100/pass,
and semantic response-repair/candidate-repair counts were both zero
(`../generation-endpoint-wave/live-result.json:21-35`). Its tracked summary also binds observation
`observation-live-workflow-anchor-g`, diagnostics run `run-g`, 26 files/27,204 bytes, and result/observation/terminal/diagnostics
digests (`live-result.json:8-19`, `52-60`). That accepted sample **does not disprove** the contract gap.
The contract proof is existential: current provider-visible instructions/schema permit bounded outputs that current backend
policy rejects. One conforming draw does not make those permitted-invalid shapes impossible.

This also means there is **no current repair-call saving baseline**. The historical 37,787.5872 ms call remains motivation,
not a benefit S10/S11 may credit against g2. Any retention claim must be incremental over g2, whose semantic response-repair
count is already zero.

## Current Prompt, Input, Schema, and Validator Trace

| Boundary | Current V1 fact | Consequence |
| --- | --- | --- |
| Initial prompts | Direct/context say only “allowlisted findings” but provide no per-facet map and state neither containing-facet equality nor applicable-below-minimum ownership (`backend/assets/prompts/direct-semantic-review-v1.md:1-3`; `context-semantic-review-v1.md:1-3`). | A provider can satisfy the text while selecting a globally valid code unrelated to the containing facet or attaching a finding to a sufficient facet. |
| Response-repair prompts | Direct/context preserve the attempted assessment and repair shape/references, but state none of the three finding rules (`direct-semantic-review-response-repair-v1.md:1-3`; `context-semantic-review-response-repair-v1.md:1-3`). | The natural repair receives a generic diagnostic rather than the complete finding contract. |
| V1 identities/assets | Current registries select four V1 identities (`backend/services/shared/schema_identities.py:107-110`); the four V1 files exist and no corresponding V2 file exists. | The retry correction boundary is current V1 in place, not a new version layer. |
| Review-input projection | `_review_input` sends element/authority allowlists plus the composed rubric, but no `findingCodesByFacet` (`backend/services/generation/review/semantic_review_service.py:352-391`). | The provider sees facet IDs and `minimumRating`, while the backend-owned code map remains undisclosed. |
| V1 input schemas | Direct/context allowlists require only reference/schema-rule arrays (`direct-semantic-review-input.json:388-413`; `context-semantic-review-input.json:449-479`). | Current schemas neither define nor require a per-facet finding-code projection. |
| Complete response schemas | Each response schema exposes one global 15-code enum (`direct-semantic-review-response.json:76-94`; `context-semantic-review-response.json:88-106`) and no facet/code map. | All three witnesses are complete-schema valid. |
| Provider strict projection | The projector retains the supported structural subset and drops conditionals when siblings remain (`backend/services/llm/llm_client.py:133-157`, `166-222`). | The global enum remains; containing-facet, per-facet code, and below-minimum rules are not provider-schema enforced. |
| Backend registry | `FACET_FINDING_CODES` defines the exact code tuple for every one of 37 facets (`backend/services/generation/review/semantic_review_rubric.py:699-843`). | Backend finding policy is already complete and remains authoritative. |
| Backend assembly | Assembly requires the finding facet to equal its container, validates the code against that facet, and rejects a finding when calculated severity is absent (`backend/services/generation/review/semantic_review_service.py:446-480`). | Each violated rule becomes the same response-repair diagnostic, `finding_invalid @ $`. |
| Repair binding | `_repair_review_response` embeds the identical review input, rejected response, generic code/path, attempt 1, and current V1 identities before calling the same response schema (`semantic_review_service.py:408-444`). | Repair is correctly fail-closed; it should be preserved, not suppressed. |

## Three Finding-Invalid Witnesses

Each witness starts from the current context-BDD training fixture response in exact rubric order. Only the named rating and
finding fields change. Every response passes the current Azure strict-schema projection and complete backend response schema,
then the fake runtime naturally reaches exactly `finding_invalid @ $` and consumes one queued clean response repair.

| Witness | Relevant shape | Deterministic backend reason | Runtime |
| --- | --- | --- | --- |
| Facet/code mismatch | `goalFidelity`, rating `1`, finding facet `goalFidelity`, code `scope_violation` | code is not allowed for `goalFidelity` | `finding_invalid @ $` |
| Finding without gap | `goalFidelity`, rating `4`, code `goal_mismatch` | sufficient facet cannot emit a finding | `finding_invalid @ $` |
| Finding facet mismatch | containing `goalFidelity`, rating `1`, finding facet `scopeCompliance`, code `scope_violation` | finding facet differs from container | `finding_invalid @ $` |

The machine evidence binds response digests and exact validator messages. These are bounded mismatch-class witnesses, not
reconstructions of the absent Block 5 response.

## Six-Cell Facet/Code Matrix

The facet/code mismatch was reconstructed independently for every direct/context × Activity/Use Case/BDD cell:

| Mode | Activity | Use Case | BDD |
| --- | --- | --- | --- |
| Direct | provider/full pass → `finding_invalid @ $` | provider/full pass → `finding_invalid @ $` | provider/full pass → `finding_invalid @ $` |
| Context | provider/full pass → `finding_invalid @ $` | provider/full pass → `finding_invalid @ $` | provider/full pass → `finding_invalid @ $` |

Each cell made exactly two fake calls (initial plus response repair) and returned the queued clean post-repair review. The six
per-cell digests are recorded in the JSON. This rules out a context-BDD-only or cold-room-content-only explanation.

## Corrected Witness and Response-Repair Binding

The smallest policy-coherent witness keeps `goalFidelity` applicable at rating `1` and uses a `goalFidelity` /
`goal_mismatch` finding. It passes provider projection, complete response schema, and backend assembly; it returns the expected
`blocked` review through one fake call and does **not** trigger response repair.

For the invalid facet/code witness, the captured second fake-call input proves:

- the repair input carries the byte-equivalent parsed semantic-review input from call one;
- its rejected response digest equals the first response digest;
- its only safe diagnostic is `finding_invalid @ $` and `repairAttempt` is `1`;
- it binds `graphpilot.context.semantic-review-response-repair-prompt.v1` and
  `graphpilot.context.semantic-review-response.v1`;
- both system prompts are the current V1 assets; and
- the embedded review input still has no `findingCodesByFacet`.

This is the natural response-repair path that S10 must keep as a fail-closed fallback.

## Root Boundary

The unique current root remains `semantic_review_prompt_projection_schema_validator_contract`. Provider-visible V1 prompt,
input, and response-schema boundaries permit all three shapes; current semantic-review backend policy rejects them; repair and
downstream result assembly work once a valid response is supplied. No generation, readiness, generic projector, host, MCP,
layout, persistence, browser, or scoring defect is needed.

The exact S10 boundary is:

1. derive `findingCodesByFacet` from existing `FACET_FINDING_CODES` in composed-rubric order;
2. project and require it in both current V1 private review inputs, updating V1 input/repair examples;
3. update the four current V1 initial/response-repair prompt assets in place with containing-facet, per-facet-code, and
   applicable-below-minimum rules;
4. retain every V1 identity, response schema, backend validator, response repair, rubric/score/status/severity rule, and public
   result; and
5. add **no V2 file, V2 identity, compatibility branch, or trace-version accommodation**.

Exact files and regression names are machine-authoritative in [`root-decision.json`](root-decision.json).

## Verification

The durable proof ran from `backend/` with no-dotenv settings and Azure values explicitly blank:

```powershell
$env:AZURE_OPENAI_ENDPOINT=""
$env:AZURE_OPENAI_API_KEY=""
$env:AZURE_OPENAI_DEPLOYMENT=""
$env:PYTHONPATH="."
uv run --with-requirements ..\requirements.txt python ..\docs\03-development-and-delivery\epics\03-mcp-generation-and-wrappers\06-workflow-reliability-and-optimization\06-whole-workflow-optimization\evidence\semantic-review-retry-diagnosis\verify_provider_free.py
```

Result: **PASS** — 3 bounded witnesses, 6 matrix cells, corrected no-repair witness, response-repair binding, g2 control,
19 fake calls, self-digested proof/root JSON, and **0 provider calls**.

Focused current tests ran under the same blank provider boundary:

```powershell
uv run --with-requirements ..\requirements.txt python manage.py test --settings graphpilot.live_anchor_settings tests.llm.test_llm_client.ProviderStrictSchemaTests tests.llm.test_prompt_service.RealTemplatesExistTests tests.generation.test_generation_foundation.GenerationContractIdentityTests tests.generation.test_semantic_review_service
```

Result: **18 tests passed in 6.659s**; system check reported zero issues.

## Limits

This proof identifies the current owner and correction boundary. It does not identify the historical private response, change
runtime behavior, authorize or make a provider call, establish an incremental speed saving over g2, measure a candidate,
calibrate, certify, promote, deploy, or modify S15/Stage C.
