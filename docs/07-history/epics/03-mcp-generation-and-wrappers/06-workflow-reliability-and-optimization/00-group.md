# Group: Workflow Reliability and Optimization

> **High-level Epic 3 roadmap.** This package defines the approved goal, block sequence, review model, and handoff
> boundaries for improving the complete user-visible GraphPilot workflow. The blocks are not implementation slices.
> Each block receives its own audited slice plan only after the user and high-level reviewer approve that block's
> direction. Live status remains exclusively in [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md).

## Goal

Make the repository-grounded GraphPilot workflow fast, reliable, explainable, maintainable, and safe from the user's
request through a visible editable diagram or a precise actionable blocked result. Use evidence before changing behavior,
match each correction to the proven root-cause boundary, optimize all worthwhile contributors cumulatively, and promote
only changes that remain stable across representative workflows.

## User Scenario

A user asks an IDE host for a repository-grounded diagram. The host finds relevant source authority, prepares JSON 1 and
JSON 2, and calls GraphPilot through MCP. GraphPilot makes a trustworthy readiness decision, generates and reviews a
strict diagram when context is sufficient, validates provenance, persists and renders the result, returns a recoverable
editor link, and loads the diagram visibly. When context, provider, or execution state prevents generation, the workflow
returns an exact durable outcome without inventing content or repeating provider work.

## Program Model

```text
Shared Success Contract
        ↓
Block 1 — Workflow Audit and Measurement
        ↓
Block 2 — Repository Architecture and Enablement
        ↓
Block 3 — Readiness Diagnosis and Architecture Decision
        ↓
Block 4 — Readiness Correction or Redesign and Proof
        ↓
Block 5 — Complete Live Anchor and Re-Audit
        ↓
Block 6 — Whole-Workflow Optimization
        ↓
Block 7 — Representative Validation and Hardening
        ↓
Block 8 — Promotion and Certification
```

The sequence is evidence-driven rather than strictly one-way. A failed proof returns to the block that owns the failed
assumption. Block 1's audit method is rerunnable after major changes, when previously blocked stages become reachable, or
when measurements become stale. Block 7 may return a representative failure to Block 6 for another measured optimization
wave.

## Block Plan

| Block | Owner document | Completion outcome |
| --- | --- | --- |
| Shared contract | [`01-success-contract.md`](01-success-contract.md) | One stable definition of generated, blocked, failed, interrupted, quality, performance, and evidence success |
| Execution policy | [`11-block-execution-and-parallelism.md`](11-block-execution-and-parallelism.md) | Required slice dependency DAG, safe parallel lanes, ownership/resource isolation, integration gate, and overnight orchestration model for every detailed block plan |
| 1 · Workflow Audit and Measurement | [`02-block-01-workflow-audit-and-measurement.md`](02-block-01-workflow-audit-and-measurement.md) | Versioned complete workflow evidence, ranked gaps, and a reusable audit capability |
| 2 · Repository Architecture and Enablement | [`03-block-02-repository-architecture-and-enablement.md`](03-block-02-repository-architecture-and-enablement.md) | Approved target structure and behavior-preserving enabling refactors with audit parity |
| 3 · Readiness Diagnosis and Architecture Decision | [`04-block-03-readiness-diagnosis-and-architecture.md`](04-block-03-readiness-diagnosis-and-architecture.md) | Proven root-cause boundary and approved correction/redesign with exact proof |
| 4 · Readiness Correction or Redesign and Proof | [`05-block-04-readiness-correction-and-proof.md`](05-block-04-readiness-correction-and-proof.md) | Trustworthy ready/blocked outcomes and durable clean, repair, failure, and interruption evidence |
| 5 · Complete Live Anchor and Re-Audit | [`06-block-05-complete-live-anchor-and-reaudit.md`](06-block-05-complete-live-anchor-and-reaudit.md) | One correct provider-backed request-to-visible-editor success and complete critical path |
| 6 · Whole-Workflow Optimization | [`07-block-06-whole-workflow-optimization.md`](07-block-06-whole-workflow-optimization.md) | Cumulative measured improvements across all worthwhile workflow contributors without quality loss |
| 7 · Representative Validation and Hardening | [`08-block-07-representative-validation-and-hardening.md`](08-block-07-representative-validation-and-hardening.md) | Generalization, stability, and hardened failure evidence for the optimized candidate |
| 8 · Promotion and Certification | [`09-block-08-promotion-and-certification.md`](09-block-08-promotion-and-certification.md) | Explicitly approved defaults, rollback, complete verification, and separately truthful certification state |

