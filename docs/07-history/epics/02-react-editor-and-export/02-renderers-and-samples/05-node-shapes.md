# Slice 05: Type-Specific Node Shapes

## Purpose

Replace the display-first React Flow rendering (every node is a built-in `default` rectangle) with custom node/edge renderers and `parentId` containment, so that the canonical diagram JSON previews with meaningful, type-specific visuals. This makes comprehensive sample authoring (Slice 08) reliable instead of blind.

## Background

- The forward adapter currently hard-codes `type: 'default'` and passes only `data.label` into React Flow, so `node.type` (`activityNode` / `useCaseNode` / `bddNode`) and `data.semanticType` are preserved in JSON but unused for rendering (`frontend/src/adapters/reactFlow.ts`).
- `<ReactFlow>` registers no `nodeTypes` and no `edgeTypes` (`frontend/src/editor/EditorPage.tsx`), so a decision is not a diamond, an actor is not a stick figure, a `systemBoundary` is not a container, and a BDD `block` is not a compartment box — they all render identically.
- `parentId` exists in the schema/types and is carried by the reverse adapter, but the forward adapter never passes it to React Flow, so containment (e.g. use cases nested in a system boundary) does not render. This is why the Epic 2 `use_case_diagram` sample's `systemBoundary` is a disconnected container with an advisory warning.
- The reverse adapter (`reactFlowToGraphPilot`) already whitelists canonical fields and strips React Flow runtime fields; this slice must keep that guarantee intact.

## Included Work

- Add custom node components registered via `nodeTypes`, keyed by `node.type` and branching on `data.semanticType`:
  - `activityNode`: `start` / `end` (terminator), `action` (rounded rectangle), `decision` / `merge` (diamond), `note`.
  - `useCaseNode`: `actor` (stick figure), `useCase` (ellipse), `systemBoundary` (container), `note`.
  - `bddNode`: `block` (named compartment box), `part`, `value`, `constraint`, `note`.
- Add React Flow `Handle`s to the custom nodes so existing connect / reconnect / delete edge interactions keep working.
- Add edge semantics (via `edgeTypes` and/or `markerEnd` mapping) for the documented edge semantic types: `flow` (arrow), `association` (plain), `include` / `extend` (dashed), `generalization` (hollow triangle), `composition` (filled diamond).
- Render `parentId` containment by passing `parentId` (and `extent: 'parent'`) into React Flow nodes so child nodes nest inside container nodes.
- Forward adapter (`graphPilotToReactFlow`): stop hard-coding `type: 'default'`; pass the real `node.type`, the full `data` (so renderers can branch on `semanticType`), `parentId`, and the edge marker/type derived from `edge.data.semanticType`.
- Reverse adapter (`reactFlowToGraphPilot`): keep emitting canonical JSON and keep stripping React Flow runtime/session-only fields; update only as needed to stay a no-op round-trip.
- Update the Vitest round-trip test (`frontend/src/adapters/reactFlow.test.ts`) for the adapter changes; it must still prove the existing samples round-trip without data loss.

## Not In Scope

- `diagram_generate` / `diagram_render` and any MCP work (later Epic 3 slices).
- Confirming the reverse direction / canvas authoring (Slice 06).
- Restructuring the sample folders (Slice 07) and authoring new samples (Slice 08).
- Node creation/add-node UI and semantic-type editing in the property panel (kept minimal; property panel scope is unchanged beyond what rendering requires).
- New canonical schema fields or style keys (the existing schema/style subset is sufficient).
- SVG rendering parity (the browser editor and the backend SVG renderer are separate; visual parity between them is not required by this slice).

## Target Areas

- `frontend/src/editor/EditorPage.tsx` (register `nodeTypes` / `edgeTypes`)
- `frontend/src/editor/` new custom node/edge components
- `frontend/src/adapters/reactFlow.ts` (forward adapter changes; reverse adapter guardrails)
- `frontend/src/adapters/reactFlow.test.ts`
- `frontend/README.md` and `docs/01-architecture/02-frontend-architecture.md` if the renderer structure clarifies them
- `docs/02-design-and-features/01-diagram-json-mapping-design.md` if the `node.type` / `semanticType` → renderer mapping needs to be recorded

