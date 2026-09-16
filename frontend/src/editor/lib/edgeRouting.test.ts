/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import {
  anchorPoint,
  attachmentProfile,
  boundaryAnchor,
  boundaryLocation,
  deleteOrthogonalDetour,
  deletableDetourSegmentForCorner,
  fanOutAnchors,
  isDeletableDetourSegment,
  moveOrthogonalSegment,
  normalizeOrthogonalPoints,
  normalizeRouteGeometry,
  pointsToPath,
  routeEdgeByMode,
  reconnectRouteGeometry,
  resolveAttachmentAnchor,
  reverseRouteGeometry,
  routeOrthogonalEdge,
  routeStraightEdge,
  setRouteMode,
  translateRouteWaypoints,
} from './edgeRouting'
import { isContainerSemantic } from './elementCatalog'
import type { NodeRect, Pt, RouteAnchor, RouteGeometry } from './edgeRouting'

const fixturePath = fileURLToPath(new URL('../../../../backend/tests/edge_routing_fixtures.json', import.meta.url))
const fixtures = JSON.parse(readFileSync(fixturePath, 'utf8')) as {
  orthogonalCases: Array<{
    name: string
    source: NodeRect
    target: NodeRect
    geometry: RouteGeometry
    expected: { points: Pt[]; mid: Pt; sourceAnchor: RouteAnchor; targetAnchor: RouteAnchor }
  }>
  straightCases: Array<{
    name: string
    source: NodeRect
    target: NodeRect
    geometry: RouteGeometry
    expected: { points: Pt[]; mid: Pt; sourceAnchor: RouteAnchor; targetAnchor: RouteAnchor }
  }>
  fanOutCases: Array<{
    name: string
    nodes: Array<{ id: string; position: { x: number; y: number }; width: number; height: number; data: { label: string; semanticType: string } }>
    edges: Array<{ id: string; source: string; target: string; route?: RouteGeometry }>
    expected: Record<string, { sourceAnchor?: RouteAnchor; targetAnchor?: RouteAnchor }>
  }>
}

describe('shared route fixtures', () => {
  for (const fixture of fixtures.orthogonalCases) {
    it(fixture.name, () => {
      expect(routeOrthogonalEdge(fixture.source, fixture.target, fixture.geometry)).toEqual(fixture.expected)
      expect(routeEdgeByMode(fixture.source, fixture.target, fixture.geometry)).toEqual(fixture.expected)
    })
  }
  for (const fixture of fixtures.straightCases) {
    it(fixture.name, () => {
      expect(routeStraightEdge(fixture.source, fixture.target, fixture.geometry)).toEqual(fixture.expected)
      expect(routeEdgeByMode(fixture.source, fixture.target, fixture.geometry)).toEqual(fixture.expected)
    })
  }
})

// Canvas/SVG parity for endpoint spreading. The same fixture is asserted by
// backend/tests/diagrams/rendering/test_edge_fan_out.py, so the two renderers cannot
// drift: an edge that fans out in the export must fan out identically on the canvas.
describe('fan-out parity with the SVG renderer', () => {
  for (const fixture of fixtures.fanOutCases) {
    it(fixture.name, () => {
      const rects = new Map(fixture.nodes.map((node) => [node.id, {
        x: node.position.x,
        y: node.position.y,
        w: node.width,
        h: node.height,
        primitive: node.data.semanticType,
        label: node.data.label,
      }]))
      // EditorPage passes these for real; the fixture has to as well, or the container
      // rule is only enforced on the SVG side and the two silently disagree.
      const containerIds = new Set(
        fixture.nodes
          .filter((node) => isContainerSemantic(node.data.semanticType))
          .map((node) => node.id),
      )
      const actual = fanOutAnchors(
        fixture.edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          geometry: edge.route,
        })),
        rects,
        containerIds,
      )
      // The backend keys by edge index; compare on the same basis.
      const byIndex = Object.fromEntries(
        fixture.edges
          .map((edge, index) => [String(index), actual.get(edge.id)] as const)
          .filter(([, value]) => value !== undefined),
      )
      expect(byIndex).toEqual(fixture.expected)
    })
  }
})

