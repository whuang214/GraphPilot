import type { Edge, Node } from '@xyflow/react'
import { newNodeId } from './palette'
import { normalizeRouteGeometry, translateRouteWaypoints } from './edgeRouting'

function newEdgeId(source: string, target: string): string {
  return `edge_${source}_${target}_${Math.random().toString(36).slice(2, 8)}`
}

// Clone the currently-selected nodes (and any edges whose endpoints are both in
// the selection) with fresh ids and a position offset. `parentId` is remapped
// when the parent is also cloned. Used by duplicate (Ctrl+D) and paste (Ctrl+V).
export function cloneSelectedElements(
  nodes: Node[],
  edges: Edge[],
  offset = 24,
): { nodes: Node[]; edges: Edge[] } {
  const selected = nodes.filter((n) => n.selected)
  if (selected.length === 0) return { nodes: [], edges: [] }

  const idMap = new Map<string, string>()
  const clonedNodes: Node[] = selected.map((n) => {
    const semanticType = (n.data as { semanticType?: string } | undefined)?.semanticType ?? 'node'
    const id = newNodeId(String(semanticType))
    idMap.set(n.id, id)
    return {
      ...n,
      id,
      position: { x: n.position.x + offset, y: n.position.y + offset },
      selected: true,
      data: { ...n.data },
    }
  })

  for (const c of clonedNodes) {
    if (c.parentId && idMap.has(c.parentId)) c.parentId = idMap.get(c.parentId)
  }

  const clonedEdges: Edge[] = edges
    .filter((e) => idMap.has(e.source) && idMap.has(e.target))
    .map((e) => {
      const source = idMap.get(e.source) as string
      const target = idMap.get(e.target) as string
      const data = { ...(e.data ?? {}) }
      const route = normalizeRouteGeometry(data.gpRoute)
      if (route?.waypoints?.length) data.gpRoute = translateRouteWaypoints(route, offset, offset)
      return { ...e, id: newEdgeId(source, target), source, target, selected: true, data }
    })

  return { nodes: clonedNodes, edges: clonedEdges }
}
