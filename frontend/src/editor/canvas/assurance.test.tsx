/** @vitest-environment jsdom */
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { ReactFlowProvider } from '@xyflow/react'
import { GpNode } from './customNodes'
import { graphPilotToReactFlow, reactFlowToGraphPilot } from '@/adapters/reactFlow'
import type { GraphPilotDiagram, GraphPilotElementOrigin } from '@/types/diagram'

/**
 * P8. A diagram is only worth trusting if a reader can see which parts of it are claims
 * about the repository and which are somebody's inference.
 *
 * That distinction is authored, validated and saved on every element, and was drawn
 * nowhere — an assumption and a cited fact looked identical on the canvas, which is the
 * one thing a tool claiming to be evidence-backed must not do.
 */

function origin(assurance: string, rationale = ''): GraphPilotElementOrigin {
  return {
    assurance,
    evidenceRefs: [],
    assumptionRefs: [],
    schemaRules: [],
    rationale,
  } as GraphPilotElementOrigin
}

function renderNode(
  gpOrigin: GraphPilotElementOrigin | undefined,
  { semanticType = 'opaqueAction', label = 'Do it', width = 140, height = 60 } = {},
) {
  return render(
    <ReactFlowProvider>
      <GpNode
        id="n1"
        type="gpNode"
        data={{ semanticType, label, gpOrigin }}
        selected={false}
        width={width}
        height={height}
        dragging={false}
        zIndex={0}
        isConnectable
        // React Flow's `NodeProps` requires all three. Omitting them type-checked
        // nowhere but still ran under `npm run dev`, because Vite strips types without
        // checking them — so the red only appeared in `npm run build`.
        draggable
        selectable
        deletable
        positionAbsoluteX={0}
        positionAbsoluteY={0}
      />
    </ReactFlowProvider>,
  )
}

afterEach(cleanup)

describe('an assumed element is marked on the canvas', () => {
  it('marks an assumed element and gives its reason', () => {
    renderNode(origin('assumed', 'Accepted as an assumption: asm-scheduler-outside.'))

    const badge = screen.getByLabelText('assumed')
    expect(badge).toBeTruthy()
    expect(badge.getAttribute('title')).toContain('asm-scheduler-outside')
  })

  it('does not mark a grounded element', () => {
    // Every element in a repository-backed diagram is grounded, so badging them all
    // would be noise that teaches a reader to ignore the badge.
    renderNode(origin('grounded', 'Established by cited evidence: ev-a.'))

    expect(screen.queryByLabelText('assumed')).toBeNull()
  })

  it('does not mark a conceptual element', () => {
    // A conceptual diagram claims nothing about any repository, so marking each element
    // individually says nothing the diagram has not already said.
    renderNode(origin('conceptual'))

    expect(screen.queryByLabelText('assumed')).toBeNull()
  })

  it('says something useful when the element has no recorded reason', () => {
    renderNode(origin('assumed'))

    expect(screen.getByLabelText('assumed').getAttribute('title')).toContain('not established')
  })

  it('draws nothing for an element with no provenance at all', () => {
    renderNode(undefined)

    expect(screen.queryByLabelText('assumed')).toBeNull()
  })
})

describe('provenance is display-only', () => {
  it('never leaks back into the saved diagram', () => {
    // `gpOrigin` rides on React Flow's `data`, beside `gpStyle`. The reverse adapter
    // takes `origin` from the loaded diagram and must not pick this copy up, or a
    // display concern would start rewriting a canonical field.
    const diagram: GraphPilotDiagram = {
      schemaVersion: 'graphpilot.diagram.v1',
      kind: 'diagram',
      name: 'p8',
      diagramType: 'activity_diagram',
      nodes: [
        {
          id: 'n1',
          type: 'gpNode',
          position: { x: 0, y: 0 },
          data: { label: 'Do it', semanticType: 'opaqueAction' },
          origin: origin('assumed', 'Accepted as an assumption: asm-a.'),
        },
      ],
      edges: [],
      viewport: { x: 0, y: 0, zoom: 1 },
      metadata: {},
    } as unknown as GraphPilotDiagram

    const rf = graphPilotToReactFlow(diagram)
    expect(rf.nodes[0].data.gpOrigin).toBeTruthy()

    const saved = reactFlowToGraphPilot(diagram, rf.nodes, rf.edges)
    expect(saved.nodes[0].data).not.toHaveProperty('gpOrigin')
    expect(saved.nodes[0].origin).toEqual(diagram.nodes[0].origin)
  })
})

/**
 * Something a person draws on the canvas has no origin, and `origin` is required on every
 * element of an `as_implemented` diagram — so adding a node to a grounded diagram failed
 * the save with a schema error naming a field the person had never heard of.
 *
 * `user` is the honest answer to "how do we know this?". `grounded` would fabricate a
 * citation, `assumed` would invent an assumption nobody accepted, and `conceptual` is a
 * claim about the whole diagram rather than one element.
 */
