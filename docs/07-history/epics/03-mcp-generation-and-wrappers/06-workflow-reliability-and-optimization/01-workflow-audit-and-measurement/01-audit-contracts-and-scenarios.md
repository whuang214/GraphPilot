# Slice 01: Audit Contracts and Scenarios

## Purpose

Define the canonical workflow-audit design, strict versioned artifact contracts, storage/comparison semantics, and independent
provider-free scenario bundle before runner implementation depends on them.

## Design

This slice creates the previously absent workflow-audit design owner under `docs/02-design-and-features/` as one of its
outputs; it is not a prerequisite for the slice. The same atomic change adds namespace-first evaluation contracts for the
scenario set, run manifest, observation, external host evidence, browser evidence, report, and baseline ledger, then registers
and meta-validates every schema through `SchemaRegistry`.

The checked-in default bundle uses new workflow-audit identities and contains six normal context-generation anchors
(basic/complex for Activity, Use Case, and BDD) plus the smallest guard scenarios needed for blocked, response/candidate
repair, provider failure/interruption, finalized recovery, and no-rerun evidence. Scenario content may be derived from proven
fixture shapes, but runtime loading cannot import or reference S15 `FullEffortCaseSetService`, `FullEffortFakeClientFactory`,
H/M conditions, stopped identities, or full-effort schemas.

Comparison compatibility binds audit/report/scenario/schedule versions and digests, relevant prompt/schema/rubric/example/layout
assets, runtime dependency/platform identity, and browser mode. Missing values are null with explicit evidence status/reason;
zero is valid only when observed or when a domain was deliberately not called.

## Execution Contract

- **Depends on / inputs:** no implementation slice; consumes the approved Block 1 design and existing committed context
  training fixtures.
- **Outputs:** frozen workflow-audit schemas, scenario bundle/service, and canonical design owner consumed by every later slice.
- **Exclusive write ownership:** workflow-audit schema/scenario assets, scenario service/tests, and audit design owner.
- **Forbidden/shared ownership:** production generation/readiness, S15 `full_effort_*`, and unrelated fixtures are forbidden;
  `generation_contracts.py`, schema registry inventory, decision/index docs, and current state are integration-owner files.
- **Parallelism/resources:** no parallel write slice because S02 requires these committed contracts; schema inventory and approved
  training fixtures are read-only shared resources.
- **Merge/integration gate:** schema/scenario/design audit and full backend gate completed in commit `0333a62` before S02.

## Included Work

- Add the canonical workflow-audit design owner and documentation index/navigation links.
- Define and register strict bounded workflow-audit JSON Schemas with valid examples.
- Add the checked-in default scenario bundle and a copy-isolated validating loader/service.
- Define W01–W22 identities, domain/status/confidence vocabularies, artifact paths, size/count bounds, and compatibility inputs.
- Prove scenario identity uniqueness, cross-reference integrity, safe provider scripts, expected-outcome semantics, and no
  S15/H/M/stopped-identity leakage.
- Add schema inventory, loader, mutation-isolation, invalid-input, size, path, null/zero, and secret-like payload tests.
- Update the decision index only for the durable workflow-audit ownership/contract decision.

## Not In Scope

- Running scenarios or measuring current services.
- Implementing capture adapters, immutable run storage, browser execution, reports, ledger mutation, or commands.
- Reusing or migrating S15 live artifacts.
- Any provider-backed execution or certification behavior.

## Target Areas

- new Slice 01 output: `docs/02-design-and-features/09-workflow-audit-design.md`
- navigation/decision outputs: `docs/README.md` and `docs/02-design-and-features/decision-decisions.md`
- `backend/assets/schemas/workflow-audit-*.json`
- `backend/assets/evaluation/workflow-audit/scenarios.json`
- `backend/services/shared/schema_registry.py`
- `backend/services/workflow_audit/scenario_service.py`
- `backend/tests/evaluation/workflow_audit/test_scenario_service.py` and focused schema tests

## Exit Criteria

- All new schemas meta-validate and their examples validate.
- The default scenario set is deterministic, copy-isolated, digest-bound, bounded, and covers all required normal/guard roles.
- No default scenario identity or runtime import contains S15/H/M/full-effort/stopped-run coupling.
- Invalid refs, duplicate identities, unsafe paths, oversized content, secret-like fields/values, and unsupported status/null/zero
  combinations fail before runner/provider construction.
- The new workflow-audit design owner exists, is indexed, and clearly separates operational audit from generator
  certification and live status; the decision index points to it without duplicating its contract.
- Focused tests, full backend tests, Django check, compile check, and `git diff --check` pass.

## Previous Slice

None — this is the first implementation slice under the approved
[Block 1 owner](../02-block-01-workflow-audit-and-measurement.md).

## Next Slice

[`02-capture-and-evidence-adapters.md`](02-capture-and-evidence-adapters.md)

## Outcome

**Status:** Complete. Slice 01 added the canonical operational workflow-audit design, seven strict namespace-first artifact
schemas, and an immutable provider-free scenario corpus with six type/complexity anchors plus six focused guards. The new
`WorkflowAuditScenarioService` validates/copy-isolates the bundle, materializes only the six approved context training fixtures,
and proves schema, semantic, type, path, and canonical/runtime digest closure without importing S15's `full_effort_*` package.

**Deviations:** The scenario corpus references existing approved context fixtures instead of duplicating JSON 1, JSON 2, and
logical outputs. This is smaller than an embedded corpus while retaining exact asset/digest binding. No planned behavior,
contract, security, or no-live boundary was weakened.

**Verification:** Independent implementation audit passed with no critical, high, or medium finding. From `backend/`,
`uv run python manage.py test tests.support.test_schema_registry tests.evaluation.workflow_audit.test_scenario_service` passed
23 tests; `uv run python manage.py test` passed 926 tests with 5 skipped; `uv run python manage.py check`,
`uv run python -m compileall -q services/workflow_audit/scenario_service.py tests/evaluation/workflow_audit/test_scenario_service.py`,
and repository `git diff --check` passed.

**Follow-up:** Slice 02 consumes these contracts/scenarios to add normalized capture and evidence adapters with observational
equivalence.
