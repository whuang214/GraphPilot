### Correct Edge Creation with Source and Target

Source: https://reactflow.dev/learn/troubleshooting/common-errors

Ensure edges have 'source' and 'target' properties defined to be rendered correctly. This example shows the correct way to define an edge.

```javascript
import { ReactFlow } from '@xyflow/react';

const nodes = [
  /* ... */
];

const edges = [
  {
    source: '1',
    target: '2',
  },
];

function Flow(props) {
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

--------------------------------

### Incorrect Edge Creation without Source and Target

Source: https://reactflow.dev/learn/troubleshooting/common-errors

Edges without 'source' and 'target' properties will not be rendered and will trigger a warning. This example demonstrates the incorrect setup.

```javascript
import { ReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodes = [
  /* ... */
];

const edges = [
  {
    nosource: '1',
    notarget: '2',
  },
];

function Flow(props) {
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

--------------------------------

### Resolve 'Can't create edge' warning by providing source and target

Source: https://reactflow.dev/llms-medium.txt

This warning occurs when an edge object is missing 'source' and 'target' properties. Ensure both are provided for the edge to render.

```jsx
import { ReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodes = [
  /* ... */
];

const edges = [
  {
    nosource: '1',
    notarget: '2',
  },
];

function Flow(props) {
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

```jsx
import { ReactFlow } from '@xyflow/react';

const nodes = [
  /* ... */
];

const edges = [
  {
    source: '1',
    target: '2',
  },
];

function Flow(props) {
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

--------------------------------

### EdgeMarker Type Definition

Source: https://reactflow.dev/api-reference/types/edge-marker

Defines the structure and available fields for configuring edge markers in React Flow. This type is used to specify properties like marker type, color, size, and stroke.

```APIDOC
## EdgeMarker

### Description

The `EdgeMarker` type is used to configure markers at the start and end of an edge. It allows for customization of various visual properties.

### Fields

#### `type`
- **Type**: `MarkerType | "arrow" | "arrowclosed"`
- **Description**: Specifies the type of the edge marker. Can be one of the predefined `MarkerType` values or a string literal like "arrow" or "arrowclosed".

#### `color`
- **Type**: `string | null`
- **Description**: The color of the edge marker. Can be a string representing a color or null.

#### `width`
- **Type**: `number`
- **Description**: The width of the edge marker.

#### `height`
- **Type**: `number`
- **Description**: The height of the edge marker.

#### `markerUnits`
- **Type**: `string`
- **Description**: Defines the coordinate system for the marker.

#### `orient`
- **Type**: `string`
- **Description**: Specifies the orientation of the marker.

#### `strokeWidth`
- **Type**: `number`
- **Description**: The stroke width of the edge marker.
```

--------------------------------

### Edge Properties

Source: https://reactflow.dev/api-reference/types/edge

This details the common properties available for all Edge types in React Flow, used for identification, rendering, and interaction.

```APIDOC
## Edge Properties

### Description

These are the common properties for any `Edge` object in React Flow. They define the edge's identity, appearance, and behavior.

### Properties

- **`id`** (`string`) - Unique identifier for the edge.
- **`type`** (`EdgeType`) - The type of the edge, referencing registered edge types.
- **`source`** (`string`) - The ID of the source node.
- **`target`** (`string`) - The ID of the target node.
- **`sourceHandle`** (`string | null`) - The ID of the source handle, used when nodes have multiple handles.
- **`targetHandle`** (`string | null`) - The ID of the target handle, used when nodes have multiple handles.
- **`animated`** (`boolean`) - Whether the edge should be rendered with an animation.
- **`hidden`** (`boolean`) - Whether the edge should be hidden.
- **`deletable`** (`boolean`) - Whether the edge can be deleted by the user.
- **`selectable`** (`boolean`) - Whether the edge can be selected.
- **`data`** (`EdgeData`) - Arbitrary data that can be passed to the edge component.
- **`selected`** (`boolean`) - Whether the edge is currently selected.
- **`markerStart`** (`EdgeMarkerType`) - Configuration for the marker at the start of the edge.
- **`markerEnd`** (`EdgeMarkerType`) - Configuration for the marker at the end of the edge.
- **`zIndex`** (`number`) - The z-index of the edge for stacking order.
- **`ariaLabel`** (`string`) - ARIA label for accessibility.
- **`interactionWidth`** (`number`) - The width of the invisible clickable area around the edge.
- **`label`** (`ReactNode`) - Content to display as the edge label.
- **`labelStyle`** (`CSSProperties`) - Custom CSS styles for the edge label.
- **`labelShowBg`** (`boolean`) - Whether to show a background for the edge label.
- **`labelBgStyle`** (`CSSProperties`) - Custom CSS styles for the edge label background.
- **`labelBgPadding`** (`[number, number]`) - Padding around the edge label background.
- **`labelBgBorderRadius`** (`number`) - Border radius for the edge label background.
- **`style`** (`CSSProperties`) - Custom CSS styles for the edge itself.
- **`className`** (`string`) - Custom CSS class names for the edge.
- **`reconnectable`** (`boolean | HandleType`) - Determines if the edge can be reconnected.
- **`focusable`** (`boolean`) - Whether the edge is focusable for accessibility.
- **`ariaRole`** (`AriaRole`) - The ARIA role for the edge element.
- **`domAttributes`** (`Omit<SVGAttributes<SVGGElement>, "id" | "style" | "className" | "role" | "aria-label" | "dangerouslySetInnerHTML">`) - Allows adding custom SVG attributes to the edge's DOM element.
```

--------------------------------

### MarkerType Enum

Source: https://reactflow.dev/api-reference/types/marker-type

Defines the available marker types for edges. Use 'arrow' for an open arrow or 'arrowclosed' for a filled arrow.

```typescript
export enum MarkerType {
  Arrow = 'arrow',
  ArrowClosed = 'arrowclosed',
}
```

--------------------------------

### Update Edge Marker Configuration

Source: https://reactflow.dev/learn/troubleshooting/migrate-to-v10

The `arrowHeadType` property is deprecated. Use `markerStart` and `markerEnd` which accept either a string ID or a configuration object for built-in markers.

```javascript
const markerEdge = { source: '1', target: '2', arrowHeadType: 'arrow' };
```

```javascript
const markerEdge = {
  source: '1',
  target: '2',
  markerStart: 'myCustomSvgMarker',
  markerEnd: { type: 'arrow', color: '#f00' },
};
```

--------------------------------

### MarkerType

Source: https://reactflow.dev/api-reference/types

Edges may optionally have a marker on either end. The MarkerType type enumerates the options available to you when configuring a given marker.

```APIDOC
## MarkerType

### Description
Edges may optionally have a marker on either end. The MarkerType type enumerates the options available to you when configuring a given marker.

### Type
string (enum-like values: 'arrow', 'arrowclosed', 'point')
```

--------------------------------

### NodeConnection Type Definition

Source: https://reactflow.dev/api-reference/types/node-connection

Defines the structure of the NodeConnection type, which extends the basic Connection type by adding the `edgeId` field. It includes fields for source node, target node, source handle, target handle, and the edge ID.

```APIDOC
## NodeConnection

### Description
The `NodeConnection` type is an extension of a basic Connection that includes the `edgeId`.

### Fields

- **source** (string) - The id of the node this connection originates from.
- **target** (string) - The id of the node this connection terminates at.
- **sourceHandle** (string | null) - When not `null`, the id of the handle on the source node that this connection originates from.
- **targetHandle** (string | null) - When not `null`, the id of the handle on the target node that this connection terminates at.
- **edgeId** (string) - The ID of the edge associated with this connection.
```

--------------------------------

### EdgeMarker

Source: https://reactflow.dev/api-reference/types

Edges can optionally have markers at the start and end of an edge. The EdgeMarker type is used to configure those markers! Check the docs for MarkerType for details on what types of edge marker are available.

```APIDOC
## EdgeMarker

### Description
Edges can optionally have markers at the start and end of an edge. The EdgeMarker type is used to configure those markers! Check the docs for MarkerType for details on what types of edge marker are available.

### Type
object

### Properties
- **type** (MarkerType) - Required - The type of the marker.
- **color** (string) - Optional - The color of the marker.
- **width** (number) - Optional - The width of the marker.
- **height** (number) - Optional - The height of the marker.
- **offset** (number) - Optional - An offset for the marker position.
```

--------------------------------

### Improved marker customization with markerStart and markerEnd

Source: https://reactflow.dev/llms-medium.txt

The API for customizing edge markers has been improved. `markerStart` and `markerEnd` can accept a string ID or a configuration object for built-in markers.

```js
const markerEdge = {
  source: '1',
  target: '2',
  markerStart: 'myCustomSvgMarker',
  markerEnd: { type: 'arrow', color: '#f00' },
};
```

--------------------------------

### Initial Edges for React Flow Graph

Source: https://reactflow.dev/llms-medium.txt

Defines the initial set of edges connecting nodes in a React Flow graph. Includes source and target node IDs, edge IDs, and an animated property. Useful for setting up default connections.

```javascript
export const initialEdges = [
  { id: 'e12', source: '1', target: '2', animated: true },
  { id: 'e13', source: '1', target: '3', animated: true },
  { id: 'e22a', source: '2', target: '2a', animated: true },
  { id: 'e22b', source: '2', target: '2b', animated: true },
  { id: 'e22c', source: '2', target: '2c', animated: true },
  { id: 'e2c2d', source: '2c', target: '2d', animated: true },
];
```