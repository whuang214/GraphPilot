# Slice 03: Route Contract

## Purpose

Add a backward-compatible optional canonical contract for user-controlled edge geometry while keeping automatic routing as the default for every legacy edge.

## Design

- An edge may carry optional route geometry for normalized source/target boundary anchors, ordered orthogonal waypoints in diagram coordinates, and moved relationship-label positions.
- The route object and each override inside it are optional. Missing geometry is derived automatically and is not written merely because the edge was rendered.
- Anchor offsets are bounded to the node perimeter; coordinates are finite; waypoint and label collections use stable roles/order and reject malformed entries.
- Route geometry is visual. It never changes `source`, `target`, `semanticType`, association-end meaning, or marker ownership.
- Snap-back or reset removes the corresponding override so canonical JSON returns to automatic behavior instead of persisting calculated defaults.

## Included Work

- Extend the canonical JSON schema with optional per-edge route geometry and precise validation bounds.
- Mirror the contract in frontend types, runtime guards, and schema/type parity checks.
- Preserve valid route geometry exactly through GraphPilot-to-React-Flow and reverse conversion.
- Ensure clone, reconnect, save normalization, and validation handle route geometry deliberately rather than copying runtime fields.
- Add valid, legacy-without-route, partial-route, and invalid-route fixtures/tests.
- Promote the final field-level contract to the canonical schema/mapping/rendering owners during implementation.

## Not In Scope

- Choosing obstacle-aware paths or fan-out lanes.
- Canvas controls for creating or moving anchors, waypoints, or labels.
- Curves, freehand points, semantic relationship changes, or whole-diagram layout.
- Persisting automatically calculated route points.

## Target Areas

- `backend/assets/schemas/diagram.json` and backend schema/validation tests.
- `frontend/src/types/diagram.ts` and schema parity tests.
- `frontend/src/adapters/reactFlow.ts` and adapter/clone tests.
- Canonical schema, mapping, frontend-architecture, and rendering design owners.

## Exit Criteria

- Existing diagrams with no route geometry validate and round-trip unchanged.
- Valid partial or complete route overrides validate and survive load → edit → save exactly.
- Non-finite coordinates, out-of-range anchors, malformed label roles, and invalid waypoint entries fail with useful schema paths.
- React Flow runtime geometry cannot leak into the canonical route object.
- Removing an override restores omission-based automatic behavior.
- Backend schema tests, frontend parity/adapter tests, and relevant verification pass.

## Previous Slice

- [`02-bdd-marker-correctness.md`](02-bdd-marker-correctness.md)

## Next Slice

- [`04-automatic-orthogonal-routing.md`](04-automatic-orthogonal-routing.md)

## Outcome

**Completed.** Canonical edges accept an optional non-empty `route` with bounded source/target anchors, up to 32 finite ordered routing points, and a finite label offset. The schema, handwritten TypeScript types/runtime guard, adapter, property panel, and backend renderer consume the same contract. Untouched routes preserve authored points exactly; explicit reset removes the route instead of restoring the loaded value.

**Deviation.** Authored coordinates are routing controls that the resolver joins/simplifies orthogonally; the schema validates shape/bounds rather than requiring every adjacent authored point to be axis-aligned.

**Verification.** Backend schema tests reject malformed/empty/out-of-range geometry, adapter tests prove exact no-op/reset behavior, and one JSON fixture drives identical frontend/backend route-point assertions. Final aggregate gate evidence is recorded in Slice 08.
