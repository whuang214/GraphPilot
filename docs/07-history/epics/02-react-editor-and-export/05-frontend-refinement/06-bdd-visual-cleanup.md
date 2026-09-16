# Slice 06: BDD Visual Cleanup

## Purpose

Make empty BDD classifiers read as intentional compact blocks instead of large boxes with unused compartment space, without weakening populated feature-compartment fidelity.

## Design

- A classifier with no visible feature rows uses a compact header-only intrinsic size containing its keyword/stereotype and name.
- Empty classifiers render no body filler, phantom compartment, or unnecessary divider.
- Populated classifiers render only non-empty derived compartments in canonical order and retain enough height for every visible row.
- New-node defaults and feature-driven auto-fit use the same compact/expanded sizing rules. An explicit user resize remains authoritative until the user invokes auto-fit.
- Compactness is presentation/layout behavior; no empty placeholder arrays or display-only compartments are added to canonical data.
- Canvas and SVG use matching header, row, padding, divider, and minimum-size constants.

## Included Work

- Add a shared BDD visible-content/intrinsic-size contract for empty and populated classifiers.
- Update canvas classifier rendering, palette defaults, resize minimums, and auto-fit behavior.
- Update backend classifier rendering and any generation/layout defaults that produce empty BDD blocks.
- Preserve enumeration literals and every existing structured feature group when non-empty.
- Add fixtures/tests for empty blocks, each compartment family, mixed compartments, last-row removal, explicit resize, and auto-fit.

## Not In Scope

- New BDD semantic types, feature kinds, or canonical placeholder compartments.
- Rewriting user-authored explicit dimensions without an auto-fit action.
- Property-panel restructuring or relationship presets.
- General typography changes for non-BDD shapes.

## Target Areas

- `frontend/src/editor/lib/bddCompartments.ts`.
- `frontend/src/editor/canvas/customNodes.tsx` and BDD sizing/resize helpers.
- `frontend/src/editor/lib/palette.ts` for new-node defaults.
- `backend/services/diagrams/rendering/diagram_render_service.py` and shared catalog/layout constants.
- Frontend BDD compartment tests and backend render/layout tests.

## Exit Criteria

- A new or auto-fitted BDD classifier with no visible features renders as a compact header-only block.
- Empty blocks have no blank compartment body or divider on either canvas or SVG.
- Adding features expands the block to show every non-empty compartment; removing the last row returns auto-fit to the compact size.
- Explicit user sizing remains stable until auto-fit is requested.
- Canonical feature data is unchanged by compact rendering, and enumeration/populated block regressions remain covered.
- Canvas, SVG, and PNG use equivalent compact and populated BDD structure.
- Focused BDD tests and relevant frontend/backend verification pass.

## Previous Slice

- [`05-manual-route-editing.md`](05-manual-route-editing.md)

## Next Slice

- [`07-relationship-presets-and-properties.md`](07-relationship-presets-and-properties.md)

## Outcome

**Completed.** Canvas and SVG omit the divider/body for classifiers with no visible derived feature rows and center the keyword/name across the saved box. New palette classifiers, generated empty BDD classifiers, final-feature removal, and Fit to content use the shared 48px compact minimum; populated groups retain ordered compartment rows and content-fit growth. Explicitly enlarged saved boxes keep their dimensions while remaining visually unpartitioned.

**Verification.** Frontend derivation/node/patch tests and backend render/generation tests cover absent, suppressed, malformed, short, tall, and mixed features; Playwright verifies a newly authored empty classifier is 48px. Final aggregate gate evidence is recorded in Slice 08.
