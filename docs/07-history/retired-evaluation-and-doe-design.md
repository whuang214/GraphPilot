# Generation Evaluation and Experiment Design

## Purpose

GraphPilot certifies the frozen redesigned generator against absolute, independently authored hidden-gold gates. The framework measures whether final direct and context diagrams are delivered, semantically correct, grounded where required, useful, and consistent, while capturing provider calls, token usage, latency, repair/reviewer behavior, and the first failing stage.

This framework is offline and operator-triggered. It is not canonical diagram validation, UI save validation, context readiness, or a runtime generation stage. Runtime validation remains deterministic; runtime semantic review improves generation; the independent evaluator grades the delivered result.

## Scope and boundaries

### Built-in generator evaluation

The built-in suite evaluates the generator boundary from frozen validated authority through final delivery.

Direct:

```text
frozen graphpilot.direct.diagram-request.v1
  -> generation-input builder
  -> strict generation and deterministic repair
  -> reviewed-mode semantic review and semantic repair
  -> PyGraphviz layout, canonical persistence, and render
  -> final normalized semantic projection
```

Context:

```text
frozen graphpilot.context.evidence-manifest.v1
+ frozen graphpilot.context.diagram-request.v1
+ accepted frozen generation-policy identity
  -> deterministic resolution
  -> strict generation and deterministic/provenance repair
  -> reviewed-mode semantic review and semantic repair
  -> PyGraphviz layout, canonical persistence, and render
  -> final grounded semantic projection
```

A built-in context case does not call the live readiness-review LLM. Its prevalidated JSON 1/JSON 2 authority and accepted policy form the model-visible exam material. The oracle remains evaluator-only. [`08-context-backed-generation/01-readiness/`](../03-design/01-context-generation/01-readiness/README.md) keeps its independent readiness calibration and release semantics.

### RepoBench

RepoBench separately evaluates the full repository workflow:

```text
repository + natural-language request
  -> host inspection
  -> JSON 1
  -> JSON 2
  -> live readiness
  -> grounded generation
  -> final diagram
```

Built-in generator results and RepoBench results are reported separately. Neither substitutes for the other.

### Primary quality target

The primary candidate is the final canonical `.gp.json` projected to normalized semantics. The projection removes coordinates, dimensions, styles, viewport, layout/runtime metadata, and trace fields while retaining:

- exact node and edge semantic types;
- labels and logical IDs needed for internal reference;
- topology, direction, containment, guards, and branch meaning;
- multiplicities, extension points, relationship ends, features, and constraints; and
- context element origins.

Blocked and error outcomes are delivery failures. They remain observations and are never omitted from aggregates.

## Evaluation architecture and capture seam

Generation owns a neutral immutable observer seam; evaluation implements an observer without being imported by generation:

```text
GenerationObserver
  on_stage
  on_provider_call
  on_candidate
  on_result
```

Normal generation uses a no-op observer. Runtime diagnostics and offline evaluation use separate implementations. The evaluation observer captures complete bounded stage evidence without changing generation acceptance, retries, packets, or results.

Every observation records and digests:

```text
case, question, authority, and oracle identities
exact generation input
raw logical response
strict and deterministic issues
generation-repair inputs/results
normalized pre-layout candidate
runtime semantic-review response and deterministic result
semantic-repair inputs/results
final canonical diagram
final semantic projection
render result
all provider-call identities and usage
stage and total latency
outcome, operation warnings, and OperationProblem errors
```

Every capture also records the exact Git commit; generation mode/type; chat and embedding deployments/model identities; effective provider controls; quality mode; repair budgets; and prompt, schema, semantic-profile, example-set, runtime-rubric, evaluator-rubric, matcher, gate, and layout versions/digests. Secret values and raw credentials are never captured.

Failure attribution names the first failing stage and contributing defects across input contract, provider call, strict response, deterministic validation, generation repair, runtime semantic review, semantic repair, layout, canonical validation, persistence, render, and hidden-gold semantic mismatch.

## Case and oracle design

### Case contract

Each `graphpilot.evaluation.case.v1` / `generationEvaluationCase` records:

```text
caseId
generationMode: direct | context
diagramType
caseCategory
questionAuthorityRef
oracleRef
caseSetVersion
```

The sealed built-in set has 48 cases: eight in each direct/context × Activity/Use Case/BDD cell. Every cell contains one case from each category:

1. foundational;
2. alternative valid topology;
3. multi-intent;
4. advanced type semantics;
5. ambiguity/assumption boundary;
6. omission trap;
7. unsupported-addition trap; and
8. scale boundary.

