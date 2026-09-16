# Block 6 History

**Read-only.** Completed and superseded Block 6 delivery documents, kept for
provenance. Nothing here is an active plan, and nothing here should be edited except
to repair a link.

Active ownership lives in the [root plan](../plan.md),
[Lane A](../lane-a/README.md), and [Lane B](../lane-b/README.md). Where a document
here disagrees with canonical design in
[`docs/02-design-and-features/`](../../../../../../, the
design document wins.

## Contents

| Path | What it is |
| --- | --- |
| [`lane-a/`](lane-a/) | The retired Lane A slice documents (A01–A09 as originally planned) and the Lane A host workflow design. A05–A09 were retired by host observation `r1` and were never executed as written. |
| [`lane-b/`](lane-b/) | The B0 path-safety document and Lane B slice documents S01–S12 across the three waves. |
| [`shared/`](shared/) | Cross-lane documents: the original slice-group plan and the one-time lane integration record. |
| [`relocation-map.json`](relocation-map.json) | Machine-readable old-to-new path map for this reorganization. |

## Reading the old paths

These documents were written when every Block 6 document sat flat at the group root.
Their Markdown links are updated to resolve from their new locations, but paths
quoted inside body prose, and paths embedded in frozen machine evidence and in
`authorization/` manifests, are **historical**. Resolve those through
[`relocation-map.json`](relocation-map.json) rather than assuming they still exist.

Frozen machine evidence was moved as whole directories with its content unchanged,
so its self-digests still verify.

## Status accuracy

[`shared/00-group.md`](shared/00-group.md) had a stale Slice Plans table when it was
archived: shared status files had been reserved for the integration owner, so no
lane commit ever updated it. Its table was corrected to the real outcome and a
`Final status` section was appended before archiving. The rest of its prose is
original.
