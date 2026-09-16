# Workflow Optimization — retired

**Closed 2026-08-02**, superseded by the draft-first generation redesign. Two lanes ran
in parallel against one goal: make the provider-backed diagram workflow cheaper. Lane A
owned the host and authoring surface and measured in *authoring attempts*; Lane B owned
backend generation logic and measured in *milliseconds*, then provider calls.

The program's findings stand. Its subject does not: the pipeline it optimized was removed
wholesale. See [`../03-design/01-generation/`](../03-design/01-generation/README.md).

## Slices

| # | Slice | Outcome |
| --- | --- | --- |
| A01 | Commission `host-01`, a clean-room observation of the authoring surface | **5 and 4 attempts** to author JSON 1 and JSON 2, against a bar of 2. The cost was real |
| A02 | `diagram_generation_get_contract` — an authoring-contract lookup tool | **1 attempt per document, 0 rejections.** Reproduced by three later independent hosts |
| B01 | Re-measure per-request cost on the restructured tree | Dissolved two prior tiers; found metaschema re-validation at ~47% of per-request local wall |
| B02 | Cache metaschema validation across all 11 call sites | Per-request local wall **815 → 384 ms** |
| B03 | Unify the two evaluation commands | One command; live mode proven against Azure; retired rig deleted, −7,001 lines |
| B04 | Measure the live workflow and cut its cost | Semantic review defaulted off: **−56% Azure time, −48% calls** |

## What it established

**Local compute was never the problem.** After B02, local work was **0.14%** of a
generation. Every remaining cost was a provider round trip:

```text
readiness      48–100 s
generation       ~105 s
repair            ~51 s
```

**The authoring surface was fixable and was fixed.** A02 took host authoring from 5-and-4
attempts to 1-and-1, and that result reproduced across independent clean-room hosts on
the same fixture. Publishing the contract — examples, enums, ID patterns, backend-derived
fields — was what did it.

**The pipeline still never produced a diagram.** Thirteen measured runs against a
repository we controlled ended at readiness, the size gate, provider unavailability, or
deterministic SysML validation. Optimizing the stages could not fix an architecture that
asked a second model to re-derive semantics the host had already established, then
repair its notation.

That conclusion is what closed the program and opened the redesign.

## Retired identities

Slice numbers `A01`, `A02`, `B01`–`B04` are permanent and are never reused. The
`host-NN` clean-room observations and `baseline-NN` provider-free audit runs retired with
the workflow-audit rig; the `W01`–`W22` boundary taxonomy retired with it, documented in
[`retired-workflow-audit-evaluation.md`](retired-workflow-audit-evaluation.md).
