# Slice 13: Runner and Visible Calibration

## Purpose

Provide the safe operator-triggered evaluation runner, exact immutable manifests, strict resume behavior, visible
calibration workflow, leakage proof, and freeze-readiness artifacts. Omitted execution mode can never call a provider,
and unattended implementation uses fake clients only.

## Background

Slices 10–12 provide captures, deterministic alignment, judge semantics, metrics, gates, and reports but do not authorize
or orchestrate execution. This slice turns those components into an explicit, reproducible run without making live
credentials an implicit switch.

Visible synthetic and human-labeled cases are the only permitted calibration material before freeze. Hidden built-in and
RepoBench golds are independently authored only after the generator, matcher, judge, analyst, thresholds, schemas,
prompts, and versions are frozen. There is no hidden pilot.

## Design

- Require `executionMode: dry_run|live` on every runner invocation. There is no default, environment-derived mode,
  credential-derived mode, interactive “yes,” or fallback. Missing/unknown mode fails before provider construction,
  run creation, or canonical workspace mutation.
- `dry_run` validates visible case/oracle sets, configuration, deployment availability by shape (not network), versions,
  repetitions, conditions, output paths, expected calls, and resume policy. It constructs no Azure chat/embedding client,
  performs zero provider calls, does not certify, and reports `not_run`.
- `live` authorization applies only to the exact manifest written immutably before the first provider call. The runner
  may execute only its ordered case/repetition/condition observations and may not expand cases, repetitions, standard or
  historical conditions, models, or repair budgets automatically.
- Resume by unique run/case/repetition/condition identity. A completed observation is never duplicated; an incomplete
  observation resumes only through its explicit stage policy; failed/blocked observations remain final evidence and are
  never rerolled for a better result. Manifest, case-set, code, deployment, control, or version mismatch aborts rather
  than forking under the same run ID.
- Make reviewed mode the only required certification condition with exactly three repetitions per case. Any standard
  ablation or historical baseline is informational and requires its own separately authorized manifest; it cannot share
  observations or control reviewed certification.
- Calibrate framework machinery only with visible pools: synthetic unit/integration cases, human-labeled matcher cases,
  visible embedding-threshold cases, visible judge/fact cases, and visible report-analysis cases. Calibration reports
  distinguish fake/offline proof from separately authorized provider evidence and cannot certify generation quality.
- Generate a versioned threshold/freeze-readiness record containing the exact commit, case-set digests, one shared chat
  deployment identity (`AZURE_OPENAI_DEPLOYMENT`), explicit embedding deployment identity
  (`AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`), prompts, schemas, profiles, examples, rubrics, matcher/gate versions,
  controls, thresholds, visible-calibration evidence, and leakage result. A final freeze may be emitted only when all
  approved visible prerequisites are measured; otherwise status remains truthfully not run/not ready.
- Add a leakage validator that traces case/oracle loading, generation-packet assembly, observer boundaries, workspace
  files, provider payloads, caches, reports, and logs. Gold is evaluator-only: generation receives the question/authority
  packet and never an oracle path/content/digest/ID. Visible fixture access does not weaken the same boundary later used
  for hidden material.
- Use `AZURE_OPENAI_DEPLOYMENT` for all chat roles and the explicit evaluation embedding deployment for embeddings. The
  manifest records the shared-chat-role caveat and exact effective controls; secrets are never persisted.
- During this unattended slice, run only fake `live` simulations and offline visible calibration. No real Azure chat or
  embedding call is authorized while the user is away; any provider-backed visible calibration remains `not_run` until
  separately invoked with explicit authorization.

## Plan Audit

- **Safety gate:** omitted/invalid mode must fail before credentials are read or any provider client is constructed.
  `dry_run` has a zero-provider-call assertion at both runner and transport seams. No convenience default may be added.
- **Manifest gate:** live authorization is scoped to one prewritten immutable manifest. Canonical digests cover ordered
  case IDs, repetitions, conditions, commit, deployments/models/controls, all versioned assets, repair budgets, matcher/
  gate identities, output root, and resume policy.
- **Resume gate:** crash points before/during/after calls and writes, duplicate process attempts, corrupt partial files,
  completed errors, and manifest drift have explicit tests. Resume never duplicates a completed observation, silently
  skips a required one, or rerolls a failure.
