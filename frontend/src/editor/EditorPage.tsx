import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { CSSProperties, DragEvent, MouseEvent as ReactMouseEvent, ReactNode } from 'react'
import {
  Background,
  ConnectionMode,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  reconnectEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react'
import type { Connection, ConnectionLineComponentProps, Edge, EdgeTypes, InternalNode, Node, NodeChange, OnConnectEnd, OnConnectStart } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { DiagramApiError, loadDiagram, renderDiagram, saveDiagram, validateDiagram } from '@/api/diagrams'
import { edgeMarkers, graphPilotToReactFlow, reactFlowToGraphPilot } from '@/adapters/reactFlow'
import type { GraphPilotDiagram, GraphPilotEdgeData, ValidationErrorDetail } from '@/types/diagram'
import { nodeTypes } from '@/editor/canvas/nodeTypes'
import { FloatingEdge } from '@/editor/canvas/FloatingEdge'
import { CANVAS_LAYER, decorateNodeLayer, reparentNode } from '@/editor/lib/containment'
import { NodePalette } from '@/editor/components/NodePalette'
import { DEFAULT_NODE_STYLE, DRAG_MIME, defaultNodeSize, defaultRouteMode, newNodeId } from '@/editor/lib/palette'
import type { PaletteItem } from '@/editor/lib/palette'
import { canOwnSemantic, getElementSpec, isContainerSemantic, nodePrimitive } from '@/editor/lib/elementCatalog'
import { PropertyPanel } from '@/editor/components/PropertyPanel'
import type { EdgePatch, NodePatch, PanelSelection } from '@/editor/components/PropertyPanel'
import { Button, cn, Modal, useToast } from '@/ui'
import { Home } from '@/editor/components/Home'
import { TopBar } from './shell/TopBar'
import { StatusBar } from './shell/StatusBar'
import { Rail } from './shell/Rail'
import { useRail } from './shell/useRail'
import { addRecent, clearRecents, getRecents } from '@/editor/lib/recents'
import { useColorMode } from './shell/useColorMode'
import { ZoomStatus } from './canvas/ZoomStatus'
import { EmptyOverlay } from './canvas/EmptyOverlay'
import { miniMapNodeColor } from './canvas/miniMap'
import { useUndoRedo } from '@/editor/hooks/useUndoRedo'
import { cloneSelectedElements } from '@/editor/lib/clone'
import { Toolbar } from '@/editor/components/Toolbar'
import { ShortcutsHelp } from '@/editor/components/ShortcutsHelp'
import { ExportMenu } from '@/editor/components/ExportMenu'
import { ToolbarMore, type ToolbarMoreItem } from '@/editor/components/ToolbarMore'
import { downloadPng, downloadSvg } from '@/editor/lib/exportImage'
import { applyNodeResize, NodeResizeContext } from '@/editor/lib/resize'
import type { NodeResizeApi } from '@/editor/lib/resize'
import { NodeLabelEditContext } from '@/editor/lib/inlineLabel'
import type { NodeLabelEditApi } from '@/editor/lib/inlineLabel'
import { applyNodePatch } from '@/editor/lib/nodePatch'
import { mapValidationErrors } from '@/editor/lib/validation'
import type { ValidationMarkers } from '@/editor/lib/validation'
import { getHelperLines } from '@/editor/lib/alignmentGuides'
import { HelperLines } from '@/editor/canvas/HelperLines'
import { diffLines, diffStats } from '@/editor/lib/jsonDiff'
import { JsonDiffView } from '@/editor/components/JsonDiffView'
import { EditorColorModeContext } from '@/editor/hooks/editorColorMode'
import {
  isFileSystemAccessSupported,
  openDroppedDiagram,
  openLocalDiagram,
  readHandleDiagram,
  saveAsLocalDiagram,
  writeHandle,
} from '@/editor/lib/fileSystem'
import type { LocalDiagramResult, LocalFileHandle } from '@/editor/lib/fileSystem'
import { EdgeRouteEditContext } from '@/editor/lib/edgeRouteEdit'
import { applyRelationshipSemantic, defaultRelationshipSemantic } from '@/editor/lib/relationshipPresets'
import { fanOutAnchors, normalizeRouteGeometry, reconnectRouteGeometry, resolveAttachmentAnchor, reverseRouteGeometry, setRouteMode, translateRouteWaypoints } from '@/editor/lib/edgeRouting'
import type { NodeRect, RouteAnchor, RouteGeometry, RouteMode } from '@/editor/lib/edgeRouting'
import { featureBlockMinHeight } from '@/editor/lib/bddCompartments'
import { createBlankDiagram } from '@/editor/lib/diagramFactory'
import type { CatalogDiagramType } from '@/editor/lib/elementCatalog'

// Custom edge-end markers that React Flow's built-in MarkerType set does not
// provide: generalization triangles, association-end diamonds, and containment
// crosshairs. Referenced by id via `markerStart` / `markerEnd` URLs.
function EdgeMarkerDefs() {
  return (
    <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden>
      <defs>
        <marker
          id="gp-generalization"
          markerWidth="16"
          markerHeight="16"
          refX="14"
          refY="5"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          {/* Hollow generalization triangle: fill tracks the surface so it reads hollow
              on the canvas, outline tracks the edge colour. Set via `style` (not the
              fill/stroke attributes) so the CSS vars resolve and dark mode lightens it. */}
          <path d="M1,1 L14,5 L1,9 z" style={{ fill: 'var(--surface)', stroke: 'context-stroke' }} strokeWidth="1" />
        </marker>
        <marker
          id="gp-composition"
          markerWidth="18"
          markerHeight="14"
          refX="16"
          refY="5"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          {/* Solid composition diamond: fill + outline track the edge colour. Set via
              `style` so the CSS var resolves and dark mode lightens it. */}
          <path d="M1,5 L8,1 L16,5 L8,9 z" style={{ fill: 'context-stroke', stroke: 'context-stroke' }} strokeWidth="1" />
        </marker>
        <marker
          id="gp-aggregation"
          markerWidth="18"
          markerHeight="14"
          refX="16"
          refY="5"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          {/* Hollow aggregation diamond: fill tracks the surface so it reads hollow,
              outline tracks the edge colour (mirrors the composition diamond). */}
          <path d="M1,5 L8,1 L16,5 L8,9 z" style={{ fill: 'var(--surface)', stroke: 'context-stroke' }} strokeWidth="1" />
        </marker>
        <marker
          id="gp-crosshair"
          markerWidth="16"
          markerHeight="16"
          refX="8"
          refY="8"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          <circle cx="8" cy="8" r="4" style={{ fill: 'var(--surface)', stroke: 'context-stroke' }} strokeWidth="1" />
          <path d="M4,8 H12 M8,4 V12" style={{ fill: 'none', stroke: 'context-stroke' }} strokeWidth="1" />
        </marker>
      </defs>
    </svg>
  )
}

type DiagramSource =
  | { kind: 'workspace'; path: string; revision: string }
  | { kind: 'external-file'; name: string; handle: LocalFileHandle; revision: string }
  | { kind: 'read-only-file'; name: string }
  | { kind: 'unsaved'; name: string }

type DiagramSession = {
  source: DiagramSource
  diagram: GraphPilotDiagram
  // Monotonic id bumped on every successful open; used as the canvas `key` so a
  // new open always remounts (even a same-named file or a re-open of the same path).
  loadId: number
}

function sameDiagramSource(left: DiagramSource, right: DiagramSource): boolean {
  if (left.kind !== right.kind) return false
  if (left.kind === 'workspace' && right.kind === 'workspace') return left.path === right.path
  if (left.kind === 'external-file' && right.kind === 'external-file') return left.handle === right.handle
  if (left.kind === 'read-only-file' && right.kind === 'read-only-file') return left.name === right.name
  return left.kind === 'unsaved' && right.kind === 'unsaved' && left.name === right.name
}

function sameDiagramRevision(left: DiagramSource, right: DiagramSource): boolean {
  if (!sameDiagramSource(left, right)) return false
  if (left.kind === 'workspace' && right.kind === 'workspace') return left.revision === right.revision
  if (left.kind === 'external-file' && right.kind === 'external-file') return left.revision === right.revision
  return true
}

type EditorState =
  | { status: 'missing-path' }
  | { status: 'loading' }
  | { status: 'error'; code: string; message: string }
  | { status: 'loaded'; session: DiagramSession }

type SaveState =
  | { status: 'idle' }
  | { status: 'saving' }
  | { status: 'saved' }
  | { status: 'error'; code: string; message: string; validationErrors?: ValidationErrorDetail[] }

function Message({ title, body, children }: { title: string; body?: string; children?: ReactNode }) {
  return (
    <main className="p-6">
      <h2 className="mb-2 text-xl font-semibold text-fg">{title}</h2>
      {body ? <p className="m-0 text-fg-muted">{body}</p> : null}
      {children}
    </main>
  )
}

// Tracks the viewport width so the top bar can collapse its actions into a "⋯"
// menu when the window is narrow.
function useWindowWidth(): number {
  const [width, setWidth] = useState(() => (typeof window === 'undefined' ? 1024 : window.innerWidth))
  useEffect(() => {
    const onResize = () => setWidth(window.innerWidth)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])
  return width
}

function newEdgeId(source: string, target: string): string {
  return `edge_${source}_${target}_${crypto.randomUUID()}`
}

function pointerClientPosition(event: MouseEvent | TouchEvent | ReactMouseEvent): { x: number; y: number } | undefined {
  if ('clientX' in event) return { x: event.clientX, y: event.clientY }
  const touch = event.changedTouches[0] ?? event.touches[0]
  return touch ? { x: touch.clientX, y: touch.clientY } : undefined
}

function internalNodeRect(node: InternalNode): NodeRect {
  const position = node.internals.positionAbsolute
  const style = node.style as CSSProperties | undefined
  const number = (value: unknown) => typeof value === 'number' && Number.isFinite(value) ? value : undefined
  const semanticType = (node.data as { semanticType?: string } | undefined)?.semanticType
  const fallback = defaultNodeSize(semanticType ?? '')
  return {
    x: position.x,
    y: position.y,
    w: node.measured?.width ?? number(node.width) ?? number(style?.width) ?? fallback.width,
    h: node.measured?.height ?? number(node.height) ?? number(style?.height) ?? fallback.height,
    primitive: nodePrimitive(semanticType),
    label: typeof node.data.label === 'string' ? node.data.label : undefined,
  }
}

// Default marker colour for any edge marker that doesn't set its own, so markers
// match the edge stroke instead of React Flow's light-grey default. Uses the theme's
// strong-line token (light: #333333, matching the canonical sample stroke; dark: a
// lighter slate so edges/arrows stay visible on the dark canvas).
const EDGE_COLOR = 'var(--line-strong)'

// Render every edge as a floating edge (anchored to the nearest node sides by
// geometry, like the server SVG) by overriding the built-in `default` edge type.
// No runtime `type` is set on edges, so the save round-trip stays byte-stable.
// memo() so an edge only re-renders when its own props change (one instance/edge).
const edgeTypes: EdgeTypes = { default: memo(FloatingEdge) }

// Stable array reference for React Flow's delete-key binding (a new literal each
// render would re-run its keybinding effect).
const DELETE_KEY_CODES = ['Delete', 'Backspace']

function SaveBanner({ saveState }: { saveState: SaveState }) {
  if (saveState.status === 'saved') {
    return <div className="bg-success-bg px-4 py-1.5 text-success">Saved.</div>
  }
  if (saveState.status === 'error') {
    return (
      <div className="bg-danger-bg px-4 py-1.5 text-danger">
        <strong>[{saveState.code}]</strong> {saveState.message}
        {saveState.validationErrors?.length ? (
          <ul className="mt-1 list-disc pl-5">
            {saveState.validationErrors.map((issue) => (
              <li key={`${issue.code}:${issue.path ?? ''}:${issue.message}`}>
                {issue.message}
                {issue.path ? <span className="text-fg-subtle"> ({issue.path})</span> : null}
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    )
  }
  return null
}

function DiagramCanvas({
  session,
  onHome,
  onOpenLocal,
  onOpenDroppedResult,
  onSessionChange,
  onSessionReload,
}: {
  session: DiagramSession
  onHome: () => void
  onOpenLocal: () => void
  onOpenDroppedResult: (res: LocalDiagramResult) => void
  onSessionChange: (source: DiagramSource, diagram: GraphPilotDiagram, expectedSource: DiagramSource, expectedLoadId: number) => void
  onSessionReload: (source: DiagramSource, diagram: GraphPilotDiagram, force?: boolean) => void
}) {
  const { source, diagram: initialDiagram } = session
  const initial = useMemo(() => graphPilotToReactFlow(initialDiagram), [initialDiagram])
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges)
  const [relationshipSemantic, setRelationshipSemantic] = useState(() => defaultRelationshipSemantic(initialDiagram.diagramType))
  const [nextRouteMode, setNextRouteMode] = useState<RouteMode>(() => defaultRouteMode(initialDiagram.diagramType))
  const [baseDiagram, setBaseDiagram] = useState(initialDiagram)
  const [externalChange, setExternalChange] = useState<{ diagram: GraphPilotDiagram; source: DiagramSource } | null>(null)
  const [externalReviewOpen, setExternalReviewOpen] = useState(false)
  const [selection, setSelection] = useState<{ kind: 'node' | 'edge'; id: string } | null>(null)
  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([])
  // Editable diagram name. Seeded from the loaded diagram;
  // re-seeded on every open since the canvas remounts per `loadId`.
  const [name, setName] = useState(initialDiagram.name)
  // Inline validation markers: set by the Validate action,
  // cleared on the next edit so they never go stale.
  const [validationMarkers, setValidationMarkers] = useState<ValidationMarkers | null>(null)
  const [dirty, setDirty] = useState(false)
  const [saveState, setSaveState] = useState<SaveState>({ status: 'idle' })
  const { screenToFlowPosition, getIntersectingNodes, getInternalNode, getZoom } = useReactFlow()
  const { notify } = useToast()
  const [confirmState, setConfirmState] = useState<{
    message: string
    confirmLabel: string
    onConfirm: () => void
  } | null>(null)
  const [autosave, setAutosave] = useState<boolean>(() => {
    try {
      return localStorage.getItem('gp.autosave') === '1'
    } catch {
      return false
    }
  })
  // A writable local source carries a File System Access handle. A dropped or new
  // document remains read-only/unsaved until Save As obtains a handle.
  const requiresSaveAs = source.kind === 'read-only-file' || source.kind === 'unsaved'
  const fsaSupported = isFileSystemAccessSupported()
  // Bumped on every edit. Lets a completed save tell whether the user edited
  // while the request was in flight (so it must not clear the dirty flag).
  const editGenRef = useRef(0)

  const markEdited = useCallback(() => {
    editGenRef.current += 1
    setDirty(true)
    // Clear a stale "Saved."/error banner once the user edits again, but never
    // interrupt an in-flight save (leave 'saving' untouched).
    setSaveState((s) => (s.status === 'saved' || s.status === 'error' ? { status: 'idle' } : s))
    // Validation markers reflect the diagram at validate time; drop them on edit.
    setValidationMarkers(null)
  }, [])

  const { takeSnapshot, undo: restoreUndo, redo: restoreRedo, canUndo, canRedo } = useUndoRedo(nodes, edges, setNodes, setEdges)
  const undo = useCallback(() => {
    if (!canUndo) return
    restoreUndo()
    markEdited()
  }, [canUndo, restoreUndo, markEdited])
  const redo = useCallback(() => {
    if (!canRedo) return
    restoreRedo()
    markEdited()
  }, [canRedo, restoreRedo, markEdited])
  const clipboardRef = useRef<{ nodes: Node[]; edges: Edge[] } | null>(null)
  const [helpOpen, setHelpOpen] = useState(false)
  // Backend SVG render preview, for comparing the server-rendered shapes against
  // the React Flow canvas. Path-free: posts the canonical JSON, shows the SVG.
  const [renderPreview, setRenderPreview] = useState<
    | { status: 'closed' }
    | { status: 'loading' }
    | { status: 'ready'; svg: string }
    | { status: 'error'; message: string }
  >({ status: 'closed' })
  const renderPreviewSeq = useRef(0)
  // Canonical-JSON preview: a git-style diff of the current
  // diagram against how it was opened, plus a raw view. Opens via the Preview menu.
  const [jsonPreviewOpen, setJsonPreviewOpen] = useState(false)
  const [jsonRaw, setJsonRaw] = useState(false)
  // Coalesces consecutive property edits to the same field into a single undo step.
  const editKeyRef = useRef<string | null>(null)
  const snapshotStructural = useCallback(() => {
    editKeyRef.current = null
    takeSnapshot()
  }, [takeSnapshot])
  const snapshotEdit = useCallback(
    (key: string) => {
      if (editKeyRef.current !== key) {
        takeSnapshot()
        editKeyRef.current = key
      }
    },
    [takeSnapshot],
  )

  const duplicate = useCallback(() => {
    const cloned = cloneSelectedElements(nodes, edges)
    if (cloned.nodes.length === 0) return
    snapshotStructural()
    setNodes((nds) => nds.map((n): Node => ({ ...n, selected: false })).concat(cloned.nodes))
    setEdges((eds) => eds.map((e): Edge => ({ ...e, selected: false })).concat(cloned.edges))
    markEdited()
  }, [nodes, edges, setNodes, setEdges, snapshotStructural, markEdited])

  const copy = useCallback(() => {
    const sel = nodes.filter((n) => n.selected)
    if (sel.length === 0) return
    const ids = new Set(sel.map((n) => n.id))
    clipboardRef.current = { nodes: sel, edges: edges.filter((e) => ids.has(e.source) && ids.has(e.target)) }
  }, [nodes, edges])

  const paste = useCallback(() => {
    const clip = clipboardRef.current
    if (!clip) return
    const cloned = cloneSelectedElements(clip.nodes, clip.edges)
    if (cloned.nodes.length === 0) return
    snapshotStructural()
    setNodes((nds) => nds.map((n): Node => ({ ...n, selected: false })).concat(cloned.nodes))
    setEdges((eds) => eds.map((e): Edge => ({ ...e, selected: false })).concat(cloned.edges))
    markEdited()
  }, [setNodes, setEdges, snapshotStructural, markEdited])

  const deleteSelected = useCallback(() => {
    const removed = new Set(nodes.filter((n) => n.selected).map((n) => n.id))
    if (removed.size === 0 && !edges.some((e) => e.selected)) return
    snapshotStructural()
    setNodes((nds) => nds.filter((n) => !n.selected))
    setEdges((eds) => eds.filter((e) => !e.selected && !removed.has(e.source) && !removed.has(e.target)))
    markEdited()
  }, [nodes, edges, setNodes, setEdges, snapshotStructural, markEdited])

  const onBeforeDelete = useCallback(
    async ({ nodes: deletingNodes, edges: deletingEdges }: { nodes: Node[]; edges: Edge[] }) => {
      if (deletingNodes.length || deletingEdges.length) snapshotStructural()
      return true
    },
    [snapshotStructural],
  )

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (!(e.ctrlKey || e.metaKey)) return
      const target = e.target as HTMLElement | null
      const tag = target?.tagName
      // Let native shortcuts run while typing in a field (copy/paste/undo of text).
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target?.isContentEditable === true) return
      const key = e.key.toLowerCase()
      if (key === 'z' && !e.shiftKey) {
        e.preventDefault()
        undo()
      } else if ((key === 'z' && e.shiftKey) || key === 'y') {
        e.preventDefault()
        redo()
      } else if (key === 'd') {
        e.preventDefault()
        duplicate()
      } else if (key === 'c') {
        e.preventDefault()
        copy()
      } else if (key === 'v') {
        e.preventDefault()
        paste()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [undo, redo, duplicate, copy, paste])

  // Reconnect bookkeeping. `edgeReconnectSuccessful` tells the
  // end handler whether the drag landed on a valid handle; `reconnecting` suppresses
  // onConnect so a reconnect drag can't also spawn a brand-new (duplicate) edge.
  const edgeReconnectSuccessful = useRef(true)
  const reconnecting = useRef(false)
  const connectionStartRef = useRef<{ nodeId: string; anchor: RouteAnchor } | null>(null)
  const [connectionPreviewStart, setConnectionPreviewStart] = useState<{ x: number; y: number } | null>(null)
  const pendingConnectionRef = useRef<Connection | null>(null)
  const reconnectPointerRef = useRef<{ x: number; y: number } | null>(null)
  const stopReconnectPointerRef = useRef<(() => void) | null>(null)
  useEffect(() => () => stopReconnectPointerRef.current?.(), [])

  const commitConnection = useCallback(
    (connection: Connection, sourceAnchor: RouteAnchor, targetAnchor: RouteAnchor) => {
      if (!connection.source || !connection.target) return
      snapshotStructural()
      // New canvas edges carry the diagram type's primary edge semantic so they
      // save as meaningful canonical edges, plus the matching marker (display-only).
      const sourceSemantic = nodes.find((node) => node.id === connection.source)?.data.semanticType
      const targetSemantic = nodes.find((node) => node.id === connection.target)?.data.semanticType
      const semanticType = sourceSemantic === 'note' || targetSemantic === 'note'
        ? 'commentLink'
        : relationshipSemantic
      const transition = applyRelationshipSemantic({ semanticType }, semanticType)
      const data: GraphPilotEdgeData = { ...transition.data, semanticType: transition.semanticType }
      const markers = edgeMarkers(data.semanticType, data.arrow, data)
      setEdges((eds) => eds.concat({
        source: connection.source,
        target: connection.target,
        id: newEdgeId(connection.source, connection.target),
        type: 'default',
        data: {
          ...data,
          gpRoute: { mode: nextRouteMode, sourceAnchor, targetAnchor },
        } as unknown as Record<string, unknown>,
        ...markers,
      }))
      markEdited()
    },
    [setEdges, markEdited, snapshotStructural, relationshipSemantic, nextRouteMode, nodes],
  )

  const onConnectStart: OnConnectStart = useCallback((event, { nodeId }) => {
    const client = pointerClientPosition(event)
    const node = nodeId ? getInternalNode(nodeId) : undefined
    if (!client || !node || !nodeId) {
      connectionStartRef.current = null
      setConnectionPreviewStart(null)
      return
    }
    const rect = internalNodeRect(node)
    const resolved = resolveAttachmentAnchor(rect, screenToFlowPosition(client), getZoom())
    connectionStartRef.current = { nodeId, anchor: resolved.anchor }
    setConnectionPreviewStart(resolved.point)
  }, [getInternalNode, getZoom, screenToFlowPosition])

  const onConnect = useCallback((connection: Connection) => {
    if (!reconnecting.current) pendingConnectionRef.current = connection
  }, [])

  const onConnectEnd: OnConnectEnd = useCallback((event) => {
    const connection = pendingConnectionRef.current
    const start = connectionStartRef.current
    pendingConnectionRef.current = null
    connectionStartRef.current = null
    setConnectionPreviewStart(null)
    if (!connection || !start || !connection.source || !connection.target) return
    const client = pointerClientPosition(event)
    const endNodeId = start.nodeId === connection.source ? connection.target : connection.source
    const endNode = client ? getInternalNode(endNodeId) : undefined
    if (!client || !endNode) return
    const endAnchor = resolveAttachmentAnchor(internalNodeRect(endNode), screenToFlowPosition(client), getZoom()).anchor
    if (start.nodeId === connection.source) commitConnection(connection, start.anchor, endAnchor)
    else if (start.nodeId === connection.target) commitConnection(connection, endAnchor, start.anchor)
  }, [commitConnection, getInternalNode, getZoom, screenToFlowPosition])

  const connectionLineComponent = useCallback(({ fromX, fromY, toX, toY, connectionLineStyle }: ConnectionLineComponentProps) => {
    const start = connectionPreviewStart ?? { x: fromX, y: fromY }
    return <path className="react-flow__connection-path" d={`M ${start.x} ${start.y} L ${toX} ${toY}`} fill="none" style={connectionLineStyle} />
  }, [connectionPreviewStart])

  const onReconnectStart = useCallback((event: ReactMouseEvent) => {
    edgeReconnectSuccessful.current = false
    reconnecting.current = true
    reconnectPointerRef.current = pointerClientPosition(event) ?? null
    stopReconnectPointerRef.current?.()
    const move = (pointer: PointerEvent) => {
      reconnectPointerRef.current = { x: pointer.clientX, y: pointer.clientY }
    }
    const stop = () => {
      window.removeEventListener('pointermove', move)
      stopReconnectPointerRef.current = null
    }
    stopReconnectPointerRef.current = stop
    window.addEventListener('pointermove', move)
  }, [])

  const onReconnect = useCallback(
    (oldEdge: Edge, newConnection: Connection) => {
      edgeReconnectSuccessful.current = true
      const sourceChanged = oldEdge.source !== newConnection.source || oldEdge.sourceHandle !== newConnection.sourceHandle
      const targetChanged = oldEdge.target !== newConnection.target || oldEdge.targetHandle !== newConnection.targetHandle
      const nodeId = sourceChanged ? newConnection.source : targetChanged ? newConnection.target : null
      const node = nodeId ? getInternalNode(nodeId) : undefined
      const pointer = reconnectPointerRef.current
      const anchor = node && pointer ? resolveAttachmentAnchor(internalNodeRect(node), screenToFlowPosition(pointer), getZoom()).anchor : undefined
      snapshotStructural()
      setEdges((items) => reconnectEdge(oldEdge, newConnection, items, { shouldReplaceId: false }).map((edge) => {
        if (edge.id !== oldEdge.id) return edge
        const data = { ...(edge.data ?? {}) } as Record<string, unknown>
        const route = reconnectRouteGeometry(normalizeRouteGeometry(data.gpRoute), sourceChanged, targetChanged) ?? {}
        if (anchor && sourceChanged) route.sourceAnchor = anchor
        if (anchor && targetChanged) route.targetAnchor = anchor
        if (Object.keys(route).length) data.gpRoute = route
        else delete data.gpRoute
        const next = { ...edge, data }
        if (sourceChanged) delete next.sourceHandle
        if (targetChanged) delete next.targetHandle
        return next
      }))
      markEdited()
    },
    [getInternalNode, getZoom, markEdited, screenToFlowPosition, setEdges, snapshotStructural],
  )

  const onReconnectEnd = useCallback(
    (_event: unknown, edge: Edge) => {
      // Dropped the edge end somewhere that isn't a handle: remove the edge instead
      // of leaving a stale/dangling one (which read as a duplicate elsewhere).
      if (!edgeReconnectSuccessful.current) {
        snapshotStructural()
        setEdges((eds) => eds.filter((item) => item.id !== edge.id))
        markEdited()
      }
      stopReconnectPointerRef.current?.()
      reconnectPointerRef.current = null
      reconnecting.current = false
    },
    [setEdges, markEdited, snapshotStructural],
  )

  // Allow any node to connect to any other node, from any handle/side — except a
  // self-loop (same source and target), which isn't meaningful for these diagram
  // types and renders as a degenerate edge. This is also the single extension point
  // where a client could later restrict which relationships are permitted.
  const isValidConnection = useCallback(
    (connection: Connection | Edge) => connection.source !== connection.target,
    [],
  )

  // While a file is dragged over the canvas, show a "drop to open" overlay.
  // Driven off onDragOver (fires continuously and bubbles up
  // from nested React Flow elements) plus a short hide-timer, which avoids the
  // dragenter/dragleave flicker a naive approach would cause.
  const [fileDragOver, setFileDragOver] = useState(false)
  const fileDragTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const endFileDragOver = useCallback(() => {
    if (fileDragTimer.current) clearTimeout(fileDragTimer.current)
    fileDragTimer.current = undefined
    setFileDragOver(false)
  }, [])
  useEffect(
    () => () => {
      if (fileDragTimer.current) clearTimeout(fileDragTimer.current)
    },
    [],
  )

  // Open a .gp.json dropped onto the canvas. Parse first, then
  // guard unsaved edits — the DataTransfer is gone by the time the user confirms,
  // so the parsed result is captured up front.
  const handleFileDrop = useCallback(
    async (dataTransfer: DataTransfer) => {
      let res: LocalDiagramResult | null
      try {
        res = await openDroppedDiagram(dataTransfer)
      } catch (error) {
        const invalid = error instanceof SyntaxError || (error instanceof Error && error.message.includes('GraphPilot diagram'))
        notify(
          'error',
          invalid
            ? 'That file is not a valid GraphPilot diagram (.gp.json).'
            : `Could not open that file: ${error instanceof Error ? error.message : String(error)}`,
        )
        return
      }
      if (!res) return
      const loaded = res
      if (dirty) {
        setConfirmState({
          message: 'Open the dropped file? Any unsaved changes will be lost.',
          confirmLabel: 'Discard & open',
          onConfirm: () => {
            setConfirmState(null)
            onOpenDroppedResult(loaded)
          },
        })
      } else {
        onOpenDroppedResult(loaded)
      }
    },
    [dirty, notify, onOpenDroppedResult],
  )

  const onDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    if (event.dataTransfer.types.includes('Files')) {
      // External file (drop-to-open): show the overlay and refresh a hide-timer so
      // it disappears shortly after the drag leaves the canvas.
      event.dataTransfer.dropEffect = 'copy'
      setFileDragOver(true)
      if (fileDragTimer.current) clearTimeout(fileDragTimer.current)
      fileDragTimer.current = setTimeout(() => setFileDragOver(false), 160)
    } else {
      // A dragged palette shape.
      event.dataTransfer.dropEffect = 'move'
    }
  }, [])

  const addCatalogNode = useCallback(
    (item: PaletteItem, point: { x: number; y: number }) => {
      const size = defaultNodeSize(item.semanticType)
      if (nodePrimitive(item.semanticType) === 'classifier-box') size.height = featureBlockMinHeight(undefined)
      const node: Node = {
        id: newNodeId(item.semanticType),
        type: item.type,
        position: { x: point.x - size.width / 2, y: point.y - size.height / 2 },
        data: { label: item.label, semanticType: item.semanticType, gpStyle: DEFAULT_NODE_STYLE },
        style: { width: size.width, height: size.height },
      }
      snapshotStructural()
      setNodes((nds) => nds.concat(node))
      markEdited()
    },
    [setNodes, markEdited, snapshotStructural],
  )

  const addPaletteItem = useCallback(
    (item: PaletteItem) => {
      const point = screenToFlowPosition({ x: window.innerWidth / 2, y: window.innerHeight / 2 })
      addCatalogNode(item, point)
    },
    [screenToFlowPosition, addCatalogNode],
  )

  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault()
      endFileDragOver()
      // External file → open it as a diagram; otherwise it's a
      // palette shape being dropped onto the canvas.
      if (event.dataTransfer.types.includes('Files')) {
        void handleFileDrop(event.dataTransfer)
        return
      }
      const raw = event.dataTransfer.getData(DRAG_MIME)
      if (!raw) return
      let payload: { type?: string; semanticType?: string; label?: string }
      try {
        payload = JSON.parse(raw)
      } catch {
        return
      }
      const { type, semanticType, label } = payload
      if (type !== 'gpNode' || typeof semanticType !== 'string' || (label !== undefined && typeof label !== 'string')) return
      const spec = getElementSpec(semanticType)
      if (spec?.kind !== 'node') return
      const point = screenToFlowPosition({ x: event.clientX, y: event.clientY })
      addCatalogNode({ type, semanticType, label: label ?? semanticType }, point)
    },
    [screenToFlowPosition, addCatalogNode, handleFileDrop, endFileDragOver],
  )

  // Re-parent a dragged node by geometry when it lands inside a valid semantic
  // owner: containers own nested elements, classifier boxes own ports, and actions/
  // expansion regions own pins. Dropping outside clears the live parent.
  const onNodeDragStop = useCallback(
    (_event: unknown, dragged: Node) => {
      setHelperLines({})
      const semanticType = (dragged.data as { semanticType?: string } | undefined)?.semanticType
      if (!isContainerSemantic(semanticType)) {
        const owner = getIntersectingNodes(dragged).find((node) => {
          const candidate = (node.data as { semanticType?: string } | undefined)?.semanticType
          return node.id !== dragged.id && canOwnSemantic(candidate, semanticType)
        })
        const newParentId = owner?.id
        if (newParentId !== dragged.parentId) setNodes((nds) => reparentNode(nds, dragged.id, newParentId))
      }
      markEdited()
    },
    [getIntersectingNodes, setNodes, markEdited],
  )

  const onSelectionChange = useCallback(
    ({ nodes: selNodes, edges: selEdges }: { nodes: Node[]; edges: Edge[] }) => {
      // Switching selection begins a fresh undo step for the next property edit.
      editKeyRef.current = null
      setSelectedNodeIds(selNodes.map((n) => n.id))
      if (selNodes.length) setSelection({ kind: 'node', id: selNodes[0].id })
      else if (selEdges.length) setSelection({ kind: 'edge', id: selEdges[0].id })
      else setSelection(null)
    },
    [],
  )

  // Alignment guides while dragging: intercept a single node's
  // live position change, snap it to the nearest node edge/center, and surface the
  // guide-line coordinates for the overlay. Other changes pass straight through.
  const [helperLines, setHelperLines] = useState<{ horizontal?: number; vertical?: number }>({})
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      let next = changes
      let lines: { horizontal?: number; vertical?: number } = {}
      const change = changes[0]
      if (changes.length === 1 && change.type === 'position' && change.dragging && change.position) {
        const helpers = getHelperLines(change, nodes)
        const position = {
          x: helpers.snapPosition.x ?? change.position.x,
          y: helpers.snapPosition.y ?? change.position.y,
        }
        next = [{ ...change, position }]
        lines = { horizontal: helpers.horizontal, vertical: helpers.vertical }
      }
      const nodeById = new Map(nodes.map((node) => [node.id, node]))
      const positions = new Map(next.flatMap((item) =>
        item.type === 'position' && item.position ? [[item.id, item.position] as const] : [],
      ))
      const isDescendant = (nodeId: string, ancestorId: string) => {
        let parentId = nodeById.get(nodeId)?.parentId
        const visited = new Set<string>()
        while (parentId && !visited.has(parentId)) {
          if (parentId === ancestorId) return true
          visited.add(parentId)
          parentId = nodeById.get(parentId)?.parentId
        }
        return false
      }
      const movement = (nodeId: string) => {
        const direct = positions.get(nodeId)
        const current = nodeById.get(nodeId)
        if (direct && current) return { x: direct.x - current.position.x, y: direct.y - current.position.y }
        for (const [changedId, position] of positions) {
          const changed = nodeById.get(changedId)
          if (changed && isDescendant(nodeId, changedId)) {
            return { x: position.x - changed.position.x, y: position.y - changed.position.y }
          }
        }
        return undefined
      }
      if (positions.size) {
        setEdges((items) => items.map((edge) => {
          const route = normalizeRouteGeometry((edge.data as Record<string, unknown> | undefined)?.gpRoute)
          if (!route?.waypoints?.length) return edge
          const sourceMove = movement(edge.source)
          const targetMove = movement(edge.target)
          if (
            sourceMove && targetMove &&
            Math.abs(sourceMove.x - targetMove.x) < 0.001 &&
            Math.abs(sourceMove.y - targetMove.y) < 0.001
          ) {
            return {
              ...edge,
              data: {
                ...(edge.data ?? {}),
                gpRoute: translateRouteWaypoints(route, sourceMove.x, sourceMove.y),
              },
            }
          }
          return edge
        }))
      }
      setHelperLines(lines)
      onNodesChange(next)
    },
    [nodes, onNodesChange, setEdges],
  )

  // Bulk style across a multi-selection: apply the style part
  // of a NodePatch to every selected node at once, as one undo step.
  const bulkStyleNodes = useCallback(
    (ids: string[], patch: NodePatch) => {
      if (ids.length === 0) return
      const idSet = new Set(ids)
      snapshotStructural()
      setNodes((nds) => nds.map((n) => (idSet.has(n.id) ? applyNodePatch(n, patch) : n)))
      markEdited()
    },
    [setNodes, markEdited, snapshotStructural],
  )

  const updateNode = useCallback(
    (id: string, patch: NodePatch) => {
      snapshotEdit(`node:${id}:${Object.keys(patch).join(',')}`)
      setNodes((nds) => nds.map((n) => (n.id === id ? applyNodePatch(n, patch) : n)))
      markEdited()
    },
    [setNodes, markEdited, snapshotEdit],
  )

  const updateEdge = useCallback(
    (id: string, patch: EdgePatch) => {
      snapshotEdit(`edge:${id}:${Object.keys(patch).join(',')}`)
      setEdges((eds) =>
        eds.map((edge) => {
          if (edge.id !== id) return edge
          if (patch.swapEnds) {
            const data = { ...((edge.data ?? {}) as GraphPilotEdgeData & { gpRoute?: unknown }) }
            const sourceEnd = data.sourceEnd
            if (data.targetEnd) data.sourceEnd = data.targetEnd
            else delete data.sourceEnd
            if (sourceEnd) data.targetEnd = sourceEnd
            else delete data.targetEnd
            const route = reverseRouteGeometry(normalizeRouteGeometry(data.gpRoute))
            if (route) data.gpRoute = route
            else delete data.gpRoute
            const next: Edge = { ...edge, source: edge.target, target: edge.source, data: data as unknown as Record<string, unknown> }
            if (edge.targetHandle) next.sourceHandle = edge.targetHandle
            else delete next.sourceHandle
            if (edge.sourceHandle) next.targetHandle = edge.sourceHandle
            else delete next.targetHandle
            const markerColor = typeof edge.style?.stroke === 'string' ? edge.style.stroke : EDGE_COLOR
            const { markerStart, markerEnd } = edgeMarkers(data.semanticType, data.arrow, data, markerColor)
            next.markerStart = markerStart
            next.markerEnd = markerEnd
            return next
          }
          const style = { ...(edge.style ?? {}) }
          if (patch.stroke !== undefined) style.stroke = patch.stroke
          if (patch.strokeWidth !== undefined) style.strokeWidth = patch.strokeWidth
          if (patch.strokeDasharray !== undefined) {
            if (patch.strokeDasharray) style.strokeDasharray = patch.strokeDasharray
            else delete style.strokeDasharray
          }
          const data = { ...((edge.data ?? {}) as GraphPilotEdgeData & { gpRoute?: unknown }), ...(patch.data ?? {}) }
          if (patch.route !== undefined) {
            const route = normalizeRouteGeometry(patch.route)
            if (route) data.gpRoute = route
            else delete data.gpRoute
          }
          const previousSemantic = data.semanticType
          if (patch.semanticType !== undefined) data.semanticType = patch.semanticType
          for (const key of patch.clearData ?? []) delete data[key]
          if (patch.semanticType !== undefined) {
            const previousSpec = getElementSpec(previousSemantic)
            const nextSpec = getElementSpec(patch.semanticType)
            if (previousSpec?.kind === 'edge' && previousSpec.dashed && nextSpec?.kind === 'edge' && !nextSpec.dashed && style.strokeDasharray === '6 4') {
              delete style.strokeDasharray
            }
          }
          const next: Edge = { ...edge, style, data: data as unknown as Record<string, unknown> }
          if (patch.label !== undefined) next.label = patch.label
          if (patch.sourceHandle !== undefined) {
            if (patch.sourceHandle === null) delete next.sourceHandle
            else next.sourceHandle = patch.sourceHandle
          }
          if (patch.targetHandle !== undefined) {
            if (patch.targetHandle === null) delete next.targetHandle
            else next.targetHandle = patch.targetHandle
          }
          const markerColor = typeof style.stroke === 'string' ? style.stroke : EDGE_COLOR
          const { markerStart, markerEnd } = edgeMarkers(data.semanticType, data.arrow, data, markerColor)
          next.markerStart = markerStart
          next.markerEnd = markerEnd
          return next
        }),
      )
      markEdited()
    },
    [setEdges, markEdited, snapshotEdit],
  )

  const routeEditApi = useMemo(
    () => ({
      start: snapshotStructural,
      setRoute: (id: string, route: unknown) => {
        setEdges((items) => items.map((edge) => {
          if (edge.id !== id) return edge
          const data = { ...(edge.data ?? {}) } as Record<string, unknown>
          const normalized = normalizeRouteGeometry(route)
          if (normalized) data.gpRoute = normalized
          else delete data.gpRoute
          return { ...edge, data }
        }))
        markEdited()
      },
    }),
    [markEdited, setEdges, snapshotStructural],
  )

  // On-canvas resize (NodeResizer in the custom nodes): persist the live size
  // into the node `style` the reverse adapter reads (keeping the save round-trip
  // byte-stable), taking one undo snapshot at the drag start.
  const resizeApi = useMemo<NodeResizeApi>(
    () => ({
      start: snapshotStructural,
      resize: (id, width, height) => {
        setNodes((nds) => applyNodeResize(nds, id, width, height))
        markEdited()
      },
    }),
    [snapshotStructural, setNodes, markEdited],
  )

  // In-shape label editing (double-click a node): commit writes the label through
  // the same `updateNode` path the inspector uses (so undo + save are consistent).
  const [editingLabelId, setEditingLabelId] = useState<string | null>(null)
  const labelEditApi = useMemo<NodeLabelEditApi>(
    () => ({
      editingId: editingLabelId,
      begin: (id) => setEditingLabelId(id),
      commit: (id, label) => {
        updateNode(id, { label })
        setEditingLabelId(null)
      },
      cancel: () => setEditingLabelId(null),
    }),
    [editingLabelId, updateNode],
  )

  // Canonical JSON the editor would save/render: the reverse adapter takes `name`
  // from the loaded diagram, so apply the (editable) name override here, falling
  // back to the original if it was cleared so we never save an empty name.
  const buildCanonical = useCallback(() => {
    const canonical = reactFlowToGraphPilot(baseDiagram, nodes, edges)
    canonical.name = name.trim() || baseDiagram.name
    return canonical
  }, [baseDiagram, nodes, edges, name])

  const [baselineJson, setBaselineJson] = useState(() => {
    const rf = graphPilotToReactFlow(initialDiagram)
    return JSON.stringify(reactFlowToGraphPilot(initialDiagram, rf.nodes, rf.edges), null, 2)
  })

  const performSave = useCallback(async (force = false) => {
    setSaveState({ status: 'saving' })
    // Snapshot the edit generation so we only clear the dirty flag if no edits
    // happened while the save was in flight (otherwise those edits are unsaved).
    const savedGen = editGenRef.current
    const canonical = buildCanonical()
    try {
      if (source.kind === 'external-file') {
        if (!force) {
          const current = await readHandleDiagram(source.handle)
          if (current.revision !== source.revision) {
            setExternalChange({
              diagram: current.diagram,
              source: { kind: 'external-file', name: current.name, handle: source.handle, revision: current.revision },
            })
            setSaveState({ status: 'error', code: 'source_changed', message: 'The file changed on disk after it was loaded.' })
            notify('error', 'Save blocked because the file changed on disk.')
            return
          }
        }
        // Local (File System Access) source: validate on the backend, then write
        // the normalized diagram back to the opened handle (no path-based route).
        const result = await validateDiagram(canonical)
        if (!result.valid) {
          setSaveState({
            status: 'error',
            code: 'validation_failed',
            message: 'Diagram validation failed. The file was not written.',
            validationErrors: result.validationErrors,
          })
          notify('error', `Save blocked: ${result.validationErrors.length} validation issue${result.validationErrors.length === 1 ? '' : 's'}.`)
          return
        }
        const revision = await writeHandle(source.handle, result.diagram)
        const nextSource: DiagramSource = { ...source, revision }
        setBaseDiagram(result.diagram)
        setBaselineJson(JSON.stringify(result.diagram, null, 2))
        setExternalChange(null)
        onSessionChange(nextSource, result.diagram, source, session.loadId)
        setSaveState({ status: 'saved' })
        if (editGenRef.current === savedGen) setDirty(false)
        notify('success', 'Diagram saved.')
        return
      }
      if (source.kind !== 'workspace') return
      const saveResult = await saveDiagram(source.path, canonical, force ? undefined : source.revision)
      const nextSource: DiagramSource = { kind: 'workspace', path: saveResult.diagramPath, revision: saveResult.revision }
      setBaseDiagram(saveResult.diagram)
      setBaselineJson(JSON.stringify(saveResult.diagram, null, 2))
      setExternalChange(null)
      onSessionChange(nextSource, saveResult.diagram, source, session.loadId)
      setSaveState({ status: 'saved' })
      if (editGenRef.current === savedGen) setDirty(false)
      // Render-on-save writes a sibling <name>.svg server-side; surface its name.
      const svgName = saveResult.svgPath?.split(/[\\/]/).pop()
      notify('success', svgName ? `Diagram saved + rendered ${svgName}.` : 'Diagram saved.')
    } catch (err) {
      if (err instanceof DiagramApiError) {
        if (err.code === 'source_changed' && source.kind === 'workspace') {
          try {
            const current = await loadDiagram(source.path)
            setExternalChange({
              diagram: current.diagram,
              source: { kind: 'workspace', path: current.diagramPath, revision: current.revision },
            })
          } catch {
            // Keep the original conflict error visible when the refresh also fails.
          }
        }
        setSaveState({
          status: 'error',
          code: err.code,
          message: err.message,
          validationErrors: err.validationErrors,
        })
        const count = err.validationErrors?.length ?? 0
        notify('error', count ? `Save blocked: ${count} validation issue${count === 1 ? '' : 's'}.` : `Save failed: ${err.message}`)
      } else {
        setSaveState({ status: 'error', code: 'unknown_error', message: String(err) })
        notify('error', 'Save failed.')
      }
    }
  }, [buildCanonical, notify, onSessionChange, session.loadId, source])

  // Save As: validate, then write a copy to a new location via the picker and
  // adopt that handle as the current local source (File System Access only).
  const saveAs = useCallback(async () => {
    const canonical = buildCanonical()
    setSaveState({ status: 'saving' })
    const savedGen = editGenRef.current
    try {
      const result = await validateDiagram(canonical)
      if (!result.valid) {
        setSaveState({
          status: 'error',
          code: 'validation_failed',
          message: 'Diagram validation failed. Nothing was written.',
          validationErrors: result.validationErrors,
        })
        notify('error', `Save blocked: ${result.validationErrors.length} validation issue${result.validationErrors.length === 1 ? '' : 's'}.`)
        return
      }
      const baseName = name.trim() || baseDiagram.name || 'diagram'
      const suggestedName = baseName.toLowerCase().endsWith('.gp.json') ? baseName : `${baseName}.gp.json`
      const saved = await saveAsLocalDiagram(result.diagram, suggestedName)
      if (!saved) {
        setSaveState({ status: 'idle' })
        return
      }
      const nextSource: DiagramSource = {
        kind: 'external-file',
        name: saved.handle.name,
        handle: saved.handle,
        revision: saved.revision,
      }
      setBaseDiagram(result.diagram)
      setBaselineJson(JSON.stringify(result.diagram, null, 2))
      setExternalChange(null)
      onSessionChange(nextSource, result.diagram, source, session.loadId)
      setSaveState({ status: 'saved' })
      if (editGenRef.current === savedGen) setDirty(false)
      notify('success', `Saved a copy as ${saved.handle.name}.`)
    } catch (err) {
      setSaveState({ status: 'error', code: 'unknown_error', message: String(err) })
      notify('error', 'Save As failed.')
    }
  }, [buildCanonical, name, baseDiagram.name, notify, onSessionChange, session.loadId, source])

  // Render the current canvas to SVG via the backend (path-free; writes nothing).
  // Builds the same canonical JSON a save would, so the render preview and the
  // image export share one render path.
  const getServerSvg = useCallback(() => renderDiagram(buildCanonical()), [buildCanonical])

  // Preview the backend SVG render of the current canvas, for comparing the
  // server-rendered shapes against React Flow.
  const previewRender = useCallback(async () => {
    const seq = ++renderPreviewSeq.current
    setRenderPreview({ status: 'loading' })
    try {
      const svg = await getServerSvg()
      if (renderPreviewSeq.current === seq) setRenderPreview({ status: 'ready', svg })
    } catch (err) {
      if (renderPreviewSeq.current !== seq) return
      const message = err instanceof DiagramApiError ? err.message : String(err)
      setRenderPreview({ status: 'error', message })
      notify('error', `Render preview failed: ${message}`)
    }
  }, [getServerSvg, notify])

  const closeRenderPreview = useCallback(() => {
    renderPreviewSeq.current += 1
    setRenderPreview({ status: 'closed' })
  }, [])

  // Current canonical JSON + its line diff vs. the last opened/saved baseline,
  // recomputed only
  // while the preview is open.
  const jsonPreview = useMemo(() => {
    if (!jsonPreviewOpen) return null
    const current = JSON.stringify(buildCanonical(), null, 2)
    const rows = diffLines(baselineJson, current)
    return { current, rows, stats: diffStats(rows) }
  }, [jsonPreviewOpen, buildCanonical, baselineJson])

  const externalReview = useMemo(() => {
    if (!externalChange) return []
    return diffLines(JSON.stringify(externalChange.diagram, null, 2), JSON.stringify(buildCanonical(), null, 2))
  }, [buildCanonical, externalChange])

  const previewJson = useCallback(() => setJsonPreviewOpen(true), [])

  const copyJson = useCallback(() => {
    const text = jsonPreview?.current
    if (!text) return
    const clip = navigator.clipboard
    if (!clip) {
      notify('error', 'Clipboard unavailable in this browser.')
      return
    }
    clip.writeText(text).then(
      () => notify('success', 'JSON copied to clipboard.'),
      () => notify('error', 'Could not copy to clipboard.'),
    )
  }, [jsonPreview, notify])

  // Export the current canvas as an image, rendered server-side: download the
  // SVG directly, or a client-side PNG rasterization of it.
  const exportImage = useCallback(
    async (format: 'png' | 'svg') => {
      try {
        const svg = await getServerSvg()
        const fileName = name.trim() || baseDiagram.name || 'diagram'
        if (format === 'svg') downloadSvg(svg, fileName)
        else await downloadPng(svg, fileName)
      } catch (err) {
        const message = err instanceof DiagramApiError ? err.message : String(err)
        notify('error', `Export failed: ${message}`)
      }
    },
    [getServerSvg, name, baseDiagram.name, notify],
  )

  // Validate the current canvas via the path-free endpoint and map each issue to
  // the node/edge it concerns, so the offending elements are outlined on the
  // canvas and flagged in the inspector. Markers clear on edit.
  const runValidation = useCallback(async () => {
    const canonical = buildCanonical()
    try {
      const result = await validateDiagram(canonical)
      setValidationMarkers(mapValidationErrors(canonical, result.validationErrors))
      if (result.valid) notify('success', 'No validation issues.')
      else notify('error', `${result.validationErrors.length} validation issue(s) found.`)
    } catch (err) {
      const message = err instanceof DiagramApiError ? err.message : String(err)
      notify('error', `Validation failed: ${message}`)
    }
  }, [buildCanonical, notify])

  // Open any file from disk (File System Access); guard unsaved edits first.
  const requestOpenLocal = useCallback(() => {
    if (dirty) {
      setConfirmState({
        message: 'Open a file? Any unsaved changes will be lost.',
        confirmLabel: 'Discard & open',
        onConfirm: () => {
          setConfirmState(null)
          onOpenLocal()
        },
      })
      return
    }
    onOpenLocal()
  }, [dirty, onOpenLocal])

  const handleSave = useCallback(() => {
    if (requiresSaveAs) {
      void saveAs()
      return
    }
    const force = externalChange !== null
    setConfirmState({
      message: force
        ? 'The source changed on disk. Overwrite that newer version with your canvas changes?'
        : 'Overwrite the saved diagram with your changes?',
      confirmLabel: 'Overwrite',
      onConfirm: () => {
        setConfirmState(null)
        void performSave(force)
      },
    })
  }, [externalChange, requiresSaveAs, saveAs, performSave])

  // Guard returning home when there are unsaved edits.
  const requestHome = useCallback(() => {
    if (dirty) {
      setConfirmState({
        message: 'Return home? Any unsaved changes will be lost.',
        confirmLabel: 'Discard & go home',
        onConfirm: () => {
          setConfirmState(null)
          onHome()
        },
      })
      return
    }
    onHome()
  }, [dirty, onHome])

  // Persist the autosave preference and, while it is on, debounce-save unsaved
  // edits (autosave is implicit consent, so it skips the overwrite confirm).
  useEffect(() => {
    try {
      localStorage.setItem('gp.autosave', autosave ? '1' : '0')
    } catch {
      // ignore write failures
    }
  }, [autosave])

  useEffect(() => {
    if (!autosave || requiresSaveAs || !dirty || saveState.status === 'saving' || saveState.status === 'error') return
    const t = setTimeout(() => void performSave(), 1500)
    return () => clearTimeout(t)
  }, [autosave, requiresSaveAs, dirty, saveState.status, performSave])

  useEffect(() => {
    if (source.kind === 'read-only-file' || source.kind === 'unsaved') return
    let active = true
    const refresh = async () => {
      if (document.visibilityState === 'hidden') return
      try {
        const current = source.kind === 'workspace'
          ? await loadDiagram(source.path).then((response) => ({
              source: { kind: 'workspace', path: response.diagramPath, revision: response.revision } as DiagramSource,
              diagram: response.diagram,
              revision: response.revision,
            }))
          : await readHandleDiagram(source.handle).then((response) => ({
              source: {
                kind: 'external-file',
                name: response.name,
                handle: source.handle,
                revision: response.revision,
              } as DiagramSource,
              diagram: response.diagram,
              revision: response.revision,
            }))
        if (!active || current.revision === source.revision) return
        if (dirty) {
          setExternalChange({ diagram: current.diagram, source: current.source })
          return
        }
        onSessionReload(current.source, current.diagram)
      } catch {
        return
      }
    }
    const stop = () => {
      active = false
    }
    window.addEventListener('focus', refresh)
    window.addEventListener('beforeunload', stop)
    document.addEventListener('visibilitychange', refresh)
    return () => {
      stop()
      window.removeEventListener('focus', refresh)
      window.removeEventListener('beforeunload', stop)
      document.removeEventListener('visibilitychange', refresh)
    }
  }, [dirty, onSessionReload, source])

  // Warn before a page refresh or tab close would discard unsaved edits.
  useEffect(() => {
    if (!dirty) return
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [dirty])

  // Auto-dismiss the brief "Saved." banner a few seconds after a successful save (a
  // success toast already confirms it); error banners stay until the next edit so the
  // user can read the validation issues.
  useEffect(() => {
    if (saveState.status !== 'saved') return
    const t = setTimeout(() => setSaveState((s) => (s.status === 'saved' ? { status: 'idle' } : s)), 2500)
    return () => clearTimeout(t)
  }, [saveState.status])

  const palette = useRail('gp.rail.palette', 180)
  const inspector = useRail('gp.rail.inspector', 280)
  const { mode, toggle: toggleTheme } = useColorMode()

  // Decorate (display-only) the nodes/edges flagged by validation with a
  // `gp-invalid` class for the red outline. Identity is preserved when there are
  // no markers, and `className` is never read back by the reverse adapter.
  const decoratedNodes = useMemo(() => nodes.map((node) => {
    const layered = decorateNodeLayer(node)
    return validationMarkers?.nodeIds.has(node.id) ? { ...layered, className: cn(layered.className, 'gp-invalid') } : layered
  }), [nodes, validationMarkers])
  // Parallel edges into one node would otherwise all attach at that side's centre and
  // draw as a single line. Computed once over the whole graph — an edge cannot see its
  // siblings — and handed to each edge as runtime-only data the reverse adapter ignores.
  // Mirrors `_fan_out_anchors` in the SVG renderer so canvas and export agree.
  const fanOutByEdge = useMemo(() => {
    const rects = new Map(nodes.map((node) => [node.id, {
      x: node.position.x,
      y: node.position.y,
      w: Number(node.style?.width ?? node.measured?.width ?? 0),
      h: Number(node.style?.height ?? node.measured?.height ?? 0),
      primitive: (node.data as { semanticType?: string } | undefined)?.semanticType,
      label: (node.data as { label?: string } | undefined)?.label,
    }]))
    // A system boundary or a partition is scenery, not an obstacle: an edge crossing one
    // is normal. The SVG renderer excludes them from the same check.
    const containerIds = new Set(
      nodes
        .filter((node) => isContainerSemantic((node.data as { semanticType?: string } | undefined)?.semanticType))
        .map((node) => node.id),
    )
    return fanOutAnchors(
      edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        geometry: (edge.data as { gpRoute?: RouteGeometry } | undefined)?.gpRoute,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
      })),
      rects,
      containerIds,
    )
  }, [nodes, edges])

  const decoratedEdges = useMemo(() => edges.map((edge) => {
    const layered = edge.zIndex === CANVAS_LAYER.edge ? edge : { ...edge, zIndex: CANVAS_LAYER.edge }
    const fanOut = fanOutByEdge.get(edge.id)
    const withFanOut = fanOut ? { ...layered, data: { ...(layered.data ?? {}), gpFanOut: fanOut } } : layered
    return validationMarkers?.edgeIds.has(edge.id)
      ? { ...withFanOut, className: cn(withFanOut.className, 'gp-invalid') }
      : withFanOut
  }), [edges, validationMarkers, fanOutByEdge])

  const selectionIssues = useMemo(() => {
    if (!validationMarkers || !selection) return undefined
    return selection.kind === 'node'
      ? validationMarkers.byNode[selection.id]
      : validationMarkers.byEdge[selection.id]
  }, [validationMarkers, selection])

  const panelSelection: PanelSelection = useMemo(() => {
    if (selection?.kind === 'node') {
      const node = nodes.find((n) => n.id === selection.id)
      return node ? { kind: 'node', node } : null
    }
    if (selection?.kind === 'edge') {
      const edge = edges.find((e) => e.id === selection.id)
      return edge ? { kind: 'edge', edge } : null
    }
    return null
  }, [selection, nodes, edges])
  const paletteRelationshipSemantic = panelSelection?.kind === 'edge' && typeof panelSelection.edge.data?.semanticType === 'string'
    ? panelSelection.edge.data.semanticType
    : relationshipSemantic
  const chooseRelationshipSemantic = useCallback((semanticType: string) => {
    setRelationshipSemantic(semanticType)
    if (panelSelection?.kind !== 'edge' || panelSelection.edge.data?.semanticType === semanticType) return
    const transition = applyRelationshipSemantic((panelSelection.edge.data ?? {}) as GraphPilotEdgeData, semanticType)
    updateEdge(panelSelection.edge.id, {
      semanticType: transition.semanticType,
      data: transition.data,
      clearData: transition.clearData,
    })
  }, [panelSelection, updateEdge])
  const selectedRoute = panelSelection?.kind === 'edge'
    ? normalizeRouteGeometry((panelSelection.edge.data as Record<string, unknown> | undefined)?.gpRoute)
    : undefined
  const paletteRouteMode = panelSelection?.kind === 'edge' ? selectedRoute?.mode ?? 'orthogonal' : nextRouteMode
  const chooseRouteMode = useCallback((mode: RouteMode) => {
    setNextRouteMode(mode)
    if (panelSelection?.kind !== 'edge' || (selectedRoute?.mode ?? 'orthogonal') === mode) return
    updateEdge(panelSelection.edge.id, { route: setRouteMode(selectedRoute, mode) })
  }, [panelSelection, selectedRoute, updateEdge])

  const saveText =
    saveState.status === 'saving'
      ? 'Saving…'
      : saveState.status === 'saved'
        ? 'Saved'
        : saveState.status === 'error'
          ? 'Save failed'
          : dirty
            ? 'Unsaved changes'
            : 'Up to date'

  const sourceInfo = source.kind === 'workspace'
    ? { location: source.path, state: 'Writable path', revision: source.revision, copyPath: source.path }
    : source.kind === 'external-file'
      ? { location: source.name, state: 'Writable for this browser session', revision: source.revision }
      : source.kind === 'read-only-file'
        ? { location: source.name, state: 'Read-only — Save As required' }
        : { location: source.name, state: 'Unsaved — Save As required' }

  // Progressive top-bar overflow: as the window narrows, fold more actions into a
  // "⋯" menu (always keeping the primary Save inline) so the action row never wraps.
  // Thresholds are window-width px and easy to retune.
  const winWidth = useWindowWidth()
  const showExportSaveAs = winWidth >= 700
  const showFileOps = winWidth >= 840
  const showSecondary = winWidth >= 1000

  const topBarMore: ToolbarMoreItem[] = []
  if (!showSecondary) {
    topBarMore.push({ label: mode === 'dark' ? 'Switch to light theme' : 'Switch to dark theme', onClick: toggleTheme })
    topBarMore.push({
      label: autosave ? 'Turn autosave off' : 'Turn autosave on',
      onClick: () => setAutosave((v) => !v),
      disabled: requiresSaveAs,
    })
  }
  if (!showFileOps) {
    topBarMore.push({ label: 'Home', onClick: requestHome })
    topBarMore.push({ label: 'Open file…', onClick: requestOpenLocal, disabled: !fsaSupported })
  }
  if (!showExportSaveAs) {
    topBarMore.push({ label: 'Export PNG', onClick: () => void exportImage('png') })
    topBarMore.push({ label: 'Export SVG', onClick: () => void exportImage('svg') })
    if (!requiresSaveAs) {
      topBarMore.push({
        label: 'Save As…',
        onClick: () => void saveAs(),
        disabled: !fsaSupported || saveState.status === 'saving',
      })
    }
  }

  return (
    <div className="flex h-screen w-screen flex-col">
      <TopBar
        name={name}
        onNameChange={(v) => {
          setName(v)
          markEdited()
        }}
        diagramType={baseDiagram.diagramType}
        dirty={dirty}
        sourceInfo={sourceInfo}
        actions={
          <>
            {showSecondary ? (
              <>
                <label
                  className="flex items-center gap-1 text-xs text-fg-muted"
                  title={requiresSaveAs ? 'Autosave is unavailable until this diagram has a writable file' : 'Automatically save edits'}
                >
                  <input
                    type="checkbox"
                    checked={autosave}
                    disabled={requiresSaveAs}
                    onChange={(e) => setAutosave(e.target.checked)}
                  />
                  Autosave
                </label>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleTheme}
                  title="Toggle light/dark theme"
                  aria-label="Toggle light/dark theme"
                >
                  {mode === 'dark' ? '☀' : '☾'}
                </Button>
              </>
            ) : null}
            {showFileOps ? (
              <>
                <Button variant="secondary" size="sm" onClick={requestHome}>
                  Home
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={requestOpenLocal}
                  disabled={!fsaSupported}
                  title={fsaSupported ? 'Open any .gp.json file from disk' : 'Open file… needs a Chromium browser (Chrome/Edge)'}
                >
                  Open file…
                </Button>
              </>
            ) : null}
            {showExportSaveAs ? (
              <>
                <ExportMenu
                  onExportPng={() => void exportImage('png')}
                  onExportSvg={() => void exportImage('svg')}
                />
                {!requiresSaveAs ? (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => void saveAs()}
                    disabled={!fsaSupported || saveState.status === 'saving'}
                    title={fsaSupported ? 'Save a copy to a new location' : 'Save As needs a Chromium browser (Chrome/Edge)'}
                  >
                    Save As
                  </Button>
                ) : null}
              </>
            ) : null}
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={saveState.status === 'saving' || (requiresSaveAs && !fsaSupported)}
              title={requiresSaveAs ? 'Choose a file location for this diagram' : undefined}
            >
              {saveState.status === 'saving' ? 'Saving…' : requiresSaveAs ? 'Save As' : 'Save'}
            </Button>
            {topBarMore.length > 0 ? <ToolbarMore items={topBarMore} /> : null}
          </>
        }
      />
      <SaveBanner saveState={saveState} />
      {externalChange ? (
        <div className="flex items-center justify-between gap-3 border-b border-warn/40 bg-warn/10 px-4 py-2 text-sm text-fg">
          <span>The source diagram changed on disk while this canvas has unsaved edits.</span>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setExternalReviewOpen(true)}>Review changes</Button>
            <Button variant="secondary" onClick={() => setExternalChange(null)}>Keep editing</Button>
            <Button variant="secondary" onClick={() => onSessionReload(externalChange.source, externalChange.diagram, true)}>Reload from disk</Button>
          </div>
        </div>
      ) : null}
      <EdgeMarkerDefs />
      <main className="flex min-h-0 flex-1">
        <Rail
          side="left"
          title="Shapes"
          width={palette.width}
          collapsed={palette.collapsed}
          onWidthChange={palette.setWidth}
          onToggle={palette.toggle}
          min={150}
          max={320}
        >
          <NodePalette
            diagramType={baseDiagram.diagramType}
            onAdd={addPaletteItem}
            relationshipSemantic={paletteRelationshipSemantic}
            onRelationshipSemanticChange={chooseRelationshipSemantic}
            routeMode={paletteRouteMode}
            onRouteModeChange={chooseRouteMode}
          />
        </Rail>
        <div className="relative min-w-0 flex-1" onDrop={onDrop} onDragOver={onDragOver}>
          <NodeResizeContext.Provider value={resizeApi}>
          <NodeLabelEditContext.Provider value={labelEditApi}>
          <EdgeRouteEditContext.Provider value={routeEditApi}>
          <EditorColorModeContext.Provider value={mode}>
          <ReactFlow
            nodes={decoratedNodes}
            edges={decoratedEdges}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            colorMode={mode}
            // No 16px grid-snap: generated layouts use their own spacing (not
            // 16-multiples), so snapping made a moved node impossible to return to
            // its original off-grid spot. Free movement + the alignment guides
            // (snap to neighbours) + undo cover positioning instead.
            connectionMode={ConnectionMode.Loose}
            elevateNodesOnSelect={false}
            connectionLineComponent={connectionLineComponent}
            isValidConnection={isValidConnection}
            connectionRadius={20}
            defaultMarkerColor={EDGE_COLOR}
            onNodesChange={handleNodesChange}
            onEdgesChange={onEdgesChange}
            onConnectStart={onConnectStart}
            onConnect={onConnect}
            onConnectEnd={onConnectEnd}
            onReconnectStart={onReconnectStart}
            onReconnect={onReconnect}
            onReconnectEnd={onReconnectEnd}
            onNodeDragStart={() => snapshotStructural()}
            onNodeDragStop={onNodeDragStop}
            onNodeDoubleClick={(_, node) => {
              setSelection({ kind: 'node', id: node.id })
              setEditingLabelId(node.id)
            }}
            onBeforeDelete={onBeforeDelete}
            onNodesDelete={() => markEdited()}
            onEdgesDelete={() => markEdited()}
            onSelectionChange={onSelectionChange}
            deleteKeyCode={DELETE_KEY_CODES}
            fitView
          >
            <Background gap={16} />
            <HelperLines horizontal={helperLines.horizontal} vertical={helperLines.vertical} />
            <MiniMap nodeColor={miniMapNodeColor} pannable zoomable />
            <Controls />
            <Toolbar
              onUndo={undo}
              onRedo={redo}
              canUndo={canUndo}
              canRedo={canRedo}
              onDuplicate={duplicate}
              onDelete={deleteSelected}
              onPreviewRender={previewRender}
              onPreviewJson={previewJson}
              onValidate={runValidation}
              onHelp={() => setHelpOpen(true)}
            />
          </ReactFlow>
          </EditorColorModeContext.Provider>
          </EdgeRouteEditContext.Provider>
          </NodeLabelEditContext.Provider>
          </NodeResizeContext.Provider>
          {nodes.length === 0 ? <EmptyOverlay /> : null}
          {fileDragOver ? (
            // pointer-events-none so the drop still reaches the canvas's onDrop.
            <div className="pointer-events-none absolute inset-0 z-50 flex items-center justify-center bg-accent/5 p-6">
              <div className="rounded-xl border-2 border-dashed border-accent bg-surface/95 px-6 py-5 text-center shadow-lg">
                <p className="text-sm font-medium text-fg">Drop to open this diagram</p>
                <p className="mt-1 text-xs text-fg-muted">
                  Release the <code className="font-mono">.gp.json</code> file to load it
                </p>
              </div>
            </div>
          ) : null}
        </div>
        <Rail
          side="right"
          title="Properties"
          width={inspector.width}
          collapsed={inspector.collapsed}
          onWidthChange={inspector.setWidth}
          onToggle={inspector.toggle}
          min={220}
          max={420}
        >
          <PropertyPanel
            diagramType={baseDiagram.diagramType}
            selection={panelSelection}
            onNodeChange={updateNode}
            onEdgeChange={updateEdge}
            selectedNodeCount={selectedNodeIds.length}
            onBulkNodeStyle={(patch) => bulkStyleNodes(selectedNodeIds, patch)}
            issues={selectionIssues}
          />
        </Rail>
      </main>
      <StatusBar nodeCount={nodes.length} edgeCount={edges.length} saveText={saveText} extra={<ZoomStatus />} />
      <ShortcutsHelp open={helpOpen} onClose={() => setHelpOpen(false)} />
      <Modal open={confirmState !== null} onClose={() => setConfirmState(null)} title="Confirm">
        <p className="mb-4 text-sm text-fg">{confirmState?.message}</p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmState(null)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={() => confirmState?.onConfirm()}>
            {confirmState?.confirmLabel ?? 'Confirm'}
          </Button>
        </div>
      </Modal>
      <Modal
        open={externalReviewOpen && externalChange !== null}
        onClose={() => setExternalReviewOpen(false)}
        title="Source changes"
        size="xl"
      >
        <p className="mb-3 text-xs text-fg-muted">Disk version compared with the current canvas.</p>
        <JsonDiffView rows={externalReview} raw="" showRaw={false} />
      </Modal>
      <Modal
        open={renderPreview.status !== 'closed'}
        onClose={closeRenderPreview}
        title="Backend render preview"
        size="xl"
      >
        <p className="mb-3 text-xs text-fg-muted">
          Server-rendered SVG from the same canonical JSON a save would send. Compare the shapes
          against the canvas.
        </p>
        {renderPreview.status === 'loading' ? (
          <p className="text-sm text-fg">Rendering…</p>
        ) : null}
        {renderPreview.status === 'error' ? (
          <p className="text-sm text-danger">{renderPreview.message}</p>
        ) : null}
        {renderPreview.status === 'ready' ? (
          <div
            className="overflow-auto rounded border border-line bg-white p-2 [&_svg]:h-auto [&_svg]:max-w-full"
            data-testid="render-preview-svg"
            // The SVG comes from our own backend render service (trusted, no user HTML).
            dangerouslySetInnerHTML={{ __html: renderPreview.svg }}
          />
        ) : null}
      </Modal>
      <Modal
        open={jsonPreviewOpen}
        onClose={() => setJsonPreviewOpen(false)}
        title="Diagram JSON"
        size="xl"
      >
        <div className="mb-2 flex items-center justify-between gap-2">
          <p className="text-xs text-fg-muted">
            {jsonPreview && jsonPreview.stats.added + jsonPreview.stats.removed > 0
              ? `Canonical JSON (what a save would write) — ${jsonPreview.stats.added} added, ${jsonPreview.stats.removed} removed since last save`
              : 'Canonical JSON (what a save would write) — no changes since last save'}
          </p>
          <div className="flex shrink-0 items-center gap-1">
            <Button variant="ghost" size="sm" onClick={() => setJsonRaw((v) => !v)}>
              {jsonRaw ? 'Show diff' : 'Show raw'}
            </Button>
            <Button variant="secondary" size="sm" onClick={copyJson}>
              Copy
            </Button>
          </div>
        </div>
        <JsonDiffView
          rows={jsonPreview?.rows ?? []}
          raw={jsonPreview?.current ?? ''}
          showRaw={jsonRaw}
        />
      </Modal>
    </div>
  )
}

