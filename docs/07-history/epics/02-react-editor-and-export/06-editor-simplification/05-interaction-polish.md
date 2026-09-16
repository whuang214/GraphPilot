# Slice 05: Interaction Polish

## Purpose

Correct four post-delivery interaction defects: an awkward header information icon, a connection preview that starts at a strip midpoint instead of the clicked anchor, a zoom-displaced boundary indicator, and stale manual bends after node movement makes a route straight.

## Background

Slices 01–04 established minimal routing, full-boundary persisted anchors, and transport-neutral source UI. Live review confirmed that saved anchors are exact, but React Flow's temporary connection line still uses the center of the enlarged handle strip. The indicator separately mixes screen-scaled dimensions with node-local CSS coordinates. Route updates translate waypoints only when both endpoints move together and never remove a now-redundant detour after one node moves.

## Design

- Replace the Unicode information glyph with a 16×16 inline SVG (`viewBox="0 0 16 16"`, current-color circle plus dot/stem) inside a square `h-7 w-7 p-0` ghost button; retain the existing label, expansion state, focus ring, and popover behavior.
- Supply React Flow a custom `ConnectionLineComponentProps` component. It reads the captured primitive-projected start point from editor state, falls back to `fromX/fromY` only before capture, and draws the temporary path to `toX/toY`; completion/cancel clears that state.
- Convert pointer X/Y from `getBoundingClientRect()` proportions into `offsetWidth`/`offsetHeight` node-local coordinates before boundary projection and indicator CSS placement.
- Add `removeStraightRouteWaypoints(route, sourceRect, targetRect): RouteGeometry | undefined`. It resolves the authored route and a copy without `waypoints`; only when both normalize to zero bends does it remove `waypoints`, preserving source/target anchors and label offset (or omitting the route only when no fields remain).
- Integrate simplification in `handleNodesChange` after computing post-move absolute endpoint rectangles. Translate waypoints first when both endpoints/shared parent move equally; otherwise evaluate the moved endpoint geometry without shifting meaningful controls.

## Included Work

- Add exact-start connection preview state/component; in Playwright, hold a boundary drag and compare the preview path's first coordinate with the projected clicked anchor before mouse-up.
- Correct boundary-indicator coordinate conversion; at a programmatically set non-100% React Flow zoom, compare indicator center with the expected projected boundary point within a two-pixel screen tolerance.
- Add the pure route-waypoint simplifier with unit cases for redundant direct alignment, preserved non-redundant detours, and preservation of anchors/label offset.
- Add a browser regression fixture with one manual detour, drag one endpoint into alignment, save, and assert `waypoints` are omitted; retain an adjacent non-straight fixture assertion.
- Restyle and test the information trigger without changing popover content or source behavior.
- Update canonical editor/routing documentation and delivery status where behavior changes.

## Not In Scope

- Relationship semantics, endpoint reversal, routing modes, or obstacle avoidance.
- Changing canonical `edge.route` fields.
- Persisting calculated automatic geometry.
- Workspace browser/public API removal.
- Source-session, generation, readiness, or vocabulary changes.

## Target Areas

- `frontend/src/editor/shell/TopBar.tsx` and tests.
- `frontend/src/editor/canvas/customNodes.tsx` and tests.
- `frontend/src/editor/EditorPage.tsx`.
- `frontend/src/editor/lib/edgeRouting.ts` and tests.
- `frontend/e2e/smoke.spec.ts`.
- `docs/01-architecture/02-frontend-architecture.md` and `docs/02-design-and-features/editor-ui-design.md` if clarification is needed.

## Exit Criteria

- The information trigger is compact, aligned, and accessible next to diagram identity.
- During connection drag, the visible line begins at the same projected boundary point later persisted as the source anchor.
- At non-100% zoom, the hover indicator remains centered on the resolved boundary point.
- Moving one endpoint into straight alignment removes redundant waypoints automatically; meaningful manual bends remain.
- Anchor, label-offset, semantic, save/reload, reconnect, and canvas/SVG parity tests remain green.
- The implementation audit finds no material regression or scope drift.
- Full frontend and backend gates pass.

## Previous Slice

- [`04-integration-audit-cleanup.md`](04-integration-audit-cleanup.md)

## Next Slice

- End of Epic 2's `06-editor-simplification/` group.

## Outcome

**Completed.** The header now uses a compact aligned inline-SVG information trigger. The boundary indicator converts screen proportions into unscaled node-local coordinates, so it remains on the resolved outline at non-100% zoom. A custom React Flow connection line starts at the same primitive-projected point captured for persisted source anchors rather than the center of the full-side handle strip.

**Routing.** `removeStraightRouteWaypoints` removes only waypoints when both the authored and waypoint-free routes resolve with zero bends, preserving anchors and label offset. Node movement translates waypoints when both endpoints/shared parents move together, reevaluates single-end movement, and performs a final drag-stop simplification; meaningful detours remain unchanged.

**Audits.** The first plan audit blocked commit until the SVG, preview-state, zoom-test, and simplifier contracts were explicit; the revised plan passed re-audit. The implementation audit found no blockers, high-severity findings, debug output, schema drift, or unrelated scope.

**Verification.** `cd frontend; npm run verify` passes lint, production build/typecheck, 401 unit tests, and 28 Playwright tests. `cd backend; uv run python manage.py test` passes 660 tests (3 skipped), including the 62-test render suite. `git diff --check` is clean.
