import { useEffect, useId, useMemo, useState } from 'react'
import type { CSSProperties, KeyboardEvent, ReactNode } from 'react'
import type { Edge, Node } from '@xyflow/react'
import type {
  AppliedStereotype,
  ArrowDirection,
  GraphPilotEdgeData,
  GraphPilotNodeData,
  GraphPilotNodeStyle,
  ItemFlow,
  ModelConstraint,
  ModelFeatures,
  ModelOperation,
  ModelParameter,
  ModelProperty,
  Multiplicity,
  PortData,
  PropertyKind,
  RelationshipEnd,
} from '@/types/diagram'
import { allowedNodeSpecs, nodePrimitive, semanticLabel } from '@/editor/lib/elementCatalog'
import { applyRelationshipSemantic, relationshipTools } from '@/editor/lib/relationshipPresets'
import { normalizeRouteGeometry, setRouteMode } from '@/editor/lib/edgeRouting'
import { featureBlockMinSize } from '@/editor/lib/bddCompartments'
import type { RouteGeometry, RouteMode, RouteSide } from '@/editor/lib/edgeRouting'
import { Button, ColorInput, Field, Input, NumberInput, Select } from '@/ui'

export interface NodePatch {
  label?: string
  semanticType?: string
  data?: Partial<GraphPilotNodeData>
  clearData?: (keyof GraphPilotNodeData)[]
  width?: number
  height?: number
  background?: string
  borderColor?: string
  color?: string
  borderWidth?: number
  borderStyle?: string
}

export interface EdgePatch {
  label?: string
  semanticType?: string
  data?: Partial<GraphPilotEdgeData>
  clearData?: (keyof GraphPilotEdgeData)[]
  stroke?: string
  strokeWidth?: number
  strokeDasharray?: string
  sourceHandle?: string | null
  targetHandle?: string | null
  route?: RouteGeometry | null
  swapEnds?: boolean
}

export type PanelSelection =
  | { kind: 'node'; node: Node }
  | { kind: 'edge'; edge: Edge }
  | null

interface PropertyPanelProps {
  diagramType: string
  selection: PanelSelection
  onNodeChange: (id: string, patch: NodePatch) => void
  onEdgeChange: (id: string, patch: EdgePatch) => void
  selectedNodeCount?: number
  onBulkNodeStyle?: (patch: NodePatch) => void
  issues?: Array<string | { message: string; path: string | null }>
}

const PANEL = 'p-4 text-sm'
const CARD = 'rounded-md border border-line bg-surface-2/40 p-2'
const PANEL_TABS = [
  { id: 'content', label: 'Content' },
  { id: 'appearance', label: 'Appearance' },
  { id: 'advanced', label: 'Advanced' },
] as const

type PanelTab = (typeof PANEL_TABS)[number]['id']
type PanelIssue = string | { message: string; path: string | null }
type TabIndicator = { populated?: boolean; error?: boolean }

function issueMessage(issue: PanelIssue): string {
  return typeof issue === 'string' ? issue : issue.message
}

function issueTab(kind: 'node' | 'edge' | null, issue: PanelIssue): PanelTab {
  if (typeof issue === 'string' || !issue.path) return 'content'
  const path = issue.path
  if (/\.(style|width|height|route|sourceHandle|targetHandle)(?:\.|$)/.test(path) || /\.data\.arrow(?:\.|$)/.test(path)) return 'appearance'
  if (kind === 'edge' && /\.data\.semanticType(?:\.|$)/.test(path)) return 'content'
  if (/\]\.(id|type|source|target|parentId)(?:\.|$)/.test(path) || /\.data\.(semanticType|description|metadata|appliedStereotypes)(?:\.|$)/.test(path)) return 'advanced'
  if (kind === 'edge' && /\.data\.(sourceEnd|targetEnd)(?:\.|$)/.test(path) && !path.includes('.multiplicity')) return 'advanced'
  return 'content'
}

function indicatorMap(
  kind: 'node' | 'edge',
  issues: PanelIssue[] | undefined,
  populated: Record<PanelTab, boolean>,
): Record<PanelTab, TabIndicator> {
  const errors = new Set((issues ?? []).map((issue) => issueTab(kind, issue)))
  return Object.fromEntries(PANEL_TABS.map((tab) => [tab.id, {
    populated: populated[tab.id],
    error: errors.has(tab.id),
  }])) as Record<PanelTab, TabIndicator>
}

const PROPERTY_KINDS: readonly PropertyKind[] = ['part', 'reference', 'value', 'constraint', 'flow']
const PRIMARY_STEREOTYPES = ['valueType', 'constraint', 'interfaceBlock', 'enumeration'] as const
const PARAMETER_DIRECTIONS = ['in', 'out', 'inout', 'return'] as const
const PROPERTY_DIRECTIONS = ['in', 'out', 'inout'] as const

function editorKey(group: string, index: number): string {
  return `${group}-${index}`
}

const STYLE_PRESETS: { name: string; patch: NodePatch }[] = [
  {
    name: 'Reset',
    patch: {
      background: '#ffffff',
      color: '#111111',
      borderColor: '#333333',
      borderWidth: 1,
      borderStyle: 'solid',
    },
  },
  { name: 'Blue', patch: { background: '#dbeafe', color: '#1e3a8a', borderColor: '#2563eb' } },
  { name: 'Amber', patch: { background: '#fef3c7', color: '#92400e', borderColor: '#d97706' } },
  { name: 'Green', patch: { background: '#dcfce7', color: '#166534', borderColor: '#16a34a' } },
]

const DASH_VALUES = { solid: '', dashed: '6 4', dotted: '2 4' } as const
type DashKey = keyof typeof DASH_VALUES

function num(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function dashKey(value: string | undefined): DashKey {
  if (!value) return 'solid'
  return value === DASH_VALUES.dotted ? 'dotted' : 'dashed'
}

function textOrUndefined(value: string): string | undefined {
  return value.trim() ? value : undefined
}

function lines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function isEmptyObject(value: object): boolean {
  return Object.keys(value).length === 0
}

function setOptional<T extends object, K extends keyof T>(source: T, key: K, value: T[K] | undefined): T {
  const next = { ...source }
  if (value === undefined) delete (next as Partial<T>)[key]
  else next[key] = value
  return next
}

function replaceAt<T>(items: readonly T[], index: number, value: T): T[] {
  return items.map((item, itemIndex) => (itemIndex === index ? value : item))
}

function displayLooseValue(value: unknown): string {
  if (value === undefined) return ''
  if (typeof value === 'string') return value
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

function parseLooseValue(value: string): unknown {
  const trimmed = value.trim()
  if (!trimmed) return undefined
  try {
    return JSON.parse(trimmed)
  } catch {
    return value
  }
}

function IssueFlag({ issues }: { issues?: PanelIssue[] }) {
  if (!issues || issues.length === 0) return null
  return (
    <div className="mb-3 rounded-md border border-danger bg-danger-bg px-2.5 py-2 text-xs text-danger">
      <p className="mb-1 font-semibold">{issues.length === 1 ? 'Validation issue' : 'Validation issues'}</p>
      <ul className="list-disc space-y-0.5 pl-4">
        {issues.map((issue) => (
          <li key={`${typeof issue === 'string' ? '' : issue.path}:${issueMessage(issue)}`}>{issueMessage(issue)}</li>
        ))}
      </ul>
    </div>
  )
}

function ElementHeader({
  kind,
  label,
  semanticType,
}: {
  kind: 'Node' | 'Edge'
  label: string
  semanticType: string
}) {
  const humanType = semanticType ? semanticLabel(semanticType) : 'Type not set'
  return (
    <header className="mb-3 min-w-0">
      <p className="text-[11px] font-semibold tracking-wide text-fg-subtle uppercase">{kind}</p>
      <h3 className="truncate text-base font-semibold text-fg">{label.trim() || humanType}</h3>
      {label.trim() ? <p className="truncate text-xs text-fg-subtle">{humanType}</p> : null}
    </header>
  )
}

function HumanType({ semanticType }: { semanticType: string }) {
  return (
    <dl className="mb-3 rounded-md border border-line bg-surface-2/40 px-2.5 py-2">
      <dt className="text-xs font-semibold text-fg-muted">Type</dt>
      <dd className="mt-0.5 text-sm text-fg">{semanticType ? semanticLabel(semanticType) : 'Not set'}</dd>
    </dl>
  )
}

function IdentifierRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[auto_1fr_auto] items-center gap-2 text-xs">
      <span className="font-semibold text-fg-muted">{label}</span>
      <span className="min-w-0 break-all text-fg-subtle">{value}</span>
      <Button
        variant="ghost"
        size="sm"
        aria-label={`Copy ${label}`}
        onClick={() => {
          const write = navigator.clipboard?.writeText(value)
          if (write) void write.catch(() => undefined)
        }}
      >
        Copy
      </Button>
    </div>
  )
}

