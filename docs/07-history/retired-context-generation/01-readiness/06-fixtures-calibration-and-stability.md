# Readiness Fixtures, Calibration, and Stability

> **Scope of this doc.** This file is the single owner of deterministic calculation fixtures, semantic
> fixture coverage, human labels, calibration/release targets, and unchanged-input repeated-run stability for
> the exact readiness policy. The on-disk fixture-bundle schema is an implementation-owned detail governed by
> the semantic obligations below.

## Purpose

Make readiness policy and LLM semantic judgments testable. Fixtures prove deterministic calculations and
cross-field validation; calibrated semantic cases detect false-ready, false-blocking, omission, assumption,
and repeated-run instability before release.

## 1. Fixture layers

| Layer | Purpose | LLM required? |
| --- | --- | --- |
| Deterministic policy fixtures | Prove caps, N/A/uncertain treatment, score/rounding, finding injection, and status. | No |
| Structured-output fixtures | Prove valid/invalid raw JSON combinations, allowlists, and repair exhaustion. | No |
| Semantic rubric fixtures | Label expected applicability, rating bands, findings, and recommendations for representative context. | Yes for live calibration; deterministic expected outputs remain reviewable offline. |
| End-to-end grounded fixtures | Exercise source → JSON 1 → JSON 2 → readiness → resolved context → diagram. | Mixed; the implementation-owned bundle contract is separate. |

All fixtures identify exact rubric, raw-output, prompt, and model/deployment versions relevant to their
expected result. Training examples and held-out calibration fixtures remain disjoint.

## 2. Deterministic calculation fixtures

The test suite includes at least:

| Fixture | Expected assertion |
| --- | --- |
| `all-required-strong` | All required facets `4`, conditionals N/A -> score `100`, no coverage blockers. |
| `high-average-required-partial` | High score with one required rating `2` -> `needs_context`. |
| `conditional-not-applicable` | N/A facet contributes neither rating nor weight. |
| `conditional-uncertain` | Uncertain contributes zero with its weight retained and blocks. |
| `conditional-partial-overrideable` | Rating `2` creates overrideable blocker; holistic goal blocker can still prevent override. |
| `assumption-cap` | Assumption-backed coverage cannot exceed `3` and always emits `assumption_backed_coverage`. |
| `assumption-now-supported` | An active/current equivalent claim emits `assumption_supported_by_claim` with exact `replace_assumption_with_claim` payload. |
| `decision-asserts-fact` | A decision attempting unsupported factual meaning emits `decision_asserts_unsupported_fact`. |
| `round-half-up` | Exact half cases round upward identically across runtimes. |
| `bdd-single-definition-aligned` | One supported definition may be ready when it satisfies the confirmed request. |
| `bdd-single-definition-insufficient` | A broader structural request with only one bare definition receives the appropriate general alignment/detail/modelability finding. |
| `typed-action-valid` | Every action kind accepts its exact required payload and no extra fields. |
| `typed-action-invalid` | Missing, cross-kind, unknown, or non-allowlisted action payload fields are rejected. |
| `finding-policy-injection` | Raw code receives exact registered category/severity/overrideability. |
| `invalid-policy-field` | Raw LLM-supplied status/weight/severity is rejected. |
| `invalid-ref` | Invented/non-allowlisted claim, uncertainty, or assumption ref is rejected. |
| `invalid-assumption-strong` | Rating `4` with assumption ref is rejected and defensively capped. |
| `invalid-output-exhaustion` | Two invalid structured responses return operation error, never readiness. |
| `invalid-preflight-no-score` | Layer 1 invalidity returns sorted nonempty `invalidIssues`, null score, and empty coverage without an LLM call. |

## 3. Semantic fixture contract

Each semantic fixture contains or deterministically references:

- bounded JSON 1;
- JSON 2;
- canonical reviewer projection;
- exact rubric version;
- complete human-labeled facet applicability;
- one acceptable rating band per facet (`0..4` ordered integer bounds when applicable; null bounds when N/A or uncertain);
- required-facet pass/fail;
- exact mandatory finding signatures (code plus related claim, uncertainty, and assumption refs) and forbidden finding codes;
- mandatory emitted finding-action kinds;
- expected final status and overrideability plus the exact mandatory non-overrideable blocker subset;
- top-level mandatory and forbidden selection/removal recommendations; and
- complete allowed claim, uncertainty, and assumption ref sets.

The implementation-owned fixture-bundle contract defines exact paths, file names, schema version,
training/held-out split metadata, and source-repository bundle shape while preserving these semantic obligations.

## 4. Activity fixture matrix

At minimum:

- straight-line flow with all conditional facets N/A -> `ready`;
- branch present but guard absent -> `needs_context`;
- complete branch/guards -> pass `controlConditions`;
- concurrency indicated but synchronization unknown -> overrideable gap;
- in-scope failure cause known but handling unknown -> exception gap;
- accepted narrow exception assumption -> `ready_with_warnings` at most;
- disconnected action facts -> `selection_not_modelable`.

