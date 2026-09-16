# Group: Editor Connectors and Audit (Epic 2 phase)

> This Epic 2 follow-on consolidates connector tools, adds explicit straight routing, closes a diamond-boundary interaction defect, and re-audits the complete frontend interaction surface. Live cross-epic status belongs only in `../../00-current-state.md`; implementation evidence and deviations belong in each slice's `## Outcome`.

## Goal

Make relationship authoring visually coherent and directly editable from the palette, support both straight and orthogonal connectors without canvas/SVG drift, and verify the complete editor interaction surface against every authorable node type.

## User Scenario

A user finds all relationships together, selects an existing edge and changes its relationship or route mode from the same tool tray, connects exact diamond vertices without accidentally moving the node, chooses straight lines for Use Case diagrams, and can move/save/reload every authorable node reliably.

## Scope

- Consolidate the active scope's relationship tools into one palette tray rather than repeating relationship sections inside shape groups.
- Apply a palette relationship choice to the selected edge through the existing semantic transition while retaining it as the next-edge tool.
- Make all four exact diamond cardinal vertices reliable source and target hit areas without changing canonical anchor projection.
- Add canonical per-edge `orthogonal` and `straight` route modes with frontend/backend rendering parity.
- Keep missing route mode orthogonal for compatibility; initialize new Use Case edges as straight and other new edges as orthogonal.
- Re-audit frontend source, configuration, tests, and browser interactions, including moving every authorable node type and preserving positions through save/reload.

## Out of Scope

- Curved, freehand, spline, or obstacle-avoiding connectors.
- Migrating existing edges or rewriting committed example diagrams to straight mode.
- New node/relationship semantics, diagram types, or backend authoring profiles.
- Automatic whole-diagram layout or a diagram-wide bulk route conversion.
- Unrelated Epic 3 generation/evaluation work.

## Accepted Design

| Area | Intended behavior |
| --- | --- |
| Relationship tray | One relationship tray sits below palette scope/organization controls. Scope and search still filter its catalog-derived choices; shape groups contain shapes only. |
| Selected-edge action | With an edge selected, a relationship click applies the existing safe identity transition and also updates the next-edge tool. Without an edge selected, it only updates the next-edge tool. |
| Diamond targets | Zoom-stable cardinal hit targets overlap the existing diagonal bands at top/right/bottom/left. Indicator, preview, and persisted anchors still project to the exact diamond boundary. |
| Route contract | Optional `edge.route.mode` is `orthogonal` or `straight`; absence means orthogonal. Straight mode excludes orthogonal waypoints. |
| Route tools | Orthogonal/Straight appears in the palette connector tray and the selected edge's Appearance route section. Palette behavior mirrors relationship behavior: selected edge plus next-edge state, or next edge alone. |
| Defaults | Existing edges remain orthogonal when mode is absent. New Use Case edges start straight; Activity, BDD, and Custom start orthogonal. |
| Rendering | Straight paths use primitive-aware boundary anchors and true segment vectors for markers. Canvas, SVG, labels, anchors, save/reload, and export remain in parity. |
| Audit | The audit covers all frontend source/configuration/E2E plus a browser matrix over all 17 deduplicated authorable node identities (19 profile entries with shared Note), every route/relationship tool family, save/reload, selection, movement, containment, and console/network evidence. |

## Slice Plan

1. [`01-relationship-tools-and-diamond-targets.md`](01-relationship-tools-and-diamond-targets.md) — **Complete, audited, and verified — Relationship Tools and Diamond Targets:** consolidated relationship choices, selected-edge application, and cardinal diamond targets.
2. [`02-straight-and-orthogonal-routing.md`](02-straight-and-orthogonal-routing.md) — **Complete, audited, and verified — Straight and Orthogonal Routing:** added the canonical route mode, palette/inspector controls, and canvas/SVG parity.
3. [`03-frontend-interaction-audit.md`](03-frontend-interaction-audit.md) — **Complete, audited, and verified — Frontend Interaction Audit:** audited all frontend code and browser interactions, moved every authorable node, addressed in-scope findings, and recorded the remaining narrow-window policy gap.

Slice numbers are local to this group. Canonical architecture/design owners describe the accepted final system; this group and the current-state board distinguish implementation progress.

## Dependencies

- Catalog-driven relationship tools and semantic transitions from `07-editor-usability` S04–S05.
- Primitive-owned attachment geometry and soft cardinal aim-lock from `07-editor-usability` S01–S02.
- Canonical route anchors/waypoints, manual segment editing, and canvas/SVG parity from `06-editor-simplification`.
- The strict diagram schema, frontend runtime guard, React Flow adapter, and backend `DiagramRenderService`.
- Existing Vitest and Playwright infrastructure with temporary `.graphpilot` workspaces.

## Acceptance Criteria

- Every active relationship choice appears once in one palette tray and remains searchable/scoped.
- Clicking a relationship while an edge is selected updates that edge cleanly and retains the choice for the next edge.
- Exact top/right/bottom/left diamond vertices start and finish connections without moving the node.
- Straight and orthogonal modes round-trip canonically and render equivalently on canvas and SVG; existing missing-mode edges remain orthogonal.
- New Use Case edges default to straight while other diagram types remain orthogonal.
- Straight mode has no stale orthogonal waypoint behavior; undo restores a cleared route-mode transition.
- Browser coverage moves all 17 unique authorable node identities and proves saved/reloaded positions.
- The full frontend gate and affected backend gate pass; all audit findings are fixed or explicitly reported with evidence and scope.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 2 goal and phase plan.
- [`../07-editor-usability/00-group.md`](../07-editor-usability/00-group.md) — preceding observed-usability phase.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — single live delivery-status board.
- [`../../../../01-architecture/02-frontend-architecture.md`](../../../../02-architecture/04-frontend.md) — frontend runtime and editor responsibilities.
- [`../../../../02-design-and-features/00-diagram-json-schema.md`](../../../../03-design/03-diagram-json-schema.md) — canonical route contract.
- [`../../../../02-design-and-features/01-diagram-json-mapping-design.md`](../../../../03-design/04-diagram-json-mapping.md) — React Flow route mapping.
- [`../../../../02-design-and-features/03-rendering-design.md`](../../../../03-design/06-rendering.md) — canvas/SVG route parity.
- [`../../../../02-design-and-features/editor-ui-design.md`](../../../../03-design/12-editor-ui.md) — palette and connector interaction design.
- [`../../../../02-design-and-features/decision-decisions.md`](../../../../05-delivery/04-decisions.md) — active design decisions.
