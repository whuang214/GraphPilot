# Diagram JSON ↔ React Flow Mapping

> **Design authority:** GraphPilot JSON is the source of truth; React Flow canvas state is a derived, disposable
> view. Runtime delivery status belongs only to
> [`01-current-state.md`](../05-delivery/01-current-state.md).

## Purpose

The adapters in `frontend/src/adapters/reactFlow.ts` translate a saved GraphPilot document onto the editable React Flow canvas and back. This document owns what survives that round-trip and what is display-only. The canonical JSON shape and semantic vocabulary are owned by [`01-diagram-json-schema.md`](../03-design/02-diagram-schemas/01-diagram-json-schema.md).

```mermaid
flowchart LR
    J["Canonical GraphPilot JSON<br/>source of truth"] -->|forward| C["React Flow state<br/>editable projection"]
    C -->|reverse whitelist| J
    C -. "discarded" .-> X["runtime state<br/>selected, dragging, measured, internals"]
```

## Core mapping

- **Forward (`graphPilotToReactFlow`)** expands canonical nodes/edges into canvas state, copies semantic data, maps visual style to runtime `data.gpStyle`, preserves ownership, and derives markers from `frontend/src/editor/lib/elementCatalog.ts` plus relationship-end data.
- **Reverse (`reactFlowToGraphPilot`)** rebuilds strict canonical JSON by whitelisting all known structured fields. The 48-example fixture suite guards no-op and clone round-trips; it never serializes React Flow session/internals.
- `node.type` is always the single `gpNode` renderer family. Core node identity remains `node.data.semanticType`; BDD Block `data.stereotype` independently selects its primary visible heading.
- `edge.type` remains the React Flow edge family; core relationship identity remains `edge.data.semanticType`.

## Fields handled specially

| Canonical field | Canvas projection | Rule |
| --- | --- | --- |
| `node.type` | `gpNode` | shape comes from the catalog primitive for `data.semanticType`, never from another persisted node family |
| `node.data` | node `data` | preserve core identity, optional BDD primary `stereotype`, features, extension points, definition detail, join specs, and applied stereotypes |
| `node.style` | runtime `data.gpStyle` | lets custom glyphs repaint live; reverse mapping restores the canonical style subset |
| `node.width` / `height` | wrapper size | persisted design intent, not measured runtime size |
| `node.parentId` | `parentId` | owns contained/grouped nodes and boundary features |
| `node.origin` / `edge.origin` | preserved nonvisual canonical data | context provenance survives load/edit/save unchanged; it is not React Flow runtime state or editable presentation data |
| diagram `metadata.generationMode` / `generationContext` | preserved canonical metadata | generation trace survives round-trip even when the UI does not display it |
| `edge.data.semanticType` and relationship ends | markers/line style/labels | notation is derived; markers are never persisted |
| `edge.label` | edge label | empty display labels are omitted on save |
| `edge.route` | runtime `data.gpRoute` + custom edge controls | optional `orthogonal`/`straight` mode, authored anchors, orthogonal waypoints, and label offset round-trip; calculated automatic paths never persist |

## Ownership and geometry

`parentId` has two canonical uses:

The core profile uses `parentId` for a use case inside a displayed System Boundary. Retained legacy/custom containers and boundary features may preserve existing ownership for compatibility, but core Activity and BDD palettes do not create grouped activity nodes, ports, or pins.

The editor's drag/reparent logic owns changes to `parentId` and rejects missing parents or cycles. Alignment guides compare absolute canvas positions even when a retained child stores a parent-relative position.

## Edge route geometry

An optional `edge.route` contains only user-authored presentation geometry: optional `mode`, normalized source/target boundary anchors, at most 32 ordered root-diagram routing coordinates, and an X/Y offset from the central path-length label anchor. Missing mode means `orthogonal`; `straight` excludes waypoints. A route anchor overrides the corresponding legacy midpoint handle; editing or resetting anchors clears that superseded handle. Reset and snap-back remove redundant overrides rather than serializing calculated defaults.

