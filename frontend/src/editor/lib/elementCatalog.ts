// Frontend mirror of backend/services/diagrams/catalog/element_catalog.py.
//
// Hand-maintained, and the riskiest duplication in the repository: the canvas and the SVG
// export both dispatch on it, so a disagreement is a diagram that looks different
// depending on where you open it. `test_element_catalog_parity.py` asserts that every type
// a host can author is named here.
//
// It does not mirror everything. The backend carries 98 entries and 26 are authorable; the
// rest are compatibility shapes it recognises when loading an older diagram and nothing can
// create. Those need no canvas glyph.
// Keep semantic identity separate from the finite set of render primitives: many
// UML/SysML elements intentionally share a glyph while remaining distinct types.

export type CatalogDiagramType = 'activity_diagram' | 'use_case_diagram' | 'bdd_diagram' | 'custom'
export type ElementNotation = 'common' | 'uml' | 'sysml'

export type NodePrimitive =
  | 'note'
  | 'rounded-rect'
  | 'initial'
  | 'final'
  | 'flow-final'
  | 'diamond'
  | 'bar'
  | 'actor'
  | 'ellipse'
  | 'container'
  | 'classifier-box'
  | 'object'
  | 'datastore'
  | 'pin'
  | 'partition'
  | 'region'
  | 'send-signal'
  | 'accept-event'
  | 'port'

export type EdgeTargetMarker = 'arrow' | 'triangle' | 'diamond_filled' | 'none'
export type EdgeSourceMarker = 'none' | 'diamond_filled' | 'diamond_hollow' | 'crosshair'

interface ElementSpecBase {
  readonly semanticType: string
  readonly kind: 'node' | 'edge'
  readonly notation: ElementNotation
  readonly validIn: readonly CatalogDiagramType[]
  readonly authorableIn: readonly CatalogDiagramType[]
  readonly label: string
  readonly category: string
}

export interface NodeElementSpec extends ElementSpecBase {
  readonly kind: 'node'
  readonly primitive: NodePrimitive
  readonly isContainer: boolean
}

export interface EdgeElementSpec extends ElementSpecBase {
  readonly kind: 'edge'
  readonly dashed: boolean
  readonly targetMarker: EdgeTargetMarker
  readonly sourceMarker: EdgeSourceMarker
}

export type ElementSpec = NodeElementSpec | EdgeElementSpec

const ACTIVITY_DIAGRAM: CatalogDiagramType = 'activity_diagram'
const USE_CASE_DIAGRAM: CatalogDiagramType = 'use_case_diagram'
const BDD_DIAGRAM: CatalogDiagramType = 'bdd_diagram'
const CUSTOM_DIAGRAM: CatalogDiagramType = 'custom'

const ACTIVITY_ONLY = [ACTIVITY_DIAGRAM] as const
const USE_CASE_ONLY = [USE_CASE_DIAGRAM] as const
const BDD_ONLY = [BDD_DIAGRAM] as const
const CUSTOM_ONLY = [CUSTOM_DIAGRAM] as const
const MVP_DIAGRAMS = [ACTIVITY_DIAGRAM, USE_CASE_DIAGRAM, BDD_DIAGRAM] as const

const AUTHORABLE_NODES: Readonly<Record<CatalogDiagramType, ReadonlySet<string>>> = {
  activity_diagram: new Set([
    'initialNode', 'opaqueAction', 'decisionNode', 'mergeNode', 'forkNode',
    'joinNode', 'activityFinalNode', 'note',
  ]),
  use_case_diagram: new Set(['actor', 'useCase', 'subject', 'note']),
  bdd_diagram: new Set(['block', 'note']),
  custom: new Set(['class', 'interface', 'component', 'package', 'requirement']),
}
const AUTHORABLE_EDGES: Readonly<Record<CatalogDiagramType, ReadonlySet<string>>> = {
  activity_diagram: new Set(['controlFlow', 'commentLink']),
  use_case_diagram: new Set(['association', 'generalization', 'include', 'extend', 'commentLink']),
  bdd_diagram: new Set(['association', 'composition', 'generalization', 'dependency', 'commentLink']),
  custom: new Set(['dependency', 'realization']),
}

