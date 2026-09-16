import { describe, expect, it } from 'vitest'
import type { Node } from '@xyflow/react'
import { miniMapNodeColor } from '@/editor/canvas/miniMap'
import {
  DEFAULT_NODE_STYLE,
  defaultEdgeSemantic,
  defaultNodeSize,
  defaultRouteMode,
  newNodeId,
  organizedPaletteGroups,
  paletteItems,
} from './palette'

describe('catalog-driven palette helpers', () => {
  it('uses the backend default edge semantic for every diagram profile', () => {
    expect(defaultEdgeSemantic('activity_diagram')).toBe('controlFlow')
    expect(defaultEdgeSemantic('use_case_diagram')).toBe('association')
    expect(defaultEdgeSemantic('bdd_diagram')).toBe('association')
    expect(defaultEdgeSemantic('custom')).toBe('association')
    expect(defaultEdgeSemantic('something-else')).toBe('association')
  })

  it('defaults new Use Case edges to straight and every other profile to orthogonal', () => {
    expect(defaultRouteMode('use_case_diagram')).toBe('straight')
    expect(defaultRouteMode('activity_diagram')).toBe('orthogonal')
    expect(defaultRouteMode('bdd_diagram')).toBe('orthogonal')
    expect(defaultRouteMode('custom')).toBe('orthogonal')
    expect(defaultRouteMode('something-else')).toBe('orthogonal')
  })

  it('matches every explicit backend DEFAULT_NODE_SIZES entry', () => {
    const expected: Record<string, { width: number; height: number }> = {
      initialNode: { width: 90, height: 60 },
      activityFinalNode: { width: 90, height: 60 },
      flowFinalNode: { width: 90, height: 60 },
      mergeNode: { width: 120, height: 50 },
      forkNode: { width: 120, height: 30 },
      joinNode: { width: 120, height: 30 },
      opaqueAction: { width: 160, height: 60 },
      decisionNode: { width: 140, height: 80 },
      objectNode: { width: 160, height: 60 },
      centralBufferNode: { width: 160, height: 60 },
      dataStoreNode: { width: 160, height: 70 },
      inputPin: { width: 24, height: 24 },
      outputPin: { width: 24, height: 24 },
      valuePin: { width: 24, height: 24 },
      actionInputPin: { width: 24, height: 24 },
      expansionNode: { width: 24, height: 24 },
      note: { width: 160, height: 80 },
      actor: { width: 90, height: 120 },
      useCase: { width: 200, height: 70 },
      subject: { width: 320, height: 240 },
      block: { width: 180, height: 90 },
      valueType: { width: 180, height: 90 },
      constraintBlock: { width: 180, height: 100 },
      interfaceBlock: { width: 180, height: 90 },
      enumeration: { width: 180, height: 90 },
      propertySpecificType: { width: 180, height: 90 },
      instanceSpecification: { width: 180, height: 90 },
      unit: { width: 180, height: 80 },
      quantityKind: { width: 180, height: 80 },
      associationBlock: { width: 180, height: 100 },
      port: { width: 44, height: 44 },
      proxyPort: { width: 44, height: 44 },
      fullPort: { width: 44, height: 44 },
    }
    for (const [semanticType, size] of Object.entries(expected)) {
      expect(defaultNodeSize(semanticType), semanticType).toEqual(size)
    }
  })

  it('uses a 140x60 backend fallback and usable defaults for unsized containers', () => {
    expect(defaultNodeSize('callBehaviorAction')).toEqual({ width: 140, height: 60 })
    expect(defaultNodeSize('unknown-shape')).toEqual({ width: 140, height: 60 })
    expect(defaultNodeSize('activityPartition')).toEqual({ width: 320, height: 240 })
    expect(defaultNodeSize('interruptibleActivityRegion')).toEqual({ width: 320, height: 240 })
    expect(defaultNodeSize('package')).toEqual({ width: 320, height: 240 })
  })

  it('filters to declared core vocabularies and the bounded custom authorable union', () => {
    expect(paletteItems('activity_diagram')).toHaveLength(8)
    expect(paletteItems('use_case_diagram').map((item) => item.semanticType)).toEqual([
      'note',
      'actor',
      'useCase',
      'subject',
    ])
    expect(paletteItems('bdd_diagram').map((item) => item.semanticType)).toEqual(['note', 'block'])
    expect(paletteItems('custom')).toHaveLength(17)
  })

  it('keeps palette items limited to canonical drag payload fields', () => {
    for (const item of paletteItems('custom')) {
      expect(Object.keys(item)).toEqual(['type', 'semanticType', 'label'])
      expect(item.type).toBe('gpNode')
      expect(item.semanticType).toBeTruthy()
      expect(item.label).toBeTruthy()
    }
  })

  it.each([
    ['activity_diagram', ['initialNode', 'opaqueAction', 'decisionNode', 'mergeNode', 'forkNode', 'joinNode', 'activityFinalNode', 'note'], ['controlFlow', 'commentLink']],
    ['use_case_diagram', ['actor', 'useCase', 'subject', 'note'], ['association', 'generalization', 'include', 'extend', 'commentLink']],
    ['bdd_diagram', ['block', 'note'], ['association', 'composition', 'generalization', 'dependency', 'commentLink']],
  ])('projects the exact bounded current %s shape and relationship set', (diagramType, expectedShapes, expectedRelationships) => {
    const groups = organizedPaletteGroups({ diagramType })
    expect(groups.flatMap((group) => group.shapes.map((item) => item.semanticType)).sort()).toEqual([...expectedShapes].sort())
    expect(groups.flatMap((group) => group.relationships.map((item) => item.semanticType)).sort()).toEqual([...expectedRelationships].sort())
  })

  it('groups the all-authorable union once in deliberate diagram order', () => {
    const groups = organizedPaletteGroups({ diagramType: 'activity_diagram', scope: 'all' })
    expect(groups.map((group) => group.label)).toEqual(['Shared', 'Activity', 'Use Case', 'BDD', 'Custom-only'])
    expect(organizedPaletteGroups({ diagramType: 'custom', scope: 'current' })).toEqual(groups)
    const semantics = groups.flatMap((group) => [
      ...group.shapes.map((item) => item.semanticType),
      ...group.relationships.map((item) => item.semanticType),
    ])
    expect(semantics).toHaveLength(26)
    expect(new Set(semantics).size).toBe(26)
    expect(semantics).not.toContain('proxyPort')
    expect(semantics).not.toContain('containment')
    expect(groups.find((group) => group.label === 'Shared')?.relationships.map((item) => item.semanticType)).toEqual([
      'association', 'commentLink', 'generalization',
    ])
  })

  it('organizes the same authorable union by Common/UML/SysML notation', () => {
    const groups = organizedPaletteGroups({ scope: 'all', organization: 'notation' })
    expect(groups.map((group) => group.label)).toEqual(['Common', 'UML', 'SysML'])
    expect(groups.find((group) => group.label === 'SysML')?.shapes.map((item) => item.semanticType)).toContain('block')
    expect(groups.find((group) => group.label === 'Common')?.relationships.map((item) => item.semanticType)).toEqual(['commentLink'])
  })

  it('searches labels, semantics, categories, diagram families, and notation across both sections', () => {
    const include = organizedPaletteGroups({ scope: 'all', query: 'include' })
    expect(include.flatMap((group) => group.relationships.map((item) => item.semanticType))).toEqual(['include'])

    const annotation = organizedPaletteGroups({ scope: 'all', query: 'annotation' })
    expect(annotation.flatMap((group) => group.shapes.map((item) => item.semanticType))).toEqual(['note'])
    expect(annotation.flatMap((group) => group.relationships.map((item) => item.semanticType))).toEqual(['commentLink'])

    const sysml = organizedPaletteGroups({ scope: 'all', organization: 'notation', query: 'sysml' })
    expect(sysml.map((group) => group.label)).toEqual(['SysML'])
    const useCase = organizedPaletteGroups({ scope: 'all', query: 'use case' })
    expect(useCase.flatMap((group) => group.shapes.map((item) => item.semanticType))).toEqual(expect.arrayContaining(['actor', 'useCase', 'subject']))
  })

  it('sorts labels alphabetically within every subsection', () => {
    const groups = organizedPaletteGroups({ scope: 'all' })
    for (const group of groups) {
      expect(group.shapes.map((item) => item.label)).toEqual([...group.shapes.map((item) => item.label)].sort())
      expect(group.relationships.map((item) => item.label)).toEqual([...group.relationships.map((item) => item.label)].sort())
    }
  })

  it('generates unique ids namespaced by semantic type', () => {
    const first = newNodeId('opaqueAction')
    const second = newNodeId('opaqueAction')
    expect(first).not.toBe(second)
    expect(first.startsWith('node_opaqueAction_')).toBe(true)
  })

  it('uses the backend default node style', () => {
    expect(DEFAULT_NODE_STYLE).toEqual({
      background: '#ffffff',
      borderColor: '#333333',
      color: '#111111',
      borderWidth: 1,
      borderStyle: 'solid',
    })
  })
})

describe('catalog-driven minimap colours', () => {
  const makeNode = (semanticType: string): Node => ({
    id: semanticType,
    position: { x: 0, y: 0 },
    data: { semanticType },
  })

  it('colours shared glyphs by primitive and rejects stale aliases', () => {
    expect(miniMapNodeColor(makeNode('decisionNode'))).toBe(miniMapNodeColor(makeNode('mergeNode')))
    expect(miniMapNodeColor(makeNode('block'))).toBe(miniMapNodeColor(makeNode('constraintBlock')))
    expect(miniMapNodeColor(makeNode('initialNode'))).not.toBe(miniMapNodeColor(makeNode('activityFinalNode')))
    expect(miniMapNodeColor(makeNode('start'))).toBe('#94a3b8')
    expect(miniMapNodeColor(makeNode('missing'))).toBe('#94a3b8')
  })
})
