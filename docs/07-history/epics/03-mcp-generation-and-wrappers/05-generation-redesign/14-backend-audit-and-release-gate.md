# Slice 14: Backend Audit and Release Gate

## Purpose

Perform the newly approved full backend audit after Slices 1–13, remediate every evidence-backed defect in scope, rerun
the complete offline verification gates, and publish one final release-readiness summary. This is a cross-cutting defect
and integration gate, not a semantic-certification or production-promotion claim.

## Background

The preceding slices replace backend contracts, persistence, generation, review, layout, MCP surfaces, and evaluation in
staged commits. Passing each local slice gate is necessary but can miss cross-slice defects, stale behavior, dependency
violations, or untested failure combinations. Slice 14 therefore re-audits the complete backend as one integrated system
after the final runner commit.

The audit is intentionally broader than a normal feature slice. It may remediate confirmed defects anywhere in the
backend and its owned contracts/tests/docs, while preserving unrelated work and leaving the concurrently owned frontend
untouched unless a separately coordinated public-contract correction becomes unavoidable.

## Design

Audit every tracked backend production module, schema/prompt/rubric/fixture asset, test package, management command, MCP
entry point/smoke client, project-owned backend dependency/configuration file, and backend-owned active document against
the promoted final design. Ignore local `.env`, caches, generated artifacts, and local provider/layout installations.
Record coverage and findings across all of these domains:

| Domain | Required audit coverage |
| --- | --- |
| Contracts and registries | Namespace-first IDs/kinds/paths, schema strictness/bounds, canonical serialization/digests, duplicate registration, version capture, result/error contracts |
| Configuration and providers | Startup validation, one `AZURE_OPENAI_DEPLOYMENT` for every chat role, explicit evaluation embedding deployment, strict structured output, limits/timeouts/reasoning controls, no fallback, fake-client injection, secret-safe errors/logs |
| Storage and persistence | Workspace containment, traversal/symlink/Windows path cases, bounded I/O, atomic/exclusive writes, digest conflicts, request finalization, run artifacts/resume, partial/corrupt files, no user-data deletion or silent migration |
| Context and readiness | Evidence/request validation, freshness/binding, preflight/projection, reviewer failure/repair, deterministic policy/actions, diagnostics, and separation from canonical validation |
| Generation semantics | Direct/context authority isolation, exact packets/examples, strict response parsing, deterministic conform/check/repair, budgets, unchanged-reroll prevention, reviewed default, semantic review/repair, blockers/no-write, trace/debug bounds |
| Provenance and delivery | Origin allowlists/support boundaries, context stability recheck, canonical validation, persistence ordering, render warnings after canonical commit, warning/error precedence, cleanup, and truthful terminal outcomes |
| PyGraphviz layout | Sole-engine/old-engine absence, native object lifecycle/close-on-error, process-local locking, repeatability, scale, geometry/containment, parallel edges, malformed/non-finite data, cross-platform failure classification |
| MCP/API/commands | Thin adapters, prompt/tool byte parity, exact new registrations/schemas, old-surface absence, `OperationProblem`/`isError`/HTTP mapping, stdio behavior, argument bounds, explicit dry/live command safety |
| Evaluation separation | No generation-to-evaluation imports, observer immutability, capture completeness, projection, fake embeddings/LLMs, matcher determinism, judge blinding, backend gates, reports, resume, and visible-gold leakage firewall |
| Security and resilience | Size/count ceilings, malformed/untrusted inputs, concurrency/races, resource cleanup, bounded diagnostics, no secrets/raw hidden reasoning, provider/network tripwires, deterministic fail-closed behavior |
| Tests, dependencies, and docs | High-value negative/boundary/integration coverage, dead/stale code and dependencies, old IDs/config/docs, package/import direction, README/environment/testing/architecture parity, exact offline commands |

Use one evidence-backed finding ledger during execution. Each finding records domain, severity/materiality, exact file and
line, expected versus observed behavior, minimal reproduction, affected contracts, root cause, remediation, regression
test, and verification result. Do not report or fix speculative defects from pattern matching alone.

For every confirmed in-scope defect:

