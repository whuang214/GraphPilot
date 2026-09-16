# Shared Workflow Success Contract

## Purpose

Give every roadmap block, implementation slice, audit, optimization, and promotion decision one stable definition of user
success. Block agents may add narrower acceptance criteria but may not weaken or silently reinterpret this contract.

## User-Visible Boundary

The complete workflow clock begins when the host receives the user's diagram request. It ends when one of these outcomes is
visible to the user:

1. a generated diagram is loaded visibly in the editor;
2. an actionable blocked result explains why generation is unsafe and what can resolve it;
3. a typed failure or interrupted result states what is known, what remains uncertain, and whether any retry is permitted.

A backend file write or returned path alone is not complete user-visible success.

## Generated Success

A generated outcome succeeds only when:

- the host selected the correct direct or context authority branch;
- JSON 1/JSON 2 and all relevant request/context digests are current and valid;
- context generation performed exactly one mandatory final-readiness assessment and satisfied its explicit policy;
- strict generation, deterministic validation/repair, reviewed semantic quality, and mandatory final review completed;
- required meaning is present and material unsupported meaning is absent;
- every context-generated element has valid smallest-sufficient provenance;
- the canonical diagram passed validation and context-stability checks;
- canonical JSON was atomically persisted and its identity remains owned by the exact request;
- SVG rendering succeeded or a typed non-fatal render warning identifies provider-free recovery;
- MCP returned the backend-built editor link without an unchanged retry;
- the editor loaded the exact persisted diagram visibly without a material console/network failure.

## Blocked Success

A blocked outcome is a valid workflow result when:

- the status and blocker boundary match the complete authority and deterministic policy;
- every mandatory non-overrideable blocker is present;
- no false `ready` or direct-generation fallback occurs;
- findings, references, and actions are valid and allowlisted;
- the result gives the host/user a specific next action when one is available;
- no generation/review provider call, canonical diagram, SVG, or editor link is fabricated;
- the complete safe result is returned or durably recorded without rerunning the attempt.

A blocked result may complete an individual attempt while the broader user journey remains unresolved until context is
improved or the user accepts an allowed boundary.

## Failed and Interrupted Outcomes

A failure or interruption is handled correctly only when:

- every definitely started provider call counts against the exact authorized budget;
- completed/failed safe call metrics and validation events are retained when available;
- uncertain call state remains explicitly uncertain and is never reconstructed as success/failure;
- no raw response, prompt, reasoning, source authority, secret, or hidden gold is persisted;
- the exact request/case/observation identity becomes immutable terminal state before resume can skip it;
- resume never reissues that identity's provider call;
- the result names the responsible known stage and safe error code without guessing root cause;
- another live attempt requires the policy declared by its audited package and a new authorization when applicable.

## Performance Evidence

Every complete audit or optimization comparison keeps these domains separate:

- **Host:** elapsed time, routing, searches, reads, bytes, authoring/reconciliation effort, and host tokens/credits
  when available. A host that is also the agent performing the work cannot supply comparable timing; such observations
  record contract properties only and are labeled reference-host characterization.
- **Azure provider:** exact roles, states, duration, request/response bytes, prompt/completion/reasoning/cached tokens,
  requested/effective controls, provider request ID, service tier, validity, and repairs.
- **MCP/runtime:** process startup, initialization/discovery, transport, dispatch, serialization, response bytes, timeout,
  and recovery behavior.
- **Local deterministic:** validation, digests, persistence, packet/example/rubric loading, layout, canonical assembly,
  provenance/context stability, rendering, and browser/API completion.

Complete-wall percentages require one complete non-overlapping denominator. Nested stages remain diagnostic detail and are
not summed twice. Missing evidence is `not_measured` with a reason; it is never estimated silently. Fake-provider time is
local harness cost, not Azure evidence. Copilot credits are never converted into Azure usage.

## Quality Invariants

No performance, refactor, architecture, or promotion block may weaken:

- authority completeness;
- readiness status and non-overrideable blocker correctness;
- strict output and no-fallback behavior;
- deterministic and semantic validation;
- reviewed quality and mandatory final review;
- required examples and rubrics;
- provenance and digest binding;
- request ownership and atomic persistence;
- canvas/SVG parity;
- path, secret, raw-response, hidden-reasoning, and hidden-gold protections.

## Change Evidence

Every retained behavioral or performance change records:

- baseline and candidate identities;
- measured absolute and percentage effect on complete user-visible wall time;
- call, token, credit, repair, and reliability effect where applicable;
- quality/security/compatibility trade-off;
- smallest offline proof and required live proof;
- anchor/representative results;
- rollback path;
- proposal, implementation, verification, promotion, and certification state.

Several related changes may share one wave only when they own one coherent cause and can be evaluated together without
losing attribution. Otherwise, measure them sequentially and maintain a cumulative ledger.

## Program Completion

The roadmap succeeds when GraphPilot has:

- trustworthy ready, blocked, failed, and interrupted outcomes;
- at least one complete provider-backed request-to-visible-editor proof;
- a reusable current workflow audit and versioned optimization baseline;
- an optimized candidate with material cumulative user-visible benefit;
- representative quality and stability evidence;
- explicit promotion, rollback, and truthful certification state.

## Authority

Final intended behavior remains owned by active product, architecture, MCP, and feature design documents. This contract owns
only the cross-block definition of workflow success and evidence. Live completion/progress belongs exclusively to the
current-state board, and block/slice outcomes retain historical evidence.
