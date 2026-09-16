import type {
  GraphPilotEdgeRoute,
  GraphPilotPoint,
  GraphPilotRouteAnchor,
  GraphPilotRouteMode,
  GraphPilotRouteSide,
} from '@/types/diagram'

export interface NodeRect {
  x: number
  y: number
  w: number
  h: number
  primitive?: string
  label?: string
}

export type Pt = GraphPilotPoint
export type RouteSide = GraphPilotRouteSide
export type RouteAnchor = GraphPilotRouteAnchor
export type RouteMode = GraphPilotRouteMode
export type RouteGeometry = GraphPilotEdgeRoute
export type AttachmentShape = 'box' | 'diamond' | 'ellipse'

export interface AttachmentProfile {
  shape: AttachmentShape
  bounds: Pick<NodeRect, 'x' | 'y' | 'w' | 'h'>
}

const ROUTE_SIDES = new Set<RouteSide>(['top', 'right', 'bottom', 'left'])
const CONTROL_PRIMITIVES = new Set(['initial', 'final', 'flow-final'])
const LABEL_HEIGHT = 14.4

export function attachmentProfile(rect: NodeRect): AttachmentProfile {
  if (CONTROL_PRIMITIVES.has(rect.primitive ?? '')) {
    const top = rect.y + Math.max(0, (rect.h - 34 - (rect.label?.trim() ? LABEL_HEIGHT : 0)) / 2)
    return { shape: 'ellipse', bounds: { x: rect.x + (rect.w - 34) / 2 + 2, y: top + 2, w: 30, h: 30 } }
  }
  if (rect.primitive === 'actor') {
    const contentHeight = Math.max(0, rect.h - 8)
    const itemsHeight = 48 + (rect.label?.trim() ? LABEL_HEIGHT : 0)
    const top = rect.y + 4 + Math.max(0, (contentHeight - itemsHeight) / 2)
    return { shape: 'ellipse', bounds: { x: rect.x + (rect.w - 34) / 2 + 5, y: top + 2, w: 24, h: 42 } }
  }
  if (rect.primitive === 'ellipse') return { shape: 'ellipse', bounds: { x: rect.x, y: rect.y, w: rect.w, h: rect.h } }
  if (rect.primitive === 'diamond') return { shape: 'diamond', bounds: { x: rect.x, y: rect.y, w: rect.w, h: rect.h } }
  return { shape: 'box', bounds: { x: rect.x, y: rect.y, w: rect.w, h: rect.h } }
}

function routePoint(value: unknown): Pt | undefined {
  if (!value || typeof value !== 'object') return undefined
  const point = value as Record<string, unknown>
  return typeof point.x === 'number' && Number.isFinite(point.x) && typeof point.y === 'number' && Number.isFinite(point.y)
    ? { x: point.x, y: point.y }
    : undefined
}

function routeAnchor(value: unknown): RouteAnchor | undefined {
  if (!value || typeof value !== 'object') return undefined
  const anchor = value as Record<string, unknown>
  return typeof anchor.side === 'string' && ROUTE_SIDES.has(anchor.side as RouteSide) &&
    typeof anchor.offset === 'number' && Number.isFinite(anchor.offset) && anchor.offset >= 0 && anchor.offset <= 1
    ? { side: anchor.side as RouteSide, offset: anchor.offset }
    : undefined
}

export function normalizeRouteGeometry(value: unknown): RouteGeometry | undefined {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined
  const route = value as Record<string, unknown>
  if (route.mode !== undefined && route.mode !== 'orthogonal' && route.mode !== 'straight') return undefined
  const mode = route.mode as RouteMode | undefined
  const sourceAnchor = routeAnchor(route.sourceAnchor)
  const targetAnchor = routeAnchor(route.targetAnchor)
  const waypoints = mode === 'straight' ? undefined : Array.isArray(route.waypoints)
    ? route.waypoints.map(routePoint).filter((point): point is Pt => point !== undefined).slice(0, 32)
    : undefined
  const labelOffset = routePoint(route.labelOffset)
  const normalized: RouteGeometry = {
    ...(mode ? { mode } : {}),
    ...(sourceAnchor ? { sourceAnchor } : {}),
    ...(targetAnchor ? { targetAnchor } : {}),
    ...(waypoints?.length ? { waypoints: normalizeOrthogonalPoints(waypoints) } : {}),
    ...(labelOffset ? { labelOffset } : {}),
  }
  return Object.keys(normalized).length ? normalized : undefined
}

export function setRouteMode(route: RouteGeometry | undefined, mode: RouteMode): RouteGeometry {
  return normalizeRouteGeometry({ ...(route ?? {}), mode, waypoints: mode === 'straight' ? undefined : route?.waypoints }) ?? { mode }
}

export function pointsToPath(points: Pt[]): string {
  return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
}

function clampOffset(offset: number): number {
  return Math.min(1, Math.max(0, Number.isFinite(offset) ? offset : 0.5))
}

function boxPoint(rect: NodeRect, anchor: RouteAnchor): Pt {
  const offset = clampOffset(anchor.offset)
  if (anchor.side === 'top') return { x: rect.x + rect.w * offset, y: rect.y }
  if (anchor.side === 'bottom') return { x: rect.x + rect.w * offset, y: rect.y + rect.h }
  if (anchor.side === 'left') return { x: rect.x, y: rect.y + rect.h * offset }
  return { x: rect.x + rect.w, y: rect.y + rect.h * offset }
}

