import { useCallback, useRef, useState } from 'react'
import type { Edge, Node } from '@xyflow/react'

interface Snapshot {
  nodes: Node[]
  edges: Edge[]
}

const MAX = 50

// History stack over React Flow nodes/edges. `takeSnapshot()` is called *before*
// a mutation (drag start, connect, drop, delete, property-edit session, ...); undo
// swaps current state with the previous snapshot, redo reverses it. Current state
// is read via refs so the callbacks stay stable.
export function useUndoRedo(
  nodes: Node[],
  edges: Edge[],
  setNodes: (n: Node[]) => void,
  setEdges: (e: Edge[]) => void,
) {
  const [past, setPast] = useState<Snapshot[]>([])
  const [future, setFuture] = useState<Snapshot[]>([])

  // Current values are mirrored into refs so the callbacks stay stable AND so undo/
  // redo can read the live stacks without nesting setState calls inside another
  // updater (an impurity React's StrictMode double-invoke would otherwise duplicate).
  const nodesRef = useRef(nodes)
  nodesRef.current = nodes
  const edgesRef = useRef(edges)
  edgesRef.current = edges
  const pastRef = useRef(past)
  pastRef.current = past
  const futureRef = useRef(future)
  futureRef.current = future

  const takeSnapshot = useCallback(() => {
    setPast((p) => [...p, { nodes: nodesRef.current, edges: edgesRef.current }].slice(-MAX))
    setFuture([])
  }, [])

  const undo = useCallback(() => {
    const p = pastRef.current
    if (p.length === 0) return
    const prev = p[p.length - 1]
    setFuture((f) => [{ nodes: nodesRef.current, edges: edgesRef.current }, ...f].slice(0, MAX))
    setPast((pp) => pp.slice(0, -1))
    setNodes(prev.nodes)
    setEdges(prev.edges)
  }, [setNodes, setEdges])

  const redo = useCallback(() => {
    const f = futureRef.current
    if (f.length === 0) return
    const next = f[0]
    setPast((p) => [...p, { nodes: nodesRef.current, edges: edgesRef.current }].slice(-MAX))
    setFuture((ff) => ff.slice(1))
    setNodes(next.nodes)
    setEdges(next.edges)
  }, [setNodes, setEdges])

  return { takeSnapshot, undo, redo, canUndo: past.length > 0, canRedo: future.length > 0 }
}
