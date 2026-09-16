/** @vitest-environment jsdom */
import { afterEach, describe, expect, it } from 'vitest'
import { addRecent, clearRecents, getRecents } from './recents'

describe('recents', () => {
  afterEach(() => localStorage.clear())

  it('starts empty', () => {
    expect(getRecents()).toEqual([])
  })

  it('adds most-recent-first and de-duplicates', () => {
    addRecent('/a')
    addRecent('/b')
    addRecent('/a')
    expect(getRecents()).toEqual(['/a', '/b'])
  })

  it('ignores blank paths', () => {
    addRecent('   ')
    expect(getRecents()).toEqual([])
  })

  it('clears history without touching diagram files', () => {
    addRecent('/a')
    addRecent('/b')
    clearRecents()
    expect(getRecents()).toEqual([])
  })

  it('caps both newly written and pre-existing stored lists at 8 entries', () => {
    for (let i = 0; i < 12; i++) addRecent(`/p${i}`)
    const recents = getRecents()
    expect(recents).toHaveLength(8)
    expect(recents[0]).toBe('/p11')

    localStorage.setItem('graphpilot.recentDiagrams', JSON.stringify(Array.from({ length: 20 }, (_, i) => `/old${i}`)))
    expect(getRecents()).toHaveLength(8)
  })
})
