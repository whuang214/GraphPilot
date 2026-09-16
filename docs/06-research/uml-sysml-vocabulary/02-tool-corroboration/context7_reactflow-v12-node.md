### Set Node Dimensions with `width` and `height`

Source: https://reactflow.dev/learn/troubleshooting/migrate-to-v12

Use `width` and `height` properties directly on the node object to set fixed dimensions in v12.

```javascript
// in React Flow 11 you might have used node.style to set the dimensions
const nodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'input node' },
    position: { x: 250, y: 5 },
    style: { width: 180, height: 40 },
  },
];
```

```javascript
// in React Flow 12 you can used node.width and node.height to set the dimensions
const nodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'input node' },
    position: { x: 250, y: 5 },
    width: 180,
    height: 40,
  },
];
```

--------------------------------

### Node Type Fields

Source: https://reactflow.dev/api-reference/types/node

The `Node` type in React Flow defines the properties of a node, including its ID, position, data, and various visual and interactive attributes. Some properties like width and height are read-only and managed internally by React Flow.

```APIDOC
## Node Type Definition

### Description
Represents a node in the React Flow graph, containing all necessary information for rendering and interaction.

### Fields

- **`id`** (`string`): Unique identifier for the node.
- **`position`** (`XYPosition`): The node's position on the canvas.
- **`data`** (`NodeData`): Arbitrary data associated with the node.
- **`sourcePosition`** (`Position`): Controls the default source position for edges (relevant for default, source, target node types).
- **`targetPosition`** (`Position`): Controls the default target position for edges (relevant for default, source, target node types).
- **`hidden`** (`boolean`): Determines if the node is visible.
- **`selected`** (`boolean`): Indicates if the node is currently selected.
- **`dragging`** (`boolean`): Indicates if the node is being dragged.
- **`draggable`** (`boolean`): Allows or disallows dragging the node.
- **`selectable`** (`boolean`): Allows or disallows selecting the node.
- **`connectable`** (`boolean`): Allows or disallows connecting edges to this node.
- **`deletable`** (`boolean`): Allows or disallows deleting the node.
- **`dragHandle`** (`string`): CSS class name for elements that act as drag handles.
- **`width`** (`number`): Read-only. The calculated width of the node.
- **`height`** (`number`): Read-only. The calculated height of the node.
- **`initialWidth`** (`number`): The initial width of the node before measurement.
- **`initialHeight`** (`number`): The initial height of the node before measurement.
- **`parentId`** (`string`): The ID of the parent node for sub-flows.
- **`zIndex`** (`number`): The z-index of the node.
- **`extent`** (`CoordinateExtent | "parent" | null`): The boundary within which the node can be moved.
- **`expandParent`** (`boolean`): If true, the parent node expands when this node is dragged to its edge.
- **`ariaLabel`** (`string`): ARIA label for accessibility.
- **`origin`** (`NodeOrigin`): The origin of the node relative to its position.
- **`handles`** (`NodeHandle[]`): An array of node handles.
- **`measured`** (`{ width?: number; height?: number; }`): The measured dimensions of the node.
- **`type`** (`string | NodeType | (NodeType & undefined)`): The type of the node, defined in `nodeTypes`.
- **`style`** (`CSSProperties`): Custom CSS styles for the node.
- **`className`** (`string`): Custom CSS class names for the node.
- **`resizing`** (`boolean`): Indicates if the node is currently being resized.
- **`focusable`** (`boolean`): Indicates if the node is focusable.
- **`ariaRole`** (`AriaRole`): The ARIA role for the node element (`"group"` by default).
- **`domAttributes`** (`Omit<HTMLAttributes<HTMLDivElement>, "id" | "draggable" | "style" | "className" | "role" | "aria-label" | "defaultValue" | keyof DOMAttributes<HTMLDivElement>>`): Custom DOM attributes for the node's element.

### Notes
- `width` and `height` are read-only and calculated by React Flow. Use `style` or `className` for size control.
```

--------------------------------

### Set Node Dimensions - New API (v12+)

Source: https://reactflow.dev/llms-medium.txt

Example of setting node dimensions using 'width' and 'height' properties in React Flow v12+.

```js
// in React Flow 12 you can used node.width and node.height to set the dimensions
const nodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'input node' },
    position: { x: 250, y: 5 },
    width: 180,
    height: 40,
  },
];
```

--------------------------------

### Get Measured Node Dimensions - New API

Source: https://reactflow.dev/llms-medium.txt

How to access node width and height using the 'measured' property in React Flow v12+.

```js
// getting the measured width and height
const nodeWidth = node.measured?.width;
const nodeHeight = node.measured?.height;
```

--------------------------------

