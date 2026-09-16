import { useCallback, useEffect, useState } from 'react'

export interface RailState {
  width: number
  collapsed: boolean
}

// Per-rail width + collapsed state, persisted to localStorage so the layout
// survives reloads. Used by the left palette rail and right inspector rail.
export function useRail(storageKey: string, defaultWidth: number) {
  const [state, setState] = useState<RailState>(() => {
    try {
      const raw = localStorage.getItem(storageKey)
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<RailState>
        return {
          width: typeof parsed.width === 'number' && Number.isFinite(parsed.width) && parsed.width > 0
            ? parsed.width
            : defaultWidth,
          collapsed: parsed.collapsed === true,
        }
      }
    } catch {
      // ignore malformed/inaccessible storage and fall back to defaults
    }
    return { width: defaultWidth, collapsed: false }
  })

  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(state))
    } catch {
      // ignore write failures (e.g. storage disabled)
    }
  }, [storageKey, state])

  const setWidth = useCallback((width: number) => setState((s) => ({ ...s, width })), [])
  const toggle = useCallback(() => setState((s) => ({ ...s, collapsed: !s.collapsed })), [])

  return { width: state.width, collapsed: state.collapsed, setWidth, toggle }
}