Every activity facet has boundary fixtures at ratings `0`, `1`, `2`, `3`, and `4`; every conditional facet
also has `not_applicable` and `uncertain` cases that exercise its exact applicability arrays.

## 5. Use-case fixture matrix

At minimum:

- simple subject/actors/goals/associations with no special relationships -> `ready`;
- actors and goals present but association absent -> required coverage blocker;
- internal component misclassified as actor -> scope/abstraction finding;
- extend relationship missing condition or extension location -> conditional gap;
- active in-scope goal omitted -> exact selection recommendation;
- actor/goal abstraction mixed with private operations -> abstraction warning.

Every use-case facet has fixtures at ratings `0`, `1`, `2`, `3`, and `4`; `useCaseRelationships` also has
N/A and uncertain cases that exercise its exact applicability arrays.

## 6. BDD fixture matrix

At minimum:

- one supported definition satisfying an explicit single-definition request -> potentially `ready`;
- one bare definition against a broader structural request -> general alignment/detail/modelability blocker;
- one block with supported typed features -> `ready`;
- multiple definitions with ambiguous relationship meaning -> ambiguity blocker;
- composition requested but ownership unknown -> conditional ownership gap;
- material cardinality unknown -> conditional multiplicity gap;
- ports/interfaces absent and not requested -> N/A;
- internal connector network requested as BDD -> scope/type finding rather than invented BDD edges.

Every BDD facet has fixtures at ratings `0`, `1`, `2`, `3`, and `4`; every conditional facet has N/A and
uncertain cases that exercise its exact applicability arrays. Request-alignment fixtures distinguish an
intentional single-definition diagram from insufficient context for a broader structural goal.

## 7. Cross-cutting Layer 3 fixtures

At minimum:

- relevant existing claim omitted versus genuinely absent fact;
- same-viewpoint contradiction;
- coherent exclusion versus goal-conflicting exclusion;
- accepted assumption that is narrow versus one that conflicts with context or substitutes too broadly;
- assumption already supported by active/current claim;
- decision remaining non-factual versus one asserting unsupported fact;
- redundant/out-of-scope selections;
- detail below request but truthful smaller result available;
- relevant uncertainty with each `block|exclude|assume|defer` disposition.

Each registered finding code requires at least one positive fixture. Each blocking code also requires a nearby
negative fixture that must not emit it.

## 8. Human labeling

At least two reviewers independently label each calibration fixture for:

- applicability;
- acceptable rating range;
- required-facet pass/fail;
- mandatory and forbidden finding codes/refs;
- expected recommendations/actions;
- final status and overrideability.

Disagreements are adjudicated into one fixture answer key before prompt/rubric tuning. Keep a holdout set out
of prompt and example authoring.

## 9. Calibration and release targets

A rubric/model/prompt combination is releasable only when the holdout set has:

- zero false-ready results on fixtures labeled `invalid` or non-overrideable `needs_context`;
- zero missing mandatory non-overrideable blocker codes;
- zero invented or non-allowlisted references;
- at least 90% exact final-status agreement overall;
- at least 95% required-facet pass/fail agreement;
- exact facet-applicability agreement and ratings within every adjudicated acceptable band;
- exact mandatory finding-signature recall, forbidden-finding absence, and mandatory emitted action-kind recall;
- at least 90% exact mandatory selection/removal recommendation recall;
- no required release metric with a zero denominator: an unmeasured rate is `0.0` and never passes; a metric may be
  inapplicable to one case only when the complete holdout matrix measures it in other cases;
- no systematic diagram-type or detail-level false-blocking pattern; the v1 command conservatively fails on any
  false-blocked case adjudicated as `ready` or `ready_with_warnings` and reports every affected group.

Score error is diagnostic rather than a release gate when status/facet boundaries agree. Calibration tunes
facet instructions, examples, and model configuration; it does not add an unversioned score threshold.

## 10. Repeated-run stability

For every unchanged semantic fixture, run ten independent reviews with:

- canonical input ordering;
- fixed rubric, structured-output, and reviewer-prompt versions;
- fixed model/deployment and every deterministic control the deployment accepts: request `temperature: 0` and a
  fixed seed, fall back only when the provider explicitly rejects that control, and record the exact effective
  controls in the report;
- no semantic retry or majority vote;
- invalid-output repair measured separately.

Acceptance requires:

1. exact final status and overrideability in `10/10` runs;
2. exact facet applicability, ratings inside the adjudicated band, and required-facet pass/fail in `10/10` runs;
3. every exact mandatory finding signature present, every forbidden finding code absent, and every mandatory emitted
   finding-action kind present in `10/10` runs;
4. identical non-overrideable blocker codes and related refs in `10/10` runs;
5. no ready/blocked boundary flip for any facet;
6. readiness-score spread no greater than five points;
7. every mandatory recommendation present and no forbidden recommendation in `10/10` runs;
8. no invented refs or invalid policy combinations; and
9. first-response schema validity recorded separately rather than hidden by repair.