1. add or identify the smallest reliable failing regression;
2. fix the root cause without weakening a contract, gate, type, or safety control;
3. update the canonical owner when behavior/configuration/contracts change;
4. run focused checks;
5. audit the remediation diff for parity, regressions, stale/dead paths, and missing tests; and
6. rerun the affected domain plus the complete final gate.

If evidence exposes a material unresolved product/architecture decision, stop rather than guessing. Non-material
refactoring or cleanup is allowed only when required to remove a proven stale/dead replacement path or make a confirmed
fix safe; this slice is not license for aesthetic rewrites.

The final release gate has two distinct statuses:

- **backend implementation readiness:** may pass when this full offline audit has no unresolved material finding and all
  required checks pass; and
- **semantic/production readiness:** remains `not_run`/not promoted until separately authorized visible provider
  calibration, freeze, independent hidden-gold authoring, three-repeat live reviewed certification, adjudication, and
  production-promotion approval occur.

## Plan Audit

- **Completeness gate:** the audit inventory must account for every tracked/project-owned file and domain in `backend/`,
  backend dependencies/configuration examples, and backend-owned active docs. Local ignored secrets/artifacts are excluded;
  sampling only changed files or Slices 10–13 is insufficient.
- **Evidence/remediation gate:** every finding needs a reproducible defect or concrete contract/test/doc inconsistency.
  Every confirmed material backend defect is remediated in this slice with regression coverage; no warning is suppressed,
  test weakened, or failure reclassified merely to pass the gate.
- **Cross-slice gate:** explicitly trace direct and context workflows from MCP entry through storage/readiness/generation/
  review/layout/validation/persistence/render, and trace evaluation from runner through observer/capture/matcher/judge/
  gates/reports/resume. Audit terminal errors and generated outcomes with post-operation warnings, not just happy paths.
- **Provider/leakage gate:** all ordinary audit checks use fake embeddings and fake LLM clients. Omitted execution mode
  must remain incapable of a live call. No real Azure call, hidden-gold artifact, hidden pilot, or fabricated calibration
  evidence is permitted while the user is away.
- **Ownership gate:** generation remains evaluation-neutral; adapters remain thin; canonical design owners remain the
  authority. Frontend files and concurrent frontend changes are not modified or staged. A discovered required frontend
  contract change is reported and coordinated rather than silently taken over.
- **Destructive-safety gate:** never edit `.env`, credentials, user diagrams/context/evaluation runs, local Graphviz
  files, or unrelated work. Already approved old-runtime removals should have occurred in earlier slices; this audit may
  remove only a proven stale tracked remnant, with replacement/parity confirmed and ordinary revert available.
- **Reversibility gate:** preserve the exact Slice 13 baseline and use normal corrective/revert commits only—no reset,
  destructive checkout, force push, or history rewrite. Audit/remediation changes are staged by owned path only.
- **Release-truth gate:** passing offline implementation checks cannot be described as hidden semantic certification or
  production approval. Missing live calibration/certification remains explicitly `not_run` in reports and final summary.
- **Verification gate:** focused reproductions and domain checks are followed by Django system checks, the entire backend
  suite, real offline stdio smoke, readiness check-only calibration, evaluation dry-run, stale/dependency/import scans,
  applicable settled-tree frontend verification, and `git diff --check`. Any failure is resolved or truthfully reported
  as a blocker; it is never ignored.

Plan audit result: **Pass.** The audit confirmed complete tracked-backend/domain coverage, evidence-led findings and remediation, end-to-end direct/context/evaluation traces, fake-provider/leakage tripwires, frontend non-ownership, destructive/local-file safety, full offline gates, and strict implementation-versus-certification reporting.

## Included Work

- Capture the exact post-Slice-13 baseline, owned/dirty-path inventory, backend file inventory, and audit checklist before
  remediation.
- Review every domain and end-to-end path in the Design table, including negative, boundary, concurrency, interruption,
  post-operation warning, and resource-cleanup behavior.
- Maintain the evidence-backed finding ledger and severity/materiality classification.
- Reproduce, root-cause, and remediate every confirmed in-scope backend defect, with high-value regression tests and
  required canonical documentation/configuration updates.
