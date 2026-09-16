/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CSSProperties, ReactNode } from 'react'
import { cleanup, render, screen } from '@testing-library/react'
import type { NodeProps } from '@xyflow/react'
import type { ModelFeatures } from '@/types/diagram'
import { NodeResizeContext } from '@/editor/lib/resize'
import { GpNode } from './customNodes'

const flowState = vi.hoisted(() => ({ zoom: 1, updateNodeInternals: vi.fn() }))

vi.mock('@xyflow/react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@xyflow/react')>()
  return {
    ...actual,
    Handle: ({ children, position, type, ...props }: { children?: ReactNode; position: string; type: string }) => (
      <div data-position={position} data-type={type} {...props}>{children}</div>
    ),
    NodeResizer: ({ handleStyle }: { handleStyle?: CSSProperties }) => <div data-testid="node-resizer" style={handleStyle} />,
    useStore: (selector: (state: { transform: [number, number, number] }) => unknown) => selector({ transform: [0, 0, flowState.zoom] }),
    useUpdateNodeInternals: () => flowState.updateNodeInternals,
  }
})

afterEach(() => {
  cleanup()
  flowState.zoom = 1
  flowState.updateNodeInternals.mockClear()
})

const resizeApi = { start: vi.fn(), resize: vi.fn() }

function renderClassifier(features?: ModelFeatures, stereotype?: string) {
  const props = {
    id: 'vehicle',
    data: { label: 'Vehicle', semanticType: 'block', features, stereotype },
    selected: false,
  } as unknown as NodeProps
  return render(<GpNode {...props} />)
}

describe('GpNode connection boundaries', () => {
  it('exposes full-side source and target strips instead of center dots', () => {
    renderClassifier()
    const source = screen.getAllByLabelText(/Start relationship on/)
    const target = screen.getAllByLabelText(/Finish relationship on/)
    expect(source).toHaveLength(4)
    expect(target).toHaveLength(4)
    expect(source.find((handle) => handle.getAttribute('data-position') === 'top')?.style.width).toBe('100%')
    expect(source.find((handle) => handle.getAttribute('data-position') === 'left')?.style.height).toBe('100%')
  })

  it('places narrow hit bands along all four diamond edges', () => {
    const props = {
      id: 'merge',
      data: { label: 'Merge', semanticType: 'mergeNode' },
      selected: false,
    } as unknown as NodeProps
    render(<GpNode {...props} />)
    const upperLeft = screen.getByLabelText('Start relationship on upper-left diamond edge')
    const upperRight = screen.getByLabelText('Start relationship on upper-right diamond edge')
    const lowerRight = screen.getByLabelText('Start relationship on lower-right diamond edge')
    const lowerLeft = screen.getByLabelText('Start relationship on lower-left diamond edge')
    const targetUpperLeft = screen.getByLabelText('Finish relationship on upper-left diamond edge')
    expect(upperLeft.style.cssText).toContain('clip-path')
    expect(targetUpperLeft.style.clipPath).toBe(upperLeft.style.clipPath)
    expect(upperLeft.style.left).toBe('0px')
    expect(upperLeft.style.top).toBe('0px')
    expect(upperRight.style.left).toBe('50%')
    expect(lowerRight.style.top).toBe('50%')
    expect(lowerLeft.style.left).toBe('0px')
  })

  it.each([
    ['initialNode', 'Initial Node', 90, 60, 'control circle', 37, -4.2, 16],
    ['activityFinalNode', 'Activity Final Node', 90, 60, 'control circle', 37, -4.2, 16],
    ['flowFinalNode', 'Flow Final Node', 90, 60, 'control circle', 37, -4.2, 16],
    ['useCase', 'Use Case', 200, 70, 'curved boundary', 92, -12, 32],
    ['actor', 'Actor', 90, 120, 'actor figure', 37, 18.8, 16],
  ])('places profile-aligned hit samples around %s', (semanticType, label, width, height, boundary, left, top, sampleCount) => {
    const props = {
      id: semanticType,
      data: { label, semanticType },
      selected: false,
      width,
      height,
    } as unknown as NodeProps
    render(<GpNode {...props} />)
    const topSample = screen.getByLabelText(`Start relationship on top ${boundary} point 1`)
    const targetBottom = screen.getByLabelText(`Finish relationship on bottom ${boundary} point ${sampleCount / 2 + 1}`)
    expect(Number.parseFloat(topSample.style.left)).toBeCloseTo(left, 5)
    expect(Number.parseFloat(topSample.style.top)).toBeCloseTo(top, 5)
    expect(topSample.style.width).toBe('16px')
    expect(topSample.style.height).toBe('16px')
    expect(topSample.style.borderRadius).toBe('50%')
    expect(targetBottom.style.borderRadius).toBe('50%')
    expect(topSample.id).toBe('gp-top-s')
    expect(topSample.dataset.attachmentSide).toBe('top')
    expect(topSample.dataset.attachmentCardinal).toBe('true')
    expect(topSample.tabIndex).toBe(0)
    const customSample = screen.getByLabelText(`Start relationship on top ${boundary} point 2`)
    expect(customSample.dataset.attachmentCardinal).toBe('false')
    expect(customSample.getAttribute('aria-hidden')).toBe('true')
    expect(customSample.tabIndex).toBe(-1)
    expect(screen.getAllByLabelText(/Start relationship on/)).toHaveLength(sampleCount)
    expect(screen.getAllByLabelText(/Finish relationship on/)).toHaveLength(sampleCount)
    expect(flowState.updateNodeInternals).not.toHaveBeenCalled()
  })

  it('refreshes React Flow internals when zoom changes the sample tier', () => {
    const props = {
      id: 'use-case',
      data: { label: 'Use Case', semanticType: 'useCase' },
      selected: false,
      width: 200,
      height: 70,
    } as unknown as NodeProps
    const { rerender } = render(<GpNode {...props} />)
    expect(screen.getAllByLabelText(/Start relationship on/)).toHaveLength(32)
    flowState.zoom = 1.5
    rerender(<GpNode {...props} />)
    expect(screen.getAllByLabelText(/Start relationship on/)).toHaveLength(44)
    expect(flowState.updateNodeInternals).toHaveBeenCalledWith('use-case')
  })

  it.each([0.5, 0.76, 1, 1.5])('keeps a twelve-screen-pixel pointer halo at %s zoom', (zoom) => {
    flowState.zoom = zoom
    const props = {
      id: 'start',
      data: { label: 'Initial', semanticType: 'initialNode' },
      selected: false,
      width: 90,
      height: 60,
    } as unknown as NodeProps
    render(<GpNode {...props} />)
    const topSample = screen.getByLabelText('Start relationship on top control circle point 1')
    expect(Number.parseFloat(topSample.style.left)).toBeCloseTo(45 - 8 / zoom, 5)
    expect(Number.parseFloat(topSample.style.top)).toBeCloseTo(7.8 - 12 / zoom, 5)
    expect(Number.parseFloat(topSample.style.width)).toBeCloseTo(16 / zoom, 5)
    expect(Number.parseFloat(topSample.style.height)).toBeCloseTo(16 / zoom, 5)
  })
})

