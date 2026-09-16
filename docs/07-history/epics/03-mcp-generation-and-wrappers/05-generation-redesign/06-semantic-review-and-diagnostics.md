# Slice 06: Semantic Review and Diagnostics

## Purpose

Implement the production/default semantic-candidate review path for direct and context generation, including composed
rubrics, deterministic findings and host actions, bounded semantic repair, explicit quality results, an optional compact
trace sidecar, and optional safe numbered diagnostics.

## Background

Slices 1–5 establish the contract registry and observer seam, persisted mode-specific authority, strict logical
schemas/model packets, fixed training fixtures, and an accepted normalized pre-layout candidate with explicit
deterministic repair. This slice reviews that normalized candidate before layout. It does not alter canonical save
validation, context readiness, or authority, and it does not expose the redesigned public MCP surface before Slice 9.

## Design

### Exact quality behavior

`GRAPHPILOT_GENERATION_QUALITY_MODE` accepts only `reviewed|standard`, is validated strictly at startup, and defaults
to `reviewed`:

- `reviewed` runs semantic review over normalized pre-layout semantics, permits bounded review-guided repair, reruns
  deterministic validation after every repair, and requires a final valid review before layout/persistence;
- `standard` is an explicit environment-only diagnostic/ablation path: direct still runs strict generation plus
  deterministic diagram validation/repair; context still runs readiness, strict generation, and deterministic diagram/
  provenance validation/repair; it makes no semantic-review LLM call and reports `reviewStatus: not_run`; and
- reviewer/provider/contract failure in `reviewed` mode is a typed operation error. It never falls back to `standard` or
  returns an unreviewed diagram.

`GRAPHPILOT_GENERATION_SEMANTIC_REPAIR_MAX_ROUNDS` is also startup-validated, allows `0..2`, and defaults to `1`.
All chat roles—including generation, readiness, semantic review, response repair, and semantic candidate repair—resolve
the one configured `AZURE_OPENAI_DEPLOYMENT`; no role-specific deployment selector or hidden model fallback is added.
The exact deployment/model used is captured outside canonical JSON.

Warnings and blockers may request repair while budget remains. Warnings may remain after exhaustion; any blocker after
exhaustion returns `outcome: blocked`, `isError: false`, host actions, and no canonical/trace write. Actual operational
failures use `OperationProblem` with `isError: true`. No unchanged candidate is rerolled.

### Rubric and actions

Each final rubric is an immutable, digest-bound composition:

```text
common layer + direct|context authority layer + activity|use-case|bdd type layer
```

The shared document/rating IDs are `graphpilot.generation.semantic-review-rubric.v1` and
`graphpilot.generation.semantic-review-rating.v1`. Source layers are exactly:

```text
graphpilot.generation.semantic-review-rubric-layer.common.v1
graphpilot.direct.semantic-review-rubric-layer.authority.v1
graphpilot.context.semantic-review-rubric-layer.authority.v1
graphpilot.generation.semantic-review-rubric-layer.activity.v1
graphpilot.generation.semantic-review-rubric-layer.use-case.v1
graphpilot.generation.semantic-review-rubric-layer.bdd.v1
```

The six final snapshots use `graphpilot.<mode>.semantic-review-rubric.<type>.v1`. Their exact facet catalog is:

```text
Common:
  goalFidelity, scopeCompliance, abstractionConsistency, unsupportedAdditions,
  internalCoherence
Direct:
  requirementCoverage, assumptionCompliance, decisionApplication,
  inferenceAppropriateness
Context:
  selectedClaimCoverage, originRelevance, originMinimality, assumptionAuthority,
  decisionApplication, viewpointFidelity, groundingCompleteness
Activity:
  trigger, behaviorSequence, decisionGuards, completionOutcomes, concurrency,
  dataMovement, exceptionPaths
Use case:
  subjectBoundary, actorCoverage, actorGoalCoverage, participationCorrectness,
  includeExtendCorrectness, generalizationCorrectness, extensionPointCorrectness
BDD:
  structuralSubject, entityCoverage, relationshipCorrectness, ownershipComposition,
  propertiesAndTypes, multiplicity, generalizationDependency, constraints
```