export function anchorPoint(rect: NodeRect, anchor: RouteAnchor): Pt {
  const encoded = boxPoint(rect, anchor)
  const profile = attachmentProfile(rect)
  if (profile.shape === 'box') return encoded
  const rx = Math.max(profile.bounds.w / 2, 0.001)
  const ry = Math.max(profile.bounds.h / 2, 0.001)
  const cx = profile.bounds.x + rx
  const cy = profile.bounds.y + ry
  const dx = encoded.x - cx
  const dy = encoded.y - cy
  const scale = profile.shape === 'diamond'
    ? 1 / Math.max(Math.abs(dx) / rx + Math.abs(dy) / ry, 0.001)
    : 1 / Math.max(Math.hypot(dx / rx, dy / ry), 0.001)
  return { x: cx + dx * scale, y: cy + dy * scale }
}

function radialBoxAnchor(rect: NodeRect, center: Pt, point: Pt): RouteAnchor {
  const dx = point.x - center.x
  const dy = point.y - center.y
  if (Math.abs(dx) < 0.001 && Math.abs(dy) < 0.001) return { side: 'top', offset: 0.5 }
  const candidates: Array<{ side: RouteSide; scale: number }> = []
  if (dx > 0) candidates.push({ side: 'right', scale: (rect.x + rect.w - center.x) / dx })
  else if (dx < 0) candidates.push({ side: 'left', scale: (rect.x - center.x) / dx })
  if (dy > 0) candidates.push({ side: 'bottom', scale: (rect.y + rect.h - center.y) / dy })
  else if (dy < 0) candidates.push({ side: 'top', scale: (rect.y - center.y) / dy })
  const hit = candidates.filter((candidate) => candidate.scale >= 0).sort((left, right) => left.scale - right.scale)[0]
  if (!hit) return { side: 'top', offset: 0.5 }
  const x = center.x + dx * hit.scale
  const y = center.y + dy * hit.scale
  const offset = hit.side === 'top' || hit.side === 'bottom'
    ? (x - rect.x) / Math.max(rect.w, 1)
    : (y - rect.y) / Math.max(rect.h, 1)
  return { side: hit.side, offset: clampOffset(offset) }
}

function profileCenter(rect: NodeRect): Pt {
  const bounds = attachmentProfile(rect).bounds
  return { x: bounds.x + bounds.w / 2, y: bounds.y + bounds.h / 2 }
}

function automaticStraightAnchors(source: NodeRect, target: NodeRect, geometry: RouteGeometry): { source: RouteAnchor; target: RouteAnchor } {
  let sourceAnchor = geometry.sourceAnchor
  let targetAnchor = geometry.targetAnchor
  if (!sourceAnchor && !targetAnchor) {
    sourceAnchor = radialBoxAnchor(source, profileCenter(source), profileCenter(target))
    targetAnchor = radialBoxAnchor(target, profileCenter(target), profileCenter(source))
  } else if (!sourceAnchor && targetAnchor) {
    sourceAnchor = radialBoxAnchor(source, profileCenter(source), anchorPoint(target, targetAnchor))
  } else if (sourceAnchor && !targetAnchor) {
    targetAnchor = radialBoxAnchor(target, profileCenter(target), anchorPoint(source, sourceAnchor))
  }
  return { source: sourceAnchor!, target: targetAnchor! }
}

export function boundaryAnchor(rect: NodeRect, point: Pt): RouteAnchor {
  const profile = attachmentProfile(rect)
  if (profile.shape === 'box') {
    const distances = [
      { side: 'top' as const, distance: Math.abs(point.y - rect.y) },
      { side: 'right' as const, distance: Math.abs(point.x - (rect.x + rect.w)) },
      { side: 'bottom' as const, distance: Math.abs(point.y - (rect.y + rect.h)) },
      { side: 'left' as const, distance: Math.abs(point.x - rect.x) },
    ].sort((left, right) => left.distance - right.distance)
    const side = distances[0].side
    const offset = side === 'top' || side === 'bottom'
      ? (point.x - rect.x) / Math.max(rect.w, 1)
      : (point.y - rect.y) / Math.max(rect.h, 1)
    return { side, offset: clampOffset(offset) }
  }
  const center = {
    x: profile.bounds.x + profile.bounds.w / 2,
    y: profile.bounds.y + profile.bounds.h / 2,
  }
  return radialBoxAnchor(rect, center, point)
}

export interface ResolvedAttachment {
  anchor: RouteAnchor
  point: Pt
  distance: number
  snapped?: RouteSide
}

export function boundaryLocation(rect: NodeRect, point: Pt): ResolvedAttachment {
  const anchor = boundaryAnchor(rect, point)
  const projected = anchorPoint(rect, anchor)
  return { anchor, point: projected, distance: Math.hypot(point.x - projected.x, point.y - projected.y) }
}

export function resolveAttachmentAnchor(rect: NodeRect, point: Pt, zoom: number, snapPixels = 8): ResolvedAttachment {
  const exact = boundaryLocation(rect, point)
  const profile = attachmentProfile(rect).bounds
  const cardinalPoints: Array<{ side: RouteSide; point: Pt }> = [
    { side: 'top', point: { x: profile.x + profile.w / 2, y: profile.y } },
    { side: 'right', point: { x: profile.x + profile.w, y: profile.y + profile.h / 2 } },
    { side: 'bottom', point: { x: profile.x + profile.w / 2, y: profile.y + profile.h } },
    { side: 'left', point: { x: profile.x, y: profile.y + profile.h / 2 } },
  ]
  const scale = Math.max(zoom, 0.01)
  const nearest = cardinalPoints
    .map((cardinal) => ({ ...cardinal, distance: Math.hypot(exact.point.x - cardinal.point.x, exact.point.y - cardinal.point.y) * scale }))
    .sort((left, right) => left.distance - right.distance)[0]
  if (nearest.distance > snapPixels) return exact
  const anchor = boundaryAnchor(rect, nearest.point)
  const projected = anchorPoint(rect, anchor)
  return { anchor, point: projected, distance: Math.hypot(point.x - projected.x, point.y - projected.y), snapped: nearest.side }
}

