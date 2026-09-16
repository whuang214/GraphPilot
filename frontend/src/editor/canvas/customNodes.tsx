import { useEffect, useRef, useState } from 'react'
import type { CSSProperties, PointerEvent as ReactPointerEvent, ReactNode } from 'react'
import { Handle, NodeResizer, Position, useStore, useUpdateNodeInternals } from '@xyflow/react'
import type { NodeProps } from '@xyflow/react'
import type {
  GraphPilotElementOrigin,
  GraphPilotNodeData,
  GraphPilotNodeStyle,
} from '@/types/diagram'
import { MIN_NODE_HEIGHT, MIN_NODE_WIDTH, useNodeResize } from '@/editor/lib/resize'
import { useNodeLabelEdit } from '@/editor/lib/inlineLabel'
import { useEditorColorMode } from '@/editor/hooks/editorColorMode'
import { featureCompartments } from '@/editor/lib/bddCompartments'
import { nodePrimitive, semanticKeyword, semanticLabel } from '@/editor/lib/elementCatalog'
import { defaultNodeSize } from '@/editor/lib/palette'
import { borderCss, resolveStyle } from '@/editor/lib/nodeStyle'
import type { ResolvedStyle } from '@/editor/lib/nodeStyle'
import { attachmentProfile, resolveAttachmentAnchor } from '@/editor/lib/edgeRouting'
import type { NodeRect } from '@/editor/lib/edgeRouting'

// React Flow node `data` shape used by the custom renderers. The forward adapter
// (`graphPilotToReactFlow`) passes the canonical node `data` plus `gpStyle` (the
// GraphPilot visual style) so each renderer can draw its type-specific shape
// without the reverse adapter ever reading these display-only fields back.
export interface GpNodeData extends Omit<GraphPilotNodeData, 'label'> {
  label?: string
  gpStyle?: GraphPilotNodeStyle
  /** The element's provenance, so the canvas can mark what was assumed rather than cited. */
  gpOrigin?: GraphPilotElementOrigin
}

const fillBox: CSSProperties = {
  width: '100%',
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  textAlign: 'center',
  boxSizing: 'border-box',
  padding: 4,
  fontFamily: 'system-ui, sans-serif',
  fontSize: 12,
  lineHeight: 1.2,
  overflow: 'hidden',
}

// Each side is one narrow connection strip rather than one center dot. React Flow
// still owns the connection lifecycle, while the exact pointer positions are saved
// as normalized route anchors by EditorPage.
const HANDLE_BASE_STYLE: CSSProperties = {
  zIndex: 5,
  background: 'rgba(0, 0, 0, 0.001)',
  border: 0,
  borderRadius: 0,
  cursor: 'crosshair',
}

const CONTROL_HANDLE_PRIMITIVES = new Set(['initial', 'final', 'flow-final'])
const CURVED_HANDLE_PRIMITIVES = new Set([...CONTROL_HANDLE_PRIMITIVES, 'ellipse', 'actor'])

interface HandleSpec {
  id: string
  type: 'source' | 'target'
  position: Position
  boundary: Position
  cardinal?: boolean
  sample?: number
  sampleCount?: number
}