- **Calibration-truth gate:** fake/offline, visible provider-backed, freeze-ready, hidden-certified, and production-
  promoted states remain distinct. In the absence of authorized live visible evidence, the implementation may pass
  offline gates but must not claim a provider-calibrated freeze.
- **Leakage gate:** committed fixtures are visible only and tests use unique sentinel strings/paths. No hidden-gold file,
  placeholder masquerading as hidden gold, or hidden outcome is created or consumed.
- **Deployment gate:** one `AZURE_OPENAI_DEPLOYMENT` serves every chat role; embeddings require
  `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`. Neither has a role-specific or cross-role fallback, and dry-run does
  not test connectivity.
- **Cost/control gate:** planned/actual calls, tokens, stage latency, and effective controls are captured, but no cost or
  latency pass gate is invented. Automatic condition expansion or provider retries beyond the owning bounded policy are
  forbidden.
- **Reversibility and verification:** rollback is an ordinary revert; immutable non-canonical run artifacts remain
  versioned historical evidence and are never silently migrated/deleted. Fake runner integration, leakage, resume, and
  full offline backend checks precede commit.

Plan audit result: **Pass.** The audit confirmed mandatory dry/live mode with pre-client failure, immutable manifest authorization, exact crash-safe resume, reviewed three-repeat scope, visible-only calibration, truthful freeze readiness, end-to-end leakage proof, fake live simulations, and no unattended provider call.

## Included Work

- Operator runner/management-command surface with required explicit dry/live mode and strict argument validation.
- Immutable run-manifest creation, exact authorization boundary, bounded artifact layout, and status reporting.
- Observation scheduler for reviewed three-repeat runs and separately manifested optional standard/historical runs.
- Crash-safe exact resume, duplicate suppression, lock/ownership behavior, mismatch rejection, and conservative terminal
  error handling.
- Dry-run planning for cases, repetitions, roles/deployments, versions, expected call ranges, artifacts, and resume.
- Visible synthetic/human-labeled matcher, embedding, judge, fact, and report-analysis calibration fixtures and reports.
- Threshold/freeze-readiness artifact assembly with exact identities and truthful prerequisite state.
- End-to-end leakage validator and sentinel tests across generator input, observer, workspace, caches, reports, and logs.
- Fake chat/embedding `live` simulations proving scheduling, capture, grading, reports, and resume without network access.
- Active evaluation, environment, testing, backend, operator, and decision documentation updates required by the runner.

## Not In Scope

- Any real Azure generation, readiness, semantic-review, judge, report-analysis, or embedding call during unattended
  implementation.
- Hidden built-in or RepoBench gold authoring/review/adjudication, a hidden pilot, or hidden certification.
- Claiming the generator/evaluator frozen when required visible provider calibration has not been explicitly run.
- Weakening gates after seeing hidden outcomes, automatically rerunning failures, or expanding a manifest.
- Production promotion, deployment, or user-facing runtime evaluation.
- Reintroducing the removed DOE runner or retaining the old generator as a runtime baseline.

## Target Areas

- runner, scheduler, resume, calibration, freeze-readiness, and leakage modules under `backend/services/evaluation/`
- operator command entry points under `backend/operations/management/commands/`
- evaluation run/calibration/freeze schemas and visible assets under `backend/graphpilot/`
- safe run-artifact storage under `backend/services/shared/`
- fake chat/embedding seams and tests under `backend/services/llm/` and `backend/tests/evaluation/`
- active backend/evaluation/environment/testing/operator documentation and local-artifact ignore rules as required

## Exit Criteria

- Omitted/invalid execution mode fails before provider construction or output mutation; `dry_run` performs zero provider
  calls, validates the exact plan/resume behavior, and reports `not_run` rather than pass.
- Fake `live` runs write the immutable manifest before calls, execute exactly the ordered observations, include blocked/
  error outcomes, and neither auto-expand nor favorably reroll.
- Crash/resume tests at every persisted stage avoid duplicate completed observations, reject identity/version/digest
  drift, and deterministically finish or fail incomplete runs.
- Required reviewed plans use exactly three repetitions; optional standard/historical conditions require separate
  manifests and cannot affect reviewed status.