describe('GpNode control rendering', () => {
  it('fits Initial content and exposes larger resize grabbers', () => {
    const props = {
      id: 'start',
      data: { label: 'Initial Node', semanticType: 'initialNode' },
      selected: true,
    } as unknown as NodeProps
    render(
      <NodeResizeContext.Provider value={resizeApi}>
        <GpNode {...props} />
      </NodeResizeContext.Provider>,
    )
    const initial = screen.getByLabelText('Initial Node')
    expect(initial.style.padding).toBe('0px')
    expect(initial.style.gap).toBe('0px')
    expect(initial.querySelector('svg')?.style.flexShrink).toBe('1')
    expect(screen.getByTestId('node-resizer').style.width).toBe('9px')
    expect(screen.getByTestId('node-resizer').style.height).toBe('9px')
  })
})

describe('GpNode note rendering', () => {
  it('draws both the outer diagonal and inner dog-ear crease', () => {
    const props = {
      id: 'note',
      data: { label: 'Comment', semanticType: 'note' },
      selected: false,
    } as unknown as NodeProps
    const { container } = render(<GpNode {...props} />)
    expect(container.querySelector('svg path')?.getAttribute('d')).toBe('M0 0 L14 14 M0 0 V14 H14')
  })
})

describe('GpNode classifier compartments', () => {
  it.each([
    ['absent features', undefined],
    ['suppressed feature entries', { properties: [{ kind: 'value' as const, name: '   ' }] }],
  ])('renders %s as one centered section without a header divider', (_case, features) => {
    renderClassifier(features)

    const classifier = screen.getByLabelText('Block')
    expect(classifier.childElementCount).toBe(1)
    const section = classifier.firstElementChild as HTMLElement
    expect(section.style.height).toBe('100%')
    expect(section.style.justifyContent).toBe('center')
    expect(section.style.borderBottom).toBe('')
    expect(screen.getByText('«block»')).toBeTruthy()
    expect(screen.getByText('Vehicle')).toBeTruthy()
  })

  it('uses the primary stereotype heading without changing Block identity', () => {
    renderClassifier(undefined, 'enumeration')
    expect(screen.getByText('«enumeration»')).toBeTruthy()
    expect(screen.getByLabelText('Block')).toBeTruthy()
  })

  it('keeps the partitioned header and feature section when content exists', () => {
    renderClassifier({ properties: [{ kind: 'value', name: 'mass', type: 'kg' }] })

    const classifier = screen.getByLabelText('Block')
    const header = classifier.firstElementChild as HTMLElement
    expect(header.style.height).toBe('34px')
    expect(header.style.borderBottom).not.toBe('')
    expect(screen.getByText('value properties')).toBeTruthy()
    expect(screen.getByText('mass: kg')).toBeTruthy()
  })
})
