import { BaseEdge, EdgeLabelRenderer, useInternalNode, useReactFlow } from '@xyflow/react'
import { useEffect, useRef } from 'react'
import type { CSSProperties, PointerEvent as ReactPointerEvent } from 'react'
import type { EdgeProps, InternalNode } from '@xyflow/react'
import {
  boundaryAnchor,
  deleteOrthogonalDetour,
  deletableDetourSegmentForCorner,
  endLabelPosition,
  moveOrthogonalSegment,
  pointsToPath,
  routeEdgeByMode,
  segmentDirection,
} from '@/editor/lib/edgeRouting'
import type { NodeRect, Pt, RouteAnchor, RouteGeometry } from '@/editor/lib/edgeRouting'
import type { GraphPilotEdgeData } from '@/types/diagram'
import { getElementSpec, nodePrimitive } from '@/editor/lib/elementCatalog'
import { edgeDisplayLabel, relationshipEndLabel } from '@/editor/lib/edgePresentation'
import { edgeDisplayStroke } from '@/adapters/reactFlow'
import { useEdgeRouteEdit } from '@/editor/lib/edgeRouteEdit'

function num(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

// Absolute rectangle for a node. Size prefers the measured DOM size but falls back
// to the declared width/height (style) so an as-yet-unmeasured node never collapses
// to a zero-size box — which previously made edges attach at the node's corner/centre
// ("in the middle / not at the point").
function rectOf(node: InternalNode): NodeRect {
  const pos = node.internals.positionAbsolute
  const style = node.style as CSSProperties | undefined
  const w = node.measured?.width ?? num(node.width) ?? num(style?.width) ?? 0
  const h = node.measured?.height ?? num(node.height) ?? num(style?.height) ?? 0
  const data = node.data as { label?: string; semanticType?: string } | undefined
  return { x: pos.x, y: pos.y, w, h, primitive: nodePrimitive(data?.semanticType), label: data?.label }
}

function handleAnchor(handleId: string | null | undefined): RouteAnchor | undefined {
  const match = handleId?.match(/^gp-(top|right|bottom|left)-[st]$/)
  return match ? { side: match[1] as RouteAnchor['side'], offset: 0.5 } : undefined
}

// Floating edge: routes between the nodes' resolved perimeter anchors using the
// canonical straight/orthogonal mode, mirroring the server SVG renderer so the
// canvas matches the export. It keeps edges attached at the right point and markers
// aligned with the final segment. Registered as the `default` edge type, so no edge
// needs a runtime `type`, keeping the save round-trip byte-stable.
export function FloatingEdge({
  id,
  source,
  target,
  sourceHandleId,
  targetHandleId,
  markerStart,
  markerEnd,
  style,
  label,
  data,
  selected,
}: EdgeProps) {
  const sourceNode = useInternalNode(source)
  const targetNode = useInternalNode(target)
  const reactFlow = useReactFlow()
  const routeEdit = useEdgeRouteEdit()
  const stopRouteDrag = useRef<(() => void) | null>(null)
  useEffect(() => () => stopRouteDrag.current?.(), [])
  if (!sourceNode || !targetNode) return null

  const sourceRect = rectOf(sourceNode)
  const targetRect = rectOf(targetNode)
  const runtimeData = data as (GraphPilotEdgeData & {
    gpRoute?: RouteGeometry
    gpFanOut?: { sourceAnchor?: RouteAnchor; targetAnchor?: RouteAnchor }
  }) | undefined
  const savedGeometry = runtimeData?.gpRoute ?? {}
  // Derived spacing so parallel edges into one node do not stack. Runtime-only: the
  // reverse adapter reads `gpRoute` alone, so this never reaches the saved diagram.
  const fanOut = runtimeData?.gpFanOut
  const geometry: RouteGeometry = {
    ...savedGeometry,
    sourceAnchor: savedGeometry.sourceAnchor ?? handleAnchor(sourceHandleId) ?? fanOut?.sourceAnchor,
    targetAnchor: savedGeometry.targetAnchor ?? handleAnchor(targetHandleId) ?? fanOut?.targetAnchor,
  }
  const routeMode = geometry.mode ?? 'orthogonal'
  const { points, mid } = routeEdgeByMode(sourceRect, targetRect, geometry)
  const path = pointsToPath(points)

  // Theme the relationship stroke for display (light: #333333, matching the server
  // render's EDGE_DEFAULTS; dark: a lighter slate so edges stay visible on the dark
  // canvas). The generator bakes the default stroke (#333333) into every edge, so that
  // value — and a missing stroke — follows the theme; a genuinely custom stroke is kept
  // as authored. This only rewrites the LOCAL display style (never the edge's state),
  // so the save round-trip keeps the original stroke and stays byte-stable.
  const incoming = (style ?? {}) as CSSProperties
  const authored = typeof incoming.stroke === 'string' ? incoming.stroke : undefined
  const edgeStyle: CSSProperties = { strokeWidth: 2, ...incoming, stroke: edgeDisplayStroke(authored) }
  // Catalog-derived dashes are display-only, so an implicit UML/SysML line style
  // never leaks into otherwise byte-stable saved JSON.
  const edgeData = runtimeData
  const spec = getElementSpec(edgeData?.semanticType)
  if (edgeStyle.strokeDasharray == null && spec?.kind === 'edge' && spec.dashed) edgeStyle.strokeDasharray = '6 4'
  const displayLabel = edgeDisplayLabel(label, edgeData)
  const sourceLabel = relationshipEndLabel(edgeData?.sourceEnd)
  const targetLabel = relationshipEndLabel(edgeData?.targetEnd)
  const itemFlow = (edgeData?.itemFlows ?? []).map((flow) => flow.item).filter(Boolean).join(', ')
  const sourcePoint = points[0]
  const targetPoint = points[points.length - 1]
  // Placed along the outward direction so a role/multiplicity clears its own node rather
  // than landing on the node's label. Same formula as the SVG export.
  const sourceEndLabelAt = endLabelPosition(
    sourcePoint,
    points.length > 1 ? segmentDirection(sourcePoint, points[1]) : { x: 0, y: -1 },
  )
  const targetEndLabelAt = endLabelPosition(
    targetPoint,
    points.length > 1 ? segmentDirection(targetPoint, points[points.length - 2]) : { x: 0, y: -1 },
  )
  const labelPoint = {
    x: mid.x + (geometry.labelOffset?.x ?? 0),
    y: mid.y + (geometry.labelOffset?.y ?? 0),
  }
  const labelStyle: CSSProperties = {
    position: 'absolute',
    zIndex: 1001,
    background: 'var(--surface)',
    color: 'var(--fg)',
    border: '1px solid var(--line)',
    borderRadius: 3,
    padding: '1px 4px',
    fontSize: 11,
    fontFamily: 'system-ui, sans-serif',
    pointerEvents: 'all',
  }
  const controlStyle: CSSProperties = {
    position: 'absolute',
    zIndex: 1002,
    width: 10,
    height: 10,
    borderRadius: '50%',
    border: '1px solid var(--surface)',
    background: 'var(--accent)',
    pointerEvents: 'all',
    transform: 'translate(-50%, -50%)',
    cursor: 'move',
    padding: 0,
  }
  const baseRoute = runtimeData?.gpRoute ?? {}
  const beginRouteDrag = (
    event: ReactPointerEvent<HTMLElement>,
    update: (point: { x: number; y: number }, start: { x: number; y: number }) => RouteGeometry,
  ) => {
    if (!routeEdit) return
    event.preventDefault()
    event.stopPropagation()
    stopRouteDrag.current?.()
    const start = reactFlow.screenToFlowPosition({ x: event.clientX, y: event.clientY })
    let started = false
    const move = (pointer: PointerEvent) => {
      if (!started) {
        routeEdit.start()
        started = true
      }
      const point = reactFlow.screenToFlowPosition({ x: pointer.clientX, y: pointer.clientY })
      routeEdit.setRoute(id, update(point, start))
    }
    const end = () => {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', end)
      if (stopRouteDrag.current === end) stopRouteDrag.current = null
    }
    stopRouteDrag.current = end
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', end, { once: true })
  }
  const applyRouteAction = (nextPoints: Pt[]) => {
    if (!routeEdit || nextPoints === points) return
    const waypoints = nextPoints.slice(1, -1)
    routeEdit.start()
    routeEdit.setRoute(id, { ...baseRoute, waypoints: waypoints.length ? waypoints : undefined })
  }

  return (
    <>
      <BaseEdge id={id} path={path} markerStart={markerStart} markerEnd={markerEnd} style={edgeStyle} />
      <EdgeLabelRenderer>
        {displayLabel ? (
          <div
            className="nodrag nopan"
            onPointerDown={(event) => beginRouteDrag(event, (point, start) => ({
              ...baseRoute,
              labelOffset: {
                x: (baseRoute.labelOffset?.x ?? 0) + point.x - start.x,
                y: (baseRoute.labelOffset?.y ?? 0) + point.y - start.y,
              },
            }))}
            style={{ ...labelStyle, cursor: routeEdit ? 'move' : 'default', transform: `translate(-50%, -50%) translate(${labelPoint.x}px, ${labelPoint.y}px)` }}
          >
            {displayLabel}
          </div>
        ) : null}
        {itemFlow ? (
          <div
            className="nodrag nopan"
            onPointerDown={(event) => beginRouteDrag(event, (point, start) => ({
              ...baseRoute,
              labelOffset: {
                x: (baseRoute.labelOffset?.x ?? 0) + point.x - start.x,
                y: (baseRoute.labelOffset?.y ?? 0) + point.y - start.y,
              },
            }))}
            style={{ ...labelStyle, cursor: routeEdit ? 'move' : 'default', transform: `translate(-50%, 6px) translate(${labelPoint.x}px, ${labelPoint.y}px)`, fontStyle: 'italic' }}
          >
            {itemFlow}
          </div>
        ) : null}
        {sourceLabel ? (
          <div className="nodrag nopan" style={{ ...labelStyle, transform: `translate(-50%, -50%) translate(${sourceEndLabelAt.x}px, ${sourceEndLabelAt.y}px)` }}>
            {sourceLabel}
          </div>
        ) : null}
        {targetLabel ? (
          <div className="nodrag nopan" style={{ ...labelStyle, transform: `translate(-50%, -50%) translate(${targetEndLabelAt.x}px, ${targetEndLabelAt.y}px)` }}>
            {targetLabel}
          </div>
        ) : null}
        {selected && routeEdit ? (
          <>
            <div
              className="nodrag nopan"
              aria-label="Move source anchor"
              onPointerDown={(event) => beginRouteDrag(event, (point) => ({
                ...baseRoute,
                sourceAnchor: boundaryAnchor(sourceRect, point),
              }))}
              style={{ ...controlStyle, left: sourcePoint.x, top: sourcePoint.y }}
            />
            <div
              className="nodrag nopan"
              aria-label="Move target anchor"
              onPointerDown={(event) => beginRouteDrag(event, (point) => ({
                ...baseRoute,
                targetAnchor: boundaryAnchor(targetRect, point),
              }))}
              style={{ ...controlStyle, left: targetPoint.x, top: targetPoint.y }}
            />
            {routeMode === 'orthogonal' ? <>
            {points.slice(0, -1).map((segmentStart, index) => {
              const segmentEnd = points[index + 1]
              const grip = { x: (segmentStart.x + segmentEnd.x) / 2, y: (segmentStart.y + segmentEnd.y) / 2 }
              return (
                <div
                  key={`${segmentStart.x}:${segmentStart.y}-${segmentEnd.x}:${segmentEnd.y}`}
                  className="nodrag nopan"
                  aria-label={`Move route segment ${index + 1}`}
                  title="Drag segment"
                  onPointerDown={(event) => beginRouteDrag(event, (point) => ({
                    ...baseRoute,
                    waypoints: moveOrthogonalSegment(points, index, point),
                  }))}
                  style={{
                    ...controlStyle,
                    left: grip.x,
                    top: grip.y,
                    borderRadius: 2,
                    cursor: Math.abs(segmentStart.y - segmentEnd.y) < 0.001 ? 'ns-resize' : 'ew-resize',
                  }}
                />
              )
            })}
            {points.map((corner, index) => {
              const segmentIndex = deletableDetourSegmentForCorner(points, index)
              if (segmentIndex === undefined) return null
              const deleteDetour = () => applyRouteAction(deleteOrthogonalDetour(points, segmentIndex))
              return (
                <button
                  key={`corner-${corner.x}:${corner.y}`}
                  type="button"
                  className="nodrag nopan"
                  aria-label={`Delete detour at corner ${index}`}
                  title="Delete this detour and its two corners"
                  onClick={(event) => {
                    event.preventDefault()
                    event.stopPropagation()
                    if (event.detail > 1) return
                    deleteDetour()
                  }}
                  onKeyDown={(event) => {
                    if (event.key !== 'Delete' && event.key !== 'Backspace') return
                    event.preventDefault()
                    event.stopPropagation()
                    deleteDetour()
                  }}
                  onPointerDown={(event) => event.stopPropagation()}
                  style={{
                    ...controlStyle,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    left: corner.x,
                    top: corner.y,
                    width: 12,
                    height: 12,
                    borderRadius: 1,
                    borderColor: 'var(--accent)',
                    background: 'var(--surface)',
                    cursor: 'pointer',
                    transform: 'translate(-50%, -50%) rotate(45deg)',
                  }}
                >
                  <span aria-hidden="true" style={{ color: 'var(--accent)', fontSize: 10, lineHeight: 1, transform: 'rotate(-45deg)' }}>×</span>
                </button>
              )
            })}
            </> : null}
          </>
        ) : null}
      </EdgeLabelRenderer>
    </>
  )
}
