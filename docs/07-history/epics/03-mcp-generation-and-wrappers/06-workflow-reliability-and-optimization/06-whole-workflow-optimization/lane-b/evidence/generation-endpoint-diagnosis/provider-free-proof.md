# Generation Endpoint Provider-Free Proof

- Machine evidence: [`provider-free-proof.json`](provider-free-proof.json)
- Executable proof: [`verify_provider_free.py`](verify_provider_free.py)
- Source: `4bd7ba4dcb278a251fe0bb87e4112ce39f42cdf9`
- Provider calls: **0**
- Production/test/prompt/schema changes: **none**
- Root owner: `generation_prompt_projection_schema_validator_contract`

## Safe Block 5 Baseline

Only committed safe evidence and safe immutable event metrics/issues were used. The initial generation call completed in
44,694.0544 ms and its strict response shape failed deterministic validation with
`bdd_relationship_endpoints_invalid @ $.edges[3]`. Its safe candidate event records four nodes, four edges, and only that
issue code. One generation-repair call completed in 26,052.5176 ms; its candidate event records four nodes, three edges,
and no issue code. No raw provider message, response, reasoning, or diagram payload was read.

The raw response was intentionally not retained. This diagnosis therefore does **not** claim the actual fourth edge, its
semantic type, IDs, direction, end data, label, or origin. The synthetic remove-edge correction mirrors only the safe
4-edge to 3-edge count transition; it is not a reconstruction of the live repair.

## Exact Failing Shape Class

The current validator establishes a narrower fact than the absent raw response:

1. `LogicalCandidateValidator._bdd` skips an edge unless both endpoint IDs resolve
   (`backend/services/generation/pipeline/pre_layout_generation_service.py:404-406`).
2. It emits the safe code when either resolved endpoint is not a `block`
   (`backend/services/generation/pipeline/pre_layout_generation_service.py:407-411`).
3. The complete context BDD schema admits only `block` and `note` nodes
   (`backend/assets/schemas/context-logical-diagram-bdd.json:565-570`).

Therefore the exact safe class is: **the fourth BDD edge had two resolvable endpoint IDs and at least one resolved
`note` endpoint**. The code/path cannot distinguish the five allowed edge semantics, source/target orientation, or one
note from two notes. No stronger raw-edge claim is made.

## Prompt, Projection, Schema, and Validator Trace

| Boundary | Current fact | Consequence |
| --- | --- | --- |
| Context generation prompt | Requires the supplied diagram model but states no BDD endpoint matrix (`backend/assets/prompts/context-generation-v1.md:1-3`) | Exact endpoint semantics must come from the packet. |
| Provider input projection | `_diagram_model` injects catalog vocabularies and `structuralRules` (`backend/services/generation/requests/generation_packet_builder.py:351-384`) | The same projection reaches direct/context initial calls and repair authority. |
| Current BDD rules | Name generalization/composition direction and describe association vaguely; dependency and note/comment endpoints are absent (`backend/services/diagrams/validation/structural_constraints.py:320-325`) | The provider does not receive a complete semantic-specific endpoint matrix. |
| Catalog | `commentLink` is “an attachment from a comment to the element it annotates” and is authorable for BDD (`backend/services/diagrams/catalog/element_catalog.py:179`, `247-254`) | A note attachment is intended provider-visible vocabulary. |
| Provider strict projection | Retains only the supported structural subset (`backend/services/llm/llm_client.py:133-157`, `200-273`) | It retains the independent node/edge enums but cannot resolve edge IDs to node types. |
| Complete schemas | Direct/context independently admit `block|note` and all five edge semantics (`backend/assets/schemas/direct-logical-diagram-bdd.json:449-548`; `context-logical-diagram-bdd.json:545-652`) | These schemas deliberately delegate cross-item endpoint topology to deterministic code. |
| Endpoint validator | Applies one block/block predicate to **every** BDD edge before any semantic-specific branch (`backend/services/generation/pipeline/pre_layout_generation_service.py:404-417`), although shared connectivity already skips `commentLink` (`:285-287`) | It misclassifies annotation `commentLink` as a structural relationship and rejects note attachment. |
| Repair | The exact candidate and issue enter `validationIssues`; unchanged authority/diagram model is sent without examples (`backend/services/generation/pipeline/pre_layout_generation_service.py:701-795`) | Repair is working as designed but repeats the incomplete provider-visible matrix. |
| Accepted assembly | A valid repaired candidate is accepted (`:556-623`), consumed by semantic review, compacted (`backend/services/generation/pipeline/diagram_generation_service.py:869-881`), assembled and canonically validated (`:465-532`) | No downstream retarget/drop defect is needed to explain the event. |

