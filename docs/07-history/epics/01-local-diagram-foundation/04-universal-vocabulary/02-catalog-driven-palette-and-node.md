# Slice 02: Catalog-Driven Palette and Node

## Purpose

Mirror the backend element catalog (Slice 01) on the frontend: converge the three custom node
components into **one catalog-driven `gpNode`**, and reorganize the palette into **notation groups
(Common / UML / SysML) with a diagram-type filter** — implementing
`docs/02-design-and-features/00-diagram-json-schema.md` §5 + §8.

## Background

- Today `editor/canvas/nodeTypes.ts` registers `activityNode` / `useCaseNode` / `bddNode`, each a component
  in `customNodes.tsx` that already **dispatches by `data.semanticType`**; `editor/lib/palette.ts` is a
  flat per-type list. So the convergence is mostly de-duplication, not new rendering.
- The standard mandates a single `gpNode` (no aliases) + a family-grouped, filterable palette. This
  is the frontend half of the catalog; it depends on Slice 01 (the backend catalog).

## Design

- **Catalog mirror.** A small frontend view of the catalog (`semanticType → { primitive, family,
  nativeTypes }`), sourced from the backend (e.g. via `diagram_list_types` / a generated constant) so
  the two never drift.
- **`GpNode` component.** Collapse `ActivityNode` / `UseCaseNode` / `BddNode` into one `GpNode`
  that switches on `data.semanticType` (the existing per-component switches merge). Register only
  `gpNode` in `nodeTypes`.
- **`gpNode` cutover (coordinated with backend).** Emit `type: "gpNode"` from
  `assemble_canonical` / the profile, and **re-seed** the example library so committed examples carry
  `gpNode`. This is a deliberate **data cutover** (not byte-identical), per the clean-slate standard —
  no `activityNode`/`useCaseNode`/`bddNode` aliases remain.
- **Palette.** Rebuild `palette.ts` as catalog-derived entries grouped **Common / UML / SysML**, with
  a **filter** defaulting to the current diagram type's subset and a "Show all" toggle; an off-type
  drop relaxes the diagram to `custom` (existing authoring model).

## Included Work

- `editor/canvas/customNodes.tsx` → one `GpNode`; `editor/canvas/nodeTypes.ts` registers `gpNode` only.
- `editor/lib/palette.ts` → catalog-derived, family-grouped, filterable.
- Backend `type: "gpNode"` emission + example re-seed; `reactFlow` adapter/tests updated.
- Vitest: node rendering per `semanticType`, palette grouping/filter, round-trip on the re-seeded
  examples.

## Not In Scope

- New diagram types (deferred post-MVP); the `custom` canvas behavior + metadata (Slice 03, though the
  palette "Show all" hook lands here).
- SVG renderer catalog wiring (Slice 03).

## Target Areas

- `frontend/src/editor/canvas/customNodes.tsx`, `nodeTypes.ts`, `palette.ts`, `adapters/reactFlow.ts` (+ tests)
- `backend/services/generation/pipeline/diagram_generation_service.py` / `diagram_types.py` (emit `gpNode`) + re-seed

## Exit Criteria

- Frontend `npm run test` green; the 3 types render identically (visual parity) and round-trip.
- Examples re-seeded to `type: "gpNode"`; backend `manage.py test` green.
- Palette shows Common/UML/SysML groups + a working type filter.

## Previous Slice

- `01-vocabulary-catalog.md` (and builds on Epic 2's BDD compartments, S10).

## Next Slice

- `03-catalog-conform-render-and-authoring.md` — the backend generation/render + authoring half of
  the enabler.

## Outcome

✅ Completed. One `gpNode` render family + a family-grouped palette; the 3 types render identically.

**Delivered.** `customNodes.tsx` collapses `ActivityNode` / `UseCaseNode` / `BddNode` into one
`GpNode` (dispatch by `semanticType`); `nodeTypes.ts` registers only `gpNode`; `palette.ts` regrouped
into **Common / UML / SysML** families; `PropertyPanel`'s compartment editor gates on `semanticType`
(block-family) instead of `type`. Backend emits `type: "gpNode"` (all 3 profiles) and the 36 examples
were re-seeded (only the node `type` field changed). The render service's now-dead
`type == "bddNode"` branch was dropped (the `semanticType` check covers it).

**Verification.** backend `manage.py test` → 372; frontend `npm run test` → 247; `npm run lint`
(0 errors) + `npm run build` clean. The example re-seed diff is only the `type` field per node.

**Deviations.** The diagram-type-scoped palette *filter* (default to the current type) is deferred to
Slice 04 (when there are many types to filter); the existing search box + the Common/UML/SysML
grouping stand in for now.

**Follow-up.** none — Slice 03 (conform/render ← catalog + authoring/metadata) next.
