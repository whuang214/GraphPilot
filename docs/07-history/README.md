# History

**Read-only.** Completed delivery work, retired designs, and legacy archive. Nothing
here describes the current system — for that, start at [`../README.md`](../README.md).

Documents here are frozen. They record what was true when written and are not updated
when the system changes. Do not link to them from active documentation except to cite
a decision's origin.

## Contents

| Area | What |
| --- | --- |
| `epics/` | Every completed epic and block, including all of Epic 3 Block 6 |
| `completed-draft-first-generation.md` | The program that replaced the provider pipeline with host-authored drafts. Completed 2026-08-03 |
| `retired-context-generation/` | JSON 1, JSON 2, the four-layer readiness reviewer, the three per-type rubrics, and provenance. Retired 2026-08-02 with the provider-backed pipeline |
| `retired-workflow-audit-evaluation.md` | The workflow-audit evaluation rig and the `W01`–`W22` boundary taxonomy, retired with the pipeline it measured |
| `retired-evaluation-and-doe-design.md` | The earlier DOE evaluation subsystem, retired 2026-07-30 |
| `retired-answer-key-generation.md` | Offline answer-key scoring design |
| `retired-workflow-optimization.md` | The two-lane program that measured and tuned the provider pipeline |
| `retired-delivery-readme.md` | The former delivery-tree index |
| `archive/` | Pre-existing legacy archive |
| `internal/` | Untracked internal working material |

## Why the generation package was retired

GraphPilot generated diagrams by sending host-authored claims to a model, gating them
behind a paid readiness reviewer, and repairing the model's notation mistakes. Across
thirteen measured runs that path produced **no diagram** on a repository we controlled:
it failed at readiness, at the size gate, at provider availability, and at deterministic
SysML validation, in that order.

The replacement inverts it. The host — already an LLM with repository access — authors
the diagram's semantics directly, and the backend materializes them deterministically
with no provider call. See `../03-design/01-generation/`.

## Path-frozen evidence

`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/06-whole-workflow-optimization/authorization/`
must keep its exact path. Five frozen live-run manifests bind those paths and digests;
moving the folder invalidates provider-paid evidence that cost 19 Azure calls and
cannot be regenerated.