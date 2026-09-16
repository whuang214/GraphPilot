import type { CSSProperties } from 'react'
import { MarkerType } from '@xyflow/react'
import type { Edge, EdgeMarker, Node, Viewport } from '@xyflow/react'
import type {
  ArrowDirection,
  GraphPilotDiagram,
  GraphPilotEdge,
  GraphPilotEdgeData,
  GraphPilotEdgeStyle,
  GraphPilotElementOrigin,
  GraphPilotNode,
  GraphPilotNodeData,
  GraphPilotNodeStyle,
} from '../types/diagram'
import { getElementSpec } from '@/editor/lib/elementCatalog'
import { normalizeRouteGeometry } from '@/editor/lib/edgeRouting'

export interface ReactFlowDiagram {
  nodes: Node[]
  edges: Edge[]
  viewport: Viewport
}

// Custom node renderers draw their own type-specific shapes from `data.gpStyle`,
// so only sizing is passed to the React Flow node wrapper here. Visual style
// (background/border/color) travels in `data.gpStyle` instead of the wrapper
// `style`, which also keeps it out of the reverse adapter's whitelist.
function nodeSizeCss(node: GraphPilotNode): CSSProperties | undefined {
  const css: CSSProperties = {}
  if (node.width != null) css.width = node.width
  if (node.height != null) css.height = node.height
  return Object.keys(css).length ? css : undefined
}

// Maps the canonical generated default to the theme-aware display stroke while
// preserving genuinely authored colors. Keep the literal in sync with backend EDGE_DEFAULTS.
export const DEFAULT_EDGE_STROKE = '#333333'

export function edgeDisplayStroke(stroke?: string): string {
  return !stroke || stroke.toLowerCase() === DEFAULT_EDGE_STROKE ? 'var(--line-strong)' : stroke
}

// Maps a GraphPilot edge `semanticType` to its catalog-defined target marker.
// Markers are display-only and are never read back by the reverse adapter.
// Exported so canvas-created edges can use the same mapping.
function openArrow(color: string): EdgeMarker {
  return { type: MarkerType.Arrow, width: 15, height: 15, color }
}

function catalogMarker(marker: string | undefined, color: string): EdgeMarker | string | undefined {
  if (marker === 'arrow') return openArrow(color)
  if (marker === 'triangle') return 'gp-generalization'
  if (marker === 'diamond_filled') return 'gp-composition'
  if (marker === 'diamond_hollow') return 'gp-aggregation'
  if (marker === 'crosshair') return 'gp-crosshair'
  return undefined
}

// Resolve start/end markers from the relationship identity, structured association
// ends, and the optional directional override. Aggregation/crosshair/navigability
// semantics remain fixed when an ordinary directional arrow is overridden.
export function edgeMarkers(
  semanticType: string | undefined,
  arrow: ArrowDirection | undefined,
  data: Pick<GraphPilotEdgeData, 'sourceEnd' | 'targetEnd'> = {},
  color = 'var(--line-strong)',
): { markerStart?: EdgeMarker | string; markerEnd?: EdgeMarker | string } {
  const markerColor = edgeDisplayStroke(color)
  const spec = getElementSpec(semanticType)
  const sourceAggregation = data.sourceEnd?.aggregation
  const targetAggregation = data.targetEnd?.aggregation
  const fixedStart = sourceAggregation === 'composite'
    ? catalogMarker('diamond_filled', markerColor)
    : sourceAggregation === 'shared'
      ? catalogMarker('diamond_hollow', markerColor)
      : spec?.kind === 'edge'
        ? catalogMarker(spec.sourceMarker, markerColor)
        : undefined
  const fixedEnd = targetAggregation === 'composite'
    ? catalogMarker('diamond_filled', markerColor)
    : targetAggregation === 'shared'
      ? catalogMarker('diamond_hollow', markerColor)
      : undefined
  const navigableStart = data.sourceEnd?.navigable ? openArrow(markerColor) : undefined
  const navigableEnd = data.targetEnd?.navigable ? openArrow(markerColor) : undefined
  const semanticMarker = spec?.kind === 'edge' ? catalogMarker(spec.targetMarker, markerColor) : openArrow(markerColor)
  const canOverride = semanticType === 'controlFlow' || semanticType === 'objectFlow' || semanticType === 'exceptionHandler' || semanticType === 'dependency'
  let directionalStart: EdgeMarker | string | undefined
  let directionalEnd: EdgeMarker | string | undefined = semanticMarker
  if (canOverride && semanticMarker) {
    const direction = arrow ?? 'forward'
    directionalStart = direction === 'backward' || direction === 'both' ? semanticMarker : undefined
    directionalEnd = direction === 'forward' || direction === 'both' ? semanticMarker : undefined
    if (direction === 'none') directionalStart = directionalEnd = undefined
  }
  const markerStart = fixedStart ?? navigableStart ?? directionalStart
  const markerEnd = fixedEnd ?? navigableEnd ?? directionalEnd
  return {
    ...(markerStart ? { markerStart } : {}),
    ...(markerEnd ? { markerEnd } : {}),
  }
}