// Every side gets BOTH a source and a target strip. The source strip renders last
// so a new drag has stable source→target direction under ConnectionMode.Loose;
// either strip remains a valid drop target.
function handleSpecs(primary: 'vertical' | 'horizontal', primitive: string | undefined, rect: NodeRect | undefined, zoom: number): HandleSpec[] {
  const positions = primary === 'vertical'
    ? [Position.Top, Position.Bottom, Position.Left, Position.Right]
    : [Position.Left, Position.Right, Position.Top, Position.Bottom]
  if (rect && CURVED_HANDLE_PRIMITIVES.has(primitive ?? '')) {
    const bounds = attachmentProfile(rect).bounds
    const a = bounds.w / 2
    const b = bounds.h / 2
    const perimeter = Math.PI * (3 * (a + b) - Math.sqrt((3 * a + b) * (a + 3 * b)))
    const sampleCount = Math.min(48, Math.max(16, Math.ceil(perimeter * Math.max(zoom, 0.01) / 64) * 4))
    const quarter = sampleCount / 4
    const samples = Array.from({ length: sampleCount }, (_, sample) => {
      const angle = -Math.PI / 2 + sample * Math.PI * 2 / sampleCount
      const x = Math.cos(angle)
      const y = Math.sin(angle)
      const boundary = Math.abs(x) >= Math.abs(y)
        ? x >= 0 ? Position.Right : Position.Left
        : y >= 0 ? Position.Bottom : Position.Top
      return { boundary, sample, sampleCount }
    })
    const t = ({ boundary, sample, sampleCount }: { boundary: Position; sample: number; sampleCount: number }): HandleSpec => ({ id: sample % quarter === 0 ? `gp-${boundary}-t` : `gp-${boundary}-${sample}-t`, type: 'target', position: boundary, boundary, sample, sampleCount })
    const s = ({ boundary, sample, sampleCount }: { boundary: Position; sample: number; sampleCount: number }): HandleSpec => ({ id: sample % quarter === 0 ? `gp-${boundary}-s` : `gp-${boundary}-${sample}-s`, type: 'source', position: boundary, boundary, sample, sampleCount })
    return [...samples.map(t), ...samples.map(s)]
  }
  const projected = primitive === 'diamond'
  const t = (boundary: Position): HandleSpec => ({ id: `gp-${boundary}-t`, type: 'target', position: projected ? Position.Top : boundary, boundary })
  const s = (boundary: Position): HandleSpec => ({ id: `gp-${boundary}-s`, type: 'source', position: projected ? Position.Top : boundary, boundary })
  if (!projected) return [...positions.map(t), ...positions.map(s)]
  const cardinalTarget = (boundary: Position): HandleSpec => ({ id: `gp-cardinal-${boundary}-t`, type: 'target', position: boundary, boundary, cardinal: true })
  const cardinalSource = (boundary: Position): HandleSpec => ({ id: `gp-cardinal-${boundary}-s`, type: 'source', position: boundary, boundary, cardinal: true })
  return [...positions.map(t), ...positions.map(s), ...positions.map(cardinalTarget), ...positions.map(cardinalSource)]
}

function quadrantHandleStyle(position: Position, clipPath: string): CSSProperties {
  if (position === Position.Top) return { ...HANDLE_BASE_STYLE, top: 0, right: 'auto', bottom: 'auto', left: 0, width: '50%', height: '50%', transform: 'none', clipPath }
  if (position === Position.Right) return { ...HANDLE_BASE_STYLE, top: 0, right: 'auto', bottom: 'auto', left: '50%', width: '50%', height: '50%', transform: 'none', clipPath }
  if (position === Position.Bottom) return { ...HANDLE_BASE_STYLE, top: '50%', right: 'auto', bottom: 'auto', left: '50%', width: '50%', height: '50%', transform: 'none', clipPath }
  return { ...HANDLE_BASE_STYLE, top: '50%', right: 'auto', bottom: 'auto', left: 0, width: '50%', height: '50%', transform: 'none', clipPath }
}

function profileHandleStyle(sample: number, sampleCount: number, rect: NodeRect, zoom: number): CSSProperties {
  const profile = attachmentProfile(rect).bounds
  const scale = Math.max(zoom, 0.01)
  const angle = -Math.PI / 2 + sample * Math.PI * 2 / sampleCount
  const rx = Math.max(profile.w / 2, 0.001)
  const ry = Math.max(profile.h / 2, 0.001)
  const cos = Math.cos(angle)
  const sin = Math.sin(angle)
  const normalLength = Math.hypot(cos / rx, sin / ry)
  const shift = 4 / scale
  const size = 16 / scale
  const x = profile.x + rx + rx * cos + cos / rx / normalLength * shift
  const y = profile.y + ry + ry * sin + sin / ry / normalLength * shift
  return {
    ...HANDLE_BASE_STYLE,
    top: y - size / 2,
    right: 'auto',
    bottom: 'auto',
    left: x - size / 2,
    width: size,
    height: size,
    transform: 'none',
    borderRadius: '50%',
  }
}

