# Slice 15: Full Workflow Performance Audit

## Purpose

Audit the complete user-visible context-backed GraphPilot workflow from the user's request through source gathering, JSON 1
and JSON 2, MCP, mandatory final readiness, reviewed generation, persistence/rendering, timeout recovery, and visible editor
completion. Measure cold and warm critical paths, assign every material delay or failure to host work, Azure provider wait,
MCP/runtime overhead, or local deterministic work, and rank the smallest safe fixes by expected user-visible impact.

The frozen `high` versus `medium` reasoning-effort matrix remains one subordinate controlled Azure-role experiment. It does
not define the audit, hide host/MCP/local bottlenecks, or authorize a runtime effort change.

## Background

Context S13 established the first separated host/provider/local evidence: the cold Copilot-host observation reached about
129.6K host-context tokens and about 374 visible Copilot credits while recreating JSON 1; the real architecture artifacts
were 21,047 compact JSON 1 bytes, 6,705 JSON 2 bytes, 64,319 readiness-projection bytes, and 59,811 generation-wire bytes;
and an isolated fake-provider generation path took about 1.5 seconds. S13 also removed duplicated standalone readiness from
the normal host path, instrumented provider calls, and added provider-free finalized-output recovery after a lost MCP
response.

Context S14 measured one identical blocked BDD request at two operator-only reasoning efforts:

| Metric | High | Medium |
| --- | ---: | ---: |
| Readiness calls | 2 | 1 |
| Provider duration | 462,166.341 ms | 77,941.939 ms |
| Input tokens | 30,244 | 15,130 |
| Completion tokens | 22,803 | 6,698 |
| Medium reasoning tokens | unavailable | 4,608 |
| Status / score | `needs_context` / 81 | `needs_context` / 61 |

Medium eliminated response repair and reduced provider duration 83.1%, but added three conservative facet blockers. It
preserved the non-overrideable scope blocker and secondary evidence blocker and never returned false ready. One conflicted
case cannot establish parity, reviewed-generation quality, stability, or a runtime setting.

### Scope clarification and preserved work

On 2026-07-22 the user clarified that S15's primary deliverable is the full workflow performance audit, with H/M retained
only as a controlled subexperiment. Before that clarification, initial uncommitted H/M implementation already existed in the
working tree. This is an unavoidable workflow deviation from the required plan-first cadence. The documentation-only plan
checkpoint must explicitly stage only revised planning documents, preserve every implementation file byte-for-byte, and
commit before further implementation. The existing code is reused as the provider/backend measurement component after the
checkpoint; it is not discarded, rewritten merely to match the new title, or treated as proof that the broader audit is
complete.

The existing readiness release calibration and reviewed-generation certification remain separate. Their human-label and
repeat requirements are neither satisfied nor replaced by this visible, non-certifying audit.

## Design

### 1. Define one complete critical path

The end-to-end clock starts when the host receives the user's diagram request and stops when the returned editor link has
loaded the persisted diagram visibly, where browser execution is safe. Each observation records explicit cold/warm state,
diagram type, basic/complex case, artifact-reuse state, process/cache state, start/end timestamps, outcome, and measurement
coverage.

- **Cold workflow:** a new host task, no reusable JSON 1/JSON 2 for that fixture, a new MCP process, and cold in-process
  schema/rubric/example caches.
- **Warm workflow:** a new user request whose current JSON 1 is reusable, whose JSON 2 needs only measured reconciliation or
  exact no-op persistence, and whose MCP/runtime caches are already populated.
- Artifact reuse and process-cache state are also recorded independently so a “warm” result never ambiguously combines the
  two effects.
- Complete wall time is not the sum of nested spans. Reports use one non-overlapping critical-path attribution and retain
  nested role/stage details separately.
- Historical S13/S14 observations retain their actual coverage. Missing boundaries are labeled `not_measured`; no complete
  wall time or percentage is fabricated from partial evidence.

### 2. Measure all user-visible boundaries

| ID | Workflow boundary | Primary measurement owner | Required evidence |
| --- | --- | --- | --- |
| W01 | User request and host-workflow routing | Host/Copilot | elapsed, route selected, host tokens/credits when available |
| W02 | Repository/source discovery and inspection | Host/Copilot | elapsed, searches, source reads, bytes/excerpts inspected |
| W03 | Evidence gathering and JSON 1 construction | Host/Copilot | elapsed, authoring/reconciliation actions, output bytes |
| W04 | JSON 1 validation, digest, reconciliation, persistence | Host + local | host elapsed; local validation/digest/read/compare/write spans and outcome |
| W05 | JSON 2 framing, validation, digest, persistence | Host + local | host authoring elapsed; local validation/digest/read/compare/write spans and outcome |
| W06 | MCP process, transport, and tool invocation | MCP/runtime | startup, initialize/discovery, request transport, dispatch, serialization, response bytes |
| W07 | `DiagramGenerationService.generate_context(require_ready)` | MCP + local orchestrator | entry/exit, request load/preflight, outcome, child span identities |
| W08 | Mandatory final readiness exactly once | Azure + local | invocation count, projection/validation self time, exact provider role metrics |
| W09 | Optional readiness response-contract repair | Azure + local | trigger diagnostics, full repair role metrics, validity and outcome |
| W10 | Generation packet and fixed-example loading | Local | construction/load/cache spans, bytes by authority/example/rubric component |
| W11 | Strict logical generation | Azure | exact generation role metrics and response validity |
| W12 | Deterministic validation and repair | Local + Azure repair | validation self time/issues; repair role metrics only when reached |
| W13 | Reviewed semantic review | Azure | exact semantic-review role metrics and score/findings outcome |
| W14 | Semantic-review response repair | Azure + local | trigger diagnostics, role metrics, validation self time |
| W15 | Semantic candidate repair and mandatory final review | Azure + local | repair/final-review calls, validations, accepted/blocked outcome |
| W16 | PyGraphviz layout | Local | engine/load/layout duration, graph size, success/failure |
| W17 | Canonical assembly, provenance, and context stability | Local | assembly and each validation span/outcome |
| W18 | Atomic persistence | Local | final digest recheck, exclusive write duration/bytes/outcome |
| W19 | SVG rendering | Local | load/render/write duration, input/output bytes/outcome |
| W20 | MCP result serialization and editor-link return | MCP/runtime | result construction/serialization bytes and client-visible return time |
| W21 | Timeout and finalized-output recovery | MCP/runtime + local | timeout boundary, no-rerun behavior, no-op recovery spans/calls/outcome |
| W22 | Editor-link load and visible completion | Local (browser/frontend) | navigation-to-visible elapsed, API/network/console failures, rendered diagram identity |

