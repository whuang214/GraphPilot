# Slice 14: Context Workflow Performance

## Purpose

Intensively audit the complete cold/warm context-backed MCP workflow, rank bottlenecks by host context, provider calls,
tokens, duration, repair frequency, and user-visible timeout risk, and publish an evidence-backed design for the smallest
safe speed improvements. Implement only the measurement foundation and one operator-only `medium` final-readiness proof
needed to choose the next fix without changing production generation behavior, automatically tuning prompts/configuration,
or claiming certification.

## Background

Context S13's one live `high`-effort generation-path attempt used no standalone readiness and stopped correctly at final
readiness. The initial readiness role took 112,631.031 ms with 15,130 input and 11,632 output tokens; strict response repair
took 349,535.310 ms with 15,114 input and 11,171 output tokens. The final result was `needs_context`, score 81, with one
non-overrideable goal/scope blocker and one secondary evidence blocker. The response JSON bodies were only 9,958 and
9,001 bytes, so aggregate completion tokens strongly suggest substantial hidden reasoning, but S13 did not retain the SDK's
reasoning/cached-token detail or the safe `{code,path}` diagnostics that triggered repair.

The user changed the shared runtime effort to `medium` and approved one new proof: exercise readiness through
`DiagramGenerationService.generate_context(..., require_ready)`, never call standalone readiness, allow at most two Azure
calls (final readiness plus optional readiness response repair), and prevent any generation/review provider call locally.
No `.env` inspection or modification belongs to this slice.

### Whole-workflow baseline

The audit begins from measured evidence, keeping host and Azure costs separate:

| Boundary | Current evidence |
| --- | --- |
| Cold Copilot host | about 129.6K host-context tokens and about 374 visible credits while recreating JSON 1 |
| Public workflow | reduced by S13 from 8,634 to 8,228 UTF-8 bytes with no standalone-readiness normal step |
| Current architecture authority | JSON 1 21,047 compact bytes, JSON 2 6,705 bytes, 21 selected claims |
| Readiness input | 64,319-byte projection / 76,894-byte wire request; embedded rubric is the largest contributor |
| High initial readiness | 112.6 seconds, 15,130 input, 11,632 completion tokens |
| High readiness repair | 349.5 seconds, 15,114 input, 11,171 completion tokens; almost the complete input rerun |
| Generation packet | 59,811 wire bytes including two required examples (9,309 and 16,534 bytes) |
| Reviewed pipeline | sequential generation, optional deterministic repair, semantic review/response repair/candidate repair/final review |
| Local fake path | about 1.5 seconds including layout/validation/persistence/render; provider roles dominate live time |
| Timeout behavior | synchronous MCP can lose the response; S13 now prevents unchanged rerun and recovers finalized output |

### Audit questions and design output

The slice measures and evaluates every stage rather than assuming reasoning effort is the sole cause:

1. **Host efficiency:** whether deterministic claim query/detail tools could avoid loading complete JSON 1/source into
   Copilot while preserving full authority and readiness closure checks.
2. **Readiness packet:** duplicated/stable rubric, allowlist, claim, and evidence bytes; prompt-caching evidence from exact
   `cached_tokens`; no authority/rubric truncation.
3. **First-response validity:** exact safe validation code/path frequencies that trigger repair and whether prompt/schema
   projection or deterministic mechanical canonicalization owns each defect.
4. **Repair architecture:** current full-projection reconstruction versus safe deterministic fixes or targeted repair;
   rejected raw responses/hidden reasoning remain unpersisted.
5. **Provider controls:** `low|medium|high|xhigh` reasoning, reasoning-token volume, model/service latency, and whether one
   shared setting remains sufficient.
6. **Generation/review chain:** actual role durations/tokens/repairs after readiness passes; preserve required examples,
   reviewed quality, final review, and strict no-fallback behavior.
7. **MCP experience:** progress/job alternatives versus current synchronous call plus stage-correct recovery; distinguish
   true speed from perceived reliability.
8. **Local stages:** layout/validation/persistence/render profile only after provider work is no longer dominant.

