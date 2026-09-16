# Slice 02: Capture and Evidence Adapters

## Purpose

Implement normalized W01–W22 evidence capture and non-overlapping accounting through evaluation-only adapters while proving
that instrumentation cannot alter provider calls, generated meaning, persistence, rendering, or runtime acceptance.

## Design

Reuse the existing generation observer for stage, candidate, repair, quality, and result events. Add an evaluation-only
capturing client around the stable `LLMClient` protocol to collect provider role/state, request/response bytes, duration,
input/output/reasoning/cached tokens, provider request identity, service tier, requested/effective controls, and safe validation
`{code,path}` evidence. Fake-provider duration is classified as local harness time; a future separately authorized Azure client
can use the same adapter without changing this block's provider-free command.

Add fixture-host and validated external-host evidence adapters, plus the current real-stdio measurement seam. Normalize every
value with evidence status, source, confidence, and reason. Complete-wall accounting keeps host, Azure, MCP, local, browser,
and residual values non-overlapping.

## Execution Contract

- **Depends on / inputs:** committed S01 schemas, scenario service/bundle, and canonical evidence semantics.
- **Outputs:** frozen measurement/accounting contracts, metric store/observer/client, host adapters, and equivalence proof for
  S03.
- **Exclusive write ownership:** workflow-audit capture/client/contracts modules and their focused/equivalence tests.
- **Forbidden/shared ownership:** runner, audit server, browser, report, and ledger code are forbidden; service/architecture/
  status docs and shared path-safety remediation are integration-owner changes.
- **Parallelism/resources:** no parallel write slice because S03 consumes the committed capture APIs; temporary workspaces and
  fake clients remain unique to focused tests.
- **Merge/integration gate:** focused equivalence/security plus full backend gate completed in commit `ea0cd8e` before S03.

## Included Work

- Extract/reuse current metric append/read, wrapper, observer, boundary-map, and accounting logic without changing production
  acceptance behavior.
- Implement bounded normalized capture types/services for W01–W22.
- Implement the scenario-backed fake client and generic audit-capturing client without S15 factories.
- Implement fixture-host evidence and strict optional external-host import validation.
- Preserve real-stdio request/response byte and elapsed capture for later runner orchestration.
- Record repair diagnostics and missing provider metadata exactly, never by estimation.
- Add callback/capture failure-isolation and instrumented-versus-uninstrumented equivalence tests.

## Not In Scope

- Immutable run orchestration, observation terminal state, browser execution, reports, ledger writes, or CLI migration.
- Production observer-event/schema changes.
- Constructing or calling Azure.
- Optimizing any measured stage.

## Target Areas

- `backend/services/workflow_audit/service.py`
- `backend/services/workflow_audit/capture_service.py` and `client.py`
- `backend/services/generation/diagnostics/generation_observer.py` as an unchanged consumed contract
- existing readiness validation callback and `LLMResponseDocument` metadata seams
- focused capture, LLM, generation, and evaluation tests

## Exit Criteria

- All required provider metadata is exact when supplied and null with a reason when unavailable.
- Fixture host, external host, MCP, fake-provider/local, browser-placeholder, and residual domains cannot overlap.
- Fake-provider duration never appears as Azure latency; Azure call count is an explicit observed zero in provider-free runs.
- Instrumented and uninstrumented scenarios have identical provider-call order, result, canonical JSON, SVG, and writes.
- Capture/observer/storage callback failures cannot abort or change the production operation under observation.
- Bounds, redaction, invalid external evidence, status/confidence, and null-versus-zero tests pass.
- Focused tests, full backend tests, Django check, compile check, and `git diff --check` pass.

## Previous Slice

[`01-audit-contracts-and-scenarios.md`](01-audit-contracts-and-scenarios.md)

## Next Slice

[`03-audit-runner-and-recovery.md`](03-audit-runner-and-recovery.md)

## Outcome

**Status:** Complete. Slice 02 added strict W01–W22 measurement/accounting contracts, bounded failure-isolated JSONL/event capture,
fixture and imported-host adapters, and an evaluation-only `WorkflowAuditCapturingClient` that preserves delegate call/result/
exception identity while recording bounded provider role/state/bytes/timing/token/cache/control/validation metadata. Production
`GenerationObserver`, readiness/generation behavior, and S15 services remain unchanged.

**Equivalence:** A production `DiagramGenerationService` context anchor produced identical provider calls/order, generation
result, complete workspace writes, canonical JSON bytes, and SVG bytes with and without audit instrumentation. Fake-provider
work remains local harness evidence and Azure remains unavailable/not called rather than inferred.

**Audit and deviations:** Independent audit's first pass raised a false null/zero concern; direct zero-total coverage confirms
unavailable browser values remain null while observed zero domains remain zero. Valid efficiency/concurrency findings were fixed
with a lazy metric count and lock-ordered sink writes plus concurrent store/observer regressions. Re-audit passed with no
critical, high, or medium finding. No planned scope or contract changed.

**Verification:** From `backend/`, the final focused command
`uv run python manage.py test tests.evaluation.workflow_audit.test_scenario_service tests.evaluation.workflow_audit.test_client tests.evaluation.workflow_audit.test_capture_service tests.evaluation.workflow_audit.test_instrumentation_equivalence`
passed 40 tests. The required full suite initially exposed a reproducible pre-existing Python 3.14/Windows race where
`Path.resolve()` alternated between normal and `\\?\` extended forms during concurrent exclusive creation; normalized
post-resolution drive/UNC forms plus a deterministic regression and 100 repeated isolated passes fixed the false containment
failure without weakening symlink/traversal checks. The final complete backend suite passed 954 tests with 5 skipped; Django
check, compileall, and `git diff --check` pass.

**Follow-up:** Slice 03 composes these scenarios/adapters into immutable real-stdio cold/warm and guard observations with
recovery and no-rerun state.
