# Slice 02: Layout Subsystem

## Purpose

Turn a logical diagram (nodes + edges, no coordinates) into a positioned, sized diagram, so generated diagrams get a clean layout the renderer and editor can use. Design: `docs/02-design-and-features/04-generation-design.md` (Layout).

## Included Work

- define a `LayoutEngine` interface: takes a logical graph + per-type node sizes, returns positions
- implement the **Graphviz** engine (primary): per-type direction (top-to-bottom for activity, etc.) and containment via clusters; binary resolved as `GRAPHVIZ_DOT_PATH` → `backend/.graphviz/` → system `PATH`
- implement the **`grandalf`** pure-Python fallback (used when Graphviz is absent) so layout never hard-blocks
- per-type default node sizes (widened for long labels)
- add the `grandalf` dependency; document Graphviz install (portable in `backend/.graphviz/`, gitignored; no-admin options)
- tests: lay out the answer keys with the fallback (offline, no binary); basic position/size/no-overlap checks; engine selection prefers Graphviz when present

## Not In Scope

- calling the LLM / assembling the prompt (Slice 03)
- the rendering itself (Slice 01)
- the Graphviz-vs-`grandalf` quality DOE (catalogued; run at epic end)

## Target Areas

- backend layout module + tests
- `requirements.txt`, settings (`GRAPHVIZ_DOT_PATH`), `.gitignore` (`backend/.graphviz/`, done)
- dev-environment doc (Graphviz install)

## Exit Criteria

- a logical graph lays out into positioned/sized nodes; containment is respected
- Graphviz is used when available, `grandalf` otherwise; a missing binary never hard-blocks
- the answer keys lay out offline via the fallback in tests
- `python manage.py test` passes

## Previous Slice

- `01-render-service-and-tool.md`

## Next Slice

- `../02-generation/03-generation-core.md`

## Outcome

> Historical outcome: this records the original dual-engine delivery. Redesign Slice 08 replaced it atomically with the
> sole pinned `PyGraphvizLayoutEngine`; current behavior is owned by the active generation design and backend architecture.

✅ Completed.

**Delivered.** `backend/services/generation/pipeline/diagram_layout_service.py` — a `LayoutEngine` interface with two interchangeable engines, plus a `DiagramLayoutService` orchestrator that turns a logical diagram (nodes + edges, no coordinates) into positioned, sized nodes.

- **`GraphvizLayoutEngine` (primary):** shells out to the Graphviz `dot` binary with `-Tplain` and parses the result (center coords in inches, origin bottom-left) into top-left pixel positions. Binary resolved `GRAPHVIZ_DOT_PATH` → `backend/.graphviz/bin/dot[.exe]` → system `PATH` (`resolve_dot_path`). Per-type `rankdir` (activity/BDD `TB`, use-case `LR`).
- **`GrandalfLayoutEngine` (fallback):** pure-Python Sugiyama layout, used when no `dot` is found so layout never hard-blocks. Lays out each connected component and packs components left-to-right; swaps axes for `LR`.
- **`DiagramLayoutService`:** selects Graphviz when available else grandalf (overridable for tests); assigns per-type, **label-widened** default sizes (`node_size`); handles **`parentId` containment** by laying out each container's children inside it and sizing the container to enclose them (children keep parent-relative positions per the canonical schema).
- **Config:** `GRAPHVIZ_DOT_PATH` added to settings + `.env.example`; `grandalf==0.8` pinned in `requirements.txt`; dev-environment doc gains a "Graphviz (optional)" install section.

**Verification.** `python manage.py test` → 192 OK (+19 layout tests). The 12 answer keys lay out **offline via the grandalf fallback** (no binary); checks cover sizing, top-level non-overlap, per-type direction, containment enclosure, engine selection (stubbed availability), and Graphviz `-Tplain` parsing (captured sample, no binary). The Graphviz engine was also confirmed live against the vendored `backend/.graphviz/` build.

**Deviations.** Graphviz is driven via **subprocess `dot -Tplain`**, not `pygraphviz`/`pydot` C bindings — those need native build tooling that is painful on Windows; the subprocess approach needs only the binary. Containment is handled one level deep (the MVP system-boundary case) via nested layout. The Graphviz-vs-grandalf quality comparison is the Slice 07 DOE.

**Follow-ups.** None blocking. Slice 03 (generation core) consumes this to position LLM output.
