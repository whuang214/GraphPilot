import { createContext, useContext } from 'react'

// Shared with the custom node renderers so a node's label can be edited in place
// (double-click -> an in-shape input), instead of only via the inspector. The
// label still maps to the same canonical `data.label`, so the save round-trip is
// unchanged. `begin` opens the editor for a node, `commit` writes the new label,
// `cancel` closes without change.
export interface NodeLabelEditApi {
  editingId: string | null
  begin: (id: string) => void
  commit: (id: string, label: string) => void
  cancel: () => void
}

export const NodeLabelEditContext = createContext<NodeLabelEditApi | null>(null)

export function useNodeLabelEdit(): NodeLabelEditApi | null {
  return useContext(NodeLabelEditContext)
}
