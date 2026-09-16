/** @vitest-environment jsdom */
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { JsonDiffView } from './JsonDiffView'
import { diffLines } from '@/editor/lib/jsonDiff'

afterEach(cleanup)

describe('JsonDiffView', () => {
  it('shows the plain JSON in raw mode', () => {
    render(<JsonDiffView rows={[]} raw={'{"a":1}'} showRaw />)
    expect(screen.getByText('{"a":1}')).toBeTruthy()
  })

  it('folds a long unchanged run and expands it on click', () => {
    const before = Array.from({ length: 10 }, (_, i) => `line ${i}`).join('\n')
    const after = `${before}\nNEW`
    render(<JsonDiffView rows={diffLines(before, after)} raw={after} showRaw={false} />)

    const fold = screen.getByText(/unchanged line/)
    expect(fold).toBeTruthy()
    fireEvent.click(fold)
    expect(screen.queryByText(/unchanged line/)).toBeNull()
  })

  it('renders prev/next change navigation when there are changes', () => {
    render(<JsonDiffView rows={diffLines('a\nb', 'a\nX')} raw={'a\nX'} showRaw={false} />)
    expect(screen.getByTitle('Next change')).toBeTruthy()
    expect(screen.getByTitle('Previous change')).toBeTruthy()
  })
})
