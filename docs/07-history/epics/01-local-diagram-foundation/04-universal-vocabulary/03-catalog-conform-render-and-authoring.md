# Slice 03: Catalog Conform, Render and Authoring

## Purpose

Wire generation + SVG rendering to the element catalog (Slice 01), and land the standard's
**authoring model**: the `custom` / `generated` freeform-vs-rules switch, the `metadata` identity
block, the `custom` universal canvas, and graceful unknown-`semanticType` fallback — implementing
`docs/02-design-and-features/00-diagram-json-schema.md` §9–§10, §16.

## Background

- After Slice 01, `conform` already reads catalog-derived subsets. This slice moves the **SVG
  renderer** onto the catalog and adds the runtime **authoring behaviors** the standard defines.
- Rendering already dispatches by `semanticType` (`_draw_node` + module-level marker sets), so this is
  a source swap (read the catalog) plus new capabilities.

## Design

- **SVG renderer ← catalog.** `diagram_render_service.py` reads each element's **primitive + edge
  markers** from the catalog instead of the hardcoded `if/elif` + `DASHED`/`TRIANGLE`/`DIAMOND` sets.
  Behavior-preserving for existing elements.
- **Metadata identity block.** `assemble_canonical` stamps `metadata.originalType` / `notation`
  (derived from the diagram type) / `intent` (from the prompt/name), so an editing agent has context
  even for a `custom` graph.
- **`custom` universal canvas.** Register the `custom` diagram type (subset = whole catalog); it saves
  as `authoring: custom`; generation targets a concrete type as today.
- **Unknown-type fallback.** An unrecognized `semanticType` renders via a **fallback primitive** (a
  labeled box showing the raw type as a `«stereotype»`) instead of failing — on canvas + SVG.
- **Authoring switch.** Confirm `custom` = freeform (advisory only) vs `generated` = conforms to the
  type subset + structural rules (already the model; documented + tested here).

## Included Work

- `diagram_render_service.py` marker/shape lookups → catalog; fallback primitive.
- `diagram_generation_service.py` → stamp the identity block; register the `custom` type.
- `diagram_types.py` → `custom` profile (whole-catalog subset).
- Backend tests: catalog-driven render parity, identity-block stamping, unknown-type fallback,
  `custom`-type generation/validation.

## Not In Scope

- New diagram types (deferred post-MVP); the frontend `gpNode`/palette (Slice 02).
- Special-render types (sequence/timing/communication).

## Target Areas

- `backend/services/diagrams/rendering/diagram_render_service.py`, `diagram_generation_service.py`, `diagram_types.py`,
  `element_catalog.py`; `backend/tests/`

## Exit Criteria

- Backend `manage.py test` green; SVG output for the 3 types unchanged (render parity).
- Generated diagrams carry `metadata.originalType` / `notation` / `intent`.
- A `custom` diagram accepts mixed elements; an unknown `semanticType` saves + renders via fallback.

## Previous Slice

- `02-catalog-driven-palette-and-node.md`

## Next Slice

- `04-universal-shape-vocabulary.md` — add the common UML/SysML shapes (relationships + classifiers +
  `port`) to the catalog + palette, canvas-only (generation unchanged).

## Outcome

✅ Completed. Render + conform read the catalog; the authoring model (metadata identity block,
`custom` canvas, unknown-type fallback) is in. Behavior-preserving for the 3 types.

**Delivered.**
- **Render ← catalog:** `element_catalog.py` gained edge markers (`target_marker` / `source_marker`)
  + `node_primitive()` / `all_node_semantic_types()` / `all_edge_semantic_types()` helpers;
  `diagram_render_service.py` dispatches node shapes by the catalog **render primitive** and reads
  edge dashing/markers per-edge from the catalog (the module-level marker sets are gone; `CONTAINER`
  is catalog-derived).
- **Metadata identity block:** `assemble_canonical` stamps `metadata.originalType` / `notation` /
  `intent`; profiles gained a `notation` field.
- **`custom` canvas:** a `custom` type profile whose vocabulary is the whole catalog — valid for
  save/validation (in `TYPE_PROFILES`) but **not** generatable (kept out of
  `SUPPORTED_DIAGRAM_TYPES`, which drives generation / structural critic / eval / list-types).
- **Unknown-type fallback:** an off-catalog `semanticType` renders as a rounded box (SVG) instead of
  failing.

**Verification.** backend `manage.py test` → 375 (incl. edge-marker parity, `custom`-type, and
unknown-fallback tests); no frontend change (247 stands); examples unchanged (the identity block is
generation-only).

**Deviations.** The unknown-type fallback renders a plain rounded box (matching the editor's `GpNode`
fallback) rather than a «stereotype» box — simpler and behavior-consistent. Conform already read the
catalog subset since S01, so this slice's conform work was just the `custom` profile.

**Follow-up.** none — Slice 04 (new-type enablement) next.
