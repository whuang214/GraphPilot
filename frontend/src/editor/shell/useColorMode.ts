import { useCallback, useEffect, useState } from 'react'

export type ColorMode = 'light' | 'dark'
const KEY = 'gp.colorMode'

// True when the OS asks for a dark UI. Feature-detected so non-browser/jsdom
// environments (where matchMedia is absent) safely fall back.
function prefersDark(): boolean {
  try {
    return typeof window !== 'undefined' && typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
      : false
  } catch {
    return false
  }
}

function initial(): ColorMode {
  try {
    const v = localStorage.getItem(KEY)
    if (v === 'light' || v === 'dark') return v
  } catch {
    // ignore inaccessible storage
  }
  // No stored choice yet: follow the operating system's preference by default.
  return prefersDark() ? 'dark' : 'light'
}

// App color mode. Toggles the `.dark` class on <html> (which flips the design
// tokens in index.css) and is passed to React Flow's `colorMode` so the canvas
// chrome themes too. Persisted to localStorage.
export function useColorMode() {
  const [mode, setMode] = useState<ColorMode>(initial)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', mode === 'dark')
    try {
      localStorage.setItem(KEY, mode)
    } catch {
      // ignore write failures
    }
  }, [mode])

  const toggle = useCallback(() => setMode((m) => (m === 'dark' ? 'light' : 'dark')), [])
  return { mode, toggle }
}
