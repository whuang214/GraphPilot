# Readiness Fixtures, Calibration, and Stability

> **Status:** Historical fixture/calibration snapshot. Current intended behavior is owned by
> [`05-fixtures-calibration-and-stability.md`](../../../03-design/01-context-generation/01-readiness/06-fixtures-calibration-and-stability.md);
> runtime fixtures/calibration are not implemented.
>
> **Scope of this doc.** This file is the single owner of deterministic calculation fixtures, semantic
> fixture coverage, human labels, calibration/release targets, and unchanged-input repeated-run stability for
> the exact readiness policy. It does not define the future on-disk fixture-bundle schema; that contract is
> the next design step after this package split is reviewed.

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
| End-to-end grounded fixtures | Exercise source → JSON 1 → JSON 2 → readiness → resolved context → diagram. | Mixed; exact future bundle contract is designed separately. |

All fixtures identify exact rubric, raw-output, prompt, and model/deployment versions relevant to their
expected result. Training examples and held-out calibration fixtures remain disjoint.

## 2. Deterministic calculation fixtures

The implementation test set must include at least:

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
| `invalid-preflight-no-score` | Layer 1 invalidity returns null score and empty coverage without LLM call. |

## 3. Semantic fixture contract

Each semantic fixture contains or deterministically references:

- bounded JSON 1;
- JSON 2;
- canonical reviewer projection;
- exact rubric version;
- human-labeled expected facet applicability;
- acceptable rating band;
- mandatory and forbidden finding codes/refs;
- required recommendations/actions;
- expected final status and overrideability.

Exact future paths, file names, schema version, training/held-out split metadata, and source-repository bundle
shape remain to be designed after this document split; they must preserve these semantic obligations.

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
- at least 90% exact mandatory selection/removal recommendation recall;
- no systematic diagram-type or detail-level false-blocking pattern.

Score error is diagnostic rather than a release gate when status/facet boundaries agree. Calibration tunes
facet instructions, examples, and model configuration; it does not add an unversioned score threshold.

## 10. Repeated-run stability

For every unchanged semantic fixture, run ten independent reviews with:

- canonical input ordering;
- fixed rubric, structured-output, and reviewer-prompt versions;
- fixed model/deployment and deterministic settings (`temperature: 0`, plus fixed seed when supported);
- no semantic retry or majority vote;
- invalid-output repair measured separately.

Acceptance requires:

1. identical final status in `10/10` runs;
2. identical required-facet pass/fail in `10/10` runs;
3. identical non-overrideable blocker codes and related refs in `10/10` runs;
4. no ready/blocked boundary flip for any facet;
5. readiness-score spread no greater than five points;
6. every mandatory recommendation present and no forbidden recommendation in `10/10` runs;
7. no invented refs or invalid policy combinations;
8. first-response schema validity recorded separately rather than hidden by repair.

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

## Deliberate non-goals and next dependency

This file does not yet define:

- exact fixture-bundle directory/JSON schema;
- representative repository source trees;
- runtime few-shot selection;
- operator calibration command implementation;
- broad generation-evaluation/DOE rebuild.

The next fixture-design step should define one source-to-artifact bundle and prove it with one vertical
scenario before parallel per-type fixture authoring.

### Final definition

> Readiness fixtures are independently reviewed deterministic and semantic cases that prove exact policy,
> catch false-ready/false-blocking behavior, and require stable unchanged-input decisions before one
> rubric/model/prompt combination may be released.