### Oracle contract

Each `graphpilot.evaluation.oracle.v1` / `generationEvaluationOracle` contains:

```text
referenceLogicalDiagram
requiredConcepts
optionalConcepts
forbiddenConcepts
requiredRelationships
requiredStructuredFields
acceptedLabelAliases
acceptableStructuralAlternatives
acceptableGroundingSets
additionPolicy
```

The oracle combines one independently reviewed reference graph with explicit bounded equivalence rules authored before candidate generation. It does not require exact candidate IDs, wording, or layout. Concepts may be marked critical. Missing any critical concept fails that observation regardless of average recall. An explicit forbidden concept or adjudicated contradictory context fact is a hard failure.

Answer-key authoring, independence, and the training/evaluation firewall are owned by [`06-answer-key-generation-design.md`](../03-design/09-answer-key-generation.md).

## Deterministic matcher

### Explicit embedding configuration

Semantic label alignment uses exactly one explicit embedding deployment:

```text
AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT
```

There is no default, local lexical-only certification mode, reuse of the chat deployment, or alternate embedding fallback. Missing configuration is a typed evaluation failure. Offline tests use deterministic fake embeddings; a real embedding call occurs only in an explicitly authorized live run.

Gold-bearing matcher resolution is ephemeral by default: oracle text, aliases, content digests, and vectors are never
persisted in a cache. An explicit visible-only framework test may exercise the immutable cache keyed by deployment/model
identity, preprocessing version, and exact normalized content digest; that cache is not used for hidden or oracle-bearing
runs and never counts as certification evidence.

### Alignment algorithm

For each candidate/oracle pair, the matcher:

1. normalizes labels and applies exact approved aliases;
2. computes fixed versioned embedding similarity for remaining concepts;
3. applies hard semantic-type compatibility filters;
4. scores topology/neighborhood and structured-field compatibility;
5. solves deterministic maximum-weight one-to-one assignment; and
6. classifies matches as accepted, missing, extra, or ambiguous.

One candidate element cannot satisfy multiple gold concepts. Exact or embedding-near wording cannot override a hard type, direction, containment, topology, or field contradiction. Embedding identity, preprocessing, thresholds, feature weights, assignment algorithm, and tie-breaks are frozen and recorded. Ambiguity is preserved for the judge and, when material, human adjudication.

### Deterministic grades

The matcher grades:

- final delivery, canonical schema, graph, render, and mode/type vocabulary;
- required, optional, forbidden, and extra concepts;
- semantic-type accuracy;
- required and extra relationship identity/direction;
- topology and containment;
- structured fields;
- match confidence and ambiguity; and
- context origin presence and exact selected/accepted/allowlisted reference mechanics.

Type-specific checks include:

| Type | Mechanical checks |
| --- | --- |
| Activity | trigger, actions, sequence, guards/outcomes, merge versus join, fork/join concurrency, exception/retry paths, reachability |
| Use case | actors/goals/participation, subject containment, include/extend direction and meaning, extension conditions/locations, specialization direction |
| BDD | Block/entity coverage, compact-property versus expanded-definition alternatives, property kinds/types/defaults/multiplicities, relationship direction, constraints, relationship ends |
| Context | origin presence, exact allowlisted refs, schema-rule validity, nonempty grounding, duplicate-ref rejection |

Code proves origin-reference mechanics; semantic support and minimality remain judge/human questions.

The `graphpilot.evaluation.deterministic-report.v1` / `evaluationDeterministicReport` contains concept alignment, relationship and structured-field checks, forbidden matches, extra candidate inventory, origin-reference checks, delivery checks, metrics, and ambiguities.

## Independent blinded evaluation judge

### Deployment and independence

Generation, readiness, runtime semantic review, evaluation judging, and report analysis use the single shared chat deployment:

```text
AZURE_OPENAI_DEPLOYMENT
```

There is no second judge or report-analysis deployment setting and no fallback. Missing chat configuration is a typed live-evaluation failure. Judge independence comes from:

- a separate provider call after generation;
- a private versioned evaluation prompt and rubric;
- blinded input;
- no access to generator model identity, condition identity, runtime semantic-review result, or runtime repair decisions; and
- an explicit same-deployment caveat in the run manifest and report.

The judge sees the case question/authority, hidden oracle, final candidate semantic projection, deterministic alignment/report, allowlisted IDs, and the fully composed evaluation rubric. It does not see raw source outside case authority, hidden chain-of-thought, generation examples, or runtime reviewer output.

### Judge contract and rubric