function outward(point: Pt, side: RouteSide, distance = 16): Pt {
  if (side === 'top') return { x: point.x, y: point.y - distance }
  if (side === 'bottom') return { x: point.x, y: point.y + distance }
  if (side === 'left') return { x: point.x - distance, y: point.y }
  return { x: point.x + distance, y: point.y }
}

export function automaticAnchors(source: NodeRect, target: NodeRect): { source: RouteAnchor; target: RouteAnchor } {
  const dx = target.x + target.w / 2 - (source.x + source.w / 2)
  const dy = target.y + target.h / 2 - (source.y + source.h / 2)
  const overlapLeft = Math.max(source.x, target.x)
  const overlapRight = Math.min(source.x + source.w, target.x + target.w)
  if (overlapLeft <= overlapRight) {
    const x = (overlapLeft + overlapRight) / 2
    return dy >= 0
      ? {
          source: { side: 'bottom', offset: clampOffset((x - source.x) / Math.max(source.w, 1)) },
          target: { side: 'top', offset: clampOffset((x - target.x) / Math.max(target.w, 1)) },
        }
      : {
          source: { side: 'top', offset: clampOffset((x - source.x) / Math.max(source.w, 1)) },
          target: { side: 'bottom', offset: clampOffset((x - target.x) / Math.max(target.w, 1)) },
        }
  }
  const overlapTop = Math.max(source.y, target.y)
  const overlapBottom = Math.min(source.y + source.h, target.y + target.h)
  if (overlapTop <= overlapBottom) {
    const y = (overlapTop + overlapBottom) / 2
    return dx >= 0
      ? {
          source: { side: 'right', offset: clampOffset((y - source.y) / Math.max(source.h, 1)) },
          target: { side: 'left', offset: clampOffset((y - target.y) / Math.max(target.h, 1)) },
        }
      : {
          source: { side: 'left', offset: clampOffset((y - source.y) / Math.max(source.h, 1)) },
          target: { side: 'right', offset: clampOffset((y - target.y) / Math.max(target.h, 1)) },
        }
  }
  const horizontal = {
    source: { side: (dx >= 0 ? 'right' : 'left') as RouteSide, offset: 0.5 },
    target: { side: (dy >= 0 ? 'top' : 'bottom') as RouteSide, offset: 0.5 },
  }
  const vertical = {
    source: { side: (dy >= 0 ? 'bottom' : 'top') as RouteSide, offset: 0.5 },
    target: { side: (dx >= 0 ? 'left' : 'right') as RouteSide, offset: 0.5 },
  }
  const horizontalPoints = connectPair(anchorPoint(source, horizontal.source), anchorPoint(target, horizontal.target), true)
  const verticalPoints = connectPair(anchorPoint(source, vertical.source), anchorPoint(target, vertical.target), false)
  const horizontalLength = routeLength(horizontalPoints)
  const verticalLength = routeLength(verticalPoints)
  return horizontalLength < verticalLength || (horizontalLength === verticalLength && Math.abs(dx) >= Math.abs(dy))
    ? horizontal
    : vertical
}

// How far a relationship end's role/multiplicity sits from its endpoint: along the edge to
// clear the node boundary and any marker, then sideways to clear the line. Mirrors
// _END_LABEL_CLEARANCE / _END_LABEL_SIDESTEP in diagram_render_service.py.
export const END_LABEL_CLEARANCE = 22
export const END_LABEL_SIDESTEP = 13

/** Unit vector from *from* towards *to*, or a sane default when they coincide. */
export function segmentDirection(from: Pt, to: Pt): Pt {
  const dx = to.x - from.x
  const dy = to.y - from.y
  const length = Math.hypot(dx, dy)
  return length < 0.001 ? { x: 0, y: -1 } : { x: dx / length, y: dy / length }
}

/**
 * Where a relationship end's role/multiplicity is drawn.
 *
 * *outward* points from the node into the diagram. A fixed offset cannot work: on an
 * endpoint sitting on a node's bottom edge it placed the text back inside the node, on
 * top of the node's own label.
 */
export function endLabelPosition(point: Pt, outward: Pt): Pt {
  return {
    x: point.x + outward.x * END_LABEL_CLEARANCE - outward.y * END_LABEL_SIDESTEP,
    y: point.y + outward.y * END_LABEL_CLEARANCE + outward.x * END_LABEL_SIDESTEP,
  }
}

export interface FanOutEdge {
  id: string
  source: string
  target: string
  geometry?: RouteGeometry
  sourceHandle?: string | null
  targetHandle?: string | null
}

/** Boxes grow by this much when testing a route against them: a line running exactly
 *  along a node's edge is not technically through it and reads as though it is. */
const ROUTE_CLEARANCE = 6

function segmentHitsRect(a: Pt, b: Pt, rect: NodeRect): boolean {
  const left = rect.x - ROUTE_CLEARANCE
  const right = rect.x + rect.w + ROUTE_CLEARANCE
  const top = rect.y - ROUTE_CLEARANCE
  const bottom = rect.y + rect.h + ROUTE_CLEARANCE
  if (Math.abs(a.y - b.y) < 0.001) {
    const [low, high] = a.x <= b.x ? [a.x, b.x] : [b.x, a.x]
    return top < a.y && a.y < bottom && low < right && left < high
  }
  if (Math.abs(a.x - b.x) < 0.001) {
    const [low, high] = a.y <= b.y ? [a.y, b.y] : [b.y, a.y]
    return left < a.x && a.x < right && low < bottom && top < high
  }
  return false
}

export function routeCrossings(points: Pt[], blockers: NodeRect[]): number {
  return blockers.filter((rect) =>
    points.slice(1).some((point, index) => segmentHitsRect(points[index], point, rect)),
  ).length
}

