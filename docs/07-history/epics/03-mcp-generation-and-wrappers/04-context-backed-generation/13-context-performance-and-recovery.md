# Slice 13: Context Performance and Recovery

## Purpose

Reduce avoidable host-context growth and provider work in context-backed MCP generation, make client-timeout recovery
stage-correct and non-duplicating, and replace blind provider-usage fields with measured duration and available token
usage without weakening authority, readiness, reviewed quality, strict output, persistence, or rendering.

## Background

The cold Copilot-host observation reached about 129.6K host-context tokens and about 374 visible Copilot credits while
recreating JSON 1. A later warm request retried an unchanged timed-out standalone readiness call, then timed out during
generation even though the backend eventually persisted canonical JSON and an SVG. The current workflow always asks for
standalone readiness before generation even though context generation reruns mandatory final readiness.

The user-supplied historical trace and both named diagnostic runs are absent from the clean `65d8c78` worktree, so this
slice does not recreate them or repeat the costly cold live run. The committed live record remains the authority for its
ready/100, 7-node/9-edge, clean reviewed/100, one-semantic-repair outcome. The currently present architecture request,
diagram, and SVG provide the warm artifact baseline: JSON 1 was recorded at `2026-07-21T23:12:43Z`, JSON 2 was persisted
at `23:14:23Z`, and canonical generation wrote the diagram at `23:22:21Z`. Offline `diagram_validate` returns zero issues,
and inline `diagram_render` reproduces the present SVG byte-for-byte.

An isolated fake-provider baseline establishes the reproducible implementation defects:

| Measurement | Before |
| --- | ---: |
| Normal ready workflow provider calls (standalone readiness plus generation) | 4 |
| Calls inside context generation, including final readiness | 3 |
| Calls reported in result/trace | 2 |
| Unchanged completed-generation retry before name conflict | 3 provider calls / 433.736 ms |
| Trace durations and token counts | `0` / `null` |
| Rendered workflow instructions | 8,634 UTF-8 bytes |

For the real architecture inputs, compact JSON 1 is 21,047 bytes, JSON 2 is 6,705 bytes, resolved generation authority is
14,882 bytes, the readiness projection is 64,319 bytes, and the generation wire packet is 59,811 bytes. The two required
examples account for 9,309 and 16,534 bytes. These values distinguish Copilot host context from Azure provider input and
show that authority, evidence, rubrics, and examples must remain complete rather than being truncated as a shortcut.

## Design

### Workflow efficiency

The normal context branch uses `diagram_generate_from_context` with `require_ready` instead of first calling standalone
readiness. Inside that generation attempt, the one freshly loaded complete readiness assessment is the mandatory final
gate; “first” describes host orchestration and does not add or remove a second internal gate. A ready result proceeds in
one call; a normal readiness block returns the complete readiness result and drives the existing improve/accept loop.
Standalone `context_readiness_assess` remains available for readiness-only work or an explicitly requested preview, but is
no longer a required precursor to generation and never licenses cached reuse or any bypass of final readiness.

Cold evidence gathering searches within the complete safe `sourceScope`, then reads only request-relevant authoritative
files and decisive excerpts needed to support the requested meaning. Eligibility does not require loading every file into
the host conversation. Existing current JSON 1 is reused; authority, selected evidence, required examples, and rubric
content are never truncated.

### MCP discovery and user handoff

Audit real `tools/list`/`prompts/list` descriptions, required/default argument schemas, prompt/tool byte parity, and stdio
invocation so the host discovers `diagram_generation_workflow` first and receives complete efficient/recovery guidance.
The workflow description says it owns efficient execution, timeout recovery, and final user-link reporting. Both generation
tool descriptions use the same contract language: generated success returns structured `editUrl` plus a visible clickable
editor link which the host must present to the user; blocked/error results contain no link; a client timeout never permits
an unchanged retry. Discovery tests assert these exact clauses rather than only a description prefix.

Normal `_generation_tool_result` already owns the Markdown editor link and structured payload, so implementation preserves
one owner and strengthens exact transport/stdio assertions instead of adding another result formatter. Finalized no-op
request status and generation preflight recovery expose the existing canonical `diagramPath` plus backend-built `editUrl`,
allowing the host to present **Open in the GraphPilot editor** after a lost generation response without deriving a URL or
regenerating. Workflow instructions explicitly require the final user report to surface this clickable link, not merely
filesystem paths.

### Timeout recovery

