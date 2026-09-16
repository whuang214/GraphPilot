# Core Vocabulary Runtime

## Purpose

Implement the approved core Activity, Use Case, and BDD vocabulary contracts atomically across backend generation/validation/rendering and frontend authoring/rendering.

## Included Work

- Separate supported compatibility entries from authorable/generatable core entries in the shared catalog/profile model.
- Add optional canonical BDD Block `data.stereotype` and preserve it through generation helpers, adapters, editing, validation, and canvas/SVG rendering.
- Add first-class BDD `composition` with part-to-whole direction, target filled diamond, and atomic Swap ends.
- Reduce Activity and BDD generation/palette/selector vocabularies to the approved lists while keeping Use Case unchanged except for System Boundary UI naming.
- Infer `commentLink` for every new edge incident to a Note.
- Restore the Note's complete top-right dog-ear on the canvas and guard canvas/SVG parity.
- Rebaseline prompts, examples, vocabulary coverage, structural checks, and tests without specialist padding.

## Not In Scope

- Deleting or automatically migrating existing specialist documents.
- New diagram types, advanced UML/SysML generation modes, or arbitrary freeform drawing.
- Changes to context readiness semantics beyond consuming the same bounded generation vocabulary.

## Target Areas

- `backend/services/diagrams/catalog/`
- `backend/services/generation/`
- `backend/services/diagrams/rendering/diagram_render_service.py`
- `backend/assets/schemas/diagram.json`
- `backend/assets/blueprints/`
- `backend/tests/`
- `frontend/src/types/diagram.ts`
- `frontend/src/adapters/reactFlow.ts`
- `frontend/src/editor/`
- `frontend/e2e/`

## Exit Criteria

- Type/schema discovery, generation prompts, palettes, Show all, and semantic selectors expose exactly the approved core identities.
- Existing specialist JSON remains safely loadable/renderable as specified but cannot be newly authored.
- BDD Block headings, structured features, Composition markers/direction, Swap ends, Comment Links, and Note dog-ears match on canvas and SVG.
- Realistic answer keys cover every core identity without specialist coverage fixtures.
- Full backend and frontend verification passes, including browser checks.

## Previous Slice

- [`12-core-vocabulary-contract.md`](12-core-vocabulary-contract.md)

## Next Slice

- None in this group.

## Outcome

**Completion.** The backend and frontend now separate core authoring/generation from retained catalog compatibility, expose the exact Activity/Use Case/BDD profiles, preserve optional BDD Block `data.stereotype`, render first-class part-to-whole Composition at the target, infer Note Comment Links, and keep the complete Note dog-ear in canvas/SVG parity. The deterministic source specs and all 48 answer keys now use core identities directly without specialist coverage padding.

**Verification.** The implementation audit was completed and its Note SVG regression gap was addressed. The deterministic seeder completed 48/48 render-checked examples; `cd backend; uv run python manage.py test` passed 676 tests with 3 skipped; `cd frontend; npm run verify` passed lint with zero findings, production build, 411 unit tests, and 32 Chromium E2E tests including stereotype persistence, Composition Swap ends, Comment Link inference, and dog-ear rendering.

**Deviations.** Primary Block stereotypes remain manual presentation data and are deliberately absent from direct/context model output schemas. Specialist identities and structured legacy fields remain schema/catalog-readable for existing documents but are excluded from generation, palettes, Show all, and semantic selectors.

**Follow-up.** No further slice remains in this group; the next main MVP workflow gap is Epic 4 `diagram_update` planning and implementation.
