import { useMemo, useRef, useState } from 'react'
import { Button, cn } from '@/ui'
import { diffHunks, numberRows } from '@/editor/lib/jsonDiff'
import type { DiffRow, NumberedRow } from '@/editor/lib/jsonDiff'

// Unchanged lines kept visible on each side of a change before the middle of a
// long run is folded away.
const CONTEXT = 3

interface JsonDiffViewProps {
  rows: DiffRow[]
  raw: string
  showRaw: boolean
}

// A rendered line, or a fold standing in for a run of hidden unchanged lines.
type RenderItem =
  | { kind: 'row'; rowIndex: number }
  | { kind: 'fold'; id: number; count: number }

// Collapse long unchanged runs to a single expandable fold.
function buildItems(types: DiffRow['type'][], expanded: Set<number>): RenderItem[] {
  const items: RenderItem[] = []
  let i = 0
  while (i < types.length) {
    if (types[i] !== 'context') {
      items.push({ kind: 'row', rowIndex: i })
      i += 1
      continue
    }
    const start = i
    while (i < types.length && types[i] === 'context') i += 1
    const len = i - start
    if (len <= CONTEXT * 2 + 1 || expanded.has(start)) {
      for (let k = start; k < i; k += 1) items.push({ kind: 'row', rowIndex: k })
    } else {
      for (let k = start; k < start + CONTEXT; k += 1) items.push({ kind: 'row', rowIndex: k })
      items.push({ kind: 'fold', id: start, count: len - CONTEXT * 2 })
      for (let k = i - CONTEXT; k < i; k += 1) items.push({ kind: 'row', rowIndex: k })
    }
  }
  return items
}

function DiffLine({ row, lineRef }: { row: NumberedRow; lineRef: (el: HTMLDivElement | null) => void }) {
  const tint =
    row.type === 'add' ? 'bg-success-bg text-success' : row.type === 'del' ? 'bg-danger-bg text-danger' : ''
  const sign = row.type === 'add' ? '+' : row.type === 'del' ? '-' : '\u00a0'
  return (
    <div ref={lineRef} className={cn('flex whitespace-pre-wrap', tint)}>
      <span className="w-9 shrink-0 select-none px-1 text-right text-fg-subtle">{row.oldNo ?? ''}</span>
      <span className="w-9 shrink-0 select-none px-1 text-right text-fg-subtle">{row.newNo ?? ''}</span>
      <span className="w-4 shrink-0 select-none text-center opacity-60">{sign}</span>
      <span className="flex-1">{row.text}</span>
    </div>
  )
}

// Diff viewer for the Preview JSON modal: line numbers, collapsible unchanged
// regions, prev/next change navigation, and a clickable scrollbar overview.
// Raw mode shows the plain current JSON.
export function JsonDiffView({ rows, raw, showRaw }: JsonDiffViewProps) {
  const rowRefs = useRef<Map<number, HTMLDivElement>>(new Map())
  const [expanded, setExpanded] = useState<Set<number>>(() => new Set())
  const [hunkIdx, setHunkIdx] = useState(0)

  const numbered = useMemo(() => numberRows(rows), [rows])
  const hunks = useMemo(() => diffHunks(rows), [rows])
  const types = useMemo(() => rows.map((r) => r.type), [rows])
  const items = useMemo(() => buildItems(types, expanded), [types, expanded])
  const itemIndexByRow = useMemo(() => {
    const map = new Map<number, number>()
    items.forEach((item, idx) => {
      if (item.kind === 'row') map.set(item.rowIndex, idx)
    })
    return map
  }, [items])

  if (showRaw) {
    return (
      <pre
        className="max-h-[60vh] overflow-auto rounded border border-line bg-surface-2 p-2 font-mono text-xs leading-relaxed"
        data-testid="json-preview"
      >
        <code>{raw}</code>
      </pre>
    )
  }

  function goToHunk(idx: number) {
    if (hunks.length === 0) return
    const clamped = ((idx % hunks.length) + hunks.length) % hunks.length
    setHunkIdx(clamped)
    rowRefs.current.get(hunks[clamped].start)?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }

  const lastItem = Math.max(items.length - 1, 1)

  return (
    <div>
      {hunks.length > 0 ? (
        <div className="mb-2 flex items-center gap-2 text-xs text-fg-muted">
          <span>{hunks.length} change{hunks.length === 1 ? '' : 's'}</span>
          <Button variant="ghost" size="sm" onClick={() => goToHunk(hunkIdx - 1)} title="Previous change">
            ↑ Prev
          </Button>
          <Button variant="ghost" size="sm" onClick={() => goToHunk(hunkIdx + 1)} title="Next change">
            ↓ Next
          </Button>
        </div>
      ) : null}
      <div className="relative">
        <div
          className="max-h-[60vh] overflow-auto rounded border border-line bg-surface-2 pr-3 font-mono text-xs leading-relaxed"
          data-testid="json-preview"
        >
          {items.map((item) =>
            item.kind === 'fold' ? (
              <button
                key={`fold-${item.id}`}
                type="button"
                onClick={() => setExpanded((prev) => new Set(prev).add(item.id))}
                className="block w-full bg-surface px-2 py-0.5 text-left text-fg-muted hover:bg-fg/10"
              >
                {`\u22ef ${item.count} unchanged line${item.count === 1 ? '' : 's'}`}
              </button>
            ) : (
              <DiffLine
                key={`row-${item.rowIndex}`}
                row={numbered[item.rowIndex]}
                lineRef={(el) => {
                  if (el) rowRefs.current.set(item.rowIndex, el)
                  else rowRefs.current.delete(item.rowIndex)
                }}
              />
            ),
          )}
        </div>
        {hunks.length > 0 ? (
          // Scrollbar overview: a clickable tick per change at its proportional
          // position, coloured by add / remove / mixed.
          <div className="absolute bottom-0 right-0.5 top-0 w-1.5">
            {hunks.map((hunk, i) => {
              const top = ((itemIndexByRow.get(hunk.start) ?? 0) / lastItem) * 100
              const slice = rows.slice(hunk.start, hunk.end)
              const hasAdd = slice.some((r) => r.type === 'add')
              const hasDel = slice.some((r) => r.type === 'del')
              const color = hasAdd && hasDel ? 'bg-warn' : hasAdd ? 'bg-success' : 'bg-danger'
              return (
                <button
                  key={`tick-${hunk.start}`}
                  type="button"
                  title={`Change ${i + 1}`}
                  aria-label={`Go to change ${i + 1}`}
                  onClick={() => goToHunk(i)}
                  className={cn('absolute right-0 h-1 w-full rounded-sm', color)}
                  style={{ top: `${top}%` }}
                />
              )
            })}
          </div>
        ) : null}
      </div>
    </div>
  )
}
