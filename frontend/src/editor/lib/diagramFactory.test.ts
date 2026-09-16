import { describe, expect, it, vi } from 'vitest'
import { createBlankDiagram } from './diagramFactory'
import { DIAGRAM_TYPE_DESCRIPTORS } from './diagramTypes'

vi.spyOn(Date, 'now').mockReturnValue(123456)

describe('createBlankDiagram', () => {
  it.each(DIAGRAM_TYPE_DESCRIPTORS)('creates valid empty canonical $type JSON', ({ type: diagramType, defaultName: name }) => {
    expect(createBlankDiagram(diagramType)).toEqual({
      schemaVersion: 'graphpilot.diagram.v1',
      kind: 'diagram',
      diagramType,
      id: `diagram_${diagramType}_2n9c`,
      name,
      metadata: { source: 'manual', authoring: 'custom' },
      viewport: { x: 0, y: 0, zoom: 1 },
      nodes: [],
      edges: [],
    })
  })
})
