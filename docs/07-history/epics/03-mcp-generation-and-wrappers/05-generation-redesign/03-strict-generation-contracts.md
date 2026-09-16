# Slice 03: Strict Generation Contracts

## Purpose

Implement the exact internal direct/context model packets, six mode/type logical-response contracts, canonical JSON messages, versioned generation/repair prompts, strict-provider behavior, and local transport ceilings needed by the redesigned pipeline without exposing the redesigned MCP surface yet.

## Background

The current direct path sends a large rendered Markdown user message and a broad logical schema; the context path derives another broad schema and currently reuses direct examples. The shared Azure client may retry with `json_object` when strict schema output is rejected. The redesign replaces those mechanics with one role-specific system message, one canonical JSON user message, and one exact strict out-of-band response schema for each call. There is no backend natural-language normalization call and no hidden strict-output fallback.

Slice 01 establishes exact identities/registry artifacts; Slice 02 supplies validated request loading. This slice wires model-facing builders and clients to those contracts. Slice 04 will supply the twelve production fixtures, so this slice uses injected validated synthetic example pairs to prove exact-two selection without inventing, silently falling back to, or activating an incomplete production set.

## Design

### Dependencies and authority

- Slices 01 and 02 must be complete and green. The new packet builders consume canonical validated requests and Slice 01's immutable schema/prompt/profile/set IDs.
- `docs/02-design-and-features/04-generation-design.md` owns packet shape, prompt behavior, strict logical fields, provider failures, and fixed byte ceilings.
- `docs/01-architecture/01-backend-architecture.md` owns the shared LLM seam and dependency direction; `docs/03-development-and-delivery/00-development-environment.md` owns the one chat deployment and environment behavior.
- `docs/02-design-and-features/08-context-backed-generation/05-generation-and-provenance.md` owns context projection/allowlists. Public MCP names and results remain owned by `docs/01-architecture/03-mcp-tools/` and are unchanged here.

### Parallel packets with distinct authority

Both packet builders use canonical UTF-8 JSON with sorted keys and no insignificant whitespace. They share this section order only where meaning overlaps:

```text
contract identity
request/output identity
request and scope
mode-specific authority
assumptions and decisions
diagram model
mode-specific constraints
exactly two ordered examples
versions
```

`graphpilot.direct.generation-input.v1` contains request ID, immutable diagram name/type, direct request/scope, mandatory requirements, accepted assumptions/decisions, exact diagram model, two direct examples, and exact versions. It carries no claims, source, evidence, provenance allowlists, readiness data, or origins.

`graphpilot.context.generation-input.v1` contains request ID, immutable diagram name/type, request/scope, uncertainty dispositions, selected exact claim meaning, accepted assumptions/decisions, exact diagram model, context provenance allowlists, two context-native examples, and exact versions. It excludes raw source, absolute paths, full manifests, evidence records/summaries, unselected claims, and raw readiness output.

`diagramModel` records exact ordered core node/edge vocabulary, semantic guidance, structural rules, and semantic-profile version. `versions` records exact prompt, per-mode/per-type logical schema, semantic profile, training-set version, and set digest. The complete packet and its canonical byte length/digest are observable; authority and examples are never truncated, dropped, reordered, or substituted.

### Six strict logical schemas

Use one strict schema per mode/type:

```text
graphpilot.direct.logical-diagram.activity.v1
graphpilot.direct.logical-diagram.use-case.v1
graphpilot.direct.logical-diagram.bdd.v1
graphpilot.context.logical-diagram.activity.v1
graphpilot.context.logical-diagram.use-case.v1
graphpilot.context.logical-diagram.bdd.v1
```

Every response contains only `schemaVersion`, `kind`, `nodes`, and `edges`; it omits diagram name/type, positions, dimensions, style, metadata, and layout. All Azure properties are required; nullable values and bounded empty arrays represent semantic absence.

- Activity admits only the eight promoted core node identities and `controlFlow|commentLink`, with exact labels, `joinSpec`, guards, and weights.
- Use case admits only actor/useCase/subject/note and association/generalization/include/extend/commentLink, with exact parent, extension-point, condition, and extension-location fields.
- BDD admits only block/note and association/composition/generalization/dependency/commentLink, with exact features, multiplicities, operations, constraints, and relationship-end fields.
- Direct schemas reject `origin`. Context schemas require one origin on every node/edge with bounded claim, assumption, schema-rule, and rationale fields.
- Bounds are nodes `1..256`, edges `0..512`, IDs max 128, labels max 256, use-case extension points max 32, BDD feature arrays max 64 each, and context origin refs max 16 claims/8 assumptions/8 schema rules.

Graph-level uniqueness, endpoint membership, containment, topology, and provenance-reference meaning remain deterministic post-response checks for Slice 05; schema limitations are never compensated for by silent coercion.

### Prompts and strict provider seam

Add exact versioned direct/context generation and deterministic-repair prompt assets from the promoted owner. Each backend call has exactly two messages (one system, one canonical JSON user) and one strict `json_schema` response format. Prompts prohibit prose/code fences/hidden reasoning, keep output identity host-owned, and distinguish conceptual inference from repository authority. Repair prompts exist and are snapshot-tested here; Slice 05 owns invoking them.

