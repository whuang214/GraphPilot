/** @vitest-environment jsdom */
import { useState } from 'react'
import { afterEach, describe, expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import type { Edge, Node } from '@xyflow/react'
import { useUndoRedo } from './useUndoRedo'
import { useColorMode } from '@/editor/shell/useColorMode'
import { useRail } from '@/editor/shell/useRail'

function n(id: string): Node {
  return { id, position: { x: 0, y: 0 }, data: {} } as Node
}

// Harness that drives nodes/edges through real React state so the hook's refs
// update on rerender (mirrors how DiagramCanvas wires it).
function useUndoRedoHarness() {
  const [nodes, setNodes] = useState<Node[]>([n('a')])
  const [edges, setEdges] = useState<Edge[]>([])
  const ur = useUndoRedo(nodes, edges, setNodes, setEdges)
  return { nodes, setNodes, ...ur }
}

describe('useUndoRedo', () => {
  it('undoes and redoes node changes around a snapshot', () => {
    const { result } = renderHook(useUndoRedoHarness)
    expect(result.current.canUndo).toBe(false)

    act(() => result.current.takeSnapshot())
    act(() => result.current.setNodes([n('a'), n('b')]))
    expect(result.current.nodes.map((x) => x.id)).toEqual(['a', 'b'])
    expect(result.current.canUndo).toBe(true)

    act(() => result.current.undo())
    expect(result.current.nodes.map((x) => x.id)).toEqual(['a'])
    expect(result.current.canRedo).toBe(true)

    act(() => result.current.redo())
    expect(result.current.nodes.map((x) => x.id)).toEqual(['a', 'b'])
  })
})

describe('useColorMode', () => {
  afterEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('toggles the dark class and persists the choice', () => {
    const { result } = renderHook(() => useColorMode())
    expect(result.current.mode).toBe('light')
    act(() => result.current.toggle())
    expect(result.current.mode).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('gp.colorMode')).toBe('dark')
  })
})

describe('useRail', () => {
  afterEach(() => localStorage.clear())

  it('tracks width + collapsed and persists them', () => {
    const { result } = renderHook(() => useRail('gp.test.rail', 200))
    expect(result.current.width).toBe(200)
    expect(result.current.collapsed).toBe(false)

    act(() => result.current.setWidth(260))
    act(() => result.current.toggle())
    expect(result.current.width).toBe(260)
    expect(result.current.collapsed).toBe(true)

    const stored = JSON.parse(localStorage.getItem('gp.test.rail') as string) as { width: number; collapsed: boolean }
    expect(stored.width).toBe(260)
    expect(stored.collapsed).toBe(true)
  })
})