Every applicable facet uses the exact shared anchors:

| Rating | Meaning |
| ---: | --- |
| `0` | Contradicted, absent, or wholly unsupported |
| `1` | Major semantic failure; mostly incorrect |
| `2` | Partial, ambiguous, or materially incomplete |
| `3` | Sufficient and correct for requested scope |
| `4` | Complete, precise, and unambiguous |

Every V1 facet has `minimumRating: 3`; its exact `weight/blockingBelow` baseline is:

```text
Common:
  goalFidelity 4/2; scopeCompliance 4/2; abstractionConsistency 2/1;
  unsupportedAdditions 4/3; internalCoherence 3/2
Direct:
  requirementCoverage 4/2; assumptionCompliance 4/3; decisionApplication 2/1;
  inferenceAppropriateness 4/3
Context:
  selectedClaimCoverage 4/2; originRelevance 4/3; originMinimality 2/1;
  assumptionAuthority 4/3; decisionApplication 2/1; viewpointFidelity 4/3;
  groundingCompleteness 4/3
Activity:
  trigger 3/2; behaviorSequence 4/2; decisionGuards 4/2; completionOutcomes 4/2;
  concurrency 3/2; dataMovement 2/1; exceptionPaths 3/2
Use case:
  subjectBoundary 2/1; actorCoverage 4/2; actorGoalCoverage 4/2;
  participationCorrectness 4/2; includeExtendCorrectness 4/2;
  generalizationCorrectness 3/2; extensionPointCorrectness 3/2
BDD:
  structuralSubject 3/2; entityCoverage 4/2; relationshipCorrectness 4/2;
  ownershipComposition 4/2; propertiesAndTypes 3/2; multiplicity 3/2;
  generalizationDependency 3/2; constraints 3/2
```

Always-applicable facets are all common facets; direct `requirementCoverage`/`inferenceAppropriateness`; context
`selectedClaimCoverage`/`originRelevance`/`originMinimality`/`viewpointFidelity`/`groundingCompleteness`; Activity
`trigger`/`behaviorSequence`/`completionOutcomes`; Use Case `actorCoverage`/`actorGoalCoverage`/
`participationCorrectness`; and BDD `structuralSubject`/`entityCoverage`. Every other facet is conditional on supplied
authority or candidate semantics, and only conditional facets may be N/A.

Each facet also owns immutable anchors and applicability. The private reviewer response supplies every facet once in
canonical order with applicability, rating, rationale, allowlisted element/authority refs, and proposed findings. It
never supplies severity, score, acceptance, or overall status. Backend code validates all refs and cross-field rules
and computes:

```text
rating >= minimumRating  → sufficient
rating < blockingBelow   → blocking
otherwise                → warning

clean    = every applicable facet sufficient
warnings = no blocker and at least one warning
blocked  = at least one blocking facet
score    = round(100 * sum(weight * rating) / sum(applicable weight * 4))
```

The score is secondary telemetry only; one blocking facet blocks regardless of that score.

The allowed finding codes are exactly:

```text
goal_mismatch, scope_violation, required_content_missing, authority_contradiction,
authority_ambiguous, unsupported_addition, abstraction_mismatch, internal_incoherence,
incorrect_element_meaning, incorrect_relationship_meaning, incorrect_topology,
incorrect_structured_data, origin_not_relevant, origin_not_minimal, viewpoint_mismatch
```

The allowed resolution/action kinds are exactly:

```text
Shared:  repair_candidate, ask_user, report_warning
Direct:  revise_request
Context: select_existing_claim, remove_selection, revise_context,
         replace_assumption_with_claim, search_source
```

Only validated `repair_candidate` findings enter semantic repair. All authority-changing actions return to the host and
owning request/context stage. `report_warning` is valid only for a deterministic warning. One private-response contract
repair may correct response shape/refs without reevaluating the candidate; a second invalid response returns
`semantic_review_invalid`. Semantic repair receives unchanged authority, the previous normalized candidate, only
validated repair findings, round/version identity, and no examples or host-owned actions.

