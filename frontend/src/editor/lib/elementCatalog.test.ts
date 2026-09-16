import { describe, expect, it } from 'vitest'
import {
  ELEMENT_CATALOG,
  ELEMENT_SPECS,
  allowedEdgeSpecs,
  allowedNodeSpecs,
  canOwnSemantic,
  getElementSpec,
  isContainerSemantic,
  nodePrimitive,
  semanticKeyword,
  semanticLabel,
} from './elementCatalog'

interface CatalogFixture {
  diagramType: string
  nodes: { id: string; data: { semanticType?: unknown } }[]
  edges: { id: string; data?: { semanticType?: unknown } }[]
}

// Exercise every committed backend answer key directly so catalog drift cannot be
// hidden by a small hand-authored frontend fixture.
const fixtureModules = import.meta.glob<CatalogFixture>(
  '../../../../backend/assets/blueprints/*/examples/answers/*/output.gp.json',
  { eager: true, import: 'default' },
)

describe('semantic element catalog', () => {
  it('mirrors the complete backend catalog without duplicate semantic types', () => {
    expect(ELEMENT_SPECS).toHaveLength(98)
    expect(Object.keys(ELEMENT_CATALOG)).toHaveLength(98)
    expect(new Set(ELEMENT_SPECS.map((spec) => spec.semanticType)).size).toBe(98)
    expect(ELEMENT_SPECS.filter((spec) => spec.kind === 'node')).toHaveLength(84)
    expect(ELEMENT_SPECS.filter((spec) => spec.kind === 'edge')).toHaveLength(14)
    expect(allowedNodeSpecs('custom')).toHaveLength(17)
    expect(allowedEdgeSpecs('custom')).toHaveLength(9)
  })

  it('resolves every semantic type in all 36 backend output fixtures and permits its diagram type', () => {
    const fixtures = Object.entries(fixtureModules)
    expect(fixtures).toHaveLength(36)

    for (const [path, diagram] of fixtures) {
      const allowedNodes = new Set(allowedNodeSpecs(diagram.diagramType).map((spec) => spec.semanticType))
      const allowedEdges = new Set(allowedEdgeSpecs(diagram.diagramType).map((spec) => spec.semanticType))

      for (const node of diagram.nodes) {
        const semanticType = node.data.semanticType
        expect(typeof semanticType, `${path}: node ${node.id} must have a semanticType`).toBe('string')
        if (typeof semanticType !== 'string') continue
        const spec = getElementSpec(semanticType)
        expect(spec, `${path}: unknown node semanticType ${semanticType}`).toBeDefined()
        expect(spec?.kind).toBe('node')
        expect(allowedNodes.has(semanticType), `${path}: ${semanticType} is invalid for ${diagram.diagramType}`).toBe(true)
        expect(spec?.validIn).toContain(diagram.diagramType)
      }

      for (const edge of diagram.edges) {
        const semanticType = edge.data?.semanticType
        expect(typeof semanticType, `${path}: edge ${edge.id} must have a semanticType`).toBe('string')
        if (typeof semanticType !== 'string') continue
        const spec = getElementSpec(semanticType)
        expect(spec, `${path}: unknown edge semanticType ${semanticType}`).toBeDefined()
        expect(spec?.kind).toBe('edge')
        expect(allowedEdges.has(semanticType), `${path}: ${semanticType} is invalid for ${diagram.diagramType}`).toBe(true)
        expect(spec?.validIn).toContain(diagram.diagramType)
      }
    }
  })

  it('uses exact core subsets and gives custom every authorable element', () => {
    expect(allowedNodeSpecs('activity_diagram')).toHaveLength(8)
    expect(allowedEdgeSpecs('activity_diagram')).toHaveLength(2)
    expect(allowedNodeSpecs('use_case_diagram')).toHaveLength(4)
    expect(allowedEdgeSpecs('use_case_diagram')).toHaveLength(5)
    expect(allowedNodeSpecs('bdd_diagram')).toHaveLength(2)
    expect(allowedEdgeSpecs('bdd_diagram')).toHaveLength(5)
    expect(allowedNodeSpecs('not-a-diagram')).toEqual([])
    expect(allowedEdgeSpecs('not-a-diagram')).toEqual([])

    expect(allowedNodeSpecs('custom').map((spec) => spec.semanticType)).toContain('initialNode')
    expect(allowedNodeSpecs('custom').map((spec) => spec.semanticType)).toContain('block')
    expect(allowedEdgeSpecs('custom').map((spec) => spec.semanticType)).toContain('controlFlow')
    expect(allowedNodeSpecs('custom').map((spec) => spec.semanticType)).not.toContain('proxyPort')
    expect(allowedNodeSpecs('custom').map((spec) => spec.semanticType)).not.toContain('callBehaviorAction')
  })

  it('keeps the backend custom-only vocabulary isolated from MVP subsets', () => {
    const customOnly = ELEMENT_SPECS.filter(
      (spec) => spec.validIn.length === 1 && spec.validIn[0] === 'custom',
    ).map((spec) => spec.semanticType)
    expect(customOnly).toEqual(['class', 'interface', 'component', 'package', 'requirement', 'realization'])

    for (const diagramType of ['activity_diagram', 'use_case_diagram', 'bdd_diagram']) {
      const semantics = new Set([
        ...allowedNodeSpecs(diagramType).map((spec) => spec.semanticType),
        ...allowedEdgeSpecs(diagramType).map((spec) => spec.semanticType),
      ])
      for (const semanticType of customOnly) expect(semantics.has(semanticType)).toBe(false)
    }
  })

  it('maps node primitives, containers, labels, and renderer keywords', () => {
    expect(nodePrimitive('initialNode')).toBe('initial')
    expect(nodePrimitive('flowFinalNode')).toBe('flow-final')
    expect(nodePrimitive('broadcastSignalAction')).toBe('send-signal')
    expect(nodePrimitive('acceptCallAction')).toBe('accept-event')
    expect(nodePrimitive('constraintBlock')).toBe('classifier-box')
    expect(nodePrimitive('proxyPort')).toBe('port')
    expect(nodePrimitive('association')).toBeUndefined()
    expect(nodePrimitive('missing')).toBeUndefined()

    expect(isContainerSemantic('activityPartition')).toBe(true)
    expect(isContainerSemantic('subject')).toBe(true)
    expect(isContainerSemantic('package')).toBe(true)
    expect(isContainerSemantic('block')).toBe(false)
    expect(canOwnSemantic('subject', 'useCase')).toBe(true)
    expect(canOwnSemantic('activityPartition', 'opaqueAction')).toBe(true)
    expect(canOwnSemantic('block', 'proxyPort')).toBe(true)
    expect(canOwnSemantic('port', 'proxyPort')).toBe(true)
    expect(canOwnSemantic('opaqueAction', 'inputPin')).toBe(true)
    expect(canOwnSemantic('expansionRegion', 'expansionNode')).toBe(true)
    expect(canOwnSemantic('expansionRegion', 'inputPin')).toBe(false)
    expect(canOwnSemantic('opaqueAction', 'expansionNode')).toBe(false)
    expect(canOwnSemantic('subject', 'proxyPort')).toBe(false)
    expect(canOwnSemantic('block', 'opaqueAction')).toBe(false)

    expect(semanticKeyword('constraintBlock')).toBe('constraint')
    expect(semanticKeyword('associationBlock')).toBe('block')
    expect(semanticKeyword('proxyPort')).toBe('proxy')
    expect(semanticKeyword('fullPort')).toBe('full')
    expect(semanticKeyword('class')).toBe('')

    expect(semanticLabel('activityFinalNode')).toBe('Activity Final Node')
    expect(semanticLabel('subject')).toBe('System Boundary')
    expect(semanticLabel('participantPropertyLink')).toBe('Participant Property Link')
    expect(semanticLabel('unknown_shape')).toBe('Unknown Shape')
  })

  it('looks up edge notation and marker facts through getElementSpec', () => {
    expect(getElementSpec('include')).toEqual(
      expect.objectContaining({
        kind: 'edge',
        notation: 'uml',
        dashed: true,
        targetMarker: 'arrow',
        sourceMarker: 'none',
        category: 'relationship',
      }),
    )
    expect(getElementSpec('generalization')).toEqual(
      expect.objectContaining({ kind: 'edge', dashed: false, targetMarker: 'triangle' }),
    )
    expect(getElementSpec('composition')).toEqual(
      expect.objectContaining({ kind: 'edge', dashed: false, targetMarker: 'diamond_filled' }),
    )
    expect(getElementSpec('containment')).toEqual(
      expect.objectContaining({ kind: 'edge', targetMarker: 'none', sourceMarker: 'crosshair' }),
    )
    expect(getElementSpec('commentLink')).toEqual(
      expect.objectContaining({ kind: 'edge', category: 'annotation', dashed: true, targetMarker: 'none' }),
    )
    expect(getElementSpec('missing')).toBeUndefined()
  })
})
