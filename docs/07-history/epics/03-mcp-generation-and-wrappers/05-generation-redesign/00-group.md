# Group: Generation and Evaluation Redesign

> **Epic 3 redesign.** This group replaces the direct/context generation contracts, semantic pipeline, training
> fixtures, layout engine, public MCP workflow, and offline evaluation framework as one cold-turkey V1 migration.
> The current context-workflow compatibility Slice 12 is a prerequisite and remains tracked in the preceding group.

## Goal

Deliver one strict, reviewed-by-default diagram-generation system for conceptual and repository-grounded requests,
with deterministic validation/repair, independent semantic review, in-process PyGraphviz layout, bounded diagnostics,
and an offline-first certification framework that cannot leak hidden answers into generation.

## User Scenario

A host begins with the same public `diagram_generation_workflow` through either MCP prompt or tool discovery. The
workflow routes a conceptual request to direct generation or a repository-grounded request through evidence/request
preparation and context generation. Both modes produce strict logical candidates, run deterministic and optionally
semantic repair, lay out through one native engine, save only accepted canonical diagrams, and return typed summaries,
actions, trace/debug references, or stage-correct failures. Offline evaluators observe the same production path without
being imported by generation, align final semantics to sealed oracles, judge material quality/factuality, and enforce
absolute reviewed-mode gates.

## Scope

- Namespace-first strict JSON Schemas and Python contract/version constants.
- One neutral immutable generation-observer seam used separately by runtime diagnostics and offline evaluation.
- Shared direct/context request persistence with exact digest concurrency and immutable identity.
- Six mode/type logical candidate contracts and canonical model packets.
- Twelve fixed versioned mode/type training fixtures and ordered set manifests.
- Explicit deterministic and semantic repair loops with bounded budgets and typed failures/actions.
- Reviewed-by-default semantic quality gates, compact result summaries, optional trace, and optional diagnostics.
- PyGraphviz 2.0 in-process layout, parity proof, atomic cutover, and complete old-engine removal.
- One dual-namespace `diagram_generation_workflow` and cold-turkey public MCP/tool/schema cutover.
- Offline evaluation capture, deterministic matcher, Azure embedding seam, blinded judge, metrics, gates, reports,
  safe dry/live runner, visible calibration, and leakage proof.
- One default Azure chat deployment for all chat roles plus explicit evaluation embedding deployment.
- Final full-backend audit/remediation and release-readiness report.

## Out of Scope

- Live Azure generation, embedding, judge, report-analysis, calibration, or certification during implementation.
- Authoring or reviewing hidden certification golds before the generator/evaluator freeze.
- Production promotion before reviewed-mode hidden certification passes.
- Automatic migration or silent reinterpretation of old request/debug/evaluation artifacts.
- Dual runtime, deprecated public aliases, fallback output formats, or fallback layout algorithms after cutover.
- Frontend feature redesign; only minimal public-contract/type/parity follow-through is allowed, coordinated around
  concurrently owned frontend work.
- Multi-provider routing, database persistence, authentication, or remote context storage.

## Architecture Baseline

- Compatibility group Slice 12 first proves one private renderer exposed in MCP prompt/tool namespaces.
- Active product/architecture/design documents describe the final intended system; runtime state remains in this
  group's slice outcomes and the current-state board.
- Generation owns contracts, orchestration, and a neutral observer protocol; it never imports evaluation modules.
- Runtime diagnostics and offline evaluation implement independent observers over immutable bounded events.
- Model-facing calls use strict JSON Schema only; provider incompatibility is a typed failure, never a fallback.
- Deterministic validation precedes semantic review; neither silently mutates semantic meaning.
- PyGraphviz is the sole final layout engine and uses a process-local lock for the complete native object lifecycle.
- Evaluation golds remain outside generator inputs/workspaces, and normal tests use fake LLM/embedding clients.
- `AZURE_OPENAI_DEPLOYMENT` is the single configured chat deployment; evaluation uses
  `AZURE_OPENAI_EVALUATION_EMBEDDING_DEPLOYMENT` for semantic alignment.