The strict input is `graphpilot.evaluation.semantic-judge-input.v1` / `evaluationSemanticJudgeInput`. The private response is `graphpilot.evaluation.semantic-judge-response.v1` / `evaluationSemanticJudgeResponse` and contains canonical-order facet results, bounded material-fact assessments, typed proposed findings, and `adjudication: clear|uncertain` with a reason.

Every applicable facet uses the shared `0..4` scale and `minimumRating: 3`:

| Facet | Weight | `blockingBelow` | Applicability |
| --- | ---: | ---: | --- |
| `intentFidelity` | 4 | 2 | all cases |
| `semanticCompleteness` | 4 | 2 | all cases |
| `authorityFidelity` | 4 | 3 | all cases |
| `elementMeaning` | 4 | 2 | all cases |
| `relationshipTopologyMeaning` | 4 | 2 | all cases |
| `structuredDataFidelity` | 3 | 2 | when structured semantics apply |
| `abstractionCoherence` | 2 | 1 | all cases |
| `extraContentQuality` | 3 | 2 | all cases |
| `diagramUsefulness` | 2 | 1 | all cases |
| `inferenceAppropriateness` | 3 | 2 | direct only |
| `groundingFidelity` | 4 | 3 | context only |
| `viewpointFidelity` | 4 | 3 | context only |

Ratings mean: `0` contradicted/absent/unusable; `1` major semantic failure; `2` partial but materially incomplete/ambiguous; `3` sufficient and correct; `4` complete, precise, and clearly useful.

The judge may assess at most 64 material facts tied to required oracle semantics, candidate extras, matcher/judge disagreement, or a facet below 4. Fact kinds are entity, behavior, relationship, ordering, condition, property, constraint, and multiplicity; statuses are `supported`, `unsupported`, `contradicted`, or `uncertain`. Every assessment cites allowed candidate, gold, and authority refs.

The judge never outputs final score, severity, gate status, pass/fail, or promotion. The backend validates facets, applicability, refs, fact evidence, and bounds, then computes the weighted 0–100 summary and every category gate. One strict response-contract repair may correct invalid shape or refs without changing the judgment; a second invalid response fails the observation.

### Human adjudication

Humans review only ambiguous assignments, material deterministic/judge disagreement, judge uncertainty, and promotion-changing borderlines. Each adjudication records exact issue/evidence, decision, rationale, reviewer, timestamp, and any resulting match/fact change. Required adjudications must be complete before a run can pass.

## Metrics and aggregation

Per observation, the backend calculates:

```text
final delivery and hard validity
required-concept recall and precision
semantic-type accuracy
relationship recall, precision, and F1
topology correctness
structured-field accuracy
forbidden and extra classifications
context origin validity, support, and minimality
judge facet ratings and material-fact rates
runtime semantic-review false-pass and false-block
helpful and harmful generation/semantic repair
calls, tokens, stage latency, and total latency
first failing stage and contributing defects
```

Aggregation is observation → case across three repetitions → six equal-weight mode/type cells → informational overall. Large cases cannot dominate. Every cell must independently pass; an overall average cannot compensate for a failed cell or hard gate.

## Reviewed certification condition

The required production condition is `reviewed`. Explicit `standard` is environment-only diagnostic/ablation mode, never an automatic fallback and never a substitute for certification.

```text
48 hidden cases × 3 reviewed repetitions = 144 observations
minimum per observation:
  generation + runtime semantic review + independent evaluation judge
minimum confirmatory chat calls:
  432, plus repair calls and one report-analysis call per completed run
```

A standard-mode ablation and an isolated historical-commit baseline are optional, separately manifested, and informational. Historical comparison never requires retaining an old runtime path.

## Execution control, manifests, and resume

Every invocation requires an explicit value:

```text
executionMode=dry_run | live
```

There is no default.

- `dry_run` validates contracts, case order, repetitions, deployments, versions, estimated calls, output paths, and resume behavior. It makes zero provider calls and cannot certify.
- `live` writes an immutable exact manifest before the first provider call, executes only that manifest, and resumes by unique run/case/repetition/condition identity.

Live execution never silently adds cases, conditions, repetitions, ablations, or baselines; never retries a completed observation; and never rerolls a blocked/error/low-quality observation for a better outcome. Invoking `live` authorizes only the exact written manifest. A changed manifest requires a new run identity.

