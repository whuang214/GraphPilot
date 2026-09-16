# Slice 01: Minimal Edge Routing

## Purpose

Replace automatic obstacle avoidance and fan-out with predictable direct-first orthogonal routes while preserving editable manual geometry and canvas/SVG parity.

## Design

- Unrelated nodes never influence an automatic route.
- Compatible aligned anchors produce one direct segment with zero bends.
- Non-aligned automatic endpoints choose compatible boundary sides and the shortest stable one-bend path.
- Explicit anchors remain authoritative; the resolver uses the smallest orthogonal path that honors their endpoint approach.
- Persisted waypoints remain user-authored controls and may produce additional bends.
- Every displayed segment is draggable. Moving a direct segment creates the required detour; moving it back into alignment removes redundant waypoints.
- The selected-edge add-detour button, collision warning, shared trunks, and lane routing are removed.

## Included Work

- Simplify the shared frontend/backend route resolver and parity fixtures.
- Remove obstacle collection, collision scoring, fan-out compatibility, lanes, and blocked-route presentation.
- Extend segment editing to direct and endpoint-adjacent segments without changing route semantics.
- Preserve anchors, waypoint translation, reconnect behavior, label movement, undo/redo, save/reload, and reset controls.
- Update focused unit/backend/E2E tests and canonical routing documentation.

## Not In Scope

- Full-boundary connection creation; delivered in Slice 02.
- Curved, diagonal, freehand, or automatic whole-diagram routing.
- A per-edge routing mode or obstacle-avoidance toggle.
- Route schema changes.

## Target Areas

- `frontend/src/editor/lib/edgeRouting.ts` and tests.
- `frontend/src/editor/canvas/FloatingEdge.tsx`.
- `frontend/src/editor/components/PropertyPanel.tsx`.
- `backend/services/diagrams/rendering/diagram_render_service.py` and render tests.
- Shared routing fixtures and frontend E2E coverage.
- Canonical frontend, rendering, editor-design, decision, and delivery owners.

## Exit Criteria

- Aligned automatic anchors produce exactly one segment.
- Non-aligned automatic routes are deterministic and minimal, independent of unrelated nodes or edge order.
- A direct segment can be dragged into a manual detour without a separate add action.
- Straightening a manual route removes redundant bends and route overrides where appropriate.
- Existing manual anchors, waypoints, and label offsets survive round-trip and render equivalently in canvas/SVG/PNG.
- Relevant frontend/backend checks and browser coverage pass.

## Previous Slice

- [`../05-frontend-refinement/08-integrated-parity.md`](../05-frontend-refinement/08-integrated-parity.md)

## Next Slice

- [`02-boundary-connections.md`](02-boundary-connections.md)

## Outcome

**Completed.** Canvas and SVG now ignore unrelated nodes and edge-array order. Automatic endpoints align inside overlapping spans for a zero-bend segment; diagonal placements choose compatible sides and a stable one-bend path, while explicit incompatible anchors and authored waypoints remain authoritative. Selected edges expose a grip for every segment, including a direct segment that can be dragged into a persisted detour; the separate add button, blocked-route warning, obstacle corridors, shared trunks, and lane offsets are removed.

**Deviation.** Explicit user anchors can require more than one bend to preserve both boundary approach directions. This is deliberate manual geometry rather than an automatic routing mode; the canonical route schema is unchanged.

**Verification.** `cd frontend; npm run verify` passes lint, production build/typecheck, 390 unit tests, and 24 Playwright tests. `cd backend; uv run python manage.py test` passes 578 tests (3 skipped), including all 48 answer keys and shared route parity. `git diff --check` is clean.
