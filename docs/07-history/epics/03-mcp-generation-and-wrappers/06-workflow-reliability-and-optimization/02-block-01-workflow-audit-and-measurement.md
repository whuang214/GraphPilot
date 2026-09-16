# Block 1: Workflow Audit and Measurement

## Goal

Deliver and maintain a rerunnable, versioned audit capability for the complete user-visible workflow so every diagnosis,
refactor, optimization, and promotion begins from current evidence rather than historical assumptions.

## Existing Foundation

Context S13–S15 form the initial Block 1 pass:

- S13 removed duplicated standalone readiness, added provider telemetry, and made lost-response recovery non-duplicating.
- S14 added reasoning/cache/provider identity and safe readiness validation diagnostics, then recorded one directional medium
  proof.
- S15 mapped 22 workflow boundaries, measured provider-free cold/warm paths through editor completion, built a full H/M
  package, and recorded a stopped Stage B that exposed readiness/evidence-durability gaps.

Those slices are historical evidence, not the permanent audit implementation. They establish enough initial coverage to
design Block 1, but they do not complete the block's reusable capability or fresh baseline. The stopped S15 manifest and
observation identities are never rerun or treated as an incomplete budget to consume later.

## Question This Block Owns

Where does the current workflow spend user-visible time, lose reliability or quality, repeat work, hide uncertainty, or lack
evidence—from the user request through a visible diagram or actionable blocked/failure result?

## Audit Boundary

The audit covers:

1. host routing and authority branch selection;
2. source discovery, reads, and host context growth;
3. JSON 1 construction, validation, fingerprinting, reconciliation, and persistence;
4. JSON 2 framing, validation, digest binding, reconciliation, and persistence;
5. MCP startup, discovery, transport, dispatch, serialization, timeout, and recovery;
6. final readiness preparation, provider calls, validation, repair, policy, and result;
7. generation packet/examples, strict generation, deterministic validation/repair;
8. semantic review, response/candidate repair, and mandatory final review;
9. layout, assembly, provenance/context stability, persistence, and rendering;
10. editor-link return, API load, browser errors, and visible diagram completion.

## Reusable Capability Deliverable

Block 1 must implement and verify an audit that accepts approved scenarios independently of S15's H/M package and produces:

- exact cold/warm and artifact/process-cache state;
- non-overlapping host/Azure/MCP/local/browser accounting;
- nested role/stage details, bytes, calls, tokens, credits, repairs, cache, and quality;
- timeout/recovery and no-rerun evidence;
- quality failures by case;
- ranked bottlenecks with owner confidence, smallest fix, alternative, trade-off, expected benefit, offline/live proof, and
  disposition;
- a bounded versioned report and cumulative baseline ledger;
- one documented provider-free command/package another agent can rerun without S15-specific identities or live authorization;
- explicit adapters for future host and provider-backed evidence without treating unavailable evidence as zero.

## Initial Fresh Baseline

After the reusable capability passes offline/fake, failure, recovery, security, and browser-safe checks, run it against the
current provider-free workflow to create the fresh pre-Block2 baseline. Record exact commit/assets/scenarios, outputs,
cold/warm measurements, quality, and coverage gaps. This baseline is the parity authority for Block 2; historical S13–S15
numbers remain prior evidence rather than the comparison target when versions differ.

## Implementation Slice Plan

The executable provider-free plan is owned by
[`01-workflow-audit-and-measurement/00-group.md`](01-workflow-audit-and-measurement/00-group.md): contracts/scenarios,
capture/adapters, runner/recovery, browser completion, reports/ledger, then the fresh baseline. This block document remains the
high-level authority and the nested group links here rather than redefining the exit gate.

## Rerun Triggers

Re-run this block's audit method:

- immediately after the reusable capability is delivered to create the fresh pre-Block2 baseline;
- after Block 2 to prove refactor parity and detect structural performance regressions;
- after Block 4 when readiness is trustworthy;
- as part of Block 5 when every live stage becomes reachable;
- after material Block 6 optimization waves;
- when provider/model/configuration, prompts/schemas/rubrics/examples, architecture, host behavior, or editor behavior changes;
- when representative validation shows the anchor baseline is no longer sufficient.

A rerun uses new run/case/observation identities and exact current asset versions. It never reuses a stopped/completed live
identity or presents incomparable versions as one before/after pair.

## Outputs

- Versioned evidence ledger with explicit coverage/confidence.
- Complete critical-path report where a complete denominator exists.
- Ranked material gaps and unknowns.
- Rerunnable audit command/package and documented scenario interface.
- Fresh provider-free baseline identity for Block 2 parity.
- Recommendation to remain in this block, move to an owning focused block, or rerun after a prerequisite.

## Exit Gate

The current Block 1 is complete only when the reusable audit capability and scenario interface are implemented/audited,
provider-free/failure/recovery/browser-safe gates pass, a fresh current baseline is recorded, and all material workflow
boundaries are measured, derived, simulated, imported, not reached/applicable, or explicitly `not_measured` with source,
confidence, and reason. Every slow/failing stage has an attributed owner or a
smallest diagnostic proof; accounting is non-overlapping; quality/security invariants hold; and Block 2 receives an exact
parity baseline.

S13–S15 remain the initial discovery pass and readiness handoff evidence, but they do not by themselves satisfy this exit
gate.

## Not Owned Here

- Implementing the recommended behavioral fix.
- Broad repository restructuring beyond the minimal audit-specific work needed to deliver this reusable capability.
- Promoting effort, prompts, schemas, caching, host tools, or architecture.
- Formal readiness/generation certification.
- Treating fake-provider timing as live provider performance.

## Block-Agent Handoff

A Block 1 agent returns exact sources, versions, commands, artifacts, confidence limits, ranked findings, and the proposed
next owner. It may add measurement instrumentation only through an audited slice that proves observational equivalence.