Every boundary is either measured, deterministically derived from measured parent/child spans, or explicitly marked
unavailable with a reason and the smallest proof needed to close it.

### 3. Keep four accounting domains separate

#### Host/Copilot work

Capture host elapsed time; route decisions; search/read/tool counts; inspected bytes when available; JSON 1/JSON 2 authoring,
reconciliation, and correction effort; and host tokens/credits only when the host exposes them. A manual/imported host trace
must identify its source and coverage. Copilot credits are never converted into Azure calls, tokens, or cost.

#### Azure provider work

For every exact role (`readiness`, `readiness_response_repair`, `generation`, `generation_repair`, `semantic_review`,
`semantic_review_response_repair`, and `semantic_repair`) capture call state, monotonic duration, request/response bytes,
prompt/completion/reasoning/cached tokens, requested/effective effort, provider request ID, service tier, first-response
validity, bounded repair diagnostics, and final role outcome. Missing SDK metadata remains null and is never estimated.

#### MCP/runtime overhead

Measure process startup and initialization separately from tool-call transport. For each call record client wall time, server
tool wall time, request/result bytes, serialization time, and the bounded residual attributable to transport/dispatch. Track
cold versus reused process state. Exercise client-timeout and provider-free finalized-output recovery without polling,
unchanged generation retry, or fabricated backend timeout codes.

#### Local deterministic work

Measure exclusive self time for schema/semantic validation, digesting, reconciliation, context/request persistence, packet
construction, rubric/example loading, response validation, layout, canonical assembly, provenance/context-stability checks,
atomic diagram persistence, SVG rendering, and result construction. Provider child waits are excluded from local self time.
Capture cache hit/miss and relevant bounded input/output bytes where observable.

For a complete observation, the report attributes non-overlapping wall time to these domains and gives both absolute duration
and percentage of complete wall time. Nested details may explain a domain but may not be added again. Any uninstrumented
residual is shown explicitly rather than assigned by assumption.

### 4. Use staged evidence

The audit phases below are distinct from the H/M live matrix's Stage A/B/C gates.

#### Audit Phase A — reconcile S13/S14

- Preserve the committed cold/warm host observations and exact S13/S14 provider records.
- Recalculate only directly supported durations, bytes, call counts, repair rates, and partial-path contributions.
- Identify incompatible clock scopes, missing spans, and unavailable host telemetry instead of merging them.
- Build one evidence ledger that names source, case, timestamp, cold/warm state, coverage, and confidence.

#### Audit Phase B — complete offline instrumentation

- Add or verify observational spans for every measurable W01–W22 boundary.
- Reuse production observers and services; add operator/evaluation-only adapters around host, MCP client, and browser
  boundaries that production cannot observe internally.
- Keep public MCP results, runtime requests, prompts, schemas, labels, settings, repair budgets, and architecture unchanged.
- Persist only bounded safe metrics and identities: no raw source dumps, prompts, rejected provider responses, hidden
  reasoning, secrets, or oracle content.
- Prove instrumentation failure isolation and compare instrumented versus uninstrumented fake runs for identical canonical
  output and call sequence.

#### Audit Phase C — provider-free workflow fixtures

Run the existing six generation fixtures (basic and complex for Activity, Use Case, and BDD) once cold and once warm through
the complete safe fake-provider workflow, then add repetitions only where timing variance prevents a supported conclusion.
The baseline schedule is therefore 12 provider-free end-to-end observations and makes zero Azure calls.

Measure host-fixture orchestration, JSON 1/JSON 2 construction and persistence, MCP startup/transport, production
`generate_context(require_ready)`, exactly one final readiness assessment, all reached fake-provider roles, local stages,
serialization, finalized-output recovery, and editor-link loading for representative outputs where browser execution is safe.
Use controlled delays only to prove attribution and timeout behavior; do not present injected delay as performance evidence.
Fixture-host orchestration is labeled simulated rather than Copilot work, and fake-client role duration is local test-harness
cost rather than Azure wait. Neither supplies host tokens/credits, Azure latency, or live quality evidence.

#### Audit Phase D — frozen H/M Azure-role experiment

Retain the immutable visible matrix without automatic expansion:

- readiness: nine cases = three diagram types × `ready|ready_with_warnings|needs_context`;
- generation: six genuinely ready cases = basic/complex per diagram type;
- conditions: `H=high` and `M=medium`, with deployment/API/prompts/schemas/rubrics/examples/layout/repair budgets fixed;
- exact paired balanced order, immutable observations, no replacement case, favorable rerun, or completed-cell retry.

The matrix uses production final readiness and reviewed generation. It does not call standalone readiness before generation,
and it captures the same W08–W19 provider/local boundaries as the broader audit.

