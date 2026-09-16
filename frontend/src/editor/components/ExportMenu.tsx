import { useEffect, useRef, useState } from 'react'
import { Button } from '@/ui'

interface ExportMenuProps {
  onExportPng: () => void
  onExportSvg: () => void
  disabled?: boolean
}

// Small inline export menu: the Export button toggles a
// popover offering PNG or SVG, both produced from the server-side render
// (`POST /api/diagrams/render`). Closes on outside-click or Escape.
export function ExportMenu({ onExportPng, onExportSvg, disabled }: ExportMenuProps) {
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
        variant="secondary"
        size="sm"
        onClick={() => setOpen((v) => !v)}
        disabled={disabled}
        aria-haspopup="menu"
        aria-expanded={open}
        title="Export the diagram as an image (server render)"
      >
        Export
      </Button>
      {open ? (
        <div
          role="menu"
          className="absolute right-0 z-50 mt-1 w-32 overflow-hidden rounded-md border border-line bg-surface py-1 shadow-lg"
        >
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-1.5 text-left text-xs text-fg hover:bg-surface-2"
            onClick={() => choose(onExportPng)}
          >
            PNG image
          </button>
          <button
            type="button"
            role="menuitem"
            className="block w-full px-3 py-1.5 text-left text-xs text-fg hover:bg-surface-2"
            onClick={() => choose(onExportSvg)}
          >
            SVG vector
          </button>
        </div>
      ) : null}
    </div>
  )
}