// Order parent containers before their children: React Flow requires a node's
// `parentId` target to appear earlier in the array. Nodes are sorted by nesting
// depth so arbitrarily deep containment is handled, not just one level. The sort
// is stable, so the relative order of same-depth nodes (and of all nodes when
// nothing is nested) is preserved. A `parentId` cycle is guarded against so a
// malformed diagram cannot cause infinite recursion.
function orderParentsFirst(nodes: GraphPilotNode[]): GraphPilotNode[] {
  if (!nodes.some((n) => n.parentId)) return nodes
  const byId = new Map(nodes.map((n) => [n.id, n]))
  const depth = (node: GraphPilotNode, seen = new Set<string>()): number => {
    if (!node.parentId || seen.has(node.id)) return 0
    seen.add(node.id)
    const parent = byId.get(node.parentId)
    return parent ? 1 + depth(parent, seen) : 0
  }
  return [...nodes].sort((a, b) => depth(a) - depth(b))
}

/**
 * Forward adapter: GraphPilot canonical JSON -> React Flow display state.
 *
 * Passes the real `node.type` (the universal 'gpNode') and the full canonical
 * `data` so the custom renderers (`nodeTypes`) can branch on `data.semanticType`,
 * plus `data.gpStyle` for type-specific visuals and `parentId`/`extent` for
 * containment. Edges carry a `markerEnd` derived from their semanticType. None of
 * these display fields are read by the reverse adapter, so they cannot leak into
 * saved JSON.
 */
export function graphPilotToReactFlow(diagram: GraphPilotDiagram): ReactFlowDiagram {
  const marked = !drawnEntirelyByHand(diagram)
  const nodes: Node[] = orderParentsFirst(diagram.nodes).map((node) => {
    const rf: Node = {
      id: node.id,
      type: node.type,
      position: { x: node.position.x, y: node.position.y },
      // `gpOrigin` carries the element's provenance to the renderer. It is display-only,
      // like `gpStyle`: the reverse adapter takes `origin` from the loaded diagram, never
      // from here, so it cannot leak back into saved JSON. Without it a reader could not
      // tell an element the source establishes from one somebody assumed — which is the
      // distinction the whole product exists to make visible.
      data: { ...node.data, gpStyle: node.style, gpOrigin: marked ? node.origin : undefined },
    }
    const size = nodeSizeCss(node)
    if (size) rf.style = size
    if (node.parentId) {
      // No `extent: 'parent'`: children are not pinned to the container, so a node can
      // be dragged out of a system-boundary. Drag-stop re-parenting
      // (in EditorPage) manages parentId; the renderer still nests children visually.
      rf.parentId = node.parentId
    }
    return rf
  })

  const edges: Edge[] = diagram.edges.map((edge) => {
    const route = edge.route
    const mapped: Edge = {
      id: edge.id,
      source: edge.source,
      target: edge.target,
    }
    if (edge.type) mapped.type = edge.type
    if (edge.label) mapped.label = edge.label
    if (edge.sourceHandle) mapped.sourceHandle = edge.sourceHandle
    if (edge.targetHandle) mapped.targetHandle = edge.targetHandle
    if (edge.data || route) mapped.data = { ...(edge.data ?? {}), ...(route ? { gpRoute: route } : {}) }
    if (edge.style) mapped.style = edge.style as CSSProperties
    const markerColor = edge.style?.stroke || 'var(--line-strong)'
    const { markerStart, markerEnd } = edgeMarkers(edge.data?.semanticType, edge.data?.arrow, edge.data, markerColor)
    if (markerStart) mapped.markerStart = markerStart
    if (markerEnd) mapped.markerEnd = markerEnd
    return mapped
  })

  return { nodes, edges, viewport: diagram.viewport }
}

