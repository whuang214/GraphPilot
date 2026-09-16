import { createContext, useContext } from 'react'

export type ToastTone = 'success' | 'error' | 'info'

export interface ToastApi {
  notify: (tone: ToastTone, message: string) => void
}

// Kept in a non-component module so `Toast.tsx` only exports a component
// (satisfies the fast-refresh `only-export-components` lint rule).
export const ToastContext = createContext<ToastApi | null>(null)

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}
