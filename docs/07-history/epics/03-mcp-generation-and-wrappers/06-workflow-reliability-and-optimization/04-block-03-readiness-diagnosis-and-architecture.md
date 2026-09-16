# Block 3: Readiness Diagnosis and Architecture Decision

## Goal

Determine why live readiness is slow or unreliable, identify the narrowest complete root-cause boundary, and approve the
right correction level before any readiness behavior is changed.

## Why It Follows Block 2

The stopped S15 screening proved that readiness entered repair under both high and medium but did not preserve enough
provider/validation detail to attribute the defect. Block 2 must first provide clear, durable evaluation/checkpoint seams so
this diagnosis does not create another experiment-specific runner or lose call evidence again.

## Question This Block Owns

Is the readiness problem a local defect, a readiness-component or responsibility-design problem, a provider/control issue, or still insufficiently evidenced?

## Diagnosis Levels

### Local defect

Examples include an incorrect strict-schema projection, ambiguous prompt instruction, mechanical validator mismatch, missing
repair constraint, or failure to persist safe diagnostics.

### Readiness component design problem

Examples include an overloaded response contract, duplicated model/backend responsibility, full-input repair for a targeted
defect, unstable input packaging, or several independently failing responsibilities in one call/result.

### Readiness responsibility design problem

Examples include readiness owning decisions that belong in host preparation, an ineffective improve-before-ask loop, overlapping readiness/generation authority, or synchronous behavior that cannot provide a reliable user outcome. Evidence outside the readiness boundary remains `additional_evidence` until a separately audited plan owns it.

### Provider/control problem

Examples include provider availability, strict-output support, service-tier behavior, reasoning effort, caching, or context
limits rather than GraphPilot semantics.

## Evidence Requirements

Use minimal, newly identified diagnostic packages that each discriminate one active hypothesis. Human labels are not a
mechanical execution prerequisite. Every package must preserve safe provider call records and validation events through clean,
repaired, failed, and interrupted paths without rerunning identities. Diagnosis records:

- exact context/request and readiness input identity/bytes;
- provider role/state/duration/bytes/tokens/IDs/service tier/controls where known;
- exact safe response-validation `{code,path}` events;
- repair trigger, input identity, call state, validation, and final outcome;
- deterministic policy/status/finding/ref/action comparison only when an independent semantic authority exists; otherwise the claim stays mechanical/provider/performance-only;
- uncertain provider state as uncertain rather than reconstructed;
- no downstream generation/review Azure call.

Every live execution uses a new exact manifest with its own hypothesis, schedule, identities, budget, rollback, and independent pre-dispatch audit under the authorized cumulative envelope. This block may finish with an architecture decision from offline/current evidence, or require the next minimal diagnostic live discriminator when the root cause cannot be established otherwise.

## Architecture Decision

The block concludes with exactly one recommendation:

- focused implementation correction;
- readiness component redesign;
- provider/control response;
- additional evidence because no root cause is yet supported.

The decision record includes the strongest alternative, decisive trade-off, affected consumers/contracts, compatibility/security impact, migration/rollback, smallest offline proof, required live proof, and explicit non-goals. A broad redesign is correct
when it is the narrowest adequate response to a structural root cause; a small patch is not preferred merely because it is
easy.

## Implementation Slice Plan

The executable evidence audit, provider-free lifecycle, sequential diagnostic packages, causal thresholds, and root-decision
handoff live in [`03-readiness-diagnosis-and-architecture/00-group.md`](03-readiness-diagnosis-and-architecture/00-group.md).
This block owner retains the diagnosis question and exit gate; the nested group owns sequencing and Outcomes. Historical S01–S04 commits remain evidence, but their obsolete review gate is superseded.

## Outputs

- Reproducible diagnosis and evidence ledger.
- Root owner and confidence.
- Approved readiness correction/redesign specification.
- Block 4 implementation and proof boundary.
- Explicit decisions about what remains unchanged.

## Exit Gate

Block 3 completes only when evidence explains the observed failure, nearby successful/failed conditions, and why the selected
design removes the root cause. If evidence is inconclusive, remain in Block 3 rather than guessing or implementing several
competing changes.

## Not Owned Here

- Implementing or promoting the selected correction/redesign.
- H/M or provider-control promotion from an insufficient diagnostic case.
- Full generation/review testing.
- Broad representative readiness certification.

## Block-Agent Handoff

When one root threshold passes, the diagnosis agent records the complete Captain Progress Report and obtains an independent
exit audit. A clean exit automatically starts Block 4 planning under the correction boundary already authorized by this program;
implementation still requires an audited Block 4 plan. The handoff defines exact slices, proofs, live gates, rollback, and risks.
