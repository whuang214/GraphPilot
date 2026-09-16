// Canonical GraphPilot diagram JSON types (mirrors backend/graphpilot/schemas/diagram.json).
// GraphPilot JSON is the source of truth; React Flow state is derived from it.

export interface GraphPilotViewport {
  x: number
  y: number
  zoom: number
}

export interface GraphPilotPoint {
  x: number
  y: number
}

export type GraphPilotRouteSide = 'top' | 'right' | 'bottom' | 'left'

export interface GraphPilotRouteAnchor {
  side: GraphPilotRouteSide
  offset: number
}

export type GraphPilotRouteMode = 'orthogonal' | 'straight'

export interface GraphPilotEdgeRoute {
  mode?: GraphPilotRouteMode
  sourceAnchor?: GraphPilotRouteAnchor
  targetAnchor?: GraphPilotRouteAnchor
  waypoints?: GraphPilotPoint[]
  labelOffset?: GraphPilotPoint
}

export interface AppliedStereotype {
  name: string
  properties?: Record<string, unknown>
}

// What a single element is backed by. `user` marks something drawn on the canvas
// rather than authored in a draft, so the editor can tell the two apart.
export type GraphPilotAssurance = 'grounded' | 'assumed' | 'conceptual' | 'user'

export interface GraphPilotElementOrigin {
  assurance: GraphPilotAssurance
  evidenceRefs: string[]
  assumptionRefs: string[]
  schemaRules: string[]
  rationale: string
}

export interface GraphPilotEvidenceLocator {
  path: string
  symbol?: string
  lineRange: { start: number; end: number }
}

// Evidence is carried inline by the diagram, so it stays self-contained: freshness,
// provenance, and the semantic view all read from the file itself.
export interface GraphPilotEvidenceRecord {
  id: string
  kind: 'code' | 'test' | 'documentation' | 'configuration'
  locator: GraphPilotEvidenceLocator
  contentDigest: string
  summary: string
}

export interface GraphPilotDiagramAssurance {
  assumedElementIds?: string[]
}

export interface GraphPilotDiagramMetadata extends Record<string, unknown> {
  authority?: 'as_implemented' | 'conceptual'
  assurance?: GraphPilotDiagramAssurance
  evidence?: GraphPilotEvidenceRecord[]
}

export interface Multiplicity {
  lower: number
  upper: number | '*'
}

export type ParameterDirection = 'in' | 'out' | 'inout' | 'return'

export interface ModelParameter {
  name: string
  type?: string
  direction: ParameterDirection
  multiplicity?: Multiplicity
  default?: unknown
}

// The five the system can actually produce. `diagram.json` also listed `boundReference`,
// `adjunct`, `classifierBehavior`, `connector`, `distributed` and `participant`, and
// nothing could create any of them: the draft schema rejects them, `canonical_assembly`
// only ever writes these five, `authoring.md` documents these five, and the editor's own
// dropdown offers these five. They were reachable only by hand-editing a `.gp.json`, and
// a diagram that did was a trap -- valid, readable, and refused by `diagram_update` on a
// value the projection itself had handed the host.
export type PropertyKind =
  | 'part'
  | 'reference'
  | 'value'
  | 'constraint'
  | 'flow'

export interface ModelProperty {
  kind: PropertyKind
  name: string
  type?: string
  multiplicity?: Multiplicity
  default?: unknown
  direction?: 'in' | 'out' | 'inout'
  isReadOnly?: boolean
  isOrdered?: boolean
  isUnique?: boolean
  isDerived?: boolean
}

export interface ModelOperation {
  name: string
  parameters?: ModelParameter[]
  returnType?: string
  isAbstract?: boolean
  isStatic?: boolean
  isQuery?: boolean
}

export interface ModelConstraint {
  name?: string
  expression: string
}

export interface ModelFeatures {
  properties?: ModelProperty[]
  operations?: ModelOperation[]
  receptions?: string[]
  constraints?: ModelConstraint[]
  literals?: string[]
}

export interface PortData {
  type?: string
  side?: 'top' | 'right' | 'bottom' | 'left'
  offset?: number
  isConjugated?: boolean
  isBehavior?: boolean
  providedFeatures?: string[]
  requiredFeatures?: string[]
}

export interface RelationshipEnd {
  role?: string
  type?: string
  multiplicity?: Multiplicity
  navigable?: boolean
  aggregation?: 'none' | 'shared' | 'composite'
  isOrdered?: boolean
  isUnique?: boolean
  qualifiers?: ModelProperty[]
  propertyPath?: string[]
}

export interface ItemFlow {
  direction: 'sourceToTarget' | 'targetToSource'
  item: string
  itemProperty?: string
}

