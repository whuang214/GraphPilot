# Slice 09: Comprehensive Node and Edge Shapes

## Purpose

Render the common-tier UML/SysML vocabulary added in Epic 1 Slice 08 — on both the React
Flow canvas (`customNodes.tsx` / `reactFlow.ts` / `FloatingEdge.tsx`) and the SVG export
(`diagram_render_service.py`), keeping the two in lock-step ("look like the editor").

## Background

Epic 2 owns the type-specific node/edge renderers and the SVG export shape language. Slice
08 expanded the vocabulary; this slice draws it. Anchored to **UML 2.5.1** / **SysML 1.6**.

## Design

Per-type, additive-first, with the canonical shapes drawn identically on canvas and export:

### Activity
- `start` → UML **initial node** (solid filled disc); `end` → **activity-final** (bull's-eye:
  ring + solid inner dot) — replacing the earlier text "pills".
- `fork` / `join` → solid **synchronization bar**.

### Use case
- `generalization` edge → solid line, **hollow triangle at the parent** (reuses the existing
  `gp-generalization` marker / `_marker_triangle`).
- include/extend are **dashed on the canvas** (`FloatingEdge`, display-only so the save
  round-trip stays byte-stable), matching the export's `DASHED_EDGE_SEMANTIC_TYPES`. Marker
  direction follows the authored source/target per the corrected guidance.

### BDD
- `enumeration` renders as a `«enumeration»` compartment box (distinct stereotype header).
- `aggregation` → **hollow diamond** at the whole (source) end; `composition` → **filled
  diamond** at the whole end. Both now sit at the **source** on the canvas (`markerStart`) to
  match the export (`points[0]`), and neither draws a target arrowhead.
- `association` / `reference` → plain line, **no marker** (canvas already drew none; the export
  now also omits the spurious arrowhead).

## Included Work

- `backend/services/diagrams/rendering/diagram_render_service.py` — `_draw_initial_node`, `_draw_final_node`,
  `_draw_bar`; hollow option on `_marker_diamond`; marker dispatch carve-outs (no target arrow
  for whole-part + plain edges); enumeration in the BDD dispatch.
- `backend/services/diagrams/catalog/constants.py` — fork/join sizes (render + layout maps).
- `frontend/src/editor/canvas/customNodes.tsx` — `ActivityNode` disc / bull's-eye / bar branches.
- `frontend/src/adapters/reactFlow.ts` — `aggregation` marker; whole-part diamonds at the source.
- `frontend/src/editor/canvas/FloatingEdge.tsx` — display-only include/extend dashing.
- `frontend/src/editor/EditorPage.tsx` — `gp-aggregation` hollow-diamond marker def.
- `frontend/src/editor/lib/palette.ts` — Start / End / Fork / Join palette items + sizes.
- `frontend/src/editor/components/NodePalette.tsx` — `ShapePreview` glyphs updated for the new/changed
  shapes (start disc, end bull's-eye, fork/join bar, enumeration).

## Not In Scope

- Vocabulary / structural rules (Epic 1 Slice 08).
- Advanced elements (deferred list in the blueprint docs).
- Re-curating the example library / eval re-baseline (separate slice/chat).

## Target Areas

- `backend/services/diagrams/rendering/diagram_render_service.py`, `backend/services/diagrams/catalog/constants.py`
- `frontend/src/editor/canvas/customNodes.tsx`, `frontend/src/adapters/reactFlow.ts`,
  `frontend/src/editor/canvas/FloatingEdge.tsx`, `frontend/src/editor/EditorPage.tsx`,
  `frontend/src/editor/lib/palette.ts`

## Exit Criteria

- New shapes/markers render identically on the canvas and in the SVG export.
- Save round-trip stays byte-stable (display-only dashing; no new persisted fields).
- Backend + frontend test suites green; typecheck + lint clean.

## Previous Slice

- `../02-renderers-and-samples/08-sample-library.md`

## Next Slice

- `10-bdd-block-compartments.md` — the BDD feature-compartments slice (same `03-comprehensive-shapes/`
  group). Follow-up: re-curate the training/eval example library to exercise the new shapes and
  re-baseline the generation DOE (deferred to a separate chat).

## Outcome

✅ Completed as planned across all three types. Canvas and SVG export draw the new vocabulary
identically.

**Delivered.** Activity initial/final/fork/join; use-case generalization + canvas dashing for
include/extend; BDD enumeration + aggregation/association markers.

**Deviations.** Corrected two pre-existing composition issues for consistency with the new
aggregation edge: the whole-part diamond now sits at the **source/whole** end on the canvas
(it had been at the target), and whole-part / plain edges no longer draw a spurious target
arrowhead in the export. Save round-trip stays byte-stable.

**Verification.** Backend `manage.py test` → 333 passed (incl. new render tests for the
initial/final/fork/join shapes, the hollow aggregation diamond, and enumeration); frontend
`vitest` → 244 passed (incl. the whole-part marker-placement test); `tsc --noEmit` clean;
`oxlint` 0 errors. Palette previews updated for the new/changed shapes.

**Follow-up.** Example/eval re-baseline deferred to a separate slice/chat.
