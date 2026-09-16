# Slice 06: Semantic Reviewer

## Purpose

Add the injected semantic reviewer for readiness Layers 2/3 and assemble the validated final readiness result
through the deterministic policy delivered in slice `02`.

## Background

Layer 1 and the bounded reviewer projection are complete. The semantic reviewer may rate and select allowed
finding/action codes, but it cannot control severity, overrideability, scoring, status, or persistence.

## Design

This slice moves the existing `LLMClient`/`AzureLLMClient`/`FakeLLMClient` seam and `PromptService` from
`services/generation/` into neutral `services/llm/`, where both readiness and generation can depend on them
without a package cycle. `ContextReadinessService.assess(request_path)` wraps the already implemented
`prepare()` phase: identified invalid preflight returns immediately; valid preparation makes one structured
reviewer call, permits one diagnostics-only repair call for invalid structured output, validates and canonicalizes
the private review, delegates score/status to `ReadinessPolicyService`, and validates one final result. Reviewer
unavailability, refusal, provider failure, or exhausted invalid output fails safely without fallback.

## Plan Audit

- **Package cutover:** move `llm_client.py`, `prompt_service.py`, and their tests to `services/llm/` and
  `tests/llm/`; update generation, MCP, management-command, tests, and service navigation atomically with no
  compatibility modules. Generation behavior remains characterized. The shared client continues preferring strict
  Chat Completions `json_schema` and narrowly falls back to `json_object` only when the deployment explicitly
  rejects that response format; caller-side validation remains mandatory. OpenAI's current Python helper also
  exposes refusal separately, so the seam adds typed refusal detection before parsing content.
- **Schemas and bounds:** add strict Draft 2020-12 private-review and final-result schemas to `SchemaRegistry`.
  Private output uses the exact owner-defined enums/action `oneOf`s, 1 MiB decoded cap, 2,000-character semantic
  text, 512-character searches, 64-item semantic arrays, 256-item uncertainty/ref arrays, 32 searches, and exact
  question-ID grammar. The final schema includes required `invalidIssues` and enforces status/score/coverage/issues
  combinations; assembled output is capped at 2 MiB.
- **Prompt/call boundary:** add external `readiness-review.md` and `readiness-review-repair.md`. The first call's
  user content is the exact canonical Slice 05 projection. Repair receives the identical projection plus only
  sorted `{path,code,message}` diagnostics—never the rejected raw response—and uses the same strict schema/name.
  Provider/configuration failures do not consume the repair attempt; non-JSON/empty output and schema/invariant
  failures do. At most two calls occur, and a valid unfavorable review is never rerolled.
- **Private validation:** schema-validate first, then require exact rubric coverage once in rubric order; valid
  applicability/rating/support combinations; selected-only rating refs; allowlisted unique refs; active/current
  recommendation refs; selected removal refs; registered holistic code/action combinations; cross-consistent
  findings/supporting arrays; matching companions for low/uncertain facets; and no LLM-owned policy fields.
  Canonicalization sorts every model-controlled collection by the active owner rules.
- **Policy and deterministic findings:** encode exact claim refs internally as `id@version` tokens for the existing
  pure policy service and convert only at result boundaries. Add preflight `selection_closure_missing` and
  `uncertainty_disposition_blocks`, coverage/assumption findings, then validated holistic findings in policy order.
  Every final finding gets `finding-<three-digit ordinal>-<code>` after ordering; category/severity/overrideability
  come only from the immutable registry. Low/uncertain facet actions derive from a matching recommendation,
  missing-context item, relevant uncertainty, or question; missing companions invalidate reviewer output.
- **Final result:** add an immutable result DTO plus coverage/finding serialization and validate the complete result
  schema before return. Identified preflight invalidity makes zero LLM calls and returns nonempty sorted
  `invalidIssues`, null score, empty coverage/findings/recommendations, and false flags. Otherwise
  `canGenerate` is true only for `ready`; `ready_with_warnings` requires a later explicit generation policy;
  `canOverride` comes only from policy. Summary text is deterministic from status and blocker/warning counts.
