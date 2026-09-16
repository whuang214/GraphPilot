# Slice 05: Pre-Layout Repair Pipeline

## Purpose

Split semantic preparation from layout and implement one explicit, bounded, mode-specific deterministic repair pipeline so only a strict, normalized, graph-valid, provenance-valid logical candidate reaches layout and no invalid meaning is silently coerced, reversed, dropped, or rerolled.

## Background

The current shared generation pipeline conforms a broad logical response by sanitizing IDs, applying defaults, dropping invalid structured fields/elements, and normalizing relationship data before layout and canonical validation. That behavior can hide model defects or change meaning without an explicit repair record. The redesigned strict schemas prevent wrong shape/vocabulary; this slice adds deterministic checks that strict JSON Schema cannot express and routes repairable defects through an exact repair packet and provider call.

This slice remains below semantic quality review. Slice 06 will evaluate the accepted normalized candidate against user/context authority before layout, add semantic repair, and activate reviewed-by-default behavior. Slice 05 creates the pre-layout seam that Slice 06 consumes.

## Design

### Dependencies and canonical owners

- Slices 01–04 are required: observer/errors/contracts, request authority, strict packet/logical/repair schemas and prompts, and exact production example sets.
- `docs/02-design-and-features/04-generation-design.md` owns phase order, deterministic repair, failure, and no-write behavior.
- `docs/02-design-and-features/02-validation-design.md` owns the distinction among strict response validation, generation-only deterministic graph/provenance checks, canonical diagram validation, and later semantic review.
- `docs/02-design-and-features/08-context-backed-generation/05-generation-and-provenance.md` owns context allowlists/origins. `docs/01-architecture/01-backend-architecture.md` owns orchestrator/component boundaries and observer/error direction.

### Phase boundary

Refactor the internal pipeline into an explicit pre-layout phase and a downstream layout/canonical phase:

```text
strict decoded response
→ exact mode/type schema validation
→ representation-preserving normalization
→ deterministic graph checks
→ context provenance checks (context only)
→ explicit bounded repair when issues exist
→ accepted pre-layout candidate
→ [Slice 06 semantic review seam]
→ layout → canonical assembly/validation → persistence/render
```

Normalization may deep-copy, canonicalize nullable/empty representation, and produce deterministic ordering/digests only where the promoted contract defines those operations as meaning-preserving. It must not sanitize/rename IDs, substitute semantic types/default elements, reverse an edge, retarget an endpoint, drop a node/edge/field, repair multiplicity, invent containment/guards/origins, or add authority. Any such defect becomes an ordered issue.

The accepted pre-layout value is frozen and carries exact mode/type, generation-input digest, candidate digest, normalized nodes/edges, deterministic issue state, repair rounds used, and safe observer identity. It has no positions, sizes, canonical metadata, persisted path, or render output.

### Deterministic checks and issues

After exact schema validation, deterministic code checks at least:

- unique node/edge IDs, endpoint membership, parent membership, containment role/cycles, and bounded graph connectivity;
- Activity initial/final requirements, reachability, decision guards/targets, merge/fork/join degrees, and exclusion of comment links from control flow;
- Use Case actor/use-case endpoints, subject containment, include/extend/generalization direction, extend condition, and extension-location membership;
- BDD feature cross-fields, finite values, multiplicity order, relationship-end fields, and composition/generalization/dependency direction;
- context origin presence, unique and allowlisted exact claim/assumption/schema refs, at least one grounding source, smallest permitted schema-rule use, and no schema-only domain meaning; and
- deterministic structural critic findings that generation treats as hard acceptance conditions even when ordinary save validation reports them as advisory.

Issues have stable code/path/element identity, bounded safe message/details, deterministic canonical order, and maximum 256 per array. Schema/parse failures that never form the exact strict logical contract return `generation_response_invalid`; they are not disguised as graph repair.

### Explicit repair loop

A direct repair packet contains exact `schemaVersion`, `kind`, original generation-input digest, unchanged direct authority, exact previous logical candidate, ordered validation issues, ordered structural issues, repair round, and versions. Context adds ordered provenance issues and unchanged allowlists. Repair packets contain no few-shot examples, source/evidence records, raw readiness output, semantic findings/actions, layout, canonical JSON, or new authority.

The repair call uses the Slice 03 mode-specific deterministic-repair prompt and the same exact mode/type strict logical response schema as initial generation. The configured budget defaults to one round and accepts only `0..2`; invalid configuration fails at startup/construction rather than clamping. Round values are `1..2`. After each repair response, rerun exact schema, normalization, graph, structural, and context provenance checks from the beginning.

A repair response with the same canonical candidate digest and remaining issues terminates immediately; it is not called again merely because budget remains. No automatic retry/reroll occurs for a valid but unchanged bad candidate. This deterministic stage does not rank subjective semantic quality: a changed candidate passes only if complete revalidation resolves every deterministic issue without introducing another. Any schema/graph-valid but authority-poor or semantically degraded candidate proceeds unchanged to Slice 06, whose independent semantic review must warn, repair, or block it before layout. Provider failures retain the Slice 03 provider code. After budget:

