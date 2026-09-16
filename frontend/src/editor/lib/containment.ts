import type { Node } from '@xyflow/react'
import { isContainerSemantic } from './elementCatalog'

type XY = { x: number; y: number }

export const CANVAS_LAYER = {
  container: 0,
  edge: 1,
  node: 2,
  selectedNode: 3,
} as const

export function decorateNodeLayer(node: Node): Node {
  const semanticType = (node.data as { semanticType?: string } | undefined)?.semanticType
  const zIndex = isContainerSemantic(semanticType) ? CANVAS_LAYER.container : node.selected ? CANVAS_LAYER.selectedNode : CANVAS_LAYER.node
  return node.zIndex === zIndex ? node : { ...node, zIndex }
}

// A node's position is relative to its parent when parented; walk the parent chain
// to get its absolute canvas position. Guards against a parentId cycle.
export function absolutePosition(node: Node, byId: Map<string, Node>): XY {
  let x = node.position.x
  let y = node.position.y
  let parentId = node.parentId
  const seen = new Set<string>()
  while (parentId && !seen.has(parentId)) {
    seen.add(parentId)
    const parent = byId.get(parentId)
    if (!parent) break
    x += parent.position.x
    y += parent.position.y
    parentId = parent.parentId
  }
  return { x, y }
}

function depth(node: Node, byId: Map<string, Node>): number {
  let d = 0
  let parentId = node.parentId
  const seen = new Set<string>()
  while (parentId && !seen.has(parentId)) {
    seen.add(parentId)
    const parent = byId.get(parentId)
    if (!parent) break
    d += 1
    parentId = parent.parentId
  }
  return d
}

// Move `nodeId` under `newParentId` (or to the top level when `undefined`), keeping
// it visually put by converting between absolute and parent-relative coordinates.
// Nodes are re-sorted so a parent always precedes its children (a React Flow
// requirement). Used by drag-stop re-parenting so a node can be dragged into or out
// of a system-boundary container.
export function reparentNode(nodes: Node[], nodeId: string, newParentId: string | undefined): Node[] {
  const byId = new Map(nodes.map((n) => [n.id, n]))
  const node = byId.get(nodeId)
  if (!node || node.parentId === newParentId) return nodes
  if (newParentId) {
    if (!byId.has(newParentId)) return nodes
    let current: string | undefined = newParentId
    const seen = new Set<string>()
    while (current && !seen.has(current)) {
      if (current === nodeId) return nodes
      seen.add(current)
      current = byId.get(current)?.parentId
    }
  }

  const abs = absolutePosition(node, byId)
  let position: XY = abs
  if (newParentId) {
    const parent = byId.get(newParentId)
    if (parent) {
      const parentAbs = absolutePosition(parent, byId)
      position = { x: abs.x - parentAbs.x, y: abs.y - parentAbs.y }
    }
  }

  const updated = nodes.map((n) => (n.id === nodeId ? { ...n, position, parentId: newParentId } : n))
  const updatedById = new Map(updated.map((n) => [n.id, n]))
  return [...updated].sort((a, b) => depth(a, updatedById) - depth(b, updatedById))
}
