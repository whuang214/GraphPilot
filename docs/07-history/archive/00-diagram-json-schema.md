# Diagram JSON Schema

> **Confirmed (Epic 2 Slice 04).** This schema was validated against the React Flow load/edit/save round-trip using the canonical per-type samples then under `backend/assets/blueprints/<type>/examples/` (since re-curated and split into the `examples/{training,eval}/<name>/output.gp.json` pools in Epic 3 Slice 05). No structural changes were required. Round-trip notes: empty-string edge labels are omitted (the reverse adapter treats `""` as absent), and `width`/`height` are persisted design intent — React Flow's measured runtime dimensions are not saved. See `docs/03-development-and-delivery/epics/02-react-editor-and-export/01-browser-load-edit-save/04-canonical-samples.md`.

## 1. Purpose

This document defines the canonical saved JSON format for GraphPilot diagrams in the MVP.

GraphPilot JSON is the source of truth after creation. It is not raw React Flow JSON, but it should stay React Flow-friendly so the editor can translate it with minimal friction.

## 2. Design Principles

- GraphPilot JSON is the source of truth
- GraphPilot JSON is not raw React Flow JSON
- The canonical shape should stay close to React Flow `nodes`, `edges`, and `viewport`
- Stable IDs matter because saved diagrams must support repeated IDE and UI edits
- The schema must support validation, visual editing, rendering, saving, and IDE-based updates
- React Flow runtime or session-only fields must not be persisted

## 3. Supported Diagram Types

- `activity_diagram`
- `use_case_diagram`
- `bdd_diagram`

## 4. Top-Level Structure

```json
{
  "schemaVersion": "graphpilot.diagram.v1",
  "kind": "diagram",
  "diagramType": "activity_diagram",
  "id": "diagram_example",
  "name": "Example Diagram",
  "metadata": {
    "source": "mcp",
    "blueprintKey": "activity_diagram.curated"
  },
  "viewport": { "x": 0, "y": 0, "zoom": 1 },
  "nodes": [],
  "edges": []
}
```

### Top-level fields

| Field | Required | Purpose |
| --- | --- | --- |
| `schemaVersion` | Yes | Identifies the diagram schema version |
| `kind` | Yes | Must be `diagram` |
| `diagramType` | Yes | Supported diagram family |
| `id` | Yes | Stable diagram identifier |
| `name` | Yes | Human-readable diagram name |
| `metadata` | Yes | Provenance and lightweight diagram metadata |
| `viewport` | Yes | Saved editor viewport as `{ x, y, zoom }` |
| `nodes` | Yes | Diagram nodes |
| `edges` | Yes | Diagram edges |

Notes:

- Use top-level `viewport`, not `canvas.viewport`.
- Do not include top-level `groups` for MVP.
- If grouping is needed later, prefer React Flow-compatible `parentId`.

## 5. Nodes

Nodes should stay close to the React Flow node shape.

```json
{
  "id": "node_start",
  "type": "activityNode",
  "position": { "x": 100, "y": 100 },
  "width": 160,
  "height": 60,
  "data": {
    "label": "Start",
    "semanticType": "start",
    "description": "",
    "metadata": {}
  },
  "style": {
    "background": "#ffffff",
    "borderColor": "#333333",
    "color": "#111111",
    "borderWidth": 1,
    "borderStyle": "solid"
  }
}
```

### Required node fields

- `id`
- `type`
- `position`
- `data`
- `data.label`

### Optional node fields

- `width`
- `height`
- `data.semanticType`
- `data.description`
- `data.metadata`
- `style`
- `parentId`

### Node field notes

- `id` must be stable and unique within the diagram.
- `type` is the React Flow rendering/component type.
- `data.semanticType` stores the diagram meaning.
- `width` and `height` are saved intended dimensions, not React Flow runtime measurements.
- `data.metadata` is optional and should stay lightweight.
- `parentId` is not required for MVP but is the preferred future grouping mechanism.
- `data.compartments` (BDD only, optional) is an ordered list of feature compartments —
  `[{ "label": string, "items": string[] }]` (e.g. a block's `parts`/`values`, or an
  `enumeration`'s `literals`). It is additive under the open `data` object (no schema
  change) and is rendered identically on the canvas and the SVG export.

### Recommended node types

These are the per-type React Flow rendering types defined by the type profile (`backend/services/diagrams/catalog/diagram_types.py`); edges use the `default` rendering type:

- `activityNode`
- `useCaseNode`
- `bddNode`

### Recommended semantic types

Anchored to **UML 2.5.1** (activity, use case) and **SysML 1.6** (BDD). Node semantic types:

- `activity_diagram`: `start`, `action`, `decision`, `merge`, `end`, `note`, `fork`, `join`
- `use_case_diagram`: `actor`, `useCase`, `systemBoundary`, `note`
- `bdd_diagram`: `block`, `part`, `value`, `constraint`, `note`, `enumeration`

