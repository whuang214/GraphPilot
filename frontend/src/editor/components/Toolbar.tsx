import { Panel, useStore } from '@xyflow/react'
import { Button } from '@/ui'
import { PreviewMenu } from './PreviewMenu'
import { ToolbarMore } from './ToolbarMore'
import type { ToolbarMoreItem } from './ToolbarMore'

interface ToolbarProps {
  onUndo: () => void
  onRedo: () => void
  canUndo: boolean
  canRedo: boolean
  onDuplicate: () => void
  onDelete: () => void
  onPreviewRender: () => void
  onPreviewJson: () => void
  onValidate: () => void
  onHelp: () => void
}

// Progressive overflow: as the canvas pane narrows, more of the lower-priority
// actions fold into the "⋯ More" menu (one step at a time) so the bar stays a
// single row instead of wrapping. Undo/Redo and Preview always
// stay inline. Thresholds are pane-width px and are easy to retune.
const SHOW_DELETE_AT = 360
const SHOW_DUPLICATE_AT = 430
const SHOW_VALIDATE_AT = 500
const SHOW_HELP_AT = 560

function Divider() {
  return <span className="mx-0.5 h-5 w-px bg-line" />
}

// Floating editor toolbar rendered inside the React Flow pane. Zoom/fit are NOT
// duplicated here — React Flow's built-in Controls (bottom-left) already provide them.
export function Toolbar({ onUndo, onRedo, canUndo, canRedo, onDuplicate, onDelete, onPreviewRender, onPreviewJson, onValidate, onHelp }: ToolbarProps) {
  // Pane width from React Flow's store; shrinks as the side rails open/resize.
  // Treat an unmeasured (0) width as wide so nothing collapses on first paint.
  const paneWidth = useStore((s) => s.width) || Number.POSITIVE_INFINITY
  const showDelete = paneWidth >= SHOW_DELETE_AT
  const showDuplicate = paneWidth >= SHOW_DUPLICATE_AT
  const showValidate = paneWidth >= SHOW_VALIDATE_AT
  const showHelp = paneWidth >= SHOW_HELP_AT

  // Build the overflow menu in a stable display order (only the collapsed ones).
  const overflow: ToolbarMoreItem[] = []
  if (!showDuplicate) overflow.push({ label: 'Duplicate (Ctrl+D)', onClick: onDuplicate })
  if (!showDelete) overflow.push({ label: 'Delete (Del)', onClick: onDelete })
  if (!showValidate) overflow.push({ label: 'Validate', onClick: onValidate })
  if (!showHelp) overflow.push({ label: 'Keyboard shortcuts', onClick: onHelp })

  return (
    <Panel position="top-right" className="max-w-full">
      <div className="flex max-w-full flex-wrap items-center justify-end gap-1 rounded-md border border-line bg-surface/95 p-1 shadow-sm">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={onUndo} disabled={!canUndo} title="Undo (Ctrl+Z)">
            Undo
          </Button>
          <Button variant="ghost" size="sm" onClick={onRedo} disabled={!canRedo} title="Redo (Ctrl+Shift+Z)">
            Redo
          </Button>
        </div>
        {showDuplicate || showDelete ? <Divider /> : null}
        {showDuplicate || showDelete ? (
          <div className="flex items-center gap-1">
            {showDuplicate ? (
              <Button variant="ghost" size="sm" onClick={onDuplicate} title="Duplicate selection (Ctrl+D)">
                Duplicate
              </Button>
            ) : null}
            {showDelete ? (
              <Button variant="ghost" size="sm" onClick={onDelete} title="Delete selection (Del)">
                Delete
              </Button>
            ) : null}
          </div>
        ) : null}
        <Divider />
        <div className="flex items-center gap-1">
          {showValidate ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={onValidate}
              title="Validate the diagram and highlight any issues"
            >
              Validate
            </Button>
          ) : null}
          <PreviewMenu onRender={onPreviewRender} onJson={onPreviewJson} />
          {showHelp ? (
            <Button variant="ghost" size="sm" onClick={onHelp} title="Keyboard shortcuts" aria-label="Keyboard shortcuts">
              ?
            </Button>
          ) : null}
          {overflow.length > 0 ? <ToolbarMore items={overflow} /> : null}
        </div>
      </div>
    </Panel>
  )
}
