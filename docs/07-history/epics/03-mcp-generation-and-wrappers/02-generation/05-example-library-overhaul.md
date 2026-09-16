# Slice 05: Example Library Overhaul

## Purpose

Completely re-curate and expand the example library so generation has strong few-shot training material and the eval/DOE (Slices 06–07) have a trustworthy, **leakage-free** basis. Split the library into a **training pool** (few-shot context) and an **eval pool** (held out from training, scoring only).

> **Source of truth:** design context lives in `docs/02-design-and-features/07-evaluation-and-doe-design.md` (the training/eval split) and `docs/02-design-and-features/04-generation-design.md` (the examples library). This slice carries the implementation detail; the design docs win on conflict.

## Background

A design review of the eval framework (now Slice 06) surfaced two problems with the current 12 examples (4/type):

- **Leakage.** The same `output.gp.json` files are used both as generation few-shot context (`_build_few_shot`) and as eval answer keys, so a generated diagram can be scored against an example it was literally shown — inflating DOE scores.
- **Too few + low diversity.** 4/type gives weak DOE signal and limited structural coverage.

This slice fixes both by re-curating to a larger, diverse, **split** library before the eval/DOE consume it. It also renumbers the downstream Epic 3 slices: eval → **06**, run-the-DOE → **07**.

## Design

### Count + split (36 total)

Per MVP type (`activity_diagram`, `use_case_diagram`, `bdd_diagram`):

- **4 training** examples — the few-shot pool (supports the 0/2/4 few-shot DOE level)
- **8 eval** examples — held out from training, eval/DOE scoring only

= 12/type × 3 = **36 total**. The two pools never overlap, so a diagram is never scored against an example used to teach generation.

### Split mechanism (subfolders)

Restructure under each type:

```text
backend/assets/blueprints/<type>/examples/
  training/<name>/{prompt.md, output.gp.json}
  eval/<name>/{prompt.md, output.gp.json}
```

- `_build_few_shot` globs `examples/training/*/output.gp.json` only.
- the Slice 06 eval loader globs `examples/eval/*/...` only.

### Diversity targets (real coverage, not padding)

Constrained to the MVP type vocabulary (`diagram_types.py`) so nothing is silently coerced:

- **activity_diagram** (`start, action, decision, merge, end, note`; edges `flow`): linear flow; single decision + merge; loop/rework (merge back to an earlier action); two sequential decisions; labeled Yes/No branches; multiple end nodes; long pipeline; an action annotated with a `note`.
- **use_case_diagram** (`actor, useCase, systemBoundary, note`; edges `association, include, extend`): single actor + few use cases; multiple actors sharing use cases; `include`; `extend`; `systemBoundary` containment (`parentId`); many use cases for one actor; mixed include+extend; a `note`.
- **bdd_diagram** (`block, part, value, constraint, note`; edges `composition, reference, generalization`): simple block→part composition; multi-level composition; `reference` between blocks; `generalization` (specialized → general block); a block with `value` properties; a `constraint` node; many parts; deep nesting.

The training pool gets ~4 canonical/representative shapes per type; the eval pool gets the broader 8 including the trickier variants. (Note: the MVP vocabulary has no fork/join, aggregation, or actor generalization, so "parallelism" is approximated with decision/merge and variety comes from structure size/shape rather than new node kinds.)

### Authoring method (curated gold standards, **not** generated)

Each example is a **hand-curated gold standard**, authored as a compact **logical spec** (nodes: `id` / `semanticType` / `label` / `parentId`; edges: `source` / `target` / `semanticType` / `label`) plus a `prompt.md`. The full `output.gp.json` is produced **deterministically** from the logical spec via the existing conform + assemble + layout path (`grandalf`, offline) — **not** via `diagram_generate`, which would make the eval circular (scoring the model against its own output). Each output is then **validated** (`DiagramValidationService`, no errors) and **rendered** (`DiagramRenderService`) to confirm it is well-formed, and stamped as a curated sample (`metadata.source = "sample"`).

A small, reviewable seed script (e.g. `backend/assets/blueprints/_seed_examples.py` or a management command) holds the 36 logical specs and writes the files, so the library is reproducible and the gold content is easy to review in one place. The human reviewer signs off on correctness.

