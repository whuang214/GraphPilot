import { describe, expect, it } from 'vitest'
import type { Edge, Node } from '@xyflow/react'
import { edgeMarkers, graphPilotToReactFlow, reactFlowToGraphPilot } from './reactFlow'
import type { GraphPilotDiagram } from '../types/diagram'

// Load the committed example diagrams directly (via Vite's glob import) so this
// test proves the *real* fixtures round-trip, with no hand-maintained copies that
// could drift. Examples live at
// backend/assets/blueprints/<type>/examples/{training,eval}/<name>/output.gp.json.
const sampleModules = import.meta.glob<GraphPilotDiagram>(
  '../../../backend/assets/blueprints/*/examples/*/*/output.gp.json',
  { eager: true, import: 'default' },
)

function loadSample(diagramType: string): GraphPilotDiagram {
  const entry = Object.entries(sampleModules).find(([path]) => path.includes(`/${diagramType}/`))
  if (!entry) throw new Error(`No canonical sample found for ${diagramType}`)
  return entry[1]
}

// Round-trip *every* committed example (not just one per type), labeled by its
// path under blueprints/ for readable test output.
const fixtures: [string, GraphPilotDiagram][] = Object.entries(sampleModules)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([path, diagram]) => {
    const match = path.match(/blueprints\/(.+)\/output\.gp\.json$/)
    return [match ? match[1] : path, diagram] as [string, GraphPilotDiagram]
  })

// Simulate React Flow runtime/session-only fields that must never be persisted.
function withRuntimeJunk(nodes: Node[]): Node[] {
  return nodes.map(
    (n) =>
      ({
        ...n,
        selected: true,
        dragging: false,
        measured: { width: 999, height: 999 },
        width: 999,
        height: 999,
        positionAbsolute: { x: 1, y: 2 },
        zIndex: 999,
      }) as unknown as Node,
  )
}

function edgesWithJunk(edges: Edge[]): Edge[] {
  return edges.map((e) => ({ ...e, selected: true, animated: true }) as unknown as Edge)
}

describe('node order survives a round-trip', () => {
  // React Flow requires a parent before its children, so the forward adapter sorts
  // containers first. Nothing restored the order, so loading and saving a diagram whose
  // children were written before their container reordered its nodes: a save that
  // changed nothing still produced a diff. Found when host-generated diagrams joined
  // the fixture set — every curated answer happened to be written parents-first.
  const childBeforeParent: GraphPilotDiagram = {
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    name: 'child-first',
    diagramType: 'use_case_diagram',
    nodes: [
      { id: 'uc', type: 'gpNode', position: { x: 20, y: 20 }, parentId: 'system',
        data: { label: 'Do a thing', semanticType: 'useCase' } },
      { id: 'system', type: 'gpNode', position: { x: 0, y: 0 },
        data: { label: 'System', semanticType: 'subject' } },
      { id: 'actor', type: 'gpNode', position: { x: -200, y: 20 },
        data: { label: 'User', semanticType: 'actor' } },
    ],
    edges: [],
    viewport: { x: 0, y: 0, zoom: 1 },
    metadata: {},
  } as unknown as GraphPilotDiagram

  it('puts the children back where they were', () => {
    const rf = graphPilotToReactFlow(childBeforeParent)
    // The canvas needs its own order and is entitled to it — what matters is that the
    // file does not inherit it.
    expect(rf.nodes.map((n) => n.id)).not.toEqual(['uc', 'system', 'actor'])

    const result = reactFlowToGraphPilot(childBeforeParent, rf.nodes, rf.edges)
    expect(result.nodes.map((n) => n.id)).toEqual(['uc', 'system', 'actor'])
  })

  it('appends a node drawn on the canvas rather than sorting it into the middle', () => {
    const rf = graphPilotToReactFlow(childBeforeParent)
    const added = [...rf.nodes, {
      id: 'fresh', type: 'gpNode', position: { x: 5, y: 5 },
      data: { label: 'New', semanticType: 'useCase' },
    } as unknown as Node]

    const result = reactFlowToGraphPilot(childBeforeParent, added, rf.edges)
    expect(result.nodes.map((n) => n.id)).toEqual(['uc', 'system', 'actor', 'fresh'])
  })
})

