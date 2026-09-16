import { describe, expect, it } from 'vitest'
import type { GraphPilotDiagram } from '@/types/diagram'
import { mapValidationErrors } from './validation'

const diagram = {
  schemaVersion: 'graphpilot.diagram.v1',
  kind: 'diagram',
  diagramType: 'activity_diagram',
  id: 'd',
  name: 'D',
  metadata: {},
  viewport: { x: 0, y: 0, zoom: 1 },
  nodes: [
    { id: 'n0', type: 'gpNode', position: { x: 0, y: 0 }, data: { label: 'A' } },
    { id: 'n1', type: 'gpNode', position: { x: 0, y: 0 }, data: { label: '' } },
  ],
  edges: [{ id: 'e0', source: 'n0', target: 'n1' }],
} as unknown as GraphPilotDiagram

describe('mapValidationErrors', () => {
  it('maps node and edge paths to their element ids', () => {
    const markers = mapValidationErrors(diagram, [
      { code: 'empty_node_label', message: 'empty label', path: '$.nodes[1].data.label' },
      { code: 'edge_bad', message: 'bad source', path: '$.edges[0].source' },
    ])
    expect(markers.nodeIds.has('n1')).toBe(true)
    expect(markers.byNode.n1).toEqual([{ message: 'empty label', path: '$.nodes[1].data.label' }])
    expect(markers.edgeIds.has('e0')).toBe(true)
    expect(markers.byEdge.e0).toEqual([{ message: 'bad source', path: '$.edges[0].source' }])
    expect(markers.general).toEqual([])
  })

  it('buckets diagram-level, out-of-range, and null paths as general', () => {
    const markers = mapValidationErrors(diagram, [
      { code: 'no_nodes', message: 'no nodes', path: '$.nodes' },
      { code: 'root', message: 'root issue', path: '$' },
      { code: 'oob', message: 'out of range', path: '$.nodes[9].id' },
      { code: 'nullpath', message: 'null path', path: null },
    ])
    expect(markers.general).toEqual([
      { message: 'no nodes', path: '$.nodes' },
      { message: 'root issue', path: '$' },
      { message: 'out of range', path: '$.nodes[9].id' },
      { message: 'null path', path: null },
    ])
    expect(markers.nodeIds.size).toBe(0)
    expect(markers.edgeIds.size).toBe(0)
  })
})