Straight canvas/SVG routing joins authored or primitive-aware automatic boundary anchors with exactly one segment. Orthogonal routing ignores unrelated nodes: compatible aligned anchors use one direct segment, while non-aligned endpoints use the smallest stable path that preserves boundary approach. Manual waypoints override only the orthogonal resolver, remain fixed when one endpoint moves, and translate when both endpoints or their shared parent move together. Switching to straight clears waypoints in the same undoable edit while preserving anchors and label offset.

## Edge notation derived from semantics

| Relationship | Canvas notation |
| --- | --- |
| `controlFlow` | directed activity arrow |
| `association` | plain BDD/use-case relationship; navigability may add an end arrow |
| `composition` | part source → whole target; filled diamond at target |
| `include`, `extend`, `dependency` | dashed open arrow; include/extend keyword label derived from type |
| `generalization`, `realization` | hollow triangle at the parent/supplier target |
| `commentLink` | dashed line without arrowhead |
| unknown/off-catalog relationship | open-arrow fallback, matching the SVG renderer |

Composition is one canonical edge identity rather than association aggregation. **Swap ends** exchanges source/target, source/target end data, endpoint handles/anchors, and authored route direction atomically so target remains the whole. Include and extend remain distinct relationships rather than dependency stereotypes. Changing Relationship type from either the consolidated palette tray or Content inspector uses one transition: it preserves common description/metadata/applied stereotypes, retains only structured fields compatible with the new identity (association/composition ends, extend condition/locations, or control-flow fields), clears every incompatible structured field, and immediately re-derives canvas/SVG line and marker presentation.

An optional canonical `data.arrow` can still control permitted directional overrides for relationships whose semantics allow it; it must not reverse fixed direction. Runtime markers inherit the authored edge stroke and are never persisted.

## Reverse mapping rules

- **Whitelist, never copy wholesale.** Runtime-only fields (`selected`, `dragging`, `resizing`, `measured`, `positionAbsolute`, `internals`, and similar) never reach disk.
- **Loaded and canvas-created elements.** Loaded elements preserve canonical nonvisual data by ID; canvas-created elements recover canonical data from their live node/edge data.
- **Live semantic editing.** Read core `semanticType`, BDD primary `stereotype`, structured `features`, `extensionPoints`, type-specific node fields, relationship ends, guards, extension data, and `appliedStereotypes` from current canvas state.
- **Structured features are authoritative.** Compartments are a derived presentation of `data.features`; never round-trip a second free-text compartment source.
- **Sizes express intent.** Save only positive explicit dimensions; do not use measured dimensions as the canonical fallback.
- **Style remains narrow.** Reconstruct the supported node/edge style subset from `gpStyle`, wrapper state, and the original element.
- **Empty optional values disappear.** Remove blank labels, empty collections/objects, and empty optional strings without deleting required semantic fields.
- **Ownership follows the canvas.** A valid edited `parentId` persists; clearing ownership persists only where the element kind can legally be top-level.

## Round-trip invariants

1. No-op load/save preserves core or retained compatibility identity and structured model data.
2. Canvas and SVG derive Block compartments, primary stereotype headings, note dog-ears, and edge markers from the same canonical fields.
3. Editing visual notation does not silently change semantic identity; changing BDD `stereotype` deliberately changes only the primary heading.
4. React Flow runtime fields never appear in `.gp.json`.
5. Concrete diagrams remain within their profile or are explicitly reconciled to `custom` by the API workflow.
6. Optional element origins and diagram generation trace round-trip byte-stably unless a separately designed
   grounded-edit workflow deliberately updates them.

## Owned elsewhere

- Canonical JSON and semantic fields: [`01-diagram-json-schema.md`](../03-design/02-diagram-schemas/01-diagram-json-schema.md)
- Per-type notation and structural intent: [`02-diagram-schemas/`](../03-design/02-diagram-schemas/README.md)
- Type reconciliation and validation: [`02-diagram-validation.md`](../03-design/03-validation/02-diagram-validation.md)
- Frontend runtime, editor route, and save flow: [`04-frontend.md`](04-frontend.md)
- Canvas implementation: `frontend/src/adapters/reactFlow.ts` and `frontend/src/editor/`
