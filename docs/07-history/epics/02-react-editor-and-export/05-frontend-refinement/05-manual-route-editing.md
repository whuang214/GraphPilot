# Slice 05: Manual Route Editing

## Purpose

Let users refine an automatic orthogonal connector by sliding its anchors, adding or moving waypoints, and repositioning relationship labels, while making it easy to return each override to automatic behavior.

## Design

- Selecting an edge exposes route controls without changing its semantic source or target.
- Source and target anchors slide along their node boundaries and persist as normalized perimeter positions, so resizing a node keeps the anchor attached.
- Users can add detours and move axis-constrained segments; edited segments remain orthogonal and normalization removes redundant waypoints.
- Supported relationship labels can move independently of the path and persist through the route contract.
- Dragging a segment near collision-free straight alignment snaps it back and removes redundant bends. Explicit route/anchor/label resets provide omission-based automatic behavior for every override.
- Reconnection discards or revalidates endpoint-specific geometry that no longer applies, rather than attaching stale overrides to a different node.
- One completed drag is one undo/redo step; selection-only and hover state never enter canonical JSON.

## Included Work

- Add selected-edge anchor, waypoint, segment, label, and reset affordances.
- Convert pointer movement between screen, flow, parented-node, and canonical diagram coordinates consistently.
- Persist route overrides through the Slice 03 contract and consume them in canvas/SVG route construction.
- Integrate route edits with undo/redo, dirty state, validation, clone, reconnect, save, and reload.
- Add keyboard-accessible removal/reset actions and clear visual distinction between automatic and manual geometry.
- Cover node resize/move, nested nodes, reconnect, snap-back thresholds, save/reload, and stale runtime-state exclusion.

## Not In Scope

- Diagonal, curved, spline, or freehand routes.
- Changing relationship semantics by dragging a route handle.
- Whole-diagram layout, edge bundling, or automatic persistence of derived paths.
- New labels beyond those already derived from canonical relationship data.

## Target Areas

- `frontend/src/editor/canvas/FloatingEdge.tsx` and route-edit overlays under `frontend/src/editor/canvas/`.
- `frontend/src/editor/lib/edgeRouting.ts` and route-edit helpers under `frontend/src/editor/lib/`.
- `frontend/src/editor/EditorPage.tsx` and `frontend/src/editor/components/PropertyPanel.tsx`.
- `frontend/src/adapters/reactFlow.ts` and undo/clone/reconnect tests.
- `backend/services/diagrams/rendering/diagram_render_service.py` and route-geometry render tests.

## Exit Criteria

- A user can slide either endpoint anchor without reconnecting the edge.
- A user can add a detour, move its segments, and reset waypoints while the displayed route remains orthogonal.
- Supported relationship labels can be moved independently and retain their positions after save/reload.
- Near-straight segment drag removes redundant bends; explicit route/anchor/label reset restores the corresponding automatic behavior.
- Reconnect, resize, node move, nested coordinates, undo/redo, clone, and validation preserve coherent geometry.
- Manual geometry renders equivalently on the canvas and in SVG/PNG, with no runtime fields in saved JSON.
- Interaction, adapter, rendering, and relevant verification checks pass.

## Previous Slice

- [`04-automatic-orthogonal-routing.md`](04-automatic-orthogonal-routing.md)

## Next Slice

- [`06-bdd-visual-cleanup.md`](06-bdd-visual-cleanup.md)

## Outcome

**Completed.** Selected edges expose draggable perimeter anchors, axis-constrained segment grips, an add-detour control, and independently draggable central/item-flow labels. One drag creates one undo snapshot; explicit Property-panel controls reset waypoints, anchors (including legacy handles), or label offset. Segment movement snaps near alignment and normalization removes duplicate/zero-length/monotonic-collinear bends; moving both endpoints or a shared parent translates manual waypoints, while moving one endpoint preserves them. Reconnection retains the canonical edge ID.

**Deviation.** Snap-back is applied to route segments, the accepted straightening case. Anchors and labels use explicit keyboard-operable reset actions rather than implicit near-default deletion; waypoint removal is the route reset rather than one delete button per point.

**Verification.** Pure routing tests cover detours, axis movement, reversal preservation, straightening, and translation. Playwright drags an anchor, segment, and label, saves, reloads, and confirms the same rendered path; backend SVG consumes the same manual fixture. Final aggregate gate evidence is recorded in Slice 08.
