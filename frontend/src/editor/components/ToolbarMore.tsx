import { useEffect, useRef, useState } from 'react'
import { Button } from '@/ui'

export interface ToolbarMoreItem {
  label: string
  onClick: () => void
  disabled?: boolean
}

// Overflow "⋯ More" menu for the floating toolbar: keeps the
// bar to one row by tucking the less-used / shortcut-backed / redundant actions
// behind a dropdown. Modelled on ExportMenu / PreviewMenu; closes on outside-click
// or Escape.
export function ToolbarMore({ items }: { items: ToolbarMoreItem[] }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    function onPointer(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('mousedown', onPointer)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('mousedown', onPointer)
      window.removeEventListener('keydown', onKey)
    }
  }, [open])

  function choose(action: () => void) {
    setOpen(false)
    action()
  }

  return (
    <div ref={ref} className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="More actions"
        title="More actions"
      >
        {'\u22ef'}
      </Button>
      {open ? (
        <div
          role="menu"
          className="absolute right-0 z-50 mt-1 w-44 overflow-hidden rounded-md border border-line bg-surface py-1 shadow-lg"
        >
          {items.map((item) => (
            <button
              key={item.label}
              type="button"
              role="menuitem"
              disabled={item.disabled}
              className="block w-full px-3 py-1.5 text-left text-xs text-fg hover:bg-surface-2 disabled:opacity-50"
              onClick={() => choose(item.onClick)}
            >
              {item.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