- Remove confirmed stale/dead backend symbols, registrations, schemas, prompts, dependencies, config names, and docs
  left by the cold-turkey redesign only when their replacements and absence gates are proven.
- Re-audit the complete remediation diff and repeat affected-domain checks until no material finding remains.
- Run the complete provider-free release gate, including fake embedding/LLM evaluation and explicit dry-run safety.
- Record exact command output, test counts/skips, stale-search results, audit coverage, findings, remediations, deviations,
  and remaining external gates.
- Finish this slice's `Outcome` and the parent handoff with one final summary containing: baseline/end commits; domains
  audited; findings by severity and disposition; files/remediations/tests; exact gates/results; no-live/no-hidden proof;
  backend implementation readiness; semantic certification status; decisions/deviations; and next authorized actions.

## Not In Scope

- A frontend-wide audit or remediation, frontend feature work, or staging concurrently owned frontend changes.
- Real Azure generation/readiness/review/judge/report/embedding calls, live visible calibration, or live certification.
- Hidden built-in/RepoBench gold authoring, review, adjudication, sealing, or a hidden pilot.
- Production promotion, deployment, push, destructive Git operations, or history rewrite.
- Epic 4 `diagram_update`, optional RAG, authentication/database work, or unrelated backlog features.
- Speculative performance rewrites, dependency churn, broad style refactors, or cleanup without a demonstrated defect.
- Editing/deleting `.env`, secrets, user-owned workspace artifacts, or local provider/layout installations.

## Target Areas

- all backend production areas: `backend/api/`, `backend/mcp_server/`, `backend/services/`, and `backend/graphpilot/`
- all backend verification areas: `backend/tests/` and `backend/mcp_server/smoke_test.py`
- backend dependencies/configuration: `requirements.txt`, `backend/.env.example`, and relevant Django/runtime settings
- backend-owned active architecture, MCP, generation, validation, evaluation, environment, testing, and README owners
- this slice's `Outcome` and the live current-state board for truthful completion/external-gate status
- frontend verification only against a coordinated settled tree; no frontend file ownership in this slice

## Exit Criteria

- The final summary accounts for every audit domain and tracked/project-owned backend file area, with exact evidence and
  disposition for every finding; no confirmed material backend defect remains unresolved.
- Every remediation has a regression test or documented equivalent proof, its focused check passes, and the final diff
  audit finds no parity regression, stale/dead replacement path, weakened gate, or missing high-value test.
- Direct/context generation and evaluation end-to-end fake paths pass generated, generated-with-warning, blocked,
  provider/error, resume, and leakage scenarios while preserving generation/evaluation observer separation.
- All chat roles resolve only through `AZURE_OPENAI_DEPLOYMENT`; embeddings resolve only through
  `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT`; strict output/no-fallback behavior and effective identity capture are
  verified. Normal tests remain provider-free.
- Explicit execution-mode tests prove omission fails before provider construction, dry-run makes zero calls, fake live
  follows only its manifest, resume creates no duplicate, and gold cannot reach generation/workspace/logs.
- Stale searches find no removed public IDs, schemas, prompts, training paths, Grandalf/subprocess layout code or
  dependency, legacy deployment variables, re-export shims, or obsolete eval/DOE runtime paths except intentional
  migration/history assertions.
- Run and record the complete final gate from the appropriate directories:
  - `cd backend; uv run python manage.py check`
  - `cd backend; uv run python manage.py test`
  - `cd backend; uv run python mcp_server/smoke_test.py`
  - `cd backend; uv run python manage.py calibrate_readiness --json` (check-only, no `--live`)
  - the Slice 13 evaluation runner with explicit `dry_run` using its final promoted command contract
  - focused stale identifier/config/dependency/import and generation→evaluation dependency searches
  - `git diff --check`
  - `cd frontend; npm run verify` only after coordination if a settled public/canonical compatibility gate applies;
    do not modify or stage frontend files
- The eventual `Outcome` and final handoff include exact test counts/skips and command results, audit/remediation summary,
  deviations/follow-ups, and a clear split: backend implementation gate passed or blocked; provider-backed visible
  calibration, freeze, hidden certification, and production promotion remain separately authorized and `not_run`.
- No live provider call, hidden-gold work, secret/user-artifact modification, frontend ownership violation, push, or
  destructive Git operation occurred.

