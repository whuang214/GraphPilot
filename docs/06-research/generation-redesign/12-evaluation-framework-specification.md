# Generation Evaluation Framework Specification

> **Status: user-approved evaluation design (2026-07-17); implementation not approved.** Approval is recorded in
> `evaluation-framework-approval.json`. This document specifies the offline framework that certifies the redesigned
> generator against absolute hidden-gold quality gates. It is not a production validation stage.

## Purpose

The framework answers:

> Given unseen direct/context questions with independently authored golds, does frozen redesigned GraphPilot generate
> correct, grounded, useful final diagrams consistently, and what calls/tokens/latency does that require?

The current implementation is recorded by exact Git commit and may be run later as an isolated informational
historical reference. It is not retained in the redesigned runtime and is not a certification requirement.

## Evaluation boundaries

### Built-in generator suite

Direct boundary:

```text
frozen validated DirectRequest
→ generation input builder
→ strict generation/repair
→ runtime reviewed-mode semantic review/repair
→ PyGraphviz/canonical persistence/render
→ final semantic projection
```

Context boundary:

```text
frozen validated JSON 1 + JSON 2
→ deterministic resolver and accepted frozen generation policy identity
→ strict generation/repair
→ runtime reviewed-mode semantic review/repair
→ PyGraphviz/canonical persistence/render
→ final grounded semantic projection
```

Built-in context cases do not invoke a live readiness-review LLM. The prevalidated question/authority packet is the
model-visible exam question/reference material; the hidden expected diagram/oracle is evaluator-only.

### RepoBench

RepoBench owns end-to-end repository evaluation:

```text
repository + natural-language request
→ host inspection
→ JSON 1
→ JSON 2
→ live readiness
→ grounded generation
→ final diagram
```

## Primary candidate and captures

The primary quality target is the final canonical diagram projected to normalized semantics. The projection removes
coordinates, dimensions, styles, viewport, layout/runtime metadata, and trace fields while retaining exact semantic
types, labels, topology, structured fields, and context origins.

Every observation captures/digests:

```text
case/question/authority identity
exact generation input
raw logical response
strict/deterministic issues
generation repairs
normalized candidate
runtime semantic-review response/result
semantic repairs
final canonical diagram
final semantic projection
render result
provider calls/usage
stage latency
outcome, warnings, and operation errors
```

Every capture records exact commit, model/deployment, prompt/schema/profile/example/rubric versions, quality mode,
repair budgets, and effective provider controls. Blocked/error observations remain scored delivery failures and are
never omitted from aggregates.

## Case and oracle contracts

### Case contract

```text
schemaVersion: graphpilot.evaluation.case.v1
kind: generationEvaluationCase
caseId
generationMode: direct|context
diagramType
caseCategory
questionAuthorityRef
oracleRef
caseSetVersion
```

The future sealed set contains 48 cases: eight per direct/context × activity/use-case/BDD cell. Categories are
foundational, alternative topology, multi-intent, advanced semantics, ambiguity/assumption boundary, omission trap,
unsupported-addition trap, and scale boundary.

### Oracle contract

