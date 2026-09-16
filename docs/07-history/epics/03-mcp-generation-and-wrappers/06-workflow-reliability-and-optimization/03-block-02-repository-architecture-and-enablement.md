# Block 2: Repository Architecture and Enablement

## Goal

Make the repository easier and safer to change before new readiness behavior is designed, while preserving current public
contracts, workflow decisions, outputs, quality, and provider-free performance.

## Why This Block Exists

S13–S15 added valuable measurement and experiment support but exposed large, overlapping, and experiment-coupled modules.
Block 1 then delivers a reusable audit capability and fresh provider-free parity baseline. The evaluation area still mixes
reusable capture/report infrastructure, generation quality/certification, workflow performance, readiness experiments, and
S15-specific H/M artifacts; similar provider-call, validation-event, checkpoint, failure, and report logic appears in more
than one path.

Block 2 consumes the approved Block 1 audit rather than inventing it while restructuring the repository. This block is an
enabling refactor, not the readiness fix or workflow optimization block.

## Question This Block Owns

What repository structure and service boundaries let future block agents change, test, audit, and roll back the workflow
safely without preserving unnecessary files, creating speculative abstractions, or changing behavior accidentally?

## Repository Audit

Audit the full repository—not only `services/`—and classify every relevant file/module as:

- keep;
- rename;
- move;
- split;
- combine;
- delete;
- defer.

Each disposition requires current consumers, responsibility, change lifecycle, dynamic loading/entry points, test/docs
ownership, compatibility impact, and migration/rollback evidence. File count or size alone is not a decision.

## Evaluation-Specific Review

Classify evaluation assets into at least these responsibility classes:

1. reusable capture/artifact/checkpoint/metrics infrastructure;
2. reusable Block 1 workflow-performance auditing;
3. readiness diagnosis/proof support;
4. generation quality and certification;
5. experiment-specific historical packages such as S15 full effort;
6. proven redundant, superseded, or dead code.

Block 1's delivered audit must remain independently runnable without S15's H/M case identities, schedule, or decision
algorithm throughout the refactor. Block 2 may relocate, split, combine, or simplify its internals only through approved
waves that preserve the audit's scenario/result contract and fresh parity baseline. Historical reproducibility is a consumer,
but it does not make every S15 file active common architecture.

## Refactor Waves

After a target structure is reviewed and approved, execute bounded behavior-preserving waves. Likely concerns include:

- shared safe provider-call, validation-event, checkpoint, terminal-observation, and bounded report responsibilities;
- workflow audit separation from experiment-specific cases/decisions;
- readiness evaluation separation from generation certification;
- oversized orchestration modules with multiple reasons to change;
- management command, schema, fixture, test, and documentation organization;
- proven dead or superseded file removal.

The audit chooses actual waves. This document does not preapprove a package tree, broad move, merge, split, or deletion.

## Implementation Slice Plan

The executable audited inventory, target architecture, path migrations, ownership DAG, bounded refactor waves, and parity
handoff live in [`02-repository-architecture-and-enablement/00-group.md`](02-repository-architecture-and-enablement/00-group.md).
This block owner retains the question and exit gate; the nested group owns implementation sequencing and Outcomes.

## Behavior-Parity Gate

Every wave must preserve:

- public MCP/REST/management behavior unless explicitly characterized as internal-only;
- request/context/diagram schemas and serialized outputs;
- provider call order, roles, budgets, and no-rerun rules;
- readiness/generation/review decisions;
- canonical JSON/SVG/editor behavior;
- security, authority, quality, provenance, persistence, and recovery;
- focused/full tests and documentation links.

After the complete block, rerun the provider-free Block 1 audit and compare exact outputs plus cold/warm timing. Any material
behavior or performance drift returns to the owning wave before readiness diagnosis begins.

## Outputs

- Current responsibility/dependency and dynamic-entry-point map.
- Approved target architecture and migration order.
- Keep/move/split/combine/delete/defer inventory with evidence.
- Behavior-preserving implementation slices and commits.
- Updated architecture/service/test/documentation owners.
- Before/after Block 1 parity report against the exact fresh baseline and remaining deferred maintenance list.

## Exit Gate

Block 2 completes when required enabling refactors are implemented and audited, Block 1 parity passes, active behavior is
unchanged, future readiness/audit work has clear reusable seams, and remaining cleanup is cosmetic, speculative, or safely
deferred.

## Not Owned Here

- Readiness prompt/schema/policy/effort or workflow behavior changes.
- Provider-backed experiments.
- Performance optimizations presented as refactors.
- Removing historical/reproducibility assets without current-consumer and migration proof.
- Reorganizing every folder merely for consistency.

## Block-Agent Handoff

The block agent first returns an audit and target design for high-level/user review. Implementation begins only after that
approval. Its final handoff includes the exact inventory, moved/removed references, parity evidence, deferred work, checks,
commits, and the readiness-diagnosis starting seams.
