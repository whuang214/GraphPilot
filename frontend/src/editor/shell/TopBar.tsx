import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { Badge, Button } from '../../ui'

interface TopBarProps {
  name: string
  // When provided, the name is editable in place.
  onNameChange?: (name: string) => void
  diagramType: string
  dirty: boolean
  sourceInfo: {
    location: string
    state: string
    revision?: string
    copyPath?: string
  }
  actions: ReactNode
}

// Editor top app bar: diagram identity + provenance + dirty state on the left, the
// action slot (Open file, Browse, theme toggle, Save, …) on the right.
export function TopBar({ name, onNameChange, diagramType, dirty, sourceInfo, actions }: TopBarProps) {
  const [infoOpen, setInfoOpen] = useState(false)
  const infoRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!infoOpen) return
    const onPointer = (event: MouseEvent) => {
      if (!infoRef.current?.contains(event.target as Node)) setInfoOpen(false)
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      setInfoOpen(false)
      infoRef.current?.querySelector<HTMLButtonElement>('[aria-label="Diagram information"]')?.focus()
    }
    window.addEventListener('mousedown', onPointer)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('mousedown', onPointer)
      window.removeEventListener('keydown', onKey)
    }
  }, [infoOpen])
  const copyPath = async () => {
    if (!sourceInfo.copyPath) return
    try {
      await navigator.clipboard.writeText(sourceInfo.copyPath)
    } catch {}
  }
  return (
    // Single, non-wrapping row (identity left, actions right via justify-between).
    // The bar never wraps to a second row: the identity group shrinks (the name
    // truncates) while the shrink-0 actions stay put, so flipping the "unsaved"
    // indicator can't bump the actions onto a new row. The
    // actions collapse into a "⋯" menu as the window narrows (in EditorPage).
    <header className="flex items-center justify-between gap-x-3 border-b border-line bg-surface px-4 py-2 text-sm">
      <div className="flex min-w-0 items-center gap-x-3">
        {onNameChange ? (
          <input
            value={name}
            onChange={(e) => onNameChange(e.target.value)}
            aria-label="Diagram name"
            title="Rename the diagram"
            className="min-w-0 max-w-[18rem] rounded border border-transparent bg-transparent px-1 py-0.5 font-semibold text-fg hover:border-line focus:border-accent focus:bg-surface focus:outline-none"
          />
        ) : (
          <strong className="truncate text-fg">{name}</strong>
        )}
        <Badge>{diagramType}</Badge>
        <div ref={infoRef} className="relative">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 rounded-full p-0"
            aria-label="Diagram information"
            aria-expanded={infoOpen}
            onClick={() => setInfoOpen((value) => !value)}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
              <circle cx="8" cy="8" r="6.25" />
              <circle cx="8" cy="4.75" r="0.75" fill="currentColor" stroke="none" />
              <path d="M8 7.25v4" />
            </svg>
          </Button>
          {infoOpen ? (
            <div className="absolute top-full left-0 z-50 mt-2 w-80 rounded-md border border-line bg-surface p-3 shadow-lg" role="dialog" aria-label="Diagram information">
              <dl className="space-y-2 text-xs">
                <div><dt className="font-medium text-fg">Location</dt><dd className="break-all text-fg-muted">{sourceInfo.location}</dd></div>
                <div><dt className="font-medium text-fg">State</dt><dd className="text-fg-muted">{sourceInfo.state}</dd></div>
                {sourceInfo.revision ? <div><dt className="font-medium text-fg">Revision</dt><dd className="truncate font-mono text-fg-muted" title={sourceInfo.revision}>{sourceInfo.revision}</dd></div> : null}
              </dl>
              {sourceInfo.copyPath ? <Button variant="secondary" size="sm" className="mt-3" onClick={() => void copyPath()}>Copy path</Button> : null}
            </div>
          ) : null}
        </div>
        {dirty ? <span className="whitespace-nowrap text-warn">● unsaved changes</span> : null}
      </div>
      <div className="flex shrink-0 items-center gap-2">{actions}</div>
    </header>
  )
}