### NodeDimensionChange Type Definition

Source: https://reactflow.dev/llms-full.txt

Represents a change in a node's dimensions, including width, height, and resizing attributes.

```typescript
type NodeDimensionChange = {
  id: string
  type: "dimensions"
  dimensions?: Dimensions
  resizing?: boolean
  setAttributes?: boolean | "width" | "height"
};
```

--------------------------------

### Adding a Child Node with Parent ID and Extent

Source: https://reactflow.dev/learn/layouting/sub-flows

Use the `parentId` option to nest a node within another. Set `childExtent` to 'parent' to keep child nodes confined within their parent's boundaries. The `style` option can be used to set a fixed width and height for the parent node.

```javascript
const nodes = [
  // parent node
  {
    id: '1',
    type: 'group',
    data: { label: 'Group 1' },
    position: { x: 0, y: 0 },
    style: {
      width: 300,
      height: 300,
    },
  },
  // child node 1
  {
    id: '1-1',
    data: { label: 'child node 1' },
    position: { x: 50, y: 50 },
    parentId: '1',
    childExtent: 'parent',
  },
  // child node 2
  {
    id: '1-2',
    data: { label: 'child node 2' },
    position: { x: 50, y: 100 },
    parentId: '1',
    childExtent: 'parent',
  },
];
```

--------------------------------

### Inspect Node Properties

Source: https://reactflow.dev/llms-full.txt

Renders detailed information about each node, including its ID, type, position, dimensions, and data. This helps in understanding the state of individual nodes.

```tsx
export const NodeInspector = () => {
  const { getInternalNode } = useReactFlow();
  const nodes = useNodes();

  return (
    <ViewportPortal>
      <div className="text-secondary-foreground">
        {nodes.map((node) => {
          const internalNode = getInternalNode(node.id);
          if (!internalNode) {
            return null;
          }

          const absPosition = internalNode?.internals.positionAbsolute;

          return (
            <NodeInfo
              key={node.id}
              id={node.id}
              selected={!!node.selected}
              type={node.type || "default"}
              position={node.position}
              absPosition={absPosition}
              width={node.measured?.width ?? 0}
              height={node.measured?.height ?? 0}
              data={node.data}
            />
          );
        })}
      </div>
    </ViewportPortal>
  );
};
```

```tsx
const NodeInfo = ({ 
  id,
  type,
  selected,
  position,
  absPosition,
  width,
  height,
  data,
}: NodeInfoProps) => {
  if (!width || !height) return null;

  const absoluteTransform = `translate(${absPosition.x}px, ${absPosition.y + height}px)`;
  const formattedPosition = `${position.x.toFixed(1)}, ${position.y.toFixed(1)}`;
  const formattedDimensions = `${width} × ${height}`;
  const selectionStatus = selected ? "Selected" : "Not Selected";

  return (
    <div
      style={{
        position: "absolute",
        transform: absoluteTransform,
        width: width * 2,
      }}
      className="text-xs"
    >
      <div>id: {id}</div>
      <div>type: {type}</div>
      <div>selected: {selectionStatus}</div>
      <div>position: {formattedPosition}</div>
      <div>dimensions: {formattedDimensions}</div>
      <div>data: {JSON.stringify(data, null, 2)}</div>
    </div>
  );
};
```

--------------------------------

### Default Nodes for React Flow (Simplified)

Source: https://reactflow.dev/llms-medium.txt

Defines a simplified set of nodes for a React Flow graph, omitting explicit styling properties. Includes basic node properties like id, type, data, and position.

```jsx
export const defaultNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Input Node' },
    position: { x: 250, y: 25 },
  },

  {
    id: '2',
    // you can also pass a React component as a label
    data: { label: <div>Default Node</div> },
    position: { x: 100, y: 125 },
  },
  {
    id: '3',
    type: 'output',
    data: { label: 'Output Node' },
    position: { x: 250, y: 250 },
  },
];
```

--------------------------------

### Using a Default Node Type as a Parent with Non-Draggable Children

Source: https://reactflow.dev/learn/layouting/sub-flows

Demonstrates using a standard node type as a parent and setting child nodes to be non-draggable using the `draggable: false` option.

