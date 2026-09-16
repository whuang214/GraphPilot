import { useEffect, useId, useState } from 'react'
import type { DragEvent, ReactNode } from 'react'
import { nodePrimitive } from '@/editor/lib/elementCatalog'
import type { NodePrimitive } from '@/editor/lib/elementCatalog'
import { DRAG_MIME, organizedPaletteGroups } from '@/editor/lib/palette'
import type { PaletteItem, PaletteOrganization, PaletteScope } from '@/editor/lib/palette'
import type { RouteMode } from '@/editor/lib/edgeRouting'
import { relationshipTools } from '@/editor/lib/relationshipPresets'
import { Select } from '@/ui'

function onDragStart(event: DragEvent<HTMLDivElement>, item: PaletteItem) {
  // Keep the transfer object canonical. Palette grouping/primitive metadata is UI
  // state and must never leak into a newly-authored GraphPilot node.
  event.dataTransfer.setData(
    DRAG_MIME,
    JSON.stringify({ type: 'gpNode', semanticType: item.semanticType, label: item.label }),
  )
  event.dataTransfer.effectAllowed = 'move'
}

// A small monochrome glyph for each catalog render primitive. Semantic types that
// share a primitive therefore always get the same preview as the canvas renderer.
function ShapePreview({ primitive }: { primitive: NodePrimitive | undefined }) {
  const stroke = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.5 } as const
  let glyph: ReactNode
  switch (primitive) {
    case 'note':
      glyph = (
        <g {...stroke} strokeLinejoin="round">
          <path d="M6 4 H28 L34 10 V24 H6 Z" />
          <path d="M28 4 V10 H34" />
        </g>
      )
      break
    case 'initial':
      glyph = <circle cx="20" cy="14" r="7" fill="currentColor" />
      break
    case 'final':
      glyph = (
        <g>
          <circle cx="20" cy="14" r="8" {...stroke} />
          <circle cx="20" cy="14" r="3.5" fill="currentColor" />
        </g>
      )
      break
    case 'flow-final':
      glyph = (
        <g {...stroke} strokeLinecap="round">
          <circle cx="20" cy="14" r="8" />
          <line x1="15" y1="9" x2="25" y2="19" />
          <line x1="25" y1="9" x2="15" y2="19" />
        </g>
      )
      break
    case 'diamond':
      glyph = <polygon points="20,4 36,14 20,24 4,14" {...stroke} strokeLinejoin="round" />
      break
    case 'bar':
      glyph = <rect x="6" y="11" width="28" height="5" rx="1" fill="currentColor" />
      break
    case 'actor':
      glyph = (
        <g {...stroke} strokeLinecap="round">
          <circle cx="20" cy="6" r="3" />
          <line x1="20" y1="9" x2="20" y2="17" />
          <line x1="13" y1="12" x2="27" y2="12" />
          <line x1="20" y1="17" x2="14" y2="24" />
          <line x1="20" y1="17" x2="26" y2="24" />
        </g>
      )
      break
    case 'ellipse':
      glyph = <ellipse cx="20" cy="14" rx="16" ry="9" {...stroke} />
      break
    case 'container':
      glyph = <rect x="3" y="4" width="34" height="20" rx="3" {...stroke} />
      break
    case 'classifier-box':
      glyph = (
        <g {...stroke}>
          <rect x="6" y="4" width="28" height="20" rx="1.5" />
          <line x1="6" y1="11" x2="34" y2="11" />
        </g>
      )
      break
    case 'object':
      glyph = <rect x="5" y="6" width="30" height="16" {...stroke} />
      break
    case 'datastore':
      glyph = (
        <g {...stroke}>
          <rect x="5" y="5" width="30" height="18" />
          <line x1="5" y1="11" x2="35" y2="11" />
        </g>
      )
      break
    case 'pin':
      glyph = <rect x="15" y="9" width="10" height="10" {...stroke} />
      break
    case 'partition':
      glyph = (
        <g {...stroke}>
          <rect x="4" y="3" width="32" height="22" />
          <line x1="12" y1="3" x2="12" y2="25" />
        </g>
      )
      break
    case 'region':
      glyph = <rect x="4" y="3" width="32" height="22" rx="2" {...stroke} strokeDasharray="3 2" />
      break
    case 'send-signal':
      glyph = <polygon points="4,6 28,6 36,14 28,22 4,22" {...stroke} strokeLinejoin="round" />
      break
    case 'accept-event':
      glyph = <polygon points="4,6 36,6 28,14 36,22 4,22 12,14" {...stroke} strokeLinejoin="round" />
      break
    case 'port':
      glyph = <rect x="14" y="7" width="12" height="12" {...stroke} />
      break
    case 'rounded-rect':
    default:
      glyph = <rect x="5" y="6" width="30" height="16" rx="3" {...stroke} />
  }
  return (
    <svg width="40" height="28" viewBox="0 0 40 28" aria-hidden className="text-fg">
      {glyph}
    </svg>
  )
}

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="10"
      height="10"
      viewBox="0 0 10 10"
      aria-hidden
      className={open ? 'rotate-90 transition-transform' : 'transition-transform'}
    >
      <path d="M3 2 L7 5 L3 8" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  )
}

