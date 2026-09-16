# Slice 02: Semantic Review Correction

## Purpose

Implement and prove the narrow semantic-review contract correction selected by S01, without weakening backend validation or changing any other optimization lane.

## Included Work

- Add failing-before regressions for the exact provider-projection/backend-validator witness and a corrected first response.
- Change only the audited semantic-review prompt/projection/schema/validator contract owner.
- Preserve strict finding validation, final review authority, required/forbidden meaning, provenance, and response-repair fallback.
- Prove the Block 5 repaired response and current fixtures remain accepted.
- Run independent implementation audit, focused generation/readiness/live-harness tests, full backend, compatibility, security, and diff checks.
- Commit the correction before any S03 manifest exists.

## Not In Scope

Generation endpoint correction; host-interface work; packet/cache/effort/MCP/local/browser optimization; provider calls; anchor output edits; validator weakening; calibration/certification/promotion; S15/Stage C.

## Target Areas

Exact files named by S01's root decision, neighboring contract tests, and this Outcome.

## Exit Criteria

- Regressions fail before and pass after the correction.
- Provider projection and backend validator express one coherent first-response contract.
- Independent audit has no unresolved critical/high/medium finding.
- Full required checks pass and a coherent implementation commit exists.
- No live manifest, identity, or provider call is created.

## Previous Slice

[`01-semantic-review-diagnosis.md`](01-semantic-review-diagnosis.md)

## Next Slice

[`03-semantic-review-proof.md`](03-semantic-review-proof.md) after committed S02 and dedicated authorization freeze.

## Outcome

**Status:** Complete · independently audited and fully verified; ready for S03 after this commit.

**Failing-before proof:** The exact nine-test gate produced 16 expected errors before implementation: missing `findingCodesByFacet` across all six cells, absent V2 prompt assets, and absent V2 registry identities. The three provider-projection/full-schema witnesses and corrected witness remained passing characterizations. After correction, the clean 32-test semantic-review/prompt/identity/trace gate passed.

**Implementation:** Both direct/context private review inputs now project the existing `FACET_FINDING_CODES` registry in rubric order as `allowlists.findingCodesByFacet`. New immutable V2 review and response-repair prompts make containing-facet equality, per-facet code membership, and applicable-below-minimum ownership explicit; production and compact traces select V2. Input/repair/trace V1 schemas additively accept V2 identities while preserving old V1 packets, prompt files, and frozen historical registry keys. Backend finding/reference/action validation, one response-repair fallback, rubric/scoring/status, semantic candidate repair, generation endpoints, readiness, provenance, persistence, MCP/public results, host, local, and browser behavior are unchanged.

**Disposition:** S04 reverted the correction after the one authorized S03 candidate failed pre-dispatch and could not satisfy retention. No semantic-review behavior, prompt, schema, trace, test, or canonical-design change from S02 remains in production; S01/S03 evidence and authorization remain immutable. Future rework, if separately authorized, updates the current private V1 in place rather than preserving this unpromoted V2 layer.

**Audit and verification:** Independent implementation audit initially missed the two dedicated below-minimum tests in their correct prompt-test module; focused re-audit confirmed both exact names and all four direct/context initial/repair assertions, then passed with zero critical/high/medium finding. S03 pre-dispatch review later exposed one real high schema-completeness gap: V2 packets emitted the map but the additive V1 schema did not require it. A new regression failed for both modes, then passed after prompt-version-conditional requirements preserved frozen V1 compatibility; the stale `-02` manifest made zero calls and must never dispatch. The follow-up audit passed with zero material finding, 81 focused tests passed, and the full backend passed 1,056 tests with 5 skipped. Focused implementation suites passed 121 + 32 compatibility tests and a clean 32-test gate. The initial full backend passed 1,055 tests with 5 skipped; Django check, compileall, 13-tool/one-prompt stdio smoke, schema/meta/projection/trace tests, frozen full-effort compatibility, workflow-audit/live-harness tests, `git diff --check`, and secret scan passed. Frontend verify passed lint/build, 419 tests, and 43 Chromium E2E. No provider call, `.env` value exposure, raw response, S15 identity/Stage C, calibration, certification, promotion, deployment, or push occurred; controlled/aggregate accounting remains 10/1000 and 11/1000.
