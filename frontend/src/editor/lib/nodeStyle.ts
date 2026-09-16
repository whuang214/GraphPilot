import type { GraphPilotNodeStyle } from '@/types/diagram'

// Resolved visual style for a custom node renderer (all fields concrete).
export interface ResolvedStyle {
  background: string
  borderColor: string
  color: string
  borderWidth: number
  borderStyle: string
}

export const STYLE_DEFAULTS: ResolvedStyle = {
  background: '#ffffff',
  borderColor: '#333333',
  color: '#111111',
  borderWidth: 1,
  borderStyle: 'solid',
}

// Dark-mode equivalents for the DEFAULT (unauthored) look:
// a draw.io-style transparent interior with a light outline + light text, so the
// default white shapes don't glare on the dark canvas and stay legible. Authored
// colors (anything other than the defaults) are preserved in either theme.
const DARK_BORDER = '#94a3b8'
const DARK_TEXT = '#e2e8f0'

// Resolve a node's visual style, theming only the DEFAULT values for dark mode.
// Saved JSON / gpStyle is never changed by this; it is render-only.
export function resolveStyle(gp: GraphPilotNodeStyle | undefined, dark: boolean): ResolvedStyle {
  const background = gp?.background ?? STYLE_DEFAULTS.background
  const borderColor = gp?.borderColor ?? STYLE_DEFAULTS.borderColor
  const color = gp?.color ?? STYLE_DEFAULTS.color
  return {
    background: dark && background === STYLE_DEFAULTS.background ? 'transparent' : background,
    borderColor: dark && borderColor === STYLE_DEFAULTS.borderColor ? DARK_BORDER : borderColor,
    color: dark && color === STYLE_DEFAULTS.color ? DARK_TEXT : color,
    borderWidth: gp?.borderWidth ?? STYLE_DEFAULTS.borderWidth,
    borderStyle: gp?.borderStyle ?? STYLE_DEFAULTS.borderStyle,
  }
}

export function borderCss(s: ResolvedStyle): string {
  return `${s.borderWidth}px ${s.borderStyle} ${s.borderColor}`
}