const PALETTE_SCOPE_KEY = 'gp.palette.scope'
const PALETTE_ORGANIZATION_KEY = 'gp.palette.organization'
const PALETTE_COLLAPSED_KEY = 'gp.palette.collapsed'

function storedScope(): PaletteScope {
  return sessionStorage.getItem(PALETTE_SCOPE_KEY) === 'all' ? 'all' : 'current'
}

function storedOrganization(): PaletteOrganization {
  return sessionStorage.getItem(PALETTE_ORGANIZATION_KEY) === 'notation' ? 'notation' : 'diagram'
}

function storedCollapsed(): Record<string, boolean> {
  try {
    const value = JSON.parse(sessionStorage.getItem(PALETTE_COLLAPSED_KEY) ?? '{}')
    return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, boolean> : {}
  } catch {
    return {}
  }
}

export interface NodePaletteProps {
  // Optional only for backwards compatibility with hosts that have not supplied a
  // loaded diagram yet; a missing type is the universal custom vocabulary.
  diagramType?: string
  onAdd?: (item: PaletteItem) => void
  relationshipSemantic?: string
  onRelationshipSemanticChange?: (semanticType: string) => void
  routeMode?: RouteMode
  onRouteModeChange?: (mode: RouteMode) => void
}

export function NodePalette({
  diagramType = 'custom',
  onAdd,
  relationshipSemantic = 'association',
  onRelationshipSemanticChange,
  routeMode,
  onRouteModeChange,
}: NodePaletteProps = {}) {
  const groupId = useId()
  const [query, setQuery] = useState('')
  const [scope, setScope] = useState<PaletteScope>(storedScope)
  const [organization, setOrganization] = useState<PaletteOrganization>(storedOrganization)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>(storedCollapsed)

  useEffect(() => sessionStorage.setItem(PALETTE_SCOPE_KEY, scope), [scope])
  useEffect(() => sessionStorage.setItem(PALETTE_ORGANIZATION_KEY, organization), [organization])
  useEffect(() => sessionStorage.setItem(PALETTE_COLLAPSED_KEY, JSON.stringify(collapsed)), [collapsed])

  const q = query.trim().toLowerCase()
  const allRelationshipTools = relationshipTools('custom')
  const groups = organizedPaletteGroups({ diagramType, scope, organization, query })
  const relationshipSemantics = new Set(groups.flatMap((group) => group.relationships.map((item) => item.semanticType)))
  const relationships = (scope === 'current' ? relationshipTools(diagramType) : allRelationshipTools)
    .filter((tool) => relationshipSemantics.has(tool.semanticType))
  const shapeGroups = groups.filter((group) => group.shapes.length > 0)

  return (
    <div className="p-3">
      <input
        type="search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search shapes and relationships…"
        aria-label="Search shapes and relationships"
        className="mb-2 w-full rounded-md border border-line bg-surface px-2 py-1.5 text-xs text-fg placeholder:text-fg-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
      />
      <div className="mb-3 grid grid-cols-2 gap-2">
        <div className="space-y-1 text-[11px] font-medium text-fg-muted">
          <span>Scope</span>
          <Select aria-label="Palette scope" value={scope} onChange={(event) => setScope(event.target.value as PaletteScope)}>
            <option value="current">Current diagram</option>
            <option value="all">All authorable</option>
          </Select>
        </div>
        <div className="space-y-1 text-[11px] font-medium text-fg-muted">
          <span>Organize by</span>
          <Select aria-label="Organize palette by" value={organization} onChange={(event) => setOrganization(event.target.value as PaletteOrganization)}>
            <option value="diagram">Diagram</option>
            <option value="notation">Notation</option>
          </Select>
        </div>
      </div>
      <p className="mb-3 text-xs text-fg-subtle">Drag a shape or select a relationship.</p>

      {relationships.length || routeMode ? (
        <div className="mb-3 space-y-2">
          {relationships.length ? (
            <div>
              <p className="mb-1 px-1 text-[10px] font-semibold tracking-wide text-fg-subtle uppercase">Relationships</p>
              <div className="grid grid-cols-2 gap-2">
                {relationships.map((relationship) => (
                  <button
                    key={relationship.semanticType}
                    type="button"
                    disabled={!onRelationshipSemanticChange}
                    onClick={() => onRelationshipSemanticChange?.(relationship.semanticType)}
                    aria-pressed={relationshipSemantic === relationship.semanticType}
                    className={`flex min-h-12 flex-col items-center justify-center rounded-md border p-1.5 text-fg hover:border-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 ${relationshipSemantic === relationship.semanticType ? 'border-accent bg-accent/10' : 'border-line bg-surface-2'}`}
                    title={`Use ${relationship.label} relationship`}
                  >
                    <span className="font-mono text-sm" aria-hidden>{relationship.glyph}</span>
                    <span className="text-[10px] leading-tight">{relationship.label}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : null}
          {routeMode ? (
            <div>
              <p className="mb-1 px-1 text-[10px] font-semibold tracking-wide text-fg-subtle uppercase">Path</p>
              <div className="grid grid-cols-2 gap-2" role="group" aria-label="Route mode">
                {(['straight', 'orthogonal'] as const).map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    disabled={!onRouteModeChange}
                    onClick={() => onRouteModeChange?.(mode)}
                    aria-pressed={routeMode === mode}
                    className={`rounded-md border px-2 py-1.5 text-[11px] font-medium text-fg hover:border-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 ${routeMode === mode ? 'border-accent bg-accent/10' : 'border-line bg-surface-2'}`}
                  >
                    {mode === 'straight' ? 'Straight' : 'Orthogonal'}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}

      {shapeGroups.length === 0 ? (
        relationships.length === 0 ? <p className="text-xs text-fg-subtle">No shapes or relationships match your search.</p> : null
      ) : (
        shapeGroups.map((group) => {
          // While searching, force categories open so all matches are visible.
          const open = q ? true : !collapsed[group.id]
          return (
            <div key={group.id} className="mb-2">
              <button
                type="button"
                onClick={() => setCollapsed((value) => ({ ...value, [group.id]: !value[group.id] }))}
                aria-expanded={open}
                aria-controls={`${groupId}-${group.id}`}
                className="flex w-full items-center gap-1.5 rounded px-1 py-1 text-[11px] font-semibold tracking-wide text-fg-subtle uppercase hover:text-fg"
              >
                <Chevron open={open} />
                <span>{group.label}</span>
              </button>
              {open ? (
                <div id={`${groupId}-${group.id}`} className="mt-1">
                  <p className="mb-1 px-1 text-[10px] font-semibold tracking-wide text-fg-subtle uppercase">Shapes</p>
                  <div className="grid grid-cols-2 gap-2">
                    {group.shapes.map((item) => (
                      <div
                        key={item.semanticType}
                        draggable
                        onDragStart={(event) => onDragStart(event, item)}
                        onDoubleClick={() => onAdd?.(item)}
                        onKeyDown={(event) => {
                          if (!onAdd || (event.key !== 'Enter' && event.key !== ' ')) return
                          event.preventDefault()
                          onAdd(item)
                        }}
                        role="button"
                        tabIndex={0}
                        aria-label={`Add ${item.label}`}
                        className="flex cursor-grab flex-col items-center gap-1 rounded-md border border-line bg-surface-2 p-2 text-fg select-none hover:border-accent/40 hover:bg-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
                        title={`${item.type} · ${item.semanticType}`}
                      >
                        <ShapePreview primitive={nodePrimitive(item.semanticType)} />
                        <span className="text-[11px]">{item.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )
        })
      )}
    </div>
  )
}