The final `Outcome` contains a ranked design table for each confirmed bottleneck: evidence, root cause, recommended smallest
fix, strongest alternative, safety/compatibility cost, proof, and defer/promote decision. This slice does not silently
implement every candidate optimization.

## Design

### Safe response metadata

Extend private dict-compatible `LLMResponseDocument` with bounded, read-only optional metadata from the pinned OpenAI SDK:

- `reasoning_tokens` from `completion_tokens_details.reasoning_tokens`;
- `cached_input_tokens` from `prompt_tokens_details.cached_tokens`;
- existing prompt/completion totals;
- bounded provider request ID and service tier when available.

Provider request ID and service tier are read as bounded strings when present and become null when absent/invalid; they
are never synthesized or estimated. The mapping still contains only the parsed strict JSON document. Plain-dict custom
clients remain compatible. Invalid or missing usage metadata becomes null and is never estimated. No prompt, response text, hidden reasoning, credential, source,
or complete context is persisted.

### Safe readiness validation diagnostics

Add frozen readiness-owned `ReadinessValidationDiagnosticEvent` and keyword-only constructor argument
`validation_callback: Optional[Callable[[ReadinessValidationDiagnosticEvent], None]] = None` on each
`ContextReadinessService`. The event contains exact `role`, `attempt`, `valid`, `issue_count`, and immutable bounded
`issues: Tuple[Tuple[str, str], ...]` code/path pairs. Emit one event after each first/repair response validation with only:

```text
role, attempt, valid, issueCount, issues[{code,path}]
```

Messages and rejected responses are excluded. The callback is observational and failure-isolated. Runtime generation need
not subscribe; the benchmark captures it directly. Existing result, observer, trace, diagnostics, readiness, and generation
schemas remain unchanged unless an additive bounded benchmark-report schema is registered.

### Operator-only benchmark

Add `benchmark_readiness_effort`, separate from release calibration, with an explicit provider-control flag:

```powershell
uv run python manage.py benchmark_readiness_effort `
  --workspace <absolute-workspace> `
  --request-path .graphpilot/requests/<name>.gp-request.json `
  --reasoning-effort medium `
  --live `
  --json
