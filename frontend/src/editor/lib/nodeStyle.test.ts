import { describe, expect, it } from 'vitest'
import { resolveStyle, STYLE_DEFAULTS } from './nodeStyle'

describe('resolveStyle', () => {
  it('uses the defaults as-is in light mode', () => {
    const s = resolveStyle(undefined, false)
    expect(s.background).toBe(STYLE_DEFAULTS.background)
    expect(s.borderColor).toBe(STYLE_DEFAULTS.borderColor)
    expect(s.color).toBe(STYLE_DEFAULTS.color)
  })

  it('themes only the DEFAULT look for dark mode (transparent interior, light outline/text)', () => {
    const s = resolveStyle(undefined, true)
    expect(s.background).toBe('transparent')
    expect(s.borderColor).not.toBe(STYLE_DEFAULTS.borderColor)
    expect(s.color).not.toBe(STYLE_DEFAULTS.color)
  })

  it('preserves authored colors in dark mode', () => {
    const authored = { background: '#dbeafe', borderColor: '#2563eb', color: '#1e3a8a' }
    const s = resolveStyle(authored, true)
    expect(s.background).toBe('#dbeafe')
    expect(s.borderColor).toBe('#2563eb')
    expect(s.color).toBe('#1e3a8a')
  })
})
