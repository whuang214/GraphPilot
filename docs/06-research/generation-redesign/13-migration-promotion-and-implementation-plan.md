# Migration, Promotion, and Implementation Plan

> **Status: user-approved 2026-07-17; revised execution authorized through audited planning, promotion, Slices 1–14,
> and final backend audit commits.** Approval and exact destructive-removal scope are recorded in
> `migration-plan-approval.json`. Live provider calls, hidden-gold authoring before freeze, push, destructive Git
> operations, and production promotion remain unapproved.

## Execution model

- Implement directly on `master`; no redesign branch or dual-runtime feature flag.
- Every slice follows `.devin/rules/graphpilot.md` exactly:

```text
create/update slice plan
→ audit plan
→ commit audited plan
→ add failing tests
→ implement
→ audit implementation
→ address findings
→ run focused and required broad checks
→ commit implementation
```

- Standing permission covers completed audited plan/implementation commits; never push.
- Preserve unrelated working-tree changes and stage only owned files. A separate frontend agent is active: recheck
  status before every frontend-affecting change, avoid overlap, and never stage its work.
- User-approved old-file removals occur only in their named slices after replacement/parity gates; never remove user
  diagrams, `.env`, or local Graphviz files.
- Use ordinary revert/corrective commits for rollback; no reset, force-push, history rewrite, or skipped hooks.
- Each committed slice keeps applicable tests green and records completion/deviations/verification/follow-ups in its
  `Outcome`.

## Immediate compatibility prerequisite

Before redesign implementation, deliver current context-backed workflow client compatibility as Epic 3 context group
Slice 12:

```text
Prompt namespace: context_backed_generation_workflow
Tool namespace:   context_backed_generation_workflow
```

Both registrations call one private renderer and return exact instruction parity. The compatibility tool is
model-callable, returns public host workflow instructions only, and does not inspect source, write files, call Azure,
apply readiness actions, replace bounded tools, or expose internal prompts.

Plan and implementation touch only the current MCP/backend/active-doc/test owners listed in the compatibility
handoff. After its implementation commit, record the exact final pre-redesign code baseline.

The later redesign public cutover applies the same pattern:

```text
Prompt namespace: diagram_generation_workflow
Tool namespace:   diagram_generation_workflow
```

The old context workflow prompt and tool are removed together in that cutover.

## Phase 0 — Complete slice plan and active design promotion

No implementation code, including the compatibility bridge, begins until both Phase 0 document commits are complete.

### Phase 0A — Delivery and slice plan

1. Create one Epic 3 generation-redesign group and its `00-group.md`.
2. Update the Epic 3 `00-epic.md` slice plan and dependencies.
3. Create all 14 slice documents with purpose, background/design, included work, exclusions, target areas, exact
   dependencies, rollback boundary, exit criteria, previous/next slice, verification commands, and pending outcome;
   Slice 14 owns the full backend audit/remediation and final report.
4. Include the complete approved research/approval package and compatibility Slice 12 plan in the planning commit.
5. Update the current-state board to show planning/promotion as active without claiming implementation.
6. Audit the complete plan for scope, source owners, sequencing, atomic cutover, reversibility, evaluation seams,
   hidden-gold timing, destructive steps, final backend coverage, concurrent frontend ownership, and verification.
7. Address every plan-audit finding.
8. Commit only the audited generation-redesign planning/research/delivery package and owned status files; exclude and
   never stage the concurrently owned frontend agent's work.

Suggested plan commit:

```text
docs(generation): plan generation redesign delivery
```

### Phase 0B — Active design-document promotion

After the plan commit and still before any compatibility or redesign code:

1. Reconcile research `01`–`13` once into active product, architecture, MCP, generation, validation, canonical schema,
   answer-key, evaluation, testing, environment, and decision owners.
2. Add/update all approved decisions in `decision-decisions.md`.
3. Replace the active evaluation stub with the approved deterministic matcher, evaluation-judge/report-analyst,
   run/gate, and leakage design.
4. Update the active MCP contract to document dual prompt/tool workflow discovery and the atomic unified cutover.
5. Promote one `AZURE_OPENAI_DEPLOYMENT` for all chat roles plus explicit
   `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`; never edit or inspect `.env`.
6. Update active intended design in present tense; keep implementation/runtime status only in board/slice outcomes.
7. Audit active docs for one owner per topic, coherent terminology/IDs/defaults, complete promotion coverage, no stale
   old tool/schema/layout/eval claims, and no active document using research as runtime authority.
8. Address every promotion-audit finding and run link/stale-term checks plus `git diff --check`.
9. Commit only the audited active design promotion, environment example, and decision changes.