describe('an element drawn on the canvas', () => {
  const loaded = {
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    name: 'grounded',
    diagramType: 'activity_diagram',
    nodes: [{
      id: 'n1',
      type: 'gpNode',
      position: { x: 0, y: 0 },
      data: { label: 'Cited', semanticType: 'opaqueAction' },
      origin: origin('grounded', 'Established by src/a.py:1-9.'),
    }],
    edges: [],
    viewport: { x: 0, y: 0, zoom: 1 },
    metadata: { authority: 'as_implemented' },
  } as unknown as GraphPilotDiagram

  it('is saved with user provenance rather than none at all', () => {
    const rf = graphPilotToReactFlow(loaded)
    const drawn = {
      id: 'n2',
      type: 'gpNode',
      position: { x: 200, y: 0 },
      data: { label: 'Added by hand', semanticType: 'opaqueAction' },
    }

    const saved = reactFlowToGraphPilot(loaded, [...rf.nodes, drawn], rf.edges)

    const added = saved.nodes.find((node) => node.id === 'n2')
    expect(added?.origin?.assurance).toBe('user')
    // Required by the canonical schema, so an empty one still has to be present.
    expect(added?.origin).toMatchObject({
      evidenceRefs: [], assumptionRefs: [], schemaRules: [],
    })
    expect(added?.origin?.rationale).toBeTruthy()
  })

  it('does not disturb the provenance of anything that was loaded', () => {
    const rf = graphPilotToReactFlow(loaded)
    const drawn = { id: 'n2', type: 'gpNode', position: { x: 200, y: 0 }, data: { label: 'x' } }

    const saved = reactFlowToGraphPilot(loaded, [...rf.nodes, drawn], rf.edges)

    expect(saved.nodes.find((node) => node.id === 'n1')?.origin)
      .toEqual(loaded.nodes[0].origin)
  })

  it('applies to edges too', () => {
    const rf = graphPilotToReactFlow(loaded)
    const drawn = { id: 'n2', type: 'gpNode', position: { x: 200, y: 0 }, data: { label: 'x' } }
    const wired = { id: 'e1', source: 'n1', target: 'n2', data: { semanticType: 'controlFlow' } }

    const saved = reactFlowToGraphPilot(loaded, [...rf.nodes, drawn], [...rf.edges, wired])

    expect(saved.edges[0].origin?.assurance).toBe('user')
  })
})

/**
 * `user` answers "how do we know this?" in a diagram that asks the question. A diagram
 * nobody drafted never asks it — and stamping every element a person draws marked the
 * norm rather than the exception, so every node of every hand-drawn PNG export came out
 * wearing a blue pencil badge.
 */
describe('a diagram nobody drafted', () => {
  const blank = {
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    name: 'Untitled Activity',
    diagramType: 'activity_diagram',
    // Exactly what `createBlankDiagram` writes: no `authority`, so the canonical schema
    // does not require `origin` on anything.
    metadata: { source: 'manual', authoring: 'custom' },
    nodes: [],
    edges: [],
    viewport: { x: 0, y: 0, zoom: 1 },
  } as unknown as GraphPilotDiagram

  const drawn = (id: string, x: number) => ({
    id, type: 'gpNode', position: { x, y: 0 }, data: { label: id, semanticType: 'opaqueAction' },
  })

  it('records no provenance for the elements drawn in it', () => {
    const saved = reactFlowToGraphPilot(blank, [drawn('n1', 0), drawn('n2', 200)], [])

    expect(saved.nodes.every((node) => node.origin === undefined)).toBe(true)
  })

  it('still records it once the diagram carries provenance', () => {
    const conceptual = {
      ...blank,
      nodes: [{ ...drawn('n1', 0), origin: origin('conceptual') }],
    } as unknown as GraphPilotDiagram

    const rf = graphPilotToReactFlow(conceptual)
    const saved = reactFlowToGraphPilot(conceptual, [...rf.nodes, drawn('n2', 200)], [])

    expect(saved.nodes.find((node) => node.id === 'n2')?.origin?.assurance).toBe('user')
  })

  it('is not badged on the canvas even when every element was already stamped', () => {
    // Files saved before the rule above exist and carry `user` on everything. Mirrors
    // `_drawn_entirely_by_hand` in `diagram_render_service.py`.
    const stamped = {
      ...blank,
      nodes: [{ ...drawn('n1', 0), origin: origin('user') }, { ...drawn('n2', 200), origin: origin('user') }],
    } as unknown as GraphPilotDiagram

    expect(graphPilotToReactFlow(stamped).nodes.every((node) => !node.data.gpOrigin)).toBe(true)
  })

  it('is badged when one hand-drawn element sits beside drafted ones', () => {
    const mixed = {
      ...blank,
      nodes: [{ ...drawn('n1', 0), origin: origin('conceptual') }, { ...drawn('n2', 200), origin: origin('user') }],
    } as unknown as GraphPilotDiagram

    const rf = graphPilotToReactFlow(mixed)

    expect(rf.nodes.find((node) => node.id === 'n2')?.data.gpOrigin).toBeTruthy()
  })
})

describe('the badge marks the visible shape', () => {
  it('sits on the disc of an initial node, not the corner of its box', () => {
    // `attachmentProfile` puts a control node's 30px disc at x=30, y=7.8 inside a 90x60
    // box, so the badge centre is (60, 7.8) and its 18px box starts at (51, -1.2). The
    // box corner is x=90 — 30px clear of the only thing drawn.
    renderNode(origin('assumed'), { semanticType: 'initialNode', label: 'Start', width: 90, height: 60 })

    const badge = screen.getByLabelText('assumed')
    expect(parseFloat(badge.style.left)).toBeCloseTo(51, 3)
    expect(parseFloat(badge.style.top)).toBeCloseTo(-1.2, 3)
    expect(badge.style.right).toBe('auto')
  })

  it('leaves a box-shaped node on the CSS corner', () => {
    renderNode(origin('assumed'))

    // No `rect` is passed for a box primitive: the profile is the box, and `.gp-assumed`
    // already puts it on that corner.
    expect(screen.getByLabelText('assumed').style.left).toBe('')
  })
})
