# Slice 06: Explicit Route Editing

## Purpose

Replace node-movement waypoint inference with explicit, orthogonality-safe route controls: click-to-delete corner pairs and Straighten route.

## Background

Live review after Slice 05 showed that deleting waypoints when node movement happens to create a straight route remains unreliable and obscures user intent. A true orthogonal corner also cannot simply disappear when its neighboring points are diagonal; it must either move to the alternate elbow or be removed as part of a larger detour.

## Design

- Node movement updates attached endpoint geometry but never deletes or relocates authored waypoints.
- Segment dragging remains the only conservative automatic simplification gesture: deliberate alignment may collapse duplicate/collinear points.
- `deleteOrthogonalDetour(points: Pt[], segmentIndex: number): Pt[]` uses a zero-based segment index for `points[i] → points[i+1]`. Only non-endpoint segments whose two endpoint points are bends and have a safe reconnection candidate are deletable; invalid or unsafe indices return the original array and render no delete affordance. Remove those two bend points, reconnect outer points `points[i-1]`/`points[i+2]` directly when aligned or through one L candidate otherwise, and normalize the whole route. A candidate is safe only when it preserves both directed terminal approach segments and introduces no new 180-degree reversal; score safe L candidates by total resulting bend count, then Manhattan length, then lexicographic candidate coordinate for a stable tie.
- `deletableDetourSegmentForCorner(points, cornerIndex)` maps either endpoint corner of a safe detour to that same segment. Both corners show focusable diamond buttons; one click, Enter/Space, or focused Delete/Backspace calls `routeEdit.start()` once and deletes the paired turns. Segment squares remain drag-only. Corner flipping is retired because serializing a flipped resolved elbow can create a reversal and increase visible turns.
- The inspector action is named **Straighten route**. It removes all authored `waypoints`, preserves source/target anchors and label offset, and returns to minimal automatic geometry through the existing one-snapshot edge-patch path.
- Every action stores only normalized user-owned route geometry; empty interior point lists become `waypoints: undefined` and normalize to route omission when no other override remains.

## Included Work

- Remove Slice 05's node-movement waypoint-deletion inference while preserving equal endpoint/shared-parent waypoint translation.
- Add the pure corner/detour helpers plus exported bend/deletable-segment predicates so FloatingEdge renders controls only where actions are valid.
- Place delete diamonds at both corners bordering each safe detour and retain drag-only square grips at segment midpoints; endpoint/label drag controls remain unchanged and control titles/ARIA distinguish Move segment from Delete detour.
- Wire single-click and keyboard handlers directly on focused corner controls, stopping canvas shortcuts; each activation invokes the existing route-edit `start()` then `setRoute()` exactly once.
- Rename Reset route to Straighten route and retain independent Auto anchors/Reset label actions.
- Add unit cases for mapping both bordering corners to one safe detour, invalid index/non-bend no-op, direct and minimal-L detour deletion, deterministic tie choice, non-deletable endpoint segments, and normalization. Add component assertions for click/key labels and Straighten preservation; browser coverage moves a node without waypoint deletion, then exercises corner deletion, Undo, Straighten, save/reload, and server-SVG parity.
- Backend rendering needs no algorithm change: it already consumes persisted normalized waypoints; existing shared render/parity tests plus the browser server-SVG assertion prove parity.
- Update canonical editor/routing design and delivery status.

## Not In Scope

- Diagonal, curved, spline, or freehand segments.
- Automatic obstacle routing or node-movement route inference.
- Endpoint reversal or relationship-semantic changes.
- Canonical route schema changes.
- Persisting calculated automatic paths.
- Source-session, landing, generation, readiness, or vocabulary changes.

## Target Areas

- `frontend/src/editor/lib/edgeRouting.ts` and tests.
- `frontend/src/editor/canvas/FloatingEdge.tsx` and focused tests.
- `frontend/src/editor/EditorPage.tsx`.
- `frontend/src/editor/components/PropertyPanel.tsx` and component tests.
- `frontend/e2e/smoke.spec.ts`.
- `docs/01-architecture/02-frontend-architecture.md` capability wording, `docs/02-design-and-features/editor-ui-design.md` relationship interaction contract, and the indexed routing decision in `docs/02-design-and-features/decision-decisions.md`.

## Exit Criteria

- Moving one connected node preserves authored waypoints exactly.
- Clicking either corner bordering a valid detour removes the same paired turns, and one Undo restores them.
- Corner deletion yields a normalized direct/minimal-L route; required one-bend routes remain and unsafe deletions expose no control.
- Straighten route removes only waypoints and preserves anchors and label offset.
- Pointer and keyboard controls are labelled, focusable, and perform one action per activation.
- Save/reload and SVG export preserve each resulting route.
- The implementation audit finds no material regression, ambiguous control, or scope drift.
- Full frontend and backend gates pass.

## Previous Slice

- [`05-interaction-polish.md`](05-interaction-polish.md)

## Next Slice

- [`../07-editor-usability/01-primitive-attachment-geometry.md`](../07-editor-usability/01-primitive-attachment-geometry.md)

## Outcome

**Completion:** Removed node-movement waypoint deletion; selected routes now expose labelled, focusable safe delete-corner controls, while the inspector exposes Straighten route. Each pointer/keyboard action takes one undo snapshot, normalized geometry survives save/reload, and server SVG output matches the canvas.

**Deviation:** Implementation evidence first limited terminal-adjacent flips and unsafe near-terminal detour reconnections. Live use then showed that even an interior Flip corner could serialize a resolved elbow into a 180-degree backtrack and that an unlabeled diamond read naturally as delete. The correction retires Flip corner: either diamond bordering a safe detour now deletes the segment and paired turns on one click, while preserving both directed terminal segments and rejecting new reversals. Anchors, labels, schema, and semantics remain unchanged.

**Verification:** `npm --prefix frontend run verify` passed lint with 0 warnings/errors, production build, 406 unit/component tests, and 29 Chromium E2E tests. `cd backend; uv run python manage.py test tests.core.test_render_service` passed 62 render/parity tests, and an explicit sweep of all tracked backend test modules passed 639 tests (3 skipped). Standard working-tree discovery additionally surfaced 4 failures and 1 error only in concurrent untracked readiness-calibration tests outside this slice; none of those files are staged here.

**Correction verification:** The corner-delete follow-up passed the exact reported-route unit regression, component coverage for click/Delete/Backspace/double-click guarding, native-Enter browser activation, save/reload/server-SVG parity, and the full frontend gate: lint 0 warnings/errors, production build, 407 unit/component tests, and 29 Chromium E2E tests.

**Parallel-edge correction:** Replaced React Flow's duplicate-suppressing `addEdge` path with explicit edge insertion so repeated same-pair gestures survive with independent UUIDs and anchors. Typed diagrams retain draft edges and validate semantic cardinality; `custom` leaves parallel relationships unrestricted. Activity Fork/Join minimums count distinct opposite endpoints, preventing duplicate edges from satisfying semantic branching or synchronization.

**Parallel-edge verification:** The exact Fork-to-same-target browser regression saves three independent edges with distinct authored anchors. The full gates pass: backend 679 tests (3 skipped), frontend 411 unit/component tests and 33 Chromium E2E tests, lint 0 warnings/errors, and production build.

**Follow-up:** Epic 2 editor simplification has no remaining route-editing follow-up.