```text
schemaVersion: graphpilot.evaluation.oracle.v1
kind: generationEvaluationOracle
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

The oracle combines one reviewed reference graph with explicit equivalence rules. It does not require exact IDs,
wording, or layout. All accepted alternatives are bounded and authored before candidate generation.

Concepts may be marked critical. Missing a critical concept is an observation failure regardless of aggregate recall.
Explicit forbidden concepts and adjudicated contradictory context facts are hard failures.

## Deterministic matcher

### Alignment stages

```text
1. normalize labels and match exact approved aliases
2. compute fixed versioned embedding similarity for unmatched concepts
3. apply hard semantic-type compatibility
4. score topology/neighbors and structured-field compatibility
5. solve deterministic maximum-weight one-to-one assignment
6. classify matched, missing, extra, or ambiguous
```

One candidate element cannot satisfy multiple gold concepts. Exact wording cannot override a hard type/topology
contradiction. Embedding model/version, preprocessing, thresholds, weights, and assignment tie-breaks are frozen and
captured. Ambiguous assignments proceed to the evaluation judge and possibly humans.

### Deterministic grades

General:

```text
final delivery/schema/render
required/optional/forbidden concept coverage
semantic-type accuracy
required/extra relationship identity and direction
topology and containment
structured fields
extra element/relationship inventory
match confidence/ambiguity
```

Activity:

```text
trigger/actions/sequence
decision guards and outcomes
merge versus join meaning
fork/join concurrency
exception/retry paths
reachability
```

Use case:

```text
actors/goals/participation
subject containment
include/extend direction and meaning
extension conditions/locations
generalization specialization direction
```

BDD:

```text
Block/entity coverage
compact property versus expanded definition alternatives
property kinds/types/defaults/multiplicities
association/composition/generalization/dependency direction
constraints and relationship ends
```

Context mechanics:

```text
origin presence
selected/accepted/allowlisted exact refs
schema-rule validity
at-least-one grounding
no duplicate refs
```

Code proves ref validity, not semantic support.

### Deterministic report

```text
schemaVersion: graphpilot.evaluation.deterministic-report.v1
kind: evaluationDeterministicReport
conceptAlignment
relationshipChecks
structuredFieldChecks
forbiddenMatches
extraCandidateElements
originReferenceChecks
deliveryChecks
metrics
ambiguities
```

## Independent evaluation judge

Certification uses the single explicit `AZURE_OPENAI_DEPLOYMENT` for the evaluation judge/report analyst as well as
runtime chat roles; missing chat configuration is a typed failure and there is no alternate deployment fallback. Judge
independence is enforced by a separate call, private evaluation prompt/rubric, blinded input, and a recorded
same-deployment caveat. The judge is blinded to generator model, condition identity, and runtime reviewer result.

### Judge input

```text
schemaVersion: graphpilot.evaluation.semantic-judge-input.v1
kind: evaluationSemanticJudgeInput
case/question authority
hidden oracle
final candidate semantic projection
deterministic alignment/report
allowlisted gold/candidate/authority IDs
final composed evaluation rubric and versions
```

### Rating scale

```text
0: contradicted, absent, or unusable
1: major semantic failure
2: partially correct but materially incomplete/ambiguous
3: sufficient and correct
4: complete, precise, and clearly useful
```

### Judge facets

All applicable facets use `minimumRating=3`.

| Facet | Weight | `blockingBelow` | Applicability / meaning |
| --- | ---: | ---: | --- |
| `intentFidelity` | 4 | 2 | Answers requested goal/scope |
| `semanticCompleteness` | 4 | 2 | Material concepts/behaviors/outcomes represented |
| `authorityFidelity` | 4 | 3 | Every material fact authorized; no hallucination |
| `elementMeaning` | 4 | 2 | Matched nodes mean expected concepts |
| `relationshipTopologyMeaning` | 4 | 2 | Edges/direction/order/branches/containment/concurrency mean the right thing |
| `structuredDataFidelity` | 3 | 2 | Guards/multiplicity/properties/constraints/extension/end data mean the right thing |
| `abstractionCoherence` | 2 | 1 | Detail is coherent for audience/scope |
| `extraContentQuality` | 3 | 2 | Unmatched additions are acceptable rather than unsupported/contradictory |
| `diagramUsefulness` | 2 | 1 | Diagram is accurate, clear, and useful |
| `inferenceAppropriateness` | 3 | 2 | Direct only: inference remains non-material and within authority |
| `groundingFidelity` | 4 | 3 | Context only: origins genuinely/minimally support meaning |
| `viewpointFidelity` | 4 | 3 | Context only: remains current as-implemented truth |

Type-specific required subchecks bind to these facets:

```text
Activity: trigger, sequence, guards, outcomes, concurrency, exception/retry
Use case: actors, goals, participation, subject, include/extend, extension points, generalization
BDD: Blocks, ownership/reference, property/type/multiplicity, generalization/dependency, constraints
```

### Material fact assessments

The judge assesses only material facts tied to required oracle semantics, candidate extras, matcher/judge disagreement,
or a facet below 4. Max 64.

```text
kinds: entity, behavior, relationship, ordering, condition, property, constraint, multiplicity
status: supported, unsupported, contradicted, uncertain
required refs: candidate IDs, gold IDs, authority refs, concise rationale
```

### Judge response

```text
schemaVersion: graphpilot.evaluation.semantic-judge-response.v1
kind: evaluationSemanticJudgeResponse
rubricVersion
canonical-order facetResults
materialFactAssessments
proposedFindings
adjudication: clear|uncertain + reason
```

The judge never outputs final score, pass/fail, severity gates, or promotion. Backend validates every facet/ref/evidence
requirement and computes the 0–100 weighted summary and independent category gates. One strict response-contract
repair may fix invalid shape/refs without changing candidate judgment; a second invalid response fails the observation.

## Human adjudication

Humans review only ambiguous matches, material deterministic/judge disagreement, judge uncertainty, and
promotion-changing borderline cases. Adjudication records exact issue/evidence, decision, rationale, reviewer,
timestamp, and whether it changes matching/fact status. Required adjudications must complete before `pass`.

## Metrics and attribution

Per observation:

```text
final delivery and hard validity
required concept recall/precision
semantic-type accuracy
relationship recall/precision/F1
topology correctness
structured-field accuracy
forbidden/extra classifications
context origin validity/support/minimality
judge facet ratings and material facts
runtime semantic-review false pass/block
helpful/harmful generation and semantic repair
calls/tokens/stage/total latency
first failing stage and contributing defects
```

Aggregation is per observation → case across three repetitions → six equal-weight mode/type cells → overall. Large
cases do not dominate; every cell passes independently. Reports slice by case category and complexity.

Failure stages are input contract, provider call, strict response, deterministic validation, generation repair,
runtime semantic review, semantic repair, layout, canonical validation, persistence, render, and hidden-gold semantic
mismatch.

## Conditions and repetitions

Production/default generation quality is revised to `reviewed`. `standard` remains explicit environment-only
ablation/diagnostic mode and is never an automatic fallback.

Required hidden certification:

```text
48 cases × 3 reviewed repetitions = 144 observations
minimum calls per observation:
  generation + runtime semantic review + independent evaluation judge