Block 1's executable Slice 01–06 plan lives in
[`01-workflow-audit-and-measurement/`](01-workflow-audit-and-measurement/00-group.md). Block 2's audited repository inventory,
target architecture, namespace waves, and parity gate live in
[`02-repository-architecture-and-enablement/`](02-repository-architecture-and-enablement/00-group.md). Block 3's provider-free lifecycle, causal offline/live diagnosis, stale-reference closure, and audited root transition live in [`03-readiness-diagnosis-and-architecture/`](03-readiness-diagnosis-and-architecture/00-group.md). Block 4's focused correction and proof live in [`04-readiness-correction-and-proof/`](04-readiness-correction-and-proof/00-group.md). Block 5's human-approved live anchor and current re-audit live in [`05-complete-live-anchor-and-reaudit/`](05-complete-live-anchor-and-reaudit/00-group.md). Block 6's two-lane measured wave plans live in [`06-whole-workflow-optimization/`](06-whole-workflow-optimization/README.md), which uses the lane work-package model rather than the slice model. Later blocks receive separate numbered slice groups only after their block direction is approved.

## Shared Constraints

- Preserve one mandatory final readiness assessment inside context generation; standalone readiness remains optional
  preview and never licenses generation.
- Preserve complete authority, rubrics, fixed examples, strict structured output, deterministic validation, reviewed
  quality, final review, provenance, digest binding, atomic persistence, PyGraphviz, and editor/SVG parity.
- Keep host/Copilot work, Azure calls, MCP/runtime overhead, local deterministic work, and browser completion separate.
- Never equate Copilot credits with Azure calls, tokens, latency, or cost.
- Never rerun a completed, failed, or uncertain live identity unless a newly audited package explicitly treats it as a
  new experiment and receives a new exact authorization.
- Persist only bounded safe metrics, identities, digests, and validation `{code,path}` evidence; never persist raw provider
  responses, prompts, hidden reasoning, source dumps, secrets, or hidden golds.
- No model output automatically changes code, prompts, schemas, labels, settings, schedules, architecture, or promotion
  state.
- Async or progress mechanisms may improve reliability and transparency but cannot be presented as provider-speed gains.
- Optimize cumulative user-visible time aggressively, but retain causal before/after evidence for each owner or tightly
  related change cluster.

## Review and Ownership Model

The user owns roadmap approval and every live budget. The high-level reviewer owns block sequencing, cross-block
invariants, evidence quality, scope control, and approval recommendations. A block agent owns only the approved block and
its eventual audited slices.

Before a block agent changes code, it must:

1. read `AGENTS.md`, the current-state board, this group, the shared success contract, and its block document;
2. inspect current code and canonical design owners rather than relying on prior summaries;
3. propose a block-specific slice plan, dependency DAG, maximum safe parallel lanes, exclusive file/resource ownership,
   integration gate, budgets, proofs, and rollback according to the execution policy;
4. justify every sequential dependency and reserve shared files/status/docs for the integration owner;
5. obtain high-level/user approval for material design choices;
6. follow the repository's plan-audit → plan-commit → implementation → implementation-audit → verification-commit cadence.

A block agent may not widen another block, alter this roadmap, run an unapproved live gate, promote behavior, or treat a
successful narrow proof as representative stability. Its handoff must state evidence, deviations, unresolved risks, exact
checks, commits, and the recommended next block decision.

## Rerun and Feedback Rules

- First complete Block 1's reusable audit capability and fresh provider-free baseline before Block 2 begins.
- Re-run Block 1 after Block 2 for behavior/performance parity, after Block 5 when all live stages are reachable, during
  Block 6 after material optimization waves, and whenever measurements become stale.
