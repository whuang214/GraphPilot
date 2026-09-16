# Slice 10: Evaluation Capture Foundation

## Purpose

Establish the offline evaluation contracts, safe artifact store, semantic projection, and evaluation-owned capture
observer needed to assess the redesigned direct/context production path without coupling generation to evaluation.
The slice proves the complete capture path with visible gold and fake provider clients only.

## Background

Slice 1 introduces a generation-owned, immutable `GenerationObserver` protocol and no-op implementation. Slices 2–9
then build and cut over the redesigned generation path. Evaluation must consume that neutral seam from the outside:
generation may emit bounded stage/provider/candidate/result events, but it must never import evaluator contracts,
services, cases, or gold.

The built-in suite evaluates final delivered semantics. Direct cases begin from a frozen validated direct request;
context cases begin from frozen validated JSON 1/JSON 2 plus deterministic resolution and do not invoke the live
readiness reviewer. End-to-end repository inspection and readiness remain a separate RepoBench concern.

## Design

- Add strict, bounded, namespace-first V1 contracts for visible evaluation cases/oracles, run manifests, observations,
  capture events, semantic projections, and artifact references. Canonical JSON digests identify every immutable input
  and output.
- Keep question/authority material separate from oracle material. The generation invocation receives only its normal
  mode-specific authority; the evaluation observer and later evaluator stages may receive the visible oracle only after
  generation input has been built. No oracle path, content, digest, ID, or metadata enters a generator packet or the
  evaluated workspace.
- Implement an evaluation-owned observer over the generation-owned protocol. It records bounded copies/digests of the
  exact generation input, raw logical response, deterministic issues and repairs, normalized candidates, runtime
  semantic-review and repair results, final canonical diagram, render outcome, provider usage, stage latency, warnings,
  and operation errors. It cannot influence retries, repair choices, persistence, rendering, or the returned outcome.
- Preserve generated attempts (including post-persistence warnings), blocked attempts, and operation errors as complete
  observations. Delivery failures remain scored observations rather than being dropped from aggregation.
- Project the final canonical diagram to normalized semantics by removing coordinates, dimensions, style, viewport,
  layout/runtime metadata, and trace fields while retaining semantic types, labels, topology/containment, structured
  fields, and context origins.
- Store evaluation artifacts beneath `.graphpilot/evaluation/runs/<run-id>/` through workspace-safe, bounded, atomic
  I/O. The manifest and completed observations are immutable; resume uses exact run/case/repetition/condition identity
  and rejects digest or version disagreement rather than overwriting evidence.
- Require an explicit `executionMode: dry_run|live` value in the run contract with no default. This slice builds and
  validates the contract/storage boundary; Slice 13 owns execution. Neither mode may be inferred from credentials or
  environment state.
- Record exact commit, chat/embedding deployment and model identities when applicable, prompts, schemas, profiles,
  examples, rubrics, quality mode, repair budgets, effective provider controls, and observer/capture versions without
  persisting secrets.

## Plan Audit

- **Dependency gate:** implementation starts only after active generation/evaluation owners are promoted and Slices 1–9
  are complete, including the neutral observer and atomic public cutover. Evaluation must target the one redesigned
  path, not preserve or recreate an old runtime.
- **Ownership gate:** `services/generation/` owns only the observer protocol/events/no-op; new evaluation modules own the
  capture observer, cases, gold, projections, and artifacts. Import-graph tests must prove generation has no evaluation
  dependency and runtime diagnostics remain a separate observer.
- **Gold and leakage gate:** all committed fixtures in this slice are visible synthetic or human-labeled calibration
  material. Hidden-gold authoring, loading, sealing, and certification are expressly deferred until Slice 13's freeze
  gate is later satisfied. Tests must use sentinel oracle content to prove it cannot reach generation packets or
  workspaces.
- **Storage and resume gate:** path containment, size/count bounds, canonical digests, exclusive/atomic creation,
  interrupted writes, duplicate identities, and mismatched resume attempts are covered before later provider execution
  can rely on the store.
- **Completeness gate:** observer tests cover success, block, post-persistence generated outcomes with warnings, and
  failures at every available generation stage. Capture must remain useful for attribution without changing the
  observed result.
- **Safety and reversibility:** normal tests use fake LLM clients and perform no Azure chat or embedding calls. Rollback
  is an ordinary revert of the slice implementation; versioned non-canonical evaluation artifacts are never silently
  migrated, deleted, or treated as production inputs.
- **Verification coverage:** focused contract/storage/projection/observer tests precede the complete offline backend
  suite, stdio smoke where affected, stale-import searches, and `git diff --check`.

Plan audit result: **Pass.** The audit confirmed generation/evaluation import separation, visible-only gold, oracle-after-packet leakage boundary, complete terminal capture, bounded immutable storage/resume, exact projection, explicit execution mode contract, fake-only tests, and artifact-preserving rollback.

## Included Work

- Evaluation case, oracle, run-manifest, observation, semantic-projection, and artifact-reference schemas and Python
  values, limited to visible calibration fixtures.
- Schema-registry and canonical serialization/digest support for evaluation artifacts.
- Workspace-safe evaluation run paths, immutable manifest/observation writes, bounded reads, and exact resume identity.
- Mode/type-neutral final semantic projection with direct/context origin handling.
- Evaluation-owned `GenerationObserver` implementation and capture assembly for every terminal outcome.
- Capture of exact version/configuration identities, calls, usage, latency, repair/review stages, warnings, and failures
  without secrets or hidden reasoning.
