# Slice 02: Provider-Free Diagnosis

> Historical S02 plan/Outcome retained as provider-free evidence. Its review-gated continuation was superseded by the active S05 causal diagnosis plan; the lifecycle implementation remains a concrete S06 input.

## Purpose

Exhaust current, offline, and fake evidence; produce a bounded reproducible diagnosis report that distinguishes trigger, cost amplifier, provider/control, workflow, and evidence-durability hypotheses without claiming Azure semantics.

## Design

Implement one minimal injected-client `ReadinessDiagnosisService` under `services/workflow_audit/` plus strict `readiness-diagnosis-case`, `readiness-diagnosis-run-manifest`, and `readiness-diagnosis-observation` schemas. The service constructs no Azure client and has no management command. It validates one visible case, freezes an exact run/observation identity, writes a pre-dispatch checkpoint before calling `ContextReadinessService.assess_bound`, captures only readiness/repair provider events and validation `{code,path}` events, writes one immutable observation/terminal, and never reruns a checkpointed or terminal identity. Resume after a nonterminal checkpoint conservatively terminalizes `uncertain` without provider use.

Fake/temporary tests cover first-response-valid, repaired-valid, completed-invalid repair, provider failure, interruption before/after checkpoint, identity conflict, and terminal resume. Generation/review roles and diagram/trace/render/browser writes are structurally forbidden.

Create machine-readable `evidence/provider-free-diagnosis.json` and a concise Markdown rendering. Bind them to exact commit/assets and cited source/Outcome evidence. The report contains:

- expected versus observed readiness behavior;
- each diagnosis level, evidence for/against, confidence, and smallest missing proof;
- first-response/repair lifecycle and complete-projection byte/token/cost evidence;
- current safe provider/validation callback behavior;
- current checkpoint/terminal/no-rerun seams and the benchmark's durability gap;
- human-review authority inventory;
- exactly one provisional recommendation state, `additional_evidence` unless provider-free evidence newly isolates a root.

Use existing provider-free tests rather than adding speculative production code. New temporary diagnostic tests are removed unless they expose a permanent high-value regression gap; permanent test/code changes require a separately corrected plan and implementation audit.

## Execution Contract

- **Depends on / inputs:** committed S01 plan, exact readiness source/assets/tests, accepted provider-free Block 2 evidence.
- **Outputs:** three strict contracts, fake-proven service/store, bounded JSON/Markdown diagnosis evidence, and S02 Outcome.
- **Exclusive write ownership:** `backend/services/workflow_audit/readiness_diagnosis_service.py`; three `backend/assets/schemas/readiness-diagnosis-*.json` files; schema identity registration; `backend/tests/evaluation/workflow_audit/test_readiness_diagnosis_service.py`; `evidence/`; this Outcome.
- **Forbidden/shared ownership:** S03 review files, readiness runtime code/prompts/rubrics, management commands, S15/generated artifacts, current-state/decision index until S04.
- **Parallelism/resources:** sequential before S03; fake clients only, temporary control/staged roots, no ports/browser/Azure.
- **Gate:** failing/characterizing lifecycle tests, focused readiness/capture tests, full backend/check/compile, schema/digest/secret checks, independent implementation/evidence audit.
- **Cancellation:** if offline evidence supports a correction only by assuming missing provider output, retain `additional_evidence`.

## Included Work

- Add strict schema examples/bounds and register exact identities without changing existing contracts.
- Add failing/characterizing tests, then implement the injected-client lifecycle and immutable safe artifacts.
- Run focused existing tests for readiness validation diagnostics, repair, provider failure, capture equivalence, interruption, terminal resume/no-rerun, and benchmark boundary.
- Recompute prompt/schema/rubric/projection/input identities and relevant byte sizes provider-free.
- Record supported/disconfirmed hypotheses without raw private content.
- Verify JSON/Markdown parity, bounds, links, and secret safety.
- Run independent read-only diagnosis-evidence audit and resolve every material finding.
- Commit the verified report.

## Not In Scope

- Azure/client construction, live performance/quality conclusions, human labels, management commands, readiness behavior changes, or Block 4 design.

## Target Areas

- `backend/services/workflow_audit/readiness_diagnosis_service.py`
- `backend/assets/schemas/readiness-diagnosis-*.json` and schema identity registration
- `backend/tests/evaluation/workflow_audit/test_readiness_diagnosis_service.py`
- `evidence/provider-free-diagnosis.json`
- `evidence/provider-free-diagnosis.md`
- this slice Outcome

## Focused Verification

```powershell
cd backend
uv run python manage.py test tests.evaluation.workflow_audit.test_readiness_diagnosis_service tests.readiness.test_semantic_readiness_service tests.readiness.test_context_readiness_service tests.management.test_calibrate_readiness_command tests.evaluation.workflow_audit.test_client tests.evaluation.workflow_audit.test_artifact_store tests.evaluation.workflow_audit.test_runner_service
uv run python manage.py test
uv run python manage.py check
uv run python -m compileall -q services/workflow_audit tests/evaluation/workflow_audit
```

Also require deterministic report regeneration/parity, exact source/digest bindings, zero Azure construction, secret scan, and `git diff --check`.

## Exit Criteria

- Current evidence is exhausted and reproducible.
- Trigger and cost amplifier are not conflated.
- Every hypothesis has evidence, disconfirmation, confidence, and smallest next proof.
- The report does not convert fake/time/test evidence into Azure or human evidence.
- Independent audit has no unresolved critical/high/medium finding.

## Previous Slice

[`01-evidence-boundary.md`](01-evidence-boundary.md)

## Next Slice

[`03-human-review-package.md`](03-human-review-package.md) after S02 passes and commits.

## Outcome

**Status:** Complete. Added three closed namespace-first diagnosis schemas and registered them through `SchemaRegistry`; their examples are schema-valid and mutually bound by actual canonical case/manifest/observation digests. `ReadinessDiagnosisService` and `ReadinessDiagnosisArtifactStore` live under the reusable workflow-audit package, accept only an injected client, expose no command, construct no Azure client, and cannot reach generation/review.

**Lifecycle proof:** A manifest and pre-dispatch checkpoint precede provider use; immutable observation precedes terminal. Clean first response, repaired valid, completed-invalid repair, provider failure, checkpoint-write failure before dispatch, checkpointed uncertain resume, terminal no-rerun, and identity conflict are covered. The initial expected import failure preceded implementation; two post-implementation resume failures exposed rebuilt `createdAt`, corrected by loading the immutable manifest before identity comparison. All eight new tests then passed.

**Diagnosis:** `evidence/provider-free-diagnosis.json` is machine authority and its Markdown renders every decisive identity/claim. It binds plan commit `643de67`, source fixture/readiness assets, a 22,911-byte bridge projection and 32,727-byte strict wire, S13–S15/Block 2 Outcomes, six hypotheses, and exactly one supported recommendation: `additional_evidence`. Trigger and complete-projection repair cost are distinct; no correction or Block 4 authorization is claimed.

**Audit and verification:** Independent implementation audit passed with no material finding; its low placeholder-digest note was corrected and retained as a cross-digest test. Independent evidence audit's commit/digest/source-trace findings were corrected by explicit Git verification, digest methods, historical paths, and refreshed hashes; re-audit passed. The 77-test focused gate and post-fix 8-test module pass; full backend passed 999 tests (5 skipped); schema inventory (70), Django check, compile, JSON/Markdown parity, file/schema hash closure, secret scan, and `git diff --check` pass. No Azure call, `.env`, generated/S15 identity, dependency, public command, approval, push, or deployment occurred.
