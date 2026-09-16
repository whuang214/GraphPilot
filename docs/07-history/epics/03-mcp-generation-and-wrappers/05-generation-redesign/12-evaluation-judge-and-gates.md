# Slice 12: Evaluation Judge and Gates

## Purpose

Add the logically independent, blinded evaluation judge and backend-owned semantic metrics, absolute certification
gates, adjudication records, deterministic reports, and aggregate report analysis. The slice proves all behavior against
visible gold with fake LLM clients and does not perform live certification.

## Background

Slice 11 supplies reproducible alignment and a deterministic report, but code cannot decide every semantic equivalence,
authority claim, grounding assertion, or useful abstraction. A strict evaluation judge assesses those bounded questions.
It does not replace deterministic matching, runtime semantic review, or human adjudication, and it never decides the
final score or certification status.

The user approved one `AZURE_OPENAI_DEPLOYMENT` chat deployment for generation, readiness/runtime review, evaluation
judge, response repair, and report-analysis roles. Judge independence is therefore logical and informational: it has a
separate versioned role, prompt, schema, invocation, and blinded packet, while manifests/reports truthfully record the
shared-deployment caveat. `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT` remains separate for Slice 11 embeddings.

## Design

- Build a strict judge packet from the visible case question/authority, visible oracle, final candidate semantic
  projection, deterministic alignment/report, allowlisted authority/gold/candidate IDs, and one fully composed versioned
  rubric. Exclude generator model/deployment identity, condition labels, runtime reviewer result, runtime repair verdict,
  prior scores, and desired outcome from the judge-visible packet.
- Use the approved 0–4 scale and required facets for intent fidelity, semantic completeness, authority fidelity, element
  meaning, relationship/topology meaning, structured-data fidelity, abstraction coherence, extra-content quality,
  usefulness, direct inference appropriateness, and context grounding/viewpoint fidelity. Every applicable facet has
  `minimumRating=3`; mode/type-specific subchecks remain mandatory where applicable.
- Permit at most 64 material fact assessments tied to required oracle semantics, candidate extras, matcher/judge
  disagreement, or a facet below 4. Each assessment has allowlisted candidate/gold/authority refs and one of
  `supported|unsupported|contradicted|uncertain`.
- Validate every facet, applicability decision, evidence ref, material fact, finding, and adjudication signal in code.
  The judge cannot return pass/fail, a final score, severity gates, or promotion. One strict response-contract repair may
  correct shape/references without rejudging the candidate; a second invalid response fails the observation.
- Compute per-observation delivery/validity, concept precision/recall, type accuracy, relationship precision/recall/F1,
  topology, structured fields, forbidden/extras, origin mechanics/support, judge facets/facts, runtime false-pass/
  false-block, repair helpfulness/harm, calls/tokens/latency, and first-failing-stage attribution. Aggregate observation
  to case across repetitions, then six equal-weight mode/type cells, with overall results informational only.
- Enforce zero-tolerance hard failures for invalid final canonical schema/graph/origin, wrong mode/type vocabulary,
  silent authority/example truncation, silent reviewed-to-standard fallback, persisted semantic blockers, corrupt
  version/run identity, explicit forbidden concepts, and adjudicated contradictory context facts.
- Keep each approved per-cell category gate independent; no weighted composite may mask a failed category:

  | Dimension | Initial gate |
  | --- | ---: |
  | Final delivery rate | `>=95%` |
  | Critical required concepts | `100%` per observation |
  | Required-concept recall | `>=90%` |
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
  | Judge/human visible-calibration agreement | `>=90%` |

- Represent human adjudication as a bounded immutable artifact with issue/evidence, decision, rationale, reviewer,
  timestamp, and matching/fact effect. Only ambiguity, material deterministic/judge disagreement, judge uncertainty,
  and promotion-changing borderlines require adjudication; unresolved required adjudication prevents `pass`.
- Build backend-authoritative `report.json` and human-readable `report.md` with `pass|fail|not_run`. One strict aggregate
  report-analysis call may interpret only backend-calculated evidence and must cite known metric/gate/case/finding IDs.
  It cannot alter status; invalid/unavailable analysis leaves deterministic reports valid with failed analysis status.
- Use `AZURE_OPENAI_DEPLOYMENT` for all chat-role clients with no role-specific deployment fallback chain. Record exact
  role/prompt/schema/effective controls and the shared-chat-deployment caveat without exposing credentials.

