# Slice 01: Repository Responsibility Audit

## Purpose

Audit the complete tracked repository, its consumers and dynamic entry points, then freeze the narrowest behavior-preserving target architecture and exact migration/rollback map for Block 2.

## Background

Preflight verified clean `master` at `4b8a6af1a81e4014078dd453f8ba15a6ff78edb8`, no active writer/lock/listener/browser session, and the accepted Block 1 package: 19 terminal observations, 16 generated, one blocked, two expected errors, zero quality/recovery failures, two passing browser artifacts, report `sha256:c3e3ded…b9e`, and compatibility key `sha256:d77f21…ebd1`. No provider call occurred.

The audit used the current source, canonical owners, Git-tracked inventory, graph navigation, LSP references, and three independent read-only investigations. Generated relationships were confirmed against source. Delegate suggestions to delete S15/leakage code, merge provider-event contracts, or introduce common artifact/report bases were rejected because live consumers, differing contracts, or the no-deletion envelope contradicted them.

## Repository Inventory

All **833 tracked files** are covered by the ownership groups below: backend 454, docs 261, frontend 112, and six root control/setup files. `keep` includes current behavior and ownership; `update` means only current navigation/file maps change with the selected moves.

| Area | Evidence and current consumers | Dynamic entry/lifecycle | Disposition | Compatibility / rollback |
| --- | --- | --- | --- | --- |
| Root `AGENTS.md`, `README.md`, requirements, Python pin, Git controls | Agent entry, human quickstart, pinned runtime/dependencies | setup/tooling | Keep | no dependency/config change |
| `.devin/rules/` | workflow conventions; ignored weekend state is operational only | agent configuration | Keep | no canonical status duplication |
| `docs/00-*` | product authority and scenarios | human/agent documentation | Keep | no product behavior change |
| `docs/01-architecture/` | system/backend/frontend/MCP/API owners | canonical architecture | Update backend navigation only | revert docs with move commits |
| `docs/02-design-and-features/` | schema, generation, readiness, evaluation, workflow-audit owners | canonical behavior | Keep; add one repository-boundary decision only if implementation changes ownership | contracts unchanged |
| `docs/03-development-and-delivery/` | environment/testing/plans/status | delivery authority | Update plan, test map, Outcomes, status | history remains in Outcomes |
| `docs/research/`, `docs/archive/` | non-authoritative history/rationale | historical | Keep | no promotion or rewrite |
| `backend/manage.py`, `graphpilot/settings.py`, URL/ASGI/WSGI | Django launch/configuration | Django discovery | Keep | no environment change; `.env` uninspected |
| `backend/api/views.py`, `api/urls.py` | React HTTP load/save/resolve/list/validate/render | Django route registration | Keep | exact REST contract unchanged |
| `operations/management/commands/` | operator-only audit/evaluation/calibration/gallery/deployment commands | filename/class-based Django discovery | Keep locations; update two internal imports | command names/arguments unchanged |
| `backend/mcp_server/server.py` | 13 tools and one prompt over shared services | FastMCP decorators, stdio | Keep | exact public discovery unchanged |
| `mcp_server/workflow_audit_server.py` | provider-free audit stdio adapter | one explicit `importlib` path | Keep location; update target string in S02 | same executable/protocol |
| `services/`, `catalog/`, `support/`, `core/`, `llm/` | leaf DTO/catalog, neutral I/O/schema/provider, canonical persistence/validation/render | direct imports only | Keep | no abstraction/dependency change |
| `services/readiness/` | rubric/policy/reviewer/result/calibration/diagnostics | MCP/generation/commands by injection | Keep | existing provider/validation callbacks are Block 3 inputs |
| `services/generation/` | direct/context orchestration, observer, strict calls/repair/review/layout | MCP and evaluation observer injection | Keep | generation imports no evaluation implementation |
| `services/evaluation/` active generation evaluation | capture/matcher/judge/gates/runs/reports/freeze | operator commands only | Keep at root after outliers move | no serialized/path behavior change |
| `services/workflow_audit_*` plus facade | Block 1 scenarios/capture/client/store/run/browser/report/ledger | command + dynamic stdio audit adapter | Move/rename into `workflow_audit/` | exact atomic import migration; revert commit |
| `services/evaluation/full_effort_*` | frozen S15 cases/manifest/runner/report/analysis | historical command only | Move/rename into `historical/full_effort/` | no terminal identity/artifact access; revert commit |
| `graphpilot/schemas/` | 58 versioned runtime/evaluation schemas via `SchemaRegistry` | fixed registry paths/IDs | Keep | moving would alter asset digests/compatibility |
| `graphpilot/prompts/`, generation/readiness assets, blueprints | strict prompts/rubrics/training fixtures | validated loaders | Keep | no prompt/rubric/example change |
| `graphpilot/evaluation/workflow-audit/scenarios.json` | independent Block 1 scenarios | `WorkflowAuditScenarioService` | Keep | scenario digest/key unchanged |
| `backend/tests/` non-evaluation | mirrored service/API/MCP/command coverage | Django recursive discovery | Keep | no test behavior change |
| `tests/evaluation/test_evaluation_*`, matcher/calibration tests and helpers | active generation-evaluation coverage | Django recursive discovery | Keep at root | no fixture/gold change |
| `tests/evaluation/test_workflow_audit_*` | Block 1 focused and equivalence coverage | Django recursive discovery | Move into mirrored `workflow_audit/` package | focused discovery gate + revert |
| `tests/evaluation/test_full_effort_*` | S15 reproducibility and terminal regression coverage | Django recursive discovery | Move into mirrored historical package | no S15 run execution + revert |
| `frontend/src/`, `public/`, standard configs/E2E | React editor, API client, canvas/SVG parity, browser smoke | Vite/Vitest/Playwright configs | Keep | frontend runtime untouched |
| `frontend/audit/`, `playwright.audit.config.ts` | input-bound Block 1 W22 proof | `npm run e2e:audit` | Keep | exact evidence schema/ports unchanged |
| `.graphpilot/` generated artifacts | ignored user/evaluation state, including accepted baseline | runtime output | Excluded/read-only | never moved/deleted/committed |

