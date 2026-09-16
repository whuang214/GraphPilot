import { useState } from 'react'
import { Button, cn, Modal } from '@/ui'
import type { CatalogDiagramType } from '@/editor/lib/elementCatalog'
import { filterDiagramTypes } from '@/editor/lib/diagramTypes'

interface HomeProps {
  // Whether the native file picker (File System Access API) is available.
  fsaSupported: boolean
  // Open a diagram from disk via the native file picker.
  onOpenFile: () => void
  // Start one unsaved canonical diagram without calling generation.
  onNewDiagram: (diagramType: CatalogDiagramType) => void
  // Recently opened (path-based) diagrams.
  recents: string[]
  // Re-open a recent diagram by its path.
  onOpenRecent: (path: string) => void
  // Clear reopenable history only; never delete files.
  onClearRecents: () => void
  // When set, a load/parse error to surface above the open options (recovery state).
  error?: { code: string; message: string }
  // Open a .gp.json dropped anywhere on the landing page.
  onDropFile?: (dataTransfer: DataTransfer) => void
}

// Split a path into its file name and parent directory for a tidier recents list.
function splitPath(path: string): { name: string; dir: string } {
  const norm = path.replace(/\\/g, '/')
  const i = norm.lastIndexOf('/')
  return i >= 0 ? { name: norm.slice(i + 1), dir: norm.slice(0, i + 1) } : { name: norm, dir: '' }
}

// Landing / empty state shown when no diagram is open. It supports the native file
// picker, drag-and-drop, recents, and MCP agent links (`?diagramPath=`), without a
// raw-path text field. The same screen
// doubles as the load-error recovery state when `error` is set.
export function Home({ fsaSupported, onOpenFile, onNewDiagram, recents, onOpenRecent, onClearRecents, error, onDropFile }: HomeProps) {
  const [dragging, setDragging] = useState(false)
  const [chooserOpen, setChooserOpen] = useState(false)
  const [query, setQuery] = useState('')
  const diagramTypes = filterDiagramTypes(query)
  const closeChooser = () => {
    setChooserOpen(false)
    setQuery('')
  }
  const chooseDiagram = (diagramType: CatalogDiagramType) => {
    closeChooser()
    onNewDiagram(diagramType)
  }
  return (
    <main
      className="flex min-h-screen items-center justify-center bg-surface-2 p-6"
      onDragOver={onDropFile ? (e) => { e.preventDefault(); setDragging(true) } : undefined}
      onDragLeave={onDropFile ? () => setDragging(false) : undefined}
      onDrop={
        onDropFile
          ? (e) => {
              e.preventDefault()
              setDragging(false)
              onDropFile(e.dataTransfer)
            }
          : undefined
      }
    >
      <div className="w-full max-w-md rounded-xl border border-line bg-surface p-8 shadow-sm">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-fg">GraphPilot</h1>
          <p className="mt-1 text-sm text-fg-muted">
            {error ? 'That diagram could not be opened. Try another.' : 'Open a diagram to view and edit it.'}
          </p>
        </header>

        {error ? (
          <div className="mb-6 rounded-md border border-danger/30 bg-danger-bg px-3 py-2 text-sm break-words text-danger">
            <strong>[{error.code}]</strong> {error.message}
          </div>
        ) : null}

        <section className="mb-6">
          <h2 className="mb-2 text-xs font-semibold tracking-wide text-fg-subtle uppercase">New diagram</h2>
          <Button variant="primary" className="w-full" onClick={() => setChooserOpen(true)}>
            New diagram…
          </Button>
        </section>

        <div className="flex flex-col gap-2">
          <Button
            variant="secondary"
            onClick={onOpenFile}
            disabled={!fsaSupported}
            title={fsaSupported ? 'Open a .gp.json file from your computer' : 'Open file needs a Chromium browser (Chrome/Edge)'}
          >
            Open file…
          </Button>
          {!fsaSupported ? <p className="text-xs text-fg-subtle">Open file needs Chrome or Edge.</p> : null}
        </div>

        {onDropFile ? (
          <div
            className={cn(
              'mt-4 rounded-md border border-dashed px-3 py-5 text-center text-xs transition-colors',
              dragging ? 'border-accent bg-accent/5 text-fg' : 'border-line text-fg-subtle',
            )}
          >
            Drop a <code className="font-mono">.gp.json</code> file here to open it
          </div>
        ) : null}

        {recents.length > 0 ? (
          <div className="mt-6 border-t border-line pt-4">
            <div className="mb-2 flex items-center justify-between gap-2">
              <h2 className="text-xs font-semibold tracking-wide text-fg-subtle uppercase">Recent</h2>
              <Button variant="ghost" size="sm" onClick={onClearRecents}>Clear recents</Button>
            </div>
            <ul className="flex flex-col gap-1">
              {recents.map((path) => {
                const { name, dir } = splitPath(path)
                return (
                  <li key={path}>
                    <button
                      type="button"
                      onClick={() => onOpenRecent(path)}
                      title={path}
                      className="w-full rounded-md border border-line bg-surface px-3 py-2 text-left hover:border-accent/40 hover:bg-surface-2"
                    >
                      <span className="block truncate text-sm font-medium text-fg">{name}</span>
                      {dir ? <span className="block truncate text-xs text-fg-subtle">{dir}</span> : null}
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        ) : null}
      </div>
      <Modal open={chooserOpen} onClose={closeChooser} title="New diagram">
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search diagram types…"
          aria-label="Search diagram types"
          data-modal-initial-focus
          className="mb-3 w-full rounded-md border border-line bg-surface px-3 py-2 text-sm text-fg placeholder:text-fg-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
        />
        {diagramTypes.length ? (
          <ul className="max-h-80 space-y-2 overflow-y-auto pr-1" aria-label="Diagram types">
            {diagramTypes.map((descriptor) => (
              <li key={descriptor.type}>
                <button
                  type="button"
                  onClick={() => chooseDiagram(descriptor.type)}
                  aria-label={`Create ${descriptor.label} diagram`}
                  className="w-full rounded-md border border-line bg-surface px-3 py-2 text-left hover:border-accent/40 hover:bg-surface-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
                >
                  <span className="flex items-center justify-between gap-3">
                    <span className="text-sm font-medium text-fg">{descriptor.label}</span>
                    <span className="rounded-full border border-line bg-surface-2 px-2 py-0.5 text-[10px] font-semibold text-fg-subtle">{descriptor.notation}</span>
                  </span>
                  <span className="mt-0.5 block text-xs text-fg-subtle">{descriptor.description}</span>
                  <span className="mt-1 block font-mono text-[10px] text-fg-subtle">{descriptor.type}</span>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-md border border-dashed border-line px-3 py-5 text-center text-sm text-fg-subtle">No diagram types match your search.</p>
        )}
        <div className="mt-4 flex justify-end">
          <Button variant="secondary" onClick={closeChooser}>Cancel</Button>
        </div>
      </Modal>
    </main>
  )
}