## Previous Slice

- [`13-runner-and-visible-calibration.md`](13-runner-and-visible-calibration.md)

## Next Slice

- No further implementation slice in this group. After a passing offline backend gate, the next milestones are separately
  authorized visible provider calibration and freeze, independent hidden-gold authoring, three-repeat reviewed live
  certification, adjudication, and production-promotion approval.

## Outcome

**Completion:** Audited the complete tracked backend and backend-owned active contracts/configuration/docs across all ten
planned domains. The post-Slice-13 backend baseline is `4f06163`; execution began from branch head `4173789` after the
concurrent frontend slices, left every frontend file untouched, and landed the audited remediation as `47eb948`.
Backend implementation readiness is **pass** with no unresolved material finding. Visible provider calibration, freeze,
hidden certification, adjudication, production promotion, and every real Azure call remain separately authorized and
`not_run`/not promoted.

**Finding ledger:** Eight evidence-backed findings were confirmed and resolved; there were no critical findings.

| Severity | Domain and observed defect | Root-cause remediation and regression proof |
| --- | --- | --- |
| Important | Configuration/provider contract drift: chat deployment silently defaulted, the compatibility call could weaken strict output and expose generic provider text, and readiness did not select the explicit bounded strict method. | Made chat deployment explicit, unified Azure/fake compatibility calls on the 8 MiB strict path with no `json_object` fallback, sanitized generic provider failures, and moved readiness to `generate_json_strict`; LLM/settings/readiness tests cover missing deployment, strict format, UTF-8 bounds, sanitization, and fake parity. |
| Important | `ContextPersistenceService` retained a second, weaker JSON 2 save/result/identity implementation after `DiagramRequestPersistenceService` became the canonical direct/context owner. | Removed the duplicate DTO, exception, write/digest helpers, adapter import, and stale callers; all request writes now pass through the shared discriminator/path/digest/identity/finalization service and its existing boundary suite. |
| Important | Concurrent first evidence promotions could both pass the pre-write digest check. | Serialized complete in-process JSON 1 promotions with one reentrant manifest-write guard; a two-writer regression proves one winner and one `ContextConflictError`. |
| Important | Context request save used a different lock from evidence promotion, leaving a manifest change window after validation/recheck and before request write. | Context request saves now hold the manifest guard inside the request-write guard; a deterministic regression proves request save cannot cross an active promotion boundary. Lock order is request then manifest, and evidence promotion never acquires the request lock. |
| Important | Live readiness calibration's counting wrapper lacked `generate_json_strict`, so an authorized live assessment would fail before its first provider call after the readiness cutover. | Added bounded strict delegation and changed the fake-live command regression to exercise/count that exact method; check-only still constructs no Azure client. |
| Important | An intentionally unconfigured direct generation emitted an observer event with an empty model before reaching `llm_not_configured`, causing a validation error and breaking real stdio smoke. | Normalize absent provider identity to the observer contract's `null` value in generation and semantic-review call events; service regression and real stdio smoke now prove the typed offline error. |
| Moderate | Generated post-commit warnings were not assembled in canonical execution order. | Persist trace before render and finalize diagnostics last; a three-failure regression proves `trace_write_failed`, `render_failed`, then `diagnostics_write_failed`. |
| Moderate | Three unreferenced pre-cutover prompt files retained obsolete workflow names, request paths, and `partial_success` semantics. | With explicit deletion approval, removed `context-backed-generation-workflow.md`, `context-generation.md`, and `context-generation-repair.md`; an absence test protects the active V1 replacements. |

**Audit coverage:** Contracts/registries and all 54 registered schemas; provider/configuration/strict transport; workspace,
evidence/request/diagram/run persistence; context/readiness; direct/context generation, provenance, review, repair, trace,
diagnostics, render, and terminal outcomes; PyGraphviz lifecycle/geometry/concurrency; MCP/API/management adapters and real
stdio transport; evaluation capture/matcher/judge/gates/reports/resume/leakage; security ceilings, path/race/resource/error
boundaries; all backend tests/assets/dependencies; and backend-owned architecture, environment, testing, and README owners.
Stale searches retain old names/IDs/paths only in explicit rejection/migration assertions. Generation has no evaluation
import; all schemas are registered; Grandalf, old layout/config selectors, role-specific chat settings, weak-format
fallbacks, duplicate request writers, and obsolete active prompts are absent.