##### Matrix Stage A — offline proof

No provider construction or calls: validate cases/labels/oracles/refs/versions, prove oracle isolation, materialize the exact
schedule and ceilings, fake-run both conditions through production paths, and prove immutable capture, resume, stop, redaction,
and report bounds.

##### Matrix Stage B — one screening repeat

Only after a separate explicit authorization for this exact schedule and ceiling:

```text
Readiness: 9 cases × 2 efforts = 18 assessments
Generation: 6 cases × 2 efforts = 12 attempts

Readiness maximum: 18 × (1 readiness + 1 readiness-response repair) = 36 Azure calls
Generation maximum: 12 × (1 readiness + 1 readiness-response repair + 1 generation
                    + 1 generation repair + 2 semantic reviews
                    + 2 semantic-review response repairs + 1 semantic candidate repair)
                   = 108 Azure calls
Stage B hard maximum: 144 Azure calls
```

The complete run stops immediately after any medium condition produces a false ready, misses a mandatory non-overrideable
blocker, invents/invalidates refs or actions, reaches canonical/schema/provenance failure, loses required meaning, adds a
material unsupported assertion, or breaches a role/total call budget. Completed observations remain immutable. This cap does
not change unless a newly revised audited plan declares another budget and the user explicitly authorizes it.

##### Matrix Stage C — two stability repeats

Only after the Stage B report and a separate explicit stop/go approval. Two further repeats may run only for frozen surviving
cells. The absolute original full-matrix ceiling remains 432 Azure calls. Stage C cannot expand the manifest, add retries,
replace stopped cells, or reroll quality.

#### Audit Phase E — attribute and rank

Attribute each slow/failed cell to the narrowest confirmed or best-supported owner before recommending change. Rank by
expected complete user-visible wall-time or reliability impact, not implementation convenience. Do not optimize layout or
rendering when host/provider work dominates, introduce asynchronous jobs to disguise provider latency, change effort before
hard quality gates pass, or truncate authority, rubrics, or examples.

### 5. Preserve H/M quality and decision gates

Medium fails a role if any cell/repeat has a false ready, missing mandatory non-overrideable blocker, invalid reference/action,
canonical/schema/provenance failure, missing required generation meaning, material unsupported addition, or higher unresolved
semantic-block rate than high. No aggregate average can hide a failing type/status cell.

For Stage C, each surviving cell must hold the readiness boundary and required findings/actions in `3/3`, remain within
adjudicated facet/score bands, retain required generation meaning and hard validation in `3/3`, and show no repair variance
that changes accepted meaning. Only after all hard/stability gates pass may medium satisfy the performance gate through at
least 30% lower paired median provider duration, at least 30% fewer reasoning tokens, or a materially lower repair/call rate.

| Result | H/M subsection recommendation |
| --- | --- |
| Medium passes readiness and generation gates with material benefit | Shared `medium` candidate |
| Generation passes but readiness fails | Shared `medium` plus at most one readiness-only `high` candidate |
| Readiness passes but generation fails | Shared `medium` plus at most one generation-only `high` candidate |
| Medium fails both or lacks material benefit | Retain shared `high` candidate |
| Both efforts repeat the same repair defect | Fix the prompt/schema/validator owner before choosing effort |
| Medium is faster but conservative or unstable | No promotion; retain current behavior and diagnose quality owner |

These are recommendations for explicit review, never automatic promotion. A runtime setting, prompt, schema, label, or
architecture change requires a separately approved implementation slice and its own proof.

### 6. Produce one complete bottleneck report

The durable report must show:

- total cold and warm workflow time with measurement coverage;
- stage-by-stage critical path for W01–W22;
- absolute and percentage host, Azure, MCP, local, and uninstrumented-residual contribution;
- duplicated/avoidable work, cache behavior, repair behavior, timeout/recovery behavior, and quality failures by case;
- H/M comparison as one clearly subordinate subsection;
- ranked solution design, recommended next implementation slice, strongest alternative, decisive trade-off, unresolved
  risks, and smallest next proof.

For every material slow or failed stage, include exactly these decision inputs:

1. measured evidence;
2. absolute and percentage contribution to complete wall time;
3. accounting domain (`host`, `azure`, `mcp`, or `local`);
4. confirmed or best-supported root owner and confidence;
5. smallest safe fix;
6. strongest alternative;
7. quality/security/compatibility trade-off;
8. expected time/token/call/reliability benefit;
9. smallest offline proof;
10. required live proof;
11. disposition: implement now, plan separately, or defer.

Partial historical evidence may populate a stage row only with its coverage caveat. A final percentage requires a complete
observation denominator.

### 7. Keep changes reversible and gated

Instrumentation is additive, observer-driven, bounded, and removable without changing generation semantics. Evaluation
artifacts live only in dedicated control/evaluated roots with exact identities, immutable completion, and exclusive writes.
Production request/context/diagram artifacts remain authoritative and unchanged by analysis. Model output cannot modify code,
prompts, labels, settings, schedules, or reports.

After evidence identifies a candidate fix: change one bounded owner, run the smallest offline proof, obtain any required live
budget, rerun only the predeclared affected proof, and rerun the complete applicable gate before promotion. Provider-backed
release certification remains `not_run` unless its separate process passes.

### Agent execution prompt

