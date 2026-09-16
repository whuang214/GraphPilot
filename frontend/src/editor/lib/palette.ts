import type { GraphPilotNodeStyle, GraphPilotRouteMode } from '@/types/diagram'
import { allowedNodeSpecs, ELEMENT_SPECS, isContainerSemantic } from './elementCatalog'
import type { CatalogDiagramType, EdgeElementSpec, ElementNotation, ElementSpec, NodeElementSpec } from './elementCatalog'

// Helpers for catalog-driven drag-from-palette authoring. Palette entries are
// deliberately the canonical drag payload shape: grouping remains UI metadata.
export interface PaletteItem {
  type: 'gpNode'
  semanticType: string
  label: string
}

export type PaletteScope = 'current' | 'all'
export type PaletteOrganization = 'diagram' | 'notation'

export interface PaletteRelationshipItem {
  semanticType: string
  label: string
}

export interface OrganizedPaletteGroup {
  id: string
  label: string
  shapes: PaletteItem[]
  relationships: PaletteRelationshipItem[]
}

export interface NodeSize {
  width: number
  height: number
}

// The MIME type used to carry the dragged block descriptor on the drag event.
export const DRAG_MIME = 'application/graphpilot-node'

// Default visual style for a newly created node, matching backend STYLE_DEFAULTS.
export const DEFAULT_NODE_STYLE: GraphPilotNodeStyle = {
  background: '#ffffff',
  borderColor: '#333333',
  color: '#111111',
  borderWidth: 1,
  borderStyle: 'solid',
}

const DIAGRAM_GROUPS = [
  { id: 'shared', label: 'Shared' },
  { id: 'activity', label: 'Activity' },
  { id: 'use-case', label: 'Use Case' },
  { id: 'bdd', label: 'BDD' },
  { id: 'custom', label: 'Custom-only' },
] as const
const NOTATION_GROUPS: readonly { id: ElementNotation; label: string }[] = [
  { id: 'common', label: 'Common' },
  { id: 'uml', label: 'UML' },
  { id: 'sysml', label: 'SysML' },
]
const CORE_DIAGRAM_GROUP: Readonly<Record<string, string>> = {
  activity_diagram: 'activity',
  use_case_diagram: 'use-case',
  bdd_diagram: 'bdd',
}

function toPaletteItem(spec: NodeElementSpec): PaletteItem {
  return { type: 'gpNode', semanticType: spec.semanticType, label: spec.label }
}

/**
 * Return one diagram type's authorable node subset; `custom` is the bounded
 * all-authorable union used by compatibility-aware editor views.
 */
export function paletteItems(diagramType = 'custom'): PaletteItem[] {
  return allowedNodeSpecs(diagramType).map(toPaletteItem)
}

function diagramGroup(spec: ElementSpec): string {
  const core = spec.authorableIn.filter((diagramType) => diagramType !== 'custom')
  if (core.length > 1) return 'shared'
  if (core.length === 1) return CORE_DIAGRAM_GROUP[core[0]] ?? 'custom'
  return 'custom'
}

function includedSpecs(diagramType: string, scope: PaletteScope): ElementSpec[] {
  if (scope === 'all' || diagramType === 'custom') return ELEMENT_SPECS.filter((spec) => spec.authorableIn.length > 0)
  return ELEMENT_SPECS.filter((spec) => spec.authorableIn.includes(diagramType as CatalogDiagramType))
}

function matchesPaletteQuery(spec: ElementSpec, query: string): boolean {
  if (!query) return true
  const families = spec.authorableIn.flatMap((diagramType) => [
    diagramType,
    diagramType === 'activity_diagram' ? 'activity' : diagramType === 'use_case_diagram' ? 'use case' : diagramType === 'bdd_diagram' ? 'bdd' : 'custom',
  ])
  return [spec.label, spec.semanticType, spec.category, spec.notation, ...families]
    .some((value) => value.toLowerCase().includes(query))
}