The operator command is `run_generation_evaluation`. Its required positional mode is followed by exact canonical
`--manifest`, `--case-set`, `--control-workspace`, and separate `--evaluated-workspace` paths. Argument omission/unknown
mode fails in Django parsing before service/provider construction. The manifest commit must equal a clean checked-out Git
worktree, so uncommitted code cannot masquerade as the recorded identity. The manifest and case set also bind explicit
`visible|hidden` visibility; visible evidence can produce framework reports but never hidden certification.

The `graphpilot.evaluation.run-manifest.v1` / `generationEvaluationRunManifest` records:

```text
runId and executionMode
sealed case-set version/digest and ordered IDs
repetition count and exact reviewed condition
Git commit
chat and embedding deployment/model identities and effective controls
all prompt/schema/profile/example/rubric/matcher/gate versions and digests
repair budgets and quality mode
embedding preprocessing, thresholds, and assignment identity
output root, observation identities, and resume policy
createdAt
```

## Backend-owned certification gates

No composite score, judge opinion, or report-analysis prose can override a failed gate.

### Zero-tolerance hard gates

Any observation fails certification if it has:

- an invalid final canonical schema, graph, or origin;
- wrong mode/type vocabulary;
- silent authority or example truncation/substitution;
- silent reviewed-to-standard fallback;
- a persisted semantic blocker;
- corrupt version or run identity;
- an explicit forbidden concept; or
- an adjudicated contradictory context fact.

### Initial per-cell thresholds

Each cell contains eight cases × three repetitions = 24 observations.

| Dimension | Gate |
| --- | ---: |
| Final delivery rate | `>=95%` |
| Critical required concepts | `100%` per observation |
| Overall required-concept recall | `>=90%` |
| Semantic-type accuracy | `>=95%` |
| Relationship/topology F1 | `>=90%` |
| Structured-field accuracy | `>=90%` |
| Judge intent-fidelity mean | `>=3.0/4` |
| Judge authority-fidelity mean | `>=3.2/4` |
| Judge topology-meaning mean | `>=3.0/4` |
| Judge usefulness mean | `>=3.0/4` |
| Context grounding-fidelity mean | `>=3.2/4` |
| Unsupported material-fact rate | `<=2%` |
| Runtime semantic-review false-pass rate | `<=5%` |
| Runtime semantic-review false-block rate | `<=5%` |
| Harmful semantic-repair rate | `<=5%` |
| Evaluation-judge/human calibration agreement | `>=90%` |

Visible calibration may make a threshold stricter through a new frozen gate version. Hidden outcomes may not weaken thresholds. Calls, tokens, cost, and latency are reported but remain informational until a separate product budget is approved.

## Reports

Each run writes under:

```text
.graphpilot/evaluation/runs/<run-id>/
  manifest.json
  observations/<case-id>/repetition-001.json
  observations/<case-id>/repetition-002.json
  observations/<case-id>/repetition-003.json
  case-summaries/
  cell-summaries/
  report-analysis.json
  report.json
  report.md
```

`report.json` is machine authority. It contains run identity, completeness, adjudication state, hard gates, category gates, six cell scorecards, case/observation references, failure attribution, runtime reviewer/repair metrics, usage/latency, and exact versions. `report.md` presents the same backend status and evidence for humans.

Certification status is exactly `pass`, `fail`, or `not_run`:

- `pass` requires a complete live reviewed run, every required adjudication, and every hard/category gate;
- `fail` covers any failed gate, incomplete/invalid live observation, unresolved required adjudication, or invalid run identity; and
- `not_run` covers dry-run, missing explicit live authorization/configuration, or absence of a completed certification run.

One strict report-analysis call per completed run uses `AZURE_OPENAI_DEPLOYMENT`. It receives backend-calculated identities, status, six cell scorecards, gates, failure clusters, deterministic/judge/fact aggregates, reviewer/repair metrics, usage/latency, adjudications, and bounded representative case summaries. Its output contains evidence-cited interpretation, strengths, risks, failure patterns, recommendations, and caveats. It cannot invent metrics/cases or change backend status. A run-level checkpoint and immutable terminal prevent duplication after interruption; uncertainty records `analysisStatus: failed` rather than calling again. Any failure leaves deterministic JSON/Markdown reports valid.

## Visible calibration and framework proof

Before generator/evaluator freeze or hidden authoring, visible non-held-out pools prove the machinery:

- synthetic schema and integration fixtures;
- human-labeled alias, embedding-threshold, type-filter, topology, field, assignment, ambiguity, and tie-break cases;
- visible blinded-judge rubric/fact cases with human labels;
- generated/blocked/error and helpful/harmful-repair cases;
- dry/live, immutable-manifest, strict-resume, and no-expansion cases;
- six-cell aggregation and gate boundary cases; and
- separately authorized visible live embedding, judge, and report-analysis cases.