// --- Reverse adapter: React Flow state -> canonical GraphPilot JSON ---
//
// The canonical schema is strict (`additionalProperties: false`), so the reverse
// direction whitelists fields explicitly. React Flow runtime/session-only fields
// (e.g. `selected`, `dragging`, `measured`, `positionAbsolute`) are never copied,
// because we only read the canonical fields below. For nodes/edges that were
// loaded, non-visual canonical fields are taken from the originally loaded diagram
// (keyed by id). For nodes/edges created on the canvas there is no
// original, so those canonical fields are recovered from the React Flow element's
// own `data`.

function finiteNumber(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function nonEmptyString(value: unknown): string | undefined {
  return typeof value === 'string' && value !== '' ? value : undefined
}

function cssToNodeStyle(style: CSSProperties | undefined): GraphPilotNodeStyle | undefined {
  if (!style) return undefined
  const out: GraphPilotNodeStyle = {}
  if (nonEmptyString(style.background)) out.background = style.background as string
  if (nonEmptyString(style.borderColor)) out.borderColor = style.borderColor as string
  if (nonEmptyString(style.color)) out.color = style.color as string
  const borderWidth = finiteNumber(style.borderWidth)
  if (borderWidth != null) out.borderWidth = borderWidth
  if (nonEmptyString(style.borderStyle)) out.borderStyle = style.borderStyle as string
  return Object.keys(out).length ? out : undefined
}

// Node visual style is the renderer's source of truth: the forward adapter puts
// it in `data.gpStyle` and the property panel edits it there, so the reverse
// adapter reads it back from there (whitelisting the supported keys). This keeps
// the wrapper `style` free of visual fields and lets recolours repaint the custom
// shape live.
function normalizeGpStyle(value: unknown): GraphPilotNodeStyle | undefined {
  if (!value || typeof value !== 'object') return undefined
  const v = value as Record<string, unknown>
  const out: GraphPilotNodeStyle = {}
  if (nonEmptyString(v.background)) out.background = v.background as string
  if (nonEmptyString(v.borderColor)) out.borderColor = v.borderColor as string
  if (nonEmptyString(v.color)) out.color = v.color as string
  const borderWidth = finiteNumber(v.borderWidth)
  if (borderWidth != null) out.borderWidth = borderWidth
  if (nonEmptyString(v.borderStyle)) out.borderStyle = v.borderStyle as string
  return Object.keys(out).length ? out : undefined
}

// Recover every canonical semantic field from live React Flow data while excluding
// display/runtime keys such as `gpStyle`. Since the forward adapter copies canonical
// data into React Flow, an absent key represents an intentional inspector clear.
const NODE_DATA_KEYS = [
  'semanticType',
  'stereotype',
  'description',
  'metadata',
  'appliedStereotypes',
  'features',
  'extensionPoints',
  'isAbstract',
  'unit',
  'quantityKind',
  'constraintExpression',
  'constraintParameters',
  'port',
  'joinSpec',
] as const satisfies readonly (keyof GraphPilotNodeData)[]

const EDGE_DATA_KEYS = [
  'semanticType',
  'description',
  'metadata',
  'appliedStereotypes',
  'sourceEnd',
  'targetEnd',
  'condition',
  'extensionLocations',
  'itemFlows',
  'guard',
  'weight',
  'isInterrupting',
  'arrow',
] as const satisfies readonly (keyof GraphPilotEdgeData)[]

/**
 * Put `items` back into the order they were loaded in, leaving anything new at the end.
 *
 * Only elements that were in `originals` are reordered; nodes created on the canvas have
 * no original position in the file and are appended in the order they were drawn.
 */
function restoreOriginalOrder<T extends { id: string }>(items: T[], originals: readonly T[]): void {
  const rank = new Map(originals.map((item, index) => [item.id, index]))
  const after = originals.length
  items.sort((a, b) => (rank.get(a.id) ?? after) - (rank.get(b.id) ?? after))
}

/**
 * The provenance of something a person drew on the canvas.
 *
 * A loaded element keeps the origin the backend gave it; anything created here has none,
 * and `origin` is required on every element of an `as_implemented` diagram — so adding a
 * node to a grounded diagram used to fail the save with a schema error naming a field the
 * person had never heard of.
 *
 * `user` is the honest answer to "how do we know this?". The alternatives were all worse:
 * `grounded` would fabricate a citation, `assumed` would invent an assumption nobody
 * accepted, and `conceptual` is a claim about the whole diagram rather than one element.
 * A host may never author it — only this path can make it true.
 */
function drawnByHand(): GraphPilotElementOrigin {
  return {
    assurance: 'user',
    evidenceRefs: [],
    assumptionRefs: [],
    schemaRules: [],
    rationale: 'Added in the editor by a person. Not established by the cited source.',
  }
}

/**
 * Whether this diagram records where its elements came from at all.
 *
 * `user` answers "how do we know this?" in a diagram that asks the question. A diagram
 * nobody drafted never asks it: `createBlankDiagram` writes no `authority`, so `origin`
 * is not required, nothing else in the file carries one, and stamping every element a
 * person draws marks the norm rather than the exception. Every node of every hand-drawn
 * export came out wearing a pencil badge.
 */
function carriesProvenance(diagram: GraphPilotDiagram): boolean {
  return diagram.metadata?.authority === 'as_implemented'
    || diagram.nodes.some((node) => node.origin)
    || diagram.edges.some((edge) => edge.origin)
}

/**
 * True when every element is one a person drew here.
 *
 * The canvas mirror of `_drawn_entirely_by_hand` in `diagram_render_service.py`: a badge
 * is an admission, and an admission is only information beside something it is not. This
 * catches diagrams saved before `carriesProvenance` existed, which carry `user` on every
 * element and would otherwise stay badged forever.
 */
function drawnEntirelyByHand(diagram: GraphPilotDiagram): boolean {
  const elements = [...diagram.nodes, ...diagram.edges]
  return elements.length > 0 && elements.every((el) => el.origin?.assurance === 'user')
}

function recoverCanonicalData<T extends object>(
  original: T | undefined,
  rfData: unknown,
  keys: readonly string[],
): T {
  const out = { ...(original ?? {}) } as Record<string, unknown>
  const live = rfData && typeof rfData === 'object' ? rfData as Record<string, unknown> : {}
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(live, key) && live[key] !== undefined) out[key] = live[key]
    else delete out[key]
  }
  return out as T
}