/** The faces of `rect` that point towards `other`, nearest first. */
function facing(rect: NodeRect, other: NodeRect): RouteSide[] {
  const dx = other.x + other.w / 2 - (rect.x + rect.w / 2)
  const dy = other.y + other.h / 2 - (rect.y + rect.h / 2)
  const horizontal: RouteSide = dx >= 0 ? 'right' : 'left'
  const vertical: RouteSide = dy >= 0 ? 'bottom' : 'top'
  return Math.abs(dy) >= Math.abs(dx) ? [vertical, horizontal] : [horizontal, vertical]
}

/**
 * Pick the pair of faces whose route does not run through a third node.
 *
 * Mirrors `_faces_clear_of` in `diagram_render_service.py`. Only faces pointing at the
 * other node are eligible — without that the search will leave the top of a block to
 * reach one below it, which has fewer crossings and is unreadable.
 */
export function facesClearOf(
  source: NodeRect,
  target: NodeRect,
  anchors: { source: RouteAnchor; target: RouteAnchor },
  blockers: NodeRect[],
  crowding?: (side: RouteSide) => number,
): { source: RouteAnchor; target: RouteAnchor } {
  if (blockers.length === 0) return anchors
  const score = (
    pair: { source: RouteAnchor; target: RouteAnchor },
  ): [number, number, number, number] => {
    const points = minimalAnchoredRoute(
      anchorPoint(source, pair.source), anchorPoint(target, pair.target),
      pair.source, pair.target, blockers,
    )
    return [
      routeCrossings(points, blockers),
      crowding ? crowding(pair.target.side) : 0,
      routeBendCount(points),
      routeLength(points),
    ]
  }
  const below = (a: number[], b: number[]) => {
    for (let index = 0; index < a.length; index += 1) {
      if (a[index] !== b[index]) return a[index] < b[index]
    }
    return false
  }

  let best = anchors
  let bestScore = score(anchors)
  if (bestScore[0] === 0) return anchors
  for (const sourceSide of facing(source, target)) {
    for (const targetSide of facing(target, source)) {
      const candidate = {
        source: { side: sourceSide, offset: 0.5 },
        target: { side: targetSide, offset: 0.5 },
      }
      const candidateScore = score(candidate)
      if (below(candidateScore, bestScore)) {
        best = candidate
        bestScore = candidateScore
        // Clear *and* unoccupied. Stopping on `clear` alone was the defect: `facing` puts
        // the most direct face first, so a rewired edge took it the moment it crossed
        // nothing and the other terms were never read. Right when the face is free — it is
        // why three parts of one whole fan onto left, top and right — and wrong when it is
        // already taken, which is how an edge ran the length of a third node to arrive
        // beside its neighbour on a face it had to share.
        if (candidateScore[0] === 0 && candidateScore[1] === 0) return best
      }
    }
  }
  return best
}

/**
 * Spread endpoints that would otherwise be drawn on the same point.
 *
 * Anchors are chosen per edge, so several edges reaching the same side of the same node
 * all get that side's centre and land on top of one another — three parts composing into
 * one block read as an unrelated chain. This regroups the automatic anchors by
 * (node, side) and spreads each group evenly, ordered by where the other end sits along
 * that side's axis so the fan opens without the lines crossing.
 *
 * Mirrors `_fan_out_anchors` in `diagram_render_service.py`; the canvas and the SVG
 * export must agree.
 *
 * Authored anchors, explicit handles, and manual waypoints are left alone: a user who
 * positioned an edge outranks this.
 */