function humanizeSemanticType(semanticType: string): string {
  return semanticType
    .replace(/([a-z\d])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function node(
  semanticType: string,
  primitive: NodePrimitive,
  notation: ElementNotation,
  validIn: readonly CatalogDiagramType[],
  category: string,
  isContainer = false,
  label?: string,
): NodeElementSpec {
  return {
    semanticType,
    kind: 'node',
    notation,
    validIn,
    authorableIn: validIn.filter((diagramType) => AUTHORABLE_NODES[diagramType].has(semanticType)),
    label: label ?? humanizeSemanticType(semanticType),
    category,
    primitive,
    isContainer,
  }
}

function edge(
  semanticType: string,
  notation: ElementNotation,
  validIn: readonly CatalogDiagramType[],
  category = 'relationship',
  dashed = false,
  targetMarker: EdgeTargetMarker = 'arrow',
  sourceMarker: EdgeSourceMarker = 'none',
): EdgeElementSpec {
  return {
    semanticType,
    kind: 'edge',
    notation,
    validIn,
    authorableIn: validIn.filter((diagramType) => AUTHORABLE_EDGES[diagramType].has(semanticType)),
    label: humanizeSemanticType(semanticType),
    category,
    dashed,
    targetMarker,
    sourceMarker,
  }
}

const ACTION_PRIMITIVES = [
  ['opaqueAction', 'rounded-rect'],
  ['callBehaviorAction', 'rounded-rect'],
  ['callOperationAction', 'rounded-rect'],
  ['broadcastSignalAction', 'send-signal'],
  ['sendSignalAction', 'send-signal'],
  ['sendObjectAction', 'rounded-rect'],
  ['acceptEventAction', 'accept-event'],
  ['acceptCallAction', 'accept-event'],
  ['replyAction', 'rounded-rect'],
  ['createObjectAction', 'rounded-rect'],
  ['destroyObjectAction', 'rounded-rect'],
  ['readSelfAction', 'rounded-rect'],
  ['readExtentAction', 'rounded-rect'],
  ['readIsClassifiedObjectAction', 'rounded-rect'],
  ['reclassifyObjectAction', 'rounded-rect'],
  ['startClassifierBehaviorAction', 'rounded-rect'],
  ['startObjectBehaviorAction', 'rounded-rect'],
  ['addStructuralFeatureValueAction', 'rounded-rect'],
  ['removeStructuralFeatureValueAction', 'rounded-rect'],
  ['clearStructuralFeatureAction', 'rounded-rect'],
  ['readStructuralFeatureAction', 'rounded-rect'],
  ['writeStructuralFeatureAction', 'rounded-rect'],
  ['addVariableValueAction', 'rounded-rect'],
  ['removeVariableValueAction', 'rounded-rect'],
  ['clearVariableAction', 'rounded-rect'],
  ['readVariableAction', 'rounded-rect'],
  ['writeVariableAction', 'rounded-rect'],
  ['createLinkAction', 'rounded-rect'],
  ['createLinkObjectAction', 'rounded-rect'],
  ['destroyLinkAction', 'rounded-rect'],
  ['readLinkAction', 'rounded-rect'],
  ['readLinkObjectEndAction', 'rounded-rect'],
  ['readLinkObjectEndQualifierAction', 'rounded-rect'],
  ['clearAssociationAction', 'rounded-rect'],
  ['raiseExceptionAction', 'rounded-rect'],
  ['reduceAction', 'rounded-rect'],
  ['testIdentityAction', 'rounded-rect'],
  ['unmarshallAction', 'rounded-rect'],
  ['valueSpecificationAction', 'rounded-rect'],
] as const satisfies readonly (readonly [string, NodePrimitive])[]

// Canonical ordered list. The object index below is derived from this list; no
// semantic facts are duplicated between palette, minimap, and renderer helpers.
export const ELEMENT_SPECS: readonly ElementSpec[] = [
  node('note', 'note', 'common', MVP_DIAGRAMS, 'annotation'),
  node('initialNode', 'initial', 'uml', ACTIVITY_ONLY, 'control'),
  node('activityFinalNode', 'final', 'uml', ACTIVITY_ONLY, 'control'),
  node('flowFinalNode', 'flow-final', 'uml', ACTIVITY_ONLY, 'control'),
  node('decisionNode', 'diamond', 'uml', ACTIVITY_ONLY, 'control'),
  node('mergeNode', 'diamond', 'uml', ACTIVITY_ONLY, 'control'),
  node('forkNode', 'bar', 'uml', ACTIVITY_ONLY, 'control'),
  node('joinNode', 'bar', 'uml', ACTIVITY_ONLY, 'control'),
  node('activityParameterNode', 'object', 'uml', ACTIVITY_ONLY, 'object'),
  node('objectNode', 'object', 'uml', ACTIVITY_ONLY, 'object'),
  node('centralBufferNode', 'object', 'uml', ACTIVITY_ONLY, 'object'),
  node('dataStoreNode', 'datastore', 'uml', ACTIVITY_ONLY, 'object'),
  node('inputPin', 'pin', 'uml', ACTIVITY_ONLY, 'pin'),
  node('outputPin', 'pin', 'uml', ACTIVITY_ONLY, 'pin'),
  node('valuePin', 'pin', 'uml', ACTIVITY_ONLY, 'pin'),
  node('actionInputPin', 'pin', 'uml', ACTIVITY_ONLY, 'pin'),
  node('activityPartition', 'partition', 'uml', ACTIVITY_ONLY, 'group', true),
  node('interruptibleActivityRegion', 'region', 'uml', ACTIVITY_ONLY, 'group', true),
  node('structuredActivityNode', 'region', 'uml', ACTIVITY_ONLY, 'group', true),
  node('sequenceNode', 'region', 'uml', ACTIVITY_ONLY, 'group', true),
  node('conditionalNode', 'region', 'uml', ACTIVITY_ONLY, 'group', true),
  node('loopNode', 'region', 'uml', ACTIVITY_ONLY, 'group', true),
  node('expansionRegion', 'region', 'uml', ACTIVITY_ONLY, 'group', true),
  node('expansionNode', 'pin', 'uml', ACTIVITY_ONLY, 'pin'),
  node('actor', 'actor', 'uml', USE_CASE_ONLY, 'participant'),
  node('useCase', 'ellipse', 'uml', USE_CASE_ONLY, 'behavior'),
  node('subject', 'container', 'uml', USE_CASE_ONLY, 'container', true, 'System Boundary'),
  node('block', 'classifier-box', 'sysml', BDD_ONLY, 'definition'),
  node('valueType', 'classifier-box', 'sysml', BDD_ONLY, 'definition'),
  node('constraintBlock', 'classifier-box', 'sysml', BDD_ONLY, 'definition'),
  node('interfaceBlock', 'classifier-box', 'sysml', BDD_ONLY, 'definition'),
  node('enumeration', 'classifier-box', 'uml', BDD_ONLY, 'definition'),
  node('propertySpecificType', 'classifier-box', 'sysml', BDD_ONLY, 'definition'),
  node('instanceSpecification', 'classifier-box', 'uml', BDD_ONLY, 'instance'),
  node('unit', 'classifier-box', 'sysml', BDD_ONLY, 'quantity'),
  node('quantityKind', 'classifier-box', 'sysml', BDD_ONLY, 'quantity'),
  node('associationBlock', 'classifier-box', 'sysml', BDD_ONLY, 'definition'),
  node('port', 'port', 'uml', BDD_ONLY, 'port'),
  node('proxyPort', 'port', 'sysml', BDD_ONLY, 'port'),
  node('fullPort', 'port', 'sysml', BDD_ONLY, 'port'),
  node('class', 'classifier-box', 'uml', CUSTOM_ONLY, 'definition'),
  node('interface', 'classifier-box', 'uml', CUSTOM_ONLY, 'definition'),
  node('component', 'classifier-box', 'uml', CUSTOM_ONLY, 'definition'),
  node('package', 'container', 'uml', CUSTOM_ONLY, 'container', true),
  node('requirement', 'classifier-box', 'sysml', CUSTOM_ONLY, 'requirement'),
  edge('commentLink', 'common', MVP_DIAGRAMS, 'annotation', true, 'none'),
  edge('controlFlow', 'uml', ACTIVITY_ONLY),
  edge('objectFlow', 'uml', ACTIVITY_ONLY),
  edge('exceptionHandler', 'uml', ACTIVITY_ONLY, 'handler'),
  edge('association', 'uml', [USE_CASE_DIAGRAM, BDD_DIAGRAM], 'relationship', false, 'none'),
  edge('composition', 'sysml', BDD_ONLY, 'relationship', false, 'diamond_filled'),
  edge('generalization', 'uml', [USE_CASE_DIAGRAM, BDD_DIAGRAM], 'relationship', false, 'triangle'),
  edge('include', 'uml', USE_CASE_ONLY, 'relationship', true),
  edge('extend', 'uml', USE_CASE_ONLY, 'relationship', true),
  edge('dependency', 'uml', [BDD_DIAGRAM, CUSTOM_DIAGRAM], 'relationship', true),
  edge('containment', 'sysml', BDD_ONLY, 'relationship', false, 'none', 'crosshair'),
  edge('participantPropertyLink', 'sysml', BDD_ONLY, 'relationship', false, 'none'),
  edge('connectorPropertyLink', 'sysml', BDD_ONLY, 'relationship', true, 'none'),
  edge('realization', 'uml', CUSTOM_ONLY, 'relationship', true, 'triangle'),
  ...ACTION_PRIMITIVES.map(([semanticType, primitive]) =>
    node(semanticType, primitive, 'uml', ACTIVITY_ONLY, 'action'),
  ),
]

// A dictionary-shaped view is convenient for consumers and mirrors the backend's
// ELEMENT_CATALOG. ELEMENT_SPECS remains the single source used to construct it.
export const ELEMENT_CATALOG: Readonly<Record<string, ElementSpec>> = Object.freeze(
  Object.fromEntries(ELEMENT_SPECS.map((spec) => [spec.semanticType, spec])),
)

const SPEC_BY_SEMANTIC = new Map(ELEMENT_SPECS.map((spec) => [spec.semanticType, spec] as const))

// These are the exact classifier/port keywords emitted by the backend renderer.
// An empty string means that the semantic uses no «keyword» adornment.
const SEMANTIC_KEYWORDS = new Map<string, string>([
  ['block', 'block'],
  ['valueType', 'valueType'],
  ['constraintBlock', 'constraint'],
  ['interfaceBlock', 'interfaceBlock'],
  ['enumeration', 'enumeration'],
  ['propertySpecificType', 'propertySpecificType'],
  ['associationBlock', 'block'],
  ['unit', 'unit'],
  ['quantityKind', 'quantityKind'],
  ['interface', 'interface'],
  ['component', 'component'],
  ['requirement', 'requirement'],
  ['proxyPort', 'proxy'],
  ['fullPort', 'full'],
])

export function getElementSpec(semanticType: string | null | undefined): ElementSpec | undefined {
  return semanticType ? SPEC_BY_SEMANTIC.get(semanticType) : undefined
}

export function nodePrimitive(semanticType: string | null | undefined): NodePrimitive | undefined {
  const spec = getElementSpec(semanticType)
  return spec?.kind === 'node' ? spec.primitive : undefined
}

export function semanticKeyword(semanticType: string | null | undefined): string {
  return semanticType ? (SEMANTIC_KEYWORDS.get(semanticType) ?? '') : ''
}

export function isContainerSemantic(semanticType: string | null | undefined): boolean {
  const spec = getElementSpec(semanticType)
  return spec?.kind === 'node' && spec.isContainer
}

export function canOwnSemantic(
  parentSemanticType: string | null | undefined,
  childSemanticType: string | null | undefined,
): boolean {
  const parent = getElementSpec(parentSemanticType)
  const child = getElementSpec(childSemanticType)
  if (parent?.kind !== 'node' || child?.kind !== 'node') return false
  if (child.semanticType === 'expansionNode') return parent.semanticType === 'expansionRegion'
  if (child.primitive === 'port') return parent.primitive === 'classifier-box' || parent.primitive === 'port'
  if (child.primitive === 'pin') return parent.category === 'action'
  if (parent.semanticType === 'subject') return child.semanticType === 'useCase'
  return parent.isContainer
}

function isValidFor(spec: ElementSpec, diagramType: string): boolean {
  return diagramType === CUSTOM_DIAGRAM
    ? spec.authorableIn.length > 0
    : spec.authorableIn.some((type) => type === diagramType)
}

export function allowedNodeSpecs(diagramType: string): NodeElementSpec[] {
  return ELEMENT_SPECS.filter(
    (spec): spec is NodeElementSpec => spec.kind === 'node' && isValidFor(spec, diagramType),
  )
}

export function allowedEdgeSpecs(diagramType: string): EdgeElementSpec[] {
  return ELEMENT_SPECS.filter(
    (spec): spec is EdgeElementSpec => spec.kind === 'edge' && isValidFor(spec, diagramType),
  )
}

export function semanticLabel(semanticType: string): string {
  return getElementSpec(semanticType)?.label ?? humanizeSemanticType(semanticType)
}
