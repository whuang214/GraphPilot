# Semantic Review Root Decision

- Machine authority: [`root-decision.json`](root-decision.json)
- Provider-free proof: [`provider-free-proof.md`](provider-free-proof.md)
- Recommendation: `focused_implementation_correction`
- Owner: `semantic_review_prompt_projection_schema_validator_contract`
- Confidence: high in owner; bounded/unknown original trigger variant
- Azure calls: **0**

## Decision

Proceed to S02 with one focused provider-visible finding-contract correction. The semantic-review input must expose the exact existing per-facet finding-code allowlist, and both initial and response-repair prompts must state that each finding stays in its containing facet, uses a code allowed for that facet, and appears only for an applicable rating below `minimumRating`.

Backend validation, response repair, rubric authority, scoring, status, and semantic repair remain fail-closed and unchanged.

## Decisive Evidence

1. Block 5 safely recorded `finding_invalid @ $` followed by a 37,787.5872 ms response-repair call; no raw response was retained or accessed.
2. Provider strict schema and full response schema expose only one global finding-code enum.
3. Review inputs do not expose the backend's `FACET_FINDING_CODES` mapping.
4. Prompts say “allowlisted findings” without supplying that allowlist or the complete finding conditionals.
5. Three bounded shapes pass provider projection and full response schema but trigger the exact runtime signature.
6. The facet/code witness reproduces in every direct/context × diagram-type cell.
7. A smallest corrected witness passes without response repair.

The original private variant cannot be distinguished from safe evidence and is not claimed. This does not prevent owner selection: every bounded variant is permitted by the provider-visible semantic-review finding contract and rejected only by the semantic-review backend validator.

## S02 Boundary

- Add an exact provider-visible per-facet code allowlist derived from the existing registry to both private review inputs.
- Make initial/repair prompt rules exact.
- Bump changed prompt identities and preserve old prompt assets.
- Use the established additive private-v1 projection policy; do not alter public/result contracts or rubric meaning.
- Add exact failing-before and passing-after regressions across all six cells, with dedicated initial- and repair-prompt assertions that findings are allowed only when an applicable rating is below `minimumRating`.
- Preserve the fallback response-repair path and every validator rule.

## Alternatives

- **Strongest:** facet-specific response-schema branches. Deferred because it duplicates the facet catalog and still cannot express dynamic input-reference allowlists or all backend rules under Azure's supported subset.
- **Keep generic repair:** rejected because it retains the measured extra call and leaves the first response under-specified.
- **Weaken validation:** forbidden.
- **More provider evidence first:** unnecessary for owner selection and unable to recover the intentionally absent raw response.

## Live Proof and Rollback

After audited/committed S02, exactly one new-identity cold-room candidate may run under the authorized max-nine sequential schedule. Retention requires no semantic-review response-repair call and every existing quality/provenance/compatibility/browser gate. Generation's endpoint repair remains the unchanged control.

Rollback reverts only S02's correction commit. S01 and all terminal evidence remain immutable.

## Audit

Independent read-only audit confirmed the safe-evidence boundary, all three projected/full-schema-valid witnesses, six-cell reproduction, corrected witness, unique owner, narrow/version-safe rollback, generation control, and accounting. It raised one medium documentation ambiguity: the regression list did not explicitly name below-minimum coverage. Dedicated initial- and response-repair prompt tests were added to the plan; focused re-audit passed with zero critical, high, or medium finding.
