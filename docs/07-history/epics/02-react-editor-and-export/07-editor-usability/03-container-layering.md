# Slice 03: Container Layering

## Purpose

Keep System Boundaries and other containers visually behind ordinary nodes so adding or selecting a container cannot block existing content.

## Background

New palette nodes are appended to the React Flow node array. A newly added 320×240 System Boundary therefore renders above earlier siblings; live pointer hit-testing selected the boundary before an Actor, and an attempted Actor drag moved the boundary instead. The backend renderer already draws all containers first, so SVG output is correctly layered and the canvas is not.

The accepted behavior is layering only: adding a boundary does not automatically adopt enclosed Use Cases or change `parentId`.

## Design

- Give containers and ordinary nodes explicit display-only z tiers on the canvas, with containers always below ordinary nodes even when selected.
- Preserve a higher selected tier for ordinary nodes without allowing React Flow's default selection elevation to lift a container above them.
- Keep container borders and exposed empty interior selectable so the boundary itself remains movable/resizable.
- Do not reorder or mutate canonical containment solely for display layering.
- Preserve existing explicit drag-stop containment: moving a compatible Use Case into or out of a System Boundary remains the only automatic `parentId` transition.
- Match the backend's existing containers → edges → ordinary nodes → labels ordering and promote that complete ordering into the rendering design owner.

## Included Work

- Add a pure node-layer decoration helper and tests for containers, ordinary nodes, and selection.
- Configure React Flow selection elevation consistently with those tiers.
- Verify newly added, loaded, selected, moved, and resized System Boundaries.
- Verify underlying Actor/Use Case selection and movement through overlap.
- Preserve existing `reparentNode` behavior and adapter round-trip.
- Add browser and canvas/SVG layering regression coverage.
- Update `editor-ui-design.md` (canvas layering), `03-rendering-design.md` (full draw order), `02-frontend-architecture.md` (display-only z tiers), `decision-decisions.md` (layer-only containment decision), and this slice's Outcome when implemented.

## Not In Scope

- Automatic adoption of enclosed Use Cases when a boundary is added.
- A general Layers panel, persisted `zIndex`, arbitrary Bring Forward/Send Back commands, or backend schema changes.
- Allowing Actors to become children of a System Boundary.
- Changing container styling or dimensions.

## Target Areas

- `frontend/src/editor/EditorPage.tsx`
- `frontend/src/editor/lib/containment.ts` and focused tests
- `frontend/src/adapters/reactFlow.ts` tests
- `frontend/e2e/smoke.spec.ts`
- Backend render-order parity tests where needed
- Active editor/architecture/decision owners

## Exit Criteria

- Adding or selecting a System Boundary over existing nodes never prevents selecting or moving those nodes.
- The boundary remains selectable and movable through its exposed border/interior.
- Adding or layering the boundary does not change any `parentId`.
- Explicitly dragging a Use Case into/out of the boundary still sets/clears `parentId` and preserves absolute position.
- Canvas and SVG use equivalent container-behind-content ordering.
- Focused tests and `npm run verify` pass; backend render tests pass if touched.

## Previous Slice

- [`02-connection-guidance.md`](02-connection-guidance.md)

## Next Slice

- [`04-relationship-authoring.md`](04-relationship-authoring.md)

## Outcome

**Completion:** Added pure display-tier decoration with containers at tier 0, edge strokes at 1, ordinary nodes at 2, and selected ordinary nodes at 3; React Flow's automatic selected-node elevation is disabled so a selected container stays behind. Edge labels and selected route controls retain their existing top overlay tiers. Runtime `zIndex` is stripped by the canonical adapter.

**Deviation:** None. Layering is display-only: adding/selecting a System Boundary does not reorder canonical nodes or change `parentId`, Actors remain ineligible for subject containment, and explicit Use Case drag-stop reparent/unparent behavior is unchanged.

**Verification:** `cd backend; uv run python manage.py test` passed 682 tests (4 skipped), including a new containers → edges → ordinary nodes → labels SVG-order assertion. `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build, 427 unit/component tests, and 38 Chromium E2E tests. Browser coverage adds a boundary over existing Actor/Use Case content, verifies all runtime tiers while selected, moves the underlying Actor and exposed boundary independently, confirms no implicit containment on save, then verifies explicit drag-in/drag-out `parentId` round-trip. A read-only implementation audit found no code or scope defect.

**Follow-up:** Slice 04 owns catalog-driven relationship tools and primary-tab relationship identity.