describe('reactFlowToGraphPilot round-trip', () => {
  it.each(fixtures)('%s round-trips without data loss', (_type, diagram) => {
    const rf = graphPilotToReactFlow(diagram)
    const result = reactFlowToGraphPilot(diagram, rf.nodes, rf.edges)
    expect(result).toEqual(diagram)
  })

  it.each(fixtures)('%s strips React Flow runtime/session-only fields', (_type, diagram) => {
    const rf = graphPilotToReactFlow(diagram)
    const result = reactFlowToGraphPilot(diagram, withRuntimeJunk(rf.nodes), edgesWithJunk(rf.edges))

    // Fidelity is preserved even when the React Flow state carries runtime junk
    // (e.g. measured dimensions must not override the declared width/height).
    expect(result).toEqual(diagram)

    const json = JSON.stringify(result)
    for (const key of ['selected', 'dragging', 'measured', 'positionAbsolute', 'zIndex', 'animated']) {
      expect(json).not.toContain(`"${key}"`)
    }
  })
})

describe('graphPilotToReactFlow rendering fields', () => {
  it.each(fixtures)('%s passes the real node.type, semanticType, gpStyle and parentId', (_type, diagram) => {
    const rf = graphPilotToReactFlow(diagram)
    for (const node of diagram.nodes) {
      const rfNode = rf.nodes.find((n) => n.id === node.id)
      if (!rfNode) throw new Error(`missing rf node ${node.id}`)
      // The forward adapter no longer forces 'default'; the real React Flow
      // component type drives the custom renderers.
      expect(rfNode.type).toBe(node.type)
      const data = rfNode.data as { semanticType?: string; gpStyle?: unknown }
      expect(data.semanticType).toBe(node.data.semanticType)
      expect(data.gpStyle).toEqual(node.style)
      if (node.parentId) {
        expect(rfNode.parentId).toBe(node.parentId)
      }
    }
  })

  it('orders parent containers before their children', () => {
    const useCase = loadSample('use_case_diagram')
    const rf = graphPilotToReactFlow(useCase)
    for (const node of rf.nodes) {
      if (!node.parentId) continue
      const parentIndex = rf.nodes.findIndex((n) => n.id === node.parentId)
      const childIndex = rf.nodes.findIndex((n) => n.id === node.id)
      expect(parentIndex).toBeGreaterThanOrEqual(0)
      expect(parentIndex).toBeLessThan(childIndex)
    }
  })

  it('persists a node recolour made via data.gpStyle', () => {
    const diagram = loadSample('activity_diagram')
    const rf = graphPilotToReactFlow(diagram)
    const targetId = diagram.nodes[0].id
    const editedNodes = rf.nodes.map((n) => {
      if (n.id !== targetId) return n
      const gpStyle = { ...(n.data as { gpStyle?: Record<string, unknown> }).gpStyle, background: '#ff0000' }
      return { ...n, data: { ...n.data, gpStyle } }
    })
    const result = reactFlowToGraphPilot(diagram, editedNodes, rf.edges)
    const saved = result.nodes.find((n) => n.id === targetId)
    expect(saved?.style?.background).toBe('#ff0000')
  })

  it('derives control-flow edge markers from exact semantic identities', () => {
    const activity = loadSample('activity_diagram')
    const rf = graphPilotToReactFlow(activity)
    expect(rf.edges.length).toBeGreaterThan(0)
    for (const edge of rf.edges) {
      expect((edge.data as { semanticType?: string }).semanticType).toBe('controlFlow')
      expect(edge.markerEnd).toMatchObject({ type: 'arrow' })
    }
  })
})

