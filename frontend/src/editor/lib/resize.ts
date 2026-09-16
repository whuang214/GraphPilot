import { createContext, useContext } from 'react'
import type { Node } from '@xyflow/react'

// Minimum on-canvas node size (also passed to React Flow's NodeResizer so the
// handles can't drag below it).
export const MIN_NODE_WIDTH = 40
export const MIN_NODE_HEIGHT = 30

// Write a resized size into the target node's wrapper `style`, clamped to the
// minimum and rounded to whole pixels, preserving any other style keys. Size is
// kept in `style` (not React Flow's measured `width`/`height`) because that is
// where the reverse adapter reads node size from — which is what keeps the
// load -> edit -> save round-trip byte-stable.
export function applyNodeResize(
  nodes: Node[],
  id: string,
  width: number,
  height: number,
): Node[] {
  if (!Number.isFinite(width) || !Number.isFinite(height)) return nodes
  const w = Math.max(MIN_NODE_WIDTH, Math.round(width))
  const h = Math.max(MIN_NODE_HEIGHT, Math.round(height))
  return nodes.map((n) =>
    n.id === id ? { ...n, style: { ...(n.style ?? {}), width: w, height: h } } : n,
  )
}

// Resize handlers shared with the custom node renderers (which host the
// NodeResizer): `start` takes one undo snapshot at the drag start; `resize`
// persists the live size into the node style and marks the diagram edited.
export interface NodeResizeApi {
  start: () => void
  resize: (id: string, width: number, height: number) => void
}

export const NodeResizeContext = createContext<NodeResizeApi | null>(null)

export function useNodeResize(): NodeResizeApi | null {
  return useContext(NodeResizeContext)
}
