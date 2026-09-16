import type { Node } from '@xyflow/react'
import { nodePrimitive } from '@/editor/lib/elementCatalog'
import type { NodePrimitive } from '@/editor/lib/elementCatalog'

// MiniMap tint follows the finite render primitive set. Every catalog semantic
// therefore receives a stable colour without maintaining a second semantic map.
const COLORS: Record<NodePrimitive, string> = {
  note: '#eab308',
  'rounded-rect': '#2563eb',
  initial: '#16a34a',
  final: '#dc2626',
  'flow-final': '#e11d48',
  diamond: '#d97706',
  bar: '#475569',
  actor: '#7c3aed',
  ellipse: '#2563eb',
  container: '#64748b',
  'classifier-box': '#0891b2',
  object: '#0f766e',
  datastore: '#0d9488',
  pin: '#ea580c',
  partition: '#64748b',
  region: '#64748b',
  'send-signal': '#c026d3',
  'accept-event': '#9333ea',
  port: '#0891b2',
}

export function miniMapNodeColor(node: Node): string {
  const semanticType = (node.data as { semanticType?: string } | undefined)?.semanticType
  const primitive = semanticType ? nodePrimitive(semanticType) : undefined
  return primitive ? COLORS[primitive] : '#94a3b8'
}