- residual direct graph/structural defects return non-retryable `generation_validation_failed`;
- residual context provenance defects take deterministic precedence as non-retryable `generation_provenance_failed`; otherwise residual context graph/structural defects return `generation_validation_failed`; and
- every failure writes no canonical diagram, SVG, trace, or request mutation and leaves any existing target unchanged.

### Observer, public, and rollback boundaries

Emit Slice 01 observer events for every reached stage, provider call, raw/normalized/repaired candidate, accepted pre-layout result, and terminal failure. Events preserve canonical order/digests/call counts and bounded issue summaries. The default no-op remains side-effect-free; tests use a recording observer. Generation still imports no diagnostics or evaluation implementation.

This slice does not add the Slice 06 semantic-review result/blocked transport or the Slice 09 public tools. Existing MCP names, arguments, and result envelopes remain unchanged. Internal acceptance may now expose an existing typed generation failure instead of silently mutating semantics, but no new public contract is registered.

Rollback is an ordinary revert of Slice 05 only, retaining Slices 01–04. Tests use fake clients and temporary workspaces. Because no failed candidate is persisted and no new public artifact format is activated here, rollback requires no request/diagram migration or user-file deletion.

## Plan Audit

The plan audit must verify:

- **Dependencies:** S01 observer/error contracts, S02 authority loading, S03 strict schemas/prompts/client, and S04 exact examples are hard prerequisites.
- **Phase order:** graph/provenance acceptance occurs before layout; the S06 semantic-review insertion point is explicit and canonical validation/persistence remains downstream.
- **Mutation boundary:** only representation-preserving normalization is allowed; ID/type/direction/endpoint/field/element/guard/multiplicity/origin changes cannot happen silently.
- **Issue completeness:** direct and all three type topologies plus context provenance/allowlists have stable bounded codes, paths, identities, order, and tests.
- **Repair contract:** unchanged authority and previous candidate are present, examples/semantic findings/layout are absent, round/version/input digest are exact, and the same per-type strict schema validates output.
- **Budget/calls:** default one, allowed `0..2`, no clamping, exact call counts, full revalidation, unchanged-digest early stop, and no blind reroll are covered.
- **Failures:** strict-response invalid, provider failure, direct/context validation exhaustion, and context provenance exhaustion have deterministic precedence/codes/retryability and write nothing.
- **Observer direction:** events cover every reached stage and terminal result without evaluation/diagnostics imports, secret/source leakage, or no-op side effects.
- **Public boundary:** no quality-mode/review/trace/debug/public-MCP/frontend change is pulled forward.
- **Reversibility:** reverting S05 leaves S01–S04 contracts/fixtures intact and requires no local artifact deletion.
- **Verification:** add failing fake-client/recording-observer and graph/provenance tests first, then require the complete offline backend suite, current MCP characterization, stale silent-conformer searches, and `git diff --check`.

Plan audit result: **Pass after correction.** The audit confirmed no silent semantic mutation, complete deterministic/type/provenance checks, bounded exact repair calls, issue/failure precedence, no blind reroll, and explicit routing of schema-valid semantic degradation to Slice 06 review before layout.

## Included Work

- Split the generation pipeline into a frozen accepted pre-layout candidate stage and downstream layout/canonical continuation.
- Replace silent meaning-changing conformance with exact schema validation, representation-preserving normalization, and stable deterministic issues.
- Implement direct/context graph and structural checks for IDs, endpoints, containment, topology, direction, guards, multiplicities, fields, reachability, and critic findings.
- Compose context provenance validation for allowlisted origins and schema-rule constraints before layout.
- Build exact direct/context deterministic-repair packets from unchanged authority, previous candidate, ordered issues, round, digest, and versions with no examples.
- Execute at most the strictly configured `0..2` repair rounds through the Slice 03 strict fake/provider seam and exact mode/type response schema.
- Revalidate every repaired candidate from the strict-schema boundary and stop immediately on unchanged invalid output.
- Return exact response/provider/validation/provenance failures and guarantee no canonical write on rejection/exhaustion.
- Wire Slice 01 stage/provider/candidate/result events with a no-op default and recording-observer tests.
- Add characterization tests for current successful persistence/render behavior after an accepted candidate and for unchanged MCP surface contracts.
- Update promoted generation/validation/provenance/backend owners only for implementation-backed corrections.

## Not In Scope

- Semantic candidate rubrics, reviewer calls, semantic findings/actions, semantic repair, reviewed/standard quality mode, or blocker result transport; those are Slice 06.
- Trace-sidecar or diagnostics persistence; observers only report bounded events here.
- PyGraphviz integration/cutover, layout tuning, frontend/canvas/SVG parity work, or old-engine removal.
- Public `diagram_generation_workflow`, `diagram_request_save`, `diagram_generate_direct`, result-schema cutover, or old MCP removal.
- Changing request authority, adding assumptions/claims, rerunning readiness, best-of-N generation, or force-saving a blocker.
- Live Azure calls, hidden-gold work, `.env` changes, production promotion, or push.

