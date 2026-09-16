import { describe, expect, it } from 'vitest'
import type { Node } from '@xyflow/react'
import { decorateNodeLayer, reparentNode } from './containment'

function n(id: string, x: number, y: number, parentId?: string): Node {
  return { id, position: { x, y }, data: {}, ...(parentId ? { parentId } : {}) } as Node
}

describe('decorateNodeLayer', () => {
  it('keeps selected and unselected containers on the lowest display tier', () => {
    const container = { ...n('boundary', 10, 20), data: { semanticType: 'subject' }, selected: true }
    expect(decorateNodeLayer(container)).toMatchObject({ id: 'boundary', zIndex: 0, selected: true, position: { x: 10, y: 20 } })
    expect(decorateNodeLayer({ ...container, selected: false }).zIndex).toBe(0)
  })

  it('raises only selected ordinary nodes above their normal tier', () => {
    const node = { ...n('actor', 30, 40), data: { semanticType: 'actor' } }
    expect(decorateNodeLayer(node).zIndex).toBe(2)
    expect(decorateNodeLayer({ ...node, selected: true }).zIndex).toBe(3)
    expect(decorateNodeLayer({ ...node, parentId: 'boundary' }).parentId).toBe('boundary')
  })
})

describe('reparentNode', () => {
  it('un-parents: converts the position to absolute and clears parentId', () => {
    const nodes = [n('p', 100, 100), n('c', 10, 10, 'p')]
    const c = reparentNode(nodes, 'c', undefined).find((x) => x.id === 'c')!
    expect(c.parentId).toBeUndefined()
    expect(c.position).toEqual({ x: 110, y: 110 })
  })

  it('parents: converts the position to be relative to the new parent', () => {
    const nodes = [n('p', 100, 100), n('c', 110, 110)]
    const c = reparentNode(nodes, 'c', 'p').find((x) => x.id === 'c')!
    expect(c.parentId).toBe('p')
    expect(c.position).toEqual({ x: 10, y: 10 })
  })

  it('orders a parent before its child', () => {
    const out = reparentNode([n('c', 110, 110), n('p', 100, 100)], 'c', 'p')
    expect(out.findIndex((x) => x.id === 'p')).toBeLessThan(out.findIndex((x) => x.id === 'c'))
  })

  it('is a no-op when the parent is unchanged', () => {
    const nodes = [n('p', 100, 100), n('c', 10, 10, 'p')]
    expect(reparentNode(nodes, 'c', 'p')).toBe(nodes)
  })

  it('rejects a missing parent and a parent that would create a cycle', () => {
    const nodes = [n('p', 100, 100), n('c', 10, 10, 'p')]
    expect(reparentNode(nodes, 'p', 'missing')).toBe(nodes)
    expect(reparentNode(nodes, 'p', 'c')).toBe(nodes)
  })
})
