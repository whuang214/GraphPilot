# Authorization (Legacy)

**Legacy storage. Closed to new entries. Scheduled for removal.**

These folders hold frozen live-run approvals from Block 6's completed waves. They
remain at these exact paths, byte-identical, for one reason only: frozen `g2` and
`s1` package manifests bind these paths and digests, and moving or editing a file
here would invalidate machine evidence that must stay verifiable.

This is compatibility storage, not active architecture.

## Rules

- **Do not add a folder or file here.** Not for a new wave, not for a new lane, not
  for a new candidate.
- **Do not edit, reformat, or re-serialize any file here.** Their bytes are bound by
  digest.
- **Do not delete anything here** while any evidence still references it.

## Contents

| Folder | Wave | Outcome |
| --- | --- | --- |
| `semantic-review-wave-01/` | S03 semantic review proof | Reverted |
| `generation-endpoint-wave-01/` | S07 generation endpoint proof | Retained — candidate `g2` |
| `generation-endpoint-wave-02/` | S07 continuation | Retained |
| `semantic-review-retry-wave-02/` | S11 semantic review retry proof | Reverted — candidate `s1` failed |

Each folder holds `anchor.json`, `approval.json`, and `approval.schema.json`.

## Future live runs

A future live run still requires a new explicit user authorization — see root gate
G3 in the [root plan](../plan.md). That authorization does **not** go here. Before
any new live work is authorized, a separately audited rules amendment must define a
parent-owned, immutable location for lane run records. Until that location exists,
no live run may be authorized.

## Removal

This folder is scheduled for removal during the broader repository cleanup, once the
frozen manifests that bind these paths are themselves retired or re-anchored. Track
the path bindings in
[`../history/relocation-map.json`](../history/relocation-map.json).
