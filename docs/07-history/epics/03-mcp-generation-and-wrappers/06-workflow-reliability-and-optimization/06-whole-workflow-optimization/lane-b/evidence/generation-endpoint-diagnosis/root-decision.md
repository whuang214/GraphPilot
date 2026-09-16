# Generation Endpoint Root Decision

- Machine authority: [`root-decision.json`](root-decision.json)
- Provider-free proof: [`provider-free-proof.md`](provider-free-proof.md)
- Recommendation: `focused_implementation_correction`
- Owner: `generation_prompt_projection_schema_validator_contract`
- Root class: `semantic_blind_bdd_structural_endpoint_scope`
- Confidence: high in owner; bounded/unknown raw edge variant
- Provider calls: **0**

## Decision

Independent diagnosis audit passed with no critical/high/medium finding. S06 is narrowly implementable without a provider
call, schema-ID change, prompt-asset change, or validator weakening, but remains held until the user reviews the separate B0
and S05 handoffs.

The provider-visible BDD `diagramModel` and deterministic BDD validator must share one exact endpoint scope:

- `association`, `composition`, `generalization`, and `dependency` require two existing Blocks;
- note attachments use `commentLink`, which is excluded from the structural Block-endpoint/connectivity rule.

The existing relationship-specific direction/end checks and `bdd_relationship_endpoints_invalid` fail-closed repair path
remain authoritative.

## Decisive Evidence

1. Safe Block 5 evidence records `bdd_relationship_endpoints_invalid @ $.edges[3]`, a 44,694.0544 ms generation call,
   and a 26,052.5176 ms repair call; no raw response is retained or claimed.
2. The validator can emit that code only when both endpoint IDs resolve and at least one resolves to a `note` under the
   complete `block|note` schema.
3. The generic prompt delegates to `diagramModel`; its current BDD structural rules omit complete structural-versus-annotation endpoint scope.
4. Provider projection and full schemas admit node and edge enums independently and cannot bind endpoint IDs to node
   types.
5. The validator applies the structural Block/Block rule to all five semantics and therefore rejects note-attached
   `commentLink`; Block/Block compatibility controls confirm there is no semantic branch.
6. The same validator already excludes `commentLink` from connectivity, and generation conformance maps note incidence to
   `commentLink`; only the BDD endpoint predicate has the inconsistent structural scope.
7. Ten bounded direct/context × five-semantic witnesses pass provider projection/full schema and reproduce the exact safe
   signature.
8. A smallest corrected witness passes both modes. Fake repair receives the exact issue and valid accepted assembly works
   unchanged downstream.

The raw edge semantic, direction, IDs, end data, label, and origin remain unknowable. The decision closes the entire
resolved-note endpoint class rather than guessing the private variant.

## S06 Affected Files

### Production

- `backend/services/diagrams/validation/structural_constraints.py` — make the BDD provider-visible `structuralRules` scope exact for
  initial and repair packets.
- `backend/services/generation/pipeline/pre_layout_generation_service.py` — scope the Block-only predicate to structural
  semantics while retaining the stable issue/repair authority.

### Tests

- `backend/tests/generation/test_generation_packet_builder.py`
- `backend/tests/generation/test_pre_layout_generation_service.py`

### Design and slice record

- `docs/02-design-and-features/04-generation-design.md` — state the implementation-backed provider/deterministic scope.
- `06-generation-endpoint-correction.md` Outcome.

The canonical schema and BDD notation owners already describe note incidence and Block structural endpoints correctly;
S06 should use them as controls rather than rewrite them. Direct/context BDD logical schemas and generic prompt assets do
not need modification: cross-item reference typing remains deterministic, and the current prompts already require the
supplied diagram model. The private current-V1 projection changes in place under the Block 6 contract.

## Failing-Before Regression Names

These exact tests should fail on `4bd7ba4` and pass only after the correction:

1. `test_bdd_generation_packets_expose_structural_endpoint_and_note_attachment_rules_in_both_modes`
2. `test_bdd_note_comment_link_is_excluded_from_structural_block_endpoint_rule_in_both_directions_and_modes`
3. `test_bdd_endpoint_scope_repair_packet_repeats_provider_visible_rules`
4. `test_bdd_note_comment_link_reaches_pre_layout_acceptance_without_generation_repair_in_both_modes`

Preserving coverage must also enumerate all four structural semantics × both modes with a Note endpoint and keep them
rejected; retain Block/Block `commentLink` as a characterized compatibility shape; prove projection/full-schema acceptance
before deterministic rejection; retain exact repair authority; and keep the Block 5 repaired candidate plus all twelve
training fixtures accepted.

## Strongest Alternative

**Validator-only semantic branching** is the strongest narrower alternative. It would exclude `commentLink` from the
structural Block-only rule, but it would leave structural-edge endpoint rules incomplete in the provider-visible packet. Since
the raw edge semantic is unknowable, it would not close the whole live failure class or prevent a provider-produced
non-`commentLink` Note edge from consuming repair. The paired projection/validator correction is therefore the smallest
whole-class correction.

A stricter semantic matrix—exactly one Note plus one Block and rejection of Block/Block or Note/Note `commentLink`—is
the strongest policy alternative. It is deferred because current canonical/editor contracts establish Note-incidence
coercion, not the converse; S06 does not need that broader authoring/validation choice. Schema- or prompt-only tightening
is insufficient because strict/full schemas cannot resolve endpoint IDs to node types, and guidance alone leaves annotation
under the structural backend rule. Forbidding all BDD Note edges or removing structural endpoint validation is forbidden.

## Guards, Live Proof, and Rollback

S06 must not alter logical schema IDs, generic prompt identities, public results, provenance, semantic review, readiness,
host/MCP/local/browser behavior, layout, persistence, or caching. Repair remains enabled. Focused failing-before/passing-
after proof, existing provider-free suites, full backend/frontend gates, and an independent implementation audit are
required.

S05 authorizes no live call. After audited/committed S06 and path-length proof, S07 still needs new explicit user
authorization and fresh short identities. Retention requires first generation validity with no `generation_repair` role
and every existing meaning, provenance, review, compatibility, recovery, and browser gate. Rollback reverts only the S06
projection/validator/test/design correction and retains all diagnosis/live evidence.

## Audit State

The authoring agent's mechanical source, witness, digest, scope, and focused-test checks pass. Independent read-only review
verified every required root, boundary, witness, alternative, affected-file, regression, digest, accounting, and gate claim
and passed with zero critical/high/medium finding. `root-decision.json` binds reviewer `independent-read-only-agent-fe804acb`.
S06 remains intentionally unstarted pending user review.