The redesigned strict client performs one provider call for one requested response. A deployment/API rejection of strict output returns non-retryable `structured_output_unsupported`; it never issues a `json_object` fallback call. Provider context rejection maps to `llm_context_limit_exceeded`; transient timeout/rate/service failures map to retryable `llm_provider_unavailable`; refusal, malformed/invalid response, missing configuration, and local bounds use their exact promoted codes. Changing/removing an unsupported reasoning control must not become a hidden output-format fallback.

Enforce fixed code-owned ceilings on UTF-8 bytes:

```text
complete outbound packet:       16 MiB
raw provider response:           8 MiB
```

These are memory/transport safety limits, not token or model-capacity claims and not environment overrides. Azure owns token capacity. Packet overflow fails before the provider call; response overflow fails before JSON parse. No code calculates cost or guesses tokenizers.

### Public and rollback boundaries

No `diagram_generate_direct`, shared request-save tool, or unified workflow is registered in this slice. Existing MCP names/argument/result envelopes remain unchanged even if their internal service begins using strict packet infrastructure. Slice 09 owns the public cold cutover.

The versioned replacement assets coexist internally with legacy `backend/assets/prompts/generate.md` and `repair.md` only because current public handlers remain on their old path through Slice 09. The redesigned builders never treat those legacy files as fallback assets. Slice 09 removes the two approved legacy files atomically when it switches every public caller; this slice does not create a commit in which current generation lacks its prompt assets or production fixtures.

Rollback is an ordinary revert of Slice 03's new schemas, builders, prompts, and strict client while retaining Slices 01–02 and the legacy public path. It does not touch persisted requests/diagrams, remove a legacy prompt, or require a live provider.

## Plan Audit

The plan audit must verify:

- **Dependencies:** exact identities and internal request loading come from Slices 01–02; production fixture activation remains Slice 04 and deterministic repair execution remains Slice 05.
- **Authority:** direct packets contain no grounding claims/origins and context packets contain no raw source/unselected authority or direct requirements.
- **Schema precision:** all six schemas enforce only current core vocabulary/fields/bounds; direct rejects origins, context requires them, and output identity/layout are absent.
- **Packet determinism:** canonical bytes/digests, section content, exact profile/rule order, exactly two manifest-ordered examples, and full version identities are testable.
- **Fixture sequencing:** S3 contract tests use injected validated synthetic pairs; missing production manifests fail rather than falling back to old examples, and S4 owns activation.
- **Provider behavior:** strict unsupported, response invalid, refusal, context limit, unavailable, and byte-bound cases have exact call counts/codes/retryability; no `json_object` fallback exists on the redesigned path.
- **Safety:** 16 MiB/8 MiB limits use UTF-8 bytes and boundary tests; authority/examples are never truncated or logged with secrets.
- **Prompt ownership:** exact prompt text/version snapshots are single-source; legacy `generate.md`/`repair.md` remain current-path-only and cannot be used by redesigned builders, while Slice 09 owns their approved removal.
- **Public boundary:** no new/renamed MCP registration, no public result change, no layout/semantic-review behavior, no broken interval before S04 fixtures exist, and no frontend change.
- **Reversibility:** one revert removes only new internal prompt/client/schema work without mutating requests, diagrams, `.env`, legacy prompt assets, or user files.
- **Verification:** add failing fake-client/schema/packet/prompt tests first to prove messages/schemas/call counts fully offline; then require focused and complete backend tests, stale prompt/schema/ID searches, and `git diff --check`.

Plan audit result: **Pass.** The audit confirmed six exact mode/type schemas, authority-clean canonical packets, exact-two injected examples, strict-json-schema/no-fallback behavior, fixed byte ceilings, public-surface preservation, and deferred atomic legacy-prompt removal in Slice 09.

## Included Work

- Complete and consume the exact direct/context generation-input and six mode/type logical schemas registered by Slice 01.
- Add canonical direct/context packet builders over validated requests, type profiles, structural rules, allowlists, and an injected example-set loader.
- Add exact packet serialization, byte count, digest, and version capture.
- Add exact direct/context generation and deterministic-repair prompt assets and byte-for-byte snapshot tests.
- Add a strict-only generation call seam with safe provider classification and no output-format fallback.
- Enforce the 16 MiB outbound-packet and 8 MiB raw-response ceilings before call/parse respectively.
- Extend `FakeLLMClient` (or the promoted fake seam) to capture exact messages/schema identity, return bounded raw/decoded responses, and simulate each provider failure without network access.
- Test each schema's allowed/forbidden vocabulary and fields, nullable/empty representation, cross-mode origin rules, lexical bounds, and exact example count/order.
- Prove the redesigned builders never read legacy `generate.md` or `repair.md`; retain those files solely for the unchanged current public path and hand their approved atomic removal to Slice 09.
- Characterize current MCP registrations/results and update promoted canonical owners only for implementation-backed corrections.

## Not In Scope

