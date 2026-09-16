# Draft-First Generation — completed

**Frozen 2026-08-03.** Eight packages, `P0`–`P7`, nine commits. GraphPilot stopped calling
a model to draw diagrams: the host authors the semantics as a draft and the backend
materializes them deterministically.

Live design: [`../03-design/01-generation/`](../03-design/01-generation/README.md).
Follow-on quality work: `docs/05-delivery/07-generation-quality/plan.md`.

## Why

The provider-backed pipeline produced **no diagram in thirteen measured runs** against a
repository we controlled. It failed at readiness, at the size gate, at provider
availability, and at deterministic SysML validation. The cause was structural: the host
established the semantics, then a second model re-derived them from claims and got the
notation wrong. Optimizing the stages could not fix that. Findings:
[`retired-workflow-optimization.md`](retired-workflow-optimization.md).

```text
before   host claims → readiness LLM → generation LLM → repair LLM → validate → diagram
after    host draft  → validate → materialize → layout → validate → diagram
```

Provider calls per diagram: **3–5 → 0**.

## What shipped

| # | Package | Result |
| --- | --- | --- |
| P0 | Demolition | 85,115 deletions; readiness, generation, repair, semantic review, JSON 1/2, the Azure client and the workflow-audit rig removed with their assets, tests, and docs |
| P1 | Design | `03-design/01-generation/` (draft, materialization, lifecycle) + `05-edit.md`; `03-design` restructured, 217 links repaired |
| P2 | Draft contract | `graphpilot.draft.v1`, validator, evidence/freshness, secret and size bounds |
| P3 | Materializer | Draft → canonical; provenance moved from claims to evidence in schema **and** `diagram.ts` |
| P4 | `diagram_create` | The whole path in one call |
| P5 | Host surface | `diagram_workflow`, `diagram_get_authoring_contract`, per-type `authoring.md` |
| P6 | Activity + use case | No materializer change needed; twelve tests passed first run |
| P7 | Outside-in validation | First-attempt success on a real repo; found the composition double-diamond |

Tests: **1046 → 385 → 495** backend, **420** frontend + 43 e2e. MCP surface **14 → 9**.

## Decisions worth carrying forward

**The ownership boundary.** If getting something wrong is a *judgement* error the host
owns it; if it is a *notation* error GraphPilot owns it. A host states
`composition, source, target, sourceRole`; it never authors a relationship-end object, a
marker, or a position. That is what makes a whole class of malformed-notation failure
impossible rather than merely detected.

**Authority is a field, not a pipeline.** `as_implemented` and `conceptual` are values on
one draft, not two code paths.

**The diagram carries its own evidence.** `metadata.evidence` inline, so a diagram can be
validated, re-rendered, freshness-checked, and projected back into draft shape with
nothing but itself. No manifest to bind, no second document to go stale.

**Freshness is per cited region.** A change outside the cited lines, in another file, or
to line endings alone is not stale. The retired model fingerprinted the repository and
staled on any edit.

**Draft IDs reach the canonical document unchanged.** Nodes and edges alike. That is what
lets Epic 4 editing match on identity instead of guessing from labels, and it had to hold
from the first diagram ever created.

**Refuse, never repair.** An off-vocabulary type, a forbidden relationship end, an
unsupported containment — all rejected with the permitted set named, never coerced.
Silent coercion hides a modelling mistake behind a diagram that looks fine.

**Every reason at once.** Findings return complete and sorted by path. The retired surface
cost five and four attempts per document by revealing mistakes one round at a time.

**Determinism deleted the apparatus.** Because the pipeline is free and repeatable, the
authorization gates, cost ceilings, sealed evidence, resume/checkpoint and leakage
controls that surrounded the old rig had nothing left to protect.

## Corrections made during the program

**Composition drew two diamonds.** The materializer set `aggregation: "composite"` on the
source end, but `composition` already carries `target_marker="diamond_filled"` in the
element catalog — `aggregation` is how a plain *association* expresses composition. The
rule traced back to `composition_part_end_missing`, a validator deleted in P0: a dead
constraint carried into the new design. **Every payload-level test passed while the
picture was wrong.**

**A block cannot contain a block.** Only `subject`, `package`, and the activity regions
are containers. `conform_logical` was dropping a non-container `parentId` in silence.

**The frontend baseline was stale.** Four test files globbed `backend/graphpilot/`, a path
that stopped existing at `0126efd`. The reported 419-passing suite had been partly
inert.

## What was not finished

- **P7.3 held-out validation never happened.** One outside-in run, one repo (GraphPilot
  itself), one diagram type. A second repo and a held-out type were not tested.
- **The outside-in run was not independent.** The same agent wrote the authoring contract
  and then the draft against it, so first-attempt success is flattered.
- **P8 (assurance display in the editor) did not ship.** It moved to the follow-on
  program, deliberately placed after presentation quality: a correct diagram that reads as
  the wrong graph is a worse problem than a missing badge.
- **Presentation quality was found wanting and left alone.** 21 of 36 committed examples
  draw markers on top of one another; use-case diagrams sprawl horizontally. Pre-existing,
  not caused by this program, and the reason the follow-on program exists.