## Evaluation Classification

### Reusable capture, artifact, checkpoint, and metrics infrastructure

These active generation-evaluation modules remain together because their schemas and lifecycle are one consumer family: `evaluation_contracts.py`, `evaluation_capture_observer.py`, `evaluation_artifact_store.py`, `evaluation_observation_service.py`, `evaluation_runner_service.py`, and `evaluation_metrics_service.py`. They are kept, not generalized across workflow audit or S15; those systems deliberately use different manifests, terminal states, bounds, and reports.

### Reusable Block 1 workflow auditing

| Current module | Responsibility / consumers | Disposition / exact target |
| --- | --- | --- |
| `workflow_audit_contracts.py` | W01–W22 measurement/accounting used by capture/run/report | Move → `workflow_audit/contracts.py` |
| `workflow_audit_scenario_service.py` | validates/materializes independent scenario bundle for run/browser/report | Move → `workflow_audit/scenario_service.py` |
| `workflow_audit_capture_service.py` | bounded metric store, generation observer, host adapters | Move → `workflow_audit/capture_service.py` |
| `workflow_audit_client.py` | exact-delegation provider metadata + validation `{code,path}` capture; used by fake factory/equivalence tests and future diagnosis | Move → `workflow_audit/client.py` |
| `workflow_audit_fake_client.py` | provider-free readiness/generation scripts and production service factory; command stdio adapter | Move → `workflow_audit/fake_client.py` |
| `workflow_audit_artifact_store.py` | immutable manifest/observation/checkpoint/terminal/evaluated-workspace lifecycle | Move → `workflow_audit/artifact_store.py` |
| `workflow_audit_run_service.py` | exact 19-observation real-stdio scheduling/recovery/no-rerun | Move → `workflow_audit/run_service.py` |
| `workflow_audit_browser_service.py` | input-bound built-preview W22 execution/evidence validation | Move → `workflow_audit/browser_service.py` |
| `workflow_audit_report_service.py` | authoritative aggregation/findings/compatibility comparison | Move → `workflow_audit/report_service.py` |
| `workflow_audit_ledger_service.py` | append-only accepted baseline summaries | Move → `workflow_audit/ledger_service.py` |
| `full_workflow_audit_service.py` | thin `WorkflowAuditService` facade over scenarios/run service | Move+rename → `workflow_audit/service.py` |

All are **keep through move**, not combine/delete. The facade's stale filename is corrected only because its responsibility namespace now supplies the context. The nine matching test modules move to `tests/evaluation/workflow_audit/`; command/server/scenario/frontend asset locations remain fixed.

### Readiness diagnosis and proof support

`services/readiness/`, readiness schemas/rubrics/calibration fixtures/tests, `benchmark_readiness_effort.py`, and the workflow-audit client/store/run seams are kept. The current client captures safe terminal provider metadata and validation diagnostics without influencing calls; the artifact/run layers own persistence and no-rerun. Block 3 may extend a new diagnosis package only after its own audited plan. No readiness behavior moves in Block 2.

### Generation quality and certification

Keep at `services/evaluation/` root: `deterministic_matcher.py`, `embedding_cache_service.py`, `semantic_projection_service.py`, all `evaluation_*` modules, and `visible_calibration_service.py`. Their current consumers are `run_generation_evaluation`, `calibrate_generation_evaluation`, and their tests; generation imports none of them. Moving this coherent root into a third nested package is deferred as cosmetic churn.

### S15 historical package

| Current module | Responsibility / consumers | Disposition / exact target |
| --- | --- | --- |
| `full_effort_case_service.py` | frozen visible S15 cases; manifest/runner/command/tests | Move → `historical/full_effort/case_service.py` |
| `full_effort_manifest_service.py` | immutable H/M schedule/assets/call ceilings | Move → `historical/full_effort/manifest_service.py` |
| `full_effort_runner_service.py` | historical staged execution, artifact/checkpoint/terminal and offline proof | Move → `historical/full_effort/runner_service.py` |
| `full_effort_report_service.py` | stopped/complete bounded S15 report | Move → `historical/full_effort/report_service.py` |
| `full_effort_analysis_service.py` | frozen H/M decision and ranked-solution rules | Move → `historical/full_effort/analysis_service.py` |