- Creating the twelve production direct/context training fixtures or their human sign-off.
- Deterministic graph/provenance repair orchestration, semantic review/repair, quality mode, trace/debug writes, or observer stage wiring beyond the Slice 01 protocol.
- Layout, canonical assembly changes, persistence/publication, rendering, or PyGraphviz.
- Registering `diagram_request_save`, `diagram_generate_direct`, or `diagram_generation_workflow`; removing current MCP names/IDs.
- Dynamic example selection, zero-example mode, tokenizers, cost calculation, model-specific token tables, packet truncation, or best-of-N rerolls.
- Live Azure compatibility testing, `.env` access, frontend changes, hidden-gold work, or production promotion.

## Target Areas

- `backend/assets/schemas/direct-generation-input.json`
- `backend/assets/schemas/context-generation-input.json`
- `backend/assets/schemas/{direct,context}-logical-diagram-{activity,use-case,bdd}.json`
- `backend/assets/schemas/direct-generation-repair-input.json` and `context-generation-repair-input.json`
- versioned replacement assets under `backend/assets/prompts/`; legacy `backend/assets/prompts/generate.md` and `repair.md` are characterization-only inputs and remain unmodified for Slice 09 removal
- `backend/services/llm/llm_client.py` and `backend/services/llm/prompt_service.py`
- `backend/services/generation/prompt_diagram_generation_service.py`, `context_diagram_generation_service.py`, and focused packet/profile/example-loader modules under the same package
- `backend/services/diagrams/catalog/diagram_types.py`, `backend/services/diagrams/validation/structural_constraints.py`, and Slice 01 contract/registry values as consumers, not duplicate owners
- `backend/tests/llm/`, `backend/tests/generation/`, exact schema fixtures/snapshots, and current MCP characterization tests
- promoted backend/generation/context/environment/testing owners only for evidence-backed corrections
- this slice document and the live current-state board for implementation outcome/status only

## Exit Criteria

- All six strict schemas meta-validate and accept only their mode/type core fields and bounds; cross-type vocabulary, output identity/layout, direct origins, and ungrounded context shape fail.
- Direct/context packet snapshots are canonical and deterministic, contain exact authority/profile/rules/versions, and require exactly two injected manifest-ordered examples.
- Missing/corrupt/wrong-mode/wrong-type examples and complete-packet overflow fail before any provider call; no old-example substitution occurs.
- Prompt snapshots match the promoted exact texts and IDs; redesigned code has no dependency on legacy `generate.md`/`repair.md`, while current public code still has exactly its characterized dependency until Slice 09.
- Fake tests prove exactly one system and one canonical JSON user message, the exact per-type response schema, one call on strict-output rejection, and no `json_object` fallback.
- Boundary tests cover 16 MiB packet and 8 MiB response limits by UTF-8 byte count, including multibyte content and no truncation.
- Missing configuration, strict unsupported, context limit, transient unavailable, refusal, oversize, and invalid response map to exact codes/retryability with bounded safe details.
- Current MCP registrations, arguments, and result envelopes remain unchanged; no new public redesign tool is discoverable.
- Focused schema/packet/prompt/fake-provider tests and `cd backend; uv run python manage.py test` pass fully offline.
- Stale prompt/schema/ID searches, `git diff --check`, and implementation audit pass with no unresolved finding; no live provider, frontend, `.env`, hidden gold, or user artifact is used.

## Previous Slice

- [`02-request-persistence-foundation.md`](02-request-persistence-foundation.md)

## Next Slice

- [`04-training-fixtures.md`](04-training-fixtures.md)

## Outcome

**Completion:** Added canonical direct/context packet construction from validated requests and injected exact-two example
sets, deterministic catalog/profile/rule projection, all six strict logical response-schema selections, externalized
versioned generation/repair prompts, full wire digest/byte accounting, and fixed 16 MiB packet/8 MiB raw response
ceilings. Added a new one-call `generate_json_strict` provider path with no output-format or control retry, typed strict
format/context/transient/refusal/size/invalid-response classification, local response validation, and a strict-capable
fake client. Existing public generation continues using the unchanged compatibility client/path until Slice 09.

**Deviations:** Slice 03 uses injected schema-valid synthetic pairs with the approved fixed IDs because Slice 04 owns the
production source fixtures/manifests. The existing `generate_json` strict-to-JSON-object compatibility behavior remains
only for current public callers; redesigned packets exclusively call the new no-fallback strict method. Legacy prompt
assets remain current-path-only for Slice 09 removal.

**Verification:** Added exact prompt snapshots, canonical packet/digest, direct/context leakage, all-six response schema,
example count/ID/mode/type, packet-bound, strict-call, response-validation, provider-code/call-count, UTF-8 response-bound,
and compatibility regression tests. The implementation audit passed with no blocker/important finding; 135 focused
LLM/direct/context/readiness tests, all 724 provider-free backend tests (4 skipped), real stdio smoke, Python compilation,
and `git diff --check` pass.

**Follow-up:** Slice 04 replaces the injected pairs with the twelve reviewed deterministic production fixtures and six
ordered manifests. Slice 05 invokes the versioned repair packets/prompts; Slice 09 alone activates the new public surface.
