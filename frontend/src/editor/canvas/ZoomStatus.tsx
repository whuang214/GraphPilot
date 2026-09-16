import { useStore } from '@xyflow/react'

// Live zoom percentage read from the React Flow store transform ([x, y, zoom]).
// Rendered in the StatusBar; must be used inside a ReactFlowProvider.
export function ZoomStatus() {
  const zoom = useStore((s) => s.transform[2])
  return <span title="Zoom level">{Math.round(zoom * 100)}%</span>
}