describe('reactFlowToGraphPilot canvas-origin authoring', () => {
  const blankOriginal: GraphPilotDiagram = {
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    diagramType: 'activity_diagram',
    id: 'authored',
    name: 'Authored',
    metadata: {},
    viewport: { x: 0, y: 0, zoom: 1 },
    nodes: [],
    edges: [],
  }

  it('builds exact canonical semantic identities from canvas-created elements', () => {
    const nodes = [
      {
        id: 'node_initial',
        type: 'gpNode',
        position: { x: 10, y: 20 },
        data: { label: 'Start', semanticType: 'initialNode', gpStyle: { background: '#ffffff', borderColor: '#333333' } },
        style: { width: 50, height: 50 },
        selected: true,
        measured: { width: 999, height: 999 },
      },
      {
        id: 'node_action',
        type: 'gpNode',
        position: { x: 10, y: 120 },
        data: { label: 'Do it', semanticType: 'opaqueAction', gpStyle: { background: '#ffffff' } },
        style: { width: 160, height: 60 },
      },
    ] as unknown as Node[]

    const edges = [
      {
        id: 'edge_1',
        source: 'node_initial',
        target: 'node_action',
        data: { semanticType: 'controlFlow', guard: 'ready' },
        markerEnd: { type: 'arrow' },
        selected: true,
      },
    ] as unknown as Edge[]

    const result = reactFlowToGraphPilot(blankOriginal, nodes, edges)

    expect(result.nodes.map((node) => node.data.semanticType)).toEqual(['initialNode', 'opaqueAction'])
    expect(result.nodes[0]).toMatchObject({ type: 'gpNode', width: 50, height: 50 })
    expect(result.nodes[0].style).toMatchObject({ background: '#ffffff', borderColor: '#333333' })
    expect(result.edges[0].data).toMatchObject({ semanticType: 'controlFlow', guard: 'ready' })

    const json = JSON.stringify(result)
    for (const key of ['selected', 'measured', 'markerEnd', 'gpStyle']) {
      expect(json).not.toContain(`"${key}"`)
    }
  })
})

describe('canonical edge routes', () => {
  it('projects route geometry into runtime data and restores it on save', () => {
    const diagram = structuredClone(loadSample('bdd_diagram'))
    diagram.edges[0].route = {
      mode: 'orthogonal',
      sourceAnchor: { side: 'right', offset: 0.25 },
      targetAnchor: { side: 'top', offset: 0.75 },
      waypoints: [{ x: 200, y: 120 }, { x: 200, y: 180 }],
      labelOffset: { x: 8, y: -12 },
    }
    const rf = graphPilotToReactFlow(diagram)
    expect(rf.edges[0].data?.gpRoute).toEqual(diagram.edges[0].route)
    const result = reactFlowToGraphPilot(diagram, rf.nodes, rf.edges)
    expect(result.edges[0].route).toEqual(diagram.edges[0].route)
  })

  it('round-trips a straight route without calculated points', () => {
    const diagram = structuredClone(loadSample('use_case_diagram'))
    diagram.edges[0].route = { mode: 'straight' }
    const rf = graphPilotToReactFlow(diagram)
    expect(rf.edges[0].data?.gpRoute).toEqual({ mode: 'straight' })
    expect(reactFlowToGraphPilot(diagram, rf.nodes, rf.edges).edges[0].route).toEqual({ mode: 'straight' })
  })

  it('preserves untouched route points exactly and permits an explicit route reset', () => {
    const diagram = structuredClone(loadSample('bdd_diagram'))
    diagram.edges[0].route = {
      waypoints: [{ x: 100, y: 100 }, { x: 200, y: 100 }, { x: 300, y: 100 }],
    }
    const rf = graphPilotToReactFlow(diagram)
    expect(reactFlowToGraphPilot(diagram, rf.nodes, rf.edges).edges[0].route).toEqual(diagram.edges[0].route)
    const resetEdges = rf.edges.map((edge, index) => index === 0
      ? { ...edge, data: Object.fromEntries(Object.entries(edge.data ?? {}).filter(([key]) => key !== 'gpRoute')) }
      : edge)
    expect(reactFlowToGraphPilot(diagram, rf.nodes, resetEdges).edges[0].route).toBeUndefined()
  })
})