## Included Work

- restructure `examples/` into `training/` and `eval/` subfolders per type
- author 36 gold-standard examples (12/type: 4 training + 8 eval), each validated + rendered
- update `_build_few_shot` (and any other example reader) to use the **training** pool only
- tests: every example validates + renders; pool counts are correct (4 training + 8 eval per type); few-shot draws only from training
- docs: this slice; `04-generation-design.md` (the split + new paths); renumber the downstream slice references (eval → 06, DOE → 07)

## Not In Scope

- the eval comparator / judge and the DOE run (Slices 06–07, later removed — deferred post-MVP, pending an embeddings-based rebuild) — this slice only supplies the data + the split
- changing the canonical schema, the type vocabulary, or generation logic (beyond the few-shot source path)
- `diagram_generate`-based authoring of answer keys (explicitly excluded — gold standards are curated)

## Target Areas

- `backend/assets/blueprints/<type>/examples/` (restructured + re-curated)
- `backend/services/generation/pipeline/diagram_generation_service.py` (`_build_few_shot` source path)
- a seed script / management command for reproducible authoring
- backend tests
- `docs/02-design-and-features/04-generation-design.md`

## Exit Criteria

- `examples/training/` (4/type) and `examples/eval/` (8/type) exist; 36 total; the pools are disjoint
- every `output.gp.json` passes `DiagramValidationService` and renders without error
- `_build_few_shot` draws only from the training pool (covered by a test)
- `python manage.py test` passes

## Previous Slice

- `04-generate-tool.md`

## Next Slice

- `../03-eval-and-doe/09-critique-refine-loop.md`

## Outcome

✅ Completed. The example library was re-curated, diversified, and split into `training`/`eval` pools; all readers were repointed and tests updated.

**Delivered.**
- 36 curated gold-standard examples (per MVP type: **4 training + 8 eval**) authored **offline, no LLM** via `backend/assets/blueprints/_seed_examples.py` (hand-written logical specs → conform → assemble + grandalf layout → validate → render-check → write). Diverse domains *and* structures within each type's vocabulary (e.g. activity: linear / decision / single + double loops / nested decisions / multi-end / note; use_case: 1–4 actors, include + extend, `systemBoundary` containment, note; bdd: shallow + deep composition, reference webs, multi-level generalization, value + constraint).
- Library restructured into `examples/training/<name>/` + `examples/eval/<name>/`; the 12 old flat Epic 2 examples removed.
- `_build_few_shot` now reads the **training** pool only; `test_samples` / `test_contracts` / `test_layout` / `test_render` globs + the two frontend example globs + the e2e seed repointed to the split. Added `PoolSplitTests` (pool counts 4 + 8, pools disjoint, few-shot reads training only).

**Deviations.**
- Examples authored via a deterministic **seed script** (logical specs → assemble) rather than hand-written JSON — same gold-standard result, reproducible and reviewable in one place; explicitly **not** `diagram_generate` (which would be circular).
- The seed orders nodes **top-level-first, then children** so the canonical examples round-trip losslessly through the editor adapter (React Flow requires parent-before-child).
- Diversity targets were corrected to the actual MVP vocabulary (no fork/join, aggregation, or actor-generalization shapes exist).

**Verification.**
- `python manage.py test` → **242 pass** (example validation over all 36 + the new pool-split tests).
- Frontend: `vitest` **186 pass** (lossless round-trip over all 36), `oxlint` clean, `tsc -b` + `vite build` green. Playwright e2e 8/9 — the 9th is a save-toast assertion (the save itself succeeds); the editor-UI e2e is owned separately.

**Follow-up.** Slice 06 (eval framework) consumes the held-out `eval` pool. Optional: have `assemble_canonical` / `diagram_generate` adopt the same top-level-first node order for generated output.

**Follow-up (delivered).** `_build_few_shot` now injects each training example as a **request → ideal answer pair** (the `prompt.md` `## Prompt` text beside its projected logical `output.gp.json`) rather than output-only, so the model learns the prompt → structure mapping. Added `PoolSplitTests.test_few_shot_pairs_request_with_output`. (`_project_to_logical` is unchanged.)
