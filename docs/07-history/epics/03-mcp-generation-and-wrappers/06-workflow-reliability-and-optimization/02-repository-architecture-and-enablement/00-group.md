# Block 2 Slice Group: Repository Architecture and Enablement

## Goal

Separate active operational workflow auditing, active generation evaluation/certification, and frozen S15 full-effort history at the repository boundary without changing runtime behavior, serialized contracts, provider policy, evidence, or performance. Give Block 3 one clearly owned reusable workflow-audit seam for safe provider/validation capture and terminal evidence.

## User Scenario

A future diagnosis agent can locate the current readiness services and the reusable workflow-audit capture/checkpoint/report stack without entering generation certification or accidentally treating S15's stopped package as an active experiment. Existing operator commands, MCP/REST behavior, schemas, outputs, tests, and the accepted Block 1 baseline remain valid.

## Authority and Baseline

- The [Block 2 owner](../03-block-02-repository-architecture-and-enablement.md) owns the question, parity invariants, outputs, and exit gate.
- The [shared success contract](../01-success-contract.md) owns workflow outcome, evidence, quality, and performance semantics.
- The [execution policy](../11-block-execution-and-parallelism.md) owns slice topology, isolation, integration, and failure rules.
- The accepted parity authority is baseline `baseline-workflow-audit-block1-baseline-20260724-01`, run `run-workflow-audit-block1-baseline-20260724-01`, report `sha256:c3e3dedaf412bf413c9bb517aadd5125b95f73f7c3771ad0beb7153ed4031b9e`, and compatibility key `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`.
- The implementation source baseline is clean `master` commit `4b8a6af1a81e4014078dd453f8ba15a6ff78edb8`; Block 1 code is commit `c1ea9d85fbcb043e014306894fa42d0bcacb52d2`.
- S15's terminal identities are historical and are not loaded, migrated, resumed, or rerun. Stage C remains closed.

## Audit Conclusion and Target Architecture

The repository audit covers all 833 tracked files by ownership group and every evaluation production module individually. Public/runtime packages, schemas, prompts, fixtures, API/MCP entry points, frontend runtime, and generated artifact paths already have coherent owners and remain in place. The confirmed structural defect is the flat `services/evaluation/` namespace mixing three independent lifecycles.

The narrowest complete target is:

```text
backend/services/evaluation/
  *.py                              # active generation quality/certification
  workflow_audit/                   # reusable Block 1 operational audit
  historical/
    full_effort/                    # frozen S15 package; reproducibility only

backend/tests/evaluation/
  test_*.py                         # active generation quality/certification
  workflow_audit/                   # mirrored operational-audit tests
  historical/full_effort/           # mirrored S15 reproducibility tests
```

Workflow-audit and S15 schemas retain their exact `graphpilot.evaluation.*` identities and filenames under `graphpilot/schemas/`. The approved workflow scenario bundle, frontend audit harness, Django command names, MCP audit server, artifact roots, and result contracts do not move. Internal Python imports move atomically with their defining modules; no compatibility re-export shim or dual path is introduced.

The strongest alternative is a symmetric third subpackage for all active generation-evaluation files. Its only remaining benefit after the two outlier lifecycles move is cosmetic symmetry, while it would add more than twenty file moves and most of the current evaluation import churn. Leaving the now-coherent generation-evaluation root in place is the decisive lower-risk choice.

The audit also rejected premature shared abstractions. Generation and readiness provider events differ in validation/version semantics; artifact stores, terminal records, reports, and secret checks have domain-specific contracts. Their similar mechanics do not justify a common base in this block. The workflow-audit capturing client remains inside the reusable operational-audit package and is the current Block 3 evidence seam.

## Scope

- Commit the repository responsibility, consumer, lifecycle, dynamic-entry-point, compatibility, migration, and rollback inventory.
- Move the eleven workflow-audit modules into one responsibility namespace and mirror their nine focused tests.
- Move the five S15 modules into an explicit historical namespace and mirror their three focused tests.
- Update every tracked import, dynamic import, source-inspection assertion, command consumer, current implementation map, and active canonical architecture/testing owner affected by those paths.
- Preserve Django management-command discovery, real-stdio audit-server loading, schema registry behavior, test discovery, generated paths, and all public/serialized behavior.
- Run focused gates per move, independent implementation audits, the full integration gate, and a new exact compatible provider-free Block 1 baseline comparison.

## Out of Scope