The command remains discoverable for historical offline/reproducibility tests, but the weekend run never invokes a terminal S15 package. Five S15 schemas and all identity/digest values remain untouched. No deletion or archive conversion is authorized.

### Redundant or dead candidates

No production module is proven dead. `GRAPHPILOT_GENERATION_FEW_SHOT_COUNT` has one transition-only definition and no consumer, but deleting configuration is outside the selected architecture proof and remains deferred. Artifact-store bases, shared secret scanners, shared provider events, report hierarchies, generation-service splits, and frontend reorganizations are also deferred: each either joins different contracts, changes semantics, or lacks a current failure beyond navigation.

## Dynamic Entry-Point and Consumer Closure

| Entry/consumer | Required migration |
| --- | --- |
| `run_workflow_audit.py` | five imports to `services.workflow_audit.*` |
| `workflow_audit_server.py` | dynamic string to `services.workflow_audit.fake_client` |
| workflow-audit implementation | all internal absolute imports to new package paths |
| workflow-audit tests and management test | imports, patch targets, and source-inspection assertions |
| `run_full_effort_evaluation.py` | three imports to `services.evaluation.historical.full_effort.*` |
| S15 implementation | internal absolute/lazy report imports to historical package |
| S15 tests and command test | imports and patch targets |
| `SchemaRegistry`, schemas, scenario loaders | no path change |
| MCP public server, Django API, frontend | no dependency on moved implementation paths |

Search and graph evidence confirm zero `services.evaluation` import in production `generation/` or `readiness/`; the only MCP-side evaluation import is the explicit workflow-audit dynamic adapter. Django API imports evaluation only through operator commands.

## Design Decision

**Recommendation:** move only the operational workflow-audit family and S15 family into lifecycle-owned namespaces; leave active generation evaluation at the root and all contracts/assets/public entry names unchanged.

**Strongest alternative:** move all three families into symmetric `workflow_audit/`, `generation_quality/`, and `historical/full_effort/` packages. **Decisive trade-off:** after removing the two outliers, the root already has one lifecycle; moving it adds broad import/test churn without a new consumer or seam.

**Unresolved risk:** Python move churn can miss a dynamic import, patch target, or recursive test package. Exact stale searches, compile/test discovery, focused gates, full suite, and the compatible Block 1 rerun cover that risk.

**Smallest realistic proof:** complete S02 and S03 as independent import-only moves, then run the exact provider-free workflow audit with a new identity and compare under the unchanged compatibility key.

## Included Work

- Commit this evidence inventory and exact path map.
- Independent plan/design audit, correction, and re-audit.
- Freeze S02–S04 ownership, gates, rollback, and integration order.

## Not In Scope

- Production moves before the plan commit.
- Deletion, provider calls, behavior/configuration/schema changes, or S15 artifact access.

## Target Areas

- this Block 2 slice group
- current roadmap/epic/docs navigation and current-state board
- no production/test file until S02/S03

## Exit Criteria

- Every tracked area and evaluation module has a disposition, consumer/lifecycle owner, compatibility boundary, and rollback.
- Dynamic entries and exact migration paths are complete.
- Independent review has no unresolved critical, high, or medium finding.
- The audited plan is committed before implementation.

## Previous Slice

[`../01-workflow-audit-and-measurement/06-fresh-provider-free-baseline.md`](../01-workflow-audit-and-measurement/06-fresh-provider-free-baseline.md)

## Next Slice

[`02-workflow-audit-namespace.md`](02-workflow-audit-namespace.md) and [`03-historical-full-effort.md`](03-historical-full-effort.md) after this plan passes and commits.

## Outcome

**Status:** Complete. The audit classified all 833 tracked files by owner and all 38 evaluation production modules individually, confirmed direct/dynamic consumers against source, and selected the smallest complete structure: isolate the eleven reusable workflow-audit modules, quarantine five reproducible S15 modules under a historical namespace, and leave the now-coherent active generation-evaluation root in place. No production/schema/prompt/fixture/frontend behavior changed and no source deletion was approved.

**Audit:** Three bounded read-only investigations supplied navigation evidence; unsupported deletion/common-base/provider-event suggestions were rejected after source verification. The independent plan audit's two correction rounds resolved every high/medium finding. Final re-audit passed the exact migration map, DAG, ownership, initializers, command/dynamic/test discovery, docs, parity, security, and rollback design with no critical/high/medium defect.

**Verification:** Block 1 preflight matched the accepted manifest/report/browser/ledger/key and 19 terminal artifacts; all five new Block 2 docs have resolving relative links; `git diff --check` passed. No Azure call, S15 identity load/resume, `.env` access, dependency, deletion, push, or deployment occurred.
