# Slice 01: Vocabulary Catalog

## Purpose

Refactor the per-type vocabulary from independent frozensets into **one universal element catalog**
(per `docs/02-design-and-features/00-diagram-json-schema.md`), and make the type profile + validation
read from it — **without changing behavior** for the current three types. This is the foundation the
later slices (palette/`gpNode`, conform/render, new types) build on.

## Background

- The **vocabulary** lives in `diagram_types.py` (the type profile), alongside the schema +
  validation. Epic 1's Slice 08 already *expanded* it to the comprehensive UML 2.5.1 / SysML 1.6 tier —
  this slice changes **how** the vocabulary is defined (one catalog + subsets), not (yet) what new
  types exist.
- Today each type declares independent `allowed_node_semantic_types` / `allowed_edge_semantic_types`
  frozensets; the same elements (`note`, `generalization`, `association`, …) are duplicated across
  types. The standard (§3–§7) defines each element **once** in a catalog, and a type is a **subset**.
- Since validation Layer 4 and generation-conform already *read the profile's allowed sets*, pointing
  the profile at a catalog is a source swap, not a behavior change.

## Design

### The catalog (new module `services/diagrams/catalog/element_catalog.py`)

- `RENDER_PRIMITIVES` — the finite shape set (`classifier-box`, `ellipse`, `actor`, `diamond`,
  `bar`, `initial`, `final`, `container`, `note`, `port`).
- `ELEMENT_CATALOG: dict[str, ElementSpec]` — `semanticType → ElementSpec` (`kind` node/edge;
  node `primitive` + `is_container` + `supports_compartments`; edge `markers`; `notation`;
  `valid_in` = the diagram types that allow it).
- Seeded with **exactly today's vocabulary**, so the derived per-type subsets equal the current
  frozensets.

### Wire the existing services to the catalog

- `DiagramTypeProfile.allowed_node_semantic_types` / `allowed_edge_semantic_types` become **derived**
  (a catalog subset by `valid_in`), not hand-maintained literals. `node_type` + structural rules stay
  per-type this slice.
- Move the constants that already encode catalog data — conform's `_DEFAULT_NODE_SEMANTIC` /
  `_CONTAINER_SEMANTIC_TYPES` / `_DASHED_EDGE_SEMANTICS` — to read from the catalog (keeps conform
  behavior identical).
- The SVG renderer's marker/shape lookups + the canvas consume the same catalog in **Slices 02–03**;
  this slice is backend vocabulary/profile only.

### Behavior-preserving

The three types keep identical allowed sets. A test asserts each profile's catalog-derived subset
equals its previous frozenset, and re-seeding the 36 examples must produce **byte-identical**
`output.gp.json` — proof the refactor changed nothing observable.

## Included Work

- New `element_catalog.py` (primitives + `ELEMENT_CATALOG` + a subset helper).
- Refactor `diagram_types.py` profiles to derive allowed sets from the catalog.
- Refactor `conform_logical` defaults (`_DEFAULT_NODE_SEMANTIC` / `_CONTAINER_SEMANTIC_TYPES` /
  `_DASHED_EDGE_SEMANTICS`) to read the catalog.
- Tests: catalog integrity (every profile subset ⊆ catalog; each type's subset == its previous
  frozenset); existing suites stay green.

## Not In Scope

- **Frontend** (single `gpNode`, palette families/filter) — Slice 02.
- **SVG renderer** reading the catalog for shapes/markers — Slice 03 (behavior unchanged meanwhile:
  it already dispatches by `semanticType`).
- New diagram types, the `custom` universal canvas, the metadata identity block, unknown-type
  fallback — Slice 03 and the per-type slices (04+).
- Removing `activityNode` / `useCaseNode` / `bddNode` from output, or dropping `reference` — those
  land with the `gpNode` cutover (Slice 02) / new-type slices, not this behavior-preserving step.

## Target Areas

- `backend/services/diagrams/catalog/element_catalog.py` (new)
- `backend/services/diagrams/catalog/diagram_types.py`, `diagram_generation_service.py`, `constants.py`
- `backend/tests/` (catalog integrity + unchanged-subset assertions)

## Exit Criteria

- `python manage.py test` green (≥ current count) incl. the new catalog-integrity tests.
- Each of the 3 types' allowed node/edge sets is **identical** to before (asserted).
- Re-running `python graphpilot/blueprints/_seed_examples.py` yields **byte-identical** example files
  (no `git diff` under `backend/assets/blueprints/*/examples/`).
- No frontend change; frontend `npm run test` still green.

## Previous Slice

- Start of Epic 1's `04-universal-vocabulary/` group (a later technical-refactor phase). Builds on Epic 1's `../02-notation-vocabulary/08-comprehensive-notation-vocabulary.md`.

## Next Slice

- `02-catalog-driven-palette-and-node.md` — the frontend half (single `gpNode` + catalog-driven
  palette families/filter).

## Outcome

✅ Completed as planned. Behavior-preserving; all exit criteria met.

**Delivered.** New `services/diagrams/catalog/element_catalog.py` (`RENDER_PRIMITIVES` + `ELEMENT_CATALOG` seeded with
today's exact vocab + `allowed_node/edge_semantic_types` / `container_semantic_types` /
`dashed_edge_semantic_types` helpers). `diagram_types.py` profiles now **derive** their allowed sets
from the catalog and carry the per-type coerce defaults (`default_node/edge_semantic_type`).
`conform_logical` sources the container + dashed sets from the catalog and the defaults from the
profile (the old `_DEFAULT_NODE/EDGE_SEMANTIC` / `_CONTAINER_SEMANTIC_TYPES` / `_DASHED_EDGE_SEMANTICS`
constants are gone).

**Verification.** `manage.py test` → **372** (incl. 5 new `test_element_catalog` tests: integrity +
unchanged-subset guard); re-running `_seed_examples.py` left the 36 examples **byte-identical** (empty
`git diff`); no frontend change (still green).

**Follow-up.** none — Slice 02 (palette + `gpNode`) consumes the catalog next.