- Visible matcher/embedding/judge/fact/report fixtures produce bounded calibration and threshold/freeze-readiness
  artifacts; unmeasured provider evidence remains explicitly not run/not ready.
- Sentinel leakage tests prove oracle content, paths, IDs, digests, vectors, and expected answers cannot reach generator
  packets, generation-role provider calls, evaluated workspaces, canonical diagrams, runtime traces, or logs.
- Configuration tests prove all chat roles use `AZURE_OPENAI_DEPLOYMENT`, embeddings use only
  `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`, and no fallback or secret persistence exists.
- No hidden-gold artifact is added and no real Azure call is made; fake clients cover all ordinary tests.
- Focused tests, the explicit evaluation `dry_run`, `cd backend; uv run python manage.py test`, real offline stdio smoke,
  stale runner/config searches, and `git diff --check` pass with exact results recorded before commit.

## Previous Slice

- [`12-evaluation-judge-and-gates.md`](12-evaluation-judge-and-gates.md)

## Next Slice

- [`14-backend-audit-and-release-gate.md`](14-backend-audit-and-release-gate.md)

## Outcome

**Completion:** Added `run_generation_evaluation` with a required positional `dry_run|live` mode, exact canonical
manifest/case-set inputs, separate control/evaluated workspaces, clean checked-out commit binding, and one shared chat plus
explicit evaluation-embedding deployment. `dry_run` validates without constructing provider clients or writing artifacts.
`live` writes the immutable manifest before lazy client construction and executes only the ordered reviewed three-repeat
schedule through isolated production direct/context generation, capture, ephemeral oracle-bearing matching, blinded judge,
metrics/gates, case/cell summaries, authoritative JSON/Markdown, and optional report analysis.

**Resume and safety:** Added exclusive run leases with conservative same-host stale reclamation; strict monotonic
checkpoints; immutable completed/blocked/error/uncertain terminals; lazy executor construction; completed-observation
terminal reconciliation; exact evaluator rubric/matcher/gate identity binding; and no reroll after executor/provider/report-
analysis uncertainty. Bounded canonical loaders verify question/oracle/context-evidence closure and reject case, order,
version, deployment, control, commit, digest, or schedule drift before provider construction. Secret-like persisted values
fail closed.

**Calibration, leakage, and readiness:** Added strict visible case-set/calibration/leakage/freeze schemas, a committed
visible synthetic six-area bundle, provider-free `calibrate_generation_evaluation`, and immutable calibration/freeze
persistence. Sentinel proof covers generation packets, observer captures, generation-role payloads, evaluated files,
traces, caches, generation reports, and logs while allowing evaluator-only post-generation judge authority. Offline proof
passes, but visible provider evidence and genuine human calibration remain `not_run`; freeze is therefore `not_ready`,
hidden certification `not_run`, and production `not_promoted`. No hidden fixture, fake hidden gold, real Azure call,
generation feedback path, or MCP/API/frontend surface was added.

**Verification:** The final read-only implementation audit passed after hardening case-schema checks, blocked/error
classification, lazy resume, checkpoint/terminal corruption handling, stale-owner identity/races, exact evaluator versions,
clean-commit binding, secret rejection, ephemeral embeddings, complete leakage prerequisites, context execution, and
report-analysis interruption. Focused evaluation/management tests passed **116** tests (1 skipped). The exact staged Slice
13 tree passed **845** backend tests (5 skipped), Django checks, real offline MCP stdio smoke, readiness check-only
calibration, visible evaluation calibration, Python compilation, and `git diff --cached --check`. A mixed working-tree run
correctly isolated one unrelated concurrent straight-route test expectation; the exact staged tree excluded those unstaged
connector edits and was fully green.

**Deviations:** Freeze output is named a freeze-*readiness* artifact rather than a final freeze manifest because required
visible provider/human evidence is absent. Gold-bearing embedding resolution defaults to ephemeral storage; persistent
content-bound cache behavior remains explicit visible-only machinery proof so oracle text, aliases, digests, and vectors
cannot enter caches.

**Follow-up:** Slice 14 performs the complete backend audit/remediation and offline implementation-release gate. Separate
human labels, explicit provider authorization, freeze approval, independently authored hidden gold, reviewed three-repeat
certification, adjudication, and production promotion remain required.