```text
Run GraphPilot Context S15 as a full user-visible workflow performance audit. H/M reasoning effort is only one controlled
Azure-role subexperiment.

Repository: C:\Users\w105098\Desktop\Projects\GraphPilot

Start with AGENTS.md, .devin/rules/graphpilot.md, the required README/current-state/design-decision read order, the nearest
backend/docs README files, and this S15 plan. Preserve .env, remote state, user artifacts, and unrelated files; never push.

Hard sequence:
1. Revise and audit this plan for all 22 workflow boundaries, four accounting domains, budgets, reversibility, and proof.
2. Explicitly stage and commit only the audited documentation plan while preserving all existing uncommitted implementation.
3. Record that initial H/M implementation predates the scope clarification and reuse it after the checkpoint.
4. Reconcile S13/S14 without fabricating missing clocks or conflating Copilot credits with Azure usage.
5. Add/verify observational instrumentation for host, MCP, provider, and local boundaries without runtime behavior changes.
6. Run provider-free cold/warm basic/complex fixtures, timeout recovery, and safe editor-link checks.
7. Audit each slow/failed stage, attribute its owner, and produce the complete ranked bottleneck report.
8. Retain the frozen H/M matrix and its quality gates. Do not expand it automatically.
9. Run required backend/frontend/MCP/browser verification, audit the diff, update canonical delivery docs, and commit coherent
   offline work.
10. Before Matrix Stage B, print the exact balanced schedule and the 144-call hard maximum, then stop. Azure Stage B and C
    require separate explicit user authorization.

Never call standalone readiness before context generation. Final readiness occurs exactly once inside
DiagramGenerationService.generate_context(require_ready). Preserve reviewed quality/final review, strict output/no fallback,
complete authority, fixed examples, provenance, digest binding, atomic persistence, PyGraphviz, and stage-correct recovery.
Do not automatically promote a runtime setting, prompt, schema, label, or architecture change.
```

## Plan Audit

Result: **Pass.** Independent read-only review found no material defect. It verified the full workflow as primary, all 22
boundaries, non-overlapping complete-wall attribution, historical coverage caveats, strict host/Azure/MCP/local separation,
provider-free cold/warm basic/complex coverage, the subordinate immutable H/M matrix, exact 36 + 108 = 144 Stage B call
ceiling, separate Stage C approval, quality/stop/no-reroll gates, timeout recovery, editor completion, report fields,
reversibility, security, compatibility, canonical ownership, and offline/live verification. Self-audit additionally made
browser completion explicitly local and fake-client timing explicitly local harness cost rather than Azure evidence. The
plan is ready for an explicit documentation-only checkpoint that preserves all pre-clarification implementation files.

## Included Work

- Reconcile S13/S14 cold/warm host, provider, MCP, and local evidence into one coverage-aware ledger.
- Instrument or verify all measurable W01–W22 boundaries without changing runtime semantics or public contracts.
- Run provider-free cold/warm basic/complex fixtures across all three diagram types and recovery paths.
- Preserve and complete the existing H/M case, manifest, runner, capture, analysis, and report component.
- Retain the 9-case readiness and 6-case generation matrix, immutable schedule, budgets, resume/stop/no-reroll rules, and
  hard quality gates.
- Produce the complete stage-attributed bottleneck report and rank smallest safe fixes by user-visible impact.
- Verify backend, MCP, frontend, browser-safe editor loading, security/redaction, and instrumentation equivalence.
- Update delivery owners/outcome and commit coherent offline checkpoints before any live gate.

## Not In Scope

- Running H/M Matrix Stage B or C without their exact separate live authorizations.
- Expanding the frozen matrix, adding conditions/cases/repeats by convenience, replacing failures, or favorable reruns.
- Automatically changing or promoting runtime effort, prompts, schemas, rubrics, labels, examples, architecture, or settings.
- Weakening readiness, strict generation, reviewed semantic quality/final review, provenance, digest/persistence, or layout.
- Truncating authority, rubrics, or examples; persisting raw provider content/reasoning/secrets/source dumps/oracles.
- Introducing asynchronous jobs merely to hide synchronous provider latency.
- Treating provider-free timings or one S14 H/M case as live quality/performance certification.
- Editing `.env`, user-owned artifacts, Git configuration, remote state, or pushing.

## Target Areas

- host-workflow and MCP prompt/tool measurement adapters
- `backend/mcp_server/` transport/serialization boundaries
- `backend/services/readiness/`, `generation/`, `core/`, `support/`, and `evaluation/`
- `backend/assets/schemas/` for bounded evaluation-only metric artifacts
- `backend/tests/` provider-free boundary, fixture, recovery, and equivalence coverage
- `frontend/e2e/` only where editor-link visible completion needs repeatable proof
- S13/S14 evidence, backend/testing/MCP documentation owners, this group/epic, and the current-state board

## Exit Criteria

- The audited plan and implementation map every W01–W22 boundary to a measured span, derived value, or explicit
  `not_measured` reason and next proof.
- Cold/warm complete observations use one non-overlapping wall-time denominator and separately report host, Azure, MCP,
  local, and residual absolute/percentage contributions.
- S13/S14 evidence is reconciled without unsupported clock alignment or Copilot/Azure conflation.
- The provider-free six-case basic/complex matrix runs cold and warm with zero Azure construction/calls and proves exactly one
  final readiness assessment inside generation, reached-role attribution, local stages, MCP overhead, recovery, and safe
  editor-link completion where applicable.
- Instrumented and uninstrumented fake runs have identical provider-call order, result, canonical JSON, SVG, and persistence
  behavior; diagnostics remain bounded and failure-isolated.
- The H/M package remains immutable, visible, non-certifying, and subordinate; Stage B cannot exceed 144 Azure calls or start
  without exact authorization, and Stage C retains a separate stop/go gate.
- The complete bottleneck report contains every required per-stage field, ranks by user-visible impact, and states evidence
  coverage, strongest alternatives, trade-offs, unresolved risks, and smallest offline/live proofs.
- No runtime setting/prompt/schema/label/architecture change is promoted automatically and no authority/rubric/example is
  truncated.