A client timeout never authorizes the same readiness or generation call again. This is an MCP-client transport loss: the
backend does not receive a timeout exception and may still be running, so no fabricated `readiness_timeout` or
`generation_timeout` operation code is added. Azure/provider timeouts continue to map through the existing typed provider
availability errors. After a readiness client timeout, the host stops rather than guessing a policy from an unknown result.
Timeout recovery adds no tool or parameter. After a generation client timeout, the host calls `diagram_request_save` with
the unchanged complete candidate and exact current digest; this provider-free exact no-op returns `finalized: true` plus
the existing `diagramPath` and backend-built `editUrl` when the owned output committed. The host then reads that canonical
JSON through its local file access, verifies request/mode/digest ownership, calls inline `diagram_validate`, and calls
path-backed `diagram_render` only if the SVG is absent or the completed result recorded render failure. It presents the
returned editor link to the user. `finalized: false` means completion is not established, so the outcome remains unknown
and the host stops instead of polling or rerolling. An accidental later generation re-entry is independently rejected by
the pre-provider finalization check.

`DiagramRequestPersistenceService.require_generation_target_available(loaded_request)` is the new shared public preflight.
Both `generate_direct` and `generate_context` call it immediately after `_load_request()` and before final readiness or any
other provider call. It checks exact request ID, mode, digest, path, canonical target, and sibling-only conflicts using the
existing finalization/ownership rules. An exact owned output raises `DiagramRequestFinalizedError`, mapped to the existing
`request_finalized` problem with canonical path/link; a foreign, corrupt, digest-mismatched, or sibling-only target raises
`DiagramNameConflictError`, mapped to existing `diagram_name_conflict`. The existing exclusive canonical create and final
digest recheck remain the race-safe final gate.

### Provider telemetry

The strict LLM seam returns private `LLMResponseDocument(dict)` with read-only optional `input_tokens` and
`output_tokens` attributes; its mapping contains only the parsed provider document, so JSON shape, schema validation,
plain-dict custom clients, and public result content remain unchanged. `_parse_content` reads only exact OpenAI SDK
`usage.prompt_tokens` and `usage.completion_tokens` integer fields, bounds them to the observer contract, and otherwise
stores null. Fake/custom clients may return `LLMResponseDocument` for deterministic usage tests or a normal dict to prove
compatibility. Tokens are never estimated from bytes and no `{content,usage}` response envelope is introduced.

Readiness owns immutable `ReadinessProviderCallEvent` and optional
`Callable[[ReadinessProviderCallEvent], None]`. `ContextReadinessService.assess`/`assess_bound` accept that keyword-only
callback and emit reached readiness/response-repair start/completion/failure events without importing generation.
`DiagramGenerationService` translates them into existing `GenerationProviderCallEvent` values and replays them to
optional diagnostics after the final readiness result establishes the run. Injected readiness stubs retain their existing
one-argument call path. Readiness, generation, deterministic repair, semantic review, response repair, and semantic
candidate repair measure local monotonic elapsed time around each logical strict call; the SDK does not supply duration.

The context generation observer includes mandatory final-readiness calls in result/trace/debug provider counts and retains
the existing `readiness`, `readiness_response_repair`, generation, and semantic role distinctions. Result
`providerCallCount` and compact trace totals both count every reached final-readiness-through-review logical call exactly
once. Every completed production call has measured duration rather than an absent value coerced to zero. Telemetry remains
observational: it cannot affect retries, acceptance, candidates, or persistence.

### Benchmark and live boundary

`ContextPerformanceRecoveryBenchmarkTests` in existing
`backend/tests/generation/test_diagram_generation_service.py` owns one repeatable harness using the
`return-authorization` context training fixture, injected strict fake responses, a 20 ms per-call delay, and a fresh
`TemporaryDirectory` workspace. The before/after scenarios are: (1) cold JSON 1/request creation followed
by the normal ready workflow; (2) warm current-JSON-1 reuse with a new request; (3) generated-output re-entry representing
a lost response; and (4) optional usage supplied versus omitted. It records workflow/candidate/result UTF-8 bytes, total
roles, result/trace call counts, per-call duration/tokens, and recovery calls. Results live in this slice's `Outcome`, not a
second benchmark document. Wall-clock totals are descriptive; deterministic gates are ready-path calls **4 → 3**, lost-
response re-entry calls **3 → 0**, exact trace/actual role parity, positive delayed-fake durations, supplied token equality,
and null omitted usage.

After implementation audit and all offline gates, the session records the live budget state as `not_started`, then changes
it exactly once to `attempted` or `skipped`. At most one warm live context-generation attempt may use the unique name
`graphpilot-context-performance-recovery-bdd`; there is no standalone readiness call and no retry. The attempt proceeds
only if existing evidence is still current; otherwise it is skipped. This manual session gate is sufficient because the
slice adds no production job/run ledger. The report separates visible Copilot-credit delta when available from Azure
provider role/count and never treats fake/offline evidence as live certification.

### Reversibility

