import { describe, expect, it } from 'vitest'
import type { Edge, Node } from '@xyflow/react'
import { cloneSelectedElements } from './clone'

function node(id: string, selected: boolean, extra: Partial<Node> = {}): Node {
  return {
    id,
    type: 'gpNode',
    position: { x: 0, y: 0 },
    data: { label: id, semanticType: 'opaqueAction' },
    selected,
    ...extra,
  } as Node
}

describe('cloneSelectedElements', () => {
  it('returns nothing when no node is selected', () => {
    const res = cloneSelectedElements([node('a', false)], [])
    expect(res.nodes).toEqual([])
    expect(res.edges).toEqual([])
  })

  it('clones selected nodes with fresh ids, an offset, and preserved type/semanticType', () => {
    const a = node('a', true, { position: { x: 10, y: 20 } })
    const res = cloneSelectedElements([a, node('b', false)], [], 24)
    expect(res.nodes).toHaveLength(1)
    const clone = res.nodes[0]
    expect(clone.id).not.toBe('a')
    expect(clone.type).toBe('gpNode')
    expect(clone.position).toEqual({ x: 34, y: 44 })
    expect((clone.data as { semanticType?: string }).semanticType).toBe('opaqueAction')
    expect(clone.selected).toBe(true)
  })

  it('clones only edges whose endpoints are both selected, remapping ids', () => {
    const a = node('a', true)
    const b = node('b', true)
    const c = node('c', false)
    const edges: Edge[] = [
      { id: 'e_ab', source: 'a', target: 'b' } as Edge,
      { id: 'e_ac', source: 'a', target: 'c' } as Edge,
    ]
    const res = cloneSelectedElements([a, b, c], edges)
    expect(res.nodes).toHaveLength(2)
    expect(res.edges).toHaveLength(1)
    const ids = new Set(res.nodes.map((n) => n.id))
    expect(res.edges[0].id).not.toBe('e_ab')
    expect(ids.has(res.edges[0].source)).toBe(true)
    expect(ids.has(res.edges[0].target)).toBe(true)
  })

  it('translates manual edge waypoints with cloned endpoints', () => {
    const edge = {
      id: 'e_ab',
      source: 'a',
      target: 'b',
      data: {
        semanticType: 'dependency',
        gpRoute: {
          sourceAnchor: { side: 'right', offset: 0.5 },
          waypoints: [{ x: 50, y: 60 }],
          labelOffset: { x: 4, y: -8 },
        },
      },
    } as Edge
    const result = cloneSelectedElements([node('a', true), node('b', true)], [edge], 24)
    expect(result.edges[0].data?.gpRoute).toEqual({
      sourceAnchor: { side: 'right', offset: 0.5 },
      waypoints: [{ x: 74, y: 84 }],
      labelOffset: { x: 4, y: -8 },
    })
  })

  it('remaps parentId to the cloned parent when the parent is also cloned', () => {
    const parent = node('p', true)
    const child = node('c', true, { parentId: 'p' } as Partial<Node>)
    const res = cloneSelectedElements([parent, child], [])
    const clonedParent = res.nodes.find((n) => (n.data as { label?: string }).label === 'p')
    const clonedChild = res.nodes.find((n) => (n.data as { label?: string }).label === 'c')
    expect(clonedChild?.parentId).toBe(clonedParent?.id)
  })
})
