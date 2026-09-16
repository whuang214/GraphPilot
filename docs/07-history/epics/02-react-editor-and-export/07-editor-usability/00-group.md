# Group: Editor Usability (Epic 2 phase)

> This Epic 2 follow-on converts observed browser-editing friction into six bounded usability slices. Live cross-epic status belongs only in `../../00-current-state.md`; implementation evidence and deviations belong in each slice's `## Outcome`.

## Goal

Make common editor actions easy to discover and forgiving to execute without weakening exact diagram semantics, canonical persistence, or canvas/SVG parity.

## User Scenario

A user starts the right diagram from a scalable chooser, finds shapes and relationships in a structured palette, connects visible primitives without pixel-perfect targeting, layers a System Boundary behind existing nodes, and edits relationship identity from the primary inspector tab.

## Scope

- Align Initial/Final control and Actor attachment geometry with their visible glyphs while retaining exact persisted anchors.
- Highlight valid nearby relationship targets and softly snap attachment points to the four cardinal positions.
- Keep System Boundary containers behind ordinary nodes without automatically changing containment.
- Expose catalog-supported relationships in every applicable typed palette.
- Move relationship identity editing into the Content tab.
- Organize the shape palette by diagram family or notation, with current/all scope and unified search.
- Replace one landing-page card per diagram type with a scalable searchable New Diagram chooser.

## Out of Scope

- New diagram types, node/edge semantics, schema fields, or backend authoring profiles.
- Automatic containment when a System Boundary is added around existing Use Cases.
- General arbitrary z-order authoring, persisted z-index, or a full Layers panel.
- Magnetic route segments, grid snapping, automatic layout, or obstacle avoidance.
- Changing the Actor or control-node notation itself.
- Diagram/notation grouping in the New Diagram chooser; that control belongs only to the shape palette.

## Accepted Design

| Area | Intended behavior |
| --- | --- |
| Primitive attachment | Initial, Activity Final, and Flow Final attach to their visible outer circles. Actor attaches to a tight figure envelope that excludes its label. Use Case remains attached to its visible ellipse. A generous screen-space halo aids targeting, but the indicator and persisted endpoint project to the exact visual boundary. |
| Target guidance | React Flow's 20-pixel connection radius is restored. The valid nearby target and active boundary band become visibly highlighted while self/invalid targets do not. |
| Cardinal aim-lock | Hover, create, and reconnect share an 8-screen-pixel soft snap to top/right/bottom/left center. Moving outside the snap radius restores exact custom placement; no mode or persisted setting is introduced. |
| Container layering | Containers remain below ordinary nodes even when selected, matching the SVG renderer. Adding a System Boundary never changes `parentId`; containment remains an explicit node-drag action. |
| Relationship tools | The element catalog drives the next-relationship choices for Activity, Use Case, BDD, and Custom. Note incidence still forces Comment Link. Relationship identity is editable from Content. |
| Palette organization | The shape palette has Current diagram/All authorable scope and Diagram/Notation organization. Diagram mode uses Shared, Activity, Use Case, BDD, and Custom-only groups without duplicating semantics; both nodes and relationships participate in search. |
| New Diagram | One New diagram action opens a searchable, scrollable type chooser backed by centralized diagram-type descriptors. Open/drop/Recents/error recovery remain unchanged. |

## Slice Plan

1. [`01-primitive-attachment-geometry.md`](01-primitive-attachment-geometry.md) — **Complete, audited, and verified — Primitive Attachment Geometry:** control/Actor hit and projection geometry follows visible glyphs in canvas and SVG.
2. [`02-connection-guidance.md`](02-connection-guidance.md) — **Complete, audited, and verified — Connection Guidance:** valid-target highlighting, restored target radius, and overridable cardinal aim-lock.
3. [`03-container-layering.md`](03-container-layering.md) — **Complete, audited, and verified — Container Layering:** System Boundaries remain behind existing nodes without implicit containment.
4. [`04-relationship-authoring.md`](04-relationship-authoring.md) — **Complete, audited, and verified — Relationship Authoring:** catalog-driven relationship tools and primary-tab relationship identity.
5. [`05-palette-organization.md`](05-palette-organization.md) — **Complete, audited, and verified — Palette Organization:** current/all scope, diagram/notation organization, and unified search.
6. [`06-new-diagram-chooser.md`](06-new-diagram-chooser.md) — **Complete, audited, and verified — New Diagram Chooser:** scalable searchable blank-diagram selection.

Slice numbers are local to this group. Canonical architecture/design owners are updated only when each accepted behavior is implemented; this group records delivery scope rather than replacing those owners.

## Dependencies

- The existing element catalog and bounded authoring profiles delivered by Epic 1 `04-universal-vocabulary`.
- Canonical `edge.route` side/offset anchors and explicit route controls from `06-editor-simplification` S01, S02, and S06.
- React Flow connection state, node z-index behavior, and source/target handles.
- Existing explicit drag-to-contain `parentId` behavior from Epic 2 renderer/authoring slices.
- The three-tab property panel from `05-frontend-refinement` S07, source session lifecycle, File System Access helpers, and blank-diagram factory.

## Acceptance Criteria

- Control and Actor relationships attach near the visible glyph at common zoom levels while exact anchors survive save/reload/export.
- A valid nearby connection target is obvious, cardinal centers snap lightly, and custom attachment remains available immediately outside the snap radius.
- A newly added or selected System Boundary cannot block moving existing nodes and never silently changes containment.
- Every typed palette exposes its allowed relationships, and selected edge identity is editable from Content.
- The palette can be scoped and organized by diagram or notation without exposing non-authorable specialist identities.
- New blank creation remains fast with the current four types and scales through search rather than adding more landing-page buttons.
- Relevant focused tests, backend parity tests, `npm run verify`, and `uv run python manage.py test` pass at the slices that affect them.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 2 goal and phase plan.
- [`../06-editor-simplification/00-group.md`](../06-editor-simplification/00-group.md) — preceding editor simplification phase.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — single live delivery-status board.
- [`../../../../01-architecture/02-frontend-architecture.md`](../../../../02-architecture/04-frontend.md) — frontend runtime and editor responsibilities.
- [`../../../../02-design-and-features/editor-ui-design.md`](../../../../03-design/12-editor-ui.md) — editor interaction and visual design owner.
- [`../../../../02-design-and-features/03-rendering-design.md`](../../../../03-design/06-rendering.md) — canvas/SVG attachment parity.
- [`../../../../02-design-and-features/decision-decisions.md`](../../../../05-delivery/04-decisions.md) — active design decisions.
