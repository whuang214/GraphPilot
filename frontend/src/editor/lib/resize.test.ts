import { describe, expect, it } from 'vitest'
import type { Node } from '@xyflow/react'
import { applyNodeResize, MIN_NODE_HEIGHT, MIN_NODE_WIDTH } from './resize'

const nodes: Node[] = [
  { id: 'a', position: { x: 0, y: 0 }, data: {}, style: { width: 100, height: 50, background: '#fff' } },
  { id: 'b', position: { x: 0, y: 0 }, data: {} },
]

describe('applyNodeResize', () => {
  it('writes the rounded size into the target node style, preserving other style keys', () => {
    const out = applyNodeResize(nodes, 'a', 160.4, 80.6)
    const a = out.find((n) => n.id === 'a')
    // Size lands in `style` (where the reverse adapter reads it), other keys kept.
    expect(a?.style).toMatchObject({ width: 160, height: 81, background: '#fff' })
  })

  it('leaves other nodes untouched (same reference)', () => {
    const out = applyNodeResize(nodes, 'a', 200, 120)
    expect(out.find((n) => n.id === 'b')).toBe(nodes[1])
  })

  it('seeds style for a node that had none', () => {
    const out = applyNodeResize(nodes, 'b', 200, 120)
    expect(out.find((n) => n.id === 'b')?.style).toEqual({ width: 200, height: 120 })
  })

  it('clamps below-minimum sizes to the minimum', () => {
    const out = applyNodeResize(nodes, 'a', 5, 5)
    expect(out.find((n) => n.id === 'a')?.style).toMatchObject({
      width: MIN_NODE_WIDTH,
      height: MIN_NODE_HEIGHT,
    })
  })

  it('ignores non-finite resize events', () => {
    expect(applyNodeResize(nodes, 'a', Number.NaN, 80)).toBe(nodes)
  })
})
