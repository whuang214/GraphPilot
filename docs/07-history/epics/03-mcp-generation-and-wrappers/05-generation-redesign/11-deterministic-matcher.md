# Slice 11: Deterministic Matcher

## Purpose

Implement reproducible concept alignment and hard mechanical grading over captured final semantic projections, using an
explicit evaluation embedding deployment and deterministic one-to-one assignment. Normal verification remains fully
offline through fake embeddings and visible gold only.

## Background

Slice 10 supplies validated visible cases/oracles, final semantic projections, immutable observations, and safe artifact
storage. This slice turns an oracle and candidate projection into the versioned deterministic report consumed by the
independent evaluation judge in Slice 12.

Lexical equality alone cannot align semantically equivalent labels such as “Cancel Order” and “Abort Purchase.”
Embedding similarity helps propose those alignments, but it cannot override incompatible semantic types, topology, or
structured fields, and it cannot establish that a context citation semantically supports a claim.

## Design

- Resolve embeddings only through explicit `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`. There is no fallback to
  `AZURE_OPENAI_DEPLOYMENT`, another chat role, lexical-only certification, or a silently substituted local model.
  Missing/invalid live configuration is a typed non-run/failure condition, never a degraded score.
- Normalize concept text through one versioned preprocessing function, then cache validated vectors by embedding
  deployment, resolved model identity, preprocessing version, and normalized-content digest. Cache entries are bounded,
  path-safe, secret-free, immutable for that identity, and rejected on dimension/cardinality/index/non-finite mismatch.
- Use a stable staged alignment:
  1. normalize labels and match exact approved aliases;
  2. obtain fixed cached embedding similarity for still-unmatched concepts;
  3. eliminate hard semantic-type incompatibilities;
  4. add topology/neighbour and structured-field compatibility scores;
  5. solve deterministic maximum-weight one-to-one assignment; and
  6. classify matched, missing, extra, forbidden, or ambiguous results.
- Freeze and capture preprocessing, embedding identity, thresholds, component weights, assignment algorithm version,
  canonical ordering, and tie-break rules. Input order, batching, cache hit/miss state, process hash randomization, and
  equivalent-score ties must not change the report.
- Prevent one candidate element from satisfying multiple gold concepts. Exact wording or high cosine similarity cannot
  overcome a hard type/topology contradiction. Low-margin or equivalently valid assignments remain explicit
  ambiguities for Slice 12 rather than being forced into false certainty.
- Grade delivery, required/optional/forbidden concepts, semantic types, relationship identity/direction, topology,
  containment, structured fields, extras, confidence, and ambiguity. Add the approved Activity, Use Case, BDD, and
  context-origin mechanical checks.
- For context, code verifies origin presence, selected/accepted/allowlisted exact refs, schema mechanics, minimum
  grounding, and duplicate refs. Semantic support/minimality remains judge/human work; the deterministic matcher must
  not overclaim it.
- Emit the Slice 10 `graphpilot.evaluation.deterministic-report.v1` contract with canonical ordering and evidence refs
  suitable for strict downstream allowlisting.

## Plan Audit

- **Dependency gate:** implementation begins only after Slice 10's contracts, projection, artifact store, and observer
  separation are complete and promoted active owners define the final matcher/report contract.
- **Provider boundary:** embeddings have one dedicated environment setting,
  `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`, with no fallback. The user-approved single
  `AZURE_OPENAI_DEPLOYMENT` remains the chat deployment for all chat roles and is not reused as an embedding default.
- **Reproducibility gate:** the audit must fix normalization, vector validation, cache key/content, score precision,
  matrix ordering, assignment tie-breaks, ambiguity margins, and report ordering before implementation. No ambient
  ordering or favorable rerun may affect a result.
- **Semantic boundary:** embeddings are an alignment signal, not an authority oracle. Hard vocabulary/type rules,
  relationship direction, topology, and structured-field requirements remain independently enforced; context reference
  validity is not mislabeled as factual support.
- **Gold/leakage gate:** only visible synthetic or human-labeled matcher fixtures are committed or loaded. Embedding
  requests are evaluation-owned and cannot be made through generation; sentinel tests prove oracle labels/content do
  not enter generator packets or workspaces.
- **Dependency and rollback gate:** prefer existing Python/runtime mechanisms and add no matching/scientific dependency
  without a separately audited need. Rollback is an ordinary revert of this slice; cache identity/version checks keep
  old non-canonical vectors from being silently reused.
- **Verification coverage:** fake embedding tests cover every response/error/cache edge and every approved grading
  domain. A live embedding calibration is a separate explicit Slice 13 action and is not part of implementation checks.

Plan audit result: **Pass.** The audit confirmed explicit embedding-only configuration, validated cache identity, deterministic one-to-one assignment/tie-breaks, hard semantic/topology boundaries, complete mechanical graders, ambiguity preservation, visible-only fake embedding proof, and no generation dependency.

## Included Work

- Evaluation-only embedding client/configuration adapter using the explicit evaluation embedding deployment.
- Versioned text normalization, bounded request batching, strict embedding response validation, and vector similarity.
- Atomic normalized-text/vector cache with deployment/model/preprocessing/content identity and corruption detection.
- Exact alias handling and hard mode/type semantic compatibility filters.
- Topology/neighbour and structured-field compatibility scoring.
- Deterministic maximum-weight one-to-one assignment, canonical tie-breaks, confidence margins, and ambiguity inventory.
- Required/optional/forbidden concept, extra-content, semantic-type, relationship/direction, topology/containment,
  structured-field, delivery, and origin-reference grades.
- Activity-specific sequence/guard/concurrency/reachability checks; Use Case actor/subject/include/extend/generalization
  checks; BDD property/multiplicity/relationship/constraint checks; and context origin mechanics.
