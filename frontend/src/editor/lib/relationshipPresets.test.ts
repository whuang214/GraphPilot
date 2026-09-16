import { describe, expect, it } from 'vitest'
import {
  applyRelationshipSemantic,
  defaultRelationshipSemantic,
  relationshipTools,
} from './relationshipPresets'

describe('relationship tools', () => {
  it.each([
    ['activity_diagram', ['controlFlow', 'commentLink']],
    ['use_case_diagram', ['association', 'generalization', 'include', 'extend', 'commentLink']],
    ['bdd_diagram', ['association', 'composition', 'generalization', 'dependency', 'commentLink']],
    ['custom', ['association', 'controlFlow', 'composition', 'generalization', 'include', 'extend', 'dependency', 'realization', 'commentLink']],
  ])('derives the bounded %s relationship set from the catalog', (diagramType, expected) => {
    expect(relationshipTools(diagramType).map((tool) => tool.semanticType)).toEqual(expected)
  })

  it.each([
    ['activity_diagram', [['controlFlow', '──→'], ['commentLink', '╌╌╌']]],
    ['use_case_diagram', [['association', '───'], ['generalization', '──▷'], ['include', '╌╌→'], ['extend', '╌╌→'], ['commentLink', '╌╌╌']]],
    ['bdd_diagram', [['association', '───'], ['composition', '──◆'], ['generalization', '──▷'], ['dependency', '╌╌→'], ['commentLink', '╌╌╌']]],
    ['custom', [['association', '───'], ['controlFlow', '──→'], ['composition', '──◆'], ['generalization', '──▷'], ['include', '╌╌→'], ['extend', '╌╌→'], ['dependency', '╌╌→'], ['realization', '╌╌▷'], ['commentLink', '╌╌╌']]],
  ])('derives %s glyphs from catalog marker metadata', (diagramType, expected) => {
    expect(relationshipTools(diagramType).map(({ semanticType, glyph }) => [semanticType, glyph])).toEqual(expected)
  })

  it('selects the first catalog tool as each diagram default', () => {
    expect(defaultRelationshipSemantic('activity_diagram')).toBe('controlFlow')
    expect(defaultRelationshipSemantic('use_case_diagram')).toBe('association')
    expect(defaultRelationshipSemantic('bdd_diagram')).toBe('association')
    expect(defaultRelationshipSemantic('custom')).toBe('association')
  })

  it('maps composition to its first-class identity while preserving common and end data', () => {
    const patch = applyRelationshipSemantic(
      {
        semanticType: 'association',
        description: 'owns',
        metadata: { reviewed: true },
        appliedStereotypes: [{ name: 'domain' }],
        sourceEnd: { role: 'part', multiplicity: { lower: 1, upper: 1 }, aggregation: 'none' },
        targetEnd: { role: 'whole', aggregation: 'composite' },
        itemFlows: [{ direction: 'sourceToTarget', item: 'Power' }],
      },
      'composition',
    )
    expect(patch).toEqual({
      semanticType: 'composition',
      data: {
        description: 'owns',
        metadata: { reviewed: true },
        appliedStereotypes: [{ name: 'domain' }],
        sourceEnd: { role: 'part', multiplicity: { lower: 1, upper: 1 } },
        targetEnd: { role: 'whole' },
      },
      clearData: ['condition', 'extensionLocations', 'itemFlows', 'guard', 'weight', 'isInterrupting', 'arrow'],
    })
  })

  it('preserves only fields compatible with the next relationship identity', () => {
    const extend = applyRelationshipSemantic({
      semanticType: 'association',
      description: 'optional behavior',
      sourceEnd: { role: 'source' },
      condition: 'account is verified',
      extensionLocations: ['Verified'],
      guard: 'legacy',
    }, 'extend')
    expect(extend.data).toEqual({
      description: 'optional behavior',
      condition: 'account is verified',
      extensionLocations: ['Verified'],
    })
    expect(extend.clearData).toEqual(['sourceEnd', 'targetEnd', 'itemFlows', 'guard', 'weight', 'isInterrupting', 'arrow'])

    const control = applyRelationshipSemantic({
      semanticType: 'extend',
      condition: 'legacy',
      guard: 'approved',
      weight: 2,
      isInterrupting: false,
    }, 'controlFlow')
    expect(control.data).toEqual({ guard: 'approved', weight: 2, isInterrupting: false })
    expect(control.clearData).toContain('condition')
    expect(control.clearData).toContain('sourceEnd')
  })
})