describe('catalog-driven edge markers', () => {
  it('maps exact relationship identities to their canonical markers', () => {
    expect(edgeMarkers('controlFlow', undefined).markerEnd).toMatchObject({ type: 'arrow' })
    expect(edgeMarkers('include', undefined).markerEnd).toMatchObject({ type: 'arrow' })
    expect(edgeMarkers('extend', undefined).markerEnd).toMatchObject({ type: 'arrow' })
    expect(edgeMarkers('generalization', undefined).markerEnd).toBe('gp-generalization')
    expect(edgeMarkers('composition', undefined)).toEqual({ markerEnd: 'gp-composition' })
    expect(edgeMarkers('commentLink', undefined)).toEqual({})
    expect(edgeMarkers('containment', undefined).markerStart).toBe('gp-crosshair')
    expect(edgeMarkers('unknownRelationship', undefined).markerEnd).toMatchObject({ type: 'arrow' })
    expect(edgeMarkers(undefined, undefined).markerEnd).toMatchObject({ type: 'arrow' })
  })

  it('themes default directional markers and preserves an authored edge stroke', () => {
    expect(edgeMarkers('controlFlow', undefined, {}, '#333333').markerEnd).toMatchObject({ color: 'var(--line-strong)' })
    expect(edgeMarkers('controlFlow', undefined, {}, '#ef4444').markerEnd).toMatchObject({ color: '#ef4444' })
  })

  it('keeps permitted arrow overrides without moving fixed structural markers', () => {
    const back = edgeMarkers('controlFlow', 'backward')
    expect(back.markerStart).toBeTruthy()
    expect(back.markerEnd).toBeUndefined()
    expect(edgeMarkers('controlFlow', 'both')).toMatchObject({ markerStart: expect.anything(), markerEnd: expect.anything() })
    expect(edgeMarkers('controlFlow', 'none')).toEqual({})
    expect(edgeMarkers('containment', 'both')).toEqual({ markerStart: 'gp-crosshair' })
  })
})

describe('structured relationship-end markers', () => {
  it('places composite/shared diamonds on the association end carrying aggregation', () => {
    expect(edgeMarkers('association', undefined, { sourceEnd: { aggregation: 'composite' } })).toEqual({
      markerStart: 'gp-composition',
    })
    expect(edgeMarkers('association', undefined, { targetEnd: { aggregation: 'shared' } })).toEqual({
      markerEnd: 'gp-aggregation',
    })
  })

  it('adds navigability arrows without overriding aggregation', () => {
    expect(edgeMarkers('association', undefined, { targetEnd: { navigable: true } }).markerEnd).toBeTruthy()
    expect(edgeMarkers('association', undefined, {
      sourceEnd: { aggregation: 'composite', navigable: true },
      targetEnd: { navigable: true },
    })).toMatchObject({ markerStart: 'gp-composition', markerEnd: expect.anything() })
  })
})

