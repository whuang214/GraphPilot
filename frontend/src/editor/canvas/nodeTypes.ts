import { memo } from 'react'
import type { NodeTypes } from '@xyflow/react'
import { GpNode } from './customNodes'

// React Flow node-type registry. A single universal `gpNode` renderer branches
// internally on `data.semanticType` (the old per-type
// activityNode / useCaseNode / bddNode families were removed). Wrapped in memo() so one
// node's change (or any unrelated canvas update) doesn't re-render every node.
export const nodeTypes: NodeTypes = {
  gpNode: memo(GpNode),
}