- Deleting any source, schema, fixture, command, historical package, or generated user artifact.
- Loading, migrating, resuming, or rerunning any terminal S15 identity or opening Stage C.
- Readiness prompt/schema/policy/result changes or a readiness root-cause conclusion.
- Generation behavior, provider controls, caching, performance optimization, MCP/REST/frontend behavior, or public names.
- A common artifact-store base, common report hierarchy, common secret scanner, provider-event unification, or a split of `DiagramGenerationService`.
- Moving stable schemas/prompts/fixtures merely to mirror Python package layout.
- Adding dependencies or compatibility shims.

## Execution Topology

```text
S01 Repository Responsibility Audit
  ├── S02 Workflow Audit Namespace
  └── S03 Historical Full Effort
          \        /
           S04 Integration Parity
```

S01 freezes the inventory, exact path map, target architecture, and invariants in the audited plan commit. S02 and S03 then consume only that committed design and have disjoint production, test, command, and dynamic-entry-point ownership. They are parallel-safe only in separate worktrees; the primary agent may execute them sequentially in the integration worktree to avoid concurrent filesystem moves. S04 waits for both commits and is the sole owner of shared canonical documentation, current-state, complete gates, the parity run, and the block exit handoff.

## Slice Concurrency and Ownership

| Slice | Depends on | Inputs | Outputs | Exclusive write ownership | Forbidden/shared ownership | Parallel with | Resources | Integration gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | accepted Block 1 | clean `4b8a6af`, canonical owners, source/reference audit | audited inventory, exact target and DAG | this group and S01–S04 plan docs; parent navigation/status only by primary integrator | all production/tests/schemas/artifacts | none | read-only source/graph/LSP; no ports or provider | plan/design audit and `git diff --check` |
| S02 | committed S01 | frozen workflow-audit path map and baseline | `services/workflow_audit/`, mirrored tests, updated audit command/server imports | eleven workflow-audit modules; nine workflow-audit tests; import-only updates in `run_workflow_audit.py` and `workflow_audit_server.py` | generation-evaluation modules/tests, S15 modules/tests/command, schemas/scenarios/frontend, shared docs/status | S03 only in a separate worktree | unique temp roots; no live provider; focused tests use no shared ports | focused workflow-audit/command tests, compile, stale-reference and independent audit |
| S03 | committed S01 | frozen S15 path map and canonical Outcome | `services/workflow_audit/full_effort/`, mirrored tests, updated historical command imports | five `full_effort_*` modules; three focused tests; `run_full_effort_evaluation.py` and its command test | workflow-audit lane, generation-evaluation modules/tests, S15 generated identities/artifacts, schemas, shared docs/status | S02 only in a separate worktree | temporary test roots only; no historical run root or provider | focused full-effort/command tests, compile, stale-reference and independent audit |
| S04 | S02 and S03 passed | both committed namespace migrations and accepted Block 1 baseline | canonical docs/status, full verification, new compatible parity baseline/report/ledger entry, Block 3 handoff | shared backend/docs maps, slice Outcomes, current-state, generated gitignored parity run and ledger | production behavior, schemas/prompts/fixtures, S15 identities, provider calls | none | ports `15173`/`18080`; unique browser session; new run/baseline identities; isolated output root | backend/frontend/MCP/browser/security/diff gates plus compatible Block 1 comparison |

## Exact Path Migrations

### Workflow audit

| Current | Target |
| --- | --- |
| `services/workflow_audit_artifact_store.py` | `services/workflow_audit/artifact_store.py` |
| `services/workflow_audit_browser_service.py` | `services/workflow_audit/browser_service.py` |
| `services/workflow_audit_capture_service.py` | `services/workflow_audit/capture_service.py` |
| `services/workflow_audit_client.py` | `services/workflow_audit/client.py` |
| `services/workflow_audit_contracts.py` | `services/workflow_audit/contracts.py` |
| `services/workflow_audit_fake_client.py` | `services/workflow_audit/fake_client.py` |
| `services/workflow_audit_ledger_service.py` | `services/workflow_audit/ledger_service.py` |
| `services/workflow_audit_report_service.py` | `services/workflow_audit/report_service.py` |
| `services/workflow_audit_run_service.py` | `services/workflow_audit/run_service.py` |
| `services/workflow_audit_scenario_service.py` | `services/workflow_audit/scenario_service.py` |
| `services/evaluation/full_workflow_audit_service.py` | `services/workflow_audit/service.py` |

The matching `test_workflow_audit_*.py` files move under `tests/evaluation/workflow_audit/` and drop only the redundant `workflow_audit_` filename prefix. The instrumentation-equivalence test moves unchanged in purpose.

### S15 full effort