describe('structured semantic data round-trip', () => {
  const diagram = (): GraphPilotDiagram => ({
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    diagramType: 'bdd_diagram',
    id: 'd',
    name: 'D',
    metadata: {
      authority: 'as_implemented',
      evidence: [{
        id: 'ev-vehicle',
        kind: 'code',
        locator: { path: 'src/vehicle.py', symbol: 'Vehicle', lineRange: { start: 1, end: 40 } },
        contentDigest: `sha256:${'1'.repeat(64)}`,
        summary: 'Vehicle owns an engine and exposes start().',
      }],
    },
    viewport: { x: 0, y: 0, zoom: 1 },
    nodes: [
      {
        id: 'vehicle',
        type: 'gpNode',
        position: { x: 0, y: 0 },
        width: 220,
        height: 160,
        data: {
          label: 'Vehicle',
          semanticType: 'block',
          stereotype: 'interfaceBlock',
          features: {
            properties: [
              { kind: 'part', name: 'engine', type: 'Engine', multiplicity: { lower: 1, upper: 1 } },
              { kind: 'value', name: 'mass', type: 'Mass', default: 1200 },
            ],
            operations: [{ name: 'start', parameters: [], returnType: 'Status' }],
            constraints: [{ name: 'range', expression: 'range >= 500' }],
          },
          appliedStereotypes: [{ name: 'physical', properties: { domain: 'vehicle' } }],
        },
        origin: {
          assurance: 'grounded',
          evidenceRefs: ['ev-vehicle'],
          assumptionRefs: [],
          schemaRules: [],
          rationale: 'The cited region establishes the Vehicle block.',
        },
      },
      {
        id: 'engine',
        type: 'gpNode',
        position: { x: 300, y: 0 },
        data: { label: 'Engine', semanticType: 'block' },
      },
    ],
    edges: [
      {
        id: 'e1',
        type: 'default',
        source: 'vehicle',
        target: 'engine',
        data: {
          semanticType: 'association',
          sourceEnd: { role: 'vehicle', aggregation: 'composite', multiplicity: { lower: 1, upper: 1 } },
          targetEnd: { role: 'engine', navigable: true, multiplicity: { lower: 1, upper: '*' } },
          itemFlows: [{ direction: 'sourceToTarget', item: 'torque' }],
        },
        origin: {
          assurance: 'grounded',
          evidenceRefs: ['ev-vehicle'],
          assumptionRefs: [],
          schemaRules: [],
          rationale: 'The cited region establishes this association.',
        },
      },
    ],
  })

  it('preserves all structured fields byte-for-byte with no edit', () => {
    const original = diagram()
    const rf = graphPilotToReactFlow(original)
    const roundTrip = reactFlowToGraphPilot(original, rf.nodes, rf.edges)
    expect(roundTrip).toEqual(original)
    expect(roundTrip.metadata.evidence).toEqual(original.metadata.evidence)
    expect(roundTrip.nodes[0].origin).toEqual(original.nodes[0].origin)
    expect(roundTrip.edges[0].origin).toEqual(original.edges[0].origin)
  })

  it('preserves legacy diagrams without origins or generation trace', () => {
    const legacy = diagram()
    legacy.metadata = { source: 'mcp' }
    for (const node of legacy.nodes) delete node.origin
    for (const edge of legacy.edges) delete edge.origin

    const rf = graphPilotToReactFlow(legacy)
    expect(reactFlowToGraphPilot(legacy, rf.nodes, rf.edges)).toEqual(legacy)
  })

  it('persists live structured edits on loaded elements', () => {
    const original = diagram()
    const rf = graphPilotToReactFlow(original)
    rf.nodes[0].data = {
      ...rf.nodes[0].data,
      semanticType: 'block',
      stereotype: 'valueType',
      unit: 'kg',
      features: { literals: ['LOW', 'HIGH'] },
    }
    rf.edges[0].data = {
      ...rf.edges[0].data,
      semanticType: 'dependency',
      guard: 'enabled',
      sourceEnd: { role: 'client' },
    }
    const back = reactFlowToGraphPilot(original, rf.nodes, rf.edges)
    expect(back.nodes[0].data).toMatchObject({
      semanticType: 'block',
      stereotype: 'valueType',
      unit: 'kg',
      features: { literals: ['LOW', 'HIGH'] },
    })
    expect(back.edges[0].data).toMatchObject({
      semanticType: 'dependency',
      guard: 'enabled',
      sourceEnd: { role: 'client' },
    })
  })

  it('recovers structured fields for cloned/canvas-origin elements', () => {
    const original = diagram()
    const rf = graphPilotToReactFlow(original)
    const clonedNode = { ...rf.nodes[0], id: 'vehicle_copy' }
    const clonedEdge = { ...rf.edges[0], id: 'e2', source: 'vehicle_copy' }
    const back = reactFlowToGraphPilot(original, [...rf.nodes, clonedNode], [...rf.edges, clonedEdge])
    expect(back.nodes.find((node) => node.id === 'vehicle_copy')?.data.features).toEqual(original.nodes[0].data.features)
    expect(back.edges.find((edge) => edge.id === 'e2')?.data?.sourceEnd).toEqual(original.edges[0].data?.sourceEnd)

    // A clone is something a person put on the canvas, so its provenance is `user`.
    // This used to assert `undefined`, which was the honest answer while nothing could
    // describe a hand-drawn element — and it made the save fail, because `origin` is
    // required on every element of an `as_implemented` diagram.
    //
    // Copying the source's origin would be worse than either: the clone would claim to be
    // established by lines that say nothing about it, which is a fabricated citation in a
    // tool whose entire promise is that citations are real.
    expect(back.nodes.find((node) => node.id === 'vehicle_copy')?.origin?.assurance).toBe('user')
    expect(back.edges.find((edge) => edge.id === 'e2')?.origin?.assurance).toBe('user')
  })
})
