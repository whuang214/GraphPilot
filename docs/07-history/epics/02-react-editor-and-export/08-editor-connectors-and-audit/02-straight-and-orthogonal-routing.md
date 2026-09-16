# Slice 02: Straight and Orthogonal Routing

## Purpose

Allow each relationship to use a persisted straight or orthogonal path while preserving deterministic anchors, marker direction, save/reload, and canvas/SVG/PNG parity.

## Background

The editor currently resolves every edge through the orthogonal router, and the strict route schema has no mode. This is appropriate for Activity flow but makes many Use Case relationships visually heavy. A browser-only preference would disappear on reload and diverge from backend export, so route mode must be canonical.

## Design

- Add optional `edge.route.mode` with `orthogonal` and `straight`; absence remains orthogonal for backward compatibility.
- Reject canonical straight routes that also contain orthogonal waypoints.
- Keep route mode per edge. Palette mode selection controls the next edge; with an edge selected it also updates that edge.
- Initialize the next-edge mode through one centralized per-diagram default helper: straight for Use Case and orthogonal for Activity, BDD, and Custom. Opening an existing edge with no mode still displays orthogonal.
- Straight routing uses authored anchors when present and primitive-aware center-ray anchors otherwise. Its path contains exactly the source and target boundary points.
- Switching an edge to straight clears authored orthogonal waypoints in the same undoable edit while retaining anchors and label offset.
- Straight edges expose anchor and label controls but no orthogonal segment/corner controls. Switching back to orthogonal restores normal automatic/manual editing from the retained anchors.
- Backend markers use normalized first/last segment vectors so arrows, triangles, and diamonds align with diagonal paths.

## Included Work

- Extend schema, TypeScript types/runtime guard, normalizer, adapter round-trip, and validation tests.
- Preserve route mode through endpoint swap, reconnect, anchor reset, label movement, and orthogonal waypoint translation.
- Add shared straight-route fixtures and deterministic frontend/backend routing tests.
- Add palette and inspector mode controls plus next-edge defaults and selected-edge application.
- Update `FloatingEdge`, manual controls, backend SVG route selection, marker orientation, bounds, labels, and PNG-derived parity.
- Add browser coverage for Use Case default straight creation, selected-edge mode changes, waypoint cleanup/undo, save/reload, and render preview parity.
- Update canonical schema/mapping/rendering/frontend/per-type/decision docs and this slice's `## Outcome`.

## Not In Scope

- Curves, splines, freehand paths, obstacle avoidance, or automatic whole-diagram rerouting.
- Rewriting existing diagram files or committed examples to add route modes.
- A diagram-wide bulk conversion command or persisted global preference.
- Changing relationship semantics, line dashing, marker meaning, or endpoint cardinality validation.

## Target Areas

- `backend/assets/schemas/diagram.json`
- `backend/services/diagrams/rendering/diagram_render_service.py`
- `backend/tests/edge_routing_fixtures.json`
- `backend/tests/core/test_render_service.py`
- `backend/tests/core/test_validation_service.py`
- `frontend/src/types/diagram.ts` and `diagram.parity.test.ts`
- `frontend/src/adapters/reactFlow.ts` and tests
- `frontend/src/editor/lib/palette.ts` and tests
- `frontend/src/editor/lib/edgeRouting.ts` and tests
- `frontend/src/editor/canvas/FloatingEdge.tsx` and tests
- `frontend/src/editor/components/NodePalette.tsx`
- `frontend/src/editor/components/PropertyPanel.tsx` and component tests
- `frontend/src/editor/EditorPage.tsx`
- `frontend/e2e/smoke.spec.ts`
- Active schema/mapping/rendering/frontend/per-type/decision docs

## Exit Criteria

- The strict schema and frontend runtime guard accept only valid modes and reject straight routes with waypoints.
- Missing mode remains byte-stable and orthogonal; existing fixtures require no migration.
- New Use Case edges persist straight mode by default; new Activity, BDD, and Custom edges remain orthogonal.
- Palette and inspector changes are synchronized and undoable; route mode survives swap/reconnect/reset operations and preserves anchors/label offset while clearing incompatible waypoints.
- Straight edges render as one true boundary-to-boundary segment with correctly oriented markers and labels on canvas and SVG.
- Orthogonal routing and manual segment editing retain existing behavior and shared fixtures.
- Focused frontend/backend tests, full backend tests, and `npm run verify` pass.

## Previous Slice

- [`01-relationship-tools-and-diamond-targets.md`](01-relationship-tools-and-diamond-targets.md)

## Next Slice

- [`03-frontend-interaction-audit.md`](03-frontend-interaction-audit.md)

## Outcome

**Completion:** Added optional canonical `route.mode` with backward-compatible orthogonal fallback and straight-mode waypoint exclusion across the strict schema, TypeScript guard, adapter, route transforms, palette defaults, selected-edge palette/inspector controls, canvas edge renderer, backend SVG/PNG renderer, and shared parity fixtures. New Use Case relationships start straight; Activity, BDD, and Custom remain orthogonal. Straight routes retain anchors and label offsets, clear incompatible waypoints, expose no orthogonal segment/corner controls, and orient backend markers from normalized true segment vectors.

**Deviation:** No product-contract deviation. The implementation audit corrected a backend test that expected rectangular endpoints from use-case ellipse nodes, made edge selection in the route-mode browser test independent of the central label overlay, and added explicit route-mode preservation coverage for waypoint translation and anchor reset. Concurrent uncommitted LLM/readiness configuration, code, and test changes were preserved and excluded from this slice rather than overwritten or staged.

**Verification:** `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build/typecheck, 418 unit/component tests, and 42 Chromium E2E tests. `cd backend; uv run python manage.py test tests.core.test_render_service tests.core.test_validation_service` passed 111 affected tests. The full backend suite passed 848 tests with 5 skipped when the unrelated modified test modules were loaded in memory from `HEAD`, proving the connector slice independently; the earlier direct dirty-worktree run isolated its failures to those unrelated files. Browser coverage proves per-type next-edge defaults, selected-edge mode changes with undo/redo, waypoint cleanup, save/reload, and exact canvas/SVG straight-path parity. Three read-only implementation audits found no unresolved material production defect.

**Follow-up:** Slice 03 audits the complete frontend source/configuration and browser interaction matrix, including movement and persistence for every deduplicated authorable node identity.