### Canonical, trace, and debug separation

Canonical `.gp.json` keeps only generic diagram metadata, minimal generation mode/request ownership, the context
manifest reference where applicable, and context element origins. It never receives model, prompt, logical-schema,
example, rubric/score, review, finding/action, layout-engine, usage, or diagnostics payloads.

`persistGenerationTrace` and `persistGenerationDebug` are independent workflow booleans, both default `false`, and do
not alter acceptance. Slice 6 implements their internal services/contracts; Slice 9 is the only slice that exposes and
propagates the redesigned workflow arguments.

- Trace is written only after successful canonical persistence to
  `.graphpilot/diagrams/<name>.gp.trace.json` under `graphpilot.generation.trace.v1`. The atomic sidecar is bound to the
  exact diagram digest and contains compact request/manifest refs, model/version/example/repair/review/rubric/score/
  layout/usage summaries. It excludes prompts, full rubrics, candidates, source, findings, and rationales. A later
  diagram-digest mismatch makes it historical. `trace_write_failed` does not undo the diagram; blocked/error attempts
  have no trace sidecar.
- Debug writes one bounded run beneath
  `.graphpilot/diagnostics/generation/<request-id>/<run-id>/`, with stable stages `00` through `08`: run, authority,
  optional context readiness, generation, semantic review, layout, canonical validation, persistence/render, and final
  result. Optional/unreached stages are absent rather than renumbered. `00-run.json` and `08-result.json` use strict
  envelopes; one collection README explains the format. One artifact is limited to 16 MiB and one run to 128 MiB.
  Secrets, auth headers, raw unselected source/evidence, and unbounded provider transport are never saved. Debug is
  local, gitignored, disposable, non-authoritative, and never runtime/training/evaluation input. A diagnostics-only
  failure preserves the primary generated/blocked/error result and reports `diagnostics_write_failed` where transport
  permits.

## Plan Audit

- **Dependencies and ordering:** require implemented/audited Slices 1–5 and the promoted generation, validation,
  canonical-schema, backend, environment, and MCP owners. Consume the Slice 1 observer/contracts rather than adding an
  evaluation dependency, and leave public registration/result replacement to Slice 9.
- **Exact default:** make `reviewed` the strict production/default mode, retain `standard` only as explicit
  environment-level diagnostics/ablation, validate both settings at startup, and forbid every automatic reviewed-to-
  standard fallback or per-call public override.
- **Trust boundaries:** review only the normalized candidate after deterministic graph/provenance checks and before
  layout. The reviewer is not readiness, canonical validation, or save-blocking UI validation and cannot mutate
  request/context authority.
- **Rubric determinism:** own common/mode/type source layers once, compose and snapshot all six ordered final rubrics,
  bind versions/digests, validate conditional N/A and refs, and keep severity/status/score in deterministic backend
  code rather than model output.
- **Repair and routing:** permit one response-contract repair, `0..2` semantic candidate repairs (default one), and no
  blind reroll. Route every non-repair action to the host; warnings may generate after budget, blockers never save or
  force through.
- **Result transport:** always return explicit quality mode/status/repair count/findings. Keep semantic findings under
  `quality.findings`, operational warnings under `operationWarnings`, valid blocks as `isError: false`, and technical
  failures as `OperationProblem`/`isError: true`.
- **Trace/debug safety:** keep both opt-in and independent, enforce atomic/bounded/path-safe writes and exact schemas,
  isolate optional write failures, prove canonical output is unchanged, and never persist secrets, full authority,
  hidden reasoning, or unrestricted provider payloads.
- **Frontend boundary:** update only optional canonical metadata/origin preservation types and parity tests if the
  promoted contracts require it; recheck status and coordinate exact files with the concurrent frontend agent before
  editing, never stage its work, and do not add review/debug UI or copy trace/debug content into editor state.