## Plan Audit

- **Dependency gate:** Slice 10 capture/contracts and Slice 11 matcher/report must be complete. Implementation follows the
  promoted active evaluation owner; this slice does not infer authority from older removed eval/DOE behavior.
- **Blinding gate:** snapshot and negative tests must prove generator identity, condition, runtime reviewer result,
  desired status, and prior outcomes are absent from the judge packet even though backend aggregation may later compare
  reviewer and judge results.
- **Deployment gate:** all chat roles resolve through `AZURE_OPENAI_DEPLOYMENT`; no
  `AZURE_OPENAI_EVALUATION_JUDGE_DEPLOYMENT`, report-analyst override, or silent fallback is added. The report records
  that deployment-level model independence was not claimed.
- **Decision-authority gate:** deterministic backend code owns score arithmetic, hard/category gates, aggregate
  weighting, pass/fail/not_run, and report authority. The judge and analyst return bounded evidence/interpretation only.
- **Gold/leakage gate:** committed judge and report fixtures use visible gold only. No hidden cases are authored, loaded,
  named, or simulated as certification evidence; hidden outcomes can never tune or weaken thresholds.
- **Failure gate:** generated, generated-with-warning, blocked, provider-error, invalid-judge, and unresolved-adjudication
  observations all aggregate conservatively. Invalid judge output is not dropped or favorably rerolled.
- **Safety and rollback:** normal tests use `FakeLLMClient` only and make no Azure calls. Rollback is an ordinary revert
  of this slice; versioned reports remain non-canonical historical artifacts and cannot change generation behavior.
- **Verification coverage:** tests hit every rating/facet/applicability/ref/fact bound, hard gate, threshold on both sides,
  macro-aggregation path, report citation rule, analyst failure, and status transition before the full offline gate.

Plan audit result: **Pass.** The audit confirmed one shared chat deployment with truthful caveat, strict judge blinding, backend-owned scores/gates/status, complete facets/facts/thresholds, bounded adjudication, analyst non-authority, visible fake-LLM coverage, and no generation feedback path.

## Included Work

- Strict semantic-judge input/response/response-repair schemas, composed rubric identities, prompts, and validators.
- Blinded judge packet assembly and one response-contract-only repair path through the shared fake/Azure chat seam.
- Material fact assessments, bounded findings, uncertainty/adjudication signals, and reference allowlists.
- Pure deterministic observation metrics, first-failure attribution, case aggregation, and six-cell macro aggregation.
- Every hard failure and per-cell category threshold, including exact boundary behavior and no composite override.
- Runtime reviewer false-pass/false-block and generation/semantic repair helpful/harmful attribution.
- Human adjudication artifact validation and conservative unresolved-state handling.
- Backend-authoritative JSON report, human Markdown rendering, and one strict aggregate report-analysis input/response.
- Evidence-citation validation and analyst failure isolation.
- Fake-LLM visible calibration fixtures and complete score/gate/report tests.
- Active evaluation, environment, testing, backend, and decision documentation updates required by implementation.

## Not In Scope

- Runner CLI/management-command execution, explicit dry/live orchestration, manifest resume, or repetitions; Slice 13
  owns them.
- Live judge, report-analysis, generation, readiness, or embedding calls while implementation is unattended.
- Hidden-gold authoring, hidden pilots, hidden certification, RepoBench gold, or production promotion.
- Changing generation/runtime semantic-review decisions or allowing evaluation results to feed generation.
- Cost/latency certification budgets; usage and latency remain reported information until separately approved.
- Deployment-level judge independence; the approved configuration deliberately uses one chat deployment for all roles.

## Target Areas

- judge, metric, gate, adjudication, report, and analyst modules under `backend/services/evaluation/`
- strict evaluation schemas, rubrics, and prompts under `backend/graphpilot/`
- shared injectable chat transport/fakes under `backend/services/llm/` without role-specific deployment settings
- `backend/tests/evaluation/` plus focused `backend/tests/llm/` contract/blinding tests
- `backend/.env.example` and active evaluation/environment/testing/backend/decision owners during implementation

## Exit Criteria

- Fake judge tests cover all facets, ratings, applicability, type-specific subchecks, 64-fact bound, allowed statuses,
  unknown/duplicate/missing refs, evidence requirements, and canonical ordering.
