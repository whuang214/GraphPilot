import { useCallback, useEffect, useRef } from 'react'
import type { KeyboardEvent as ReactKeyboardEvent, PointerEvent as ReactPointerEvent, ReactNode } from 'react'
import { cn } from '../../ui'

interface RailProps {
  side: 'left' | 'right'
  title: string
  width: number
  collapsed: boolean
  onWidthChange: (width: number) => void
  onToggle: () => void
  min?: number
  max?: number
  children: ReactNode
}

// Collapsible + drag-resizable side rail. Owns the container chrome (width,
// border, header, scroll) so its content (NodePalette / PropertyPanel) stays
// layout-agnostic.
export function Rail({
  side,
  title,
  width,
  collapsed,
  onWidthChange,
  onToggle,
  min = 140,
  max = 480,
  children,
}: RailProps) {
  const startRef = useRef<{ x: number; w: number } | null>(null)
  const safeWidth = Math.min(max, Math.max(min, Number.isFinite(width) ? width : min))

  const onPointerMove = useCallback(
    (e: PointerEvent) => {
      const start = startRef.current
      if (!start) return
      const dx = e.clientX - start.x
      const raw = side === 'left' ? start.w + dx : start.w - dx
      onWidthChange(Math.min(max, Math.max(min, raw)))
    },
    [side, min, max, onWidthChange],
  )

  const onPointerUp = useCallback(() => {
    startRef.current = null
    window.removeEventListener('pointermove', onPointerMove)
    window.removeEventListener('pointerup', onPointerUp)
    window.removeEventListener('pointercancel', onPointerUp)
  }, [onPointerMove])

  const onResizeStart = useCallback(
    (e: ReactPointerEvent) => {
      e.preventDefault()
      startRef.current = { x: e.clientX, w: safeWidth }
      window.addEventListener('pointermove', onPointerMove)
      window.addEventListener('pointerup', onPointerUp)
      window.addEventListener('pointercancel', onPointerUp)
    },
    [safeWidth, onPointerMove, onPointerUp],
  )

  useEffect(() => () => onPointerUp(), [onPointerUp])

  // Keyboard resize for the focusable splitter: arrow keys nudge the width by a
  // step (direction depends on which side the rail sits), so resizing isn't
  // pointer-only.
  const onResizeKey = useCallback(
    (e: ReactKeyboardEvent) => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return
      e.preventDefault()
      const dir = e.key === 'ArrowRight' ? 1 : -1
      const delta = (side === 'left' ? dir : -dir) * 16
      onWidthChange(Math.min(max, Math.max(min, safeWidth + delta)))
    },
    [side, safeWidth, min, max, onWidthChange],
  )

  const border = side === 'left' ? 'border-r' : 'border-l'

  if (collapsed) {
    return (
      <div className={cn('flex w-9 shrink-0 flex-col items-center bg-surface py-2', border, 'border-line')}>
        <button
          type="button"
          onClick={onToggle}
          title={`Expand ${title}`}
          aria-label={`Expand ${title}`}
          className="rounded p-1 text-fg-muted hover:bg-surface-2"
        >
          {side === 'left' ? '»' : '«'}
        </button>
      </div>
    )
  }

  return (
    <aside className={cn('relative flex shrink-0 flex-col bg-surface', border, 'border-line')} style={{ width: safeWidth }}>
      <div className="flex items-center justify-between border-b border-line px-3 py-1.5">
        <span className="text-xs font-semibold tracking-wide text-fg-subtle uppercase">{title}</span>
        <button
          type="button"
          onClick={onToggle}
          title={`Collapse ${title}`}
          aria-label={`Collapse ${title}`}
          className="rounded p-1 text-fg-muted hover:bg-surface-2"
        >
          {side === 'left' ? '«' : '»'}
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
      <div
        onPointerDown={onResizeStart}
        onKeyDown={onResizeKey}
        role="separator"
        aria-orientation="vertical"
        aria-label={`Resize ${title} panel`}
        aria-valuenow={safeWidth}
        aria-valuemin={min}
        aria-valuemax={max}
        tabIndex={0}
        className={cn(
          'absolute inset-y-0 w-1 cursor-col-resize hover:bg-accent/30 focus-visible:bg-accent/50 focus-visible:outline-none',
          side === 'left' ? 'right-0' : 'left-0',
        )}
      />
    </aside>
  )
}
