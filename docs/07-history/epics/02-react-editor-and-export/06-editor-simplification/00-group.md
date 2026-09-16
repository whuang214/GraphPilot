# Group: Editor Simplification (Epic 2 phase)

> This Epic 2 follow-on records the accepted simplification of routing, connection creation, and standalone entry behavior. Live cross-epic status belongs only in `../../00-current-state.md`; implementation evidence and deviations live in each slice's `## Outcome`.

## Goal

Make the editor predictable and document-focused: minimal user-directed relationship routes, boundary-native connection creation, and one quiet editor surface whether a diagram arrives from an IDE link or a local file.

## User Scenario

A user opens or starts a diagram, connects elements at the intended boundary positions, adjusts only the route segments that need manual placement, and edits without persistent transport/workspace labels or automatic routing surprises.

## Scope

- Replace obstacle-aware/fan-out routing with direct-first minimal orthogonal routing.
- Remove the selected-edge add-detour button; dragging a route segment creates or moves a detour and straightening collapses redundant bends.
- Start and finish new relationships anywhere along visible node boundaries while preserving exact normalized anchors.
- Keep node interiors available for move/select and preserve movable existing endpoints.
- Show a landing page for standalone entry with type-first blank creation, Open file, drag-to-open, reopenable Recents, and Clear recents.
- Open valid IDE `diagramPath` links directly in the editor.
- Remove workspace browsing and persistent source chips; expose available path/write/revision details only through an information popover.
- Require Save As for the first save of a blank diagram.

## Out of Scope

- Semantic-catalog or generation changes.
- Automatic obstacle avoidance, shared routing trunks, whole-diagram layout, or a per-edge automatic/manual mode.
- Persisting browser file handles across restarts.
- Project/workspace browsing in the standalone landing page.
- New diagram types, freeform drawing primitives, or schema changes to route geometry.

## Accepted Design

| Area | Intended behavior |
| --- | --- |
| Automatic routes | Use zero bends when compatible anchors align; otherwise choose the smallest stable orthogonal route that preserves endpoint approach. Unrelated nodes do not affect the path. |
| Manual routes | Every displayed segment can be dragged. Moving a direct segment creates a detour; normalization removes duplicate and redundant aligned bends. No separate add-detour button is shown. |
| Boundary connections | A narrow boundary hit area and hover indicator allow source and target placement along the complete visible perimeter. The exact side/offset persists in `edge.route`; node interiors remain draggable/selectable. |
| Standalone entry | No `diagramPath` shows the landing page. New blank asks for Activity, Use Case, BDD, or advanced Custom; Open file, file drop, reopenable Recents, and Clear recents remain. |
| IDE entry | A valid `diagramPath` bypasses the landing page and opens directly. Load failure remains explicit and recoverable. |
| Source presentation | The editor header shows no workspace/MCP/URL/file-origin chip. One information popover exposes only available filename/path, write state, unsaved/revision state, and copy path. |
| Persistence | Blank diagrams are browser-owned unsaved sessions and use Save As first. Persistent Recents contain only paths GraphPilot can reopen; clearing history never deletes files. |

## Slice Plan

1. [`01-minimal-edge-routing.md`](01-minimal-edge-routing.md) — **Complete — Minimal Edge Routing:** direct-first canvas/SVG routing, draggable segments without the add button, and parity coverage.
2. [`02-boundary-connections.md`](02-boundary-connections.md) — **Complete — Boundary Connections:** full-perimeter connection gestures, exact persisted anchors, and shape-aware attachment parity.
3. [`03-landing-and-source.md`](03-landing-and-source.md) — **Complete — Landing and Source:** standalone landing/new blank, clean header information, no workspace browser, and honest recents.
4. [`04-integration-audit-cleanup.md`](04-integration-audit-cleanup.md) — **Complete — Integration Audit Cleanup:** remove stale obstacle-routing internals and wording found by the cross-slice audit.
5. [`05-interaction-polish.md`](05-interaction-polish.md) — **Complete — Interaction Polish:** align source UI and connection affordances, then collapse bends made redundant by node movement.
6. [`06-explicit-route-editing.md`](06-explicit-route-editing.md) — **Complete — Explicit Route Editing:** supersede node-movement inference with safe click-to-delete corner pairs and Straighten route.

Slice numbers are local to this group. Canonical architecture/design owners are updated as accepted behavior is promoted and implemented; this group records delivery scope rather than replacing those owners.

## Dependencies

- The optional canonical `edge.route` anchor/waypoint/label contract.
- The existing `gpNode`, `FloatingEdge`, React Flow adapter, source-session lifecycle, and File System Access helpers.
- The backend SVG renderer and SVG-derived PNG export path.
- Existing validation-before-write and stale-source safeguards.

## Acceptance Criteria

- Automatic routes never react to unrelated nodes and use no redundant bend when endpoints align.
- A user can drag a direct or bent segment without first pressing an add button, and straightening removes redundant route geometry.
- Canvas and SVG render equivalent automatic/manual points, marker approaches, and label positions.
- A user can begin and finish a relationship along the visible boundary of every supported node primitive; exact anchors survive save/reload/export.
- Starting without a diagram shows New blank, Open file/drop, reopenable Recents, and Clear recents; no project list is shown.
- A valid IDE link opens directly, while every editor header remains transport-neutral and source details stay behind one information button.
- A blank diagram starts valid and unsaved, and its first save uses Save As.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 2 goal and phase plan.
- [`../05-frontend-refinement/00-group.md`](../05-frontend-refinement/00-group.md) — preceding refinement phase superseded where this group deliberately simplifies behavior.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — single live delivery-status board.
- [`../../../../01-architecture/02-frontend-architecture.md`](../../../../02-architecture/04-frontend.md) — frontend runtime and editor responsibilities.
- [`../../../../02-design-and-features/editor-ui-design.md`](../../../../03-design/12-editor-ui.md) — editor interaction and visual design owner.
- [`../../../../02-design-and-features/03-rendering-design.md`](../../../../03-design/06-rendering.md) — SVG/PNG rendering contract.
