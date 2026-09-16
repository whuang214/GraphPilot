import { useEffect, useId, useRef } from 'react'
import type { ReactNode } from 'react'

interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  /** Panel max-width. Defaults to 'md'; 'lg'/'xl' suit wider content (e.g. an SVG preview). */
  size?: 'md' | 'lg' | 'xl'
  children: ReactNode
}

const SIZE_CLASS: Record<NonNullable<ModalProps['size']>, string> = {
  md: 'max-w-md',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}

const FOCUSABLE =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

// Accessible modal: backdrop + centered panel, closes on Escape or backdrop click.
// On open it moves focus into the dialog, traps Tab within it, and restores focus
// to the previously focused element on close. Used by the shortcuts help and the
// save/preview dialogs.
export function Modal({ open, onClose, title, size = 'md', children }: ModalProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  const restoreFocusRef = useRef<HTMLElement | null>(null)
  const titleId = useId()

  useEffect(() => {
    if (!open) return
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onClose()
        return
      }
      if (e.key !== 'Tab') return
      const panel = panelRef.current
      if (!panel) return
      const items = Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE))
      if (items.length === 0) {
        e.preventDefault()
        panel.focus()
        return
      }
      const first = items[0]
      const last = items[items.length - 1]
      const active = document.activeElement
      if (e.shiftKey && (active === first || !panel.contains(active))) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && active === last) {
        e.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  // Move focus into the dialog on open; restore it to the opener on close.
  useEffect(() => {
    if (!open) return
    restoreFocusRef.current = document.activeElement as HTMLElement | null
    const panel = panelRef.current
    const preferred = panel?.querySelector<HTMLElement>('[data-modal-initial-focus]')
    const first = panel?.querySelector<HTMLElement>(FOCUSABLE)
    ;(preferred ?? first ?? panel)?.focus()
    return () => restoreFocusRef.current?.focus?.()
  }, [open])

  if (!open) return null
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        ref={panelRef}
        className={`max-h-[80vh] w-full ${SIZE_CLASS[size]} overflow-y-auto rounded-lg border border-line bg-surface p-4 shadow-lg`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? titleId : undefined}
        aria-label={title ? undefined : 'Dialog'}
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          {title ? (
            <h2 id={titleId} className="text-base font-semibold text-fg">
              {title}
            </h2>
          ) : <span />}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className="rounded px-1.5 py-0.5 text-fg-muted hover:bg-surface-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
