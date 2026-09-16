# Semantic Review Provider-Free Proof

- Machine evidence: [`provider-free-proof.json`](provider-free-proof.json)
- Source: `043ff93643025ad0ccefd68f080cc34e265bd72b`
- Provider calls: **0**
- Production changes: **none**
- Root owner: `semantic_review_prompt_projection_schema_validator_contract`

## Safe Baseline

Block 5 retained only bounded safe evidence. The semantic-review call completed in 42,267.6134 ms and failed first-response validation with `finding_invalid @ $`; one response-repair call then completed in 37,787.5872 ms. The repaired review produced reviewed quality 75/pass. The raw response was intentionally not retained and was not accessed, so this proof does not claim its private shape.

Generation's separate `bdd_relationship_endpoints_invalid @ $.edges[3]` event remains an unchanged control.

## Contract Trace

The direct/context review prompts say to propose only “allowlisted findings,” but neither prompt identifies the per-facet finding-code allowlist or states both finding conditionals. The private response schemas expose one global 15-code enum. Their Azure strict-schema projections retain that global enum but no facet-to-code mapping, containing-facet equality, or below-minimum requirement. The provider-visible review input includes facet IDs, applicability, thresholds, references, and rating anchors, but no per-facet finding-code map.

The backend is stricter by design: `FACET_FINDING_CODES` validates code by facet; a proposed finding must name its containing facet; and only a below-minimum applicable facet may emit a finding. Any violation reaches the response-repair boundary as the same safe `finding_invalid @ $` diagnostic.

## Bounded Witnesses

Each witness starts from a complete schema-valid context BDD response in exact rubric order. Only the listed fields change.

| Witness | Relevant shape | Provider projection | Full response schema | Runtime |
| --- | --- | --- | --- | --- |
| Facet/code mismatch | `goalFidelity`, rating `1`, code `scope_violation` | pass | pass | `finding_invalid @ $` |
| Finding without gap | `goalFidelity`, rating `4`, code `goal_mismatch` | pass | pass | `finding_invalid @ $` |
| Finding facet mismatch | containing `goalFidelity`, finding facet `scopeCompliance`, rating `1` | pass | pass | `finding_invalid @ $` |

The facet/code mismatch reproduces in all six direct/context × Activity/Use Case/BDD cells, so the mismatch is not cold-room content or context-BDD-only behavior.

The smallest corrected witness keeps rating `1` and changes only the finding to `goalFidelity` / `goal_mismatch`. It passes provider projection, full response schema, backend assembly, and the fake runtime without response repair. Its blocked result is expected mechanical proof, not an anchor-quality claim.

## Root Boundary

The unique owner is the provider-visible semantic-review finding contract. The original trigger variant remains unknowable, but all bounded variants share this one boundary: the provider contract permits a response that semantic-review backend policy rejects. S02 must make the complete finding contract explicit rather than guess which hidden variant occurred.

The narrow correction boundary is:

1. project the exact per-facet finding-code allowlist into both direct and context semantic-review inputs from the existing backend registry;
2. state in initial and response-repair prompts that a finding must stay in its containing facet, use that facet's code list, and appear only when the applicable rating is below `minimumRating`;
3. preserve backend validation and response repair unchanged as fail-closed safeguards;
4. add six-cell provider-projection/backend regressions plus focused conditional-rule regressions;
5. bump changed prompt identities while retaining old prompt assets, and apply the established additive private-v1 projection policy without changing public/result/rubric authority.

The stronger schema-only alternative would duplicate facet-specific response branches and still not express dynamic input allowlists under Azure's subset. It is broader and does not replace the explicit provider-input contract.

## Limits

This proof identifies the owner and correction class. It does not identify the original raw response, measure candidate improvement, change production behavior, call Azure, diagnose generation, calibrate, certify, or promote anything.