function handleStyle(handle: HandleSpec, primitive: string | undefined, rect: NodeRect | undefined, zoom: number): CSSProperties {
  if (primitive === 'diamond' && handle.cardinal) {
    const size = 16 / Math.max(zoom, 0.01)
    const position = handle.boundary === Position.Top
      ? { left: '50%', top: 0 }
      : handle.boundary === Position.Right
        ? { left: '100%', top: '50%' }
        : handle.boundary === Position.Bottom
          ? { left: '50%', top: '100%' }
          : { left: 0, top: '50%' }
    return { ...HANDLE_BASE_STYLE, ...position, right: 'auto', bottom: 'auto', width: size, height: size, transform: 'translate(-50%, -50%)', borderRadius: '50%' }
  }
  if (primitive === 'diamond') {
    const descending = 'polygon(0 70%, 30% 100%, 100% 30%, 70% 0)'
    const ascending = 'polygon(0 0, 30% 0, 100% 70%, 100% 100%, 70% 100%, 0 30%)'
    return quadrantHandleStyle(handle.boundary, handle.boundary === Position.Top || handle.boundary === Position.Bottom ? descending : ascending)
  }
  if (rect && handle.sample !== undefined && handle.sampleCount !== undefined) return profileHandleStyle(handle.sample, handle.sampleCount, rect, zoom)
  if (handle.boundary === Position.Top) return { ...HANDLE_BASE_STYLE, top: 0, left: 0, width: '100%', height: 12, transform: 'translateY(-50%)' }
  if (handle.boundary === Position.Bottom) return { ...HANDLE_BASE_STYLE, right: 0, bottom: 0, left: 0, width: '100%', height: 12, transform: 'translateY(50%)' }
  if (handle.boundary === Position.Left) return { ...HANDLE_BASE_STYLE, top: 0, bottom: 0, left: 0, width: 12, height: '100%', transform: 'translateX(-50%)' }
  return { ...HANDLE_BASE_STYLE, top: 0, right: 0, bottom: 0, width: 12, height: '100%', transform: 'translateX(50%)' }
}

function handleBoundaryLabel(position: Position, primitive: string | undefined, sample: number | undefined, cardinal: boolean | undefined): string {
  if (primitive === 'diamond' && cardinal) return `${position} diamond vertex`
  if (sample !== undefined) {
    const profile = CONTROL_HANDLE_PRIMITIVES.has(primitive ?? '')
      ? 'control circle'
      : primitive === 'actor' ? 'actor figure' : 'curved boundary'
    return `${position} ${profile} point ${sample + 1}`
  }
  const quadrant = position === Position.Top
    ? 'upper-left'
    : position === Position.Right
      ? 'upper-right'
      : position === Position.Bottom
        ? 'lower-right'
        : 'lower-left'
  if (primitive === 'diamond') return `${quadrant} diamond edge`
  return `${position} boundary`
}

function isCardinalHandle(handle: HandleSpec, primitive: string | undefined): boolean {
  if (handle.cardinal) return true
  if (primitive === 'diamond') return false
  if (handle.sample === undefined) return true
  return handle.sampleCount !== undefined && handle.sample % (handle.sampleCount / 4) === 0
}

function NodeHandles({ id, primary, primitive, rect }: { id: string; primary: 'vertical' | 'horizontal'; primitive?: string; rect?: NodeRect }) {
  const zoom = useStore((state) => state.transform[2])
  const updateNodeInternals = useUpdateNodeInternals()
  const handles = handleSpecs(primary, primitive, rect, zoom)
  const curved = Boolean(rect && CURVED_HANDLE_PRIMITIVES.has(primitive ?? ''))
  const internalsKey = curved ? `${handles.length}:${rect?.w}:${rect?.h}:${rect?.label ?? ''}` : ''
  const previousInternalsKey = useRef(internalsKey)
  useEffect(() => {
    if (curved && previousInternalsKey.current !== internalsKey) updateNodeInternals(id)
    previousInternalsKey.current = internalsKey
  }, [curved, id, internalsKey, updateNodeInternals])
  const [indicator, setIndicator] = useState<{ x: number; y: number; snapped?: string } | null>(null)
  const updateIndicator = (event: ReactPointerEvent<HTMLDivElement>) => {
    const node = event.currentTarget.closest('.react-flow__node') as HTMLElement | null
    if (!node) return
    const bounds = node.getBoundingClientRect()
    const width = node.offsetWidth || bounds.width
    const height = node.offsetHeight || bounds.height
    const location = resolveAttachmentAnchor(
      { x: 0, y: 0, w: width, h: height, primitive, label: rect?.label },
      {
        x: (event.clientX - bounds.left) * width / Math.max(bounds.width, 1),
        y: (event.clientY - bounds.top) * height / Math.max(bounds.height, 1),
      },
      zoom,
    )
    setIndicator({ ...location.point, snapped: location.snapped })
  }
  return (
    <>
      {handles.map((handle) => {
        const cardinal = isCardinalHandle(handle, primitive)
        return (
          <Handle
            key={`${handle.type}-${handle.id}`}
            id={handle.id}
            type={handle.type}
            position={handle.position}
            style={handleStyle(handle, primitive, rect, zoom)}
            aria-label={`${handle.type === 'source' ? 'Start' : 'Finish'} relationship on ${handleBoundaryLabel(handle.boundary, primitive, handle.sample, handle.cardinal)}`}
            aria-hidden={!cardinal}
            data-attachment-side={handle.boundary}
            data-attachment-sample={handle.sample}
            data-attachment-cardinal={cardinal ? 'true' : 'false'}
            tabIndex={cardinal ? 0 : -1}
            onPointerMove={updateIndicator}
            onPointerLeave={() => setIndicator(null)}
          />
        )
      })}
      {indicator ? (
        <div
          data-testid="boundary-indicator"
          data-anchor-kind={indicator.snapped ? 'cardinal' : 'custom'}
          aria-hidden
          style={{
            position: 'absolute',
            left: indicator.x,
            top: indicator.y,
            zIndex: 6,
            width: 10,
            height: 10,
            transform: 'translate(-50%, -50%)',
            borderRadius: '50%',
            border: '2px solid var(--surface)',
            background: 'var(--accent)',
            pointerEvents: 'none',
          }}
        />
      ) : null}
    </>
  )
}