Visible human-labeled calibration must meet the matcher/judge agreement targets. One visible live run produces complete JSON and Markdown artifacts but cannot certify the generator. Normal automated tests use fake embeddings and fake chat clients and make no provider calls.

`calibrate_generation_evaluation` evaluates the committed visible bundle without constructing provider clients. Its report
keeps `offlineFrameworkProof`, `visibleProviderEvidence`, and `humanCalibration` separate; the committed synthetic bundle
may pass only the first. `canCertifyGeneration` is always false. Provider-backed and genuinely human-labeled evidence must
be supplied by their separately authorized workflows rather than inferred from fake clients or synthetic labels.

## Leakage firewall and freeze

The framework enforces these boundaries:

1. Training fixture identities and gold never overlap hidden built-in or RepoBench cases.
2. Visible calibration cases are labeled visible and never count as hidden evidence.
3. Generator, runtime reviewer, matcher, judge, report analyst, thresholds, schemas, prompts, examples, and versions freeze before hidden authoring.
4. Prompt/training authors cannot author or approve hidden gold.
5. Every hidden case has an independent author, reviewer, and adjudicator.
6. Hidden gold lives outside the evaluated repository/workspace, model-visible prompts/examples, and production package.
7. Generation receives only question/authority; the judge receives gold only after generation completes.
8. A leakage validator proves that no gold path, content, digest, alias table, vector, or oracle metadata reaches generation packets, generation-role provider payloads, observer captures, evaluated workspaces, generation traces, caches, generation reports, or logs. Evaluator-only judge packets remain allowed only after generation completes.
9. There is no hidden pilot; all 48 cases are reserved for the frozen three-repeat run.
10. If hidden outcomes change the generator or evaluator, the exposed set becomes historical and a new independent set is required. A framework defect invalidates the run; independent adjudication determines case replacement before rerun.

A freeze-readiness artifact records the exact commit, case-set visibility/version/digests, shared chat and explicit
embedding settings/deployment/model identities, prompts, schemas, semantic profiles, examples, runtime/evaluator rubrics,
matcher, gates, controls, thresholds, calibration evidence, and leakage report. Its states are separately
`offlineFrameworkProof`, `visibleProviderEvidence`, `freezeReadiness`, `hiddenCertification`, and `productionPromotion`;
without measured visible provider and human evidence or a pass covering every required leakage surface, freeze remains
`not_ready`, hidden certification remains `not_run`, and production remains `not_promoted`. The evaluator control workspace
is intentionally excluded from prohibited-surface scanning because it is the authorized home of oracle evidence; only its
generation-facing boundaries are scanned. RepoBench follows the same firewall.

## DOE and ablation policy

Design-of-experiments work uses visible cases before freeze and changes one factor at a time. It is engineering evidence, not hidden certification. Supported visible comparisons include:

| Factor | Controlled comparison |
| --- | --- |
| Request packaging | legacy-style Markdown versus canonical direct JSON |
| Host framing | raw prompt versus workflow-framed request |
| Training examples | zero versus fixed two; historical versus approved examples |
| Context examples | direct-example misuse versus context-native examples |
| Quality mode | explicit `standard` versus `reviewed` |
| Historical baseline | one exact recorded historical commit versus redesign |
| Prompt phrasing | controlled visible paraphrases with one fixed oracle |

Each ablation has its own manifest and report and cannot alter the required reviewed condition. Model, prompt, example, matcher, rubric, or threshold choices informed by visible experiments must freeze before independent hidden authoring.

## Related owners

- [`09-workflow-audit-design.md`](../03-design/11-workflow-audit.md) — separate operational request-to-visible-editor scenarios, evidence accounting, recovery, reports, and compatibility baselines; provider-free audit evidence is not certification.
- [`06-answer-key-generation-design.md`](../03-design/09-answer-key-generation.md) — exact training fixtures, manifests, derivation, sign-off, and gold-authoring firewall.
- [`04-generation-design.md`](../03-design/07-generation.md) — generation, repair, reviewed quality mode, and PyGraphviz behavior under evaluation.
- [`08-context-backed-generation/`](../03-design/01-context-generation/README.md) — context authority, readiness, provenance, result, and trace semantics.
- [`02-validation-design.md`](../03-design/05-validation.md) — deterministic runtime validation, which remains separate from evaluation.
- [`decision-decisions.md`](../05-delivery/04-decisions.md) — active accepted evaluation and generation decisions; evaluation outcomes do not become design decisions unless they change the intended contract.
