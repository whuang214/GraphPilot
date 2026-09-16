import type { Node, NodePositionChange } from '@xyflow/react'
import { absolutePosition } from './containment'

// Alignment / distance guides while dragging. Given the live
// position change for the dragged node, find the nearest edge/center alignment
// with any other node (within `distance`), returning the guide-line coordinates
// to draw and a snapped position. Adapted from React Flow's helper-lines example.
export interface HelperLinesResult {
  horizontal?: number
  vertical?: number
  snapPosition: { x?: number; y?: number }
}

function toNum(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function sizeW(node: Node): number {
  return node.measured?.width ?? toNum(node.width) ?? toNum(node.style?.width) ?? 0
}

function sizeH(node: Node): number {
  return node.measured?.height ?? toNum(node.height) ?? toNum(node.style?.height) ?? 0
}

function isDescendant(node: Node, ancestorId: string, byId: Map<string, Node>): boolean {
  let parentId = node.parentId
  const seen = new Set<string>()
  while (parentId && !seen.has(parentId)) {
    if (parentId === ancestorId) return true
    seen.add(parentId)
    parentId = byId.get(parentId)?.parentId
  }
  return false
}

export function getHelperLines(
  change: NodePositionChange,
  nodes: Node[],
  distance = 5,
): HelperLinesResult {
  const result: HelperLinesResult = { snapPosition: {} }
  const nodeA = nodes.find((n) => n.id === change.id)
  if (!nodeA || !change.position) return result

  const byId = new Map(nodes.map((node) => [node.id, node]))
  const parent = nodeA.parentId ? byId.get(nodeA.parentId) : undefined
  const parentOffset = parent ? absolutePosition(parent, byId) : { x: 0, y: 0 }
  const aW = sizeW(nodeA)
  const aH = sizeH(nodeA)
  const absoluteChange = {
    x: change.position.x + parentOffset.x,
    y: change.position.y + parentOffset.y,
  }
  const a = {
    left: absoluteChange.x,
    right: absoluteChange.x + aW,
    top: absoluteChange.y,
    bottom: absoluteChange.y + aH,
    centerX: absoluteChange.x + aW / 2,
    centerY: absoluteChange.y + aH / 2,
  }

  let vDist = distance
  let hDist = distance

  for (const nodeB of nodes) {
    if (nodeB.id === nodeA.id || isDescendant(nodeB, nodeA.id, byId)) continue
    const bW = sizeW(nodeB)
    const bH = sizeH(nodeB)
    const bPosition = absolutePosition(nodeB, byId)
    const b = {
      left: bPosition.x,
      right: bPosition.x + bW,
      top: bPosition.y,
      bottom: bPosition.y + bH,
      centerX: bPosition.x + bW / 2,
      centerY: bPosition.y + bH / 2,
    }

    // Vertical guides (align on x): left-left, right-right, center-center,
    // left-right, right-left. `snapX` is the dragged node's new x.
    const vChecks = [
      { d: Math.abs(a.left - b.left), line: b.left, snapX: b.left },
      { d: Math.abs(a.right - b.right), line: b.right, snapX: b.right - aW },
      { d: Math.abs(a.centerX - b.centerX), line: b.centerX, snapX: b.centerX - aW / 2 },
      { d: Math.abs(a.left - b.right), line: b.right, snapX: b.right },
      { d: Math.abs(a.right - b.left), line: b.left, snapX: b.left - aW },
    ]
    for (const c of vChecks) {
      if (c.d < vDist) {
        vDist = c.d
        result.vertical = c.line
        result.snapPosition.x = c.snapX - parentOffset.x
      }
    }

    // Horizontal guides (align on y): top-top, bottom-bottom, center-center,
    // top-bottom, bottom-top.
    const hChecks = [
      { d: Math.abs(a.top - b.top), line: b.top, snapY: b.top },
      { d: Math.abs(a.bottom - b.bottom), line: b.bottom, snapY: b.bottom - aH },
      { d: Math.abs(a.centerY - b.centerY), line: b.centerY, snapY: b.centerY - aH / 2 },
      { d: Math.abs(a.top - b.bottom), line: b.bottom, snapY: b.bottom },
      { d: Math.abs(a.bottom - b.top), line: b.top, snapY: b.top - aH },
    ]
    for (const c of hChecks) {
      if (c.d < hDist) {
        hDist = c.d
        result.horizontal = c.line
        result.snapPosition.y = c.snapY - parentOffset.y
      }
    }
  }

  return result
}
