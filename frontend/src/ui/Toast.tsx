import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { cn } from './cn'
import { ToastContext } from './toastContext'
import type { ToastTone } from './toastContext'

interface ToastItem {
  id: number
  tone: ToastTone
  message: string
}

let nextId = 1

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  // Track pending auto-dismiss timers so they can be cleared on unmount — otherwise
  // a timer that fires after the provider unmounts updates state on a dead component.
  const timers = useRef<Set<ReturnType<typeof setTimeout>>>(new Set())
  const notify = useCallback((tone: ToastTone, message: string) => {
    const id = nextId++
    setToasts((t) => [...t, { id, tone, message }])
    const timer = setTimeout(() => {
      timers.current.delete(timer)
      setToasts((t) => t.filter((x) => x.id !== id))
    }, 4000)
    timers.current.add(timer)
  }, [])
  useEffect(
    () => () => {
      timers.current.forEach((t) => clearTimeout(t))
      timers.current.clear()
    },
    [],
  )
  const value = useMemo(() => ({ notify }), [notify])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 bottom-4 z-50 flex flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            role={t.tone === 'error' ? 'alert' : 'status'}
            className={cn(
              'pointer-events-auto rounded-md border px-3 py-2 text-sm shadow-md',
              t.tone === 'success' && 'border-success bg-success-bg text-success',
              t.tone === 'error' && 'border-danger bg-danger-bg text-danger',
              t.tone === 'info' && 'border-line bg-surface text-fg',
            )}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