```

`--reasoning-effort` is required and exactly `low|medium|high|xhigh`. It is operator-only, passed to
`AzureLLMClient(reasoning_effort=...)`, recorded as requested/effective control, and never exposed through MCP, persisted
requests, or `.env`. A later comparison may invoke the same command under another explicitly authorized budget; this
slice authorizes only the one `medium` invocation.

The command:

1. requires explicit `--live` before constructing Azure;
2. safely loads exact canonical JSON 2 and its bound JSON 1 from the source workspace, recomputes that manifest's exact
   configured source fingerprint, and stops before Azure unless status is current;
3. copies only those two canonical documents into a fresh temporary workspace;
4. creates `AzureLLMClient(reasoning_effort=<flag>)` without modifying `.env`;
5. wraps it in a benchmark client that permits only the readiness review schema and at most two delegated Azure calls;
6. injects the instrumented readiness service into `DiagramGenerationService`;
7. calls `generate_context` once with `require_ready`, no trace/debug, and the exact request path;
8. returns a bounded strict benchmark report to stdout and writes no report or canonical artifact.

If final readiness blocks, the command records the complete bounded status/score/finding identity summary. If readiness
returns `ready`, production generation tries to build its first generator call; the wrapper rejects that non-readiness
schema locally before Azure, the command reports `generation_boundary_reached`, and no diagram can be persisted. The
boundary is expected benchmark behavior, not a production operation code. Provider refusal/failure remains an explicit
benchmark error. The command never retries.

### Exact live budget

This slice has one authorized medium generation-path benchmark attempt:

```text
one command invocation
one DiagramGenerationService.generate_context attempt
Azure call 1: mandatory final readiness
Azure call 2: optional readiness response repair
Azure call 3+: impossible (local guard)
standalone readiness: forbidden
retry: forbidden
```

Before the call, verify source evidence/request are still current and state budget `0/1`. Missing/stale/mismatched input
changes the budget state to `skipped`; do not rebuild it. After invocation the state is `attempted` regardless of result.
The previous high run is the comparison baseline; Copilot credits remain separate and are unavailable for this direct Azure
operator command.

### Benchmark report

The report is explicitly non-certifying and bounded. Its exact identity is
`graphpilot.readiness-effort-benchmark.v1` / `readinessEffortBenchmark`. It includes:

- exact schema/kind and `benchmarkOnly: true`, `releaseStatus: not_run`;
- request/manifest IDs and digests, requested/effective effort, deployment/model;
- outcome `readiness_blocked|generation_boundary_reached|error`;
- final readiness status, score, blocker/warning `{id,code,facet,overrideable,actionKind}` summaries;
- first-response validity, repair used, bounded validation issue code/path summaries;
- ordered provider roles with bytes, duration, prompt/completion/reasoning/cached tokens;
- aggregate duration/tokens/call count.

It excludes raw authority, evidence, rubric, prompts, responses, reasoning, full findings prose, credentials, and paths
outside the canonical request reference.

### Comparison and feedback

The medium pilot is semantically acceptable only if it preserves:

- `needs_context` rather than false `ready`;
- the non-overrideable `scope_conflicts_with_goal` blocker;
- the secondary evidence blocker or an independently justified equivalent;
- valid refs and permitted action kinds.

Performance evidence is directional: repair avoidance, fewer reasoning tokens, lower duration, or fewer calls. One pilot
cannot promote medium or split role settings. Findings route one next action:

| Observation | Owner / next action |
| --- | --- |
| Same quality, no repair, faster | Plan small ready/warning/blocked matrix |
| Same validation issue under high and medium | Fix exact prompt/schema/validator contract |
| Repair only under medium | Retain high or improve first-response instructions |
| Missing/weaker blocker | Reject medium for readiness |
| Equivalent but still slow | Investigate provider/model latency and reasoning volume |
| Later generation degrades at medium | Consider one generation-only high override after separate evidence |

No model output changes prompts, code, settings, labels, or runtime behavior automatically.

### Reversibility

Rollback removes the benchmark command/report schema, optional metadata fields, and readiness validation callback. Existing
production clients, final readiness, generation/review calls, strict schemas, request persistence, and `.env` semantics
remain unchanged. The operator command writes only to temporary storage, so rollback requires no artifact migration or
deletion.

## Plan Audit

Result: **Pass.** Independent review found no material issue and verified whole-workflow coverage, measured host/provider
baseline separation, ranked-design output, exact operator-only effort flag, source freshness/temp identity, production
`generate_context(require_ready)` path, two-call/readiness-schema guard, no writes/standalone readiness, telemetry bounds,
redacted diagnostics, non-certifying report, release-calibration separation, failure behavior, reversibility, tests, live
budget, and canonical owners. Three minor ambiguities are resolved above with the exact keyword-only validation callback
and immutable event shape, explicit report schema/kind, and null/non-synthesis rules for provider request ID/service tier.

## Included Work

- Measure the complete cold/warm host, readiness, generation/review, timeout/recovery, and local-stage workflow using S13
  evidence plus fresh offline packet/profile measurements; produce the ranked end-to-end optimization design.
- Add bounded reasoning/cached-token and safe provider identity metadata to the private strict response document.
- Emit safe first/repair readiness validation diagnostics through an optional readiness-owned callback.
- Add and register a strict bounded readiness-effort benchmark report contract.
- Implement the explicit-live operator command with exact temporary JSON 1/JSON 2 staging and two-call/schema guard.
- Add offline fake tests for high/medium metadata, first-response validity/repair issues, blocked result, unexpected-ready
  generation boundary, third-call prevention, provider failure, path/input safety, redaction, no writes, and JSON output.
- Run focused and complete offline gates, independent implementation audit, and diff/security checks.
- Run the one approved medium final-readiness replay only after all offline gates and input-freshness checks pass.
- Compare against S13 high baseline, update canonical docs/status/outcome, and commit the verified implementation.

## Not In Scope

- Calling standalone `context_readiness_assess` before generation.
- More than one live benchmark invocation or more than two Azure calls.
- Allowing actual generation/review provider use or writing a canonical diagram during the benchmark.
- Implementing every optimization candidate from the whole-workflow design; each material follow-up needs its own proof/slice.
- A ready/warning/blocked matrix, ten-repeat release calibration, certification, freeze, or production promotion.
- Automatic prompt/config/code mutation, self-training, unchanged rerolls, or quality optimization toward passing.
- Adding readiness-specific runtime environment configuration or changing the shared medium setting.
- Lowering mandatory final readiness, reviewed quality, strict output, provenance, digest binding, or atomic persistence.
- Truncating authority, evidence, rubrics, or examples.
- Inspecting/modifying `.env`, existing GraphPilot artifacts, Git configuration, or remote state.

## Target Areas

- `backend/services/llm/llm_client.py`
- `backend/services/readiness/context_readiness_service.py`
- `backend/operations/management/commands/benchmark_readiness_effort.py`
- `backend/assets/schemas/` and `backend/services/shared/schema_registry.py`
- relevant LLM/readiness/management/schema tests
- `backend/README.md`
- `docs/01-architecture/01-backend-architecture.md`
- `docs/02-design-and-features/04-generation-design.md`
- `docs/02-design-and-features/08-context-backed-generation/01-readiness/`
- `docs/03-development-and-delivery/00-development-environment.md`
- `docs/03-development-and-delivery/01-testing-strategy.md`
- delivery board/group/epic and this slice outcome

## Exit Criteria

- Outcome ranks every measured end-to-end bottleneck with evidence, root cause, smallest fix, alternative, trade-off, and
  proof; it distinguishes implemented measurement from proposed optimization.
- Benchmark exposes required operator-only `--reasoning-effort low|medium|high|xhigh`, records requested/effective value,
  and never changes runtime/MCP/request configuration.
- Benchmark invokes the production context generation service once with `require_ready`; it never invokes standalone
  readiness and delegates at most two readiness-schema Azure calls.
- A `ready` result cannot reach Azure generation or persistence; local boundary behavior is explicit in the report.
- Existing production generation behavior and public MCP contracts remain unchanged.
- Reasoning/cached tokens and safe provider identity are exact when supplied, null when absent/invalid, and never estimated.
- First/repair response validation emits bounded code/path diagnostics without raw response/message/context.
- Report is schema-valid, bounded, non-certifying, secret-safe, and contains no raw authority/provider content.
- Offline tests prove blocked, repaired, ready-boundary, provider-error, budget, path, redaction, and no-write behavior.
- One medium live attempt occurs only after freshness and complete offline gates; no retry occurs.
- Medium/high comparison records semantic parity and performance evidence without automatic promotion.
- Backend/frontend/MCP gates, `git diff --check`, and independent audit pass.
- No `.env`, existing canonical artifact, Git configuration, certification state, or remote branch is changed; no push occurs.

## Previous Slice

[`13-context-performance-and-recovery.md`](13-context-performance-and-recovery.md)

## Next Slice

No planned successor. A small reasoning-effort matrix requires separate evidence, plan, and live authorization.

## Outcome

**Completion:** Audited the complete cold/warm workflow and implemented only the measurement foundation plus the approved
operator proof. Private strict responses now retain exact reasoning/cached tokens and bounded provider request ID/service
tier without changing JSON shape. Readiness can emit failure-isolated first/repair validation diagnostics containing only
bounded code/path pairs. `benchmark_readiness_effort` requires explicit `--live` and
`--reasoning-effort low|medium|high|xhigh`, verifies current context, stages exact JSON 1/JSON 2 temporarily, invokes
production `generate_context(require_ready)`, permits at most two readiness-schema calls, blocks generation locally, writes
no artifact/report, and emits a schema-validated non-certifying report.

**Medium proof:** Budget state is `attempted` (1/1), with no standalone readiness and no retry. The exact S13 request under
`medium` returned `needs_context` in one first-response-valid readiness call: **77,941.939 ms**, 15,130 input tokens, 6,698
completion tokens including **4,608 reasoning tokens**, zero cached tokens, 76,894 request bytes, and 9,483 response bytes.
It made no repair or generation call. Versus high's 462,166.341 ms/two calls/30,244 input/22,803 completion, medium reduced
provider duration **83.1%**, calls **50%**, and completion tokens **70.6%**. It preserved the two decisive
`scope_conflicts_with_goal` and `secondary_context_incomplete` blockers and never produced false ready, but added three
conservative facet blockers and lowered score **81 → 61**. Medium is therefore promising performance evidence but lacks
semantic parity and is not promoted/certified by this single case.

**Ranked whole-workflow design:**

| Rank | Evidence / root cause | Recommended smallest fix | Strongest alternative / decision |
| --- | --- | --- | --- |
| 1 | High readiness repair alone cost 349.5 s and replayed almost the full 15K-token projection; first invalid diagnostics were previously invisible. | Aggregate the new safe code/path events across a small labeled matrix, then fix the dominant prompt/schema/validator mismatch or apply only proven mechanical canonicalization. | Targeted model repair would need more contract complexity; do not send/persist raw responses. **Promote next proof.** |
| 2 | Medium removed repair and cut duration 83.1%, but added blockers/score drift; 4,608 of 6,698 completion tokens were reasoning. | Run a separately authorized ready/warning/blocked high-vs-medium matrix with human status/blocker bands before changing defaults. | Readiness-medium/generation-high split only if later generation evidence requires it. **Do not promote setting yet.** |
| 3 | Cold Copilot creation reached ~129.6K host tokens/~374 credits; canonical JSON 1 is 21 KB compact and host source reads dominate. | Design deterministic bounded claim-query/detail MCP tools so the host retrieves candidate IDs/summaries then exact selected claims, while readiness still checks complete closure. | Prompt guidance is cheaper but already applied and insufficient for cold authoring. **Separate public-tool design required.** |
| 4 | Readiness wire input is 76.9 KB; rubric is the largest stable contributor; medium reported `cachedInputTokens: 0`. | Measure cache behavior over repeated labeled cases and evaluate contract-equivalent stable-prefix packaging; retain every rubric/authority field. | Provider stored prompts/model split are provider-coupled. **Research, no truncation.** |
| 5 | Generation packet is 59.8 KB and reviewed flow may use generation, repair, review-response repair, candidate repair, and final review; no post-readiness live timings exist for S14. | Use existing role telemetry on one separately authorized ready case before changing generation/review calls. | Parallelization is invalid across dependent stages; never drop examples/final review. **Measure first.** |
| 6 | Synchronous MCP can outlive clients; S13 recovery prevents duplicate work but does not shorten Azure time. | Keep stage-correct recovery; evaluate progress notifications before job/polling APIs after provider latency work. | Async jobs improve reliability, not provider speed, and add public lifecycle state. **Defer.** |
| 7 | Delayed-fake complete local path is ~1.5 s versus 77–462 s provider time. | Defer layout/validation/render optimization until provider roles are no longer dominant. | Local micro-optimization has negligible current user impact. **Defer.** |

**Verification:** Focused instrumentation/command/schema tests passed **78**, audit-edge tests passed **35**, and independent
implementation re-audit passed. Full backend passed **887 tests (5 skipped)**; Django check and real MCP stdio smoke passed.
Frontend `npm run verify` passed lint/build, **419** unit/component tests, and **43** Chromium E2E tests; the existing
non-failing chunk advisory remains. The benchmark report remained `benchmarkOnly: true`, `releaseStatus: not_run`, and no
diagram/current artifact was written.

**Deviations / follow-up:** The approved proof was broadened before implementation to rank the full workflow, while code
remained limited to reusable measurement and the guarded effort command. No `.env` inspection/change, public MCP argument,
production reasoning split, prompt tuning, automatic feedback, certification, existing-artifact write, retry, or push
occurred. The next highest-value slice is safe validation-diagnostic aggregation plus a small labeled effort/repair matrix;
claim-query tools require a separate material MCP design.