export function fanOutAnchors(
  edges: FanOutEdge[],
  rects: Map<string, NodeRect>,
  containerIds?: Set<string>,
): Map<string, { sourceAnchor?: RouteAnchor; targetAnchor?: RouteAnchor }> {
  const base = new Map<string, { source: RouteAnchor; target: RouteAnchor }>()
  const natural = new Map<string, { source: RouteAnchor; target: RouteAnchor }>()

  // Which faces the edges are already aiming at, worked out before any of them is moved.
  // Face choice is otherwise made one edge at a time with no knowledge of the others,
  // which is the same blind spot that makes the spreading below necessary at all.
  const aimedAt = new Map<string, number>()
  for (const edge of edges) {
    const source = rects.get(edge.source)
    const target = rects.get(edge.target)
    if (!source || !target) continue
    const geometry = edge.geometry ?? {}
    // An authored anchor counts where it was put; everything else counts where routing
    // would naturally send it. Handles are ignored here on purpose, so this pass is the
    // same two lines in both implementations — it is a tiebreak, not a contract.
    const side = (geometry.targetAnchor ?? automaticAnchors(source, target).target).side
    const key = `${edge.target}\u0000${side}`
    aimedAt.set(key, (aimedAt.get(key) ?? 0) + 1)
  }

  for (const edge of edges) {
    const source = rects.get(edge.source)
    const target = rects.get(edge.target)
    if (!source || !target) continue
    const geometry = edge.geometry ?? {}
    if (geometry.sourceAnchor || geometry.targetAnchor || geometry.waypoints?.length ||
        edge.sourceHandle || edge.targetHandle) continue
    if (geometry.mode === 'straight') {
      const anchors = automaticStraightAnchors(source, target, geometry)
      base.set(edge.id, anchors)
      natural.set(edge.id, anchors)
      continue
    }
    const anchors = automaticAnchors(source, target)
    natural.set(edge.id, anchors)
    // Faces are chosen before offsets are spread, because an edge moved onto a different
    // face to dodge a node would otherwise land on whatever already occupies that face.
    // The natural anchors see only the two boxes, so they will happily send a line
    // straight through a third node.
    const blockers: NodeRect[] = []
    for (const [id, rect] of rects) {
      if (id === edge.source || id === edge.target) continue
      if (containerIds?.has(id)) continue
      blockers.push(rect)
    }
    const ownSide = anchors.target.side
    const crowding = (side: RouteSide) =>
      (aimedAt.get(`${edge.target}\u0000${side}`) ?? 0) - (side === ownSide ? 1 : 0)
    base.set(edge.id, facesClearOf(source, target, anchors, blockers, crowding))
  }

  // Keyed by (node, side) only: an edge leaving a side and another arriving at it are two
  // points on the same stretch of boundary, so they compete for the same space.
  const groups = new Map<string, Array<{ id: string; end: 'source' | 'target' }>>()
  const byId = new Map(edges.map((edge) => [edge.id, edge]))
  for (const [id, anchors] of base) {
    const edge = byId.get(id)!
    for (const end of ['source', 'target'] as const) {
      const key = `${end === 'source' ? edge.source : edge.target}\u0000${anchors[end].side}`
      const bucket = groups.get(key) ?? []
      bucket.push({ id, end })
      groups.set(key, bucket)
    }
  }

  // An override is a *change* from what routing would work out on its own, so a face moved
  // to dodge a node is carried even when it is the only edge on that face.
  const overrides = new Map<string, { sourceAnchor?: RouteAnchor; targetAnchor?: RouteAnchor }>()
  for (const [id, anchors] of base) {
    const natural_ = natural.get(id)!
    const moved: { sourceAnchor?: RouteAnchor; targetAnchor?: RouteAnchor } = {}
    // Compared whole, side *and* offset. Comparing only the side meant that when
    // `facesClearOf` kept a face but moved the point along it, the move was dropped and
    // the natural offset drawn instead — so the route scored as clear was not the route
    // that appeared. A rewired edge was drawn from directly above the node it was meant
    // to avoid, and went straight down through it.
    const same = (a: RouteAnchor, b: RouteAnchor) => a.side === b.side && a.offset === b.offset
    if (!same(anchors.source, natural_.source)) moved.sourceAnchor = anchors.source
    if (!same(anchors.target, natural_.target)) moved.targetAnchor = anchors.target
    if (moved.sourceAnchor || moved.targetAnchor) overrides.set(id, moved)
  }

  for (const [key, members] of groups) {
    if (members.length < 2) continue
    const nodeId = key.split('\u0000')[0]
    const side = key.split('\u0000')[1] as RouteSide
    const along = (member: { id: string; end: 'source' | 'target' }) => {
      const edge = byId.get(member.id)!
      const other = rects.get(member.end === 'source' ? edge.target : edge.source)
      if (!other) return 0
      return side === 'top' || side === 'bottom' ? other.x + other.w / 2 : other.y + other.h / 2
    }
    const ordered = [...members].sort((left, right) => along(left) - along(right))
    const spread = new Map<string, RouteAnchor>(
      ordered.map((member, rank) => [
        member.id, { side, offset: (rank + 1) / (ordered.length + 1) },
      ]),
    )
    const box = rects.get(nodeId)
    if (box && spreadingOnlyMakesItWorse(box, side, ordered, spread, base, byId, rects, containerIds)) {
      continue
    }
    ordered.forEach((member) => {
      const current = overrides.get(member.id) ?? {}
      const anchor = spread.get(member.id)!
      overrides.set(member.id, member.end === 'source'
        ? { ...current, sourceAnchor: anchor }
        : { ...current, targetAnchor: anchor })
    })
  }
  return overrides
}

/**
 * How far apart two endpoints on one side must be before spreading leaves them alone.
 * An arrowhead is about 10px across, so this is roughly two of them.
 */
const MIN_ANCHOR_GAP = 22

/**
 * Whether a group is better off left where it is.
 *
 * Mirrors `_spreading_only_makes_it_worse` in `diagram_render_service.py`; the canvas and
 * the SVG export must agree, and the shared fixtures in
 * `backend/tests/edge_routing_fixtures.json` are what hold them to it.
 *
 * Three conditions, all required. The endpoints must already be clear of one another —
 * measured in pixels along the face, because a 0.2 gap is 32px on a 160px block and 12px
 * on a 60px one. Leaving them alone must add no crossing, since spreading sometimes moves
 * an edge off a line that would have gone through a third node, and that is worth a bend.
 * And it must remove at least one bend, or there is nothing to win.
 *
 * Without this the fan-out took two edges whose boxes overlap — already far apart, already
 * drawn straight, because `automaticAnchors` derives those offsets from the overlap — and
 * put a two-bend dog-leg in each. A person straightening them in the editor could not make
 * it stick: the anchors that bend them are recomputed on every render, not stored.
 */
function spreadingOnlyMakesItWorse(
  box: NodeRect,
  side: RouteSide,
  members: Array<{ id: string; end: 'source' | 'target' }>,
  spread: Map<string, RouteAnchor>,
  base: Map<string, { source: RouteAnchor; target: RouteAnchor }>,
  byId: Map<string, FanOutEdge>,
  rects: Map<string, NodeRect>,
  containerIds?: Set<string>,
): boolean {
  const extent = side === 'top' || side === 'bottom' ? box.w : box.h
  const positions: number[] = []
  for (const member of members) {
    const anchors = base.get(member.id)
    if (!anchors) return false
    const anchor = member.end === 'source' ? anchors.source : anchors.target
    if (anchor.side !== side) return false
    positions.push(anchor.offset * extent)
  }
  positions.sort((left, right) => left - right)
  for (let index = 1; index < positions.length; index += 1) {
    if (positions[index] - positions[index - 1] < MIN_ANCHOR_GAP) return false
  }

  let improved = false
  for (const member of members) {
    const edge = byId.get(member.id)!
    const source = rects.get(edge.source)
    const target = rects.get(edge.target)
    if (!source || !target) return false
    const blockers: NodeRect[] = []
    for (const [id, rect] of rects) {
      if (id === edge.source || id === edge.target) continue
      if (containerIds?.has(id)) continue
      blockers.push(rect)
    }
    const kept = base.get(member.id)!
    const anchor = spread.get(member.id)!
    const moved = member.end === 'source'
      ? { source: anchor, target: kept.target }
      : { source: kept.source, target: anchor }
    const keptRoute = minimalAnchoredRoute(
      anchorPoint(source, kept.source), anchorPoint(target, kept.target),
      kept.source, kept.target, blockers,
    )
    const movedRoute = minimalAnchoredRoute(
      anchorPoint(source, moved.source), anchorPoint(target, moved.target),
      moved.source, moved.target, blockers,
    )
    if (routeCrossings(keptRoute, blockers) > routeCrossings(movedRoute, blockers)) return false
    const keptBends = routeBendCount(keptRoute)
    const movedBends = routeBendCount(movedRoute)
    if (keptBends > movedBends) return false
    if (keptBends < movedBends) improved = true
  }
  return improved
}