- Plan and implementation audits, focused/full backend tests, Django check, real stdio smoke, frontend verify, browser-safe
  checks, and diff/security review pass; exact commands/results are recorded.
- Canonical delivery docs and final `Outcome` are current; coherent commits contain no `.env`, unrelated, user, remote, or
  push changes.

## Previous Slice

[`14-readiness-effort-evaluation.md`](14-readiness-effort-evaluation.md)

## Next Slice

Use the ranked bottleneck report to propose one separately approved smallest-fix slice. The H/M subsection may instead
recommend a bounded effort proof or no change, but cannot promote it automatically.

## Outcome

**Status:** The full offline workflow audit, instrumentation, provider-free matrix, recovery proof, browser check, and H/M
Stage A package are complete. No Azure call, runtime setting, prompt, production schema, case label, or architecture
promotion, authority/rubric/example truncation, `.env` access, or push occurred; the new schemas are bounded evaluation-only
artifacts from the audited package. Matrix Stage B was later explicitly authorized but stopped after 4/144 calls without
an evaluable readiness pair; no cell was rerun, no Stage C gate opened, and Stage C remains unauthorized.

### Evidence coverage and limits

| Evidence | Coverage | What it can establish |
| --- | --- | --- |
| S13 cold host record | About 129.6K Copilot host-context tokens and 374 visible credits while recreating JSON 1 | Host context/credit magnitude only; elapsed/search/read counts are unavailable |
| S13 high live path | Final readiness 112,631.031 ms plus response repair 349,535.310 ms; 30,244 input and 22,803 completion tokens | Exact Azure readiness subpath; not complete user-request-to-editor wall time |
| S14 medium live path | One 77,941.939 ms readiness call; 15,130 input, 6,698 completion, 4,608 reasoning, zero cached tokens | Exact Azure readiness subpath and one-case H/M direction; not semantic parity/certification |
| S15 Stage B live stop | First Activity-ready H/M pair attempted; two readiness + two repair calls, then terminal stop | Exact 4-call role/state count and repeated repair need; durations/tokens/response diagnostics were lost by the now-fixed terminal-observation bug |
| Historical warm artifacts | JSON 1 `23:12:43`, JSON 2 `23:14:23`, diagram `23:22:21` | A 578-second artifact interval containing unknown host/provider/idle work; not a controlled wall clock |
| S15 provider-free matrix | Six basic/complex generation cases × cold/warm over real stdio; 36 fake calls, zero Azure calls | MCP/local costs, call order, output/recovery reliability; fake call time is local harness cost |
| S15 browser proof | Generated Activity basic output, cold plus three warm loads against local Vite/Django | W22 visible completion and path/API correctness; dev-server timing is not a production bundle benchmark |

There is no complete live denominator, so this report does not invent live host/Azure/MCP/local percentages. Complete
percentages below belong only to the provider-free representative observation. Copilot credits are not Azure calls or tokens.

### Total cold and warm workflow time

The six-case real-stdio matrix completed **12/12** generation/render observations with exactly one mandatory final readiness
assessment inside each generation, no standalone readiness, no repairs, and no warning. Matrix median time to returned editor
link was **2,814.389 ms cold** (worst 3,041.786 ms) and **788.808 ms warm** (worst 843.881 ms). Three additional Activity
basic repetitions were 2,988.546–3,170.138 ms cold and 817.109–850.757 ms warm, confirming the same scale.

One generated Activity-basic pair was then loaded in the editor. The cold browser reached 3 visible nodes/2 edges in
**1,311 ms** (API load 320.4 ms); three warm loads were 204/139/133 ms (median **139 ms**, API 7.9/7.4/4.0 ms). There were
no console/page errors. Adding each browser observation to its exact preceding backend observation gives the complete
provider-free representative critical path:

| State | Complete wall | Host fixture | Azure | MCP/runtime | Local backend + browser | Residual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Cold | **4,099.017 ms** | 1.739 ms / 0.04% | 0 / 0% | 1,575.552 ms / 38.44% | 2,518.891 ms / 61.45% | 2.835 ms / 0.07% |
| Warm | **896.462 ms** | 0.200 ms / 0.02% | 0 / 0% | 15.402 ms / 1.72% | 879.318 ms / 98.09% | 1.542 ms / 0.17% |

The host component is explicitly a fixture setup, not Copilot performance. In live S13/S14 work, the measured 77.9–462.2
seconds of Azure readiness already exceeds the complete provider-free path by roughly two to three orders of magnitude.

### W01–W22 critical path

Times are six-case provider-free medians to editor-link return; W22 is the generated Activity-basic browser proof. W07 owns
the orchestration envelope and therefore contains nested W08–W19 work; nested rows must not be summed again.