- **Evaluation seam:** emit bounded immutable observer events/captures, but do not import evaluation modules, author
  hidden gold, or claim hidden certification from the 18 visible behavior fixtures.
- **Reversibility:** one ordinary revert of the Slice 6 implementation restores the pre-review standard pipeline and
  removes its settings/rubrics/services/optional writers. Existing canonical diagrams remain valid; disposable trace/
  debug artifacts are not rewritten or deleted.
- **Verification:** use fake clients only; cover all mode/type/status, threshold/action, contract-repair, semantic-
  repair, operation-error, trace/debug, bounds, and canonical-cleanliness matrices, then run the complete backend and
  affected frontend gates. No live Azure call, push, or production-promotion claim is allowed.

Plan audit result: **Pass after correction.** The audit verified every rubric facet/anchor/threshold, reviewed default, action and repair boundary, result/warning/error separation, canonical/trace/debug bounds, legacy-prompt deferral, generation/evaluation independence, and explicit concurrent-frontend coordination.

## Included Work

- Add the shared semantic-review service and direct/context authority adapters over normalized pre-layout candidates.
- Implement and register the shared rating scale, common/mode/type rubric layers, and all six composed immutable
  snapshots with canonical versions/digests.
- Implement strict mode-specific review inputs/private responses, local response validation, one response-contract
  repair, deterministic results, finding IDs/severity/status/score, and validated repair/host actions.
- Implement smallest-change direct/context semantic repair with startup-validated `0..2` budget and default one round.
- Wire `reviewed` as the startup-validated default and `standard` as explicit no-review diagnostics/ablation only.
- Produce compact generated/blocked quality summaries and the typed semantic-review operation failures from the
  approved registry.
- Implement atomic digest-bound trace sidecars and bounded numbered generation diagnostics through independent
  observer consumers.
- Preserve only minimal request/manifest ownership and context origins in canonical diagrams.
- Add 18 visible mode/type clean-warning-block fixtures plus boundary, host-routing, no-blocker-save, failure, sidecar,
  diagnostics, canonical-cleanliness, and optional frontend preservation tests.
- Update the active generation/backend/validation/schema/environment/testing owners and this slice outcome during
  implementation without treating research as runtime authority.

## Not In Scope

- Public `diagram_generation_workflow` or generation-tool/schema cutover; Slice 9 owns that atomic migration.
- Readiness rubric/policy changes, repository inspection, or authority mutation inside the reviewer.
- PyGraphviz integration/cutover, layout, connector routing, or render design changes.
- Runtime best-of-N, unbounded retries, a public per-request quality selector, or automatic standard fallback.
- Evaluation matcher/judge/gates, hidden-gold authoring, live calibration/certification, or production promotion.
- A frontend semantic-review/debug browser, review editing, or canonical persistence of trace/debug metadata.
- Removing or changing legacy `backend/assets/prompts/generate.md` or `repair.md`; Slice 09 owns their approved
  atomic removal after all current public callers cut over.
- Any real `.env` edit or live provider call.

## Target Areas

- `backend/services/generation/` — semantic-review orchestration, mode adapters, semantic repair, observer integration,
  and compact quality assembly
- `backend/services/` and `backend/services/shared/operation_problem.py`
- `backend/services/llm/llm_client.py`
- `backend/services/shared/schema_registry.py` and safe workspace/atomic-write services
- `backend/assets/schemas/` — Slice 1 review/result/repair/trace/debug contracts
- `backend/assets/prompts/` and the generation rubric assets established by Slice 1
- `backend/graphpilot/settings.py` and `backend/.env.example`
- `backend/tests/generation/`, `backend/tests/llm/`, `backend/tests/shared/`, and affected MCP contract tests
- `frontend/src/types/diagram.ts` and parity/preservation tests only if minimal canonical metadata changes
- canonical generation, validation, backend architecture, environment, testing, MCP, and schema design owners under
  `docs/`
- this slice document

## Exit Criteria

- `reviewed` is the strict startup-validated default; explicit `standard` makes zero semantic-review calls and reports
  `not_run`; reviewed failures never silently downgrade.