function samePoint(a: Pt, b: Pt): boolean {
  return Math.abs(a.x - b.x) < 0.001 && Math.abs(a.y - b.y) < 0.001
}

export function normalizeOrthogonalPoints(points: Pt[]): Pt[] {
  const finite = points.filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y))
  const deduplicated = finite.filter((point, index) => index === 0 || !samePoint(point, finite[index - 1]))
  const out: Pt[] = []
  for (const point of deduplicated) {
    const previous = out[out.length - 1]
    const beforePrevious = out[out.length - 2]
    if (
      beforePrevious &&
      previous &&
      ((Math.abs(beforePrevious.x - previous.x) < 0.001 && Math.abs(previous.x - point.x) < 0.001 &&
        (previous.y - beforePrevious.y) * (point.y - previous.y) >= 0) ||
        (Math.abs(beforePrevious.y - previous.y) < 0.001 && Math.abs(previous.y - point.y) < 0.001 &&
          (previous.x - beforePrevious.x) * (point.x - previous.x) >= 0))
    ) {
      out[out.length - 1] = point
    } else {
      out.push(point)
    }
  }
  return out
}

function connectPair(from: Pt, to: Pt, horizontalFirst: boolean): Pt[] {
  if (Math.abs(from.x - to.x) < 0.001 || Math.abs(from.y - to.y) < 0.001) return [from, to]
  return horizontalFirst
    ? [from, { x: to.x, y: from.y }, to]
    : [from, { x: from.x, y: to.y }, to]
}

function routeVia(points: Pt[], horizontalFirst: boolean): Pt[] {
  const out: Pt[] = []
  for (let index = 1; index < points.length; index += 1) {
    const pair = connectPair(points[index - 1], points[index], index % 2 ? horizontalFirst : !horizontalFirst)
    if (out.length) pair.shift()
    out.push(...pair)
  }
  return normalizeOrthogonalPoints(out)
}

function routeLength(points: Pt[]): number {
  let length = 0
  for (let index = 1; index < points.length; index += 1) {
    length += Math.abs(points[index].x - points[index - 1].x) + Math.abs(points[index].y - points[index - 1].y)
  }
  return length
}

export function polylineMidpoint(points: Pt[]): Pt {
  if (!points.length) return { x: 0, y: 0 }
  const total = routeLength(points)
  if (total === 0) return points[0]
  let traversed = 0
  for (let index = 1; index < points.length; index += 1) {
    const from = points[index - 1]
    const to = points[index]
    const segment = Math.abs(to.x - from.x) + Math.abs(to.y - from.y)
    if (traversed + segment >= total / 2) {
      const ratio = (total / 2 - traversed) / segment
      return { x: from.x + (to.x - from.x) * ratio, y: from.y + (to.y - from.y) * ratio }
    }
    traversed += segment
  }
  return points[points.length - 1]
}

function followsSide(origin: Pt, outside: Pt, side: RouteSide): boolean {
  if (side === 'top') return Math.abs(origin.x - outside.x) < 0.001 && outside.y <= origin.y
  if (side === 'bottom') return Math.abs(origin.x - outside.x) < 0.001 && outside.y >= origin.y
  if (side === 'left') return Math.abs(origin.y - outside.y) < 0.001 && outside.x <= origin.x
  return Math.abs(origin.y - outside.y) < 0.001 && outside.x >= origin.x
}

function minimalAnchoredRoute(
  sourcePoint: Pt,
  targetPoint: Pt,
  sourceAnchor: RouteAnchor,
  targetAnchor: RouteAnchor,
  blockers: NodeRect[] = [],
): Pt[] {
  const candidates = [
    connectPair(sourcePoint, targetPoint, true),
    connectPair(sourcePoint, targetPoint, false),
  ].map(normalizeOrthogonalPoints).filter((points) =>
    points.length >= 2 && followsSide(sourcePoint, points[1], sourceAnchor.side) &&
    followsSide(targetPoint, points[points.length - 2], targetAnchor.side),
  )
  if (!candidates.length) {
    const sourceStub = outward(sourcePoint, sourceAnchor.side)
    const targetStub = outward(targetPoint, targetAnchor.side)
    candidates.push(
      normalizeOrthogonalPoints([sourcePoint, ...connectPair(sourceStub, targetStub, true), targetPoint]),
      normalizeOrthogonalPoints([sourcePoint, ...connectPair(sourceStub, targetStub, false), targetPoint]),
    )
  }
  // Of the two L-shapes a face pair allows, one often misses what the other hits.
  candidates.sort((left, right) =>
    routeCrossings(left, blockers) - routeCrossings(right, blockers) ||
    routeBendCount(left) - routeBendCount(right) ||
    routeLength(left) - routeLength(right))
  return candidates[0]
}

