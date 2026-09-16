# Slice 02: Connection Guidance

## Purpose

Make relationship targeting obvious and forgiving while retaining exact custom boundary placement.

## Background

GraphPilot currently sets `connectionRadius={12}` rather than React Flow's 20-pixel default. Browser diagnosis found a target valid at 4–8 pixels but not 12–20 pixels; the valid handle had `connectingto valid` state but approximately 0.001 opacity and the node received no outline. Anchor resolution currently projects the exact pointer with no cardinal snap.

## Design

- Restore a 20-screen-pixel connection radius.
- Use React Flow connection state to decorate only the current valid target node and active boundary band; do not highlight the source, self-loop, or invalid target.
- Add a pure shared anchor resolver that optionally snaps to the four cardinal centers when the projected pointer is within 8 screen pixels.
- Apply the resolver consistently to hover indication, preview start, create end, and reconnect end.
- Moving outside the snap radius immediately restores the exact custom point. No mode, toggle, modifier requirement, or persisted preference is introduced.
- Give snapped cardinal feedback a subtle distinction without obscuring the general target highlight.

## Included Work

- Add target-decoration state/CSS and expose valid connection feedback at every supported primitive.
- Restore the connection radius and verify target acquisition around rectangular, diamond, curved, and container boundaries.
- Add zoom-aware cardinal snap helpers and pure tests.
- Integrate snap resolution into creation and reconnection without changing route storage.
- Add browser coverage for target highlight, self-loop rejection, cardinal snap, custom override, save/reload, and zoom behavior; rerun backend route-projection parity only if the persisted resolver changes shared output.
- Update `editor-ui-design.md` (*Relationships and labels*), `decision-decisions.md` (soft cardinal aim-lock), and this slice's Outcome when implemented.

## Not In Scope

- Grid snapping, node alignment changes, automatic route layout, or magnetic route segments.
- Snapping to corners or arbitrary evenly spaced points.
- Persistent snap settings or per-edge route modes.
- Semantic connection restrictions beyond the existing self-loop rule.

## Target Areas

- `frontend/src/editor/EditorPage.tsx`
- `frontend/src/editor/canvas/customNodes.tsx`
- `frontend/src/editor/lib/edgeRouting.ts` and focused tests
- `frontend/src/index.css`
- `frontend/e2e/smoke.spec.ts`
- Active editor interaction/decision owners

## Exit Criteria

- A valid target becomes visually obvious before the pointer reaches its exact boundary; invalid/self targets do not receive valid styling.
- Dropping within the 20-pixel radius creates the relationship and preserves the primitive-projected endpoint.
- Pointers within 8 screen pixels of top/right/bottom/left center persist an exact cardinal anchor; pointers outside persist their custom point.
- Hover, preview, create, and reconnect agree at every zoom covered by browser tests.
- Existing exact custom anchors remain editable and unchanged unless the user performs a new gesture.
- Focused tests and `npm run verify` pass.

## Previous Slice

- [`01-primitive-attachment-geometry.md`](01-primitive-attachment-geometry.md)

## Next Slice

- [`03-container-layering.md`](03-container-layering.md)

## Outcome

**Completion:** Restored React Flow's 20-screen-pixel connection radius, made the current valid target node and active boundary band visible, and added one pure zoom-aware resolver for hover, source preview, creation, and reconnection. Visual cardinal centers softly snap within 8 screen pixels; pointers immediately outside retain exact custom anchors. Existing saved anchors remain untouched until a gesture edits them.

**Deviation:** Target decoration consumes React Flow's emitted `connectingto valid` classes through scoped CSS rather than duplicating connection state in editor React state. Stable `data-attachment-*` metadata identifies sampled handles for integration coverage, while only the existing cardinal handles remain in the tab order. No backend, schema, route-storage, or preference change was needed.

**Verification:** `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build, 425 unit/component tests, and 37 Chromium E2E tests. Browser coverage proves self-target rejection, valid-only outline/band feedback, a successful drop 19 pixels outside the visible boundary, exact cardinal preview/create/reconnect output, custom override at 76% zoom, unchanged existing custom anchors, and save/reload persistence. A read-only implementation audit found no functional blocker; its selector and non-100%-zoom follow-ups were addressed before the full gate.

**Follow-up:** Slice 03 owns display-only container z tiers and preservation of explicit drag-to-contain behavior.