A stability failure changes rubric/prompt/examples/model configuration and restarts the full calibration set.
Runtime never chooses the most favorable result, averages multiple LLM reviews, or repeatedly calls the
reviewer with unchanged input. A model/deployment upgrade requires recertification even when rubric and
prompt versions do not change.

## 11. Validation invariants

- Deterministic fixture expected values are calculated independently from implementation under test.
- Semantic fixtures identify exact immutable claim/assumption/uncertainty refs.
- Training and held-out fixture pools do not overlap.
- Every facet has explicit `0..4` boundary coverage; every conditional facet also covers applicable, N/A, and uncertain branches.
- Every registered finding code and every typed action kind has positive and nearby negative/invalid coverage.
- Human labels are adjudicated before tuning.
- Invalid-output repair statistics remain separate from semantic stability.
- No runtime majority vote hides unchanged-input variance.

## Implementation-owned delivery contract

The registered bundle schema is `graphpilot.context.readiness-calibration-bundle.v1`. The default bundle root is
`backend/assets/readiness/calibration/`; each unique training or holdout case contains exact bounded JSON 1,
JSON 2, rubric/reviewer versions, `labelStatus: draft|adjudicated`, independent reviewer labels, and an adjudicated
answer key when status is `adjudicated`. Each reviewer label carries a distinct pseudonymous reviewer ID, labeling
timestamp, and explicit human attestation; the operator remains responsible for the truth of that attestation. A
holdout answer key records complete applicability and acceptable rating bands, required-facet pass/fail, exact
mandatory finding signatures and forbidden codes, mandatory finding-action kinds, final status/overrideability,
mandatory non-overrideable blockers, mandatory/forbidden selection/removal recommendations, and the complete
allowed ref sets. Training and holdout IDs are disjoint and
holdout content is never used in prompt/example authoring. A bundle is at most 64 MiB and contains at most 256
total cases; embedded JSON 1/JSON 2 must pass their canonical schemas and exact manifest ID/path/digest binding,
and report failures are
bounded to 255 entries plus one omitted-count
record so JSON output remains below 2 MiB. Synthetic test bundles prove the machinery but never count as human
calibration evidence.

The operator entry point is:

```powershell
uv run python manage.py calibrate_readiness [--fixture-root <path>] [--live] [--json]
```

Default check-only mode validates bundle structure, versions, split separation, every supplied label, and report
plumbing without calling Azure; it reports label completeness and uses `releaseStatus: "not_run"`. A structurally
valid draft bundle may therefore pass check-only validation while remaining uncertified. Explicit `--live` requires
configured Azure, two distinct human labels plus adjudication for every holdout case, a nonempty complete holdout
whose matrix tags prove every required per-type/Layer 3 case, facet `0..4` boundary, conditional N/A/uncertain
branch, finding positive/near-negative pair, and action kind. Facet, finding, and action tags count only when the
adjudicated answer key substantiates them; scenario and Layer 3 tags remain human-attested. Live evaluation requires
nonzero mandatory/forbidden finding, action, blocker, and recommendation measurements across the complete matrix
and exactly ten unchanged-input runs per case. Live calibration requests temperature zero and a fixed seed, falls
back only when the deployment explicitly rejects one of those controls, and records the exact effective controls
alongside the fixed deployment/reasoning setting. The bounded report uses exact `pass|fail|not_run`; failed targets
or an incomplete/invalid live gate exit nonzero. Reports may be redirected by the operator but are diagnostics only
and are never runtime input.

A separate operator benchmark may compare one explicit reasoning effort without changing runtime configuration:

```powershell
uv run python manage.py benchmark_readiness_effort --workspace <workspace> --request-path <request> --reasoning-effort <low|medium|high|xhigh> --live --json
```

It requires current canonical context, stages exact JSON 1/JSON 2 temporarily, invokes the production generation-path final
gate, delegates at most two readiness-schema calls, blocks generation locally, and reports bounded duration, total/reasoning/
cached tokens, first-response validity, and code/path validation diagnostics. Its exact identity is
`graphpilot.readiness-effort-benchmark.v1` / `readinessEffortBenchmark`; `benchmarkOnly: true` and
`releaseStatus: not_run` prevent benchmark evidence from becoming calibration or promotion.

The following remain deferred:

- runtime few-shot selection;
- broad generation-evaluation/DOE rebuild; and
- claiming semantic release certification until real human labels and authorized live runs meet every target.

The fixture delivery sequence begins with one source-to-artifact bundle and proves it with one vertical scenario
before parallel per-type fixture authoring. Repository-owned unlabeled/draft cases may exercise offline behavior,
but only adjudicated holdout cases participate in a live `pass` result.

### Final definition

> Readiness fixtures are independently reviewed deterministic and semantic cases that prove exact policy,
> catch false-ready/false-blocking behavior, and require stable unchanged-input decisions before one
> rubric/model/prompt combination may be released.
