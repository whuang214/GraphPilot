import { useEffect, useRef, useState } from 'react'
import { Button } from '@/ui'

interface PreviewMenuProps {
  onRender: () => void
  onJson: () => void
  disabled?: boolean
}

// Preview dropdown, modelled on ExportMenu: the Preview
// button toggles a popover offering the backend SVG render or the canonical
// JSON (with a git-style diff). Closes on outside-click or Escape.
export function PreviewMenu({ onRender, onJson, disabled }: PreviewMenuProps) {
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
        disabled={disabled}
        aria-haspopup="menu"
        aria-expanded={open}
        title="Preview the diagram (server SVG render or canonical JSON)"
      >
        Preview
      </Button>
      {open ? (
        <div
          role="menu"
          className="absolute right-0 z-50 mt-1 w-40 overflow-hidden rounded-md border border-line bg-surface py-1 shadow-lg"
        >
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-1.5 text-left text-xs text-fg hover:bg-surface-2"
            onClick={() => choose(onRender)}
          >
            Render (SVG)
          </button>
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-1.5 text-left text-xs text-fg hover:bg-surface-2"
            onClick={() => choose(onJson)}
          >
            JSON
          </button>
        </div>
      ) : null}
    </div>
  )
}