function DiagramEditor({ loadId, ...props }: {
  session: DiagramSession
  onHome: () => void
  onOpenLocal: () => void
  onOpenDroppedResult: (res: LocalDiagramResult) => void
  onSessionChange: (source: DiagramSource, diagram: GraphPilotDiagram, expectedSource: DiagramSource, expectedLoadId: number) => void
  onSessionReload: (source: DiagramSource, diagram: GraphPilotDiagram, force?: boolean) => void
  loadId: number
}) {
  // ReactFlowProvider gives `DiagramCanvas` access to `useReactFlow()`
  // (`screenToFlowPosition`) for the drag-from-palette drop handling. Keyed on the
  // per-open `loadId` (not the path) so opening any diagram — including another file
  // with the same name, or re-opening the same path — remounts the canvas with fresh
  // state.
  return (
    <ReactFlowProvider>
      <DiagramCanvas {...props} key={loadId} />
    </ReactFlowProvider>
  )
}

export default function EditorPage() {
  const [state, setState] = useState<EditorState>({ status: 'loading' })
  const { notify } = useToast()
  // Guards against a stale load response overwriting a newer one when the user
  // opens diagrams in quick succession.
  const loadSeqRef = useRef(0)
  const activeSourceRef = useRef<DiagramSource | null>(null)
  const [recents, setRecents] = useState(() => getRecents())

  const updateSourceUrl = useCallback((source: DiagramSource) => {
    activeSourceRef.current = source
    const url = new URL(window.location.href)
    if (source.kind === 'workspace') {
      url.searchParams.set('diagramPath', source.path)
      addRecent(source.path)
      setRecents(getRecents())
    } else {
      url.searchParams.delete('diagramPath')
    }
    window.history.replaceState(null, '', url)
  }, [])

  const onSessionChange = useCallback((source: DiagramSource, diagram: GraphPilotDiagram, expectedSource: DiagramSource, expectedLoadId: number) => {
    if (loadSeqRef.current !== expectedLoadId || !activeSourceRef.current || !sameDiagramSource(activeSourceRef.current, expectedSource)) return
    updateSourceUrl(source)
    setState((current) => current.status === 'loaded' && sameDiagramSource(current.session.source, expectedSource)
      ? { status: 'loaded', session: { source, diagram, loadId: current.session.loadId } }
      : current)
  }, [updateSourceUrl])

  const onSessionReload = useCallback((source: DiagramSource, diagram: GraphPilotDiagram, force = false) => {
    if (!force && activeSourceRef.current && !sameDiagramSource(activeSourceRef.current, source)) return
    if (!force && activeSourceRef.current && sameDiagramRevision(activeSourceRef.current, source)) return
    const loadId = ++loadSeqRef.current
    updateSourceUrl(source)
    setState({ status: 'loaded', session: { source, diagram, loadId } })
  }, [updateSourceUrl])

  const openDiagram = useCallback((path: string) => {
    const trimmed = path.trim()
    if (!trimmed) return
    const seq = ++loadSeqRef.current
    activeSourceRef.current = { kind: 'workspace', path: trimmed, revision: '' }
    // Keep the URL in sync so the loaded diagram stays shareable/refreshable.
    const url = new URL(window.location.href)
    url.searchParams.set('diagramPath', trimmed)
    window.history.replaceState(null, '', url)
    setState({ status: 'loading' })
    loadDiagram(trimmed)
      .then((response) => {
        if (loadSeqRef.current !== seq) return
        const source: DiagramSource = {
          kind: 'workspace',
          path: response.diagramPath,
          revision: response.revision,
        }
        updateSourceUrl(source)
        setState({ status: 'loaded', session: { source, diagram: response.diagram, loadId: seq } })
      })
      .catch((error: unknown) => {
        if (loadSeqRef.current !== seq) return
        if (error instanceof DiagramApiError) {
          setState({ status: 'error', code: error.code, message: error.message })
        } else {
          setState({ status: 'error', code: 'unknown_error', message: String(error) })
        }
      })
  }, [updateSourceUrl])

  // Open any file from disk via the File System Access API. The diagram has no
  // workspace path (it saves back through the handle), so it is not added to the
  // path-based recents. We clear any `?diagramPath=` query so a reload doesn't
  // re-open the previous MCP diagram instead of this picked file.
  // Adopt a parsed local diagram (from the picker or a drop) as the loaded state.
  // A null handle means read-only (no in-place Save) — the user can Save As.
  const loadLocalResult = useCallback(
    async (res: LocalDiagramResult) => {
      ++loadSeqRef.current
      const source: DiagramSource = res.handle
        ? { kind: 'external-file', name: res.name, handle: res.handle, revision: res.revision }
        : { kind: 'read-only-file', name: res.name || res.diagram.name || 'diagram' }
      onSessionReload(source, res.diagram, true)
    },
    [onSessionReload],
  )

  const openLocalFile = useCallback(async () => {
    try {
      const res = await openLocalDiagram()
      if (!res) return // user cancelled, or the API is unsupported
      void loadLocalResult(res)
    } catch (error) {
      // Surface the failure as a toast and keep a loaded diagram on screen rather
      // than replacing the whole editor with the error state.
      const invalid = error instanceof SyntaxError || (error instanceof Error && error.message.includes('GraphPilot diagram'))
      const message = invalid
        ? 'The selected file is not a valid GraphPilot diagram (.gp.json).'
        : `Could not open the selected file: ${error instanceof Error ? error.message : String(error)}`
      notify('error', message)
      setState((prev) => (prev.status === 'loaded' ? prev : { status: 'error', code: invalid ? 'invalid_json' : 'open_failed', message }))
    }
  }, [loadLocalResult, notify])

  // Open a .gp.json dropped onto the landing page.
  const openDroppedFile = useCallback(
    async (dataTransfer: DataTransfer) => {
      try {
        const res = await openDroppedDiagram(dataTransfer)
        if (!res) return
        await loadLocalResult(res)
      } catch (error) {
        const invalid = error instanceof SyntaxError || (error instanceof Error && error.message.includes('GraphPilot diagram'))
        const message = invalid
          ? 'The dropped file is not a valid GraphPilot diagram (.gp.json).'
          : `Could not open the dropped file: ${error instanceof Error ? error.message : String(error)}`
        notify('error', message)
        setState((prev) => (prev.status === 'loaded' ? prev : { status: 'error', code: invalid ? 'invalid_json' : 'open_failed', message }))
      }
    },
    [loadLocalResult, notify],
  )

  const newBlankDiagram = useCallback((diagramType: CatalogDiagramType) => {
    const diagram = createBlankDiagram(diagramType)
    const source: DiagramSource = { kind: 'unsaved', name: diagram.name }
    onSessionReload(source, diagram, true)
  }, [onSessionReload])

  const goHome = useCallback(() => {
    ++loadSeqRef.current
    activeSourceRef.current = null
    const url = new URL(window.location.href)
    url.searchParams.delete('diagramPath')
    window.history.replaceState(null, '', url)
    setState({ status: 'missing-path' })
  }, [])

  const handleClearRecents = useCallback(() => {
    clearRecents()
    setRecents([])
  }, [])

  useEffect(() => {
    const diagramPath = new URLSearchParams(window.location.search).get('diagramPath')
    if (!diagramPath) {
      setState({ status: 'missing-path' })
      return
    }
    openDiagram(diagramPath)
  }, [openDiagram])

  if (state.status === 'missing-path') {
    return (
      <Home
        fsaSupported={isFileSystemAccessSupported()}
        onOpenFile={openLocalFile}
        onNewDiagram={newBlankDiagram}
        recents={recents}
        onOpenRecent={openDiagram}
        onClearRecents={handleClearRecents}
        onDropFile={openDroppedFile}
      />
    )
  }

  if (state.status === 'loading') {
    return <Message title="Loading diagram…" />
  }

  if (state.status === 'error') {
    return (
      <Home
        fsaSupported={isFileSystemAccessSupported()}
        onOpenFile={openLocalFile}
        onNewDiagram={newBlankDiagram}
        recents={recents}
        onOpenRecent={openDiagram}
        onClearRecents={handleClearRecents}
        onDropFile={openDroppedFile}
        error={{ code: state.code, message: state.message }}
      />
    )
  }

  return (
    <DiagramEditor
      session={state.session}
      onHome={goHome}
      onOpenLocal={openLocalFile}
      onOpenDroppedResult={loadLocalResult}
      onSessionChange={onSessionChange}
      onSessionReload={onSessionReload}
      loadId={state.session.loadId}
    />
  )
}