export interface GraphPilotNodeData {
  label: string
  semanticType?: string
  stereotype?: string
  description?: string
  metadata?: Record<string, unknown>
  appliedStereotypes?: AppliedStereotype[]
  features?: ModelFeatures
  extensionPoints?: string[]
  isAbstract?: boolean
  unit?: string
  quantityKind?: string
  constraintExpression?: string
  constraintParameters?: ModelParameter[]
  port?: PortData
  joinSpec?: string
}

export interface GraphPilotNodeStyle {
  background?: string
  borderColor?: string
  color?: string
  borderWidth?: number
  borderStyle?: string
}

export interface GraphPilotNode {
  id: string
  type: string
  position: { x: number; y: number }
  width?: number
  height?: number
  data: GraphPilotNodeData
  style?: GraphPilotNodeStyle
  parentId?: string
  origin?: GraphPilotElementOrigin
}

// Which end(s) a relationship's arrow points to.
export type ArrowDirection = 'forward' | 'backward' | 'both' | 'none'

export interface GraphPilotEdgeData {
  semanticType?: string
  description?: string
  metadata?: Record<string, unknown>
  appliedStereotypes?: AppliedStereotype[]
  sourceEnd?: RelationshipEnd
  targetEnd?: RelationshipEnd
  condition?: string
  extensionLocations?: string[]
  itemFlows?: ItemFlow[]
  guard?: string
  weight?: number
  isInterrupting?: boolean
  arrow?: ArrowDirection
}

export interface GraphPilotEdgeStyle {
  stroke?: string
  strokeWidth?: number
  strokeDasharray?: string
}

export interface GraphPilotEdge {
  id: string
  type?: string
  source: string
  target: string
  label?: string
  sourceHandle?: string
  targetHandle?: string
  route?: GraphPilotEdgeRoute
  data?: GraphPilotEdgeData
  style?: GraphPilotEdgeStyle
  origin?: GraphPilotElementOrigin
}

