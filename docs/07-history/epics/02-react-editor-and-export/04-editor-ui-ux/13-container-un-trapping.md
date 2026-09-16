# Slice 13: Container Un-trapping

## Purpose

Let a node that was dropped inside a system-boundary container be dragged back out again (feature-list #5), instead of being permanently pinned by React Flow's `extent: 'parent'`, while keeping `parentId` containment correct as nodes enter and leave a boundary. This completes the design doc's **P2** editing behavior alongside edge editing (Slice 12).

## Background

- Slice 05 (Epic 2) introduced `parentId` containment for the use-case **system boundary**; nodes dropped inside a boundary become its children.
- Those children currently get `extent: 'parent'`, which traps them — they can't be dragged back out of the container (#5).
- The reverse adapter (`reactFlowToGraphPilot`) already maps `parentId` to the canonical JSON, so the fix is about drag behavior and re-parenting, not the schema.

## Design

- Drop (or conditionally relax) `extent: 'parent'` so a child can be dragged outside its container.
- On drag-stop, recompute parentage from geometry: if the node is dropped outside any boundary, clear its `parentId` (and convert its position back to absolute); if dropped inside a different boundary, re-parent it (relative position). Reuse the existing containment helper rather than adding a new representation.
- Keep the saved JSON shape identical — only `parentId` and the node's stored position change, exactly as they already do when a node is first dropped into a container.

## Included Work

- Remove/relax the `extent: 'parent'` pin on container children in `customNodes.tsx` / the node setup.
- Add drag-stop re-parenting in `EditorPage.tsx`: clear `parentId` when a node leaves all boundaries, set it when it enters one, adjusting position between absolute/relative consistently.
- Verify the behavior maps cleanly through `adapters/reactFlow.ts` with no runtime-field leakage.
- Unit tests for the in → out → in containment transitions (parentId set/clear + position).

## Not In Scope

- Nested or multi-level containers beyond the current single system-boundary level.
- New container shapes or any change to how containment is represented in the canonical JSON.
- Auto-layout of container contents.

## Target Areas

- `frontend/src/editor/canvas/customNodes.tsx` / `frontend/src/editor/EditorPage.tsx` (extent + drag-stop re-parenting).
- `frontend/src/adapters/reactFlow.ts` (round-trip verification only).
- Frontend unit tests (including `adapters/reactFlow.test.ts` coverage if needed).

## Exit Criteria

- A node can be dragged **out** of a container and dropped on the free canvas, and dragged back **in** again (#5).
- `parentId` is set when entering a boundary and cleared when leaving, with the stored position correct in both cases.
- The load → edit → save round-trip stays byte-stable (no schema change, no runtime-field leak); `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `12-edge-editing-and-routing.md`

## Next Slice

- `14-palette-and-landing-polish.md`

## Outcome

Implemented on `epic-6-refinements`; pending manual confirm.

**Delivered (#5).** A node can be dragged out of a system-boundary container (and into one). The forward adapter no longer sets `extent: 'parent'` (which pinned children), and `onNodeDragStop` re-parents by geometry via `reparentNode` (`containment.ts`): a node dropped over a boundary becomes its child; dropped outside any boundary it is un-parented, converting between absolute and parent-relative coordinates so it stays visually put. The reverse adapter now treats `rf.parentId` as the source of truth, so clearing a parent persists (un-trapping round-trips). Boundaries themselves are not re-parented.

**Verification.** npm run lint (0/0), npm run build (tsc + vite), npm run test (190 passed, incl. a new `containment.test.ts` covering the position/parent conversion and parent-before-child ordering; the adapter round-trip tests still pass). Byte-stable for the no-edit case (`rf.parentId` equals the loaded value). Manual confirm (drag a child out of / into a container) pending.
