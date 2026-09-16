/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import type { Edge, Node } from '@xyflow/react'
import { PropertyPanel } from './PropertyPanel'
import { Home } from './Home'
import { WorkspaceBrowser } from './WorkspaceBrowser'
import { NodePalette } from './NodePalette'
import { EditableLabel } from '@/editor/canvas/customNodes'
import { NodeLabelEditContext } from '@/editor/lib/inlineLabel'
import type { NodeLabelEditApi } from '@/editor/lib/inlineLabel'
import { listDiagrams } from '@/api/diagrams'

vi.mock('@/api/diagrams', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/api/diagrams')>()
  return {
    ...actual,
    listDiagrams: vi.fn().mockResolvedValue([{ name: 'order-approval', path: '/w/.graphpilot/diagrams/order-approval.gp.json' }]),
  }
})

afterEach(() => {
  cleanup()
  localStorage.clear()
  sessionStorage.clear()
  vi.mocked(listDiagrams).mockReset()
  vi.mocked(listDiagrams).mockResolvedValue([
    { name: 'order-approval', path: '/w/.graphpilot/diagrams/order-approval.gp.json' },
  ])
})

describe('PropertyPanel', () => {
  it('shows the empty hint with no selection', () => {
    render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={null}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
      />,
    )
    expect(screen.getByText(/select a node or edge/i)).toBeTruthy()
  })

  it('starts on Content and keeps identity and appearance edits in their fixed tabs', () => {
    const onNodeChange = vi.fn()
    const node = {
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'Alpha', semanticType: 'opaqueAction', gpStyle: {} },
      style: { width: 100, height: 50 },
    } as Node
    render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={onNodeChange}
        onEdgeChange={() => {}}
      />,
    )

    const tabs = screen.getAllByRole('tab')
    expect(tabs.map((tab) => tab.textContent)).toEqual(['Content', 'Appearance', 'Advanced'])
    expect(screen.getByRole('tab', { name: 'Content' }).getAttribute('aria-selected')).toBe('true')
    expect(within(screen.getByRole('tabpanel')).getByText('Opaque Action')).toBeTruthy()

    fireEvent.change(screen.getByDisplayValue('Alpha'), { target: { value: 'Beta' } })
    expect(onNodeChange).toHaveBeenCalledWith('n1', { label: 'Beta' })

    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    fireEvent.click(within(screen.getByRole('tabpanel')).getByText('Blue'))
    expect(onNodeChange).toHaveBeenCalledWith('n1', expect.objectContaining({ background: '#dbeafe' }))
  })

  it('supports keyboard tab navigation and preserves the active tab across element selection', () => {
    const firstNode = {
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'Alpha', semanticType: 'opaqueAction', gpStyle: {} },
    } as Node
    const secondNode = {
      ...firstNode,
      id: 'n2',
      data: { label: 'Decision', semanticType: 'decisionNode', gpStyle: {} },
    } as Node
    const { rerender } = render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node: firstNode }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
      />,
    )

    const contentTab = screen.getByRole('tab', { name: 'Content' })
    contentTab.focus()
    fireEvent.keyDown(contentTab, { key: 'ArrowRight' })
    expect(screen.getByRole('tab', { name: 'Appearance' }).getAttribute('aria-selected')).toBe('true')
    expect(document.activeElement).toBe(screen.getByRole('tab', { name: 'Appearance' }))
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'End' })
    expect(screen.getByRole('tab', { name: 'Advanced' }).getAttribute('aria-selected')).toBe('true')

    rerender(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node: secondNode }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
      />,
    )
    expect(screen.getByRole('tab', { name: 'Advanced' }).getAttribute('aria-selected')).toBe('true')
    expect(within(screen.getByRole('tabpanel')).getByLabelText('Semantic type')).toBeTruthy()
    expect(within(screen.getByRole('tabpanel')).getByRole('button', { name: 'Copy Node ID' })).toBeTruthy()
  })

  it('switches to bulk-style mode for a multi-selection and applies a preset to all', () => {
    const onBulkNodeStyle = vi.fn()
    const node = {
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'Alpha', semanticType: 'opaqueAction', gpStyle: {} },
    } as Node
    render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
        selectedNodeCount={3}
        onBulkNodeStyle={onBulkNodeStyle}
      />,
    )
    expect(screen.getByText('3 nodes selected')).toBeTruthy()
    expect(screen.getByRole('tab', { name: 'Appearance' }).getAttribute('aria-selected')).toBe('true')
    expect(screen.getAllByRole('tab').map((tab) => tab.textContent)).toEqual(['Content', 'Appearance', 'Advanced'])
    fireEvent.click(within(screen.getByRole('tabpanel')).getByText('Blue'))
    expect(onBulkNodeStyle).toHaveBeenCalledWith(expect.objectContaining({ background: '#dbeafe' }))
  })

  it('flags validation issues for the selected element', () => {
    const node = {
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'A', semanticType: 'opaqueAction', gpStyle: {} },
    } as Node
    render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
        issues={['Label is empty']}
      />,
    )
    expect(screen.getByText('Validation issue')).toBeTruthy()
    expect(screen.getByText('Label is empty')).toBeTruthy()
  })

  it('opens and marks the tab responsible for a validation issue', () => {
    const node = {
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'A', semanticType: 'opaqueAction', gpStyle: {} },
      style: { width: 160, height: 60 },
    } as Node
    render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
        issues={[{ message: 'Width is invalid', path: '$.nodes[0].width' }]}
      />,
    )
    expect(screen.getByRole('tab', { name: 'Appearance' }).getAttribute('aria-selected')).toBe('true')
    expect(screen.getByRole('tab', { name: 'Appearance' }).getAttribute('title')).toContain('validation issues')
    expect(screen.getByRole('tab', { name: 'Advanced' }).getAttribute('title')).toContain('contains values')
  })

  it('routes edge semantic validation to Content while node identity remains Advanced', () => {
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: { semanticType: 'association' },
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="use_case_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
        issues={[{ message: 'Relationship type is invalid', path: '$.edges[0].data.semanticType' }]}
      />,
    )
    expect(screen.getByRole('tab', { name: 'Content' }).getAttribute('aria-selected')).toBe('true')
    expect(screen.getByRole('tab', { name: 'Content' }).getAttribute('title')).toContain('validation issues')
    expect(within(screen.getByRole('tabpanel')).getByLabelText('Relationship type')).toBeTruthy()
  })

  it('filters node and edge semantic selections by diagram type and emits semantic patches', () => {
    const onNodeChange = vi.fn()
    const node = {
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'Act', semanticType: 'opaqueAction', gpStyle: {} },
    } as Node
    render(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={onNodeChange}
        onEdgeChange={() => {}}
      />,
    )

    fireEvent.click(screen.getByRole('tab', { name: 'Advanced' }))
    const nodeSemantic = within(screen.getByRole('tabpanel')).getByLabelText('Semantic type') as HTMLSelectElement
    const nodeValues = Array.from(nodeSemantic.options, (option) => option.value)
    expect(nodeValues).toContain('decisionNode')
    expect(nodeValues).not.toContain('block')
    fireEvent.change(nodeSemantic, { target: { value: 'decisionNode' } })
    expect(onNodeChange).toHaveBeenCalledWith('n1', { semanticType: 'decisionNode' })

    cleanup()
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: { semanticType: 'association' },
      style: {},
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="use_case_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    const edgeSemantic = within(screen.getByRole('tabpanel')).getByLabelText('Relationship type') as HTMLSelectElement
    const edgeValues = Array.from(edgeSemantic.options, (option) => option.value)
    expect(edgeValues).toContain('extend')
    expect(edgeValues).not.toContain('controlFlow')
    fireEvent.change(edgeSemantic, { target: { value: 'extend' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      semanticType: 'extend',
      data: {},
      clearData: ['sourceEnd', 'targetEnd', 'condition', 'extensionLocations', 'itemFlows', 'guard', 'weight', 'isInterrupting', 'arrow'],
    })
  })

  it('edits the BDD primary stereotype separately from applied stereotypes', () => {
    const onNodeChange = vi.fn()
    const node = {
      id: 'block-1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'Status', semanticType: 'block', appliedStereotypes: [{ name: 'domain' }] },
    } as Node
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={onNodeChange}
        onEdgeChange={() => {}}
      />,
    )
    fireEvent.change(screen.getByRole('combobox', { name: 'Primary stereotype' }), { target: { value: 'enumeration' } })
    expect(onNodeChange).toHaveBeenCalledWith('block-1', { data: { stereotype: 'enumeration' } })
  })

  it('edits a structured property without losing untouched feature collections or fields', () => {
    const onNodeChange = vi.fn()
    const node = {
      id: 'block-1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: {
        label: 'Vehicle',
        semanticType: 'block',
        gpStyle: {},
        features: {
          properties: [
            {
              kind: 'part',
              name: 'engine',
              type: 'Engine',
              multiplicity: { lower: 1, upper: 1 },
              default: 'standard',
              direction: 'in',
            },
          ],
          operations: [{ name: 'start', returnType: 'Boolean' }],
          receptions: ['shutdown'],
        },
      },
    } as Node
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={onNodeChange}
        onEdgeChange={() => {}}
      />,
    )

    expect(screen.queryByLabelText('Property 1 name')).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: /edit property 1/i }))
    fireEvent.change(screen.getByLabelText('Property 1 name'), { target: { value: 'powerUnit' } })
    expect(onNodeChange).toHaveBeenLastCalledWith('block-1', {
      data: {
        features: {
          properties: [
            {
              kind: 'part',
              name: 'powerUnit',
              type: 'Engine',
              multiplicity: { lower: 1, upper: 1 },
              default: 'standard',
              direction: 'in',
            },
          ],
          operations: [{ name: 'start', returnType: 'Boolean' }],
          receptions: ['shutdown'],
        },
      },
    })
  })

  it('keeps BDD feature collections compact, omits empty groups, and expands only one row at a time', () => {
    const onNodeChange = vi.fn()
    const node = {
      id: 'block-1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: {
        label: 'Vehicle',
        semanticType: 'block',
        gpStyle: {},
        features: {
          properties: [{ kind: 'part', name: 'engine', type: 'Engine' }],
          operations: [{ name: 'start', returnType: 'Boolean' }],
          receptions: ['shutdown'],
        },
      },
    } as Node
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'node', node }}
        onNodeChange={onNodeChange}
        onEdgeChange={() => {}}
      />,
    )

    expect(screen.getByText('Properties')).toBeTruthy()
    expect(screen.getByText('Operations')).toBeTruthy()
    expect(screen.queryByText('Constraints')).toBeNull()
    expect(screen.queryByText('Literals')).toBeNull()
    expect(screen.getByLabelText('Add content')).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: /edit property 1/i }))
    expect(screen.getByLabelText('Property 1 name')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /edit operation 1/i }))
    expect(screen.queryByLabelText('Property 1 name')).toBeNull()
    expect(screen.getByLabelText('Operation 1 name')).toBeTruthy()

    fireEvent.change(screen.getByLabelText('Add content'), { target: { value: 'literal' } })
    expect(onNodeChange).toHaveBeenLastCalledWith('block-1', {
      data: {
        features: {
          properties: [{ kind: 'part', name: 'engine', type: 'Engine' }],
          operations: [{ name: 'start', returnType: 'Boolean' }],
          receptions: ['shutdown'],
          literals: [''],
        },
      },
    })

    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    fireEvent.click(screen.getByRole('button', { name: 'Fit to content' }))
    const [, fitPatch] = onNodeChange.mock.calls.at(-1) as [string, { width: number; height: number }]
    expect(fitPatch.width).toBe(190)
    // Fit-to-content sizes the block the way the SVG renderer draws it: each
    // compartment's first baseline sits FONT_SIZE + 2 below its top, then a line per row.
    expect(fitPatch.height).toBeCloseTo(168.4)
  })

  it('preserves relationship-end data while editing aggregation and supports extension condition', () => {
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: {
        semanticType: 'extend',
        sourceEnd: {
          role: 'extension',
          type: 'OptionalBehavior',
          multiplicity: { lower: 0, upper: '*' },
          navigable: true,
        },
        condition: 'user opts in',
        extensionLocations: ['checkout'],
      },
      style: {},
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="use_case_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )

    expect(screen.queryByLabelText('Arrow')).toBeNull()
    fireEvent.click(screen.getByRole('tab', { name: 'Advanced' }))
    fireEvent.change(within(screen.getByRole('tabpanel')).getByLabelText('Source end aggregation'), { target: { value: 'shared' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      data: {
        sourceEnd: {
          role: 'extension',
          type: 'OptionalBehavior',
          multiplicity: { lower: 0, upper: '*' },
          navigable: true,
          aggregation: 'shared',
        },
      },
    })

    fireEvent.click(screen.getByRole('tab', { name: 'Content' }))
    fireEvent.change(within(screen.getByRole('tabpanel')).getByLabelText('Condition'), { target: { value: 'account is verified' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', { data: { condition: 'account is verified' } })
  })

  it('edits BDD relationship identity from Content and clears incompatible fields', () => {
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'e1',
      source: 'whole',
      target: 'part',
      label: 'owns',
      data: {
        semanticType: 'association',
        description: 'ownership',
        metadata: { reviewed: true },
        sourceEnd: { role: 'vehicle' },
        targetEnd: { role: 'wheel' },
      },
      style: { stroke: '#123456' },
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )

    const relationshipType = within(screen.getByRole('tabpanel')).getByLabelText('Relationship type') as HTMLSelectElement
    expect(Array.from(relationshipType.options, (option) => option.value)).toEqual([
      'association', 'composition', 'generalization', 'dependency', 'commentLink',
    ])
    fireEvent.change(relationshipType, { target: { value: 'composition' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      semanticType: 'composition',
      data: {
        description: 'ownership',
        metadata: { reviewed: true },
        sourceEnd: { role: 'vehicle' },
        targetEnd: { role: 'wheel' },
      },
      clearData: expect.arrayContaining(['condition', 'guard', 'arrow']),
    })

    fireEvent.change(relationshipType, { target: { value: 'generalization' } })
    expect(onEdgeChange).toHaveBeenLastCalledWith('e1', {
      semanticType: 'generalization',
      data: { description: 'ownership', metadata: { reviewed: true } },
      clearData: expect.arrayContaining(['sourceEnd', 'targetEnd', 'itemFlows']),
    })
  })

  it('offers atomic Swap ends only for Composition', () => {
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'composition',
      source: 'part',
      target: 'whole',
      data: { semanticType: 'composition' },
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    fireEvent.click(screen.getByRole('button', { name: 'Swap ends' }))
    expect(onEdgeChange).toHaveBeenCalledWith('composition', { swapEnds: true })
  })

  it('shows item flows for SysML associations, not UML activity object flows', () => {
    const association = {
      id: 'association',
      source: 'a',
      target: 'b',
      data: { semanticType: 'association' },
    } as unknown as Edge
    const { rerender } = render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge: association }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
      />,
    )
    expect(screen.getByText('Item flows')).toBeTruthy()

    const objectFlow = {
      id: 'flow',
      source: 'a',
      target: 'b',
      data: { semanticType: 'objectFlow' },
    } as unknown as Edge
    rerender(
      <PropertyPanel
        diagramType="activity_diagram"
        selection={{ kind: 'edge', edge: objectFlow }}
        onNodeChange={() => {}}
        onEdgeChange={() => {}}
      />,
    )
    expect(screen.queryByText('Item flows')).toBeNull()
  })

  it('keeps multiplicity upper at least as large as lower', () => {
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: {
        semanticType: 'association',
        sourceEnd: { multiplicity: { lower: 1, upper: 1 } },
      },
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    fireEvent.change(screen.getByLabelText('Source end multiplicity lower'), { target: { value: '5' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      data: { sourceEnd: { multiplicity: { lower: 5, upper: 5 } } },
    })
  })

  it('preserves an intermediate upper-multiplicity draft while typing', () => {
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: {
        semanticType: 'association',
        sourceEnd: { multiplicity: { lower: 5, upper: 5 } },
      },
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    const upper = screen.getByLabelText('Source end multiplicity upper') as HTMLInputElement
    fireEvent.change(upper, { target: { value: '1' } })
    expect(upper.value).toBe('1')
    expect(onEdgeChange).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    fireEvent.click(screen.getByRole('tab', { name: 'Content' }))
    expect((screen.getByLabelText('Source end multiplicity upper') as HTMLInputElement).value).toBe('1')
    fireEvent.change(upper, { target: { value: '10' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      data: { sourceEnd: { multiplicity: { lower: 5, upper: 10 } } },
    })
  })

  it('straightens route bends and resets label movement independently', () => {
    const onEdgeChange = vi.fn()
    const route = {
      sourceAnchor: { side: 'right' as const, offset: 0.25 },
      waypoints: [{ x: 100, y: 80 }],
      labelOffset: { x: 12, y: -20 },
    }
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: { semanticType: 'dependency', gpRoute: route },
      style: {},
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    const panel = screen.getByRole('tabpanel')
    fireEvent.click(within(panel).getByRole('button', { name: 'Straighten route' }))
    expect(onEdgeChange).toHaveBeenCalledWith('e1', { route: { ...route, waypoints: undefined } })
    fireEvent.click(within(panel).getByRole('button', { name: 'Reset label' }))
    expect(onEdgeChange).toHaveBeenCalledWith('e1', { route: { ...route, labelOffset: undefined } })
  })

  it('switches route mode while clearing only incompatible waypoints', () => {
    const onEdgeChange = vi.fn()
    const route = {
      sourceAnchor: { side: 'right' as const, offset: 0.25 },
      targetAnchor: { side: 'top' as const, offset: 0.75 },
      waypoints: [{ x: 100, y: 80 }],
      labelOffset: { x: 12, y: -20 },
    }
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      data: { semanticType: 'association', gpRoute: route },
      style: {},
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="use_case_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    const routeMode = within(screen.getByRole('tabpanel')).getByLabelText('Route mode') as HTMLSelectElement
    expect(routeMode.value).toBe('orthogonal')
    fireEvent.change(routeMode, { target: { value: 'straight' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      route: {
        mode: 'straight',
        sourceAnchor: route.sourceAnchor,
        targetAnchor: route.targetAnchor,
        labelOffset: route.labelOffset,
      },
    })
  })

  it('preserves straight mode and label position when resetting anchors', () => {
    const onEdgeChange = vi.fn()
    const route = {
      mode: 'straight' as const,
      sourceAnchor: { side: 'right' as const, offset: 0.25 },
      targetAnchor: { side: 'top' as const, offset: 0.75 },
      labelOffset: { x: 12, y: -20 },
    }
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      sourceHandle: 'gp-right-s',
      targetHandle: 'gp-top-t',
      data: { semanticType: 'association', gpRoute: route },
      style: {},
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="use_case_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )
    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    fireEvent.click(within(screen.getByRole('tabpanel')).getByRole('button', { name: 'Auto anchors' }))
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      route: { ...route, sourceAnchor: undefined, targetAnchor: undefined },
      sourceHandle: null,
      targetHandle: null,
    })
  })

  it('keeps friendly line/arrow controls and removes legacy stereotype and compartment editing', () => {
    const onEdgeChange = vi.fn()
    const edge = {
      id: 'e1',
      source: 'a',
      target: 'b',
      sourceHandle: 'gp-right-s',
      targetHandle: 'gp-left-t',
      data: { semanticType: 'dependency' },
      style: {},
    } as unknown as Edge
    render(
      <PropertyPanel
        diagramType="bdd_diagram"
        selection={{ kind: 'edge', edge }}
        onNodeChange={() => {}}
        onEdgeChange={onEdgeChange}
      />,
    )

    expect(screen.queryByText('Dash array')).toBeNull()
    expect(screen.queryByLabelText(/^Stereotype$/i)).toBeNull()
    expect(screen.queryByText('Compartments')).toBeNull()
    fireEvent.click(screen.getByRole('tab', { name: 'Appearance' }))
    const panel = screen.getByRole('tabpanel')
    expect(within(panel).getByText('Route')).toBeTruthy()
    fireEvent.change(within(panel).getByLabelText('Arrow'), { target: { value: 'backward' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', { data: { arrow: 'backward' } })
    fireEvent.change(within(panel).getByLabelText('Line style'), { target: { value: 'dashed' } })
    expect(onEdgeChange).toHaveBeenCalledWith('e1', { strokeDasharray: '6 4' })
    fireEvent.click(within(panel).getByRole('button', { name: 'Auto anchors' }))
    expect(onEdgeChange).toHaveBeenCalledWith('e1', {
      route: null,
      sourceHandle: null,
      targetHandle: null,
    })
  })
})

describe('Home (landing)', () => {
  it('opens a searchable diagram chooser while preserving file and recent actions', () => {
    const onOpenFile = vi.fn()
    const onNewDiagram = vi.fn()
    const onOpenRecent = vi.fn()
    const onClearRecents = vi.fn()
    render(
      <Home
        fsaSupported
        onOpenFile={onOpenFile}
        onNewDiagram={onNewDiagram}
        recents={['/w/.graphpilot/diagrams/foo.gp.json']}
        onOpenRecent={onOpenRecent}
        onClearRecents={onClearRecents}
      />,
    )
    expect(screen.getByText('GraphPilot')).toBeTruthy()
    // The ugly always-visible raw-path field is gone.
    expect(screen.queryByLabelText('Diagram path')).toBeNull()
    expect(screen.queryByRole('button', { name: 'Create Activity diagram' })).toBeNull()

    const opener = screen.getByRole('button', { name: 'New diagram…' })
    fireEvent.click(opener)
    expect(screen.getByRole('dialog', { name: 'New diagram' })).toBeTruthy()
    expect(document.activeElement).toBe(screen.getByLabelText('Search diagram types'))
    expect(within(screen.getByLabelText('Diagram types')).getAllByRole('button')).toHaveLength(4)
    fireEvent.change(screen.getByLabelText('Search diagram types'), { target: { value: 'sysml' } })
    expect(screen.getByRole('button', { name: 'Create BDD diagram' })).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Create Activity diagram' })).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'Create BDD diagram' }))
    expect(onNewDiagram).toHaveBeenCalledWith('bdd_diagram')
    expect(screen.queryByRole('dialog')).toBeNull()

    fireEvent.click(screen.getByText('Open file…'))
    expect(onOpenFile).toHaveBeenCalled()
    fireEvent.click(screen.getByText('foo.gp.json'))
    expect(onOpenRecent).toHaveBeenCalledWith('/w/.graphpilot/diagrams/foo.gp.json')
    fireEvent.click(screen.getByRole('button', { name: 'Clear recents' }))
    expect(onClearRecents).toHaveBeenCalled()
  })

  it('cancels the chooser, restores focus, and reports an empty search', () => {
    render(
      <Home
        fsaSupported
        onOpenFile={() => {}}
        onNewDiagram={() => {}}
        recents={[]}
        onOpenRecent={() => {}}
        onClearRecents={() => {}}
      />,
    )
    const opener = screen.getByRole('button', { name: 'New diagram…' })
    opener.focus()
    fireEvent.click(opener)
    fireEvent.change(screen.getByLabelText('Search diagram types'), { target: { value: 'missing' } })
    expect(screen.getByText('No diagram types match your search.')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(document.activeElement).toBe(opener)

    fireEvent.click(opener)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(document.activeElement).toBe(opener)
  })

  it('disables the picker and shows an error in the recovery state', () => {
    render(
      <Home
        fsaSupported={false}
        onOpenFile={() => {}}
        onNewDiagram={() => {}}
        recents={[]}
        onOpenRecent={() => {}}
        onClearRecents={() => {}}
        error={{ code: 'load_failed', message: 'nope' }}
      />,
    )
    expect((screen.getByText('Open file…') as HTMLButtonElement).disabled).toBe(true)
    expect(screen.getByText(/load_failed/)).toBeTruthy()
  })
})

describe('NodePalette', () => {
  it('defaults to current diagram organization and can expose the all-authorable notation view', () => {
    render(<NodePalette diagramType="use_case_diagram" />)
    expect((screen.getByLabelText('Palette scope') as HTMLSelectElement).value).toBe('current')
    expect((screen.getByLabelText('Organize palette by') as HTMLSelectElement).value).toBe('diagram')
    expect(screen.getByRole('button', { name: 'Shared' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Use Case' })).toBeTruthy()
    expect(screen.getByText('Actor')).toBeTruthy()
    expect(screen.queryByText('Block')).toBeNull()

    fireEvent.change(screen.getByLabelText('Palette scope'), { target: { value: 'all' } })
    expect(screen.getByRole('button', { name: 'Custom-only' })).toBeTruthy()
    expect(screen.getByText('Block')).toBeTruthy()
    fireEvent.change(screen.getByLabelText('Organize palette by'), { target: { value: 'notation' } })
    expect(screen.getByRole('button', { name: 'Common' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'UML' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'SysML' })).toBeTruthy()
  })

  it('keeps scoped relationships together in one tray above the shape groups', () => {
    render(<NodePalette diagramType="activity_diagram" />)
    expect(screen.getAllByText('Relationships')).toHaveLength(1)
    const relationshipHeading = screen.getByText('Relationships')
    const sharedGroup = screen.getByRole('button', { name: 'Shared' })
    expect(relationshipHeading.compareDocumentPosition(sharedGroup) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Control Flow' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Comment Link' })).toBeTruthy()

    fireEvent.change(screen.getByLabelText('Organize palette by'), { target: { value: 'notation' } })
    expect(screen.getAllByText('Relationships')).toHaveLength(1)
  })

  it('persists palette controls and collapsed groups for the browser session', () => {
    const { unmount } = render(<NodePalette diagramType="activity_diagram" />)
    fireEvent.change(screen.getByLabelText('Palette scope'), { target: { value: 'all' } })
    fireEvent.change(screen.getByLabelText('Organize palette by'), { target: { value: 'notation' } })
    fireEvent.click(screen.getByRole('button', { name: 'UML' }))
    unmount()

    render(<NodePalette diagramType="activity_diagram" />)
    expect((screen.getByLabelText('Palette scope') as HTMLSelectElement).value).toBe('all')
    expect((screen.getByLabelText('Organize palette by') as HTMLSelectElement).value).toBe('notation')
    expect(screen.getByRole('button', { name: 'UML' }).getAttribute('aria-expanded')).toBe('false')
  })

  it('searches shapes and relationships while forcing matching groups open', () => {
    render(<NodePalette diagramType="activity_diagram" />)
    expect(screen.getByText('Decision Node')).toBeTruthy()
    expect(screen.queryByText('Actor')).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'Activity' }))
    expect(screen.queryByText('Decision Node')).toBeNull()

    fireEvent.change(screen.getByLabelText('Search shapes and relationships'), { target: { value: 'initial' } })
    expect(screen.getByText('Initial Node')).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Activity' }).getAttribute('aria-expanded')).toBe('true')

    fireEvent.change(screen.getByLabelText('Search shapes and relationships'), { target: { value: 'control flow' } })
    expect(screen.getByRole('button', { name: 'Control Flow' })).toBeTruthy()
    expect(screen.queryByText('Initial Node')).toBeNull()

    fireEvent.change(screen.getByLabelText('Search shapes and relationships'), { target: { value: '' } })
    expect(screen.getByRole('button', { name: 'Activity' }).getAttribute('aria-expanded')).toBe('false')
  })

  it.each([
    ['activity_diagram', ['Control Flow', 'Comment Link']],
    ['use_case_diagram', ['Association', 'Generalization', 'Include', 'Extend', 'Comment Link']],
    ['bdd_diagram', ['Association', 'Composition', 'Generalization', 'Dependency', 'Comment Link']],
    ['custom', ['Association', 'Control Flow', 'Composition', 'Generalization', 'Include', 'Extend', 'Dependency', 'Realization', 'Comment Link']],
  ])('selects the catalog relationship used by the next %s edge', (diagramType, labels) => {
    const onRelationshipSemanticChange = vi.fn()
    render(
      <NodePalette
        diagramType={diagramType}
        relationshipSemantic={labels[0] === 'Control Flow' ? 'controlFlow' : 'association'}
        onRelationshipSemanticChange={onRelationshipSemanticChange}
      />,
    )
    expect(labels.map((label) => screen.getByRole('button', { name: label }).textContent)).toHaveLength(labels.length)
    expect(screen.getByRole('button', { name: labels[0] }).getAttribute('aria-pressed')).toBe('true')
    fireEvent.click(screen.getByRole('button', { name: labels[1] }))
    expect(onRelationshipSemanticChange).toHaveBeenCalled()
  })

  it('selects the route mode used by the selected and next edge', () => {
    const onRouteModeChange = vi.fn()
    render(
      <NodePalette
        diagramType="use_case_diagram"
        routeMode="straight"
        onRouteModeChange={onRouteModeChange}
      />,
    )
    expect(screen.getByRole('button', { name: 'Straight' }).getAttribute('aria-pressed')).toBe('true')
    fireEvent.click(screen.getByRole('button', { name: 'Orthogonal' }))
    expect(onRouteModeChange).toHaveBeenCalledWith('orthogonal')
  })

  it('adds a focused palette item with the keyboard', () => {
    const onAdd = vi.fn()
    render(<NodePalette diagramType="use_case_diagram" onAdd={onAdd} />)
    fireEvent.keyDown(screen.getByRole('button', { name: 'Add Actor' }), { key: 'Enter' })
    expect(onAdd).toHaveBeenCalledWith({ type: 'gpNode', semanticType: 'actor', label: 'Actor' })
  })

  it('writes only canonical node fields to the drag payload', () => {
    render(<NodePalette diagramType="use_case_diagram" />)
    const dataTransfer = { setData: vi.fn(), effectAllowed: 'none' }
    fireEvent.dragStart(screen.getByTitle('gpNode · actor'), { dataTransfer })

    expect(dataTransfer.setData).toHaveBeenCalledTimes(1)
    const [mime, raw] = dataTransfer.setData.mock.calls[0] as [string, string]
    expect(mime).toBe('application/graphpilot-node')
    expect(JSON.parse(raw)).toEqual({ type: 'gpNode', semanticType: 'actor', label: 'Actor' })
    expect(dataTransfer.effectAllowed).toBe('move')
  })
})

describe('EditableLabel (in-shape rename)', () => {
  const makeApi = (over: Partial<NodeLabelEditApi> = {}): NodeLabelEditApi => ({
    editingId: 'n1',
    begin: vi.fn(),
    commit: vi.fn(),
    cancel: vi.fn(),
    ...over,
  })

  it('shows an input for the edited node and commits a changed value on Enter', () => {
    const commit = vi.fn()
    const api = makeApi({ commit })
    render(
      <NodeLabelEditContext.Provider value={api}>
        <EditableLabel id="n1" text="Old" />
      </NodeLabelEditContext.Provider>,
    )
    const input = screen.getByDisplayValue('Old')
    fireEvent.change(input, { target: { value: 'New' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(commit).toHaveBeenCalledWith('n1', 'New')
  })

  it('cancels (no commit) on Escape and on an unchanged value', () => {
    const commit = vi.fn()
    const cancel = vi.fn()
    const api = makeApi({ commit, cancel })
    render(
      <NodeLabelEditContext.Provider value={api}>
        <EditableLabel id="n1" text="Same" />
      </NodeLabelEditContext.Provider>,
    )
    const input = screen.getByDisplayValue('Same')
    fireEvent.keyDown(input, { key: 'Escape' })
    fireEvent.blur(input)
    expect(cancel).toHaveBeenCalled()
    expect(commit).not.toHaveBeenCalled()
  })

  it('renders plain text when a different node is being edited', () => {
    const api = makeApi({ editingId: 'other' })
    const { container } = render(
      <NodeLabelEditContext.Provider value={api}>
        <EditableLabel id="n1" text="Hello" />
      </NodeLabelEditContext.Provider>,
    )
    expect(container.querySelector('input')).toBeNull()
    expect(screen.getByText('Hello')).toBeTruthy()
  })
})

describe('WorkspaceBrowser', () => {
  it('lists diagrams and opens the chosen one', async () => {
    const onOpen = vi.fn()
    const onClose = vi.fn()
    render(<WorkspaceBrowser open currentPath="/w/.graphpilot/diagrams/x.gp.json" onClose={onClose} onOpen={onOpen} />)
    const item = await screen.findByText('order-approval')
    fireEvent.click(item)
    expect(onOpen).toHaveBeenCalledWith('/w/.graphpilot/diagrams/order-approval.gp.json')
    expect(onClose).toHaveBeenCalled()
  })

  it('ignores a stale list response after the workspace path changes', async () => {
    let resolveFirst: ((items: { name: string; path: string }[]) => void) | undefined
    vi.mocked(listDiagrams)
      .mockReturnValueOnce(new Promise((resolve) => { resolveFirst = resolve }))
      .mockResolvedValueOnce([{ name: 'new-workspace', path: '/new/.graphpilot/diagrams/new.gp.json' }])
    const { rerender } = render(
      <WorkspaceBrowser open currentPath="/old/.graphpilot/diagrams/old.gp.json" onClose={() => {}} onOpen={() => {}} />,
    )
    rerender(
      <WorkspaceBrowser open currentPath="/new/.graphpilot/diagrams/new.gp.json" onClose={() => {}} onOpen={() => {}} />,
    )
    expect(await screen.findByText('new-workspace')).toBeTruthy()
    await act(async () => {
      resolveFirst?.([{ name: 'stale-workspace', path: '/old/.graphpilot/diagrams/old.gp.json' }])
      await Promise.resolve()
    })
    await waitFor(() => expect(screen.getByText('new-workspace')).toBeTruthy())
    expect(screen.queryByText('stale-workspace')).toBeNull()
  })
})