- Semantic repair accepts only `0..2`, defaults to one, uses no examples/host actions, and cannot blind-reroll an
  unchanged candidate.
- All source layers and six final rubrics validate, compose in canonical order, have stable versions/digests, and match
  snapshots; rating/applicability/weight/threshold boundaries are covered.
- Private responses cannot set severity/score/status, invalid response shape gets at most one contract-repair call, and
  all element/authority refs, finding codes, and resolution kinds are allowlisted.
- All 18 visible clean/warning/block cases pass across direct/context and Activity/Use Case/BDD; warning/block thresholds,
  deterministic score, host action deduplication/bounds, and operation-error mapping are covered.
- Warnings may persist after budget; every residual blocker returns actionable `outcome: blocked` with `isError: false`
  and writes no canonical diagram, SVG, or trace.
- Trace tests prove successful-only atomic write, exact diagram binding, stale-digest interpretation, exclusions, and
  non-rollback `trace_write_failed` behavior.
- Debug tests prove stable `00..08` numbering, direct/context optional-stage behavior, safe run ownership/paths, 16 MiB
  artifact and 128 MiB run bounds, secret/source exclusions, and primary-outcome isolation on write failure.
- Canonical diagrams contain only approved minimal ownership/origins; frontend load/save preservation and canvas/SVG
  behavior remain unchanged where affected.
- Generation imports no evaluation module, normal tests use no provider, and visible fixtures make no certification
  claim.
- Focused tests, stale-contract searches, and the required PowerShell verification pass:

  ```powershell
  cd backend
  uv run python manage.py test
  cd ..\frontend
  npm run verify
  cd ..
  git diff --check
  ```

- Plan and implementation audits have no unresolved findings, and the ordinary-revert boundary is recorded in the
  completed outcome.

## Previous Slice

[`05-pre-layout-repair-pipeline.md`](05-pre-layout-repair-pipeline.md)

## Next Slice

[`07-pygraphviz-parity.md`](07-pygraphviz-parity.md)

## Outcome

**Completion:** Implemented reviewed-default semantic quality with six immutable common/mode/type rubric compositions,
digest-bound strict reviewer packets, backend-owned applicability/rating/outcome/severity/score policy, bounded finding and
resolution allowlists, exact private/result schemas, one response-contract repair, and zero-to-two semantic candidate
repairs that contain no examples and rerun deterministic acceptance before re-review. `standard` is an explicit zero-call
path; invalid quality/budget configuration fails startup and reviewed failures never downgrade. Added independent compact
generation trace and numbered 00–08 debug-run services with schema/digest binding, path/exclusive ownership, 16 MiB
artifact/128 MiB run ceilings, strict payload exclusions, and non-retrying failure isolation.

**Deviations:** The diagnostics and trace services remain internal until the unified Slice 09 orchestrator owns their
public switches and final result attachment. Slice 06 corrects the direct BDD example output reference in the strict
generation packet schema so the authored strict BDD fixtures—not a stale richer duplicate definition—are authoritative.
No canonical `.gp.json`, layout, persistence, or public MCP behavior changed.

**Verification:** Added 18 rubric-policy, 9 semantic-orchestration, 17 trace/debug, and 3 startup-configuration test groups,
including all six mode/type clean cells, warnings, blockers, contract repair, candidate repair, repair-only exhaustion,
allowlist violations, provider failures, standard zero calls, trace staleness, concurrent run ownership, bounds, secret/
prompt/raw/full-authority exclusions, and canonical immutability. Independent semantic and diagnostics audits passed after
closing response-contract, authority-projection, resolution-reference, and final-action findings. All 796 provider-free
backend tests passed (4 skipped); the post-audit expanded focused matrix passed and the final full suite passed 797 tests (4 skipped).

**Follow-up:** Slice 07 consumes only accepted semantics in the single in-process PyGraphviz layout engine; Slice 09 binds
review results, trace/debug references, and public quality switches to the atomic workflow.
