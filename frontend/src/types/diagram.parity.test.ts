/// <reference types="node" />
// Schema/type parity guard.
//
// Asserts that the canonical required fields declared in `diagram.ts`
// (CANONICAL_REQUIRED_FIELDS) stay in lockstep with the backend source of truth,
// `backend/assets/schemas/diagram.json`. The compile-time half of the guard
// lives in `diagram.ts` (a `satisfies` clause tying the manifest to the interfaces);
// this runtime half fails `npm run test`/`verify` if the schema and the manifest drift.
//
// The schema is read via `node:fs` (not a module import) so no bundler fs-allow rule
// or `resolveJsonModule` is needed to reach outside the frontend project.
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { CANONICAL_REQUIRED_FIELDS, CANONICAL_SCHEMA_RULES, isGraphPilotDiagram } from './diagram'

const schemaPath = fileURLToPath(
  new URL('../../../backend/assets/schemas/diagram.json', import.meta.url),
)
const schema = JSON.parse(readFileSync(schemaPath, 'utf-8'))

const sorted = (values: readonly string[]) => [...values].sort()

describe('diagram.json <-> diagram.ts parity', () => {
  it('top-level required fields match the schema', () => {
    expect(sorted(CANONICAL_REQUIRED_FIELDS.diagram)).toEqual(sorted(schema.required))
  })

  it('node required fields match the schema', () => {
    expect(sorted(CANONICAL_REQUIRED_FIELDS.node)).toEqual(sorted(schema.$defs.node.required))
  })

  it('node.data required fields match the schema', () => {
    expect(sorted(CANONICAL_REQUIRED_FIELDS.nodeData)).toEqual(
      sorted(schema.$defs.node.properties.data.required),
    )
  })

  it('edge required fields match the schema', () => {
    expect(sorted(CANONICAL_REQUIRED_FIELDS.edge)).toEqual(sorted(schema.$defs.edge.required))
  })

  it('viewport required fields match the schema', () => {
    expect(sorted(CANONICAL_REQUIRED_FIELDS.viewport)).toEqual(
      sorted(schema.properties.viewport.required),
    )
  })

  it('schema-rule allowlist matches the canonical origin schema', () => {
    expect(sorted(CANONICAL_SCHEMA_RULES)).toEqual(
      sorted(schema.$defs.elementOrigin.properties.schemaRules.items.enum),
    )
  })

  it('the schema still enumerates the supported diagram types', () => {
    // Not tied to a TS type (the UI treats diagramType as an open string), but a cheap
    // guard that the enum exists and is non-empty so the manifest check stays meaningful.
    expect(Array.isArray(schema.properties.diagramType.enum)).toBe(true)
    expect(schema.properties.diagramType.enum.length).toBeGreaterThan(0)
  })

  it('accepts inline evidence and strict element origins', () => {
    const diagram = {
      schemaVersion: 'graphpilot.diagram.v1',
      kind: 'diagram',
      diagramType: 'activity_diagram',
      id: 'diagram-test',
      name: 'Test',
      metadata: {
        authority: 'as_implemented',
        evidence: [{
          id: 'ev-submit',
          kind: 'code',
          locator: { path: 'src/orders/submit.py', symbol: 'submit', lineRange: { start: 1, end: 20 } },
          contentDigest: `sha256:${'1'.repeat(64)}`,
          summary: 'submit validates and then persists the order.',
        }],
      },
      viewport: { x: 0, y: 0, zoom: 1 },
      nodes: [{
        id: 'start',
        type: 'gpNode',
        position: { x: 0, y: 0 },
        data: { label: 'Initial', semanticType: 'initialNode' },
        origin: {
          assurance: 'grounded',
          evidenceRefs: ['ev-submit'],
          assumptionRefs: [],
          schemaRules: ['activity.initial-node'],
          rationale: 'The cited region establishes the entry point.',
        },
      }],
      edges: [],
    }

    expect(isGraphPilotDiagram(diagram)).toBe(true)
  })

  it('accepts canonical route modes and rejects invalid straight geometry', () => {
    const base = {
      schemaVersion: 'graphpilot.diagram.v1',
      kind: 'diagram',
      diagramType: 'use_case_diagram',
      id: 'diagram-route',
      name: 'Route',
      metadata: {},
      viewport: { x: 0, y: 0, zoom: 1 },
      nodes: [
        { id: 'a', type: 'gpNode', position: { x: 0, y: 0 }, data: { label: 'A' } },
        { id: 'b', type: 'gpNode', position: { x: 200, y: 100 }, data: { label: 'B' } },
      ],
      edges: [{ id: 'edge', source: 'a', target: 'b', route: { mode: 'straight' } }],
    }
    expect(isGraphPilotDiagram(base)).toBe(true)
    expect(isGraphPilotDiagram({
      ...base,
      edges: [{ ...base.edges[0], route: { mode: 'curved' } }],
    })).toBe(false)
    expect(isGraphPilotDiagram({
      ...base,
      edges: [{ ...base.edges[0], route: { mode: 'straight', waypoints: [{ x: 10, y: 20 }] } }],
    })).toBe(false)
  })

  it('rejects a malformed origin and an assurance nothing backs', () => {
    const base = {
      schemaVersion: 'graphpilot.diagram.v1',
      kind: 'diagram',
      diagramType: 'activity_diagram',
      id: 'diagram-test',
      name: 'Test',
      metadata: {},
      viewport: { x: 0, y: 0, zoom: 1 },
      nodes: [{ id: 'start', type: 'gpNode', position: { x: 0, y: 0 }, data: { label: 'Start' } }],
      edges: [],
    }
    const origin = {
      assurance: 'grounded',
      evidenceRefs: ['ev-a'],
      assumptionRefs: [],
      schemaRules: [],
      rationale: 'Backed by the cited region.',
    }

    expect(isGraphPilotDiagram({
      ...base,
      nodes: [{ ...base.nodes[0], origin: { evidenceRefs: [], rationale: '' } }],
    })).toBe(false)
    // grounded without evidence, and assumed without an assumption.
    expect(isGraphPilotDiagram({
      ...base,
      nodes: [{ ...base.nodes[0], origin: { ...origin, evidenceRefs: [] } }],
    })).toBe(false)
    expect(isGraphPilotDiagram({
      ...base,
      nodes: [{ ...base.nodes[0], origin: { ...origin, assurance: 'assumed', evidenceRefs: [] } }],
    })).toBe(false)
  })

  it('requires authority and inline evidence to agree', () => {
    const base = {
      schemaVersion: 'graphpilot.diagram.v1',
      kind: 'diagram',
      diagramType: 'activity_diagram',
      id: 'diagram-test',
      name: 'Test',
      metadata: {},
      viewport: { x: 0, y: 0, zoom: 1 },
      nodes: [{ id: 'start', type: 'gpNode', position: { x: 0, y: 0 }, data: { label: 'Start' } }],
      edges: [],
    }
    const evidence = [{
      id: 'ev-a',
      kind: 'code',
      locator: { path: 'src/a.py', lineRange: { start: 1, end: 2 } },
      contentDigest: `sha256:${'1'.repeat(64)}`,
      summary: 'Something.',
    }]

    // as_implemented must cite; conceptual must not; evidence needs an authority.
    expect(isGraphPilotDiagram({ ...base, metadata: { authority: 'as_implemented' } })).toBe(false)
    expect(isGraphPilotDiagram({ ...base, metadata: { authority: 'conceptual', evidence } })).toBe(false)
    expect(isGraphPilotDiagram({ ...base, metadata: { evidence } })).toBe(false)
    expect(isGraphPilotDiagram({ ...base, metadata: { authority: 'conceptual' } })).toBe(true)
  })
})