| Boundary | Cold / warm | Attribution and result |
| --- | ---: | --- |
| W01 host routing | 0.111 / 0.113 ms | simulated host choice; real host elapsed unavailable |
| W02 source discovery | 0.613 / 0 ms | simulated one-read fixture; S13 real search/read counts unavailable |
| W03 JSON 1 authoring | 0.972 / 0 ms | simulated construction; S13 real host cost is 129.6K tokens/374 credits |
| W04 JSON 1 validate/digest/persist | 63.827 / 56.595 ms | local production persistence through MCP; current reuse still fingerprints source |
| W05 JSON 2 frame/validate/persist | 90.154 / 129.038 ms | local; warm exact no-op retains validation/finalization/concurrency checks |
| W06 MCP startup/transport | 1,534.430 / 7.215 ms | real stdio; cold is dominated by process/initialize startup |
| W07 `generate_context` envelope | 1,089.510 / 702.283 ms | local service construction + production context generation |
| W08 final readiness | 6.809 / 6.640 ms fake-local | one assessment each; live Azure is 77,941.939 ms medium or 462,166.341 ms high-with-repair |
| W09 readiness response repair | not reached | live high repair is 349,535.310 ms; medium avoided it |
| W10 examples + packet | 524.732 / 166.026 ms | local immutable asset loading/validation; both fixed examples retained |
| W11 strict generation | 1.837 / 2.004 ms fake-local | no post-readiness live evidence yet |
| W12 deterministic validation/repair | 1.860 / 1.896 ms | validation passed; generation repair not reached |
| W13 semantic review | 22.632 / 21.738 ms fake-local | clean result in all 12; no live timing |
| W14 review-response repair | not reached | offline fault tests cover behavior; live rate/time unknown |
| W15 candidate repair/final re-review | not reached | offline fault tests cover behavior; live rate/time unknown |
| W16 PyGraphviz | 0 ms rounded (≤1 ms observed) | local, successful in 12/12 |
| W17 assembly/provenance/stability | 82.076 / 83.490 ms | local, passed in 12/12 |
| W18 atomic persistence | 3.536 / 3.685 ms | local, passed in 12/12 |
| W19 SVG rendering | 2.463 / 2.443 ms | local, passed in 12/12 |
| W20 result serialization/link return | 10.717 / 7.326 ms | derived same-call MCP residual; link present on 12/12 |
| W21 timeout recovery | 128.018 / n/a ms | six cold finalized no-ops; **zero** additional fake/provider calls, link returned 6/6 |
| W22 visible editor completion | 1,311 / 139 ms | local dev browser; 3 nodes/2 edges, no errors |

### Duplication, repair, cache, timeout, and quality

- S13 already removed the normal standalone-readiness duplicate: delayed-fake calls fell 4 → 3 and wall 1,750.583 →
  1,514.648 ms. S15 confirms every normal context attempt still performs exactly one final assessment inside generation.
- The material remaining duplicate is W09: high repair resent almost the complete 15K-token readiness input and consumed
  349.5 seconds. Rejected raw content remains intentionally unpersisted; only safe code/path diagnostics are available now.
- Process/OS caches reduce provider-free cold-to-warm link-return median 2,814.389 → 788.808 ms (72.0%). W10 falls 524.732
  → 166.026 ms, but the per-workspace generation service remains newly constructed exactly as in production; the harness does
  not cache that service or change runtime behavior.
- Provider caching is not demonstrated: S14 medium reported `cachedInputTokens: 0`. Local schema/rubric/example cache hits are
  not exposed as individual counters; their aggregate effect is bounded by the cold/warm spans.
- W05 warm no-op is slower than cold create in the median (129.038 vs 90.154 ms) because it deliberately revalidates identity,
  manifest binding, finalization, and digest concurrency. That is not proven avoidable work.
- W21 recovery is reliable rather than faster provider execution: all six lost-response simulations recovered finalized JSON
  and an editor link without another fake call. Async jobs would not reduce Azure wait.
- Provider-free quality passed 12/12 (all three diagram types, basic/complex, cold/warm), with canonical JSON, provenance,
  SVG, and semantic review clean. This proves plumbing only; visible fake oracles are not live generation quality evidence.
- Live quality evidence remains the one blocked BDD case: both efforts preserved the two decisive blockers; medium added three
  conservative blockers and shifted score 81 → 61. No live ready generation/review cell exists yet.

### H/M controlled subsection

| Metric | High | Medium | Direction |
| --- | ---: | ---: | --- |
| Calls | 2 | 1 | -50% |
| Provider duration | 462,166.341 ms | 77,941.939 ms | -83.1% / 384,224.402 ms |
| Input tokens | 30,244 | 15,130 | -50.0% |
| Completion tokens | 22,803 | 6,698 | -70.6% |
| Reasoning / cached | unavailable | 4,608 / 0 | no high comparison; no cache hit |
| Outcome | `needs_context`, 81 | `needs_context`, 61 | same boundary, non-parity in blocker detail/score |

This subsection supports comparison design, not a setting change. Stage B was `stopped` before one evaluable pair: the
Activity-ready high cell completed readiness then failed its repair call; the medium cell completed both calls but produced no
final assessment. The immutable checkpoints therefore prove **4 Azure calls** (2 readiness + 2 response repair), but the old
runner exited before persisting durations/tokens/provider identities or safe validation diagnostics. No value is synthesized.
Stage C is `not_run` and ineligible.

### Stage B live outcome and deviation

The user explicitly authorized the printed 30-cell schedule and 144-call ceiling. `prepare` froze commit `606d2fc`, case-set
digest `sha256:075cb34f7d83b24ff43f2a55f90b654a90cd563067f52dc667111f5c28edf571`, and manifest digest
`sha256:3d3605def7366759b67bdb35ee50a8630529e3c591cc6bebdcf4d6be1734a574` with zero calls. Stage B then stopped at
**4/144** calls:

| Identity | Call 1 | Call 2 | Final assessment / artifact |
| --- | --- | --- | --- |
| Activity ready · H | readiness completed | readiness repair failed | none; terminal `interrupted_provider_work` |
| Activity ready · M | readiness completed | readiness repair completed | none; terminal `readiness_assessment_failed` |

No generation/review call, canonical diagram, SVG, or editor link was created. The old runner's assumption that every
readiness attempt returns a result caused it to exit before writing either observation; this also discarded in-memory
provider duration/token/identity and safe validation-event detail. Checkpoints retain exact role/state counts only. The first
resume terminalized/skipped H without rerunning it; M then exposed the same bug. The run was conservatively sealed with
`run-stop.json` at M, and no further resume or replacement call occurred.

