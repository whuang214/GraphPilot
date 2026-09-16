import type { GraphPilotDiagram, ValidationErrorDetail } from '@/types/diagram'

// Validation issues mapped to the canvas elements they concern, so the editor can
// outline the offending node/edge and flag it in the inspector.
// `general` collects issues not tied to a single element (e.g. `$.nodes` or `$`).
export interface ElementValidationIssue {
  message: string
  path: string | null
}

export interface ValidationMarkers {
  nodeIds: Set<string>
  edgeIds: Set<string>
  byNode: Record<string, ElementValidationIssue[]>
  byEdge: Record<string, ElementValidationIssue[]>
  general: ElementValidationIssue[]
}

// Parse a `$`-rooted JSON path (e.g. `$.nodes[2].data.label`) to the element it
// targets. Only the leading `nodes[i]` / `edges[i]` segment matters here.
function parseTarget(path: string | null): { kind: 'node' | 'edge'; index: number } | null {
  if (!path) return null
  const match = /^\$\.(nodes|edges)\[(\d+)\]/.exec(path)
  if (!match) return null
  return { kind: match[1] === 'nodes' ? 'node' : 'edge', index: Number(match[2]) }
}

export function mapValidationErrors(
  diagram: GraphPilotDiagram,
  errors: ValidationErrorDetail[],
): ValidationMarkers {
  const markers: ValidationMarkers = {
    nodeIds: new Set(),
    edgeIds: new Set(),
    byNode: {},
    byEdge: {},
    general: [],
  }
  for (const err of errors) {
    const target = parseTarget(err.path)
    const id =
      target?.kind === 'node'
        ? diagram.nodes[target.index]?.id
        : target?.kind === 'edge'
          ? diagram.edges[target.index]?.id
          : undefined
    const issue = { message: err.message, path: err.path }
    if (target?.kind === 'node' && id) {
      markers.nodeIds.add(id)
      ;(markers.byNode[id] ??= []).push(issue)
    } else if (target?.kind === 'edge' && id) {
      markers.edgeIds.add(id)
      ;(markers.byEdge[id] ??= []).push(issue)
    } else {
      markers.general.push(issue)
    }
  }
  return markers
}
