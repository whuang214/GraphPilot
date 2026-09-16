import type { GraphPilotEdgeData, RelationshipEnd } from '@/types/diagram'
import { allowedEdgeSpecs } from './elementCatalog'
import type { EdgeElementSpec } from './elementCatalog'
import { defaultEdgeSemantic } from './palette'

export interface RelationshipTool {
  semanticType: string
  label: string
  glyph: string
}

export interface RelationshipSemanticPatch {
  semanticType: string
  data: Partial<GraphPilotEdgeData>
  clearData: (keyof GraphPilotEdgeData)[]
}

const STRUCTURED_KEYS: readonly (keyof GraphPilotEdgeData)[] = [
  'sourceEnd',
  'targetEnd',
  'condition',
  'extensionLocations',
  'itemFlows',
  'guard',
  'weight',
  'isInterrupting',
  'arrow',
]

function glyph(spec: EdgeElementSpec): string {
  const line = spec.dashed ? '╌╌' : '──'
  const source = spec.sourceMarker === 'diamond_filled'
    ? '◆'
    : spec.sourceMarker === 'diamond_hollow'
      ? '◇'
      : spec.sourceMarker === 'crosshair' ? '⊕' : ''
  const target = spec.targetMarker === 'arrow'
    ? '→'
    : spec.targetMarker === 'triangle'
      ? '▷'
      : spec.targetMarker === 'diamond_filled' ? '◆' : spec.dashed ? '╌' : '─'
  return `${source}${line}${target}`
}

export function relationshipTools(diagramType: string): RelationshipTool[] {
  const defaultSemantic = defaultEdgeSemantic(diagramType)
  return allowedEdgeSpecs(diagramType)
    .map((spec) => ({ semanticType: spec.semanticType, label: spec.label, glyph: glyph(spec) }))
    .sort((left, right) => {
      if (left.semanticType === defaultSemantic) return -1
      if (right.semanticType === defaultSemantic) return 1
      if (left.semanticType === 'commentLink') return 1
      if (right.semanticType === 'commentLink') return -1
      return 0
    })
}

export function defaultRelationshipSemantic(diagramType: string): string {
  const defaultSemantic = defaultEdgeSemantic(diagramType)
  return relationshipTools(diagramType).some((tool) => tool.semanticType === defaultSemantic)
    ? defaultSemantic
    : relationshipTools(diagramType)[0]?.semanticType ?? 'association'
}

function withoutAggregation(end: RelationshipEnd | undefined): RelationshipEnd | undefined {
  if (!end) return undefined
  const { aggregation: _aggregation, ...rest } = end
  return Object.keys(rest).length ? rest : undefined
}

function definedData(data: Partial<GraphPilotEdgeData>): Partial<GraphPilotEdgeData> {
  return Object.fromEntries(Object.entries(data).filter(([, value]) => value !== undefined)) as Partial<GraphPilotEdgeData>
}

export function applyRelationshipSemantic(current: GraphPilotEdgeData, semanticType: string): RelationshipSemanticPatch {
  const data: Partial<GraphPilotEdgeData> = {
    description: current.description,
    metadata: current.metadata,
    appliedStereotypes: current.appliedStereotypes,
  }
  let allowed: readonly (keyof GraphPilotEdgeData)[] = []
  if (semanticType === 'association' || semanticType === 'composition') {
    data.sourceEnd = withoutAggregation(current.sourceEnd)
    data.targetEnd = withoutAggregation(current.targetEnd)
    allowed = ['sourceEnd', 'targetEnd']
  } else if (semanticType === 'extend') {
    data.condition = current.condition
    data.extensionLocations = current.extensionLocations
    allowed = ['condition', 'extensionLocations']
  } else if (semanticType === 'controlFlow') {
    data.guard = current.guard
    data.weight = current.weight
    data.isInterrupting = current.isInterrupting
    allowed = ['guard', 'weight', 'isInterrupting']
  }
  return {
    semanticType,
    data: definedData(data),
    clearData: STRUCTURED_KEYS.filter((key) => !allowed.includes(key) || data[key] === undefined),
  }
}
