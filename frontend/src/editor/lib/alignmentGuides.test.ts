import { describe, expect, it } from 'vitest'
import type { Node, NodePositionChange } from '@xyflow/react'
import { getHelperLines } from './alignmentGuides'

const nodes: Node[] = [
  { id: 'a', position: { x: 103, y: 53 }, data: {}, measured: { width: 100, height: 40 } },
  { id: 'b', position: { x: 100, y: 200 }, data: {}, measured: { width: 100, height: 40 } },
]

function move(x: number, y: number): NodePositionChange {
  return { id: 'a', type: 'position', position: { x, y }, dragging: true }
}

describe('getHelperLines', () => {
  it('snaps to a near left/left and top alignment and reports the guide lines', () => {
    // a.left=103 is within 5px of b.left=100 -> vertical guide at 100, snap x=100.
    const result = getHelperLines(move(103, 53), nodes)
    expect(result.vertical).toBe(100)
    expect(result.snapPosition.x).toBe(100)
  })

  it('snaps right edges together (snap x accounts for node width)', () => {
    // Narrower 'a' so only the right edges align (left/center are far away):
    // a.right ~ b.right=200 -> a.x = 200 - 60 = 140.
    const ns: Node[] = [
      { id: 'a', position: { x: 0, y: 0 }, data: {}, measured: { width: 60, height: 40 } },
      { id: 'b', position: { x: 100, y: 0 }, data: {}, measured: { width: 100, height: 40 } },
    ]
    const result = getHelperLines({ id: 'a', type: 'position', position: { x: 141, y: 0 }, dragging: true }, ns)
    expect(result.vertical).toBe(200)
    expect(result.snapPosition.x).toBe(140)
  })

  it('aligns parented and top-level nodes in absolute canvas coordinates', () => {
    const nested: Node[] = [
      { id: 'parent', position: { x: 100, y: 100 }, data: {}, measured: { width: 300, height: 200 } },
      { id: 'child', parentId: 'parent', position: { x: 95, y: 0 }, data: {}, measured: { width: 60, height: 40 } },
      { id: 'top', position: { x: 200, y: 100 }, data: {}, measured: { width: 100, height: 40 } },
    ]
    const result = getHelperLines(
      { id: 'child', type: 'position', position: { x: 96, y: 0 }, dragging: true },
      nested,
    )
    expect(result.vertical).toBe(200)
    expect(result.snapPosition.x).toBe(100)
  })

  it('does not snap a dragged container to descendants that move with it', () => {
    const nested: Node[] = [
      { id: 'parent', position: { x: 100, y: 100 }, data: {}, measured: { width: 300, height: 200 } },
      { id: 'child', parentId: 'parent', position: { x: 5, y: 5 }, data: {}, measured: { width: 60, height: 40 } },
      { id: 'grandchild', parentId: 'child', position: { x: 5, y: 5 }, data: {}, measured: { width: 20, height: 20 } },
    ]
    const result = getHelperLines(
      { id: 'parent', type: 'position', position: { x: 103, y: 103 }, dragging: true },
      nested,
    )
    expect(result.vertical).toBeUndefined()
    expect(result.horizontal).toBeUndefined()
    expect(result.snapPosition).toEqual({})
  })

  it('returns no guides when the node is far from others', () => {
    const result = getHelperLines(move(500, 500), nodes)
    expect(result.vertical).toBeUndefined()
    expect(result.horizontal).toBeUndefined()
    expect(result.snapPosition).toEqual({})
  })

  it('returns an empty result for an unknown node or missing position', () => {
    expect(getHelperLines({ id: 'zzz', type: 'position', position: { x: 0, y: 0 } }, nodes).snapPosition).toEqual({})
    expect(getHelperLines({ id: 'a', type: 'position' }, nodes).snapPosition).toEqual({})
  })
})