Prompt rollback restores standalone readiness as the normal precursor and removes the new timeout instructions. Service
rollback removes the preflight entry point/call, readiness telemetry callback, dict-compatible usage metadata, and local
timers while retaining existing request finalization, exclusive create, schemas, and provider behavior. No persisted
canonical format, migration, environment setting, dependency, or public tool name is added, so rollback requires no user
artifact rewrite or deletion.

## Plan Audit

Result: **Pass.** The first independent review correctly confirmed the late-conflict, missing-telemetry, omitted-readiness,
and duplicate-work baselines but initially treated planned implementation as absent work and proposed backend timeout codes
for a client-side transport loss. The corrected re-audit found no material issue. Its seven minor specification requests are
resolved here: one final-readiness assessment is explicit; the shared preflight method and exact exceptions are named; the
existing benchmark test owner and deterministic thresholds are fixed; dict-compatible usage metadata and the readiness-
owned callback are exact; timeout recovery uses existing no-op save/validate/render tools with no new API; discovery
clauses and link behavior are testable; and rollback/live-budget boundaries are explicit. Canonical owners, mandatory
readiness/reviewed quality/strictness, complete authority/examples, digest/persistence gates, reversibility, isolated
benchmarks, MCP link handoff, and focused plus complete verification coverage are all accounted for.

## Included Work

- Update the public workflow prompt and MCP workflow owner for targeted evidence inspection, final-readiness-first normal
  generation, and explicit no-rerun timeout recovery.
- Add pre-provider exact finalized-output and target-conflict checks for direct and context generation.
- Capture strict-call elapsed duration and available provider token usage without changing provider requests or responses.
- Include final-readiness calls in context generation provider summaries, compact trace, and optional diagnostics.
- Audit and tighten MCP prompt/tool descriptions, discovery schemas, real stdio workflow execution, generated Markdown plus
  structured `editUrl`, finalized recovery link exposure, and explicit host instructions to present the clickable link.
- Add regression tests for workflow bytes/semantics, one-fewer normal readiness call, zero-call completed-output recovery,
  foreign target rejection, timing/token capture, missing-usage behavior, trace role/count totals, discovery descriptions,
  prompt/tool parity, and generated/blocked/recovered link behavior.
- Run identical isolated fake-provider benchmarks before and after; record cold/warm and retry comparisons.
- Update canonical generation/context/MCP/error docs, backend implementation guidance, decision index where behavior changes,
  delivery status, and this outcome.
- Optionally run the single budgeted warm live attempt only after all offline gates and evidence-freshness checks pass.

## Not In Scope

- Async generation jobs, queues, background workers, polling APIs, streaming, or MCP-client timeout configuration.
- A second generation call, automatic retry, provider reroll, or regeneration to recover SVG/trace/debug/output text.
- `standard` quality mode, removal of final readiness/final semantic review, or weaker schema/provenance/digest/persistence
  gates.
- Truncating authority, evidence, rubrics, selected claims, or either required generation example.
- Changing Azure deployment, reasoning effort, timeout, credentials, or `.env`.
- `json_object` or any other structured-output fallback.
- Rebuilding missing historical live diagnostics, repeating the expensive cold live run, certification, freeze, promotion,
  frontend behavior, or Epic 4 editing.

## Target Areas

- `backend/assets/prompts/diagram-generation-workflow-v1.md`
- `backend/assets/prompts/context-workflow-branch-v1.md`
- `backend/mcp_server/server.py` and `backend/mcp_server/smoke_test.py`
- `backend/services/llm/llm_client.py`
- `backend/services/readiness/context_readiness_service.py`
- `backend/services/context/diagram_request_persistence_service.py`
- `backend/services/generation/pipeline/diagram_generation_service.py`
- `backend/services/generation/pipeline/pre_layout_generation_service.py`
- `backend/services/generation/review/semantic_review_service.py`
- relevant backend generation/readiness/LLM/request/MCP tests
- `docs/01-architecture/03-mcp-tools/`
- `docs/02-design-and-features/04-generation-design.md`
- `docs/02-design-and-features/08-context-backed-generation/`
- `backend/README.md` and delivery owners

## Exit Criteria

- A normal ready context workflow performs no standalone readiness call and saves exactly one logical readiness provider
  call while generation still executes mandatory final readiness.
- Workflow guidance requires targeted evidence reads within complete scope and forbids unchanged timeout retries.
- Exact owned/finalized and conflicting output states are detected before any readiness/generation/review provider call.
- Timeout recovery validates/reuses canonical JSON and renders only from saved JSON when needed; it never regenerates.
- Successful final-readiness/generation/review calls expose measured nonnegative durations and available SDK token counts;
  omitted usage remains null and never becomes an estimate.