function PanelTabList({
  activeTab,
  idPrefix,
  onChange,
  indicators,
}: {
  activeTab: PanelTab
  idPrefix: string
  onChange: (tab: PanelTab) => void
  indicators?: Partial<Record<PanelTab, TabIndicator>>
}) {
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    let nextIndex: number | undefined
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (index + 1) % PANEL_TABS.length
    else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (index - 1 + PANEL_TABS.length) % PANEL_TABS.length
    else if (event.key === 'Home') nextIndex = 0
    else if (event.key === 'End') nextIndex = PANEL_TABS.length - 1
    if (nextIndex === undefined) return

    event.preventDefault()
    const nextTab = PANEL_TABS[nextIndex].id
    onChange(nextTab)
    event.currentTarget.parentElement
      ?.querySelector<HTMLButtonElement>(`[data-panel-tab="${nextTab}"]`)
      ?.focus()
  }

  return (
    <div
      role="tablist"
      aria-label="Element properties"
      className="grid grid-cols-3 border-b border-line"
    >
      {PANEL_TABS.map((tab, index) => {
        const selected = activeTab === tab.id
        const indicator = indicators?.[tab.id]
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            id={`${idPrefix}-${tab.id}-tab`}
            aria-controls={`${idPrefix}-${tab.id}-panel`}
            aria-selected={selected}
            tabIndex={selected ? 0 : -1}
            data-panel-tab={tab.id}
            title={indicator?.error ? `${tab.label} contains validation issues` : indicator?.populated ? `${tab.label} contains values` : undefined}
            onClick={() => onChange(tab.id)}
            onKeyDown={(event) => handleKeyDown(event, index)}
            className={`border-b-2 px-1 py-2 text-xs font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent/50 ${selected ? 'border-accent text-fg' : 'border-transparent text-fg-subtle hover:text-fg'}`}
          >
            <span>{tab.label}</span>
            {indicator?.populated || indicator?.error ? (
              <span
                aria-hidden
                className={`ml-1 inline-block h-1.5 w-1.5 rounded-full ${indicator.error ? 'bg-danger' : 'bg-accent'}`}
              />
            ) : null}
          </button>
        )
      })}
    </div>
  )
}

function PanelTabPane({
  tab,
  activeTab,
  idPrefix,
  children,
}: {
  tab: PanelTab
  activeTab: PanelTab
  idPrefix: string
  children: ReactNode
}) {
  return (
    <div
      role="tabpanel"
      id={`${idPrefix}-${tab}-panel`}
      aria-labelledby={`${idPrefix}-${tab}-tab`}
      hidden={activeTab !== tab}
      className="pt-1"
    >
      {children}
    </div>
  )
}

function Section({ title, children, defaultOpen = true }: { title: string; children: ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <section className="border-b border-line py-2 last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
        className="mb-2 flex w-full items-center justify-between text-xs font-semibold tracking-wide text-fg-subtle uppercase"
      >
        <span>{title}</span>
        <span aria-hidden>{open ? '-' : '+'}</span>
      </button>
      {open ? <div>{children}</div> : null}
    </section>
  )
}

function CompactField({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="flex min-w-0 flex-col gap-1 text-xs text-fg-muted">
      <span className="font-medium">{label}</span>
      {children}
    </label>
  )
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <Field label={label}>
      <Input value={value} onChange={(event) => onChange(event.target.value)} />
    </Field>
  )
}

function OptionalTextField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string | undefined
  onChange: (value: string | undefined) => void
}) {
  return (
    <Field label={label}>
      <Input value={value ?? ''} onChange={(event) => onChange(textOrUndefined(event.target.value))} />
    </Field>
  )
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string
  value: number | undefined
  onChange: (value: number) => void
}) {
  return (
    <Field label={label}>
      <NumberInput
        value={value ?? ''}
        onChange={(event) => {
          const next = Number(event.target.value)
          if (event.target.value !== '' && Number.isFinite(next)) onChange(next)
        }}
      />
    </Field>
  )
}

function OptionalNumberField({
  label,
  value,
  onChange,
  min,
  max,
  step,
}: {
  label: string
  value: number | undefined
  onChange: (value: number | undefined) => void
  min?: number
  max?: number
  step?: number
}) {
  return (
    <CompactField label={label}>
      <NumberInput
        value={value ?? ''}
        min={min}
        max={max}
        step={step}
        onChange={(event) => {
          if (event.target.value === '') {
            onChange(undefined)
            return
          }
          const next = Number(event.target.value)
          if (Number.isFinite(next)) onChange(next)
        }}
      />
    </CompactField>
  )
}

function BooleanField({
  label,
  value,
  onChange,
}: {
  label: string
  value: boolean | undefined
  onChange: (value: boolean | undefined) => void
}) {
  return (
    <CompactField label={label}>
      <Select
        value={value === undefined ? '' : String(value)}
        onChange={(event) => onChange(event.target.value === '' ? undefined : event.target.value === 'true')}
      >
        <option value="">Not set</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
      </Select>
    </CompactField>
  )
}

function ColorField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string | undefined
  onChange: (value: string) => void
}) {
  return (
    <Field label={label}>
      <ColorInput value={value ?? '#000000'} onChange={(event) => onChange(event.target.value)} />
    </Field>
  )
}

function LinesField({
  label,
  values,
  onChange,
  placeholder = 'one value per line',
}: {
  label: string
  values: readonly string[]
  onChange: (values: string[]) => void
  placeholder?: string
}) {
  const serialized = values.join('\n')
  const [text, setText] = useState(serialized)
  useEffect(() => setText(serialized), [serialized])

  return (
    <Field label={label}>
      <textarea
        className="min-h-16 w-full rounded-md border border-line bg-surface px-2 py-1.5 text-xs text-fg placeholder:text-fg-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
        value={text}
        placeholder={placeholder}
        onChange={(event) => {
          setText(event.target.value)
          onChange(lines(event.target.value))
        }}
      />
    </Field>
  )
}

function JsonObjectField({
  label,
  value,
  onChange,
}: {
  label: string
  value: Record<string, unknown> | undefined
  onChange: (value: Record<string, unknown> | undefined) => void
}) {
  const serialized = value && !isEmptyObject(value) ? JSON.stringify(value, null, 2) : ''
  const [text, setText] = useState(serialized)
  const [error, setError] = useState('')

  useEffect(() => {
    setText(serialized)
    setError('')
  }, [serialized])

  const commit = () => {
    if (!text.trim()) {
      setError('')
      onChange(undefined)
      return
    }
    try {
      const parsed: unknown = JSON.parse(text)
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        setError('Enter a JSON object.')
        return
      }
      setError('')
      onChange(parsed as Record<string, unknown>)
    } catch {
      setError('Enter valid JSON before leaving this field.')
    }
  }

  return (
    <Field label={label}>
      <textarea
        className="min-h-24 w-full rounded-md border border-line bg-surface px-2 py-1.5 font-mono text-xs text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
        value={text}
        placeholder="{}"
        onChange={(event) => setText(event.target.value)}
        onBlur={commit}
      />
      {error ? <span className="text-xs text-danger" role="alert">{error}</span> : null}
    </Field>
  )
}

function SemanticTypeField({
  kind,
  diagramType,
  value,
  onChange,
  label = 'Semantic type',
}: {
  kind: 'node' | 'edge'
  diagramType: string
  value: string
  onChange: (value: string) => void
  label?: string
}) {
  const specs = kind === 'node' ? allowedNodeSpecs(diagramType) : relationshipTools(diagramType)
  const supported = specs.some((spec) => spec.semanticType === value)
  return (
    <Field label={label}>
      <Select value={supported ? value : ''} onChange={(event) => onChange(event.target.value)}>
        {!supported ? (
          <option value="" disabled>
            {value ? `${semanticLabel(value)} (not allowed)` : 'Select a semantic type'}
          </option>
        ) : null}
        {specs.map((spec) => (
          <option key={spec.semanticType} value={spec.semanticType}>
            {semanticLabel(spec.semanticType)}
          </option>
        ))}
      </Select>
    </Field>
  )
}