## Exit Criteria

- The three existing Epic 2 samples load in `/editor` and render with type-specific visuals (diamonds, actor, ellipse, container, compartment box) rather than identical rectangles.
- `parentId` containment renders: a child node visually nests inside its container, and the `use_case_diagram` `systemBoundary` reads as a container rather than an overlapping rectangle.
- The load → (no edit) → save round-trip remains a no-op for the existing samples (no data loss, no leaked React Flow runtime fields).
- `npm run test`, `npm run build`, and `npm run lint` pass.

## Previous Slice

- `../01-browser-load-edit-save/04-canonical-samples.md`

## Next Slice

- `06-canvas-authoring.md`

## Outcome

✅ Completed as planned. The display-first `default` rendering is replaced with type-specific custom renderers and `parentId` containment.

**Delivered.**

- Added `frontend/src/editor/canvas/customNodes.tsx` (`ActivityNode`, `UseCaseNode`, `BddNode`), each branching on `data.semanticType` and including React Flow `Handle`s: activity terminator/action/diamond/note; use-case actor/ellipse/ container/note; BDD compartment box with a `«stereotype»` header.
- Connection handles are on **all four sides** and the canvas runs in `ConnectionMode.Loose`, so every handle works as both a connection start and end (fixes the "one side can't connect" behavior — a `source`-only/`target`-only handle in the default strict mode). The primary pair renders first so handle-less sample edges still attach to the natural side.
- Added `frontend/src/editor/canvas/nodeTypes.ts` registering the renderers as React Flow `nodeTypes` (kept separate so `customNodes.tsx` only exports components — avoids the fast-refresh lint warning).
- Forward adapter (`frontend/src/adapters/reactFlow.ts`) now passes the real `node.type`, the full `node.data` + `data.gpStyle`, `parentId` + `extent: 'parent'`, orders parent containers before children (by nesting depth, so multi-level containment is handled), and derives `edge.markerEnd` from `edge.data.semanticType`. `EditorPage` renders custom SVG `<defs>` for the `generalization` (hollow triangle) and `composition` (filled diamond) markers and sets `defaultMarkerColor` so built-in markers match the edge stroke.
- `data.gpStyle` is the single source of truth for node visual style: the renderer draws from it, the property panel edits it, and the reverse adapter reads it back (whitelisting the supported keys). So a recolour repaints the custom shape live and persists; the wrapper `style` carries only sizing. `markerEnd` and React Flow runtime/session fields remain display-only and are never persisted.

**Deviations.**

- To make `parentId` containment demonstrable (the slice's exit criterion), the existing `use_case_diagram` sample was updated so its two use cases nest inside the `systemBoundary` via `parentId` (positions made relative). Verified schema-valid with no new blocking errors (`parentId` has no structural validation; `disconnected_node` for the boundary remains an advisory warning only).

**Post-review.** A detailed review surfaced and fixed several issues:

- Multi-level `parentId` ordering: a depth sort with a cycle guard, replacing the single-level partition.
- The actor renderer now honours `gpStyle.borderWidth`.
- Edge markers use the edge colour (`defaultMarkerColor` + a coloured new-edge marker), and new edges drawn on the canvas get a visible arrowhead.
- The property-panel recolour now repaints the custom shape live (routed through `data.gpStyle`), which also removed the earlier corner-leak/recolour limitation.
- Handle ids are namespaced (`gp-*`).
- Connection handles are enlarged and given a `zIndex` so they sit above the custom shapes — React Flow's default 6px, no-z-index handle was being painted over by the node content, which made grabbing/dropping on a handle unreliable (especially after deleting and re-drawing an edge).

**Verification.**

- `npm run test` (12 passed — round-trip + forward-rendering assertions + a recolour-persistence test), `npm run build`, `npm run lint` (0 warnings, 0 errors).
- `python manage.py test` (143 passed, incl. `tests.generation.test_samples` against the updated use-case sample).

**Follow-up.** Per-edge marker colour for the custom `generalization`/`composition` SVG markers (they currently use the shared edge colour) is left as optional polish in the backlog's robust-editor theme.