## Documentation and Execution Gate

No redesign implementation code begins until:

1. the compatibility plan, research approval package, this group, and all 14 slice plans are audited and committed;
2. all approved final design is promoted into canonical owners, audited, and committed; and
3. the delivery board truthfully distinguishes intended design from pending implementation.

The precommitted plan satisfies each slice's plan gate. If new evidence materially changes a slice, update that slice,
audit the delta, and commit it before implementation. Every implementation then follows failing tests, implementation
audit, focused/full checks, outcome update, and an atomic implementation commit.

## Plan Audit

Four independent read-only passes audited compatibility/S01–S05, S06–S09, S10–S14, and cross-slice consistency against
project rules, current code, research specifications, approval amendments, ownership, rollback, safety, and verification.
The audit found no unresolved design blocker. Corrections made before this commit include:

- explicit honest independent fixture review and pre-deletion inventory proof;
- deterministic repair handoff for schema-valid semantic degradation;
- named legacy prompt/schema removals and untouched old-artifact behavior in the atomic cutover;
- complete old-layout reference inventory and user-local-file protection;
- exact baseline characterization and concurrent-frontend ownership protocol;
- one chat deployment plus explicit embedding deployment throughout;
- final S14 full-backend evidence/remediation/report gate; and
- corrected all-docs-before-code sequencing and previous/next links.

Findings that Phase 0B, compatibility implementation, or the recorded baseline are not yet complete describe intentional
future execution gates, not plan defects. **Plan audit result: Pass.** No implementation may start until this audited
planning package and the separately audited canonical promotion are both committed.

## Promotion Audit

Independent owner-set and cross-document audits verified the promoted product, architecture, MCP, generation,
validation, rendering, fixture, context, evaluation, environment, testing, deployment, and decision contracts against
the approved research and S01–S14 plans. Findings were reconciled for one-owner boundaries, unified names/arguments,
namespace-first IDs, reviewed-default behavior, PyGraphviz-only final design, one chat plus explicit embedding
deployments, offline/live separation, links, JSON examples, and runtime-versus-intended-design truth.

Three readiness rubric JSON files remain byte-identical to current runtime assets until Slice 09 atomically changes their
namespace IDs together with backend consumers; promoting those machine-consumed IDs early was proven to break baseline
readiness tests. Narrative canonical owners already specify the final IDs. **Promotion audit result: Pass.** The focused
current-rubric parity suite and `git diff --check` pass after that sequencing correction.

## Slice Plan

1. [`01-contract-and-observer-foundation.md`](01-contract-and-observer-foundation.md) — strict schema/version registry
   and neutral generation observer. **Complete, audited, and verified.**
2. [`02-request-persistence-foundation.md`](02-request-persistence-foundation.md) — shared direct/context request
   lifecycle, storage, identity, and digest concurrency. **Complete, audited, and verified.**
3. [`03-strict-generation-contracts.md`](03-strict-generation-contracts.md) — six logical schemas, canonical packets,
   strict provider calls, prompt/profile identities, and safety ceilings. **Complete, audited, and verified.**
4. [`04-training-fixtures.md`](04-training-fixtures.md) — twelve fixed mode/type fixtures and six ordered manifests.
   **Complete, audited, and verified.**
5. [`05-pre-layout-repair-pipeline.md`](05-pre-layout-repair-pipeline.md) — deterministic semantic checks and explicit
   bounded direct/context repair before layout. **Complete, audited, and verified.**
6. [`06-semantic-review-and-diagnostics.md`](06-semantic-review-and-diagnostics.md) — reviewed default, composed
   rubrics, semantic repair, typed actions, trace, and debug. **Complete, audited, and verified.**
7. [`07-pygraphviz-parity.md`](07-pygraphviz-parity.md) — PyGraphviz integration, native safety, geometry conversion,
   and cross-engine parity proof. **Complete, audited, and verified.**
