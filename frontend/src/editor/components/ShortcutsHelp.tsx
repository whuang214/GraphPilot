import { Fragment } from 'react'
import { Modal } from '@/ui'

const SHORTCUTS: ReadonlyArray<readonly [string, string]> = [
  ['Undo', 'Ctrl/Cmd + Z'],
  ['Redo', 'Ctrl/Cmd + Shift + Z'],
  ['Duplicate selection', 'Ctrl/Cmd + D'],
  ['Copy', 'Ctrl/Cmd + C'],
  ['Paste', 'Ctrl/Cmd + V'],
  ['Delete selection', 'Delete / Backspace'],
  ['Box-select', 'Shift + drag'],
  ['Add to selection', 'Ctrl/Cmd + click'],
  ['Double-click a node', 'Edit its label in place'],
]

export function ShortcutsHelp({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Modal open={open} onClose={onClose} title="Keyboard shortcuts">
      <dl className="grid grid-cols-[1fr_auto] gap-x-6 gap-y-2 text-sm">
        {SHORTCUTS.map(([label, keys]) => (
          <Fragment key={label}>
            <dt className="text-fg-muted">{label}</dt>
            <dd className="text-right font-mono text-fg">{keys}</dd>
          </Fragment>
        ))}
      </dl>
    </Modal>
  )
}