describe('anchored routing', () => {
  it('builds an M/L path string from the points', () => {
    expect(pointsToPath([{ x: 1, y: 2 }, { x: 3, y: 4 }])).toBe('M 1 2 L 3 4')
  })

  it('places sliding anchors at normalized offsets along unchanged box and bar sides', () => {
    expect(anchorPoint({ x: 10, y: 20, w: 200, h: 100 }, { side: 'right', offset: 0.25 })).toEqual({ x: 210, y: 45 })
    expect(anchorPoint({ x: 10, y: 20, w: 200, h: 100 }, { side: 'top', offset: 0.75 })).toEqual({ x: 160, y: 20 })
    expect(anchorPoint({ x: 10, y: 20, w: 120, h: 30, primitive: 'bar' }, { side: 'bottom', offset: 0.4 })).toEqual({ x: 58, y: 50 })
  })

  it('projects encoded anchors onto visible primitive profiles', () => {
    const initialRect = { x: 0, y: 0, w: 90, h: 60, primitive: 'initial', label: 'Initial' }
    expect(attachmentProfile(initialRect)).toEqual({ shape: 'ellipse', bounds: { x: 30, y: 7.8, w: 30, h: 30 } })
    const initialPoint = anchorPoint(initialRect, { side: 'top', offset: 0.5 })
    expect(initialPoint.x).toBeCloseTo(45, 8)
    expect(initialPoint.y).toBeCloseTo(7.8, 8)

    const actorRect = { x: 0, y: 0, w: 90, h: 120, primitive: 'actor', label: 'Actor' }
    expect(attachmentProfile(actorRect)).toEqual({ shape: 'ellipse', bounds: { x: 33, y: 30.8, w: 24, h: 42 } })
    const actorLocation = boundaryLocation(actorRect, { x: 57, y: 51.8 })
    expect(actorLocation.anchor).toEqual({ side: 'right', offset: 51.8 / 120 })
    expect(actorLocation.point.x).toBeCloseTo(57, 8)
    expect(actorLocation.point.y).toBeCloseTo(51.8, 8)
    expect(actorLocation.distance).toBeCloseTo(0, 8)

    const ellipse = anchorPoint({ x: 0, y: 0, w: 100, h: 100, primitive: 'ellipse' }, { side: 'top', offset: 0.75 })
    expect(ellipse.x).toBeCloseTo(72.36, 2)
    expect(ellipse.y).toBeCloseTo(5.28, 2)
    const diamond = anchorPoint({ x: 0, y: 0, w: 100, h: 100, primitive: 'diamond' }, { side: 'top', offset: 0.75 })
    expect(diamond.x).toBeCloseTo(66.67, 2)
    expect(diamond.y).toBeCloseTo(16.67, 2)
    const wideDiamond = { x: 0, y: 0, w: 240, h: 100, primitive: 'diamond' }
    const widePoint = anchorPoint(wideDiamond, { side: 'top', offset: 0.75 })
    expect(widePoint.x).toBeCloseTo(160, 2)
    expect(widePoint.y).toBeCloseTo(16.67, 2)
    const wideLocation = boundaryLocation(wideDiamond, { x: 180, y: 25 })
    expect(wideLocation.point).toEqual({ x: 180, y: 25 })
    expect(wideLocation.distance).toBe(0)
    const tallLocation = boundaryLocation({ x: 0, y: 0, w: 100, h: 240, primitive: 'diamond' }, { x: 75, y: 60 })
    expect(tallLocation.point).toEqual({ x: 75, y: 60 })
    expect(tallLocation.distance).toBe(0)
  })

  it('encodes any ellipse-boundary direction as a stable side and offset', () => {
    const rect = { x: 0, y: 0, w: 100, h: 100, primitive: 'ellipse' }
    const anchor = boundaryAnchor(rect, { x: 85, y: 15 })
    expect(anchor).toEqual({ side: 'right', offset: 0 })
    const location = boundaryLocation(rect, { x: 85, y: 15 })
    expect(location.point.x).toBeCloseTo(85.36, 2)
    expect(location.point.y).toBeCloseTo(14.64, 2)
    expect(location.distance).toBeLessThan(1)
  })

  it('soft-snaps projected pointers to visual cardinal centers in screen space', () => {
    const ellipse = { x: 0, y: 0, w: 200, h: 100, primitive: 'ellipse' }
    const snapped = resolveAttachmentAnchor(ellipse, { x: 106, y: 0 }, 1)
    expect(snapped.snapped).toBe('top')
    expect(snapped.anchor).toEqual({ side: 'top', offset: 0.5 })
    expect(snapped.point).toEqual({ x: 100, y: 0 })

    const custom = resolveAttachmentAnchor(ellipse, { x: 112, y: 0 }, 1)
    expect(custom.snapped).toBeUndefined()
    expect(custom.anchor.side).toBe('top')
    expect(custom.anchor.offset).toBeCloseTo(0.56, 2)
    expect(custom.point.x).toBeGreaterThan(110)
  })

  it('scales cardinal aim-lock with zoom and encodes shifted profiles exactly', () => {
    const ellipse = { x: 0, y: 0, w: 200, h: 100, primitive: 'ellipse' }
    expect(resolveAttachmentAnchor(ellipse, { x: 104, y: 0 }, 2).snapped).toBe('top')
    expect(resolveAttachmentAnchor(ellipse, { x: 105, y: 0 }, 2).snapped).toBeUndefined()

    const control = { x: 0, y: 0, w: 90, h: 60, primitive: 'initial', label: 'Initial' }
    const left = resolveAttachmentAnchor(control, { x: 30, y: 22.8 }, 1)
    expect(left.snapped).toBe('left')
    expect(left.anchor.side).toBe('left')
    expect(left.anchor.offset).toBeCloseTo(0.38, 6)
    expect(left.point.x).toBeCloseTo(30, 6)
    expect(left.point.y).toBeCloseTo(22.8, 6)
  })

  it('collapses duplicate and collinear manual bends', () => {
    expect(normalizeOrthogonalPoints([
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 10 },
    ])).toEqual([{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 10 }])
  })

  it('preserves a collinear reversal needed to honor an explicit terminal side', () => {
    expect(normalizeOrthogonalPoints([
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 10, y: 0 },
    ])).toEqual([{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 10, y: 0 }])
  })

  it('moves an interior segment on one axis and snaps away redundant bends', () => {
    const points = [
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 40 },
      { x: 80, y: 40 },
      { x: 80, y: 0 },
      { x: 100, y: 0 },
    ]
    expect(moveOrthogonalSegment(points, 2, { x: 50, y: 3 })).toEqual([])
  })

  it('maps both bordering corner controls to the same safe detour', () => {
    const points = [
      { x: 100, y: 110 },
      { x: 160, y: 110 },
      { x: 160, y: 40 },
      { x: 320, y: 40 },
      { x: 320, y: 210 },
      { x: 400, y: 210 },
    ]
    expect(deletableDetourSegmentForCorner(points, 1)).toBeUndefined()
    expect(deletableDetourSegmentForCorner(points, 2)).toBe(2)
    expect(deletableDetourSegmentForCorner(points, 3)).toBe(2)
    expect(deletableDetourSegmentForCorner(points, 4)).toBeUndefined()
    expect(deleteOrthogonalDetour(points, 2)).toEqual([
      { x: 100, y: 110 },
      { x: 160, y: 110 },
      { x: 160, y: 210 },
      { x: 400, y: 210 },
    ])
  })

  it('deletes only interior detour segments and normalizes the result', () => {
    const alignedDetour = [
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 40 },
      { x: 80, y: 40 },
      { x: 80, y: 0 },
      { x: 100, y: 0 },
    ]
    expect(isDeletableDetourSegment(alignedDetour, 2)).toBe(true)
    expect(isDeletableDetourSegment(alignedDetour, 0)).toBe(false)
    expect(isDeletableDetourSegment(alignedDetour, alignedDetour.length - 2)).toBe(false)
    expect(deleteOrthogonalDetour(alignedDetour, 2)).toEqual([{ x: 0, y: 0 }, { x: 100, y: 0 }])
    expect(deleteOrthogonalDetour(alignedDetour, 0)).toBe(alignedDetour)

    const nonAligned = [
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 40 },
      { x: 80, y: 40 },
      { x: 80, y: 100 },
      { x: 100, y: 100 },
    ]
    expect(deleteOrthogonalDetour(nonAligned, 2)).toEqual([
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 100 },
      { x: 100, y: 100 },
    ])
  })

  it('rejects detour deletion when every candidate changes a terminal direction', () => {
    const points = [{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 40 }, { x: 80, y: 40 }]
    expect(isDeletableDetourSegment(points, 1)).toBe(false)
    expect(deleteOrthogonalDetour(points, 1)).toBe(points)
  })

  it('rejects a terminal-safe detour deletion that introduces a reversal', () => {
    const points = [
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 40 },
      { x: 80, y: 40 },
      { x: 80, y: 0 },
      { x: 100, y: 0 },
    ]
    expect(isDeletableDetourSegment(points, 1)).toBe(false)
    expect(isDeletableDetourSegment(points, 3)).toBe(false)
    expect(deleteOrthogonalDetour(points, 1)).toBe(points)
  })

  it('moves a direct segment into a manual detour and snaps it back', () => {
    const points = [{ x: 0, y: 0 }, { x: 100, y: 0 }]
    expect(moveOrthogonalSegment(points, 0, { x: 50, y: 20 })).toEqual([
      { x: 16, y: 20 },
      { x: 84, y: 20 },
    ])
    expect(moveOrthogonalSegment(points, 0, { x: 50, y: 3 })).toEqual([])
  })

  it('moves endpoint-adjacent segments without backtracking', () => {
    const points = [{ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 100, y: 100 }]
    expect(moveOrthogonalSegment(points, 0, { x: 50, y: 20 })).toEqual([
      { x: 16, y: 0 },
      { x: 16, y: 20 },
      { x: 100, y: 20 },
    ])
    expect(moveOrthogonalSegment(points, 1, { x: 80, y: 50 })).toEqual([
      { x: 80, y: 0 },
      { x: 80, y: 84 },
      { x: 100, y: 84 },
    ])
  })


  it('normalizes route modes and clears orthogonal waypoints when switching to straight', () => {
    expect(normalizeRouteGeometry({ mode: 'straight', labelOffset: { x: 2, y: 3 } })).toEqual({
      mode: 'straight',
      labelOffset: { x: 2, y: 3 },
    })
    expect(normalizeRouteGeometry({ mode: 'curved' })).toBeUndefined()
    expect(setRouteMode({
      sourceAnchor: { side: 'right', offset: 0.5 },
      waypoints: [{ x: 50, y: 60 }],
      labelOffset: { x: 4, y: -8 },
    }, 'straight')).toEqual({
      mode: 'straight',
      sourceAnchor: { side: 'right', offset: 0.5 },
      labelOffset: { x: 4, y: -8 },
    })
  })

  it('translates manual waypoints when both endpoints move together', () => {
    expect(translateRouteWaypoints({
      mode: 'orthogonal',
      sourceAnchor: { side: 'right', offset: 0.5 },
      waypoints: [{ x: 20, y: 30 }],
      labelOffset: { x: 4, y: -8 },
    }, 10, -5)).toEqual({
      mode: 'orthogonal',
      sourceAnchor: { side: 'right', offset: 0.5 },
      waypoints: [{ x: 30, y: 25 }],
      labelOffset: { x: 4, y: -8 },
    })
  })

  it('reverses authored route direction when endpoints swap', () => {
    expect(reverseRouteGeometry({
      mode: 'orthogonal',
      sourceAnchor: { side: 'right', offset: 0.25 },
      targetAnchor: { side: 'left', offset: 0.75 },
      waypoints: [{ x: 40, y: 20 }, { x: 80, y: 20 }],
      labelOffset: { x: 4, y: -8 },
    })).toEqual({
      mode: 'orthogonal',
      sourceAnchor: { side: 'left', offset: 0.75 },
      targetAnchor: { side: 'right', offset: 0.25 },
      waypoints: [{ x: 80, y: 20 }, { x: 40, y: 20 }],
      labelOffset: { x: 4, y: -8 },
    })
  })

  it('clears only reconnected endpoint anchors while preserving manual bends', () => {
    expect(reconnectRouteGeometry({
      mode: 'orthogonal',
      sourceAnchor: { side: 'right', offset: 0.25 },
      targetAnchor: { side: 'left', offset: 0.75 },
      waypoints: [{ x: 50, y: 60 }],
    }, true, false)).toEqual({
      mode: 'orthogonal',
      targetAnchor: { side: 'left', offset: 0.75 },
      waypoints: [{ x: 50, y: 60 }],
    })
  })

  it('honors explicit anchors and manual waypoints', () => {
    const route = routeOrthogonalEdge(
      { x: 0, y: 0, w: 100, h: 60 },
      { x: 300, y: 200, w: 100, h: 60 },
      {
        sourceAnchor: { side: 'right', offset: 0.25 },
        targetAnchor: { side: 'top', offset: 0.75 },
        waypoints: [{ x: 180, y: 40 }],
      },
    )
    expect(route.points[0]).toEqual({ x: 100, y: 15 })
    expect(route.points[route.points.length - 1]).toEqual({ x: 375, y: 200 })
    expect(route.points.some((point) => point.y === 40 && point.x >= 180)).toBe(true)
  })
})