- If Block 4 fails, return to Block 3 with the smallest failed assumption.
- If Block 5 fails in a downstream stage, diagnose and correct that stage before claiming an end-to-end baseline.
- If a Block 6 change fails its anchor or quality gates, revert or revise that change before the next optimization.
- If Block 7 exposes a representative issue, return it to Block 6 and rerun the anchor plus affected representative cases.
- If Block 8 fails a promotion gate, return to the block that owns the failed behavior; never weaken the gate.

## Roadmap Audit

Result: **Pass.** Independent read-only review found no critical, high, or medium defect. It verified one coherent
request-to-editor goal, the shared success contract, all eight blocks in dependency order, S13–S15 as initial evidence rather
than permanent architecture, rerunnable audits with new identities, behavior-preserving/bounded repository enablement,
separate readiness diagnosis and correction, one live anchor before optimization, causal cumulative optimization with a
guard set, representative feedback to optimization, promotion/certification separation, agent handoffs and review authority,
security/live-budget/no-rerun invariants, canonical design ownership, current-state-only live status, links/navigation, and
block-versus-slice terminology. A later high-level sequencing clarification assigns delivery of the reusable audit and fresh
baseline to Block 1 before Block 2 consumes it for refactor parity; this narrows ownership without changing the approved
block order, goal, or gates. No block implementation or live budget is approved by this audit.

## Scope

- User-visible context workflow reliability, performance, quality, maintainability, recovery, and promotion.
- Rerunnable end-to-end measurement and a versioned cumulative optimization ledger.
- Repository structure and behavior-preserving refactoring needed to support the workflow program.
- Readiness diagnosis and correction/redesign before downstream provider testing.
- One complete live anchor, aggressive iterative optimization, representative validation, and explicit promotion.

## Out of Scope

- Treating the blocks as preapproved implementation slices.
- Locking detailed file moves, readiness cases, schemas, prompts, budgets, or optimization changes in this roadmap.
- Replacing Epic 4's edit workflow, Epic 5 RAG scope, or formal readiness/generation certification owners.
- Unbounded cosmetic reorganization, speculative abstractions, or deleting files without reference and compatibility proof.
- Large live matrices before the owning narrow gate and exact budget are approved.

## Acceptance Criteria

- Every block has one clear question, boundary, output, exit gate, and feedback path.
- Every detailed block plan includes an audited slice DAG that maximizes safe parallelism, declares exclusive ownership and
  resource isolation, justifies sequential dependencies, and reserves an integration gate/owner.
- The shared success contract applies consistently to every slice and report.
- Block 1 becomes a reusable workflow audit rather than an S15-specific experiment.
- Block 2 improves maintainability without behavior drift and proves parity by rerunning the audit.
- Blocks 3–4 diagnose readiness before selecting and proving any correction or redesign.
- Block 5 produces the first complete provider-backed request-to-visible-editor evidence.
- Block 6 records before/after and cumulative benefits for every retained optimization.
- Block 7 validates the optimized candidate broadly enough to detect overfitting and instability.
- Block 8 keeps proposal, implementation, verification, promotion, and certification states distinct.
- Block agents can start from this package without treating historical summaries as current source authority.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 3 scope and group navigation.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — sole live-status and next-work owner.
- [`../04-context-backed-generation/13-context-performance-and-recovery.md`](../04-context-backed-generation/13-context-performance-and-recovery.md) — initial workflow efficiency/recovery evidence.
- [`../04-context-backed-generation/14-readiness-effort-evaluation.md`](../04-context-backed-generation/14-readiness-effort-evaluation.md) — provider/readiness observability evidence.
- [`../04-context-backed-generation/15-full-effort-evaluation.md`](../04-context-backed-generation/15-full-effort-evaluation.md) — complete offline audit and stopped live screening outcome.
- [`../../../../02-design-and-features/08-context-backed-generation/README.md`](../../../../03-design/01-context-generation/README.md) — intended context workflow behavior.
- [`../../../../01-architecture/01-backend-architecture.md`](../../../../02-architecture/03-backend.md) — canonical service ownership and dependency boundaries.