function PrimaryStereotypeField({
  value,
  onChange,
}: {
  value: string | undefined
  onChange: (value: string | undefined) => void
}) {
  const listId = useId()
  return (
    <Field label="Primary stereotype">
      <Input
        list={listId}
        value={value ?? ''}
        placeholder="block"
        onChange={(event) => onChange(event.target.value || undefined)}
      />
      <datalist id={listId}>
        {PRIMARY_STEREOTYPES.map((stereotype) => <option key={stereotype} value={stereotype}>{stereotype}</option>)}
      </datalist>
    </Field>
  )
}

function Card({
  title,
  removeLabel,
  onRemove,
  children,
}: {
  title: string
  removeLabel: string
  onRemove: () => void
  children: ReactNode
}) {
  return (
    <div className={CARD}>
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-xs font-semibold text-fg">{title}</p>
        <Button variant="ghost" size="sm" onClick={onRemove} aria-label={removeLabel}>
          Remove
        </Button>
      </div>
      {children}
    </div>
  )
}

function CompactEditorRow({
  title,
  summary,
  expanded,
  onToggle,
  removeLabel,
  onRemove,
  children,
}: {
  title: string
  summary: string
  expanded: boolean
  onToggle: () => void
  removeLabel?: string
  onRemove?: () => void
  children: ReactNode
}) {
  return (
    <div className={CARD}>
      <div className="flex min-w-0 items-start gap-1">
        <button
          type="button"
          aria-expanded={expanded}
          aria-label={`Edit ${title}${summary ? `: ${summary}` : ''}`}
          onClick={onToggle}
          className="flex min-w-0 flex-1 items-center gap-2 rounded-sm text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
        >
          <span aria-hidden className="w-3 shrink-0 text-fg-subtle">{expanded ? '-' : '+'}</span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-semibold text-fg">{title}</span>
            {summary ? <span className="block truncate text-[11px] text-fg-subtle">{summary}</span> : null}
          </span>
        </button>
        {onRemove && removeLabel ? (
          <Button variant="ghost" size="sm" onClick={onRemove} aria-label={removeLabel}>
            Remove
          </Button>
        ) : null}
      </div>
      {expanded ? <div className="mt-2 border-t border-line pt-2">{children}</div> : null}
    </div>
  )
}

function useExpandedKey(
  expandedKey: string | null | undefined,
  onExpandedKeyChange: ((key: string | null) => void) | undefined,
): [string | null, (key: string | null) => void] {
  const [localExpandedKey, setLocalExpandedKey] = useState<string | null>(null)
  return onExpandedKeyChange
    ? [expandedKey ?? null, onExpandedKeyChange]
    : [localExpandedKey, setLocalExpandedKey]
}

interface CompactCollectionProps {
  expandedKey?: string | null
  onExpandedKeyChange?: (key: string | null) => void
  keyPrefix?: string
  showAdd?: boolean
}

function MultiplicityEditor({
  prefix,
  value,
  onChange,
}: {
  prefix: string
  value: Multiplicity | undefined
  onChange: (value: Multiplicity | undefined) => void
}) {
  const serializedUpper = value?.upper === undefined ? '' : String(value.upper)
  const [upperText, setUpperText] = useState(serializedUpper)
  useEffect(() => setUpperText(serializedUpper), [serializedUpper])

  const commitUpper = () => {
    const raw = upperText.trim()
    if (!raw) {
      onChange(undefined)
      return
    }
    if (raw === '*') return
    const upper = Number(raw)
    if (!Number.isInteger(upper) || upper < 0) {
      setUpperText(serializedUpper)
      return
    }
    const lower = value?.lower ?? 0
    if (upper < lower) {
      setUpperText(String(lower))
      onChange({ lower, upper: lower })
    }
  }

  return (
    <div className="grid grid-cols-2 gap-2">
      <CompactField label={`${prefix} multiplicity lower`}>
        <NumberInput
          min={0}
          step={1}
          value={value?.lower ?? ''}
          onChange={(event) => {
            if (event.target.value === '') {
              onChange(undefined)
              return
            }
            const lower = Number(event.target.value)
            if (Number.isInteger(lower) && lower >= 0) {
              const upper = value?.upper === '*' ? '*' : Math.max(lower, value?.upper ?? lower)
              onChange({ lower, upper })
            }
          }}
        />
      </CompactField>
      <CompactField label={`${prefix} multiplicity upper`}>
        <Input
          value={upperText}
          placeholder="1 or *"
          onBlur={commitUpper}
          onChange={(event) => {
            const next = event.target.value
            setUpperText(next)
            const raw = next.trim()
            const lower = value?.lower ?? 0
            if (raw === '*') onChange({ lower, upper: '*' })
            else {
              const upper = Number(raw)
              if (raw && Number.isInteger(upper) && upper >= lower) onChange({ lower, upper })
            }
          }}
        />
      </CompactField>
    </div>
  )
}

function ParametersEditor({
  parameters,
  onChange,
  itemLabel = 'Parameter',
  expandedKey,
  onExpandedKeyChange,
  keyPrefix = 'parameter',
  showAdd = true,
}: {
  parameters: readonly ModelParameter[]
  onChange: (parameters: ModelParameter[]) => void
  itemLabel?: string
} & CompactCollectionProps) {
  const [openKey, setOpenKey] = useExpandedKey(expandedKey, onExpandedKeyChange)
  const addParameter = () => {
    const nextIndex = parameters.length
    onChange([...parameters, { name: '', direction: 'in' }])
    setOpenKey(`${keyPrefix}-${nextIndex}`)
  }

  return (
    <div className="space-y-2">
      {parameters.map((parameter, index) => {
        const prefix = `${itemLabel} ${index + 1}`
        const rowKey = `${keyPrefix}-${index}`
        const update = (next: ModelParameter) => onChange(replaceAt(parameters, index, next))
        const summary = `${parameter.name || 'Unnamed'}${parameter.type ? `: ${parameter.type}` : ''} · ${parameter.direction}`
        return (
          <CompactEditorRow
            key={editorKey(keyPrefix, index)}
            title={prefix}
            summary={summary}
            expanded={openKey === rowKey}
            onToggle={() => setOpenKey(openKey === rowKey ? null : rowKey)}
            removeLabel={`Remove ${prefix}`}
            onRemove={() => {
              if (openKey === rowKey) setOpenKey(null)
              onChange(parameters.filter((_, itemIndex) => itemIndex !== index))
            }}
          >
            <div className="grid grid-cols-2 gap-2">
              <CompactField label={`${prefix} name`}>
                <Input value={parameter.name} onChange={(event) => update({ ...parameter, name: event.target.value })} />
              </CompactField>
              <CompactField label={`${prefix} type`}>
                <Input
                  value={parameter.type ?? ''}
                  onChange={(event) => update(setOptional(parameter, 'type', textOrUndefined(event.target.value)))}
                />
              </CompactField>
              <CompactField label={`${prefix} direction`}>
                <Select
                  value={parameter.direction}
                  onChange={(event) =>
                    update({ ...parameter, direction: event.target.value as ModelParameter['direction'] })
                  }
                >
                  {PARAMETER_DIRECTIONS.map((direction) => (
                    <option key={direction} value={direction}>{direction}</option>
                  ))}
                </Select>
              </CompactField>
              <CompactField label={`${prefix} default`}>
                <Input
                  value={displayLooseValue(parameter.default)}
                  onChange={(event) => update(setOptional(parameter, 'default', parseLooseValue(event.target.value)))}
                />
              </CompactField>
            </div>
            <div className="mt-2">
              <MultiplicityEditor
                prefix={prefix}
                value={parameter.multiplicity}
                onChange={(multiplicity) => update(setOptional(parameter, 'multiplicity', multiplicity))}
              />
            </div>
          </CompactEditorRow>
        )
      })}
      {showAdd ? (
        <Button variant="secondary" size="sm" onClick={addParameter}>
          Add parameter
        </Button>
      ) : null}
    </div>
  )
}

