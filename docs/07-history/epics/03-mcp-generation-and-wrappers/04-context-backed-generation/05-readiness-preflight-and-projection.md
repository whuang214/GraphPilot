# Slice 05: Readiness Preflight and Projection

## Purpose

Implement deterministic readiness Layer 1 and construct the bounded, complete reviewer projection used by the
semantic review layers.

## Background

Slices `02`–`04` provide exact rubrics, context schemas, canonical persistence, and digests. Invalid context
must be rejected before any reviewer call.

## Design

This slice creates `services/readiness/`, moves the already implemented rubric/policy modules into it, and adds
`ContextReadinessService`. Its `prepare(request_path)` phase composes `ContextPersistenceService`, selects the
exact rubric, returns a typed/sorted Layer 1 result, and builds a projection only when preflight is valid. Slice
`06` adds `assess()` and the reviewer/final-result assembly around this phase; no reviewer dependency or semantic
rating lands here.

Layer 1 reuses persisted-document validation and adds only readiness-owned closure, disposition, forbidden-content,
allowlist, and projection-budget checks. Valid input is projected into exact selected details, the complete compact
v1-selectable active-claim index, open uncertainties, packet intent, rubric, and allowlists without mutating either
canonical document.

## Plan Audit

- **Package cutover:** move `ReadinessRubricService` and `ReadinessPolicyService` to
  `services/readiness/{readiness_rubric_service,readiness_policy_service}.py` and move their tests to
  `tests/readiness/`; update every import/navigation owner atomically with no compatibility module.
- **Typed phase boundary:** extend readiness contracts with immutable preflight issue/result, exact claim-ref,
  closure requirement, projection contributor/budget, projection, and prepared-context DTOs. `prepare()` returns
  invalid identified input without a projection, valid input with one projection, and raises typed load,
  reconciliation, identity, or `ContextTooLargeError` operation failures rather than conflating them with status.
- **Validation reuse:** canonical bound loads remain owned by `ContextPersistenceService`. Its validation failures
  carry safe path/document metadata so readiness can return `invalid` only when request ID, request digest,
  manifest digest, concrete type, and rubric can be identified; unparseable/missing/unsafe/stale input remains an
  operation failure.
- **Layer 1 additions:** direct nonrecursive payload closure covers only relationship source/target, property owner,
  and constraint subject refs. Missing selectable refs become sorted closure requirements for Layer 4's
  `selection_closure_missing` action; historical/inactive/non-current exact refs are invalid. A `block` disposition
  is valid input recorded for Layer 4's non-overrideable `uncertainty_disposition_blocks` finding. Any `exclude`
  requires nonempty excluded
  scope, while semantic correspondence remains Layer 3 because v1 has no machine link between those prose fields.
- **Projection:** selected details follow JSON 2 order and include exact version/payload/support, selection role/reason,
  directly cited bounded evidence summaries, and directly related uncertainties. The active index contains every
  active/current `as_implemented` claim sorted by ID/version with closed per-kind structured `keyFacts`; open
  uncertainties are sorted by ID; packet arrays retain order; rubric and sorted allowlists are exact. Raw source,
  locators, content digests, historical versions, and whole manifest bodies are excluded.
- **Safety and budget:** scan projected prose only for the high-confidence secret/private-key markers specified by
  the readiness owner and report no matched value. Estimate a conservative token upper bound as compact canonical
  UTF-8 bytes. The net deployment input limit (after Slice 06's prompt/response reserves) is constructor-injected,
  must be positive, and applies to the complete projection. V1 never filters, retrieves, truncates, or chunks: oversize raises `ContextTooLargeError`
  with phase `readiness_projection`, estimate, limit, the top ten contributors, and fixed actions to narrow scope,
  remove irrelevant selections, split the request into diagrams, or select a larger configured deployment.
- **Determinism:** issues sort by path/code/message; refs and allowlists use `(id, version)` order; contributors sort
  by descending estimate then stable path; projection digest uses the existing canonical helper. Repeated builds
  over unchanged loaded documents must compare equal byte-for-byte.

## Included Work

- Move `ReadinessRubricService`, `ReadinessPolicyService`, and their tests into `services/readiness/` without behavior changes; update imports and service navigation atomically.
- Load canonical JSON 2 and its manifest by safe path.
- Validate digests, versions, references, dispositions, assumptions, decisions, and size bounds.
- Produce deterministic typed `invalid` preflight issues without an LLM call and record closure/blocker inputs for
  Slice 06's final result assembly.
- Build the complete bounded reviewer input, canonical projection digest, allowlists, and contributor/token estimates.
- Add fixtures for stale, missing, malformed, unsafe, forbidden, closure-incomplete, oversized, and valid inputs.

## Not In Scope

- Calling an LLM or assigning facet ratings.
- Deterministic Layer 4 assembly beyond the policy already delivered in slice `02`.
- MCP registration or generation.

## Target Areas

- `backend/services/readiness/`
- `backend/services/`
- `backend/tests/readiness/`
- context schema/persistence seams from slices `03`–`04`

## Exit Criteria

- The preparation phase has no reviewer dependency; Slice 06 must invoke its reviewer only for `valid` preparation.
- Valid projections are deterministic, complete, bounded, and include all contract-required details.
- Oversized input fails explicitly without filtering, retrieval, truncation, or chunking.
- Targeted and full backend tests pass offline.

## Previous Slice

- [`04-context-persistence.md`](04-context-persistence.md)

## Next Slice

- [`06-semantic-reviewer.md`](06-semantic-reviewer.md)

## Outcome

**Completed.**

- **Implementation:** created `services/readiness/`, moved rubric/policy services and tests without behavior change,
  and added immutable preflight/projection contracts plus `ContextReadinessService.prepare()`. Preparation composes
  canonical bound loads, returns sorted safe-invalid issues, detects direct selection closure and explicit blocking
  dispositions, rejects structurally incoherent exclusions and high-confidence secret markers, and emits the exact
  deterministic reviewer projection/allowlists/digest/budget without mutating JSON 1 or JSON 2. Complete oversize
  input raises typed `ContextTooLargeError` with stable bounded diagnostics and no silent reduction.
- **Verification:** all 33 focused readiness/contract tests and all 515 backend tests pass offline. Coverage includes package moves,
  rubric/policy characterization, valid deterministic projection, direct closure, unselectable closure, block and
  exclude dispositions, forbidden content, missing/unsafe/stale inputs, safe identifiable invalidity, identity
  failure, conservative budget diagnostics, and unchanged-input equality.
- **Deviations:** scenario variants reuse and mutate the canonical Slice 03 fixtures in temporary workspaces rather
  than duplicating near-identical fixture files. `ContextValidationError` gained safe document/path metadata so
  readiness can distinguish an identified `invalid` result from a load/identity operation error; no transport or
  persistence behavior changed.
- **Follow-up:** Slice 06 adds the shared LLM package move, private reviewer schema/prompt, semantic call/repair path,
  deterministic Layer 4 validation, and final readiness result assembly around `prepare()`.