minimum confirmatory LLM calls: 432, plus repairs and one report-analysis call
```

Optional standard ablation and optional historical baseline-commit runs require separate manifests and do not control
reviewed certification.

## Execution modes and run manifest

Every invocation requires explicit `executionMode=dry_run|live`; there is no default.

Dry run validates and reports planned cases/repetitions/calls/deployments/versions/output/resume behavior without
provider calls. Live writes an immutable manifest before the first call, executes exactly that manifest, and resumes
by unique run/case/repetition/condition identity without duplicating completed observations. It never expands
conditions/repetitions/baseline automatically or rerolls failures for better outcomes.

Run manifest contract:

```text
schemaVersion: graphpilot.evaluation.run-manifest.v1
kind: generationEvaluationRunManifest
runId
executionMode
caseSet seal/version/digest and ordered IDs
repetitions
reviewed condition
commit
all deployment/model/effective controls
all prompt/schema/profile/example/rubric/matcher/gate versions/digests
repair budgets
embedding identity/thresholds
output root and resume policy
createdAt
```

## Certification gates

### Zero-tolerance hard gates

Any observation with the following fails certification:

```text
invalid final canonical schema/graph/origin
wrong mode/type vocabulary
silent authority/example truncation
silent reviewed-to-standard fallback
semantic blocker persisted
corrupt version/run identity
explicit forbidden concept
adjudicated contradictory context fact
```

### Initial per-cell thresholds

Each cell contains eight cases × three repetitions = 24 observations.

| Dimension | Minimum / maximum |
| --- | ---: |
| Final delivery rate | `>=95%` |
| Critical required concepts | `100%` per observation |
| Overall required-concept recall | `>=90%` |
| Semantic-type accuracy | `>=95%` |
| Relationship/topology F1 | `>=90%` |
| Structured-field accuracy | `>=90%` |
| Judge intent fidelity mean | `>=3.0/4` |
| Judge authority fidelity mean | `>=3.2/4` |
| Judge topology meaning mean | `>=3.0/4` |
| Judge usefulness mean | `>=3.0/4` |
| Context grounding fidelity mean | `>=3.2/4` |
| Unsupported material fact rate | `<=2%` |
| Runtime semantic-review false-pass rate | `<=5%` |
| Runtime semantic-review false-block rate | `<=5%` |
| Harmful semantic-repair rate | `<=5%` |
| Evaluation-judge human agreement on calibration | `>=90%` |

Visible calibration may make thresholds stricter. Hidden outcomes may not weaken them. Cost/latency/calls/tokens are
informational until a separate product budget is approved.

## Reports

Artifact tree:

```text
.graphpilot/evaluation/runs/<run-id>/
  manifest.json
  observations/<case-id>/repetition-001..003.json
  case-summaries/
  cell-summaries/
  report-analysis.json
  report.json
  report.md