function PropertiesEditor({
  properties,
  onChange,
  itemLabel = 'Property',
  addLabel = 'Add property',
  expandedKey,
  onExpandedKeyChange,
  keyPrefix = 'property',
  showAdd = true,
}: {
  properties: readonly ModelProperty[]
  onChange: (properties: ModelProperty[]) => void
  itemLabel?: string
  addLabel?: string
} & CompactCollectionProps) {
  const [openKey, setOpenKey] = useExpandedKey(expandedKey, onExpandedKeyChange)
  const addProperty = () => {
    const nextIndex = properties.length
    onChange([...properties, { kind: 'value', name: '' }])
    setOpenKey(`${keyPrefix}-${nextIndex}`)
  }

  return (
    <div className="space-y-2">
      {properties.map((property, index) => {
        const prefix = `${itemLabel} ${index + 1}`
        const rowKey = `${keyPrefix}-${index}`
        const update = (next: ModelProperty) => onChange(replaceAt(properties, index, next))
        const summary = `${property.name || 'Unnamed'}${property.type ? `: ${property.type}` : ''} · ${property.kind}`
        return (
          <CompactEditorRow
            key={editorKey(keyPrefix, index)}
            title={prefix}
            summary={summary}
            expanded={openKey === rowKey}
            onToggle={() => setOpenKey(openKey === rowKey ? null : rowKey)}
            removeLabel={`Remove ${prefix}`}
            onRemove={() => {
              if (openKey === rowKey) setOpenKey(null)
              onChange(properties.filter((_, itemIndex) => itemIndex !== index))
            }}
          >
            <div className="grid grid-cols-2 gap-2">
              <CompactField label={`${prefix} kind`}>
                <Select
                  value={property.kind}
                  onChange={(event) => update({ ...property, kind: event.target.value as PropertyKind })}
                >
                  {PROPERTY_KINDS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}
                </Select>
              </CompactField>
              <CompactField label={`${prefix} name`}>
                <Input value={property.name} onChange={(event) => update({ ...property, name: event.target.value })} />
              </CompactField>
              <CompactField label={`${prefix} type`}>
                <Input
                  value={property.type ?? ''}
                  onChange={(event) => update(setOptional(property, 'type', textOrUndefined(event.target.value)))}
                />
              </CompactField>
              <CompactField label={`${prefix} direction`}>
                <Select
                  value={property.direction ?? ''}
                  onChange={(event) =>
                    update(
                      setOptional(
                        property,
                        'direction',
                        (event.target.value || undefined) as ModelProperty['direction'],
                      ),
                    )
                  }
                >
                  <option value="">Not set</option>
                  {PROPERTY_DIRECTIONS.map((direction) => (
                    <option key={direction} value={direction}>{direction}</option>
                  ))}
                </Select>
              </CompactField>
              <CompactField label={`${prefix} default`}>
                <Input
                  value={displayLooseValue(property.default)}
                  onChange={(event) => update(setOptional(property, 'default', parseLooseValue(event.target.value)))}
                />
              </CompactField>
            </div>
            <div className="mt-2">
              <MultiplicityEditor
                prefix={prefix}
                value={property.multiplicity}
                onChange={(multiplicity) => update(setOptional(property, 'multiplicity', multiplicity))}
              />
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2">
              <BooleanField
                label={`${prefix} read only`}
                value={property.isReadOnly}
                onChange={(value) => update(setOptional(property, 'isReadOnly', value))}
              />
              <BooleanField
                label={`${prefix} ordered`}
                value={property.isOrdered}
                onChange={(value) => update(setOptional(property, 'isOrdered', value))}
              />
              <BooleanField
                label={`${prefix} unique`}
                value={property.isUnique}
                onChange={(value) => update(setOptional(property, 'isUnique', value))}
              />
              <BooleanField
                label={`${prefix} derived`}
                value={property.isDerived}
                onChange={(value) => update(setOptional(property, 'isDerived', value))}
              />
            </div>
          </CompactEditorRow>
        )
      })}
      {showAdd ? (
        <Button variant="secondary" size="sm" onClick={addProperty}>
          {addLabel}
        </Button>
      ) : null}
    </div>
  )
}

function OperationsEditor({
  operations,
  onChange,
  expandedKey,
  onExpandedKeyChange,
  keyPrefix = 'operation',
  showAdd = true,
}: {
  operations: readonly ModelOperation[]
  onChange: (value: ModelOperation[]) => void
} & CompactCollectionProps) {
  const [openKey, setOpenKey] = useExpandedKey(expandedKey, onExpandedKeyChange)
  const addOperation = () => {
    const nextIndex = operations.length
    onChange([...operations, { name: '' }])
    setOpenKey(`${keyPrefix}-${nextIndex}`)
  }

  return (
    <div className="space-y-2">
      {operations.map((operation, index) => {
        const prefix = `Operation ${index + 1}`
        const rowKey = `${keyPrefix}-${index}`
        const expanded = openKey === rowKey || Boolean(openKey?.startsWith(`${rowKey}/`))
        const update = (next: ModelOperation) => onChange(replaceAt(operations, index, next))
        const summary = `${operation.name || 'Unnamed'}()${operation.returnType ? `: ${operation.returnType}` : ''}`
        return (
          <CompactEditorRow
            key={editorKey(keyPrefix, index)}
            title={prefix}
            summary={summary}
            expanded={expanded}
            onToggle={() => setOpenKey(expanded ? null : rowKey)}
            removeLabel={`Remove ${prefix}`}
            onRemove={() => {
              if (expanded) setOpenKey(null)
              onChange(operations.filter((_, itemIndex) => itemIndex !== index))
            }}
          >
            <div className="grid grid-cols-2 gap-2">
              <CompactField label={`${prefix} name`}>
                <Input value={operation.name} onChange={(event) => update({ ...operation, name: event.target.value })} />
              </CompactField>
              <CompactField label={`${prefix} return type`}>
                <Input
                  value={operation.returnType ?? ''}
                  onChange={(event) => update(setOptional(operation, 'returnType', textOrUndefined(event.target.value)))}
                />
              </CompactField>
              <BooleanField
                label={`${prefix} abstract`}
                value={operation.isAbstract}
                onChange={(value) => update(setOptional(operation, 'isAbstract', value))}
              />
              <BooleanField
                label={`${prefix} static`}
                value={operation.isStatic}
                onChange={(value) => update(setOptional(operation, 'isStatic', value))}
              />
              <BooleanField
                label={`${prefix} query`}
                value={operation.isQuery}
                onChange={(value) => update(setOptional(operation, 'isQuery', value))}
              />
            </div>
            <div className="mt-3 border-t border-line pt-2">
              <p className="mb-2 text-xs font-semibold text-fg-muted">Parameters</p>
              <ParametersEditor
                parameters={operation.parameters ?? []}
                itemLabel={`${prefix} parameter`}
                keyPrefix={`${rowKey}/parameter`}
                expandedKey={openKey}
                onExpandedKeyChange={setOpenKey}
                onChange={(parameters) =>
                  update(setOptional(operation, 'parameters', parameters.length ? parameters : undefined))
                }
              />
            </div>
          </CompactEditorRow>
        )
      })}
      {showAdd ? (
        <Button variant="secondary" size="sm" onClick={addOperation}>
          Add operation
        </Button>
      ) : null}
    </div>
  )
}

function ConstraintsEditor({
  constraints,
  onChange,
  expandedKey,
  onExpandedKeyChange,
  keyPrefix = 'constraint',
  showAdd = true,
}: {
  constraints: readonly ModelConstraint[]
  onChange: (value: ModelConstraint[]) => void
} & CompactCollectionProps) {
  const [openKey, setOpenKey] = useExpandedKey(expandedKey, onExpandedKeyChange)
  const addConstraint = () => {
    const nextIndex = constraints.length
    onChange([...constraints, { expression: '' }])
    setOpenKey(`${keyPrefix}-${nextIndex}`)
  }

  return (
    <div className="space-y-2">
      {constraints.map((constraint, index) => {
        const prefix = `Constraint ${index + 1}`
        const rowKey = `${keyPrefix}-${index}`
        const update = (next: ModelConstraint) => onChange(replaceAt(constraints, index, next))
        const summary = constraint.name || constraint.expression || 'Unnamed constraint'
        return (
          <CompactEditorRow
            key={editorKey(keyPrefix, index)}
            title={prefix}
            summary={summary}
            expanded={openKey === rowKey}
            onToggle={() => setOpenKey(openKey === rowKey ? null : rowKey)}
            removeLabel={`Remove ${prefix}`}
            onRemove={() => {
              if (openKey === rowKey) setOpenKey(null)
              onChange(constraints.filter((_, itemIndex) => itemIndex !== index))
            }}
          >
            <div className="space-y-2">
              <CompactField label={`${prefix} name`}>
                <Input
                  value={constraint.name ?? ''}
                  onChange={(event) => update(setOptional(constraint, 'name', textOrUndefined(event.target.value)))}
                />
              </CompactField>
              <CompactField label={`${prefix} expression`}>
                <Input
                  value={constraint.expression}
                  onChange={(event) => update({ ...constraint, expression: event.target.value })}
                />
              </CompactField>
            </div>
          </CompactEditorRow>
        )
      })}
      {showAdd ? (
        <Button variant="secondary" size="sm" onClick={addConstraint}>
          Add constraint
        </Button>
      ) : null}
    </div>
  )
}

