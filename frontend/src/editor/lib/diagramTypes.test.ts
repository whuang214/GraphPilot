import { describe, expect, it } from 'vitest'
import { DIAGRAM_TYPE_DESCRIPTORS, diagramTypeDescriptor, filterDiagramTypes } from './diagramTypes'

describe('diagram type descriptors', () => {
  it('keeps the four supported types in deterministic display order', () => {
    expect(DIAGRAM_TYPE_DESCRIPTORS.map((descriptor) => descriptor.type)).toEqual([
      'activity_diagram', 'use_case_diagram', 'bdd_diagram', 'custom',
    ])
    expect(new Set(DIAGRAM_TYPE_DESCRIPTORS.map((descriptor) => descriptor.type)).size).toBe(DIAGRAM_TYPE_DESCRIPTORS.length)
  })

  it.each(DIAGRAM_TYPE_DESCRIPTORS)('defines complete presentation and blank defaults for $type', (descriptor) => {
    expect(descriptor.label).toBeTruthy()
    expect(descriptor.description).toBeTruthy()
    expect(descriptor.notation).toBeTruthy()
    expect(descriptor.keywords.length).toBeGreaterThan(0)
    expect(descriptor.defaultName).toMatch(/^Untitled /)
    expect(diagramTypeDescriptor(descriptor.type)).toBe(descriptor)
  })

  it('searches label, canonical id, description, notation, and keywords', () => {
    expect(filterDiagramTypes('activity').map((descriptor) => descriptor.type)).toEqual(['activity_diagram'])
    expect(filterDiagramTypes('use_case_diagram').map((descriptor) => descriptor.type)).toEqual(['use_case_diagram'])
    expect(filterDiagramTypes('actors').map((descriptor) => descriptor.type)).toEqual(['use_case_diagram'])
    expect(filterDiagramTypes('sysml').map((descriptor) => descriptor.type)).toEqual(['bdd_diagram'])
    expect(filterDiagramTypes('generic').map((descriptor) => descriptor.type)).toEqual(['custom'])
    expect(filterDiagramTypes('missing')).toEqual([])
  })

  it('returns the complete deterministic order for a blank query', () => {
    expect(filterDiagramTypes('   ')).toEqual(DIAGRAM_TYPE_DESCRIPTORS)
  })
})