**Verification:** `cd backend; uv run python manage.py test` passed **852 tests (5 skipped)**; `uv run python manage.py
check` reported no issues; and `uv run python mcp_server/smoke_test.py` passed all 13-tool, one-prompt, prompt/tool parity,
context lifecycle, render, and offline typed-generation checks. `uv run python manage.py calibrate_readiness --json`
returned `valid: true`, check mode, and truthful `releaseStatus: not_run`. The exact explicit-dry-run management-command
regression passed and proved omitted mode fails while `dry_run` constructs no provider or workspace artifact. Schema,
prompt, dependency, import-direction, and legacy-name scans passed with only intentional negative assertions.
`cd frontend; npm run verify` passed lint with 0 errors/warnings, production build/typecheck, **419** unit/component tests,
and **43** Chromium E2E tests; the existing non-failing chunk-size advisory remained. `git diff --check` passed and no
Playwright CLI session remained.

**Deviations:** No contract, product, or architecture decision changed. The fixed three-repeat/six-cell certification
shape remains intentional rather than being generalized during an audit. The final stdio gate found and drove the
additional empty-model observer fix before release. No `.env` or secret was inspected or modified; no user workspace,
hidden gold, live provider, frontend, Git history, or remote state was modified; no push occurred.

**Post-gate correction (`6f35e1e`):** A real Copilot host trial exposed that missing evidence status fingerprinted the
default `.` scope while save fingerprinted a narrower candidate scope, and that Python/virtual-environment/tool caches
could mutate the digest. Status now accepts an optional paired proposed source scope, echoes configured and effective
scope, rejects changed canonical scope, and applies deterministic built-in generated/cache exclusions. Included roots,
exclusion patterns, concrete-file locators, and the required `.gp-evidence.candidate.json` suffix are explicit in tool
schemas and byte-pinned workflow guidance. The reproduced status-to-save path, cache mutation, invalid path grammar,
backward-compatible omitted-scope path, and real MCP discovery/instruction flow are covered. Focused tests passed **103**
(1 skipped), the full backend passed **859** (5 skipped), Django checks and real stdio smoke passed, `git diff --check`
passed, no provider call occurred, and no frontend contract/file changed.

**Live-host correction (`23cb6e4`):** A real stdio MCP-client reproduction confirmed Azure rejected the complete
readiness schema before inference because `uniqueItems` and other canonical validation keywords are outside Azure's
structured-output subset. All eleven model-facing response schemas now pass through one deterministic provider projection
while complete canonical schema and semantic validation remain fail-closed locally; provider rejection has its own
non-retryable readiness transport instead of `reviewer_provider`. The live readiness call then returned `ready`, score
**100**, with no findings. Generation exposed and drove a second fix: context semantic repair now reuses the exact
review-authority projection rather than generation-only selected-claim payloads, and unexpected internal values are never
reported or leaked as `invalid_workspace`. The changed-code attempt generated `graphpilot-system-bdd` with **7 nodes**,
**9 edges**, clean reviewed score **100**, one semantic repair, zero warnings, canonical JSON/SVG/trace/full diagnostics,
and successful offline validate/render replay. The editor loaded all elements with zero console errors/warnings; initial
fit placing Workspace Storage under the minimap is an adjacent frontend-layout follow-up, not a generation failure. The
full backend passed **869** tests (5 skipped); real stdio smoke, Django check, check-only readiness calibration (`valid:
true`, `releaseStatus: not_run`), `git diff --check`, and independent implementation audit passed. No `.env` or secret was
inspected, printed, modified, or committed; no live certification/freeze occurred, no frontend source changed, and no push
occurred.

**Follow-up:** Plan Epic 4's `diagram_update` slices. Independently obtain human labels and explicit authorization before
visible provider calibration/freeze, hidden-gold authoring, reviewed three-repeat certification, adjudication, or
production promotion. Track initial editor fit/minimap occlusion as adjacent Epic 2 or Epic 4 usability work.
