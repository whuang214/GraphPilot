import { describe, expect, it } from 'vitest'
import type { Node } from '@xyflow/react'
import type { ModelFeatures } from '@/types/diagram'
import { featureBlockMinHeight } from './bddCompartments'
import { applyNodePatch } from './nodePatch'

const node: Node = {
  id: 'n1',
  type: 'gpNode',
  position: { x: 0, y: 0 },
  data: {
    label: 'Old',
    semanticType: 'opaqueAction',
    description: 'Keep me',
    gpStyle: { background: '#ffffff' },
  },
  style: { width: 100, height: 50 },
}

const classifierFeatures: ModelFeatures = {
  properties: [{ kind: 'part', name: 'engine', type: 'Engine' }],
  operations: [{ name: 'start', isQuery: false }],
}

const classifier: Node = {
  id: 'c1',
  type: 'gpNode',
  position: { x: 0, y: 0 },
  data: {
    label: 'Vehicle',
    semanticType: 'block',
    description: 'A system block',
    features: classifierFeatures,
    appliedStereotypes: [{ name: 'domain', properties: { owner: 'systems' } }],
    gpStyle: { borderColor: '#333333' },
  },
  style: { width: 180, height: 90 },
}

describe('applyNodePatch', () => {
  it('routes size to style and visual style to data.gpStyle', () => {
    const out = applyNodePatch(node, { width: 200, background: '#dbeafe', borderColor: '#2563eb' })
    expect(out.style).toMatchObject({ width: 200, height: 50 })
    expect((out.data?.gpStyle as Record<string, unknown>)).toMatchObject({
      background: '#dbeafe',
      borderColor: '#2563eb',
    })
  })

  it('applies label, semanticType, and generic structured data without dropping other data', () => {
    const port = { type: 'Telemetry', side: 'right' as const, isConjugated: true }
    const out = applyNodePatch(node, {
      label: 'New',
      semanticType: 'proxyPort',
      data: { port },
    })

    expect(out.data).toMatchObject({
      label: 'New',
      semanticType: 'proxyPort',
      description: 'Keep me',
      port,
    })
  })

  it('deletes every requested canonical data key generically', () => {
    const out = applyNodePatch(classifier, { clearData: ['description', 'appliedStereotypes'] })
    expect(out.data?.description).toBeUndefined()
    expect(out.data?.appliedStereotypes).toBeUndefined()
    expect(out.data?.features).toEqual(classifierFeatures)
  })

  it('auto-fits classifier-box height when structured features change', () => {
    const features: ModelFeatures = {
      ...classifierFeatures,
      receptions: ['temperatureChanged', 'pressureChanged'],
      constraints: [{ name: 'safe', expression: 'pressure < limit' }],
    }
    const out = applyNodePatch(classifier, { data: { features } })

    expect(out.style?.height).toBe(featureBlockMinHeight(features))
    expect(out.data?.features).toEqual(features)
  })

  it('does not auto-fit a non-classifier when a stray features patch is applied', () => {
    const out = applyNodePatch(node, { data: { features: classifierFeatures } })
    expect(out.style?.height).toBe(50)
  })

  it('returns new containers and never mutates input styles or structured data', () => {
    const originalFeatures = classifier.data?.features
    const originalGpStyle = classifier.data?.gpStyle as Record<string, unknown>
    const nextFeatures: ModelFeatures = {
      ...classifierFeatures,
      properties: [...(classifierFeatures.properties ?? []), { kind: 'value', name: 'mass', type: 'Real' }],
    }
    const out = applyNodePatch(classifier, { color: '#111111', data: { features: nextFeatures } })

    expect(out).not.toBe(classifier)
    expect(out.data).not.toBe(classifier.data)
    expect(out.style).not.toBe(classifier.style)
    expect(out.data?.features).not.toBe(originalFeatures)
    expect(originalFeatures).toEqual(classifierFeatures)
    expect(originalGpStyle.color).toBeUndefined()
  })
})
