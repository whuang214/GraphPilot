import { useEffect, useRef } from 'react'
import { useStore } from '@xyflow/react'

// Canvas overlay that draws the alignment guide lines. Lines are
// given in flow coordinates and projected to screen space with the React Flow
// transform. Rendered as a child of <ReactFlow>; pointer-events are off so it
// never intercepts canvas interaction.
export function HelperLines({ horizontal, vertical }: { horizontal?: number; vertical?: number }) {
  const width = useStore((s) => s.width)
  const height = useStore((s) => s.height)
  const tx = useStore((s) => s.transform[0])
  const ty = useStore((s) => s.transform[1])
  const zoom = useStore((s) => s.transform[2])
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return
    const dpi = window.devicePixelRatio || 1
    canvas.width = width * dpi
    canvas.height = height * dpi
    ctx.setTransform(dpi, 0, 0, dpi, 0, 0)
    ctx.clearRect(0, 0, width, height)
    ctx.strokeStyle = '#2563eb'
    ctx.lineWidth = 1

    if (typeof vertical === 'number') {
      const x = vertical * zoom + tx
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }
    if (typeof horizontal === 'number') {
      const y = horizontal * zoom + ty
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }
  }, [width, height, tx, ty, zoom, horizontal, vertical])

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute top-0 left-0"
      style={{ width, height, zIndex: 4 }}
    />
  )
}
