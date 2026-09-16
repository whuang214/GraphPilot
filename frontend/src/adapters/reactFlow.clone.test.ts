import { describe, expect, it } from 'vitest'
import type { GraphPilotDiagram } from '../types/diagram'
import { graphPilotToReactFlow, reactFlowToGraphPilot } from './reactFlow'
import { cloneSelectedElements } from '@/editor/lib/clone'

// Reuse the committed example diagrams (same glob as reactFlow.test.ts) so the
// clone path is exercised against real fixtures.
const sampleModules = import.meta.glob<GraphPilotDiagram>(
  '../../../backend/assets/blueprints/*/examples/*/*/output.gp.json',
  { eager: true, import: 'default' },
)

const fixtures: [string, GraphPilotDiagram][] = Object.entries(sampleModules)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([path, diagram]) => {
    const match = path.match(/blueprints\/(.+)\/output\.gp\.json$/)
    return [match ? match[1] : path, diagram] as [string, GraphPilotDiagram]
  })

const sig = (type: string, semanticType: string | undefined) => `${type}|${semanticType ?? ''}`

describe('cloneSelectedElements + reverse adapter (Ctrl+D / paste)', () => {
  it.each(fixtures)('%s: cloning the whole selection round-trips to canonical JSON', (_label, diagram) => {
    const rf = graphPilotToReactFlow(diagram)
    // Select everything, then clone.
    const selected = rf.nodes.map((n) => ({ ...n, selected: true }))
    const cloned = cloneSelectedElements(selected, rf.edges)

    // Every selected node is cloned with a fresh id; same for fully-internal edges.
    expect(cloned.nodes.length).toBe(diagram.nodes.length)
    expect(cloned.edges.length).toBe(diagram.edges.length)

    const result = reactFlowToGraphPilot(diagram, [...selected, ...cloned.nodes], [...rf.edges, ...cloned.edges])

    // Originals + clones are both present.
    expect(result.nodes.length).toBe(diagram.nodes.length * 2)
    expect(result.edges.length).toBe(diagram.edges.length * 2)

    // Clones carry new ids (not present in the original diagram).
    const originalIds = new Set(diagram.nodes.map((n) => n.id))
    const clonedOut = result.nodes.filter((n) => !originalIds.has(n.id))
    expect(clonedOut.length).toBe(diagram.nodes.length)

    // Clones preserve node.type + data.semanticType (the reverse adapter recovers
    // them from the node's own state for ids with no original entry).
    const originalSigs = diagram.nodes.map((n) => sig(n.type, n.data?.semanticType)).sort()
    const clonedSigs = clonedOut.map((n) => sig(n.type, n.data?.semanticType)).sort()
    expect(clonedSigs).toEqual(originalSigs)

    // No React Flow runtime/session field leaks through the clone path.
    const json = JSON.stringify(result)
    for (const key of ['selected', 'dragging', 'measured', 'positionAbsolute']) {
      expect(json).not.toContain(`"${key}"`)
    }
  })
})
