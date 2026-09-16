import { afterEach, describe, expect, it, vi } from 'vitest'
import { DiagramApiError, listDiagrams, loadDiagram, renderDiagram, saveDiagram, validateDiagram } from './diagrams'
import type { GraphPilotDiagram } from '../types/diagram'

const diagram: GraphPilotDiagram = {
  schemaVersion: 'graphpilot.diagram.v1',
  kind: 'diagram',
  diagramType: 'activity_diagram',
  id: 'd',
  name: 'D',
  metadata: {},
  viewport: { x: 0, y: 0, zoom: 1 },
  nodes: [],
  edges: [],
}

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response)
}

describe('api/diagrams', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('loadDiagram returns the response body', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { diagramPath: '/p', diagram, revision: 'rev-1' }))
    const res = await loadDiagram('/p')
    expect(res.diagramPath).toBe('/p')
    expect(res.diagram.diagramType).toBe('activity_diagram')
  })

  it('loadDiagram throws a typed error on a non-OK response', async () => {
    vi.stubGlobal('fetch', mockFetch(404, { error: { code: 'not_found', message: 'nope', retryable: true } }))
    const err = await loadDiagram('/p').catch((e: unknown) => e)
    expect(err).toBeInstanceOf(DiagramApiError)
    expect((err as DiagramApiError).code).toBe('not_found')
    expect((err as DiagramApiError).retryable).toBe(true)
  })

  it('loadDiagram rejects a malformed non-OK envelope', async () => {
    vi.stubGlobal('fetch', mockFetch(404, { code: 'legacy_flat_error', message: 'nope' }))
    await expect(loadDiagram('/p')).rejects.toMatchObject({ code: 'invalid_response' })
  })

  it('loadDiagram rejects a malformed success payload before the editor renders it', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { diagramPath: '/p', diagram: {} }))
    const err = await loadDiagram('/p').catch((e: unknown) => e)
    expect(err).toBeInstanceOf(DiagramApiError)
    expect((err as DiagramApiError).code).toBe('invalid_response')
  })

  it('loadDiagram rejects malformed style fields before marker rendering', async () => {
    const malformed = {
      ...diagram,
      edges: [{ id: 'e', source: 'a', target: 'b', style: { stroke: 1 } }],
    }
    vi.stubGlobal('fetch', mockFetch(200, { diagramPath: '/p', diagram: malformed, revision: 'rev-1' }))
    await expect(loadDiagram('/p')).rejects.toMatchObject({ code: 'invalid_response' })
  })

  it('loadDiagram rejects malformed canonical route geometry', async () => {
    const malformed = {
      ...diagram,
      edges: [{ id: 'e', source: 'a', target: 'b', route: { sourceAnchor: { side: 'right', offset: 2 } } }],
    }
    vi.stubGlobal('fetch', mockFetch(200, { diagramPath: '/p', diagram: malformed, revision: 'rev-1' }))
    await expect(loadDiagram('/p')).rejects.toMatchObject({ code: 'invalid_response' })
  })

  it('saveDiagram returns the saved response incl. render-on-save svgPath', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { saved: true, diagramPath: '/p', diagram, revision: 'rev-2', svgPath: '/x/order.svg' }))
    const res = await saveDiagram('/p', diagram)
    expect(res.saved).toBe(true)
    expect(res.svgPath).toBe('/x/order.svg')
  })

  it('saveDiagram accepts a nonfatal OperationProblem warning', async () => {
    const warning = {
      code: 'render_failed',
      message: 'saved without SVG',
      retryable: true,
      details: { diagramPath: '/p', intendedSvgPath: '/p.svg' },
    }
    vi.stubGlobal(
      'fetch',
      mockFetch(200, { saved: true, diagramPath: '/p', diagram, revision: 'rev-2', warning }),
    )
    await expect(saveDiagram('/p', diagram)).resolves.toMatchObject({ warning })
  })

  it('saveDiagram surfaces blocking validation errors on 422', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch(422, {
        error: {
          code: 'validation_failed',
          message: 'bad',
          retryable: true,
          details: { issues: [{ code: 'no_nodes', message: 'needs nodes', path: null }] },
        },
      }),
    )
    const err = await saveDiagram('/p', diagram).catch((e: unknown) => e)
    expect(err).toBeInstanceOf(DiagramApiError)
    expect((err as DiagramApiError).validationErrors).toHaveLength(1)
  })

  it('listDiagrams returns the diagrams array', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { diagrams: [{ name: 'a', path: '/a' }] }))
    expect(await listDiagrams('/p')).toEqual([{ name: 'a', path: '/a' }])
  })

  it('listDiagrams rejects malformed entries instead of silently hiding them', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { diagrams: [{ name: 'a' }] }))
    await expect(listDiagrams('/p')).rejects.toMatchObject({ code: 'invalid_response' })
  })

  it('validateDiagram returns the result + normalized diagram', async () => {
    const validationErrors = [{ code: 'no_nodes', message: 'needs nodes', path: '$.nodes' }]
    vi.stubGlobal('fetch', mockFetch(200, { valid: false, validationErrors, diagram }))
    const res = await validateDiagram(diagram)
    expect(res.valid).toBe(false)
    expect(res.validationErrors).toEqual(validationErrors)
    expect(res.diagram.id).toBe('d')
  })

  it('validateDiagram rejects malformed validation errors', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { valid: false, validationErrors: [{ code: 'no_nodes' }], diagram }))
    await expect(validateDiagram(diagram)).rejects.toMatchObject({ code: 'invalid_response' })
  })

  it('renderDiagram returns the svg string', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { svg: '<?xml version="1.0"?><svg></svg>' }))
    const svg = await renderDiagram(diagram)
    expect(svg).toContain('<svg></svg>')
  })

  it('renderDiagram rejects a malformed success payload instead of returning an empty image', async () => {
    vi.stubGlobal('fetch', mockFetch(200, {}))
    const err = await renderDiagram(diagram).catch((e: unknown) => e)
    expect(err).toBeInstanceOf(DiagramApiError)
    expect((err as DiagramApiError).code).toBe('invalid_response')
  })

  it('renderDiagram throws a typed error on a non-OK response', async () => {
    vi.stubGlobal('fetch', mockFetch(422, { error: { code: 'render_failed', message: 'bad', retryable: true } }))
    const err = await renderDiagram(diagram).catch((e: unknown) => e)
    expect(err).toBeInstanceOf(DiagramApiError)
    expect((err as DiagramApiError).code).toBe('render_failed')
  })
})
