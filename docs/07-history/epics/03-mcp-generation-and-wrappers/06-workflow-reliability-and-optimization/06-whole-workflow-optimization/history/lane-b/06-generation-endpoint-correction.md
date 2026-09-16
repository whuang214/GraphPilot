# Slice 06: Generation Endpoint Correction

## Purpose

Implement only the S05 generation endpoint-contract correction and prove it offline without changing semantic review, host integration, readiness, or other optimization owners.

## Execution Contract

- **Depends on / inputs:** committed audited S05 root and exact named regressions.
- **Outputs:** failing-before evidence, narrow current-V1 correction, passing checks/audit, S06 Outcome and commit.
- **Exclusive write ownership:** exact production/test/design files named by S05 plus S06 Outcome.
- **Forbidden/shared ownership:** validator weakening, semantic-review/host work, live identities/provider, group/current-state/decision/ledger/backlog reserved for S08, `.env`, S15/Stage C.
- **Parallelism/resources:** none; temporary test workspaces only, no ports/browser/provider.
- **Cancellation:** broader root/contract boundary, dependency, weakened gate, or material audit/check failure returns to S05.

## Included Work

- Add exact failing-before provider-projection/full-schema/backend endpoint regressions and a corrected first response.
- Change only the owner selected by S05; private current-contract changes are V1 in place unless diagnosis proves a persisted/public version boundary.
- Preserve deterministic endpoint/direction validation, explicit generation repair, provenance, reviewed semantic quality, and final review.
- Prove the Block 5 repaired candidate and all current fixtures remain accepted.
- Run independent implementation audit, focused generation/readiness/live-harness/frozen-history tests, full backend/frontend gates, compatibility/security/diff checks.
- Commit before any S07 manifest exists.

## Not In Scope

Semantic-review rework; host/interface work; packet/cache/MCP/local/browser optimization; provider calls; validator weakening; calibration/certification/promotion; S15/Stage C.

## Target Areas

Exact files named by S05, focused generation contract tests, canonical generation/backend docs, and this Outcome.

## Exit Criteria

- Exact regressions fail before and pass after correction.
- Provider-visible and backend endpoint contracts are coherent without weakening validation.
- Independent audit has no critical/high/medium finding.
- Required full checks pass and one coherent implementation commit exists.
- No live manifest/identity/provider call is created.

## Previous Slice

[`05-generation-endpoint-diagnosis.md`](05-generation-endpoint-diagnosis.md)

## Next Slice

[`07-generation-endpoint-proof.md`](07-generation-endpoint-proof.md) only after committed S06, the harness path prerequisite, and a new explicit live authorization.

## Outcome

**Status:** Complete · provider-free correction, independent audit, and full backend/frontend verification PASS; S07 live proof next.

**Correction:** The private current-V1 BDD `diagramModel` now tells direct/context initial and repair calls that
`association`, `composition`, `generalization`, and `dependency` require two existing Block endpoints, while note
attachments use `commentLink` and do not participate in structural Block-endpoint/connectivity rules. Deterministic
pre-layout validation applies the existing Block-only predicate only to those four structural semantics. It adds no
converse `commentLink` policy, preserves the Block-to-Block compatibility shape, and leaves relationship direction/end
checks plus stable `bdd_relationship_endpoints_invalid` issue ordering and repair authority unchanged. The canonical
[generation design](../../../../../../../03-design/07-generation.md) records the implemented scope.

**Test-first proof:** All four exact S05 regressions failed before production changed (`4` tests, expected `7` subtest
failures and `2` subtest errors in 4.534s) and passed after correction (`4` in 3.745s). Five preserving regressions passed
before and after; they cover eight structural-semantic/mode Note-endpoint rejection cells, four annotation
direction/mode acceptance cells, both Block-to-Block `commentLink` compatibility cells, provider projection plus full
schema before deterministic rejection, exact repair issue/candidate authority, a safe four-node/three-edge Block 5
shape-class control, and all twelve training fixtures. The intentionally unretained raw Block 5 candidate was neither
read nor reconstructed.

**Verification and scope:** With Azure settings blank and no-dotenv live-anchor settings, the changed packet/pre-layout
modules passed `37`; the S05 strict-schema/generation/repair/review/live-harness guard set passed `105`; broader
provider-free generation passed `202`; and readiness plus frozen-history ran `110` with one skip. Machine/human evidence
and exact commands/results are in
[`evidence/generation-endpoint-wave/provider-free-correction.md`](../../lane-b/evidence/generation-endpoint-wave/provider-free-correction.md)
(machine self-digest `sha256:bd00b7a6993e197e8be2261bf1bac78030dd4e0e2d63aeb2a3c4f21453f80a35`). Writes stay
inside the S05/S06 allowlist; provider calls, live identities, prompt/schema/registry/MCP/semantic-review/readiness/host/
Lane A/B0/shared-owner files, `.env`, calibration, certification, promotion, deployment, and push remain zero or unchanged.
Independent implementation audit passed with zero critical/high/medium finding; full backend passed 1,069 tests with 5
skipped, frontend lint/build/419 unit/43 E2E passed, and no S07 performance or live-quality claim is made.