This is an implementation deviation, not a favorable rerun or quality result. The offline fix now converts missing readiness
results—including completed-invalid repair and provider-failure paths—into immutable error observations, deduplicates safe
validation diagnostics, counts every reached call, generates a bounded stopped report, and stops immediately. Three dedicated
regressions (completed-invalid repair, provider failure, and checkpoint terminal skip) plus the complete S15 suite pass. The
frozen live manifest remains historical and is not migrated or resumed; any
replacement screening requires a revised audited manifest and new explicit authorization.

### Ranked solutions

#### 1. W09 readiness response validity/repair

1. **Evidence:** high repair cost 349,535.310 ms, 15,114 input, and 11,171 completion tokens after a 112,631.031 ms first call.
2. **Contribution:** 75.6% of the measured 462,166.341 ms high readiness provider subpath; complete-live percentage unavailable.
3. **Domain:** Azure wait.
4. **Owner:** best-supported `readiness_prompt` / strict response-contract validation; exact defect owner awaits repeated safe diagnostics.
5. **Smallest safe fix:** the runner now persists failed assessments and safe `{code,path}` diagnostics; a new authorized proof must identify the dominant prompt/schema/validator mismatch before any prompt fix.
6. **Strongest alternative:** deterministic canonicalization only for a proven mechanical, semantics-preserving defect.
7. **Trade-off:** targeted repair adds contract complexity; broad canonicalization could hide semantic invalidity.
8. **Expected benefit:** up to one call, 349.5 seconds, 15,114 input, and 11,171 completion tokens per avoided repeat of this defect.
9. **Smallest offline proof:** replay each repeated diagnostic through validator/repair fixtures and prove identical accepted meaning.
10. **Required live proof:** affected frozen cells plus the complete applicable matrix under a new exact budget.
11. **Disposition:** **plan a revised proof separately; stopped Stage B supplied no defect-level attribution, so do not change prompts now.**

#### 2. W08 reasoning effort

1. **Evidence:** medium reduced the same blocked readiness subpath by 384,224.402 ms but changed score and added blockers.
2. **Contribution:** 83.1% relative reduction in the measured provider subpath; complete-live percentage unavailable.
3. **Domain:** Azure wait.
4. **Owner:** `reasoning_effort` interacting with response validity and readiness semantics.
5. **Smallest safe fix:** no effort change; any replacement H/M screening needs a revised audited manifest, exact new budget, and hard cell-level quality gates.
6. **Strongest alternative:** retain shared high and fix response validity without changing effort.
7. **Trade-off:** medium may save minutes/tokens but a false ready or missed blocker is unacceptable.
8. **Expected benefit:** directional ceiling of 384.2 seconds, one call, and 16,105 completion tokens in the observed case.
9. **Smallest offline proof:** completed—immutable cases/schedule/fake paths/call ceilings/report gates.
10. **Required live proof:** a newly authorized replacement screening; only its surviving cells could later enter a separate Stage C gate.
11. **Disposition:** **defer promotion; the stopped run makes no H/M decision.**

#### 3. W01–W03 host discovery and JSON 1 authoring

1. **Evidence:** real cold host reached about 129.6K context tokens and 374 credits; exact elapsed/search/read counts are absent.
2. **Contribution:** absolute token/credit cost known; time and complete-wall percentage unavailable.
3. **Domain:** host/Copilot.
4. **Owner:** broad source discovery and complete JSON 1 authoring in host context.
5. **Smallest safe fix:** separately design bounded claim-index/query/detail MCP tools while preserving complete backend authority.
6. **Strongest alternative:** retain targeted-read workflow guidance; S13 already applied it but it cannot make cold authoring deterministic.
7. **Trade-off:** new public tools add contracts and retrieval failure modes; truncating evidence is forbidden.
8. **Expected benefit:** fewer host reads/context tokens/credits; magnitude requires a controlled host replay.
9. **Smallest offline proof:** fixed repository/request replay comparing read count/bytes and byte-identical valid JSON 1/2.
10. **Required live proof:** one cold host A/B with elapsed, reads, tokens, credits, and readiness outcome.
11. **Disposition:** **plan separately; strongest alternative if provider repair is not repeated.**

#### 4. W06/W07/W10 cold startup and immutable asset loading

1. **Evidence:** provider-free cold medians are W06 1,534.430 ms, W07 1,089.510 ms (nested), W10 524.732 ms; warm W10 is 166.026 ms.
2. **Contribution:** in the complete cold representative, MCP is 1,575.552 ms/38.44%; live high readiness makes the same 1.6 s <0.4% of its provider subpath.
3. **Domain:** MCP startup plus local construction/loading.
4. **Owner:** Python/MCP process start and repeated validation/loading of immutable schema/prompt/example assets.
5. **Smallest safe fix:** keep host MCP processes alive; profile/inject only process-shared immutable caches after live provider work is controlled.
6. **Strongest alternative:** cache whole workspace generation services.
7. **Trade-off:** whole-service caching risks stale workspace/config state and unbounded lifecycle; immutable-cache injection is narrower.
8. **Expected benefit:** at most about 1.6 s cold and a bounded fraction of ~0.5 s W10; negligible on current live path.
9. **Smallest offline proof:** same 12 cells with explicit constructor/cache counters and byte-identical JSON/SVG.
10. **Required live proof:** none until provider/host improvements make local startup material.
11. **Disposition:** **defer.**

#### 5. W05 safe request no-op/reconciliation