Suggested promotion commit:

```text
docs(generation): promote generation redesign
```

Only after both commits pass their audits does compatibility Slice 12 implementation begin. Record its implementation
commit as the pre-redesign code baseline, then execute redesign Slices 1–14.

Promotion map:

| Topic | Active owner |
| --- | --- |
| Authority scenarios/mode boundary | Product requirements/scenarios and generation design |
| Dual prompt/tool unified workflow and bounded tools | `docs/01-architecture/03-mcp-tools/` |
| Backend stages/services/errors/capture seam | Backend architecture |
| Direct/context generation/repair/review/PyGraphviz | Generation design |
| Deterministic versus semantic validation | Validation design |
| Minimal canonical metadata and origins | Diagram JSON schema design |
| Twelve fixtures/set manifests | Answer-key generation design |
| Evaluation matcher/judge/gates/reports/leakage | Evaluation design and testing strategy |
| Deployments/defaults/safety bounds | Development environment reference |
| Decisions | Active decision log |
| Runtime status/history | Current-state board and slice outcomes only |

Active docs describe the coherent intended final system in present tense and do not link to research as runtime
authority. Research receives a final ownership map only after implementation verification.

## Neutral generation-observer seam

Generation must not import evaluation modules. Slice 1 establishes a bounded immutable observer protocol:

```text
GenerationObserver
  on_stage
  on_provider_call
  on_candidate
  on_result
```

Normal generation uses a no-op observer. Runtime diagnostics and offline evaluation implement separate observers.
This makes capture/version seams part of generation implementation rather than a later retrofit.

## Redesign slice plan

### Slice 1 — Contract and Observer Foundation

Purpose: establish new schema/contract/version infrastructure and neutral observability without public behavior change.

Included:

- generation, repair, review, result, trace, debug, example, evaluation foundation schemas;
- namespace-first IDs and registry accessors;
- Python contract values;
- prompt/profile/rubric/example/layout identities;
- generation observer/no-op and bounded stage/provider/candidate/result events;
- operation code registry additions.

Exit:

- valid/invalid schema fixtures and registry tests pass;
- duplicate IDs/kinds/paths are impossible;
- observer is generation-owned and evaluation-neutral;
- public current contracts remain unchanged.

Rollback: revert Slice 1 implementation commit.

### Slice 2 — Request Persistence Foundation

Purpose: implement internal direct/context request persistence and lifecycle.

Included:

- direct request schema/validator;
- renamed context request contract;
- shared `.graphpilot/requests/` service/path;
- complete expected-digest replacement;
- immutable mode/request ID/diagram name;
- finalized-after-success behavior;
- explicit old-artifact rejection and no automatic migration.

Public current MCP surface remains until Slice 9.

Exit: direct/context create/replace/conflict/identity/finalization/path-safety tests and full backend gate pass.

Rollback: revert Slice 2; no public caller used the new path yet.

### Slice 3 — Strict Logical Schemas, Packets, and Prompts

Purpose: implement exact model-facing V1 contracts internally.

Included:

- direct/context generation inputs;
- six mode/type logical output schemas;
- canonical JSON user-message builders;
- exact generation/repair prompt snapshots;
- diagram-model profile injection;
- strict `json_schema` only and no fallback in new clients;
- 16 MiB packet / 8 MiB response ceilings;
- provider error classification.

Exit:

- each schema admits only its core vocabulary/fields;
- direct rejects origins, context requires them;
- unsupported strict output has one call and typed error;
- packet/digest/version tests pass;
- initial packet requires exactly two examples;
- full backend gate passes.

### Slice 4 — Twelve Training Fixtures

Purpose: replace old model-visible examples with the approved complete fixture/set design.

Included:

- six direct and six context source fixtures;
- six ordered set manifests;
- deterministic input/output derivation;
- canonical/PyGraphviz-ready output and render gallery proof;
- distinct author/reviewer metadata/sign-off;
- old runtime training examples removed after specific destructive confirmation.

Exit: exact topology/fields/origins/core vocabulary, manifest order/digests, no identity leakage, and all validation/
render tests pass.

Rollback: revert fixture/set commit; do not partially mix sets.

### Slice 5 — Pre-Layout Pipeline and Deterministic Repair

Purpose: split semantic preparation from layout and remove silent semantic mutation.

Pipeline:

```text
strict response
→ normalized logical candidate
→ deterministic graph/provenance checks
→ explicit bounded repair
→ accepted pre-layout candidate
```

Included:

- no silent semantic type/direction/endpoint coercion/drop;
- mode-specific repair contracts/prompts;
- default one repair round, allowed `0..2`;
- no examples in repair;
- observer events at every stage;
- typed budget-exhaustion errors.

Exit: duplicate/endpoint/topology/multiplicity/provenance issues and repair success/failure are covered; unchanged
rerolls are impossible; full backend gate passes.

### Slice 6 — Semantic Review, Reviewed Default, Trace, and Debug

Purpose: implement production/default reviewed generation.

Included:

- shared rubric schema/rating scale and source layers;
- six composed final rubrics;
- direct/context adapters;
- strict private review response and response-contract repair;
- deterministic score/findings/actions;
- semantic candidate repair;
- `reviewed` default; `standard` explicit diagnostic/ablation only; no automatic fallback;
- compact MCP generation/quality summary;
- optional `.gp.trace.json`;
- optional numbered diagnostics;
- minimal canonical request/manifest refs and context origins;
- observer captures.

Exit: 18 visible clean/warning/block cases, score/gate boundaries, host routing, no blocker save, sidecar/debug matrix,
clean canonical output, full backend and affected frontend gates.

### Slice 7 — PyGraphviz Integration and Parity

Purpose: add/test the final engine without removing current engines.

Included:

- pinned `pygraphviz==2.0`;
- `PyGraphvizLayoutEngine` with process-local full native lifecycle lock;
- bottom-left points/bounding-box to top-left conversion;
- containment, direction, spacing, parallel edges, trace identity;
- current engine remains active only for parity during this slice.

Exit: malformed/nonfinite/close-on-error, repeatability, 256-node, 10-thread, gap/no-overlap, containment, parallel
edges, all fixture galleries, platform/wheel, and canvas/SVG parity proof.

Rollback: remove new engine/dependency; current engine was not removed.

### Slice 8 — PyGraphviz Cutover and Old-Engine Removal

Purpose: switch to one layout algorithm and remove old implementation.

Included after parity proof and specific removal confirmation:

- PyGraphviz only;
- no fallback;
- remove subprocess Graphviz, Grandalf, `GRAPHVIZ_DOT_PATH`, portable setup, old tests/docs/dependency;
- typed unavailable/layout failures.

Exit: repeat Slice 7 gates plus full backend/frontend verification; no old symbol/config/doc remains.

Rollback: revert Slice 8 atomically to the prior verified parity commit.

### Slice 9 — Atomic Public MCP and Schema Cutover

Purpose: replace the public surface in both MCP namespaces and all cold-turkey IDs/paths.

Before:

```text
context_backed_generation_workflow prompt + tool
old request/tool/schema IDs
```

After:

```text
diagram_generation_workflow prompt + tool
diagram_request_save
diagram_generate_direct
diagram_generate_from_context
new IDs/paths/results only
```

Included:

- one private unified workflow renderer and prompt/tool parity;
- tools-only “call this first” description;
- direct/context routing and trace/debug propagation;
- shared request save and new result transport;
- remove old prompt/tool from both registries;
- old IDs/paths fail explicitly;
- active docs/tests cut over together;
- minimal frontend canonical adapter/type updates where needed.

Exit: prompt/tool registries/schema parity, direct/context fake E2E, no internal prompt exposure, real stdio smoke, old
surface absence, and full backend/frontend gates.

Rollback: dedicated atomic revert of all public registrations/adapters/docs/tests; no alias or partial rollback.

### Slice 10 — Evaluation Foundation and Capture Pipeline

Purpose: implement evaluator contracts/storage/capture using the generation observer.

Included:

- visible case/oracle/run manifest/observation/deterministic-report contracts;
- safe artifact storage/resume identity;
- final semantic projection;
- evaluation capture observer;
- complete generated/blocked/error observations;
- required explicit dry/live execution mode contract.

No hidden gold.

Exit: schemas/storage/projection/resume/capture completeness and fake full-pipeline tests pass; generation remains
independent from evaluation imports.

### Slice 11 — Deterministic Matcher and Azure Embeddings

Purpose: implement reproducible concept alignment and hard grading.

Included:

- explicit `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`, no fallback;
- normalized text + vector cache keyed by deployment/model/content;
- aliases, embeddings, hard type filters, topology/field scores;
- deterministic maximum-weight one-to-one assignment/tie-breaks;
- ambiguity/extra inventory;
- activity/use-case/BDD/context mechanical graders.

Normal tests use fake embeddings and make no provider calls. Visible live embedding calibration is separate.

Exit: alignment/type/topology/assignment/ambiguity/metric boundary and gold-leakage tests pass.

### Slice 12 — Evaluation Judge, Metrics, Gates, and Report Analyst

