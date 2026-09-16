import type { GraphPilotDiagram } from '@/types/diagram'
import type { CatalogDiagramType } from './elementCatalog'
import { diagramTypeDescriptor } from './diagramTypes'

export function createBlankDiagram(diagramType: CatalogDiagramType): GraphPilotDiagram {
  return {
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    diagramType,
    id: `diagram_${diagramType}_${Date.now().toString(36)}`,
    name: diagramTypeDescriptor(diagramType).defaultName,
    metadata: { source: 'manual', authoring: 'custom' },
    viewport: { x: 0, y: 0, zoom: 1 },
    nodes: [],
    edges: [],
  }
}