1. **Evidence:** 129.038 ms warm median versus 90.154 ms cold; exact representative warm no-op was 126.607 ms.
2. **Contribution:** 14.12% of the 896.462 ms complete provider-free warm representative; <0.2% of medium readiness alone.
3. **Domain:** local deterministic work.
4. **Owner:** identity/manifest/finalization/digest rechecks in request persistence.
5. **Smallest safe fix:** first add subspan counters; remove a read/validation only if concurrency equivalence is proven.
6. **Strongest alternative:** accept the bounded cost and preserve the current simple locking/recheck model.
7. **Trade-off:** shaving milliseconds can weaken stale-manifest, ownership, or timeout-finalization safety.
8. **Expected benefit:** hard ceiling around 0.13 seconds per no-op in this fixture.
9. **Smallest offline proof:** race/no-op tests showing identical conflicts/finalization with one candidate read removed.
10. **Required live proof:** none unless local work becomes material.
11. **Disposition:** **defer.**

#### 6. W22 editor visible completion

1. **Evidence:** generated output loaded cold in 1,311 ms and warm median 139 ms; API was 320.4 ms cold and 7.4 ms warm median, no errors.
2. **Contribution:** 31.98% cold and 15.51% warm of the complete provider-free representative; <2% of medium readiness.
3. **Domain:** local browser/frontend/API.
4. **Owner:** cold Vite/browser module startup and first API load; production-bundle owner is unproven.
5. **Smallest safe fix:** no code change; measure a built frontend before attributing dev-server cold cost.
6. **Strongest alternative:** frontend bundle/chunk optimization after a production trace.
7. **Trade-off:** optimizing dev cold load can add complexity without improving shipped behavior.
8. **Expected benefit:** bounded by 1.3 seconds cold/0.14 seconds warm in this environment.
9. **Smallest offline proof:** existing Playwright built-preview load with node/edge identity and console/network assertions.
10. **Required live proof:** none while provider/host dominate.
11. **Disposition:** **defer.**

#### 7. W16/W18/W19 layout, persistence, and rendering

1. **Evidence:** matrix medians: layout ≤1 ms, persistence 3.536/3.685 ms, render 2.463/2.443 ms cold/warm; all 12 passed.
2. **Contribution:** well below 1% of the provider-free complete path and negligible against live provider time.
3. **Domain:** local deterministic work.
4. **Owner:** PyGraphviz, atomic storage, and SVG renderer; no failure cluster exists.
5. **Smallest safe fix:** none.
6. **Strongest alternative:** profile only if future diagrams or provider improvements move these stages onto the critical path.
7. **Trade-off:** optimization risks layout/render parity and persistence safety for no current user-visible gain.
8. **Expected benefit:** only single-digit milliseconds in current fixtures.
9. **Smallest offline proof:** existing type-spanning layout/render/persistence suites.
10. **Required live proof:** none.
11. **Disposition:** **defer.**

### Recommendation and next proof

**Recommended next slice:** first audit a revised, bounded **Readiness Response Validity Proof** that preserves failed
observations and identifies the exact repeated `{code,path}` owner. Only then implement one prompt/schema/validator fix. The
runner terminal-accounting prerequisite is already fixed offline; no prompt or effort setting changes from the stopped run.

**Strongest alternative:** plan claim-query/detail MCP tools to reduce cold host work. **Decisive trade-off:** readiness repair
has a hard measured 349.5-second cost, while host tokens/credits are high but host elapsed is missing; fix the measured
provider defect first; the stopped Stage B confirms repeated repair entry but lost defect detail. **Unresolved risks:** no
complete live wall clock, no live ready post-readiness generation/review timings, no persisted Stage B duration/token/
diagnostic detail, no high reasoning-token/cache comparison, medium semantic drift, optional repair stages not reached in the
clean fake matrix, and browser evidence is local dev-mode only.

**Smallest next proof:** an offline failed-assessment fixture now passes. Any live replacement should begin with only the
smallest audited readiness pair needed to prove safe diagnostic persistence and response validity; it requires a new exact
budget/authorization and cannot reuse or rerun the stopped manifest. Stage C remains blocked.

### Implementation and verification

S15 reused the pre-clarification H/M case/manifest/runner/report work, then added additive local stage durations and an
evaluation-only real-stdio audit server. Its historical `audit_offline` compatibility entry ran the original 12 provider-free
cells; Block 1 replaced that entry with the independent `run_workflow_audit` command and new identities without migrating or
rerunning S15 evidence. `offline` retains the H/M production-path proof; `prepare`/`stage_b`/`stage_c` remain separately gated.
Instrumentation does not change public MCP arguments/results or production generation acceptance. The documentation-only plan
checkpoint is `ee9d7d3`.

Independent implementation audit passed with no critical/high finding; its accounting-clarity finding was fixed. The first
full backend gate exposed missing examples on four new schemas plus diagnostics-stage mapping gaps; both root causes were
fixed before rerun. Exact final checks:

- `cd backend; uv run python manage.py test` — **913 passed, 5 skipped** after the live-failure recovery fix;
- focused failed-assessment/checkpoint recovery regressions — **3 passed**; the preceding complete S15 package gate passed **25** before the checkpoint regression was added;
- `cd backend; uv run python manage.py check` — no issues;
- `cd backend; uv run python mcp_server/smoke_test.py` — all real-stdio checks passed;
- `cd backend; uv run python -m compileall -q api mcp_server services` — passed;
- `cd frontend; npm run verify` — lint/build passed, **419 unit/component + 43 Chromium E2E**;
- generated-output Playwright proof — 3 nodes/2 edges, no console/page error, cold 1,311 ms and warm median 139 ms;
- `git diff --check` — passed.

The only live gate was the explicitly authorized, terminal Stage B attempt described above: 4/144 calls, no completed
observation pair, no generation artifact, no rerun, and no Stage C/certification. The pre-clarification implementation
deviation is preserved in this history; the completed implementation reuses rather than discards that work.