Edge semantic types:

- `activity_diagram`: `flow`
- `use_case_diagram`: `association`, `include`, `extend`, `generalization`
- `bdd_diagram`: `composition`, `aggregation`, `association`, `reference`, `generalization`

The per-type `diagram-schemas/<type>-diagram-blueprints.md` docs carry the canonical shape/marker notation (and the deferred "advanced" elements). `data.semanticType` stays a **free string** in the schema so freeform `custom` diagrams are never blocked on save; the type profile (`backend/services/diagrams/catalog/diagram_types.py`) is the enforced allowed-list for `generated` diagrams.

For MVP, use case system boundaries should be represented as nodes.

### Supported node style subset

- `background`
- `borderColor`
- `color`
- `borderWidth`
- `borderStyle`

## 6. Edges

Edges should also stay close to the React Flow edge shape.

```json
{
  "id": "edge_start_to_action",
  "type": "default",
  "source": "node_start",
  "target": "node_action",
  "label": "Next",
  "data": {
    "semanticType": "flow",
    "description": "",
    "metadata": {}
  },
  "style": {
    "stroke": "#333333",
    "strokeWidth": 2
  }
}
```

### Required edge fields

- `id`
- `source`
- `target`

### Optional edge fields

- `type`
- `label`
- `data`
- `data.semanticType`
- `data.description`
- `data.metadata`
- `style`
- `sourceHandle`
- `targetHandle`

### Edge field notes

- Use `source` and `target`, not `from` and `to`.
- `label` stays at the top level.
- `data.metadata` is optional and should stay lightweight.
- `sourceHandle` and `targetHandle` are allowed but not required for MVP.

### Supported edge style subset

- `stroke`
- `strokeWidth`
- `strokeDasharray`

## 7. Metadata

Common top-level metadata fields may include:

- `source`
- `blueprintKey`
- `createdAt`
- `updatedAt`
- `generatedBy`
- `notes`

Metadata should stay lightweight and should not become a dump for runtime UI state.

## 8. Runtime Fields to Exclude

Do not persist React Flow runtime or session-only fields such as:

- `selected`
- `dragging`
- `resizing`
- `measured`
- `internals`
- other session-only or computed UI state

The canonical schema (`backend/assets/schemas/diagram.json`) is **strict**: it sets `additionalProperties: false` at the top level and on every node and edge, so unknown fields (including the runtime fields above) are rejected on save rather than silently stored. The open extension points are `data` and `metadata` (both `additionalProperties: true`), which is where lightweight, app-defined fields belong. This strictness is exactly why the frontend reverse adapter whitelists canonical fields rather than copying React Flow state wholesale — see `01-diagram-json-mapping-design.md`.

## 9. Validation Rules

Core MVP validation rules:

- `schemaVersion` is required
- `kind` must be `diagram`
- `diagramType` must be supported
- node IDs must be unique
- edge IDs must be unique
- edge `source` and `target` must reference existing node IDs
- `data.label` must be present on each node
- invalid diagrams must not be saved

## 10. Minimal Example

```json
{
  "schemaVersion": "graphpilot.diagram.v1",
  "kind": "diagram",
  "diagramType": "activity_diagram",
  "id": "diagram_order_review",
  "name": "Order Review",
  "metadata": {
    "source": "mcp",
    "blueprintKey": "activity_diagram.curated",
    "createdAt": "2026-06-23T10:00:00Z",
    "updatedAt": "2026-06-23T10:00:00Z"
  },
  "viewport": { "x": 0, "y": 0, "zoom": 1 },
  "nodes": [
    {
      "id": "node_start",
      "type": "activityNode",
      "position": { "x": 80, "y": 80 },
      "width": 140,
      "height": 60,
      "data": {
        "label": "Start",
        "semanticType": "start",
        "description": "",
        "metadata": {}
      },
      "style": {
        "background": "#ffffff",
        "borderColor": "#333333",
        "color": "#111111",
        "borderWidth": 1,
        "borderStyle": "solid"
      }
    },
    {
      "id": "node_review",
      "type": "activityNode",
      "position": { "x": 280, "y": 80 },
      "width": 180,
      "height": 60,
      "data": {
        "label": "Review Order",
        "semanticType": "action",
        "description": "",
        "metadata": {}
      },
      "style": {
        "background": "#ffffff",
        "borderColor": "#333333",
        "color": "#111111",
        "borderWidth": 1,
        "borderStyle": "solid"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_start_to_review",
      "type": "default",
      "source": "node_start",
      "target": "node_review",
      "label": "Next",
      "data": {
        "semanticType": "flow",
        "description": "",
        "metadata": {}
      },
      "style": {
        "stroke": "#333333",
        "strokeWidth": 2
      }
    }
  ]
}
```