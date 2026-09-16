# Slice 02: BDD Marker Correctness

## Purpose

Make BDD relationship markers express the canonical relationship end correctly on the canvas and in exported output before routing becomes more sophisticated.

## Background

Marker ownership is semantic: association-end aggregation and navigability come from `sourceEnd` or `targetEnd`, while generalization, dependency, and containment defaults come from the relationship identity. Route direction determines marker orientation at that end, not which end owns the marker.

## Design

- Shared-aggregation and composition diamonds appear at the association end that declares them.
- Navigability arrows remain on their declared end and do not replace a fixed aggregation marker.
- Generalization triangles and containment crosshairs remain on their catalog-defined semantic ends.
- Marker reference points, orientation, fill, stroke, and clearance make the adornment touch the node boundary without clipping, inversion, or being buried inside the node.
- Canvas and SVG derive marker selection from the same semantic precedence; arrow overrides affect only relationships that permit directional overrides.

## Included Work

- Correct BDD marker selection and source/target precedence.
- Correct marker geometry and orientation for horizontal and vertical route approaches.
- Align canvas marker definitions with backend SVG marker output.
- Add focused fixtures/tests for source-end and target-end aggregation, navigability, generalization, dependency, and containment.
- Preserve marker color, line style, and existing canonical relationship data through round-trip conversion.

## Not In Scope

- New relationship semantic types or changes to the meaning of association ends.
- Obstacle-aware routing, fan-out, persisted route geometry, or route-editing handles.
- BDD relationship presets or property-panel restructuring.

## Target Areas

- `frontend/src/adapters/reactFlow.ts`.
- Canvas marker definitions and `frontend/src/editor/canvas/FloatingEdge.tsx`.
- `backend/services/diagrams/rendering/diagram_render_service.py`.
- Element-catalog marker metadata only if a semantic-end mapping is incorrect.
- Frontend adapter/edge tests and backend render-service tests.

## Exit Criteria

- Each covered BDD marker appears at the semantic source or target end declared by canonical data.
- Horizontal and vertical approaches orient markers away from the path and against the correct node boundary without clipping.
- Aggregation, navigability, catalog defaults, and permitted arrow overrides follow one documented precedence on canvas and SVG.
- Marker fixes do not mutate edge semantics or leak display-only marker fields into saved JSON.
- Focused canvas/SVG marker tests and relevant verification pass.

## Previous Slice

- [`01-source-state-and-sync.md`](01-source-state-and-sync.md)

## Next Slice

- [`03-route-contract.md`](03-route-contract.md)

## Outcome

**Completed.** React Flow custom markers now use marker IDs in the form expected by `@xyflow/react`, eliminating malformed nested `url(...)` references. Association-end aggregation/navigability, generalization, containment, directional overrides, authored stroke color, and backend SVG marker precedence remain semantic and end-correct.

**Verification.** Adapter tests cover source/target composition, shared aggregation, navigability, generalization, containment, and overrides; backend rendering covers association-end markers; Playwright asserts valid references for every custom BDD marker. Final aggregate gate evidence is recorded in Slice 08.
