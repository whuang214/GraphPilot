# Slice 05: Generation Endpoint Diagnosis

## Purpose

Identify provider-free the exact prompt–projection–schema–validator mismatch class behind Block 5 generation's `bdd_relationship_endpoints_invalid @ $.edges[3]`, without assuming a correction or changing semantic review, host behavior, or runtime performance.

## Background

Block 5's initial generation call completed in 44,694.0544 ms and reached one 26,052.5176 ms generation-repair call after the fourth edge failed endpoint rules. Raw provider output was intentionally not retained. The completed semantic-review wave was reverted and remains an unchanged baseline control.

## Execution Contract

- **Depends on / inputs:** committed S04 revert/guard decision, safe Block 5 endpoint event, current generation prompt/projection/schema/validator source.
- **Outputs:** bounded witnesses, one root decision or explicit design stop, independent audit, S05 Outcome.
- **Exclusive write ownership:** `evidence/generation-endpoint-diagnosis/` and S05 Outcome.
- **Forbidden/shared ownership:** production/tests, semantic-review/host work, group/current-state/decision/ledger/backlog reserved for S08, provider, `.env`, S15/Stage C.
- **Parallelism/resources:** none; read-only source/evidence, no ports/browser/provider.
- **Cancellation:** non-unique root, required broader behavior decision, raw-evidence dependency, or material audit finding stops S06.

## Included Work

- Trace the context BDD generation prompt, strict provider projection, complete logical schema, relationship-end rules, deterministic validator, repair packet, and accepted candidate assembly.
- Use only safe Block 5 `{code,path}`, digests, role, timing, bytes, and token evidence.
- Construct bounded provider-free shapes that pass provider projection/full schema and reproduce the exact endpoint failure; construct a smallest corrected shape that passes.
- Determine exactly one root owner or stop for design clarification.
- Keep current semantic-review response-repair behavior and all host/readiness/MCP/local/browser behavior unchanged controls.
- Produce safe evidence and an independent diagnosis audit.

## Not In Scope

Production/test/prompt/schema edits; provider calls; semantic-review or host correction; validator weakening; packet/cache/MCP/local/browser optimization; calibration/certification/promotion; S15/Stage C.

## Target Areas

- immutable Block 5 generation events (read-only)
- context BDD generation/repair prompts and logical schema
- deterministic BDD endpoint validator and repair assembly
- this group's `evidence/generation-endpoint-diagnosis/`

## Exit Criteria

- Safe facts and missing-raw limitation are explicit.
- At least one exact witness passes provider projection/full schema and yields `bdd_relationship_endpoints_invalid @ $.edges[3]`; a corrected witness passes.
- One narrow owner is supported, or S06 stops for design clarification.
- Proposed regressions fail before correction and cover all relevant modes/types without overfitting the cold-room answer.
- Independent audit has no critical/high/medium finding.
- No provider call or tracked runtime behavior change occurs.

## Previous Slice

[`04-wave-decision.md`](04-wave-decision.md)

## Next Slice

[`06-generation-endpoint-correction.md`](06-generation-endpoint-correction.md) only after an audited focused root.

## Outcome

**Status:** Complete · provider-free diagnosis and independent audit PASS; S06 narrowly implementable but held for user review.

**Evidence:** Safe Block 5 events bind the 44,694.0544 ms generation call, `bdd_relationship_endpoints_invalid @ $.edges[3]`, four-node/four-edge failed candidate, 26,052.5176 ms generation-repair call, and four-node/three-edge accepted candidate without retaining or accessing raw provider content. Source tracing proves only the bounded raw-shape class: both fourth-edge IDs resolved and at least one endpoint resolved to a `note`; semantic type, direction, IDs, end data, label, and origin remain unknowable and are not claimed. Ten synthetic direct/context × five-edge-semantic witnesses pass provider projection and complete logical schema, then reproduce the exact code/path; two remove-edge controls pass, while Block/Block `commentLink` compatibility controls confirm that the validator has no semantic branch. Machine and human evidence live under [`evidence/generation-endpoint-diagnosis/`](../../lane-b/evidence/generation-endpoint-diagnosis/provider-free-proof.md).

**Root:** The unique owner is `generation_prompt_projection_schema_validator_contract`, class `semantic_blind_bdd_structural_endpoint_scope`: provider-visible BDD structural rules omit exact structural-versus-annotation endpoint scope, while deterministic validation applies the structural Block/Block rule to every edge and rejects note-attached `commentLink`. S06 is narrowly bounded to making the direct/context initial/repair `diagramModel` rules explicit, keeping four structural semantics Block/Block, and excluding `commentLink` from that structural validator rule—without adding a stricter converse comment-link policy or changing prompt assets, logical schemas/IDs, generic projection, repair authority, semantic review, host behavior, or public contracts. Exact affected files, failing-before regressions, strongest alternative, guards, and rollback are recorded in [`root-decision.md`](../../lane-b/evidence/generation-endpoint-diagnosis/root-decision.md).

**Verification and gate:** The durable `verify_provider_free.py` `FakeLLMClient` proof created no files and reached valid in-memory PyGraphviz/canonical assembly after one synthetic repair. With Azure variables blank and no-dotenv settings, 85 focused strict-schema/generation/repair/review/assembly/live-harness tests passed in 94.265s. No production/test/prompt/schema file, `.env`, provider/Azure call, semantic-review/host behavior, S15/Stage C, calibration, certification, promotion, deployment, commit, or push changed. Authoring-agent mechanical checks and independent read-only audit pass with zero critical/high/medium findings; [`audit.md`](../../lane-b/evidence/generation-endpoint-diagnosis/audit.md) records the reviewer and keeps S06 intentionally unstarted until the user reviews both lane handoffs.
