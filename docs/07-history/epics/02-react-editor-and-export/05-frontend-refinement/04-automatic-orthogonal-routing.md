# Slice 04: Automatic Orthogonal Routing

## Purpose

Replace midpoint doglegs with deterministic obstacle-aware orthogonal routes, compatible aligned fan-in/fan-out trunks, and compact separate lanes for incompatible groups.

## Design

- The automatic router treats unrelated node rectangles as obstacles with consistent clearance while excluding the edge's own endpoint boundaries from obstruction.
- Candidate paths remain horizontal/vertical, minimize avoidable bends and distance, and use stable tie-breaking so identical input produces identical output.
- The final source and target segments approach their anchors orthogonally, preserving marker orientation and boundary contact.
- A complete aligned group shares a trunk only when every relationship has compatible semantics, end markers, line style, and no ambiguous common-end adornment; otherwise compact lanes remain near the side center.
- Lane ordering is deterministic from endpoint geometry and canonical edge identity, not render order or selection state.
- Automatic points remain derived display geometry; this slice does not populate optional route overrides.

## Included Work

- Implement obstacle collection, orthogonal path search, simplification, and deterministic fallback behavior.
- Add collision detection and conditional lane fan-out for parallel relationships.
- Place default relationship labels on a stable usable segment of the selected route.
- Mirror route decisions in the React canvas and backend SVG renderer.
- Cover horizontal/vertical layouts, intervening nodes, containers, nested nodes, parallel edges, reordered edge arrays, and node movement.

## Not In Scope

- Moving nodes or performing whole-diagram auto-layout.
- Manual anchor, waypoint, or label interaction.
- Curved/freehand paths, edge bundling, or semantic inference.
- Persisting automatic routes in canonical JSON.

## Target Areas

- `frontend/src/editor/lib/edgeRouting.ts`.
- `frontend/src/editor/canvas/FloatingEdge.tsx`.
- `backend/services/diagrams/rendering/diagram_render_service.py`.
- Frontend routing tests, backend render-service tests, and shared parity fixtures.

## Exit Criteria

- Automatic routes do not cross unrelated node boxes in representative BDD, activity, use-case, container, and nested-node layouts.
- Route output is orthogonal, simplified, deterministic, and stable when edge array order changes.
- Parallel edges fan out when they would overlap and do not fan out when their natural routes are distinct.
- Final segments preserve correct marker orientation and contact from Slice 02.
- Canvas and SVG choose equivalent points, lanes, and default label locations from the same canonical input.
- Routing tests and relevant frontend/backend verification pass.

## Previous Slice

- [`03-route-contract.md`](03-route-contract.md)

## Next Slice

- [`05-manual-route-editing.md`](05-manual-route-editing.md)

## Outcome

**Completed.** Canvas and SVG use deterministic direct/L/corridor candidates scored by collisions, bends, and length against padded unrelated nodes. Compatible aligned source fan-out and target fan-in groups may share a derived trunk only when the complete group has matching semantics, markers, and line style with no ambiguous common-end adornment. Incompatible groups receive compact deterministic lanes near the side center; derived points never persist.

**Deviation.** Lane ordering uses stable target/source geometry plus edge ID rather than array order. A selected edge reports the nonblocking fallback state when every candidate remains obstructed.

**Verification.** Shared fixtures cover direct, obstacle, manual, and fan-out points. Playwright compares canvas and server-SVG coordinates for an intervening-node route, compatible fan-in/fan-out, and incompatible lanes. Final aggregate gate evidence is recorded in Slice 08.
