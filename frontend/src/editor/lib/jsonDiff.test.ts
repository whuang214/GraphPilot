import { describe, expect, it } from 'vitest'
import { diffHunks, diffLines, diffStats, numberRows } from './jsonDiff'

describe('diffLines', () => {
  it('marks every line as context when the two sides are identical', () => {
    const text = '{\n  "a": 1\n}'
    const rows = diffLines(text, text)
    expect(rows.every((r) => r.type === 'context')).toBe(true)
    expect(diffStats(rows)).toEqual({ added: 0, removed: 0 })
  })

  it('detects an inserted line', () => {
    const rows = diffLines('a\nb', 'a\nx\nb')
    expect(rows.map((r) => `${r.type}:${r.text}`)).toEqual(['context:a', 'add:x', 'context:b'])
    expect(diffStats(rows)).toEqual({ added: 1, removed: 0 })
  })

  it('detects a removed line', () => {
    const rows = diffLines('a\nb\nc', 'a\nc')
    expect(diffStats(rows)).toEqual({ added: 0, removed: 1 })
    expect(rows.some((r) => r.type === 'del' && r.text === 'b')).toBe(true)
  })

  it('represents a changed line as a delete + add', () => {
    const rows = diffLines('  "value": 1', '  "value": 2')
    expect(diffStats(rows)).toEqual({ added: 1, removed: 1 })
  })

  it('treats an empty baseline as all additions', () => {
    const rows = diffLines('', 'a\nb')
    expect(rows).toEqual([
      { type: 'add', text: 'a' },
      { type: 'add', text: 'b' },
    ])
  })
})

describe('diffHunks', () => {
  it('groups maximal runs of changed rows separated by context', () => {
    const hunks = diffHunks(diffLines('a\nb\nc', 'a\nX\nc\nD'))
    expect(hunks.length).toBe(2)
  })

  it('returns no hunks when the sides are identical', () => {
    expect(diffHunks(diffLines('a\nb', 'a\nb'))).toEqual([])
  })
})

describe('numberRows', () => {
  it('advances old/new line numbers per row type', () => {
    const numbered = numberRows(diffLines('a\nb', 'a\nX'))
    expect(numbered.map((r) => [r.type, r.oldNo, r.newNo])).toEqual([
      ['context', 1, 1],
      ['del', 2, null],
      ['add', null, 2],
    ])
  })
})