- Canonically ordered deterministic reports with allowlisted evidence references and metric components.
- Fake-embedding unit/integration fixtures, including visible human-labeled alignment examples and sentinel leakage
  cases.
- Required active evaluation/environment/testing/backend documentation updates and exact configuration examples without
  changing or creating a real `.env`.

## Not In Scope

- Live Azure embedding calibration or any live provider call while implementation is unattended.
- Evaluation-judge semantics, material fact assessment, human adjudication, aggregate gates, or report analysis; Slice
  12 owns them.
- Runner execution, repetitions, resume orchestration, freeze, or leakage certification; Slice 13 owns them.
- Hidden-gold cases, hidden threshold tuning, RepoBench gold, generation-example selection, or production promotion.
- Replacing deterministic canonical validation or runtime semantic review.
- Treating embedding similarity as proof of factual context support.

## Target Areas

- evaluator matcher/embedding/cache modules under `backend/services/evaluation/`
- `backend/services/llm/` only for a neutral injectable Azure/fake embedding transport seam where appropriate
- evaluation schemas/configuration identities under `backend/graphpilot/`
- `backend/tests/evaluation/` and focused `backend/tests/llm/` configuration/transport tests
- `backend/.env.example` and active environment/evaluation/testing/backend architecture owners during implementation

## Exit Criteria

- Fake embedding tests cover normalization, deterministic batching, cache hit/miss, deployment/model/preprocessing
  isolation, corrupt entries, wrong cardinality/index/dimension, non-finite vectors, bounds, and classified provider
  failures without any network access.
- Exact aliases precede embeddings; hard semantic-type incompatibilities cannot match; one candidate cannot satisfy two
  gold concepts; topology/field contradictions cannot be hidden by label similarity.
- Maximum-weight assignment and ambiguity classification are byte-for-byte stable across reordered inputs, repeated
  runs, cache states, and equal-score ties.
- Activity, Use Case, BDD, context-origin, relationship, containment, structured-field, forbidden, extra, and delivery
  graders pass positive, negative, ambiguity, and threshold-boundary fixtures.
- Deterministic reports validate, use canonical ordering, expose all evidence/ambiguities, and never claim semantic
  context support from reference validity alone.
- Live configuration requires nonblank `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT` and has no fallback to
  `AZURE_OPENAI_DEPLOYMENT`; normal tests use fake embeddings and construct no real Azure client.
- Sentinel leakage tests prove oracle text/vectors/cache paths cannot enter generation inputs, model-visible generation
  messages, canonical workspaces, or runtime diagnostics.
- Focused tests, `cd backend; uv run python manage.py test`, applicable stdio smoke, stale-config/import searches, and
  `git diff --check` pass with exact results recorded before commit.

## Previous Slice

- [`10-evaluation-capture-foundation.md`](10-evaluation-capture-foundation.md)

## Next Slice

- [`12-evaluation-judge-and-gates.md`](12-evaluation-judge-and-gates.md)

## Outcome

**Completion:** Added the evaluation-only embedding transport, versioned normalization/cache, and deterministic matcher.
`AzureEmbeddingClient` uses only explicit `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`, sends Azure embeddings with
`encoding_format=float` and SDK retries disabled, and validates response indices, cardinality, dimensions, finiteness,
and resolved model identity. `FakeEmbeddingClient` preserves the same strict seam for all normal tests; missing or empty
embedding configuration is a typed matcher failure with no chat, lexical, local-model, or alternate-provider fallback.

**Cache and reproducibility:** NFKC/casefold/whitespace preprocessing is digest-bound. Cache identity includes deployment,
resolved model, preprocessing version/digest, and normalized-content digest; immutable canonical entries and model markers
are bounded, secret-screened, symlink-contained, process-locally serialized, exclusively written, and fail closed on
shape/cardinality/dimension/nonfinite/canonical/model mismatch. Resolution deduplicates sorted normalized texts, uses
fixed 128-item batches, restores caller order, and produces byte-identical reports on cache miss/hit.

**Matcher and grading:** Exact labels and approved aliases precede embeddings. Hard element-kind/semantic-type partitions,
required topology, and critical structured-field contradictions cannot be overridden by similarity. Matching uses an
exact rectangular Hungarian assignment for full bounds with canonical ordering, 12-decimal score precision, and stable
lexicographic tie handling; low-margin embedding assignments remain explicit ambiguities. Strict reports grade required/
optional/critical concepts, forbidden and extra content, relationship identity/type/direction/topology, containment and
structured fields, delivery, and context origin presence/allowlists/uniqueness/grounding/schema mechanics. Visible fake
fixtures cover all six direct/context × Activity/Use Case/BDD cells and accepted structural/grounding alternatives.

**Verification:** Both implementation audits passed after adding explicit unconfigured/empty identity/no-lexical-fallback
tests. Embedding/cache/matcher/settings/type-cell focused tests passed, including provider classification, deterministic
batching, concurrent immutable writes, model isolation, corruption, global-optimum 21×21 assignment, equal-score ties,
high-similarity hard contradictions, warning/delivery boundaries, and context origins. The complete offline backend suite
passed 786 tests (5 skipped); Python compilation and `git diff --check` passed. No real embedding/chat call, MCP/API/
frontend surface, hidden gold, judge, gate, or runner was added.

**Deviations:** No scientific/matching dependency was needed; the exact Hungarian implementation is local and partitioned
by hard semantic compatibility. Matcher evidence uses the already-registered deterministic-report schema rather than
adding another persisted contract.

**Follow-up:** Slice 12 consumes deterministic reports and bounded artifacts for the blinded evaluation judge, material
facts, deterministic metrics/gates, adjudication, and authoritative reports.
