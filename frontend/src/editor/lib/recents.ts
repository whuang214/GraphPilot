// Recently opened diagram paths, persisted to localStorage for the Home screen.
const KEY = 'graphpilot.recentDiagrams'
const MAX = 8

export function getRecents(): string[] {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const parsed: unknown = JSON.parse(raw)
    return Array.isArray(parsed)
      ? parsed.filter((p): p is string => typeof p === 'string' && p.trim().length > 0).slice(0, MAX)
      : []
  } catch {
    return []
  }
}

export function clearRecents(): void {
  try {
    localStorage.removeItem(KEY)
  } catch {
    // ignore write failures (e.g. storage disabled)
  }
}

export function addRecent(path: string): void {
  const trimmed = path.trim()
  if (!trimmed) return
  try {
    const next = [trimmed, ...getRecents().filter((p) => p !== trimmed)].slice(0, MAX)
    localStorage.setItem(KEY, JSON.stringify(next))
  } catch {
    // ignore write failures (e.g. storage disabled)
  }
}
