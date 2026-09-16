# Slice 04: Universal Shape Vocabulary (canvas-only)

## Purpose

Add the common, reusable **UML/SysML elements** to the shared element catalog + the shape palette so
they can be composed on the **`custom` canvas** and **reused** by any diagram that shares them
(define-once / OO-DRY). This is **code only** and **canvas-only**: it adds *shapes*, **not** new
diagram types, and it does **not** enter the 3 MVP types' generation vocabulary — so
`diagram_generate` and the 36 answer keys stay **byte-identical**.

## Background

- After S01–S03 the catalog drives vocabulary, render, conform, and the palette. This slice enriches
  the catalog with generic elements that today's 3 types don't own, making them available to hand-
  authoring now and to future diagram types later — without standing up those types.
- Generation stays modular + data-driven (see `04-generation-design.md`): these elements are just
  catalog data; nothing about the generation engine changes.

## Design

- **Catalog (`element_catalog.py`).** Add the generic elements, marked **universal** (valid on the
  `custom` canvas; **not** in the `activity` / `use_case` / `bdd` subsets):
  - Relationships (edges): `dependency` (dashed, open arrow), `realization` (dashed, hollow triangle).
  - UML classifiers (nodes): `class`, `interface`, `component`, `package` (compartment box).
  - SysML (nodes): `requirement` (compartment box), `port` (small square).
- **Render — canvas + SVG parity.** Classifiers reuse the compartment-box primitive; the two new
  edges are catalog-driven (S03) so they render with no new edge code; the only new shape is the
  **`port`** primitive, added to **both** `diagram_render_service.py` (SVG) and `customNodes.tsx`
  (canvas `GpNode`).
- **Palette (`palette.ts` + `NodePalette`).** List the new shapes under **UML / SysML**, with preview
  glyphs; they carry `type: "gpNode"` like every other palette shape.

## Included Work

- `element_catalog.py`: the generic elements (universal `valid_in`) + edge markers.
- `port` render primitive in the SVG exporter + the canvas `GpNode` (parity); classifier branch in
  `GpNode` covers the new compartment-box elements.
- `palette.ts` entries + `NodePalette` preview glyphs.
- Tests: catalog integrity for the new elements; the `custom` canvas renders/round-trips them; SVG
  renders them; the 3 MVP types + the 36 examples are unchanged (byte-identical re-seed).

## Not In Scope

- New diagram **types** (deferred post-MVP; their intended vocab is documented in
  `../../../../02-design-and-features/00-diagram-json-schema.md`).
- Adding these elements to the 3 MVP types' **generation** vocab, answer keys, or prompts.

## Target Areas

- `backend/services/diagrams/catalog/element_catalog.py`, `diagram_render_service.py`
- `frontend/src/editor/canvas/customNodes.tsx`, `palette.ts`, `NodePalette.tsx`
- `backend/tests/`, `frontend/src/**/*.test.*`

## Exit Criteria

- The generic shapes appear in the palette and render on the `custom` canvas **and** SVG (parity).
- `diagram_generate` output + the 36 examples are **byte-identical** (generation untouched).
- backend `manage.py test` + frontend `npm run test` / lint / build green.

## Previous Slice

- `03-catalog-conform-render-and-authoring.md`

## Next Slice

- `05-answer-key-rebaseline.md` — regenerate the 3 MVP diagrams' answer keys on the final catalog.

## Outcome

✅ Completed. The generic UML/SysML shapes are in the catalog + palette + render (canvas-only);
the 3 MVP types are untouched — generation + the 36 examples are byte-identical.

**Delivered.**
- `element_catalog.py`: 8 generic elements — `class` / `interface` / `component` / `package` /
  `requirement` (classifier-box), `port` (new primitive), `dependency` / `realization` (dashed edges;
  `realization` = hollow triangle) — all `valid_in={custom}` (canvas-only). Added the `port` primitive.
- SVG render: `_draw_port` (small square) + a `port` dispatch branch; classifiers reuse the
  compartment box; edges use the catalog markers.
- Frontend: `GpNode` classifier-box family extended (via `CLASSIFIER_BOX_TYPES`) + a `port` shape;
  `edgeMarkerEnd` handles `dependency` (open arrow) + `realization` (hollow triangle); palette lists
  the 6 new node shapes under UML / SysML with preview glyphs.
- Schema doc §7 build-status note (built vs canvas-only vs planned).

**Verification.** backend `manage.py test` → **377** (+ canvas-only guard + generic-render tests);
frontend `npm run test` → **247**, `npm run lint` 0 errors, `npm run build` clean; re-seed
**byte-identical** (generation unchanged).

**Deviations.** `dependency` → BDD is **deferred to S05** (kept canvas-only here so generation + the
coverage assertion stay byte-identical); it joins BDD's vocab with its keys in S05. Canvas dashing for
authored `dependency`/`realization` edges follows the saved style (as with `include`/`extend`); the
SVG export dashes them via the catalog.

**Follow-up.** none — Slice 05 (regenerate the 3 diagrams' keys + `dependency`→BDD) next.