```

Status is `pass|fail|not_run`. `not_run` covers dry-run, missing live authorization/config, or absent certification.
Incomplete/invalid observations or unresolved adjudication make live certification fail.

### Aggregate report-analysis LLM

One strict call per completed run receives backend-calculated manifest identity, certification status, six cell
scorecards, gates, failure clusters, deterministic/judge/fact aggregates, reviewer/repair metrics, usage/latency,
adjudications, and bounded representative case summaries.

Contracts:

```text
graphpilot.evaluation.report-analysis-input.v1
graphpilot.evaluation.report-analysis-response.v1
graphpilot.evaluation.report-analysis-prompt.v1
```

The response contains executive interpretation, strengths, risks, failure patterns, runtime reviewer/repair analysis,
cost/latency interpretation, recommendations, and caveats. Every statement cites known metric/gate/case/finding IDs.
It never invents numbers/cases or changes backend status. Failure leaves deterministic reports valid with
`analysisStatus=failed`.

`report.json` is machine authority. `report.md` presents backend status/gates/cells first, then validated LLM
interpretation, recommendations, caveats, usage, adjudications, and exact identities.

## Framework calibration and leakage firewall

Visible pools validate/tune framework machinery:

```text
synthetic unit/integration fixtures
human-labeled deterministic matcher cases
visible embedding threshold cases
visible evaluation-judge rubric/fact cases
visible live provider/report-analysis cases
```

The generator, matcher, judge, report analyst, thresholds, schemas, prompts, and versions freeze before hidden case
authoring. Prompt/training authors cannot author/approve hidden gold. Each hidden case has independent author, reviewer,
and adjudicator. Hidden gold lives outside evaluated repository/workspace, model-visible prompts/examples, and the
production package. Generation calls receive only question/authority; the judge receives gold after generation.

The 48 hidden cases are reserved for the frozen three-repeat certification run; no hidden pilot is used. If hidden
results drive generator/evaluator changes, the old set becomes historical and a new independently authored set is
required for recertification. A genuine framework defect invalidates the run; independent adjudicators determine
whether exposed cases must be replaced before rerun. RepoBench uses the same firewall.

## Framework implementation proof

Before hidden authoring:

1. All schemas and fake observations/reports validate with exact bounds.
2. Deterministic matcher unit cases cover aliases, embeddings, type filters, topology, fields, assignment, extras,
   ambiguity, and tie-breaks.
3. Visible human-labeled calibration meets embedding/matcher and judge agreement targets.
4. Judge/response-repair/report-analysis prompts are strict, blinded where required, and reference-validating.
5. Dry/live required-mode behavior, immutable manifests, resume identity, and no automatic expansion are tested.
6. Generated/blocked/error/delivery failures remain observations and aggregate correctly.
7. Six-cell macro aggregation and every hard/threshold gate are tested at boundary values.
8. Leakage tests prove no gold path/content reaches generator packets/workspaces.
9. One visible live calibration run produces complete JSON/Markdown artifacts without certifying the redesign.
10. Generation and evaluation designs are jointly promoted before implementation begins.