function StereotypeLabel({ text, color }: { text: string; color: string }) {
  return <div style={{ fontSize: 10, fontStyle: 'italic', color }}>«{text}»</div>
}

// In-shape label input shown while a node is being renamed.
// `nodrag` keeps React Flow from starting a node drag while typing; keydown is
// stopped so the editor's shortcuts (and React Flow) don't act on the keystrokes.
// Commits on Enter / blur (only if changed), cancels on Escape.
function LabelInput({
  initial,
  onCommit,
  onCancel,
}: {
  initial: string
  onCommit: (value: string) => void
  onCancel: () => void
}) {
  const [value, setValue] = useState(initial)
  // One-shot guard: Escape cancels, but the resulting blur must not then commit
  // the discarded value, and Enter+blur must not commit twice.
  const doneRef = useRef(false)
  const commit = () => {
    if (doneRef.current) return
    doneRef.current = true
    if (value !== initial) onCommit(value)
    else onCancel()
  }
  const cancel = () => {
    if (doneRef.current) return
    doneRef.current = true
    onCancel()
  }
  return (
    <input
      className="nodrag"
      autoFocus
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onFocus={(e) => e.currentTarget.select()}
      onPointerDown={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
      onKeyDown={(e) => {
        e.stopPropagation()
        if (e.key === 'Enter') commit()
        else if (e.key === 'Escape') cancel()
      }}
      onBlur={commit}
      style={{
        width: '92%',
        font: 'inherit',
        textAlign: 'center',
        border: '1px solid #2563eb',
        borderRadius: 4,
        padding: '1px 3px',
        background: '#ffffff',
        color: '#111111',
      }}
    />
  )
}

// Renders the node label, or an in-shape input when this node is being edited
// (driven by the editor's label-edit context; a plain label outside the editor).
export function EditableLabel({ id, text }: { id: string; text?: string }) {
  const api = useNodeLabelEdit()
  if (api && api.editingId === id) {
    return <LabelInput initial={text ?? ''} onCommit={(v) => api.commit(id, v)} onCancel={api.cancel} />
  }
  return <>{text}</>
}

// On-canvas resize handles, shown only when the node is selected. The live size
// is pushed into the node `style` (via the editor's resize context) so the save
// round-trip stays byte-stable; a no-op when rendered outside the editor (no
// provider), e.g. in isolation tests.
function ResizeControls({ id, selected }: { id: string; selected?: boolean }) {
  const api = useNodeResize()
  if (!api) return null
  return (
    <NodeResizer
      isVisible={!!selected}
      minWidth={MIN_NODE_WIDTH}
      minHeight={MIN_NODE_HEIGHT}
      handleStyle={{ width: 9, height: 9 }}
      onResizeStart={api.start}
      onResize={(_, params) => api.resize(id, params.width, params.height)}
    />
  )
}

interface ShapeProps {
  id: string
  data: GpNodeData
  selected?: boolean
  style: ResolvedStyle
  semanticType: string
  ariaLabel: string
  width: number
  height: number
}

/**
 * Mark an element nobody could establish from the source.
 *
 * A diagram is only worth trusting if you can see which parts of it are claims about the
 * repository and which are somebody's inference. That distinction is authored, validated,
 * and saved on every element — and until now it was drawn nowhere, so an assumption and a
 * cited fact looked identical on the canvas.
 *
 * Two assurances are marked, and both are admissions. `assumed` is a judgement the source
 * does not establish; `user` is something a person drew on the canvas, which no draft
 * authored and no citation backs. `grounded` is the norm in a repository-backed diagram
 * and badging all of it would be noise that teaches a reader to ignore badges;
 * `conceptual` describes a whole diagram that claims nothing, so a per-element mark says
 * nothing new.
 *
 * The tooltip is the element's own `rationale`, which travels inside the diagram.
 */
const BADGES = {
  assumed: { glyph: '?', label: 'assumed', fallback: 'Assumed: not established by the cited source.' },
  user: { glyph: '\u270e', label: 'drawn by hand', fallback: 'Added in the editor by a person.' },
} as const

function AssuranceBadge({ origin, rect }: { origin?: GraphPilotElementOrigin; rect?: NodeRect }) {
  const badge = origin && BADGES[origin.assurance as keyof typeof BADGES]
  if (!badge) return null
  // The badge belongs on the shape a reader can see, which is not always the layout box:
  // an initial node's 30px disc and an actor's stick figure sit inside a much larger box,
  // so the CSS corner left the badge floating clear of the thing it marks. For a box-
  // shaped primitive the profile is the box and this resolves to the same corner.
  const bounds = rect && attachmentProfile(rect).bounds
  return (
    <div
      className={`gp-assumed gp-assurance-${origin!.assurance}`}
      style={bounds && { top: bounds.y - 9, left: bounds.x + bounds.w - 9, right: 'auto' }}
      title={origin!.rationale || badge.fallback}
      aria-label={badge.label}
    >
      {badge.glyph}
    </div>
  )
}

function ShapeChrome({
  id,
  selected,
  primary,
  primitive,
  rect,
  origin,
  children,
}: {
  id: string
  selected?: boolean
  primary: 'vertical' | 'horizontal'
  primitive?: string
  rect?: NodeRect
  origin?: GraphPilotElementOrigin
  children: ReactNode
}) {
  return (
    <>
      <ResizeControls id={id} selected={selected} />
      <NodeHandles id={id} primary={primary} primitive={primitive} rect={rect} />
      <AssuranceBadge origin={origin} rect={rect} />
      {children}
    </>
  )
}

function strokeDasharray(style: ResolvedStyle): string | undefined {
  if (style.borderStyle === 'dashed') return `${style.borderWidth * 4} ${style.borderWidth * 3}`
  if (style.borderStyle === 'dotted') return `${style.borderWidth} ${style.borderWidth * 2}`
  return undefined
}

function NoteShape({ id, data, selected, style, ariaLabel }: ShapeProps) {
  const fold = 14
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div aria-label={ariaLabel} style={{ position: 'relative', width: '100%', height: '100%' }}>
        <div
          style={{
            ...fillBox,
            color: style.color,
            background: style.background,
            border: borderCss(style),
            paddingTop: fold / 2,
            clipPath: `polygon(0 0, calc(100% - ${fold}px) 0, 100% ${fold}px, 100% 100%, 0 100%)`,
          }}
        >
          <EditableLabel id={id} text={data.label} />
        </div>
        <svg
          width={fold}
          height={fold}
          viewBox={`0 0 ${fold} ${fold}`}
          style={{ position: 'absolute', top: 0, right: 0, overflow: 'visible' }}
          aria-hidden
        >
          <path
            d={`M0 0 L${fold} ${fold} M0 0 V${fold} H${fold}`}
            fill="none"
            stroke={style.borderColor}
            strokeWidth={style.borderWidth}
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
      </div>
    </ShapeChrome>
  )
}