- Snapshot/negative tests prove strict blinding; the shared deployment identity is captured outside the judge packet and
  truthfully disclosed in reports.
- Exactly one response-contract repair is allowed, it cannot alter candidate judgment, and a second invalid response
  fails and remains in aggregation without reroll.
- Pure backend tests cover every zero-tolerance gate and every threshold immediately below, at, and above its boundary;
  all six cells must pass independently and large cases cannot dominate.
- Generated/blocked/partial/error observations, false-pass/false-block, helpful/harmful repair, unresolved adjudication,
  incomplete runs, and corrupt identity produce the conservative expected metrics/status.
- `report.json` is authoritative; `report.md` preserves status/gates/cells/identities; analyst output cites only known
  evidence, cannot alter status, and can fail without invalidating deterministic reports.
- All chat-role clients use only `AZURE_OPENAI_DEPLOYMENT`; no role-specific deployment variable or fallback exists.
  All normal tests use fake LLM responses and construct no provider client.
- No hidden case/gold is added or consumed and no evaluation artifact reaches generation imports or packets.
- Focused tests, `cd backend; uv run python manage.py test`, applicable stdio smoke, stale-role/config searches, and
  `git diff --check` pass with exact results recorded before commit.

## Previous Slice

- [`11-deterministic-matcher.md`](11-deterministic-matcher.md)

## Next Slice

- [`13-runner-and-visible-calibration.md`](13-runner-and-visible-calibration.md)

## Outcome

**Completion:** Added strict namespace-first judge input/response/repair, adjudication, report-analysis, and authoritative
report schemas plus private immutable prompts. `EvaluationJudgeService` builds a bounded packet from frozen case/
authority/oracle/projection/deterministic evidence, blinds generation condition/runtime-review and both generator and
embedding provider identities, enforces exact allowlists/rubric/applicability/facts/findings, permits one response-contract-
only repair, and returns backend-computed score/adjudication need. The judge cannot return score, severity, gates, pass/
fail, certification, or promotion authority.

**Metrics, gates, and decisions:** Added the immutable 12-facet composed rubric, complete per-observation metrics,
observation→three-repetition case→eight-case six-cell aggregation, runtime false-pass/false-block and repair attribution,
usage/latency/failure attribution, and adjudication effects. Every zero-tolerance signal and approved category threshold is
backend-owned and independently inclusive at its exact boundary; no weighted score masks a failed category. Dry runs are
`not_run`; only complete, valid, reviewed, six-cell live evidence with all gates and adjudications resolved can pass;
incomplete/invalid/failed live evidence is `fail`.

**Reports and isolation:** `EvaluationAdjudicationService` validates allowlisted evidence/effects and writes canonical
immutable records. `EvaluationReportService` validates machine-authoritative JSON and deterministic Markdown covering
completeness, cells, metrics, failures, gates, and adjudication. One strict `EvaluationReportAnalysisService` call may add
known-ID-cited interpretation only; unknown citations, invalid responses, or provider failure set analysis to failed and
cannot alter backend certification status. Reports record the shared-chat-deployment caveat truthfully.

**Verification:** Final implementation audit passed after fixing explicit equals-boundary/started/incomplete/invalid tests,
removing a hardcoded observation total, expanding report Markdown/completeness/adjudication coverage, validating malformed
metric inputs, and blinding embedding identities. The complete offline backend suite passed 811 tests (5 skipped). Focused
evaluation/schema tests passed strict examples, forbidden judge authority fields, frozen identity binding, one repair,
facts/refs/adjudication, all threshold boundaries, six-cell aggregation, hard-gate non-compensation, dry/live status,
missing observations, JSON/Markdown schema parity, citations, and analyst failure. Python compilation and `git diff
--check` passed; all provider tests use `FakeLLMClient`, and no MCP/API/frontend/generation feedback path changed.

**Deviations:** The judge rubric is code-composed from one immutable common facet set plus per-type subchecks rather than
stored as separate rubric files. Report-analysis contracts were added in this slice because Slice 1 intentionally staged
only the capture/matcher schemas.

**Follow-up:** Slice 13 adds the explicit operator runner, immutable scheduling/resume, visible calibration and leakage
validation, and truthful freeze-readiness artifacts; no live provider call is authorized by this outcome.
