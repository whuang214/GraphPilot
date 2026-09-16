import { useEffect, useState } from 'react'
import { Button, Input, Modal } from '@/ui'
import { DiagramApiError, listDiagrams } from '@/api/diagrams'
import type { DiagramSummary } from '@/types/diagram'

interface WorkspaceBrowserProps {
  open: boolean
  currentPath: string
  onClose: () => void
  onOpen: (path: string) => void
}

// Lists canonical diagrams under the current workspace's `.graphpilot/diagrams/`
// via the additive endpoint so they can be opened without hand-typing a path.
export function WorkspaceBrowser({ open, currentPath, onClose, onOpen }: WorkspaceBrowserProps) {
  const [items, setItems] = useState<DiagramSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    if (!open) return
    setItems(null)
    setError(null)
    setFilter('')
    let active = true
    listDiagrams(currentPath)
      .then((next) => {
        if (active) setItems(next)
      })
      .catch((e: unknown) => {
        if (active) setError(e instanceof DiagramApiError ? e.message : String(e))
      })
    return () => {
      active = false
    }
  }, [open, currentPath])

  const filtered = (items ?? []).filter((d) => d.name.toLowerCase().includes(filter.toLowerCase()))

  return (
    <Modal open={open} onClose={onClose} title="Open diagram">
      <Input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter by name"
        aria-label="Filter diagrams"
        className="mb-3"
      />
      {error ? <p className="mb-2 text-sm text-danger">{error}</p> : null}
      {items === null && !error ? <p className="text-sm text-fg-subtle">Loading…</p> : null}
      {items !== null && filtered.length === 0 && !error ? (
        <p className="text-sm text-fg-subtle">No diagrams found in this workspace.</p>
      ) : null}
      <ul className="flex max-h-72 flex-col gap-1 overflow-y-auto">
        {filtered.map((d) => (
          <li key={d.path}>
            <button
              type="button"
              onClick={() => {
                onClose()
                onOpen(d.path)
              }}
              className="w-full truncate rounded-md border border-line bg-surface px-3 py-2 text-left text-sm text-fg hover:border-accent/40 hover:bg-surface-2"
              title={d.path}
            >
              <span className="font-medium">{d.name}</span>
            </button>
          </li>
        ))}
      </ul>
      <div className="mt-3 flex justify-end">
        <Button variant="secondary" onClick={onClose}>Close</Button>
      </div>
    </Modal>
  )
}
