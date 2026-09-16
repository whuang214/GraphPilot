# Slice 01: Primitive Attachment Geometry

## Purpose

Make control-node and Actor relationship gestures follow the visible glyph rather than a distant or narrow full-node envelope, while preserving exact canonical anchors and canvas/SVG parity.

## Background

Browser diagnosis established two distinct failures:

- Initial/Final visible circles receive no handle hits because their interaction envelope surrounds the complete node-and-label box; at 76% zoom its narrowest band is only about 5.5 screen pixels.
- A sampled Actor node measured about 79×92 screen pixels while its visible figure measured about 26×35, leaving roughly 26.6 pixels of empty space on each side before the current relationship endpoint.

The Use Case ellipse already matches its visible boundary and remains unchanged.

## Design

- Introduce one primitive attachment-profile abstraction consumed by hover indication, connection start/end, reconnect, route rendering, and backend SVG projection.
- Project Initial, Activity Final, and Flow Final anchors to the rendered outer control circle; their labels remain outside attachment geometry.
- Project Actor anchors to a tight envelope derived from the rendered figure bounds, excluding the label region.
- Keep Use Case on its full visible ellipse; keep diamond, bar, and rectangular profiles unchanged.
- Separate the pointer hit halo from the exact projected endpoint: target acquisition is generous in screen space, while indicator and saved edge geometry remain on the visual boundary.
- The frontend attachment profile is runtime-only and has a mirrored deterministic backend projection helper; it introduces no persisted field or schema change.
- Preserve canonical `{side, offset}` route anchors. Existing diagrams need no migration, though their rendered control/Actor endpoints intentionally move closer to the glyph.

## Included Work

- Add frontend primitive-profile helpers and focused geometry tests.
- Replace control/Actor full-box curved handles with profile-aligned hit regions that remain usable from 50% through 150% zoom.
- Route hover, create, and reconnect through the profile without adding cardinal snapping yet.
- Mirror control and Actor profile projection in `DiagramRenderService`.
- Add canvas/SVG parity and realistic browser regression coverage.
- Update `editor-ui-design.md` (*Relationships and labels*), `03-rendering-design.md` (shared boundary projection), Activity/Use Case notation owners, `decision-decisions.md` (primitive-owned attachment geometry), and this slice's Outcome when implemented.

## Not In Scope

- Changing node dimensions, labels, notation, semantic identity, or palette membership.
- Use Case geometry changes.
- Target-node highlighting or cardinal aim-lock (Slice 02).
- New route fields or schema migration.
- Curved edge paths.

## Target Areas

- `frontend/src/editor/canvas/customNodes.tsx`
- `frontend/src/editor/lib/edgeRouting.ts` and focused tests
- `frontend/src/editor/EditorPage.tsx`
- `frontend/src/editor/canvas/FloatingEdge.tsx`
- `frontend/e2e/smoke.spec.ts`
- `backend/services/diagrams/rendering/diagram_render_service.py`
- `backend/tests/core/test_render_service.py`
- Active editor/rendering/per-type notation owners

## Exit Criteria

- Hovering within a 12-screen-pixel halo of a visible Initial/Final outer circle reveals an indicator projected to that circle at 50%, 76%, 100%, and 150% zoom.
- Actor endpoints and indicators follow a figure envelope that excludes the label and materially removes the diagnosed empty side gap.
- Use Case, diamond, bar, and rectangle attachment behavior is unchanged.
- Create and reconnect use the same profile and persist stable side/offset anchors.
- Existing saved anchors load without migration and render equivalently on canvas and SVG under the new profile.
- Focused frontend/backend tests, full backend tests, and `npm run verify` pass.

## Previous Slice

- [`../06-editor-simplification/06-explicit-route-editing.md`](../06-editor-simplification/06-explicit-route-editing.md)

## Next Slice

- [`02-connection-guidance.md`](02-connection-guidance.md)

## Outcome

**Completion:** Added one frontend attachment-profile resolver and a mirrored backend projection helper. Initial, Activity Final, and retained Flow Final now attach to their rendered outer circles; Actor attaches to the visible stick-figure envelope without its label; Use Case, diamond, bar, and box behavior remains unchanged. Hover/create/reconnect/render paths share the profile, canonical side/offset anchors remain migration-free, and legacy cardinal handle IDs remain compatible.

**Deviation:** Chromium delivered real pointer events through the original clipped annular handles to the SVG underneath even when `elementsFromPoint` reported the handle. The implementation therefore uses a bounded 16–48 perimeter/zoom-dependent set of ordinary sampled handles with a four-screen-pixel inward tolerance and twelve-screen-pixel outward reach. Only cardinal samples enter the tab order, and React Flow internals refresh only when the sample tier or profile geometry changes. The backend Actor drawing was aligned to the existing canvas figure geometry so SVG endpoints land on the same visible envelope; node boxes, labels, schema, and notation identity are unchanged.

**Verification:** `cd backend; uv run python manage.py test` passed 681 tests (4 skipped). `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build, 423 unit/component tests, and 36 Chromium E2E tests. Focused browser coverage verifies the 12-screen-pixel control halo at 50%, 76%, 100%, and 150% zoom plus control/use-case/Actor create, reconnect, save/reload, and server-SVG parity. Two read-only implementation audits found no remaining material issue.

**Follow-up:** Slice 02 owns the restored 20-screen-pixel target radius, valid-target decoration, and overridable cardinal aim-lock.