/**
 * Reverse adapter: merge edited / authored React Flow state back into canonical
 * GraphPilot JSON. `original` is the diagram as loaded; it supplies the canonical
 * fields the canvas does not edit for loaded elements. Elements created on the
 * canvas have no original, so their canonical fields come from their own `data`.
 * Positive sizes only are persisted (the backend rejects non-positive sizes). A node
 * label that is absent falls back to the original; an explicitly emptied label is kept
 * empty (labels are required, so the backend rejects the save rather than silently
 * restoring the old label).
 */
export function reactFlowToGraphPilot(
  original: GraphPilotDiagram,
  nodes: Node[],
  edges: Edge[],
  viewport?: Viewport,
): GraphPilotDiagram {
  const originalNodeById = new Map(original.nodes.map((node) => [node.id, node]))
  const originalEdgeById = new Map(original.edges.map((edge) => [edge.id, edge]))
  const stampNew = carriesProvenance(original)

  const outNodes: GraphPilotNode[] = nodes.map((rf) => {
    const orig = originalNodeById.get(rf.id)
    const style = rf.style as CSSProperties | undefined
    const label = (rf.data?.label as string | undefined) ?? orig?.data.label ?? ''

    const data = recoverCanonicalData<GraphPilotNodeData>(orig?.data, rf.data, NODE_DATA_KEYS)
    data.label = label

    const node: GraphPilotNode = {
      id: rf.id,
      type: orig?.type ?? (typeof rf.type === 'string' ? rf.type : 'default'),
      position: { x: rf.position.x, y: rf.position.y },
      data,
    }

    // Size is taken from the edited style (the property panel writes width/height
    // there) or the original. React Flow's own `rf.width`/`rf.height` are measured
    // runtime dimensions, so they are intentionally NOT used as a fallback to keep
    // them from leaking into saved JSON.
    const width = finiteNumber(style?.width) ?? orig?.width
    const height = finiteNumber(style?.height) ?? orig?.height
    if (width != null && width > 0) node.width = width
    if (height != null && height > 0) node.height = height

    // Prefer the renderer's `data.gpStyle` (where the property panel writes), then
    // any visual style left on the wrapper, then the originally loaded style.
    const nodeStyle = normalizeGpStyle(rf.data?.gpStyle) ?? cssToNodeStyle(style) ?? orig?.style
    if (nodeStyle) node.style = nodeStyle

    // `rf.parentId` is the source of truth: the forward adapter sets it from the loaded
    // diagram and drag-stop re-parenting updates it, so clearing it (dragging a node out
    // of a container) persists instead of reverting to the originally-loaded parent.
    const parentId = typeof rf.parentId === 'string' ? rf.parentId : undefined
    if (parentId) node.parentId = parentId
    // Only something genuinely new, and only in a diagram that records provenance. A
    // loaded element keeps what it had, including nothing: a diagram written before
    // origins existed was not drawn by hand, it just predates the field, and stamping it
    // would invent provenance for 48 committed files.
    if (orig?.origin) node.origin = orig.origin
    else if (!orig && stampNew) node.origin = drawnByHand()

    return node
  })

  // React Flow requires a parent to precede its children, so the forward adapter sorts
  // containers first. Nothing put the order back, which meant loading and saving a
  // diagram whose children were written before their container silently reordered its
  // nodes — a save that changed nothing still produced a diff. Order carries no meaning,
  // which is exactly why it should not move.
  restoreOriginalOrder(outNodes, original.nodes)

  const outEdges: GraphPilotEdge[] = edges.map((rf) => {
    const orig = originalEdgeById.get(rf.id)
    const edge: GraphPilotEdge = {
      id: rf.id,
      source: rf.source,
      target: rf.target,
    }
    const type = (typeof rf.type === 'string' ? rf.type : undefined) ?? orig?.type
    if (type) edge.type = type
    const label = typeof rf.label === 'string' ? rf.label : orig?.label
    if (nonEmptyString(label)) edge.label = label as string
    if (rf.sourceHandle) edge.sourceHandle = rf.sourceHandle
    if (rf.targetHandle) edge.targetHandle = rf.targetHandle

    // Every canonical structured edge field is read from live state for both loaded
    // and canvas-origin edges so inspector edits and cloned data survive the save.
    const edgeData = recoverCanonicalData<GraphPilotEdgeData>(orig?.data, rf.data, EDGE_DATA_KEYS)
    if (Object.keys(edgeData).length) edge.data = edgeData

    const edgeStyle = cssToEdgeStyle(rf.style as CSSProperties | undefined) ?? orig?.style
    if (edgeStyle) edge.style = edgeStyle

    const rawRoute = (rf.data as Record<string, unknown> | undefined)?.gpRoute
    if (rawRoute !== undefined) {
      const unchanged = orig?.route !== undefined && JSON.stringify(rawRoute) === JSON.stringify(orig.route)
      const route = unchanged ? orig.route : normalizeRouteGeometry(rawRoute)
      if (route) edge.route = route
    }
    if (orig?.origin) edge.origin = orig.origin
    else if (!orig && stampNew) edge.origin = drawnByHand()

    return edge
  })

  return {
    schemaVersion: original.schemaVersion,
    kind: original.kind,
    diagramType: original.diagramType,
    id: original.id,
    name: original.name,
    metadata: original.metadata,
    viewport: viewport ?? original.viewport,
    nodes: outNodes,
    edges: outEdges,
  }
}

function cssToEdgeStyle(style: CSSProperties | undefined): GraphPilotEdgeStyle | undefined {
  if (!style) return undefined
  const out: GraphPilotEdgeStyle = {}
  if (nonEmptyString(style.stroke)) out.stroke = style.stroke as string
  const strokeWidth = finiteNumber(style.strokeWidth)
  if (strokeWidth != null) out.strokeWidth = strokeWidth
  if (nonEmptyString(style.strokeDasharray)) out.strokeDasharray = String(style.strokeDasharray)
  return Object.keys(out).length ? out : undefined
}