## Target Areas

- `backend/services/generation/pipeline/generation_pipeline.py` and focused pre-layout validation/repair components under `backend/services/generation/`
- `backend/services/generation/prompt_diagram_generation_service.py`
- `backend/services/generation/context_diagram_generation_service.py`
- `backend/services/generation/review/context_provenance_validator.py`
- `backend/services/diagrams/validation/structural_constraints.py` and `diagram_validation_service.py` as canonical rule consumers, without merging trust boundaries
- Slice 01 observer/contracts/operation registry and Slice 03 repair schemas/prompts/strict client as consumers
- `backend/tests/generation/test_generation_service.py`, `test_context_generation_service.py`, `test_structural_constraints.py`, focused pre-layout/repair/observer tests, and current MCP characterization tests
- `docs/01-architecture/01-backend-architecture.md`, `docs/02-design-and-features/02-validation-design.md`, `04-generation-design.md`, and `08-context-backed-generation/05-generation-and-provenance.md` only for implementation-backed corrections
- this slice document and the live current-state board for implementation outcome/status only

## Exit Criteria

- A strict valid logical response reaches a frozen accepted pre-layout candidate with no position/canonical/persistence fields; no layout call occurs before acceptance.
- Tests prove invalid/duplicate IDs, dangling endpoints/parents, containment, Activity decision/fork/join/reachability, Use Case include/extend/generalization, BDD multiplicity/direction/fields, structural critic, and context origin/allowlist/schema-rule defects are explicit and deterministically ordered.
- No test path silently sanitizes an ID, substitutes a semantic type, reverses/retargets an edge, drops an element/field, repairs a multiplicity/guard, or invents an origin.
- Repair packets contain unchanged authority, exact prior candidate/input digest/issues/round/versions and zero examples, semantic findings, source records, layout, or canonical data.
- Budget tests cover `0`, default `1`, and maximum `2`; invalid values fail, each repaired candidate is fully revalidated, and unchanged invalid output cannot trigger another reroll.
- Fake tests prove exact initial/repair call counts and schema identities for success, provider error, invalid response, repair success, direct exhaustion, context validation exhaustion, and provenance exhaustion.
- Residual failures use exact code/retryability/precedence and leave canonical diagram, SVG, trace/debug, request, and any prior target unchanged.
- Recording-observer tests prove ordered stage/provider/candidate/result events for success and each failure, bounded safe payloads, and no generation import of diagnostics/evaluation; no-op remains side-effect-free.
- Current MCP names/arguments/result envelopes remain characterized and unchanged; no Slice 06 or Slice 09 surface is discoverable.
- Focused generation/context/provenance/structural/observer tests and `cd backend; uv run python manage.py test` pass fully offline.
- Stale silent-conformer/coercion searches, `git diff --check`, and implementation audit pass with no unresolved finding; no frontend, live provider, `.env`, hidden gold, or user artifact is used.

## Previous Slice

- [`04-training-fixtures.md`](04-training-fixtures.md)

## Next Slice

- [`06-semantic-review-and-diagnostics.md`](06-semantic-review-and-diagnostics.md)

## Outcome

**Completion:** Added a strict internal pre-layout generation path that preserves the exact decoded logical candidate,
revalidates its mode/type schema, and emits deterministic common/connectivity, Activity, Use Case, BDD feature/end/
direction/multiplicity, and context provenance issues without coercing IDs, types, directions, endpoints, fields,
elements, guards, multiplicities, or origins. Added bounded direct/context repair packets with unchanged authority, exact
prior candidate/issues/round/versions, no examples, full revalidation, observer events, default one/allowed zero-to-two
rounds, and unchanged-digest early termination.

**Deviations:** Schema-valid but semantically poor candidates intentionally pass this deterministic stage unchanged for
Slice 06's authority-aware semantic review. Current public generation remains on its compatibility pipeline until Slice
09; the new path performs no layout, persistence, rendering, or public registration.

**Verification:** Added failing-first all-six fixture-backed tests for no mutation, duplicate/endpoint/parent/connectivity,
complete Activity/Use Case/BDD rule matrices, nonfinite data, provenance allowlists/schema scaffolding, repair packet
separation, context provenance repair, default/zero/maximum budgets, two-round and unchanged stop behavior, provider/
response failures, failure precedence, and ordered observer events. Two implementation-audit passes resolved the initial
BDD/test-coverage findings. All 750 provider-free backend tests passed (4 skipped), with Python compilation and
`git diff --check` clean.

**Follow-up:** Slice 06 inserts reviewed-default semantic review/repair at the accepted-candidate seam before any layout
or canonical write.