| Current | Target |
| --- | --- |
| `services/evaluation/full_effort_analysis_service.py` | `services/workflow_audit/full_effort/analysis_service.py` |
| `services/evaluation/full_effort_case_service.py` | `services/workflow_audit/full_effort/case_service.py` |
| `services/evaluation/full_effort_manifest_service.py` | `services/workflow_audit/full_effort/manifest_service.py` |
| `services/evaluation/full_effort_report_service.py` | `services/workflow_audit/full_effort/report_service.py` |
| `services/evaluation/full_effort_runner_service.py` | `services/workflow_audit/full_effort/runner_service.py` |

The three matching `test_full_effort_*.py` files move under `tests/evaluation/historical/full_effort/` and drop only the redundant filename prefix. The Django command and command test remain in their discovery-owned directories.

## Merge and Cancellation Policy

The primary integration owner controls `master`, shared docs/status, staging, commits, and the final parity run. If worktrees are used, merge/cherry-pick order is S02 then S03, followed by S04; neither lane edits the other's paths. An S02 failure blocks only S04 while S03 may finish; an S03 failure blocks only S04 while S02 may finish. Any ambiguous move, stale dynamic import, test-discovery failure, public behavior drift, or incompatible parity key returns to the owning slice. No failed lane is reset or silently discarded.

## Rollback

Each namespace migration is one coherent commit and is reversed only by reverting that commit after preserving unrelated work. Rollback restores original source/test/import paths; schemas, generated run roots, canonical diagrams, baseline evidence, and public contracts never move. S04 records the exact pre- and post-move commits. No local artifact migration or compatibility alias is needed.

## Slice Plan

| Slice | Plan | Status | Completion outcome |
| --- | --- | --- | --- |
| 01 · Repository Responsibility Audit | [`01-repository-responsibility-audit.md`](01-repository-responsibility-audit.md) | Complete | Complete repository inventory, target decision, migration map, and plan audit |
| 02 · Workflow Audit Namespace | [`02-workflow-audit-namespace.md`](02-workflow-audit-namespace.md) | Complete | Reusable operational audit isolated with all consumers and tests migrated |
| 03 · Historical Full Effort | [`03-historical-full-effort.md`](03-historical-full-effort.md) | Complete | Frozen S15 implementation clearly quarantined while remaining reproducible |
| 04 · Integration Parity | [`04-integration-parity.md`](04-integration-parity.md) | Complete | Complete gates and exact compatible Block 1 before/after evidence |

## Plan Audit

Result: **Pass after two correction rounds (2026-07-24).** The first independent read-only audit found two high and four medium planning gaps: explicit current-doc targets, runtime dynamic-import proof, source-inspection test ownership, discovery proof, backend navigation, and package initializers. The first correction resolved those but over-broadened one test command, attempted an unnecessary module import, and described an import-only file imprecisely. The second correction restored exact package tests, verified only the real dynamic target, and clarified import-only ownership. Final re-audit verified all path counts/maps, dependencies, ownership, commands, initializers, documentation owners, historical Outcome preservation, rollback, and parity scope with no remaining critical, high, or medium finding.

## Acceptance Criteria

- Every tracked repository area and evaluation module has an evidence-backed disposition and owner.
- Workflow audit, generation evaluation, readiness proof, and S15 history have unambiguous navigation and dependency boundaries.
- All direct and dynamic Python consumers migrate atomically; no stale old-path import or re-export shim remains.
- Django command/test discovery and the workflow-audit stdio server remain operational.
- Public MCP/REST/frontend behavior, serialized schemas/results, provider call order/budgets, quality, recovery, persistence, and canvas/SVG parity are unchanged.
- S15 code remains reproducible but no terminal identity is loaded, migrated, resumed, or rerun.
- Focused and full gates pass, the new Block 1 run has the exact compatibility key, and output/quality/recovery/browser evidence has no material drift or performance regression.
- Block 3 can begin from the isolated workflow-audit capture/checkpoint seam without another repository reorganization.

## Related Docs

- [`../03-block-02-repository-architecture-and-enablement.md`](../03-block-02-repository-architecture-and-enablement.md)
- [`../00-group.md`](../00-group.md)
- [`../01-success-contract.md`](../01-success-contract.md)
- [`../11-block-execution-and-parallelism.md`](../11-block-execution-and-parallelism.md)
- [`../01-workflow-audit-and-measurement/06-fresh-provider-free-baseline.md`](../01-workflow-audit-and-measurement/06-fresh-provider-free-baseline.md)
- [`../../../../../01-architecture/01-backend-architecture.md`](../../../../../02-architecture/03-backend.md)
- [`../../../../../02-design-and-features/09-workflow-audit-design.md`](../../../../../03-design/11-workflow-audit.md)
- [`../../../../../02-design-and-features/07-evaluation-and-doe-design.md`](../../../../retired-evaluation-and-doe-design.md)