function FeaturesEditor({
  features,
  onChange,
}: {
  features: ModelFeatures
  onChange: (features: ModelFeatures | undefined) => void
}) {
  const [expandedKey, setExpandedKey] = useState<string | null>(null)

  function update<K extends keyof ModelFeatures>(key: K, value: ModelFeatures[K] | undefined) {
    const next = setOptional(features, key, value)
    onChange(isEmptyObject(next) ? undefined : next)
  }

  const properties = features.properties ?? []
  const operations = features.operations ?? []
  const receptions = features.receptions ?? []
  const constraints = features.constraints ?? []
  const literals = features.literals ?? []

  return (
    <div className="space-y-4">
      {properties.length ? (
        <div>
          <p className="mb-2 text-xs font-semibold text-fg-muted">Properties</p>
          <PropertiesEditor
            properties={properties}
            expandedKey={expandedKey}
            onExpandedKeyChange={setExpandedKey}
            showAdd={false}
            onChange={(next) => update('properties', next.length ? next : undefined)}
          />
        </div>
      ) : null}
      {operations.length ? (
        <div>
          <p className="mb-2 text-xs font-semibold text-fg-muted">Operations</p>
          <OperationsEditor
            operations={operations}
            expandedKey={expandedKey}
            onExpandedKeyChange={setExpandedKey}
            showAdd={false}
            onChange={(next) => update('operations', next.length ? next : undefined)}
          />
        </div>
      ) : null}
      {receptions.length ? (
        <div>
          <p className="mb-2 text-xs font-semibold text-fg-muted">Receptions</p>
          <CompactEditorRow
            title="Receptions"
            summary={`${receptions.length} · ${receptions.filter(Boolean).join(', ') || 'Unnamed'}`}
            expanded={expandedKey === 'receptions'}
            onToggle={() => setExpandedKey(expandedKey === 'receptions' ? null : 'receptions')}
            removeLabel="Remove receptions"
            onRemove={() => {
              setExpandedKey(null)
              update('receptions', undefined)
            }}
          >
            <LinesField
              label="Receptions"
              values={receptions}
              onChange={(next) => update('receptions', next.length ? next : undefined)}
            />
          </CompactEditorRow>
        </div>
      ) : null}
      {constraints.length ? (
        <div>
          <p className="mb-2 text-xs font-semibold text-fg-muted">Constraints</p>
          <ConstraintsEditor
            constraints={constraints}
            expandedKey={expandedKey}
            onExpandedKeyChange={setExpandedKey}
            showAdd={false}
            onChange={(next) => update('constraints', next.length ? next : undefined)}
          />
        </div>
      ) : null}
      {literals.length ? (
        <div>
          <p className="mb-2 text-xs font-semibold text-fg-muted">Literals</p>
          <CompactEditorRow
            title="Literals"
            summary={`${literals.length} · ${literals.filter(Boolean).join(', ') || 'Unnamed'}`}
            expanded={expandedKey === 'literals'}
            onToggle={() => setExpandedKey(expandedKey === 'literals' ? null : 'literals')}
            removeLabel="Remove literals"
            onRemove={() => {
              setExpandedKey(null)
              update('literals', undefined)
            }}
          >
            <LinesField
              label="Literals"
              values={literals}
              onChange={(next) => update('literals', next.length ? next : undefined)}
            />
          </CompactEditorRow>
        </div>
      ) : null}
      <div className="border-t border-line pt-3">
        <Field label="Add content">
          <Select
            aria-label="Add content"
            value=""
            onChange={(event) => {
              const kind = event.target.value
              if (kind === 'property') {
                update('properties', [...properties, { kind: 'value', name: '' }])
                setExpandedKey(`property-${properties.length}`)
              } else if (kind === 'operation') {
                update('operations', [...operations, { name: '' }])
                setExpandedKey(`operation-${operations.length}`)
              } else if (kind === 'reception') {
                update('receptions', [...receptions, ''])
                setExpandedKey('receptions')
              } else if (kind === 'constraint') {
                update('constraints', [...constraints, { expression: '' }])
                setExpandedKey(`constraint-${constraints.length}`)
              } else if (kind === 'literal') {
                update('literals', [...literals, ''])
                setExpandedKey('literals')
              }
            }}
          >
            <option value="">Choose content…</option>
            <option value="property">Property</option>
            <option value="operation">Operation</option>
            <option value="reception">Reception</option>
            <option value="constraint">Constraint</option>
            <option value="literal">Literal</option>
          </Select>
        </Field>
      </div>
    </div>
  )
}

function StereotypesEditor({
  stereotypes,
  onChange,
}: {
  stereotypes: readonly AppliedStereotype[]
  onChange: (stereotypes: AppliedStereotype[] | undefined) => void
}) {
  const update = (index: number, value: AppliedStereotype) => onChange(replaceAt(stereotypes, index, value))
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-fg-muted">Applied stereotypes</p>
      {stereotypes.map((stereotype, index) => {
        const title = `Applied stereotype ${index + 1}`
        return (
          <Card
            key={editorKey('stereotype', index)}
            title={title}
            removeLabel={`Remove ${title}`}
            onRemove={() => {
              const next = stereotypes.filter((_, itemIndex) => itemIndex !== index)
              onChange(next.length ? next : undefined)
            }}
          >
            <OptionalTextField
              label="Name"
              value={stereotype.name}
              onChange={(name) => update(index, { ...stereotype, name: name ?? '' })}
            />
            <JsonObjectField
              label="Properties"
              value={stereotype.properties}
              onChange={(properties) => update(index, setOptional(stereotype, 'properties', properties))}
            />
          </Card>
        )
      })}
      <Button
        variant="secondary"
        size="sm"
        onClick={() => onChange([...stereotypes, { name: '' }])}
      >
        Add stereotype
      </Button>
    </div>
  )
}

function PortEditor({ port, onChange }: { port: PortData; onChange: (port: PortData | undefined) => void }) {
  function update<K extends keyof PortData>(key: K, value: PortData[K] | undefined) {
    const next = setOptional(port, key, value)
    onChange(isEmptyObject(next) ? undefined : next)
  }

  return (
    <div className="space-y-3">
      <OptionalTextField label="Port type" value={port.type} onChange={(value) => update('type', value)} />
      <Field label="Port side">
        <Select
          value={port.side ?? ''}
          onChange={(event) => update('side', (event.target.value || undefined) as PortData['side'])}
        >
          <option value="">Not set</option>
          <option value="top">Top</option>
          <option value="right">Right</option>
          <option value="bottom">Bottom</option>
          <option value="left">Left</option>
        </Select>
      </Field>
      <OptionalNumberField
        label="Port offset"
        value={port.offset}
        min={0}
        max={1}
        step={0.05}
        onChange={(value) => update('offset', value)}
      />
      <div className="grid grid-cols-2 gap-2">
        <BooleanField
          label="Port conjugated"
          value={port.isConjugated}
          onChange={(value) => update('isConjugated', value)}
        />
        <BooleanField
          label="Port behavior"
          value={port.isBehavior}
          onChange={(value) => update('isBehavior', value)}
        />
      </div>
      <LinesField
        label="Provided features"
        values={port.providedFeatures ?? []}
        onChange={(values) => update('providedFeatures', values.length ? values : undefined)}
      />
      <LinesField
        label="Required features"
        values={port.requiredFeatures ?? []}
        onChange={(values) => update('requiredFeatures', values.length ? values : undefined)}
      />
    </div>
  )
}