- Context result/trace/debug provider role/count includes final readiness and all reached repair/review calls exactly once.
- MCP prompt/tool discovery descriptions and argument schemas lead the host through the efficient workflow; generated and
  finalized-recovery transports expose the backend-built `editUrl` in structured content, generated visible Markdown uses
  the clickable editor link, workflow instructions require presenting it to the user, and blocked/error results expose none.
- Real stdio proves workflow discovery/instruction parity through generated user-facing link transport end to end.
- Fake cold/warm before/after benchmarks and focused regression tests pass in isolated temporary workspaces.
- Existing architecture JSON validates and renders byte-identically without being regenerated or overwritten.
- Django check, real stdio smoke, check-only readiness calibration, complete backend tests, frontend verification, and
  `git diff --check` pass; implementation audit has no unresolved finding.
- At most one uniquely named warm live context generation is attempted after the offline gates, with the budget stated
  first, no standalone readiness, no retry, and Copilot credits separated from Azure provider roles/count.
- No `.env`, secret, existing `.graphpilot` artifact, Git configuration, remote branch, or hidden certification state is
  inspected, changed, deleted, replaced, or pushed.

## Previous Slice

[`12-workflow-client-compatibility.md`](12-workflow-client-compatibility.md)

## Next Slice

No planned successor inside this group. Resume Epic 4 planning after this bounded follow-up is complete.

## Outcome

**Completion:** Implemented and independently audited the bounded performance/recovery slice. The normal context workflow
now goes directly to generation's one freshly loaded mandatory final-readiness gate, performs targeted rather than
whole-scope host reads, rejects malformed policy and finalized/conflicting targets before provider use, and gives
client-timeout recovery one provider-free finalized-status path with visible plus structured editor link. Strict LLM
responses retain their JSON shape while carrying exact optional SDK token usage; final readiness, generation, and every
reached repair/review role now have measured duration and appear exactly once in context result/trace/debug totals. MCP
prompt/tool discovery, descriptions, parity, generated/recovered clickable links, and blocked/error no-link behavior are
covered through unit and real stdio checks. The live blocked result also exposed and fixed readiness blocks being mislabeled
as `semantic_review` in terminal diagnostics; focused coverage now requires terminal stage `readiness`.

**Benchmark:** The identical isolated delayed-fake ready path fell from four provider calls (standalone readiness plus
three generation-path calls) to three, a 25% reduction; complete workflow wall time fell from 1,750.583 ms to 1,514.648 ms
(13.5%). Trace reporting changed from two reported versus three actual calls to exact 3/3 readiness/generation/review
parity with measured 20.703/23.116/20.584 ms calls. Completed-output re-entry fell from three calls and 433.736 ms to zero
calls and 70.306 ms. After a second wording pass, rendered workflow instructions fell from the 8,634-byte baseline to
8,228 bytes (4.7%) while adding source-targeting, timeout, and link guidance. Injected-usage coverage proves exact token
aggregation (964 input/194 output); omitted usage remains null.

**Live evidence:** Budget state is `attempted` (1/1), with unique request
`graphpilot-context-performance-recovery-bdd`, current six-file evidence, no standalone readiness, and no retry. The one
call did not time out but correctly returned `outcome: blocked` at final readiness (`needs_context`, score 81) before any
generator/write. Readiness used 112,631.031 ms and 15,130/11,632 input/output tokens; strict response repair used
349,535.310 ms and 15,114/11,171 tokens. The non-overrideable blocker found that an architecture-overview scope could not
also verify telemetry/transport behavior; a second blocker required missing transport/telemetry evidence. No diagram,
SVG, trace, or editor link was created. Diagnostics are under the unique gitignored run. Copilot credit delta was not
visible in Devin; Azure roles/count/tokens/durations are recorded separately. The 462.2-second readiness pair makes
response-repair avoidance the evidence-backed remaining performance target; it was not guessed at or retried in this
exhausted live budget.

**Verification:** Focused regression gate passed 199 tests (1 skipped); final backend gate passed **880 tests (5
skipped)**. `uv run python manage.py check`, real stdio smoke, check-only readiness calibration (`valid: true`,
`releaseStatus: not_run`), `git diff --check`, and independent implementation re-audit passed. `npm run verify` passed
lint, build/typecheck, **419** unit/component tests, and **43** Chromium E2E tests; the existing non-failing chunk-size
advisory remains.

**Deviations / follow-up:** The benchmark owner lives in the existing context-generation service test module rather than
further enlarging the direct-generation module. No async job/polling API, provider/configuration change, quality fallback,
authority/example truncation, schema weakening, `.env` access, existing-artifact replacement, certification, or push
occurred. A future separately planned slice may use the new telemetry and safe validation-issue diagnostics to reduce
readiness response-repair frequency/latency without another live attempt under this slice.