Purpose: implement semantic/factual grading and certification assembly.

Included:

- evaluation judge/report analyst use the single configured `AZURE_OPENAI_DEPLOYMENT` as independent blinded calls;
- strict blinded judge input/rubric/response;
- material fact assessments and one response-contract repair;
- per-observation metrics, case/six-cell aggregation;
- hard/category gates and human adjudication artifacts;
- one strict report-analysis call per completed run;
- authoritative JSON and human Markdown reports.

Normal tests use `FakeLLMClient` only.

Exit: facets/refs/facts/blinding, scores/gates, false-pass/block/repair metrics, report evidence citations, analyst failure
isolation, and pass/fail/not_run tests pass.

### Slice 13 — Runner, Visible Calibration, and Leakage Proof

Purpose: provide safe explicit execution and freeze readiness.

Included:

- required `executionMode=dry_run|live`, no default;
- immutable manifests and strict resume;
- reviewed-only required condition and three repetitions;
- optional standard/historical manifests only;
- visible matcher/judge/report calibration fixtures;
- calibration report and threshold freeze artifact;
- leakage validator/freeze manifest;
- no hidden case content.

Exit:

- omitted mode fails;
- dry mode has zero provider calls;
- fake live executes only manifest observations and resumes without duplicates;
- no auto-expansion/rerolls;
- visible calibration/report schemas work;
- gold paths/content cannot reach generator input/workspace;
- full backend gate passes.

### Slice 14 — Full Backend Audit and Release Gate

Purpose: audit the complete backend after all redesign/evaluation slices, remediate every evidence-backed defect, and
produce the final offline implementation report.

Included:

- schema/registry/version and strict-contract audit;
- MCP prompt/tool discovery, transport, public-surface, and stale-ID audit;
- request persistence, path containment, atomicity, identity, and digest-concurrency audit;
- generation packet/bounds/provider/repair/review/provenance/diagnostics audit;
- PyGraphviz lifecycle/locking/failure/repeatability/concurrency/geometry audit;
- evaluation capture/matcher/cache/judge/gates/resume/report/leakage/provider-safety audit;
- dependencies/configuration/dead-code/documentation/test-gap audit;
- bounded independent subsystem reviews plus primary consolidation;
- reproduce, regression-test, and root-cause-fix every accepted finding;
- complete offline backend suite, stdio smoke, applicable frontend verification, stale searches, outcomes, and summary.

Exit:

- no unresolved blocker/important backend finding;
- every accepted defect has reproduction, regression coverage, fix, and verification;
- no live provider call, hidden gold, `.env` access, push, or production promotion;
- final report lists baseline/resulting commits, slices, changes, commands/results, audit findings/fixes, removals,
  deviations, remaining gates, and exact next steps.

## Verification matrix

Every backend implementation slice runs focused tests followed by:

```powershell
cd backend
uv run python manage.py test
```

Any frontend-affecting slice runs:

```powershell
cd frontend
npm run verify
```

Every slice also runs `git diff --check`, stale identifier/symbol/doc searches appropriate to its cutover, and the
implementation audit before commit. Provider-dependent checks remain explicit and are never part of default tests.

## Rollback model

- Exact final pre-redesign baseline commit is recorded after compatibility Slice 12.
- Every slice records direct revert dependencies and affected local artifacts.
- Public cutover and PyGraphviz removal have dedicated atomic revert plans.
- No history rewrite or destructive checkout is used.
- No existing local artifact is silently rewritten/deleted; old IDs fail explicitly after cutover.
- Production remains uncertified until frozen reviewed-mode hidden gates pass even though implementation occurs on
  `master`.

## Post-implementation certification

After Slice 14 and the final offline report:

1. run visible offline and separately authorized live calibration;
2. fix framework defects only with visible cases;
3. freeze generator/evaluator identities/thresholds;
4. independent authors/reviewers/adjudicators seal 48 built-in and RepoBench golds;
5. run explicit live reviewed certification (48 × 3);
6. complete required adjudications and report analysis;
7. require every hard/category gate;
8. request separate production-promotion authorization.

## Stop conditions during unattended execution

Pause and ask the user before:

- deleting/renaming any file or directory outside the specifically approved superseded artifacts recorded in
  `migration-plan-approval.json`;
- modifying `.env` or resolving authentication/permission problems;
- any live Azure evaluation/embedding/judge/report call;
- hidden-gold authoring;
- pushing;
- destructive Git operations;
- production promotion;
- a newly discovered material design contradiction.

Continue autonomously through ordinary implementation defects/test failures using the approved per-slice workflow.