export function routeOrthogonalEdge(
  source: NodeRect,
  target: NodeRect,
  geometry: RouteGeometry = {},
): { points: Pt[]; mid: Pt; sourceAnchor: RouteAnchor; targetAnchor: RouteAnchor } {
  const automatic = automaticAnchors(source, target)
  const sourceAnchor = geometry.sourceAnchor ?? automatic.source
  const targetAnchor = geometry.targetAnchor ?? automatic.target
  const sourcePoint = anchorPoint(source, sourceAnchor)
  const targetPoint = anchorPoint(target, targetAnchor)
  const sourceStub = outward(sourcePoint, sourceAnchor.side)
  const targetStub = outward(targetPoint, targetAnchor.side)
  const points = geometry.waypoints?.length
    ? routeVia([sourcePoint, sourceStub, ...geometry.waypoints, targetStub, targetPoint], true)
    : minimalAnchoredRoute(sourcePoint, targetPoint, sourceAnchor, targetAnchor)
  return { points, mid: polylineMidpoint(points), sourceAnchor, targetAnchor }
}

export function routeStraightEdge(
  source: NodeRect,
  target: NodeRect,
  geometry: RouteGeometry = {},
): { points: Pt[]; mid: Pt; sourceAnchor: RouteAnchor; targetAnchor: RouteAnchor } {
  const automatic = automaticStraightAnchors(source, target, geometry)
  const sourceAnchor = geometry.sourceAnchor ?? automatic.source
  const targetAnchor = geometry.targetAnchor ?? automatic.target
  const points = [anchorPoint(source, sourceAnchor), anchorPoint(target, targetAnchor)]
  return { points, mid: polylineMidpoint(points), sourceAnchor, targetAnchor }
}

export function routeEdgeByMode(
  source: NodeRect,
  target: NodeRect,
  geometry: RouteGeometry = {},
): { points: Pt[]; mid: Pt; sourceAnchor: RouteAnchor; targetAnchor: RouteAnchor } {
  return geometry.mode === 'straight'
    ? routeStraightEdge(source, target, geometry)
    : routeOrthogonalEdge(source, target, geometry)
}

export function routeBendCount(points: Pt[]): number {
  let bends = 0
  for (let index = 2; index < points.length; index += 1) {
    const first = points[index - 2]
    const middle = points[index - 1]
    const last = points[index]
    if ((Math.abs(first.x - middle.x) < 0.001) !== (Math.abs(middle.x - last.x) < 0.001)) bends += 1
  }
  return bends
}

export function isOrthogonalCorner(points: Pt[], cornerIndex: number): boolean {
  if (cornerIndex <= 0 || cornerIndex >= points.length - 1) return false
  const before = points[cornerIndex - 1]
  const corner = points[cornerIndex]
  const after = points[cornerIndex + 1]
  const firstVertical = Math.abs(before.x - corner.x) < 0.001 && Math.abs(before.y - corner.y) >= 0.001
  const firstHorizontal = Math.abs(before.y - corner.y) < 0.001 && Math.abs(before.x - corner.x) >= 0.001
  const secondVertical = Math.abs(corner.x - after.x) < 0.001 && Math.abs(corner.y - after.y) >= 0.001
  const secondHorizontal = Math.abs(corner.y - after.y) < 0.001 && Math.abs(corner.x - after.x) >= 0.001
  return (firstVertical && secondHorizontal) || (firstHorizontal && secondVertical)
}

function directedSegmentMatches(firstStart: Pt, firstEnd: Pt, secondStart: Pt, secondEnd: Pt): boolean {
  const firstX = Math.sign(firstEnd.x - firstStart.x)
  const firstY = Math.sign(firstEnd.y - firstStart.y)
  const secondX = Math.sign(secondEnd.x - secondStart.x)
  const secondY = Math.sign(secondEnd.y - secondStart.y)
  return firstX === secondX && firstY === secondY
}

function routeReversalCount(points: Pt[]): number {
  let reversals = 0
  for (let index = 2; index < points.length; index += 1) {
    const firstX = Math.sign(points[index - 1].x - points[index - 2].x)
    const firstY = Math.sign(points[index - 1].y - points[index - 2].y)
    const secondX = Math.sign(points[index].x - points[index - 1].x)
    const secondY = Math.sign(points[index].y - points[index - 1].y)
    if (firstX === -secondX && firstY === -secondY) reversals += 1
  }
  return reversals
}

function detourDeletion(points: Pt[], segmentIndex: number): Pt[] | undefined {
  if (
    segmentIndex <= 0 || segmentIndex >= points.length - 2 ||
    !isOrthogonalCorner(points, segmentIndex) || !isOrthogonalCorner(points, segmentIndex + 1)
  ) return undefined
  const before = points[segmentIndex - 1]
  const after = points[segmentIndex + 2]
  const bridges = Math.abs(before.x - after.x) < 0.001 || Math.abs(before.y - after.y) < 0.001
    ? [[]]
    : [[{ x: after.x, y: before.y }], [{ x: before.x, y: after.y }]]
  const reversals = routeReversalCount(points)
  const candidates = bridges.map((bridge) => ({
    corner: bridge[0] ?? before,
    points: normalizeOrthogonalPoints([
      ...points.slice(0, segmentIndex),
      ...bridge,
      ...points.slice(segmentIndex + 2),
    ]),
  })).filter((candidate) =>
    candidate.points.length >= 2 &&
    directedSegmentMatches(points[0], points[1], candidate.points[0], candidate.points[1]) &&
    directedSegmentMatches(
      points[points.length - 2],
      points[points.length - 1],
      candidate.points[candidate.points.length - 2],
      candidate.points[candidate.points.length - 1],
    ) && routeReversalCount(candidate.points) <= reversals,
  )
  candidates.sort((left, right) => {
    const bends = routeBendCount(left.points) - routeBendCount(right.points)
    if (bends) return bends
    const length = routeLength(left.points) - routeLength(right.points)
    if (length) return length
    return left.corner.x - right.corner.x || left.corner.y - right.corner.y
  })
  return candidates[0]?.points
}

