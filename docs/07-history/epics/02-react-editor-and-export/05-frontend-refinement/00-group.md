# Group: Frontend Refinement (Epic 2 phase)

> This Epic 2 follow-on records the accepted frontend-refinement behavior and its delivery slices. Live cross-epic status belongs only in `../../00-current-state.md`; implementation evidence and deviations live in each slice's `## Outcome`.

## Goal

Deliver the approved frontend refinement design: one coherent source session, correct BDD notation, editable orthogonal relationship routes, a denser BDD editing experience, and matching canvas, SVG, and PNG output.

## User Scenario

A user opens a workspace or external diagram, refines BDD structure and relationship presentation without fighting the editor, saves to the correct source, and exports an image that preserves the canvas geometry and notation.

## Scope

- Unify workspace-path and external-file state behind one source-session lifecycle, including automatic repository matching when the match is unambiguous.
- Correct BDD relationship markers before extending route behavior.
- Add backward-compatible optional route geometry for anchors, waypoints, and moved relationship labels.
- Route automatic connectors orthogonally around obstacles, share trunks only for compatible aligned groups, and keep incompatible relationships in compact separate lanes.
- Support sliding endpoint anchors, manual waypoints, movable labels, and snap-back to automatic geometry.
- Render empty BDD classifiers as compact header-only blocks while retaining full feature compartments when populated.
- Add common BDD relationship presets and reorganize the property panel into three tabs with compact structured-data rows.
- Keep the React canvas, canonical SVG, and SVG-derived PNG in behavioral parity.

## Out of Scope

- New diagram types, semantic element identities, or freeform drawing primitives.
- Whole-diagram auto-layout, curved/freehand connectors, or automatic semantic inference.
- Continuous filesystem watching, real-time collaboration, automatic conflict merging, or database persistence; focus-based refresh and revision-safe save conflicts are included.
- PDF export or a second rendering pipeline.
- Claims that any slice is implemented before its outcome and verification are recorded.

## Accepted Design

| Area | Intended behavior |
| --- | --- |
| Source sessions | URL, Browse, recent, and picker-resolved repository diagrams become one workspace-owned session. One unambiguous picker match switches automatically to the current workspace path; unmatched files remain external. Workspace revisions refresh clean sessions on focus and block stale overwrites. |
| BDD markers | Generalization, containment, navigability, shared aggregation, and composition adorn the semantic relationship end and remain correctly oriented and unclipped. |
| Route contract | Route geometry is optional. Its absence selects automatic routing; persisted geometry contains only user overrides such as anchors, waypoints, or moved label positions. |
| Automatic routing | Connectors use deterministic obstacle-aware orthogonal paths. Compatible aligned groups may share a trunk; incompatible groups use deterministic compact lanes near the side center. |
| Manual routing | Endpoint anchors slide on node boundaries, waypoints remain orthogonal, labels can move, and returning an override near its automatic position snaps back and removes that override. |
| BDD nodes | A classifier with no visible features is a compact header-only block; populated classifiers show only their non-empty derived compartments. |
| BDD editing | Presets configure canonical relationship semantics and association-end data rather than inventing new edge types. Three property tabs and compact rows expose common and structured fields without changing their meaning. |
| Parity | Canvas and SVG consume the same canonical geometry and notation rules; PNG remains a rasterization of that SVG. |

## Slice Plan

1. [`01-source-state-and-sync.md`](01-source-state-and-sync.md) — **Complete — Source State and Sync:** unified source sessions, save targeting, URL/UI synchronization, and unambiguous repository matching.
2. [`02-bdd-marker-correctness.md`](02-bdd-marker-correctness.md) — **Complete — BDD Marker Correctness:** correct semantic ends, orientation, and marker references.
3. [`03-route-contract.md`](03-route-contract.md) — **Complete — Route Contract:** optional, validated, byte-stable route geometry on canonical edges.
4. [`04-automatic-orthogonal-routing.md`](04-automatic-orthogonal-routing.md) — **Complete — Automatic Orthogonal Routing:** obstacle avoidance, compatible fan-in/fan-out, and compact incompatible lanes.
5. [`05-manual-route-editing.md`](05-manual-route-editing.md) — **Complete — Manual Route Editing:** editable anchors, detours/segments, labels, reset, and snap-back.
6. [`06-bdd-visual-cleanup.md`](06-bdd-visual-cleanup.md) — **Complete — BDD Visual Cleanup:** compact empty classifiers and populated compartment fidelity.
7. [`07-relationship-presets-and-properties.md`](07-relationship-presets-and-properties.md) — **Complete — Relationship Presets and Properties:** BDD presets and the compact three-tab inspector.
8. [`08-integrated-parity.md`](08-integrated-parity.md) — **Complete — Integrated Parity:** source/canvas/SVG/PNG parity, full frontend audit, and aggregate verification.

Slice numbers are local to this group. Canonical design owners are updated when a slice promotes or implements the accepted behavior; this group records delivery scope rather than replacing those owners.

## Dependencies

- The canonical GraphPilot diagram schema and React Flow adapter.
- The existing `gpNode`, `FloatingEdge`, property panel, source-opening flows, and undo/redo history.
- The backend SVG renderer and its SVG-derived PNG paths.
- BDD notation and semantic relationship data from the shared element catalog.

## Acceptance Criteria

- Workspace and external opens produce one coherent source session and always save to the intended target.
- BDD markers appear on the correct relationship ends on both the canvas and exports.
- Legacy edges without route geometry remain valid and route automatically.
- Automatic routes avoid unrelated node boxes and fan out only when overlap requires it.
- Manual anchors, waypoints, and label positions survive save/reload and can snap back to automatic behavior.
- Empty BDD classifiers are compact; populated classifiers preserve their non-empty compartments.
- BDD presets write canonical semantics, and the three-tab property panel keeps structured editing complete in a denser layout.
- The same diagram has equivalent geometry, markers, labels, and BDD block structure on the canvas, in SVG, and in PNG.

## Related Docs

- [`../00-epic.md`](../00-epic.md) — Epic 2 goal and existing phase plan.
- [`../04-editor-ui-ux/00-group.md`](../04-editor-ui-ux/00-group.md) — preceding editor UI/UX phase.
- [`../../00-current-state.md`](../../../../05-delivery/01-current-state.md) — single live delivery-status board.
- [`../../../../01-architecture/02-frontend-architecture.md`](../../../../02-architecture/04-frontend.md) — frontend runtime and editor responsibilities.
- [`../../../../02-design-and-features/00-diagram-json-schema.md`](../../../../03-design/03-diagram-json-schema.md) — canonical diagram contract.
- [`../../../../02-design-and-features/03-rendering-design.md`](../../../../03-design/06-rendering.md) — SVG/PNG rendering contract.
- [`../../../../02-design-and-features/editor-ui-design.md`](../../../../03-design/12-editor-ui.md) — editor interaction and visual design owner.
- [`../../../../02-design-and-features/diagram-schemas/bdd-diagram-blueprints.md`](../../../../03-design/02-diagram-schemas/02-bdd-blueprints.md) — BDD notation owner.
