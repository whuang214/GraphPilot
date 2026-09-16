# Slice 06: Draw-on-Canvas Authoring

## Purpose

Make it possible (and verified) to build a diagram by drawing on the canvas and have it convert to valid canonical GraphPilot JSON. Today the editor only confirms the *forward* direction (load an existing `output.gp.json` → React Flow → save it back). This slice confirms the **reverse** direction so a future draw.io-style "start from an empty document" experience is architecturally enabled and not expensive to add later.

## Background

- In-browser creation of brand-new diagrams is **out of MVP** (MVP browser scope is light edits to existing diagrams; new-file creation is owned by MCP generation). But the **reverse adapter's current "original-first" assumption is the expensive thing to change later**, so we enable the architecture and a basic path now rather than reworking it post-MVP.
- The reverse adapter (`frontend/src/adapters/reactFlow.ts` `reactFlowToGraphPilot()`) recovers `type`, `semanticType`, `description`, `metadata`, and `parentId` from the **originally loaded** diagram keyed by id. A node created on the canvas has no original entry, so today it would save as `type: 'default'` with **no `semanticType`** — the diagram's meaning would be lost.
- Confirming the reverse direction also hardens the sample work that follows: node creation changes the very reverse-adapter assumptions the sample round-trip (Slice 08) validates, so settling it first avoids validating twice.

## Included Work