export function isDeletableDetourSegment(points: Pt[], segmentIndex: number): boolean {
  return detourDeletion(points, segmentIndex) !== undefined
}

export function deleteOrthogonalDetour(points: Pt[], segmentIndex: number): Pt[] {
  return detourDeletion(points, segmentIndex) ?? points
}

export function deletableDetourSegmentForCorner(points: Pt[], cornerIndex: number): number | undefined {
  if (!isOrthogonalCorner(points, cornerIndex)) return undefined
  return [cornerIndex - 1, cornerIndex]
    .filter((segmentIndex) => isDeletableDetourSegment(points, segmentIndex))
    .sort((left, right) => {
      const leftLength = Math.abs(points[left + 1].x - points[left].x) + Math.abs(points[left + 1].y - points[left].y)
      const rightLength = Math.abs(points[right + 1].x - points[right].x) + Math.abs(points[right + 1].y - points[right].y)
      return leftLength - rightLength || left - right
    })[0]
}

export function moveOrthogonalSegment(
  points: Pt[],
  index: number,
  point: Pt,
  snapDistance = 8,
): Pt[] {
  if (index < 0 || index >= points.length - 1) return points.slice(1, -1)
  const start = points[index]
  const end = points[index + 1]
  const horizontal = Math.abs(start.y - end.y) < 0.001
  const coordinate = horizontal ? point.y : point.x
  const original = horizontal ? start.y : start.x
  if (points.length === 2) {
    if (Math.abs(coordinate - original) <= snapDistance) return []
    const span = horizontal ? Math.abs(end.x - start.x) : Math.abs(end.y - start.y)
    const inset = Math.min(16, span / 3)
    if (horizontal) {
      const direction = Math.sign(end.x - start.x) || 1
      return [
        { x: start.x + direction * inset, y: coordinate },
        { x: end.x - direction * inset, y: coordinate },
      ]
    }
    const direction = Math.sign(end.y - start.y) || 1
    return [
      { x: coordinate, y: start.y + direction * inset },
      { x: coordinate, y: end.y - direction * inset },
    ]
  }
  const next = points.map((item) => ({ ...item }))
  if (index === 0) {
    const span = horizontal ? Math.abs(end.x - start.x) : Math.abs(end.y - start.y)
    const inset = Math.min(16, span / 3)
    const stub = horizontal
      ? { x: start.x + (Math.sign(end.x - start.x) || 1) * inset, y: start.y }
      : { x: start.x, y: start.y + (Math.sign(end.y - start.y) || 1) * inset }
    const movedStub = horizontal ? { x: stub.x, y: coordinate } : { x: coordinate, y: stub.y }
    const movedEnd = horizontal ? { x: end.x, y: coordinate } : { x: coordinate, y: end.y }
    return normalizeOrthogonalPoints([start, stub, movedStub, movedEnd, ...next.slice(2)]).slice(1, -1)
  }
  if (index === points.length - 2) {
    const span = horizontal ? Math.abs(end.x - start.x) : Math.abs(end.y - start.y)
    const inset = Math.min(16, span / 3)
    const stub = horizontal
      ? { x: end.x - (Math.sign(end.x - start.x) || 1) * inset, y: end.y }
      : { x: end.x, y: end.y - (Math.sign(end.y - start.y) || 1) * inset }
    const movedStart = horizontal ? { x: start.x, y: coordinate } : { x: coordinate, y: start.y }
    const movedStub = horizontal ? { x: stub.x, y: coordinate } : { x: coordinate, y: stub.y }
    return normalizeOrthogonalPoints([...next.slice(0, -2), movedStart, movedStub, stub, end]).slice(1, -1)
  }
  if (horizontal) {
    const candidates = [next[index - 1]?.y, next[index + 2]?.y].filter((value): value is number => value !== undefined)
    const snap = candidates.find((value) => Math.abs(value - point.y) <= snapDistance)
    next[index].y = next[index + 1].y = snap ?? point.y
  } else {
    const candidates = [next[index - 1]?.x, next[index + 2]?.x].filter((value): value is number => value !== undefined)
    const snap = candidates.find((value) => Math.abs(value - point.x) <= snapDistance)
    next[index].x = next[index + 1].x = snap ?? point.x
  }
  return normalizeOrthogonalPoints(next).slice(1, -1)
}

export function translateRouteWaypoints(route: RouteGeometry, dx: number, dy: number): RouteGeometry {
  if (!route.waypoints?.length || (Math.abs(dx) < 0.001 && Math.abs(dy) < 0.001)) return route
  return { ...route, waypoints: route.waypoints.map((point) => ({ x: point.x + dx, y: point.y + dy })) }
}

export function reverseRouteGeometry(route: RouteGeometry | undefined): RouteGeometry | undefined {
  if (!route) return undefined
  return {
    ...(route.mode ? { mode: route.mode } : {}),
    ...(route.targetAnchor ? { sourceAnchor: route.targetAnchor } : {}),
    ...(route.sourceAnchor ? { targetAnchor: route.sourceAnchor } : {}),
    ...(route.waypoints?.length ? { waypoints: [...route.waypoints].reverse() } : {}),
    ...(route.labelOffset ? { labelOffset: route.labelOffset } : {}),
  }
}

export function reconnectRouteGeometry(
  route: RouteGeometry | undefined,
  sourceChanged: boolean,
  targetChanged: boolean,
): RouteGeometry | undefined {
  if (!route) return undefined
  const next = { ...route }
  if (sourceChanged) delete next.sourceAnchor
  if (targetChanged) delete next.targetAnchor
  return Object.keys(next).length ? next : undefined
}