8. [`08-pygraphviz-cutover.md`](08-pygraphviz-cutover.md) — atomic sole-engine cutover and old-engine removal after
   parity. **Complete, audited, and verified.**
9. [`09-atomic-public-cutover.md`](09-atomic-public-cutover.md) — unified prompt/tool workflow, request/generation
   tools, schemas, IDs, paths, results, and old-surface removal. **Complete, audited, and verified.**
10. [`10-evaluation-capture-foundation.md`](10-evaluation-capture-foundation.md) — visible cases/oracles, immutable run
    artifacts, semantic projection, and evaluation observer. **Complete, audited, and verified.**
11. [`11-deterministic-matcher.md`](11-deterministic-matcher.md) — cached embeddings, deterministic alignment, and
    hard per-type/topology/field grading. **Complete, audited, and verified.**
12. [`12-evaluation-judge-and-gates.md`](12-evaluation-judge-and-gates.md) — blinded judge, material facts, metrics,
    absolute gates, adjudication, reports, and analysis. **Complete, audited, and verified.**
13. [`13-runner-and-visible-calibration.md`](13-runner-and-visible-calibration.md) — explicit dry/live runner, strict
    resume, visible calibration, freeze readiness, and leakage proof. **Complete, audited, and verified.**
14. [`14-backend-audit-and-release-gate.md`](14-backend-audit-and-release-gate.md) — complete backend audit,
    evidence-backed remediation, full offline verification, and final report. **Complete, audited, and verified.**

Slice numbers are local to this group. Slices 1–13 deliver the redesign; Slice 14 supplies the independent cross-cutting
audit/remediation gate. Every completed slice records completion, deviations, verification, and follow-ups in its
`## Outcome`.

## Dependencies

- Current context group Slice 12 prompt/tool compatibility implementation and exact pre-redesign code baseline `1f14546`.
- Approved research package under `docs/research/generation-redesign/`, including its three approval records.
- Existing generation, context, readiness, canonical storage/rendering, schema registry, fake LLM, diagnostics, and MCP
  seams.
- Existing frontend canonical types/adapters and render parity tests; avoid overlap with the concurrent frontend agent.
- PyGraphviz 2.0 supported wheel/native runtime proof before old layout removal.
- User-approved destructive removal of superseded training directories, prompt/schema files, Grandalf/subprocess layout
  code/dependency, and old MCP registrations/contract IDs only after their replacement gates pass.

## Acceptance Criteria

- Direct and context requests share one strict, versioned, bounded workflow without authority leakage.
- Every model call uses exact schemas, byte/token ceilings, typed provider errors, and bounded explicit repair.
- Reviewed mode is the production/default quality path; standard is explicit diagnostics/ablation only.
- Only accepted semantics are laid out/saved; blockers route typed actions and never force-save.
- Twelve training fixtures are deterministic, signed off, non-leaking, and render correctly.
- PyGraphviz is the only final layout engine and passes native lifecycle, repeatability, concurrency, scale, geometry,
  canvas/SVG, and fixture-gallery proof.
- Prompt and tool namespaces expose byte-identical unified workflow instructions; old public IDs are absent.
- Evaluation remains generation-independent, deterministic where specified, blinded, resumable, bounded, and unable to
  expose gold content to generation.
- Normal tests and the complete backend audit are provider-free; omitted execution mode cannot make a live call.
- All full backend tests, stdio smoke, applicable frontend verification, stale-reference checks, and final audit gates
  pass with no unresolved material finding.
- Live certification, hidden-gold authoring, push, and production promotion remain separate explicit gates.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 3 goal and slice index.
- [`../04-context-backed-generation/12-workflow-client-compatibility.md`](../04-context-backed-generation/12-workflow-client-compatibility.md)
  — prerequisite prompt/tool compatibility proof.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — single live delivery-status board.
- [`../../../../research/generation-redesign/README.md`](../../../../06-research/generation-redesign/README.md) —
  approved research handoff and migration specification.