- **Reverse adapter (the core change):** read `type` / `data.semanticType` / `data.description` / `data.metadata` / `parentId` from the **React Flow node's own `data`** for ids that have no original entry, while still preferring the original for loaded nodes and still stripping React Flow runtime/session-only fields. Same idea for edges (`semanticType` from edge `data`).
- **Minimal node creation:** a basic way to add a node that stamps `node.type` + `data.semanticType` onto the React Flow node (e.g. a small palette or an "add node" with a type/semanticType picker), enough to exercise the reverse direction for all three diagram types. Polish (drag-from-sidebar, inline edit, copy/paste) is **not** in scope.
- **Minimal edge semantics on creation:** new edges (`onConnect`) can carry a `semanticType` so saved edges are meaningful (default to the type's primary edge semantic, e.g. `flow` / `association`).
- **Stable client-side id generation** for new nodes (extend the existing `newEdgeId` pattern `EditorPage` already uses for edges created via `onConnect`).
- **Reverse-direction confirmation test (the deliverable that proves the goal):** a Vitest that *starts* from React Flow state (nodes/edges created with `type` + `semanticType` in `data`, including React Flow runtime junk) and asserts `reactFlowToGraphPilot()` produces canonical JSON that is schema-shaped, carries the right `type`/`semanticType`, and contains no runtime fields. This is the mirror of the existing forward round-trip test.

## Not In Scope

- New-document / blank-canvas entry point and **save-new** file allocation (creating a brand-new `.graphpilot/<name>.gp.json`). The MVP editor still opens via `?diagramPath=`; save-new ties into Epic 3 name allocation and is deferred.
- Full draw.io/Lucidchart editor tiers: drag-from-palette polish, undo/redo, autosave, multi-select, snapping, minimap, palette driven by backend type profiles, auto-layout.
- The in-UI AI generate flow / frontend chatbot (post-MVP; tracked in the backlog).
- New canonical schema fields or new supported style keys.

## Target Areas

- `frontend/src/adapters/reactFlow.ts` (reverse adapter: canvas-origin support)
- `frontend/src/adapters/reactFlow.test.ts` (new reverse-direction confirmation test)
- `frontend/src/editor/EditorPage.tsx` + a minimal add-node affordance / small palette
- `frontend/src/editor/components/PropertyPanel.tsx` (set `semanticType` for nodes/edges, if needed to make created elements meaningful)
- `frontend/README.md` / `docs/01-architecture/02-frontend-architecture.md` (note reverse direction is supported)
- `docs/02-design-and-features/01-diagram-json-mapping-design.md` (record that canonical JSON can originate from canvas state, not only from a loaded diagram)
- `docs/03-development-and-delivery/02-backlog.md` (Tier A promotion note — already recorded during planning; keep consistent if scope drifts)
- `docs/02-design-and-features/decision-decisions.md` (de-risking decision — already recorded; update only if scope changes)

## Exit Criteria

- A node created on the canvas with a chosen `semanticType` saves to canonical JSON carrying the correct `node.type` and `data.semanticType` (no `default`/empty-data loss).
- New edges save with a meaningful `semanticType`.
- The reverse-direction confirmation test passes: canvas-origin React Flow state → `reactFlowToGraphPilot()` → schema-shaped canonical JSON with no leaked runtime fields.
- The existing forward round-trip test (loaded sample → RF → canonical) still passes unchanged.
- `npm run test`, `npm run build`, and `npm run lint` pass.

## Previous Slice

- `05-node-shapes.md`

## Next Slice

- `07-sample-layout.md`

## Outcome

✅ Completed as planned. The React Flow → GraphPilot direction is confirmed for elements created on the canvas (not just round-tripping a pre-loaded diagram), with a basic drag-from-palette authoring path to exercise it.

**Delivered.**

- **Reverse adapter** (`frontend/src/adapters/reactFlow.ts`): for nodes/edges with no originally loaded entry, `reactFlowToGraphPilot()` now recovers `semanticType` / `description` / `metadata` from the element's own `data` (via `recoverSemanticFields`), uses the React Flow `node.type` directly, reads visual style from `data.gpStyle`, and carries `parentId` from the node when present. Loaded elements still prefer the original; React Flow runtime/session and display-only fields (`selected`, `measured`, `markerEnd`, `gpStyle`, …) are still never persisted.
- **Drag-from-palette authoring**: a left-hand `NodePalette` (`frontend/src/editor/components/NodePalette.tsx`) lists the block types for the loaded diagram's type; dragging one onto the canvas (`onDrop` + `screenToFlowPosition`) creates a node stamped with the real `node.type`, `data.semanticType`, a default label, default size, and `DEFAULT_NODE_STYLE`. Catalog, sizes, default-edge-semantic and id generation live in `frontend/src/editor/lib/palette.ts`. The editor is wrapped in `ReactFlowProvider` so the canvas can use `useReactFlow()`.
- **Meaningful new edges**: `onConnect` stamps new edges with the diagram type's primary edge semantic (`flow` / `association` / `composition`) and the matching marker.
- **Stable client-side ids**: `newNodeId()` mirrors the existing `newEdgeId()` pattern.
- **Reverse-direction confirmation test**: a Vitest builds canonical JSON purely from canvas-origin React Flow state (with runtime junk) and asserts the correct `type`/`semanticType`/size/style with no leaked runtime fields — the mirror of the forward round-trip.

**Deviations.** New-document / blank-canvas entry point and **save-new** file allocation remain out of scope (the editor still opens via `?diagramPath=` and saves by overwriting the loaded file). This slice proves the reverse *conversion* direction and adds the minimum authoring to exercise it, as planned.

**Post-review.**

- The palette is a **generic set of simple shapes** shown for every diagram, not a per-blueprint list — so a user can compose any diagram from basic shapes regardless of the loaded type (a step toward blank-canvas authoring). Shapes still map to a `node.type` + `semanticType`; cross-type mixing only yields non-blocking advisory validation warnings.
- Connections were made **fully flexible** so any relationship can be drawn between any nodes from any side. Two things were needed: (1) a larger `connectionRadius` (the default 20px left wide/short nodes' left/right handles too far from a natural drop point), and (2) **both a `source` and a `target` handle on every side** of each node. A single-type-per-side setup could not connect, e.g., a left/target handle to another left/target handle (`ConnectionMode.Loose` permits same-type ends but the start-from-target + same-type-end path is unreliable); giving every side both types makes any side connectable to any side, in any direction. An allow-all `isValidConnection` is the single hook a client can later use to restrict relationships.

**Verification.**

- `npm run test` (13 passed — round-trip, rendering-fields, recolour-persistence, and the new canvas-origin authoring test), `npm run build`, `npm run lint` (0/0).
- `python manage.py test` (143 passed; no backend changes this slice).

**Follow-up.** Slice 07 (per-example sample-library restructure). A future follow-up can add a backend `create`/`save-new` endpoint + a blank-canvas "New diagram" entry to make the browser fully editor-first.