export interface GraphPilotDiagram {
  schemaVersion: string
  kind: string
  diagramType: string
  id: string
  name: string
  metadata: GraphPilotDiagramMetadata
  viewport: GraphPilotViewport
  nodes: GraphPilotNode[]
  edges: GraphPilotEdge[]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function isOptionalString(record: Record<string, unknown>, key: string): boolean {
  return record[key] === undefined || typeof record[key] === 'string'
}

function isOptionalNumber(record: Record<string, unknown>, key: string): boolean {
  return record[key] === undefined || isFiniteNumber(record[key])
}

function isNodeStyle(value: unknown): boolean {
  return isRecord(value) &&
    isOptionalString(value, 'background') &&
    isOptionalString(value, 'borderColor') &&
    isOptionalString(value, 'color') &&
    isOptionalNumber(value, 'borderWidth') &&
    isOptionalString(value, 'borderStyle')
}

function isEdgeStyle(value: unknown): boolean {
  return isRecord(value) &&
    isOptionalString(value, 'stroke') &&
    isOptionalNumber(value, 'strokeWidth') &&
    isOptionalString(value, 'strokeDasharray')
}

function isPoint(value: unknown): value is GraphPilotPoint {
  return isRecord(value) && Object.keys(value).every((key) => key === 'x' || key === 'y') &&
    isFiniteNumber(value.x) && isFiniteNumber(value.y)
}

function isRouteAnchor(value: unknown): value is GraphPilotRouteAnchor {
  return isRecord(value) && Object.keys(value).every((key) => key === 'side' || key === 'offset') &&
    (value.side === 'top' || value.side === 'right' || value.side === 'bottom' || value.side === 'left') &&
    isFiniteNumber(value.offset) && value.offset >= 0 && value.offset <= 1
}

function isEdgeRoute(value: unknown): value is GraphPilotEdgeRoute {
  if (!isRecord(value) || Object.keys(value).length === 0) return false
  if (!Object.keys(value).every((key) => key === 'mode' || key === 'sourceAnchor' || key === 'targetAnchor' || key === 'waypoints' || key === 'labelOffset')) return false
  if (value.mode !== undefined && value.mode !== 'orthogonal' && value.mode !== 'straight') return false
  if (value.mode === 'straight' && value.waypoints !== undefined) return false
  if (value.sourceAnchor !== undefined && !isRouteAnchor(value.sourceAnchor)) return false
  if (value.targetAnchor !== undefined && !isRouteAnchor(value.targetAnchor)) return false
  if (value.labelOffset !== undefined && !isPoint(value.labelOffset)) return false
  return value.waypoints === undefined || (
    Array.isArray(value.waypoints) && value.waypoints.length > 0 && value.waypoints.length <= 32 && value.waypoints.every(isPoint)
  )
}

const DIGEST = /^sha256:[0-9a-f]{64}$/
export const CANONICAL_SCHEMA_RULES = ['activity.initial-node'] as const
const CANONICAL_SCHEMA_RULE_SET = new Set<string>(CANONICAL_SCHEMA_RULES)

function hasOnlyKeys(value: Record<string, unknown>, keys: readonly string[]): boolean {
  return Object.keys(value).every((key) => keys.includes(key))
}

function isNonBlank(value: unknown, maxLength: number): value is string {
  return typeof value === 'string' && value.length > 0 && value.length <= maxLength && /\S/.test(value)
}

function isBoundedId(value: unknown, minLength: number, pattern: RegExp): value is string {
  return typeof value === 'string' && value.length >= minLength && value.length <= 128 && pattern.test(value)
}

function isUniqueStrings(value: unknown, maxItems: number): value is string[] {
  return Array.isArray(value) && value.length <= maxItems &&
    value.every((item) => typeof item === 'string') && new Set(value).size === value.length
}

const ASSURANCE = new Set(['grounded', 'assumed', 'conceptual', 'user'])
const EVIDENCE_ID = /^ev-[a-z0-9]+(?:-[a-z0-9]+)*$/
const ASSUMPTION_ID = /^asm-[a-z0-9]+(?:-[a-z0-9]+)*$/

function isElementOrigin(value: unknown): value is GraphPilotElementOrigin {
  if (!isRecord(value) ||
      !hasOnlyKeys(value, ['assurance', 'evidenceRefs', 'assumptionRefs', 'schemaRules', 'rationale'])) return false
  if (typeof value.assurance !== 'string' || !ASSURANCE.has(value.assurance)) return false
  if (!isUniqueStrings(value.evidenceRefs, 16) || !isUniqueStrings(value.assumptionRefs, 8) ||
      !isUniqueStrings(value.schemaRules, 8) || !isNonBlank(value.rationale, 2000)) return false
  if (!value.evidenceRefs.every((item) => isBoundedId(item, 4, EVIDENCE_ID))) return false
  if (!value.assumptionRefs.every((item) => isBoundedId(item, 5, ASSUMPTION_ID))) return false
  if (!value.schemaRules.every((item) => CANONICAL_SCHEMA_RULE_SET.has(item))) return false
  // An assurance class has to be backed by the thing it names.
  if (value.assurance === 'grounded' && value.evidenceRefs.length === 0) return false
  if (value.assurance === 'assumed' && value.assumptionRefs.length === 0) return false
  return true
}

function isEvidenceRecord(value: unknown): value is GraphPilotEvidenceRecord {
  if (!isRecord(value) || !hasOnlyKeys(value, ['id', 'kind', 'locator', 'contentDigest', 'summary'])) return false
  if (!isBoundedId(value.id, 4, EVIDENCE_ID)) return false
  if (typeof value.kind !== 'string' ||
      !['code', 'test', 'documentation', 'configuration'].includes(value.kind)) return false
  if (typeof value.contentDigest !== 'string' || !DIGEST.test(value.contentDigest)) return false
  if (!isNonBlank(value.summary, 2000)) return false
  const locator = value.locator
  if (!isRecord(locator) || !hasOnlyKeys(locator, ['path', 'symbol', 'lineRange'])) return false
  if (!isNonBlank(locator.path, 1024)) return false
  if (locator.symbol !== undefined && !isNonBlank(locator.symbol, 256)) return false
  const range = locator.lineRange
  return isRecord(range) && hasOnlyKeys(range, ['start', 'end']) &&
    Number.isInteger(range.start) && Number.isInteger(range.end) &&
    (range.start as number) >= 1 && (range.end as number) >= 1
}

function hasValidProvenanceMetadata(metadata: Record<string, unknown>): boolean {
  const authority = metadata.authority
  const evidence = metadata.evidence
  if (authority !== undefined && authority !== 'as_implemented' && authority !== 'conceptual') return false
  if (evidence !== undefined && (!Array.isArray(evidence) || !evidence.every(isEvidenceRecord))) return false
  // as_implemented claims the current source says this, so it must cite something;
  // conceptual claims nothing about the repository, so it cites nothing.
  if (authority === 'as_implemented') return Array.isArray(evidence) && evidence.length > 0
  if (authority === 'conceptual') return evidence === undefined
  return evidence === undefined
}

export function isGraphPilotDiagram(value: unknown): value is GraphPilotDiagram {
  if (!isRecord(value) || !isRecord(value.metadata) || !isRecord(value.viewport) ||
      !hasValidProvenanceMetadata(value.metadata)) return false
  if (
    typeof value.schemaVersion !== 'string' ||
    typeof value.kind !== 'string' ||
    typeof value.diagramType !== 'string' ||
    typeof value.id !== 'string' ||
    typeof value.name !== 'string' ||
    !isFiniteNumber(value.viewport.x) ||
    !isFiniteNumber(value.viewport.y) ||
    !isFiniteNumber(value.viewport.zoom) ||
    !Array.isArray(value.nodes) ||
    !Array.isArray(value.edges)
  ) return false
  // An as_implemented diagram states what supports each element; a conceptual one has
  // nothing to cite, so origins stay optional there.
  const grounded = value.metadata.authority === 'as_implemented'
  const nodesValid = value.nodes.every((node) => {
    if (!isRecord(node) || !isRecord(node.position) || !isRecord(node.data)) return false
    if (
      typeof node.id !== 'string' ||
      typeof node.type !== 'string' ||
      !isFiniteNumber(node.position.x) ||
      !isFiniteNumber(node.position.y) ||
      typeof node.data.label !== 'string'
    ) return false
    if (node.width !== undefined && (!isFiniteNumber(node.width) || node.width <= 0)) return false
    if (node.height !== undefined && (!isFiniteNumber(node.height) || node.height <= 0)) return false
    if (node.style !== undefined && !isNodeStyle(node.style)) return false
    if (node.origin !== undefined && !isElementOrigin(node.origin)) return false
    if (grounded && node.origin === undefined) return false
    return node.parentId === undefined || typeof node.parentId === 'string'
  })
  const edgesValid = value.edges.every((edge) => {
    if (!isRecord(edge)) return false
    if (typeof edge.id !== 'string' || typeof edge.source !== 'string' || typeof edge.target !== 'string') return false
    if (edge.data !== undefined && !isRecord(edge.data)) return false
    if (edge.route !== undefined && !isEdgeRoute(edge.route)) return false
    if (edge.origin !== undefined && !isElementOrigin(edge.origin)) return false
    if (grounded && edge.origin === undefined) return false
    return edge.style === undefined || isEdgeStyle(edge.style)
  })
  return nodesValid && edgesValid
}

// Browser-facing API response/error shapes.
export interface DiagramLoadResponse {
  diagramPath: string
  diagram: GraphPilotDiagram
  revision: string
}

export interface DiagramSaveResponse {
  saved: boolean
  diagramPath: string
  /** Opaque revision of the normalized document that was written. */
  revision: string
  /** Normalized document that was written (including reconciled type/provenance). */
  diagram: GraphPilotDiagram
  /** Sibling <name>.svg written by render-on-save; absent if rendering failed. */
  svgPath?: string
  /** Nonfatal post-save render problem; the canonical save still succeeded. */
  warning?: OperationProblem
}

export interface DiagramSummary {
  name: string
  path: string
}

export interface DiagramListResponse {
  diagrams: DiagramSummary[]
}

export interface ValidationErrorDetail {
  code: string
  message: string
  path: string | null
}

export interface DiagramValidateResponse {
  valid: boolean
  validationErrors: ValidationErrorDetail[]
  diagram: GraphPilotDiagram
}

export interface OperationProblem {
  code: string
  message: string
  retryable: boolean
  details?: {
    issues?: ValidationErrorDetail[]
    [key: string]: unknown
  }
}

export interface ApiErrorResponse {
  error: OperationProblem
}

// --- Schema/type parity guard -----------------------------------------------
// These types mirror `backend/graphpilot/schemas/diagram.json`, which is the source
// of truth. The manifest below lists the canonical *required* fields; the runtime
// parity test (`diagram.parity.test.ts`) asserts it equals the schema's `required`
// arrays, and the `satisfies` clause makes `tsc` fail if any listed field is not a
// required (non-optional) key of its interface. Together they force the schema, this
// manifest, and the interfaces to move as one—no new dependency or codegen.

/** The required (non-optional) keys of `T`. */
type RequiredKeys<T> = { [K in keyof T]-?: undefined extends T[K] ? never : K }[keyof T]

export const CANONICAL_REQUIRED_FIELDS = {
  diagram: ['schemaVersion', 'kind', 'diagramType', 'id', 'name', 'metadata', 'viewport', 'nodes', 'edges'],
  node: ['id', 'type', 'position', 'data'],
  nodeData: ['label'],
  edge: ['id', 'source', 'target'],
  viewport: ['x', 'y', 'zoom'],
} as const satisfies {
  diagram: readonly RequiredKeys<GraphPilotDiagram>[]
  node: readonly RequiredKeys<GraphPilotNode>[]
  nodeData: readonly RequiredKeys<GraphPilotNodeData>[]
  edge: readonly RequiredKeys<GraphPilotEdge>[]
  viewport: readonly RequiredKeys<GraphPilotViewport>[]
}