The active design is already unambiguous: any new edge incident to a note becomes `commentLink`
(`docs/02-design-and-features/00-diagram-json-schema.md:68-77`), and generation conformance implements the same mapping
(`backend/services/generation/pipeline/generation_pipeline.py:380-393`). BDD association/composition endpoints reference
Blocks while notes/comment links do not establish structure
(`docs/02-design-and-features/diagram-schemas/bdd-diagram-blueprints.md:50-75`).

## Bounded Witnesses

The proof starts from the committed context BDD `irrigation-controller` training logical graph (three Blocks and three
valid relationships). It appends one complete synthetic `note` and one fourth note-to-Block edge. The edge semantic is
varied across all five BDD values. Context witnesses retain allowlisted fixture origins; direct witnesses remove origins
and select the direct identity. No cold-room content is used.

Every one of the ten direct/context × edge-semantic witnesses:

- passes `project_strict_output_schema(...)` plus `Draft202012Validator`;
- passes the complete mode-specific BDD logical schema;
- has no context provenance issue; and
- produces exactly `bdd_relationship_endpoints_invalid @ $.edges[3]`.

| Mode | Association | Composition | Generalization | Dependency | Comment Link |
| --- | --- | --- | --- | --- | --- |
| Direct | exact signature | exact signature | exact signature | exact signature | exact signature |
| Context | exact signature | exact signature | exact signature | exact signature | exact signature |

The per-cell witness digests are in `provider-free-proof.json`. This matrix proves why the safe code/path cannot reveal the
raw edge semantic.

## Compatibility and Corrected Controls

Two compatibility controls append a fourth `commentLink` between two Blocks. Provider projection, full schema, and the
current backend all pass them. This confirms that the validator does not branch by edge semantic; it is not treated as a
separate defect because current canonical/editor contracts require note incidence to become `commentLink` but do not
establish the converse or prohibit this existing compatibility shape.

The smallest current-validator correction removes only the synthetic fourth edge while retaining the note. It passes
provider projection, full schema, deterministic validation, and provenance in both modes. In the context fake-client
runtime, the invalid note-attached `commentLink` enters an exact `contextGenerationRepairInput`; one repaired response
reaches pre-layout acceptance with one repair round. Standard semantic handoff preserves the candidate, PyGraphviz
assembles four nodes/three edges in memory, origins survive, and canonical validation passes with only the expected
floating-note `disconnected_node` warning. No file or provider call is created.

## Root Boundary

The unique owner is the shared BDD structural-versus-annotation endpoint scope inside
`generation_prompt_projection_schema_validator_contract`. This is not a generic strict-schema projector defect, repair
defect, semantic-review defect, or assembly defect. The provider-visible packet omits the exact structural-versus-annotation scope, while the backend applies a structural
rule without checking edge semantic.

The whole-class S06 correction must make that scope identical on both sides:

- `association`, `composition`, `generalization`, and `dependency`: existing Block ↔ Block endpoints, retaining each
  relationship's existing direction/end rules;
- note attachments use `commentLink`; `commentLink` is excluded from the structural Block-endpoint/connectivity rule.

This is semantic scoping, not validator weakening: Block-only validation remains unchanged for every structural
relationship, while annotation is no longer misclassified. S06 must not add a stricter converse rule or reject existing
Block/Block `commentLink` compatibility shapes without a separate design decision.

## Verification

The durable witness proof ran with Azure settings blank and no-dotenv settings:

```powershell
$env:AZURE_OPENAI_ENDPOINT=""
$env:AZURE_OPENAI_API_KEY=""
$env:AZURE_OPENAI_DEPLOYMENT=""
$env:PYTHONPATH="."
cd backend
uv run --with-requirements ..\requirements.txt python ..\docs\03-development-and-delivery\epics\03-mcp-generation-and-wrappers\06-workflow-reliability-and-optimization\06-whole-workflow-optimization\evidence\generation-endpoint-diagnosis\verify_provider_free.py
```

Result: `status=pass`, 10 witness cells, 4 controls, 2 fake calls, one synthetic repair round, valid in-memory
`pygraphviz-dot` assembly, and **0 provider calls**.

Focused existing checks then ran under the same blank/no-dotenv boundary:

```powershell
uv run --with-requirements ..\requirements.txt python manage.py test --settings graphpilot.live_anchor_settings tests.llm.test_llm_client.ProviderStrictSchemaTests tests.generation.test_generation_packet_builder tests.generation.test_pre_layout_generation_service tests.generation.test_semantic_review_service tests.generation.test_diagram_generation_service tests.generation.test_diagram_generation_context_service tests.evaluation.workflow_audit.test_client tests.evaluation.workflow_audit.test_live_anchor_service
```

Result: **85 tests passed in 94.265s**; system check reported no issues.

## Limits

This proof identifies the exact safe shape class, unique contract owner, and narrow implementation boundary. It does not
identify the actual raw edge, guarantee what semantic the provider used, measure a candidate, authorize S06/S07 by itself,
change production behavior, call Azure, alter semantic review/host behavior, calibrate, certify, promote, or deploy.