function RoundedRectShape({ id, data, selected, style, ariaLabel }: ShapeProps) {
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div
        aria-label={ariaLabel}
        style={{
          ...fillBox,
          color: style.color,
          background: style.background,
          border: borderCss(style),
          borderRadius: 8,
        }}
      >
        <EditableLabel id={id} text={data.label} />
      </div>
    </ShapeChrome>
  )
}

function DiamondShape({ id, data, selected, style, ariaLabel }: ShapeProps) {
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical" primitive="diamond">
      <div aria-label={ariaLabel} style={{ position: 'relative', width: '100%', height: '100%' }}>
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          style={{ position: 'absolute', inset: 0 }}
          aria-hidden
        >
          <polygon
            points="50,1 99,50 50,99 1,50"
            fill={style.background}
            stroke={style.borderColor}
            strokeWidth={style.borderWidth}
            strokeDasharray={strokeDasharray(style)}
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        <div style={{ ...fillBox, position: 'relative', color: style.color, padding: '18% 22%' }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

type ControlPrimitive = 'initial' | 'final' | 'flow-final'

function ControlNodeShape(props: ShapeProps & { primitive: ControlPrimitive }) {
  const { id, data, selected, style, ariaLabel, primitive, width, height } = props
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical" primitive={primitive} rect={{ x: 0, y: 0, w: width, h: height, primitive, label: data.label }}>
      <div
        aria-label={ariaLabel}
        style={{ ...fillBox, padding: 0, flexDirection: 'column', gap: 0, color: style.color }}
      >
        <svg width="34" height="34" viewBox="0 0 34 34" aria-hidden style={{ flexShrink: 1, minHeight: 0 }}>
          {primitive === 'initial' ? (
            <circle cx="17" cy="17" r="15" fill={style.borderColor} stroke={style.borderColor} strokeWidth={style.borderWidth} />
          ) : (
            <>
              <circle cx="17" cy="17" r="15" fill={style.background} stroke={style.borderColor} strokeWidth={style.borderWidth} />
              {primitive === 'final' ? (
                <circle cx="17" cy="17" r="7.5" fill={style.borderColor} stroke="none" />
              ) : (
                <g stroke={style.borderColor} strokeWidth={style.borderWidth} strokeLinecap="round">
                  <line x1="9" y1="9" x2="25" y2="25" />
                  <line x1="25" y1="9" x2="9" y2="25" />
                </g>
              )}
            </>
          )}
        </svg>
        <div style={{ fontWeight: 600 }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function BarShape({ id, data, selected, style, ariaLabel }: ShapeProps) {
  const hasLabel = Boolean(data.label)
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div
        aria-label={ariaLabel}
        style={{ ...fillBox, position: 'relative', padding: 0, color: style.color }}
      >
        <div
          style={{
            position: 'absolute',
            top: hasLabel ? 6 : '50%',
            left: 0,
            width: '100%',
            height: 'clamp(6px, 40%, 16px)',
            transform: hasLabel ? undefined : 'translateY(-50%)',
            background: style.borderColor,
          }}
        />
        <div style={{ position: 'absolute', right: 4, bottom: 1, left: 4 }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function ActorShape({ id, data, selected, style, ariaLabel, width, height }: ShapeProps) {
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="horizontal" primitive="actor" rect={{ x: 0, y: 0, w: width, h: height, primitive: 'actor', label: data.label }}>
      <div
        aria-label={ariaLabel}
        style={{ ...fillBox, flexDirection: 'column', gap: 2, color: style.color }}
      >
        <svg width="34" height="46" viewBox="0 0 34 46" aria-hidden style={{ flexShrink: 0 }}>
          <g fill="none" stroke={style.borderColor} strokeWidth={style.borderWidth} strokeLinecap="round">
            <circle cx="17" cy="8" r="6" fill={style.background} />
            <line x1="17" y1="14" x2="17" y2="30" />
            <line x1="5" y1="20" x2="29" y2="20" />
            <line x1="17" y1="30" x2="7" y2="44" />
            <line x1="17" y1="30" x2="27" y2="44" />
          </g>
        </svg>
        <div>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function EllipseShape({ id, data, selected, style, ariaLabel, width, height }: ShapeProps) {
  const extensionPoints = Array.isArray(data.extensionPoints)
    ? data.extensionPoints.map((point) => String(point))
    : []
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="horizontal" primitive="ellipse" rect={{ x: 0, y: 0, w: width, h: height, primitive: 'ellipse', label: data.label }}>
      <div
        aria-label={ariaLabel}
        style={{
          ...fillBox,
          flexDirection: 'column',
          color: style.color,
          background: style.background,
          border: borderCss(style),
          borderRadius: '50%',
          padding: '5% 12%',
        }}
      >
        <div style={{ transform: extensionPoints.length ? 'translateY(-2px)' : undefined }}>
          <EditableLabel id={id} text={data.label} />
        </div>
        {extensionPoints.length ? (
          <div style={{ width: '84%', marginTop: 3, borderTop: `1px solid ${style.borderColor}`, paddingTop: 1 }}>
            <div style={{ fontSize: 9, lineHeight: 1.15, fontStyle: 'italic' }}>extension points</div>
            <div style={{ fontSize: 9, lineHeight: 1.15 }}>{extensionPoints.join(', ')}</div>
          </div>
        ) : null}
      </div>
    </ShapeChrome>
  )
}

function ContainerShape({ id, data, selected, style, ariaLabel }: ShapeProps) {
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="horizontal">
      <div
        aria-label={ariaLabel}
        style={{
          width: '100%',
          height: '100%',
          boxSizing: 'border-box',
          border: borderCss(style),
          borderRadius: 8,
          background: 'transparent',
          color: style.color,
          fontFamily: 'system-ui, sans-serif',
          fontSize: 12,
          fontWeight: 600,
          padding: '6px 10px',
          overflow: 'hidden',
        }}
      >
        <EditableLabel id={id} text={data.label} />
      </div>
    </ShapeChrome>
  )
}

function keyedItems(items: string[]): Array<{ key: string; text: string }> {
  const occurrences = new Map<string, number>()
  return items.map((text) => {
    const occurrence = occurrences.get(text) ?? 0
    occurrences.set(text, occurrence + 1)
    return { key: `${text}\u0000${occurrence}`, text }
  })
}

function ClassifierShape(props: ShapeProps) {
  const { id, data, selected, style, semanticType, ariaLabel } = props
  const primary = typeof data.stereotype === 'string' ? data.stereotype.trim() : ''
  const keyword = semanticType === 'block' && primary ? primary : semanticKeyword(semanticType)
  const compartments = featureCompartments(data.features)
  const hasCompartments = compartments.length > 0
  const divider = `${style.borderWidth}px solid ${style.borderColor}`
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="horizontal">
      <div
        aria-label={ariaLabel}
        style={{
          width: '100%',
          height: '100%',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          background: style.background,
          border: borderCss(style),
          color: style.color,
          fontFamily: 'system-ui, sans-serif',
          fontSize: 12,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: hasCompartments ? 34 : '100%',
            flexShrink: 0,
            boxSizing: 'border-box',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2px 6px',
            textAlign: 'center',
            borderBottom: hasCompartments ? divider : undefined,
          }}
        >
          {keyword ? <StereotypeLabel text={keyword} color={style.color} /> : null}
          <div style={{ fontWeight: 600, lineHeight: 1.15 }}>
            <EditableLabel id={id} text={data.label} />
          </div>
        </div>
        {compartments.map((compartment, index) => (
          <div
            key={compartment.label}
            style={{
              flexShrink: 0,
              padding: '2px 8px 4px',
              textAlign: 'left',
              borderTop: index === 0 ? undefined : divider,
            }}
          >
            <div style={{ fontStyle: 'italic', fontSize: 10, lineHeight: '14.4px' }}>
              {compartment.label}
            </div>
            {keyedItems(compartment.items).map((item) => (
              <div key={item.key} style={{ fontSize: 12, lineHeight: '14.4px' }}>
                {item.text}
              </div>
            ))}
          </div>
        ))}
        {hasCompartments ? <div style={{ flex: 1, minHeight: 8 }} /> : null}
      </div>
    </ShapeChrome>
  )
}

function ObjectShape(props: ShapeProps & { datastore?: boolean }) {
  const { id, data, selected, style, semanticType, ariaLabel, datastore = false } = props
  const keyword = datastore ? semanticKeyword(semanticType) || 'datastore' : ''
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div
        aria-label={ariaLabel}
        style={{
          ...fillBox,
          flexDirection: 'column',
          color: style.color,
          background: style.background,
          border: borderCss(style),
        }}
      >
        {keyword ? <StereotypeLabel text={keyword} color={style.color} /> : null}
        <div style={{ transform: keyword ? 'translateY(2px)' : undefined }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function PinShape({ id, data, selected, style, ariaLabel }: ShapeProps) {
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div
        aria-label={ariaLabel}
        style={{ ...fillBox, flexDirection: 'column', gap: 2, color: style.color, overflow: 'visible' }}
      >
        <div style={{ width: 16, height: 16, flexShrink: 0, background: style.background, border: borderCss(style) }} />
        <div style={{ maxWidth: '100%' }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function RegionShape(props: ShapeProps & { dashed: boolean }) {
  const { id, data, selected, style, ariaLabel, dashed } = props
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div
        aria-label={ariaLabel}
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          boxSizing: 'border-box',
          color: style.color,
          fontFamily: 'system-ui, sans-serif',
          fontSize: 12,
          fontWeight: 600,
          padding: '6px 8px',
          overflow: 'hidden',
        }}
      >
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          style={{ position: 'absolute', inset: 0 }}
          aria-hidden
        >
          <rect
            x="1"
            y="1"
            width="98"
            height="98"
            fill="none"
            stroke={style.borderColor}
            strokeWidth={style.borderWidth}
            strokeDasharray={dashed ? '6 4' : strokeDasharray(style)}
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        <div style={{ position: 'relative' }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function SignalShape(props: ShapeProps & { accepting: boolean }) {
  const { id, data, selected, style, ariaLabel, accepting } = props
  const points = accepting
    ? '17,1 99,1 83,50 99,99 17,99 1,50'
    : '1,1 83,1 99,50 83,99 1,99'
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="vertical">
      <div aria-label={ariaLabel} style={{ position: 'relative', width: '100%', height: '100%' }}>
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          style={{ position: 'absolute', inset: 0 }}
          aria-hidden
        >
          <polygon
            points={points}
            fill={style.background}
            stroke={style.borderColor}
            strokeWidth={style.borderWidth}
            strokeDasharray={strokeDasharray(style)}
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        <div style={{ ...fillBox, position: 'relative', color: style.color, padding: '4px 12%' }}>
          <EditableLabel id={id} text={data.label} />
        </div>
      </div>
    </ShapeChrome>
  )
}

function PortShape(props: ShapeProps) {
  const { id, data, selected, style, semanticType, ariaLabel } = props
  const keyword = semanticKeyword(semanticType)
  const port = data.port
  const typeName = typeof port?.type === 'string' ? port.type : ''
  const conjugated = port?.isConjugated === true
  return (
    <ShapeChrome id={id} selected={selected} origin={data.gpOrigin} primary="horizontal">
      <div
        aria-label={ariaLabel}
        style={{ ...fillBox, flexDirection: 'column', gap: 2, color: style.color, overflow: 'visible' }}
      >
        <div style={{ width: 20, height: 20, flexShrink: 0, background: style.background, border: borderCss(style) }} />
        <div style={{ width: 120, maxWidth: 'none', lineHeight: 1.2 }}>
          {conjugated ? '~' : ''}
          {keyword ? <span>«{keyword}»</span> : null}
          {keyword && data.label ? ' ' : ''}
          <EditableLabel id={id} text={data.label} />
          {typeName ? `: ${typeName}` : ''}
        </div>
      </div>
    </ShapeChrome>
  )
}

// One universal node renderer: semantic identity is resolved through the frontend
// element catalog, then only the finite render primitive controls the canvas glyph.
export function GpNode({ id, data, selected, width, height }: NodeProps) {
  const d = data as GpNodeData
  const semanticType = d.semanticType ?? ''
  const style = resolveStyle(d.gpStyle, useEditorColorMode() === 'dark')
  const fallback = defaultNodeSize(semanticType)
  const props: ShapeProps = {
    id,
    data: d,
    selected,
    style,
    semanticType,
    ariaLabel: semanticLabel(semanticType) || 'Diagram node',
    width: typeof width === 'number' && Number.isFinite(width) ? width : fallback.width,
    height: typeof height === 'number' && Number.isFinite(height) ? height : fallback.height,
  }

  switch (nodePrimitive(semanticType)) {
    case 'note':
      return <NoteShape {...props} />
    case 'initial':
      return <ControlNodeShape {...props} primitive="initial" />
    case 'final':
      return <ControlNodeShape {...props} primitive="final" />
    case 'flow-final':
      return <ControlNodeShape {...props} primitive="flow-final" />
    case 'diamond':
      return <DiamondShape {...props} />
    case 'bar':
      return <BarShape {...props} />
    case 'actor':
      return <ActorShape {...props} />
    case 'ellipse':
      return <EllipseShape {...props} />
    case 'container':
      return <ContainerShape {...props} />
    case 'classifier-box':
      return <ClassifierShape {...props} />
    case 'object':
      return <ObjectShape {...props} />
    case 'datastore':
      return <ObjectShape {...props} datastore />
    case 'pin':
      return <PinShape {...props} />
    case 'partition':
      return <RegionShape {...props} dashed={false} />
    case 'region':
      return <RegionShape {...props} dashed />
    case 'send-signal':
      return <SignalShape {...props} accepting={false} />
    case 'accept-event':
      return <SignalShape {...props} accepting />
    case 'port':
      return <PortShape {...props} />
    case 'rounded-rect':
    default:
      return <RoundedRectShape {...props} />
  }
}