- Fake direct and context full-pipeline tests, including generated, generated-with-warning, blocked, and error
  observations.
- Import-direction and sentinel-gold leakage tests proving observer separation.
- Active evaluation/backend/testing/environment documentation updates required by the implementation, while keeping live
  status in the current-state board and implementation history in this slice's eventual outcome.

## Not In Scope

- Embedding retrieval, concept alignment, deterministic semantic grading, or matcher thresholds; Slice 11 owns them.
- Evaluation-judge calls, metrics aggregation, certification gates, adjudication, or reports; Slice 12 owns them.
- Executing dry/live runs, calibration, freeze manifests, or operational resume orchestration; Slice 13 owns them.
- Hidden-gold authoring, hidden pilots, RepoBench golds, live Azure calls, semantic certification, or production
  promotion.
- Any change to generation decisions, repair budgets, public MCP contracts, or canonical diagram behavior.
- Persisting secrets, raw hidden reasoning, or evaluation artifacts as canonical diagram/context inputs.

## Target Areas

- `backend/assets/schemas/` for evaluation foundation contracts
- new evaluator-owned modules under `backend/services/evaluation/`
- generation-owned observer interfaces under `backend/services/generation/` only where established by Slice 1
- `backend/services/shared/` for bounded path-safe artifact I/O and canonical digests
- `backend/tests/evaluation/` plus focused generation/support/contract integration tests
- active backend architecture, evaluation design, testing-strategy, and environment owners

## Exit Criteria

- Valid and invalid fixtures prove every new schema's field, unknown-property, text/array, byte, identity, and digest
  bounds.
- Evaluation artifacts are path-contained, atomically written, immutable after completion, and safely resumable only
  under an exact matching identity; interrupted/corrupt/mismatched artifacts fail closed.
- Semantic projections for all six mode/type cells remove presentation/runtime data while retaining exact semantics,
  structured fields, topology/containment, and permitted origins.
- Fake direct/context production-path tests capture complete generated, generated-with-warning, blocked, and operation-
  error observations, including provider usage and first-failing-stage evidence, without changing generation results.
- Import checks prove production generation does not import evaluation modules and normal generation still uses the
  no-op observer unless an external observer is injected.
- Sentinel tests prove visible oracle content/paths never enter generation inputs, prompts, traces, canonical workspace
  artifacts, or runtime diagnostics.
- Omitted/invalid execution mode is rejected by the foundation contract; no test constructs a real provider client or
  makes an Azure call.
- Focused tests, `cd backend; uv run python manage.py test`, affected stdio smoke, stale-import searches, and
  `git diff --check` pass, with exact results recorded before commit.

## Previous Slice

- [`09-atomic-public-cutover.md`](09-atomic-public-cutover.md)

## Next Slice

- [`11-deterministic-matcher.md`](11-deterministic-matcher.md)

## Outcome

**Completion:** Added the offline-only evaluation capture foundation under `services/evaluation/`: frozen capture/reference
values, a failure-isolated downstream `EvaluationCaptureObserver`, strict six-cell `SemanticProjectionService`, bounded
canonical `EvaluationArtifactStore`, and complete `EvaluationObservationService`. Generation still imports no evaluator;
its neutral provider events now include exact request/response digests and the production orchestrator emits terminal plus
post-layout canonical/persistence/render evidence to injected observers without allowing observer failures to affect the
primary outcome.

**Storage and leakage:** Run manifests require explicit `dry_run|live`, exact output/run identity, complete
prompt/schema/profile/example/rubric/layout/observer/capture version categories, and supported observer/capture versions.
Manifests, capture artifacts, and completed observations use canonical JSON, 16 MiB per-artifact and 64-artifact
per-observation bounds, exclusive writes, exact digest/byte verification, symlink-safe paths, immutable idempotent resume,
and fail-closed corruption/mismatch handling. Evaluation control storage can be explicitly bound to—and must differ
from—the evaluated workspace, so oracle IDs/paths/digests/content never enter generation packets or that workspace.

**Capture and projection:** Complete generated, generated-with-render-warning, readiness/semantic blocked, and operation-
error attempts remain observations with first-failing stage, defects, exact provider digests/bytes/usage/latency, stage
evidence, warnings, errors, configuration, commit, and version bindings. Projection tests cover all six direct/context ×
Activity/Use Case/BDD cells, retain labels/topology/containment/structured fields/context origins, normalize strict BDD
fields, and remove viewport/coordinates/dimensions/style/runtime metadata. Frozen case references are checked against the
captured question/oracle artifacts before observation completion.

**Verification:** Implementation audit passed with no blocker/important findings. Twenty-seven evaluation tests cover
schemas, Python contracts, immutable/concurrent storage, exact resume, corruption/tamper/symlink rejection, all six
projections, generated/warning/blocked/error capture, direct/context production paths, observer isolation, import
direction, version completeness, and sentinel-oracle leakage. The complete offline backend suite passed 758 tests (5
skipped); focused generation/evaluation tests passed; Python compilation/import checks and `git diff --check` passed. No MCP/API/frontend surface changed and no Azure chat or embedding client was constructed.

**Deviations:** Slice 10 does not add separate persisted capture-event or artifact-reference schema files; those exact
bounded values are evaluation-owned Python contracts, while persisted references remain strictly defined inside the
registered observation schema. Visible material is limited to registered schema examples and synthetic/fake tests;
Slice 13 still owns durable visible calibration pools and the operator runner.

**Follow-up:** Slice 11 consumes immutable semantic projections and observations to add deterministic matching,
explicit evaluation embeddings, and a digest-bound cache.