```javascript
const nodes = [
  // parent node
  {
    id: '1',
    data: { label: 'Node B' },
    position: { x: 0, y: 0 },
  },
  // child node 1
  {
    id: '1-1',
    data: { label: 'Child Node 1' },
    position: { x: 50, y: 50 },
    parentId: '1',
    draggable: false,
  },
  // child node 2
  {
    id: '1-2',
    data: { label: 'Child Node 2' },
    position: { x: 50, y: 100 },
    parentId: '1',
    draggable: false,
  },
  {
    id: '2',
    data: { label: 'Child 1' },
    position: { x: 100, y: 200 },
  },
  {
    id: '3',
    data: { label: 'Child 2' },
    position: { x: 200, y: 200 },
  },
  {
    id: '4',
    data: { label: 'Child 3' },
    position: { x: 300, y: 200 },
  },
  {
    id: '5',
    data: { label: 'Node C' },
    position: { x: 400, y: 200 },
  },
];

const edges = [
  {
    id: 'e1-1',
    source: '1-1',
    target: '1-2',
  },
  {
    id: 'e2-3',
    source: '2',
    target: '3',
  },
  {
    id: 'e3-4',
    source: '3',
    target: '4',
  },
  {
    id: 'e4-5',
    source: '4',
    target: '5',
  },
];
```

--------------------------------

### Node

Source: https://reactflow.dev/api-reference/types

The Node type represents everything React Flow needs to know about a given node. Many of these properties can be manipulated both by React Flow or by you, but some such as width and height should be considered read-only.

```APIDOC
## Node

### Description
The Node type represents everything React Flow needs to know about a given node. Many of these properties can be manipulated both by React Flow or by you, but some such as width and height should be considered read-only.

### Type
object

### Properties
- **id** (string) - Required - Unique identifier for the node.
- **type** (string) - Optional - The type of the node (e.g., 'input', 'output', 'default', 'custom').
- **data** (any) - Optional - Custom data associated with the node.
- **position** (object) - Required - The position of the node.
  - **x** (number) - Required - The x-coordinate.
  - **y** (number) - Required - The y-coordinate.
- **style** (object) - Optional - Style for the node.
- **className** (string) - Optional - CSS class for the node.
- **hidden** (boolean) - Optional - Whether the node is hidden.
- **draggable** (boolean) - Optional - Whether the node is draggable.
- **selectable** (boolean) - Optional - Whether the node is selectable.
- **dragHandle** (string) - Optional - CSS selector for the drag handle.
- **width** (number) - Optional - The width of the node (read-only after initial render).
- **height** (number) - Optional - The height of the node (read-only after initial render).
- **parentNodeId** (string) - Optional - The ID of the parent node for nested nodes.
- **expandParent** (boolean) - Optional - Whether to expand the parent node when this node is interacted with.
```

--------------------------------

### Specifying Static Node Dimensions for SSR

Source: https://reactflow.dev/learn/advanced-use/ssr-ssg-configuration

Provide explicit `width` and `height` for nodes when rendering on the server. These values are used as inline styles.

```javascript
const nodes = [
  {
    id: '1',
    type: 'default',
    position: { x: 0, y: 0 },
    data: { label: 'Node 1' },
    width: 100,
    height: 50,
  },
];
```

--------------------------------

### Specifying Dynamic Node Dimensions for SSR

Source: https://reactflow.dev/learn/advanced-use/ssr-ssg-configuration

Use `initialWidth` and `initialHeight` for nodes with dynamic dimensions that are not known in advance or may change. These are used for the first render only.

```javascript
const nodes: Node[] = [
  {
    id: '1',
    type: 'default',
    position: { x: 0, y: 0 },
    data: { label: 'Node 1' },
    width: 100,
    height: 50,
    handles: [
      {
        type: 'target',
        position: Position.Top,
        x: 100 / 2,
        y: 0,
      },
      {
        type: 'source',
        position: Position.Bottom,
        x: 100 / 2,
        y: 50,
      },
    ],
  },
];
```

--------------------------------

### Default Nodes for React Flow

Source: https://reactflow.dev/llms-medium.txt

Defines the initial set of nodes for a React Flow graph. Includes basic node properties like id, type, data, position, and styling.

```jsx
export const defaultNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Input Node' },
    position: { x: 250, y: 25 },
    style: { backgroundColor: '#6ede87', color: 'white' },
  },

  {
    id: '2',
    // you can also pass a React component as a label
    data: { label: <div>Default Node</div> },
    position: { x: 100, y: 125 },
    style: { backgroundColor: '#ff0072', color: 'white' },
  },
  {
    id: '3',
    type: 'output',
    data: { label: 'Output Node' },
    position: { x: 250, y: 250 },
    style: { backgroundColor: '#6865A5', color: 'white' },
  },
];
```

--------------------------------

### Access Measured Node Dimensions

Source: https://reactflow.dev/learn/troubleshooting/migrate-to-v12

Retrieve measured node width and height from `node.measured` in v12.

```javascript
// getting the measured width and height
const nodeWidth = node.width;
const nodeHeight = node.height;
```

```javascript
// getting the measured width and height
const nodeWidth = node.measured?.width;
const nodeHeight = node.measured?.height;
```