function RelationshipEndDetailsEditor({
  prefix,
  value,
  onChange,
}: {
  prefix: string
  value: RelationshipEnd
  onChange: (value: RelationshipEnd | undefined) => void
}) {
  function update<K extends keyof RelationshipEnd>(key: K, nextValue: RelationshipEnd[K] | undefined) {
    const next = setOptional(value, key, nextValue)
    onChange(isEmptyObject(next) ? undefined : next)
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <CompactField label={`${prefix} role`}>
          <Input value={value.role ?? ''} onChange={(event) => update('role', textOrUndefined(event.target.value))} />
        </CompactField>
        <CompactField label={`${prefix} type`}>
          <Input value={value.type ?? ''} onChange={(event) => update('type', textOrUndefined(event.target.value))} />
        </CompactField>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <BooleanField label={`${prefix} navigable`} value={value.navigable} onChange={(next) => update('navigable', next)} />
        <CompactField label={`${prefix} aggregation`}>
          <Select
            value={value.aggregation ?? ''}
            onChange={(event) =>
              update('aggregation', (event.target.value || undefined) as RelationshipEnd['aggregation'])
            }
          >
            <option value="">Not set</option>
            <option value="none">None</option>
            <option value="shared">Shared</option>
            <option value="composite">Composite</option>
          </Select>
        </CompactField>
        <BooleanField label={`${prefix} ordered`} value={value.isOrdered} onChange={(next) => update('isOrdered', next)} />
        <BooleanField label={`${prefix} unique`} value={value.isUnique} onChange={(next) => update('isUnique', next)} />
      </div>
      <LinesField
        label={`${prefix} property path`}
        values={value.propertyPath ?? []}
        onChange={(path) => update('propertyPath', path.length ? path : undefined)}
      />
      <div>
        <p className="mb-2 text-xs font-semibold text-fg-muted">{prefix} qualifiers</p>
        <PropertiesEditor
          properties={value.qualifiers ?? []}
          itemLabel={`${prefix} qualifier`}
          addLabel="Add qualifier"
          onChange={(qualifiers) => update('qualifiers', qualifiers.length ? qualifiers : undefined)}
        />
      </div>
    </div>
  )
}

function ItemFlowsEditor({ itemFlows, onChange }: { itemFlows: readonly ItemFlow[]; onChange: (value: ItemFlow[]) => void }) {
  return (
    <div className="space-y-2">
      {itemFlows.map((itemFlow, index) => {
        const prefix = `Item flow ${index + 1}`
        const update = (next: ItemFlow) => onChange(replaceAt(itemFlows, index, next))
        return (
          <Card
            key={editorKey('item-flow', index)}
            title={prefix}
            removeLabel={`Remove ${prefix}`}
            onRemove={() => onChange(itemFlows.filter((_, itemIndex) => itemIndex !== index))}
          >
            <div className="grid grid-cols-2 gap-2">
              <CompactField label={`${prefix} direction`}>
                <Select
                  value={itemFlow.direction}
                  onChange={(event) =>
                    update({ ...itemFlow, direction: event.target.value as ItemFlow['direction'] })
                  }
                >
                  <option value="sourceToTarget">Source to target</option>
                  <option value="targetToSource">Target to source</option>
                </Select>
              </CompactField>
              <CompactField label={`${prefix} item`}>
                <Input value={itemFlow.item} onChange={(event) => update({ ...itemFlow, item: event.target.value })} />
              </CompactField>
              <CompactField label={`${prefix} item property`}>
                <Input
                  value={itemFlow.itemProperty ?? ''}
                  onChange={(event) =>
                    update(setOptional(itemFlow, 'itemProperty', textOrUndefined(event.target.value)))
                  }
                />
              </CompactField>
            </div>
          </Card>
        )
      })}
      <Button
        variant="secondary"
        size="sm"
        onClick={() => onChange([...itemFlows, { direction: 'sourceToTarget', item: '' }])}
      >
        Add item flow
      </Button>
    </div>
  )
}

function NodeStyleEditor({
  gp,
  set,
}: {
  gp: GraphPilotNodeStyle
  set: (patch: NodePatch) => void
}) {
  return (
    <>
      <div className="mb-3 flex flex-wrap gap-1">
        {STYLE_PRESETS.map((preset) => (
          <Button key={preset.name} variant="secondary" size="sm" onClick={() => set(preset.patch)}>
            {preset.name}
          </Button>
        ))}
      </div>
      <ColorField label="Background" value={gp.background} onChange={(value) => set({ background: value })} />
      <ColorField label="Text color" value={gp.color} onChange={(value) => set({ color: value })} />
      <ColorField label="Border color" value={gp.borderColor} onChange={(value) => set({ borderColor: value })} />
      <NumberField label="Border width" value={num(gp.borderWidth)} onChange={(value) => set({ borderWidth: value })} />
      <Field label="Border style">
        <Select value={gp.borderStyle ?? 'solid'} onChange={(event) => set({ borderStyle: event.target.value })}>
          <option value="solid">solid</option>
          <option value="dashed">dashed</option>
          <option value="dotted">dotted</option>
          <option value="none">none</option>
        </Select>
      </Field>
    </>
  )
}

