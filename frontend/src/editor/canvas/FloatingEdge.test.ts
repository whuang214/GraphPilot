/** @vitest-environment jsdom */
import { createElement } from 'react'
import type { ReactNode } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import type { EdgeProps } from '@xyflow/react'
import { edgeDisplayLabel, relationshipEndLabel } from '@/editor/lib/edgePresentation'
import { EdgeRouteEditContext } from '@/editor/lib/edgeRouteEdit'
import type { RouteGeometry } from '@/editor/lib/edgeRouting'
import { FloatingEdge } from './FloatingEdge'

vi.mock('@xyflow/react', async () => {
  const React = await import('react')
  return {
    BaseEdge: ({ id, path }: { id: string; path: string }) => React.createElement('svg', null, React.createElement('path', { 'data-testid': `path-${id}`, d: path })),
    EdgeLabelRenderer: ({ children }: { children: ReactNode }) => React.createElement(React.Fragment, null, children),
    useInternalNode: (id: string) => ({
      id,
      internals: { positionAbsolute: id === 'source' ? { x: 0, y: 80 } : { x: 400, y: 180 } },
      measured: { width: 100, height: 60 },
      data: { semanticType: 'block' },
    }),
    useReactFlow: () => ({ screenToFlowPosition: (point: { x: number; y: number }) => point }),
  }
})

afterEach(cleanup)

const routeProps = {
  id: 'manual',
  source: 'source',
  target: 'target',
  selected: true,
  data: {
    semanticType: 'association',
    gpRoute: {
      sourceAnchor: { side: 'right', offset: 0.5 },
      targetAnchor: { side: 'left', offset: 0.5 },
      waypoints: [{ x: 160, y: 110 }, { x: 160, y: 40 }, { x: 320, y: 40 }, { x: 320, y: 210 }],
    },
  },
} as unknown as EdgeProps

function renderRouteControls(
  start: () => void,
  setRoute: (edgeId: string, route: RouteGeometry | undefined) => void,
  props: EdgeProps = routeProps,
) {
  return render(createElement(
    EdgeRouteEditContext.Provider,
    { value: { start, setRoute } },
    createElement(FloatingEdge, props),
  ))
}

describe('FloatingEdge semantic labels', () => {
  it('derives include and extend keywords without storing them as labels', () => {
    expect(edgeDisplayLabel(undefined, { semanticType: 'include' })).toBe('«include»')
    expect(edgeDisplayLabel('«include»', { semanticType: 'include' })).toBe('«include»')
    expect(edgeDisplayLabel('optional path', { semanticType: 'extend', condition: 'eligible' })).toBe(
      '«extend» optional path [eligible]',
    )
  })

  it('appends activity guards and leaves ordinary labels unchanged', () => {
    expect(edgeDisplayLabel('Approved', { semanticType: 'controlFlow', guard: 'valid' })).toBe('Approved [valid]')
    expect(edgeDisplayLabel('owns', { semanticType: 'association' })).toBe('owns')
  })

  it('formats relationship-end roles and multiplicities', () => {
    expect(relationshipEndLabel({ role: 'engine', multiplicity: { lower: 1, upper: '*' } })).toBe('engine 1..*')
    expect(relationshipEndLabel({ multiplicity: { lower: 1, upper: 1 } })).toBe('1')
    expect(relationshipEndLabel(undefined)).toBe('')
  })
})

describe('FloatingEdge route controls', () => {
  it('renders safe corner deletes and performs one action on click', () => {
    const start = vi.fn()
    const setRoute = vi.fn()
    renderRouteControls(start, setRoute)

    const corners = screen.getAllByRole('button', { name: /Delete detour at corner/ })
    expect(corners).toHaveLength(2)
    expect(screen.getAllByLabelText(/Move route segment/)).toHaveLength(5)
    expect(screen.queryByRole('button', { name: /Move route segment/ })).toBeNull()
    fireEvent.click(corners[0])
    expect(start).toHaveBeenCalledTimes(1)
    expect(setRoute).toHaveBeenCalledTimes(1)
  })

  it('renders a straight path without orthogonal segment or corner controls', () => {
    const straightProps = {
      ...routeProps,
      data: {
        semanticType: 'association',
        gpRoute: {
          mode: 'straight',
          sourceAnchor: { side: 'right', offset: 0.5 },
          targetAnchor: { side: 'left', offset: 0.5 },
        },
      },
    } as unknown as EdgeProps
    renderRouteControls(vi.fn(), vi.fn(), straightProps)
    expect(screen.getByTestId('path-manual').getAttribute('d')).toBe('M 100 110 L 400 210')
    expect(screen.queryByLabelText(/Move route segment/)).toBeNull()
    expect(screen.queryByRole('button', { name: /Delete detour at corner/ })).toBeNull()
    expect(screen.getByLabelText('Move source anchor')).toBeTruthy()
    expect(screen.getByLabelText('Move target anchor')).toBeTruthy()
  })

  it('maps both corners and deletion keys to one guarded detour action', () => {
    const start = vi.fn()
    const setRoute = vi.fn()
    renderRouteControls(start, setRoute)

    const corners = screen.getAllByRole('button', { name: /Delete detour at corner/ })
    fireEvent.click(corners[0])
    const firstRoute = setRoute.mock.calls[0][1]
    for (const key of ['Delete', 'Backspace']) {
      start.mockClear()
      setRoute.mockClear()
      fireEvent.keyDown(corners[1], { key })
      expect(start).toHaveBeenCalledTimes(1)
      expect(setRoute).toHaveBeenCalledWith('manual', firstRoute)
    }
    start.mockClear()
    setRoute.mockClear()
    fireEvent.click(corners[0], { detail: 1 })
    fireEvent.click(corners[0], { detail: 2 })
    expect(start).toHaveBeenCalledTimes(1)
    expect(setRoute).toHaveBeenCalledTimes(1)
  })
})
