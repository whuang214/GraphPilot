import type { CatalogDiagramType } from './elementCatalog'

export interface DiagramTypeDescriptor {
  type: CatalogDiagramType
  label: string
  description: string
  notation: string
  keywords: readonly string[]
  defaultName: string
}

export const DIAGRAM_TYPE_DESCRIPTORS: readonly DiagramTypeDescriptor[] = [
  {
    type: 'activity_diagram',
    label: 'Activity',
    description: 'Workflow and control flow',
    notation: 'UML',
    keywords: ['activity', 'workflow', 'process', 'control flow'],
    defaultName: 'Untitled Activity Diagram',
  },
  {
    type: 'use_case_diagram',
    label: 'Use Case',
    description: 'Actors and system goals',
    notation: 'UML',
    keywords: ['use case', 'actor', 'goal', 'system boundary'],
    defaultName: 'Untitled Use Case Diagram',
  },
  {
    type: 'bdd_diagram',
    label: 'BDD',
    description: 'Blocks and structure',
    notation: 'SysML',
    keywords: ['bdd', 'block definition', 'structure', 'system'],
    defaultName: 'Untitled BDD Diagram',
  },
  {
    type: 'custom',
    label: 'Custom',
    description: 'Advanced mixed canvas',
    notation: 'Advanced',
    keywords: ['custom', 'mixed', 'generic', 'advanced'],
    defaultName: 'Untitled Custom Diagram',
  },
]

export function diagramTypeDescriptor(diagramType: CatalogDiagramType): DiagramTypeDescriptor {
  return DIAGRAM_TYPE_DESCRIPTORS.find((descriptor) => descriptor.type === diagramType)!
}

export function filterDiagramTypes(query: string): DiagramTypeDescriptor[] {
  const normalized = query.trim().toLowerCase()
  if (!normalized) return [...DIAGRAM_TYPE_DESCRIPTORS]
  return DIAGRAM_TYPE_DESCRIPTORS.filter((descriptor) => [
    descriptor.label,
    descriptor.type,
    descriptor.description,
    descriptor.notation,
    ...descriptor.keywords,
  ].some((value) => value.toLowerCase().includes(normalized)))
}