export function organizedPaletteGroups({
  diagramType = 'custom',
  scope = 'current',
  organization = 'diagram',
  query = '',
}: {
  diagramType?: string
  scope?: PaletteScope
  organization?: PaletteOrganization
  query?: string
} = {}): OrganizedPaletteGroup[] {
  const normalizedQuery = query.trim().toLowerCase()
  const specs = includedSpecs(diagramType, scope).filter((spec) => matchesPaletteQuery(spec, normalizedQuery))
  const groups = organization === 'diagram' ? DIAGRAM_GROUPS : NOTATION_GROUPS
  return groups.map((group) => {
    const grouped = specs.filter((spec) => (organization === 'diagram' ? diagramGroup(spec) : spec.notation) === group.id)
    const shapes = grouped
      .filter((spec): spec is NodeElementSpec => spec.kind === 'node')
      .map(toPaletteItem)
      .sort((left, right) => left.label.localeCompare(right.label))
    const relationships = grouped
      .filter((spec): spec is EdgeElementSpec => spec.kind === 'edge')
      .map((spec) => ({ semanticType: spec.semanticType, label: spec.label }))
      .sort((left, right) => left.label.localeCompare(right.label))
    return { id: group.id, label: group.label, shapes, relationships }
  }).filter((group) => group.shapes.length > 0 || group.relationships.length > 0)
}

// Exact render fallback sizes from backend/services/catalog/constants.py.
const DEFAULT_NODE_SIZES = new Map<string, NodeSize>([
  ['initialNode', { width: 90, height: 60 }],
  ['activityFinalNode', { width: 90, height: 60 }],
  ['flowFinalNode', { width: 90, height: 60 }],
  ['mergeNode', { width: 120, height: 50 }],
  ['forkNode', { width: 120, height: 30 }],
  ['joinNode', { width: 120, height: 30 }],
  ['opaqueAction', { width: 160, height: 60 }],
  ['decisionNode', { width: 140, height: 80 }],
  ['objectNode', { width: 160, height: 60 }],
  ['centralBufferNode', { width: 160, height: 60 }],
  ['dataStoreNode', { width: 160, height: 70 }],
  ['inputPin', { width: 24, height: 24 }],
  ['outputPin', { width: 24, height: 24 }],
  ['valuePin', { width: 24, height: 24 }],
  ['actionInputPin', { width: 24, height: 24 }],
  ['expansionNode', { width: 24, height: 24 }],
  ['note', { width: 160, height: 80 }],
  ['actor', { width: 90, height: 120 }],
  ['useCase', { width: 200, height: 70 }],
  ['subject', { width: 320, height: 240 }],
  ['block', { width: 180, height: 90 }],
  ['valueType', { width: 180, height: 90 }],
  ['constraintBlock', { width: 180, height: 100 }],
  ['interfaceBlock', { width: 180, height: 90 }],
  ['enumeration', { width: 180, height: 90 }],
  ['propertySpecificType', { width: 180, height: 90 }],
  ['instanceSpecification', { width: 180, height: 90 }],
  ['unit', { width: 180, height: 80 }],
  ['quantityKind', { width: 180, height: 80 }],
  ['associationBlock', { width: 180, height: 100 }],
  ['port', { width: 44, height: 44 }],
  ['proxyPort', { width: 44, height: 44 }],
  ['fullPort', { width: 44, height: 44 }],
])

const FALLBACK_SIZE: NodeSize = { width: 140, height: 60 }
// Containers without a backend fixed fallback need enough room to receive a
// child immediately after being dragged onto the canvas.
const CONTAINER_FALLBACK_SIZE: NodeSize = { width: 320, height: 240 }

export function defaultNodeSize(semanticType: string): NodeSize {
  const exact = DEFAULT_NODE_SIZES.get(semanticType)
  const size = exact ?? (isContainerSemantic(semanticType) ? CONTAINER_FALLBACK_SIZE : FALLBACK_SIZE)
  return { ...size }
}

// Per-type conform defaults from backend/services/catalog/diagram_types.py.
const DEFAULT_EDGE_SEMANTICS = new Map<string, string>([
  ['activity_diagram', 'controlFlow'],
  ['use_case_diagram', 'association'],
  ['bdd_diagram', 'association'],
  ['custom', 'association'],
])

export function defaultEdgeSemantic(diagramType: string): string {
  return DEFAULT_EDGE_SEMANTICS.get(diagramType) ?? 'association'
}

export function defaultRouteMode(diagramType: string): GraphPilotRouteMode {
  return diagramType === 'use_case_diagram' ? 'straight' : 'orthogonal'
}

export function newNodeId(semanticType: string): string {
  return `node_${semanticType}_${Math.random().toString(36).slice(2, 8)}`
}