export function PropertyPanel({
  diagramType,
  selection,
  onNodeChange,
  onEdgeChange,
  selectedNodeCount,
  onBulkNodeStyle,
  issues,
}: PropertyPanelProps) {
  const isBulkSelection = Boolean(selectedNodeCount && selectedNodeCount > 1 && onBulkNodeStyle)
  const [activeTab, setActiveTab] = useState<PanelTab>(() => (isBulkSelection ? 'appearance' : 'content'))
  const tabId = useId()
  const selectionKind = selection?.kind ?? null
  const selectionKey = selection?.kind === 'node' ? `node:${selection.node.id}` : selection?.kind === 'edge' ? `edge:${selection.edge.id}` : ''
  const validationTab = useMemo(
    () => issues?.length ? issueTab(selectionKind, issues[0]) : undefined,
    [issues, selectionKind],
  )

  useEffect(() => {
    if (isBulkSelection) setActiveTab('appearance')
    else if (validationTab) setActiveTab(validationTab)
  }, [isBulkSelection, selectionKey, validationTab])

  if (isBulkSelection && onBulkNodeStyle) {
    const set = (patch: NodePatch) => onBulkNodeStyle(patch)
    return (
      <div className={PANEL}>
        <header className="mb-3">
          <p className="text-[11px] font-semibold tracking-wide text-fg-subtle uppercase">Selection</p>
          <h3 className="text-base font-semibold text-fg">{selectedNodeCount} nodes selected</h3>
          <p className="text-xs text-fg-subtle">Shared appearance changes apply to every selected node.</p>
        </header>
        <IssueFlag issues={issues} />
        <PanelTabList
          activeTab={activeTab}
          idPrefix={tabId}
          onChange={setActiveTab}
          indicators={indicatorMap('node', issues, { content: false, appearance: true, advanced: false })}
        />
        <PanelTabPane tab="content" activeTab={activeTab} idPrefix={tabId}>
          <p className="py-3 text-xs text-fg-subtle">Content editing is available when one element is selected.</p>
        </PanelTabPane>
        <PanelTabPane tab="appearance" activeTab={activeTab} idPrefix={tabId}>
          <Section title="Style">
            <NodeStyleEditor gp={{}} set={set} />
          </Section>
        </PanelTabPane>
        <PanelTabPane tab="advanced" activeTab={activeTab} idPrefix={tabId}>
          <p className="py-3 text-xs text-fg-subtle">Advanced data is available when one element is selected.</p>
        </PanelTabPane>
      </div>
    )
  }

  if (!selection) {
    return (
      <div className={PANEL}>
        <p className="text-fg-subtle">Select a node or edge to edit its semantic data and style.</p>
      </div>
    )
  }

  if (selection.kind === 'node') {
    const node = selection.node
    const style = (node.style ?? {}) as CSSProperties
    const data = (node.data ?? {}) as unknown as GraphPilotNodeData & { gpStyle?: GraphPilotNodeStyle }
    const gp = data.gpStyle ?? {}
    const label = typeof data.label === 'string' ? data.label : ''
    const semanticType = typeof data.semanticType === 'string' ? data.semanticType : ''
    const primaryStereotype = typeof data.stereotype === 'string' ? data.stereotype.trim() : ''
    const primitive = nodePrimitive(semanticType)
    const set = (patch: NodePatch) => onNodeChange(node.id, patch)
    const patchData = (key: keyof GraphPilotNodeData, value: unknown) => {
      if (value === undefined) set({ clearData: [key] })
      else set({ data: { [key]: value } as Partial<GraphPilotNodeData> })
    }
    const showFeatures = primitive === 'classifier-box' || data.features !== undefined
    const showDefinition = primitive === 'classifier-box' || data.isAbstract !== undefined || data.unit !== undefined || data.quantityKind !== undefined
    const showExtensionPoints = semanticType === 'useCase' || data.extensionPoints !== undefined
    const showConstraint = primaryStereotype === 'constraint' || semanticType === 'constraintBlock' || data.constraintExpression !== undefined || data.constraintParameters !== undefined
    const showPort = primitive === 'port' || data.port !== undefined
    const showJoin = semanticType === 'joinNode' || data.joinSpec !== undefined
    const tabIndicators = indicatorMap('node', issues, {
      content: Boolean(label || showFeatures || showExtensionPoints || showDefinition || showConstraint || showPort || showJoin),
      appearance: Object.keys(style).length > 0 || Object.keys(gp).length > 0,
      advanced: Boolean(semanticType || data.description || data.appliedStereotypes?.length || data.metadata && Object.keys(data.metadata).length),
    })

    return (
      <div className={PANEL}>
        <ElementHeader kind="Node" label={label} semanticType={semanticType} />
        <IssueFlag issues={issues} />
        <PanelTabList activeTab={activeTab} idPrefix={tabId} onChange={setActiveTab} indicators={tabIndicators} />
        <PanelTabPane key={`node-${node.id}-content`} tab="content" activeTab={activeTab} idPrefix={tabId}>
          <Section title="Element">
            <TextField label="Label" value={label} onChange={(value) => set({ label: value })} />
            <HumanType semanticType={semanticType} />
            {diagramType === 'bdd_diagram' && semanticType === 'block' ? (
              <PrimaryStereotypeField value={data.stereotype} onChange={(value) => patchData('stereotype', value)} />
            ) : null}
          </Section>
          {showExtensionPoints ? (
            <Section title="Use case">
              <LinesField
                label="Extension points"
                values={data.extensionPoints ?? []}
                onChange={(values) => patchData('extensionPoints', values.length ? values : undefined)}
              />
            </Section>
          ) : null}
          {showFeatures ? (
            <Section title="Features">
              <FeaturesEditor
                key={node.id}
                features={data.features ?? {}}
                onChange={(value) => patchData('features', value)}
              />
            </Section>
          ) : null}
          {showDefinition ? (
            <Section title="Definition details">
              <BooleanField
                label="Abstract"
                value={data.isAbstract}
                onChange={(value) => patchData('isAbstract', value)}
              />
              <OptionalTextField label="Unit" value={data.unit} onChange={(value) => patchData('unit', value)} />
              <OptionalTextField
                label="Quantity kind"
                value={data.quantityKind}
                onChange={(value) => patchData('quantityKind', value)}
              />
            </Section>
          ) : null}
          {showConstraint ? (
            <Section title="Constraint">
              <OptionalTextField
                label="Constraint expression"
                value={data.constraintExpression}
                onChange={(value) => patchData('constraintExpression', value)}
              />
              <p className="mb-2 text-xs font-semibold text-fg-muted">Constraint parameters</p>
              <ParametersEditor
                parameters={data.constraintParameters ?? []}
                itemLabel="Constraint parameter"
                onChange={(parameters) => patchData('constraintParameters', parameters.length ? parameters : undefined)}
              />
            </Section>
          ) : null}
          {showPort ? (
            <Section title="Port">
              <PortEditor port={data.port ?? {}} onChange={(value) => patchData('port', value)} />
            </Section>
          ) : null}
          {showJoin ? (
            <Section title="Join">
              <OptionalTextField label="Join specification" value={data.joinSpec} onChange={(value) => patchData('joinSpec', value)} />
            </Section>
          ) : null}
        </PanelTabPane>
        <PanelTabPane key={`node-${node.id}-appearance`} tab="appearance" activeTab={activeTab} idPrefix={tabId}>
          <Section title="Dimensions">
            <NumberField label="Width" value={num(style.width)} onChange={(value) => set({ width: value })} />
            <NumberField label="Height" value={num(style.height)} onChange={(value) => set({ height: value })} />
            {primitive === 'classifier-box' ? (
              <Button variant="secondary" size="sm" onClick={() => set(featureBlockMinSize(label, data.features))}>
                Fit to content
              </Button>
            ) : null}
          </Section>
          <Section title="Style">
            <NodeStyleEditor gp={gp} set={set} />
          </Section>
        </PanelTabPane>
        <PanelTabPane key={`node-${node.id}-advanced`} tab="advanced" activeTab={activeTab} idPrefix={tabId}>
          <Section title="Semantics">
            <SemanticTypeField
              kind="node"
              diagramType={diagramType}
              value={semanticType}
              onChange={(value) => set({ semanticType: value })}
            />
            <OptionalTextField
              label="Description"
              value={data.description}
              onChange={(value) => patchData('description', value)}
            />
            <StereotypesEditor
              stereotypes={data.appliedStereotypes ?? []}
              onChange={(value) => patchData('appliedStereotypes', value)}
            />
          </Section>
          <Section title="Identifiers">
            <IdentifierRow label="Node ID" value={node.id} />
          </Section>
          <Section title="Metadata" defaultOpen={false}>
            <JsonObjectField label="Node metadata" value={data.metadata} onChange={(value) => patchData('metadata', value)} />
          </Section>
        </PanelTabPane>
      </div>
    )
  }

  const edge = selection.edge
  const style = (edge.style ?? {}) as CSSProperties
  const data = (edge.data ?? {}) as GraphPilotEdgeData & { gpRoute?: RouteGeometry }
  const route = normalizeRouteGeometry(data.gpRoute)
  const routeMode = route?.mode ?? 'orthogonal'
  const label = typeof edge.label === 'string' ? edge.label : ''
  const semanticType = typeof data.semanticType === 'string' ? data.semanticType : ''
  const set = (patch: EdgePatch) => onEdgeChange(edge.id, patch)
  const patchData = (key: keyof GraphPilotEdgeData, value: unknown) => {
    if (value === undefined) set({ clearData: [key] })
    else set({ data: { [key]: value } as Partial<GraphPilotEdgeData> })
  }
  const patchEndMultiplicity = (key: 'sourceEnd' | 'targetEnd', multiplicity: Multiplicity | undefined) => {
    const current = key === 'sourceEnd' ? data.sourceEnd : data.targetEnd
    const next: RelationshipEnd = { ...(current ?? {}) }
    if (multiplicity === undefined) delete next.multiplicity
    else next.multiplicity = multiplicity
    patchData(key, isEmptyObject(next) ? undefined : next)
  }
  const showEnds = semanticType === 'association' || semanticType === 'composition' || data.sourceEnd !== undefined || data.targetEnd !== undefined
  const showExtension = semanticType === 'extend' || data.condition !== undefined || data.extensionLocations !== undefined
  const showFlow =
    ['controlFlow', 'objectFlow', 'exceptionHandler'].includes(semanticType) ||
    data.guard !== undefined ||
    data.weight !== undefined ||
    data.isInterrupting !== undefined
  const showItemFlows = semanticType === 'association' || data.itemFlows !== undefined
  const canOverrideArrow = ['controlFlow', 'objectFlow', 'exceptionHandler', 'dependency'].includes(semanticType) || data.arrow !== undefined
  const changeRelationshipType = (value: string) => {
    const transition = applyRelationshipSemantic(data, value)
    set({ semanticType: transition.semanticType, data: transition.data, clearData: transition.clearData })
  }
  const tabIndicators = indicatorMap('edge', issues, {
    content: Boolean(label || semanticType || showEnds || showExtension || showFlow || showItemFlows),
    appearance: Object.keys(style).length > 0 || Boolean(route || data.arrow || edge.sourceHandle || edge.targetHandle),
    advanced: Boolean(data.description || data.appliedStereotypes?.length || data.metadata && Object.keys(data.metadata).length || showEnds),
  })

  return (
    <div className={PANEL}>
      <ElementHeader kind="Edge" label={label} semanticType={semanticType} />
      <IssueFlag issues={issues} />
      <PanelTabList activeTab={activeTab} idPrefix={tabId} onChange={setActiveTab} indicators={tabIndicators} />
      <PanelTabPane key={`edge-${edge.id}-content`} tab="content" activeTab={activeTab} idPrefix={tabId}>
        <Section title="Element">
          <TextField label="Label" value={label} onChange={(value) => set({ label: value })} />
          <SemanticTypeField
            kind="edge"
            diagramType={diagramType}
            value={semanticType}
            label="Relationship type"
            onChange={changeRelationshipType}
          />
        </Section>
        {showEnds ? (
          <Section title="Multiplicity">
            <div className="space-y-3">
              <MultiplicityEditor
                prefix="Source end"
                value={data.sourceEnd?.multiplicity}
                onChange={(value) => patchEndMultiplicity('sourceEnd', value)}
              />
              <div className="border-t border-line pt-3">
                <MultiplicityEditor
                  prefix="Target end"
                  value={data.targetEnd?.multiplicity}
                  onChange={(value) => patchEndMultiplicity('targetEnd', value)}
                />
              </div>
            </div>
          </Section>
        ) : null}
        {showExtension ? (
          <Section title="Extension">
            <OptionalTextField label="Condition" value={data.condition} onChange={(value) => patchData('condition', value)} />
            <LinesField
              label="Extension locations"
              values={data.extensionLocations ?? []}
              onChange={(values) => patchData('extensionLocations', values.length ? values : undefined)}
            />
          </Section>
        ) : null}
        {showFlow ? (
          <Section title="Flow">
            <OptionalTextField label="Guard" value={data.guard} onChange={(value) => patchData('guard', value)} />
            <OptionalNumberField label="Weight" value={data.weight} onChange={(value) => patchData('weight', value)} />
            <BooleanField
              label="Interrupting"
              value={data.isInterrupting}
              onChange={(value) => patchData('isInterrupting', value)}
            />
          </Section>
        ) : null}
        {showItemFlows ? (
          <Section title="Item flows">
            <ItemFlowsEditor
              itemFlows={data.itemFlows ?? []}
              onChange={(itemFlows) => patchData('itemFlows', itemFlows.length ? itemFlows : undefined)}
            />
          </Section>
        ) : null}
      </PanelTabPane>
      <PanelTabPane key={`edge-${edge.id}-appearance`} tab="appearance" activeTab={activeTab} idPrefix={tabId}>
        <Section title="Style">
          <ColorField label="Stroke" value={style.stroke as string} onChange={(value) => set({ stroke: value })} />
          <NumberField label="Stroke width" value={num(style.strokeWidth)} onChange={(value) => set({ strokeWidth: value })} />
          <Field label="Line style">
            <Select
              value={dashKey(style.strokeDasharray ? String(style.strokeDasharray) : undefined)}
              onChange={(event) => set({ strokeDasharray: DASH_VALUES[event.target.value as DashKey] })}
            >
              <option value="solid">Solid</option>
              <option value="dashed">Dashed</option>
              <option value="dotted">Dotted</option>
            </Select>
          </Field>
          {canOverrideArrow ? (
            <Field label="Arrow">
              <Select
                value={data.arrow ?? 'forward'}
                onChange={(event) => patchData('arrow', event.target.value as ArrowDirection)}
              >
                <option value="forward">To target</option>
                <option value="backward">To source</option>
                <option value="both">Both ends</option>
                <option value="none">None</option>
              </Select>
            </Field>
          ) : null}
        </Section>
        {semanticType === 'composition' ? (
          <Section title="Direction">
            <p className="text-xs text-fg-subtle">Composition points from part to whole; the filled diamond is at the target.</p>
            <Button variant="secondary" size="sm" onClick={() => set({ swapEnds: true })}>Swap ends</Button>
          </Section>
        ) : null}
        <Section title="Route">
          <div className="space-y-3">
            <Field label="Route mode">
              <Select
                value={routeMode}
                onChange={(event) => set({ route: setRouteMode(route, event.target.value as RouteMode) })}
              >
                <option value="straight">Straight</option>
                <option value="orthogonal">Orthogonal</option>
              </Select>
            </Field>
            <p className="text-xs text-fg-subtle">
              {routeMode === 'straight'
                ? 'Straight boundary-to-boundary route'
                : route?.waypoints?.length
                  ? `Manual orthogonal route · ${route.waypoints.length} waypoint${route.waypoints.length === 1 ? '' : 's'}`
                  : 'Automatic minimal orthogonal route'}
            </p>
            {(['sourceAnchor', 'targetAnchor'] as const).map((key) => {
              const anchor = route?.[key]
              const prefix = key === 'sourceAnchor' ? 'Source' : 'Target'
              return (
                <div key={key} className="grid grid-cols-2 gap-2">
                  <CompactField label={`${prefix} side`}>
                    <Select
                      value={anchor?.side ?? ''}
                      onChange={(event) => {
                        const side = event.target.value as RouteSide | ''
                        const next = { ...(route ?? {}) }
                        if (side) next[key] = { side, offset: anchor?.offset ?? 0.5 }
                        else delete next[key]
                        set({ route: Object.keys(next).length ? next : null })
                      }}
                    >
                      <option value="">Auto</option>
                      <option value="top">Top</option>
                      <option value="right">Right</option>
                      <option value="bottom">Bottom</option>
                      <option value="left">Left</option>
                    </Select>
                  </CompactField>
                  <CompactField label={`${prefix} position`}>
                    <NumberInput
                      min={0}
                      max={100}
                      disabled={!anchor}
                      value={anchor ? Math.round(anchor.offset * 100) : ''}
                      onChange={(event) => {
                        if (!anchor) return
                        const percent = Math.min(100, Math.max(0, Number(event.target.value)))
                        set({ route: { ...(route ?? {}), [key]: { ...anchor, offset: percent / 100 } } })
                      }}
                    />
                  </CompactField>
                </div>
              )
            })}
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => set({ route: route ? { ...route, waypoints: undefined } : null })} disabled={routeMode === 'straight' || !route?.waypoints?.length}>
                Straighten route
              </Button>
              <Button
                variant="secondary"
                onClick={() => set({
                  route: route ? { ...route, sourceAnchor: undefined, targetAnchor: undefined } : null,
                  sourceHandle: null,
                  targetHandle: null,
                })}
                disabled={!route?.sourceAnchor && !route?.targetAnchor && !edge.sourceHandle && !edge.targetHandle}
              >
                Auto anchors
              </Button>
              <Button variant="secondary" onClick={() => set({ route: route ? { ...route, labelOffset: undefined } : null })} disabled={!route?.labelOffset}>
                Reset label
              </Button>
            </div>
            <p className="text-xs text-fg-subtle">Select the relationship on the canvas to drag anchors or move its label{routeMode === 'orthogonal' ? ', and drag segments to add waypoints' : ''}.</p>
          </div>
        </Section>
      </PanelTabPane>
      <PanelTabPane key={`edge-${edge.id}-advanced`} tab="advanced" activeTab={activeTab} idPrefix={tabId}>
        <Section title="Semantics">
          <OptionalTextField
            label="Description"
            value={data.description}
            onChange={(value) => patchData('description', value)}
          />
          <StereotypesEditor
            stereotypes={data.appliedStereotypes ?? []}
            onChange={(value) => patchData('appliedStereotypes', value)}
          />
        </Section>
        {showEnds ? (
          <Section title="Relationship end details">
            <div className="space-y-4">
              <div>
                <p className="mb-2 text-xs font-semibold text-fg-muted">Source end</p>
                <RelationshipEndDetailsEditor
                  prefix="Source end"
                  value={data.sourceEnd ?? {}}
                  onChange={(value) => patchData('sourceEnd', value)}
                />
              </div>
              <div className="border-t border-line pt-3">
                <p className="mb-2 text-xs font-semibold text-fg-muted">Target end</p>
                <RelationshipEndDetailsEditor
                  prefix="Target end"
                  value={data.targetEnd ?? {}}
                  onChange={(value) => patchData('targetEnd', value)}
                />
              </div>
            </div>
          </Section>
        ) : null}
        <Section title="Identifiers">
          <div className="space-y-1">
            <IdentifierRow label="Edge ID" value={edge.id} />
            <IdentifierRow label="Source ID" value={edge.source} />
            <IdentifierRow label="Target ID" value={edge.target} />
          </div>
        </Section>
        <Section title="Metadata" defaultOpen={false}>
          <JsonObjectField label="Edge metadata" value={data.metadata} onChange={(value) => patchData('metadata', value)} />
        </Section>
      </PanelTabPane>
    </div>
  )
}