- **Failures:** `ReadinessReviewerUnavailableError` covers unconfigured clients;
  `ReadinessReviewFailedError` carries stage, attempts used, bounded diagnostics, and retryability for refusal,
  provider failure, or exhausted invalid output. No deterministic-only or force-skip fallback exists, and prompts,
  raw outputs, hidden reasoning, or secrets are never persisted/logged.
- **Verification:** fixed fake responses cover all statuses, closure/block disposition synthesis, action kinds,
  assumption cap, canonical order, invalid refs/codes/policy fields, first-response repair, repair exhaustion,
  refusal/unavailable/provider errors, exact call counts, schema meta-validation, package-move characterization, and
  unchanged-input deterministic output. Live Azure review is opt-in and skipped by the default offline suite.

## Included Work

- Move `llm_client.py`, `prompt_service.py`, and their tests into `services/llm/`; update generation imports without behavior changes.
- Add readiness-review and repair prompts plus strict private-review/final-result schemas.
- Add an injected reviewer path using the existing offline fake pattern.
- Validate/canonicalize coverage, findings, evidence references, and action payloads.
- Apply assumption cap, score, finding order, status, and result serialization from slice `02`.
- Add offline end-to-end fixtures and opt-in live-provider checks.

## Not In Scope

- MCP tools, typed-action execution, host loops, or context generation.
- Persisting prompts, raw responses, or hidden reasoning.
- Fallback that bypasses semantic review.

## Target Areas

- `backend/assets/prompts/`
- `backend/services/readiness/`
- `backend/services/llm/`
- `backend/services/generation/` import consumers
- `backend/services/`
- `backend/tests/readiness/`, `backend/tests/llm/`, and affected generation tests

## Exit Criteria

- Fixed fake responses produce exact deterministic final results.
- Invalid/unavailable reviewer outcomes fail safely with typed errors.
- The model cannot invent codes or override deterministic policy.
- Offline targeted and full backend tests pass; live-provider tests remain optional.

## Previous Slice

- [`05-readiness-preflight-and-projection.md`](05-readiness-preflight-and-projection.md)

## Next Slice

- [`07-context-mcp-tools.md`](07-context-mcp-tools.md)

## Outcome

**Completed.**

- **Implementation:** moved the shared Azure/fake structured-JSON client and prompt loader into `services/llm/`
  without generation behavior changes; added refusal detection, readiness review/repair prompts, strict private/final
  schemas, immutable final-result DTOs, the finding/action policy registry, private review validation/canonicalization,
  deterministic result assembly, and `ContextReadinessService.assess()`. Identified invalid preflight returns with
  sorted `invalidIssues` and zero model calls; valid input gets one semantic call plus at most one diagnostics-only
  repair against identical projection input. All policy fields, score/status, finding IDs/order, warning/override
  flags, and final schema validation remain deterministic.
- **Verification:** 83 focused LLM/readiness/schema/contract tests and all 534 backend tests pass offline; the opt-in
  Azure reviewer check is skipped unless `GRAPHPILOT_RUN_LIVE_READINESS=1`. Coverage includes all seven action
  schemas, schema meta-validation/caching, package characterization, ready/needs-context/warnings/invalid states,
  assumption cap, overrideability, closure/block findings, holistic policy injection, canonical ordering, one repair,
  repair exhaustion, invented refs/codes, refusal, unconfigured/provider failures, and exact call counts.
- **Deviations:** live documentation confirmed the current OpenAI Python helper exposes refusals separately, so the
  shared seam now raises a typed refusal before content parsing. Final action shape is revalidated against the same
  private action schema during final-result validation rather than duplicating that large `oneOf` inside the final
  schema. No raw response, prompt, hidden reasoning, or secret is persisted or included in repair diagnostics.
- **Follow-up:** Slice 07 adapts persistence/readiness typed outcomes into the four context lifecycle/readiness MCP
  tools while keeping these services protocol-independent.
