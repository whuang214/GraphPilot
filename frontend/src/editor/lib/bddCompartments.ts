import type { ModelFeatures } from '@/types/diagram'

export interface FeatureCompartment {
  label: string
  items: string[]
}

// Exact mirrors of backend/services/diagrams/catalog/constants.py. The canvas consumes
// the same derived rows as the SVG renderer, and auto-fit callers use the same arithmetic.
const FONT_SIZE = 12
const HEADER_HEIGHT = 34
const LINE_HEIGHT = FONT_SIZE * 1.2
const COMPARTMENT_PAD = 6
const EMPTY_MIN_HEIGHT = 48
const FILLED_MIN_HEIGHT = 90

type UnknownRecord = Record<string, unknown>

function isRecord(value: unknown): value is UnknownRecord {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

// Python's renderer interpolates arbitrary JSON defaults with `str(value)`. Mirror
// that spelling (not JavaScript's `[object Object]`, lowercase booleans, etc.) so a
// structured default is identical on the canvas and in the exported SVG.
function pythonString(value: unknown, nested = false): string {
  if (value === null) return 'None'
  if (value === true) return 'True'
  if (value === false) return 'False'
  if (typeof value === 'string') {
    if (!nested) return value
    return `'${value.replaceAll('\\', '\\\\').replaceAll("'", "\\'")}'`
  }
  if (Array.isArray(value)) return `[${value.map((item) => pythonString(item, true)).join(', ')}]`
  if (isRecord(value)) {
    const entries = Object.entries(value).map(
      ([key, item]) => `${pythonString(key, true)}: ${pythonString(item, true)}`,
    )
    return `{${entries.join(', ')}}`
  }
  return String(value)
}

function trimmed(value: unknown): string {
  return pythonString(value).trim()
}

function multiplicityText(value: unknown): string {
  if (!isRecord(value)) return ''
  const { lower, upper } = value
  if (lower === null || lower === undefined || upper === null || upper === undefined) return ''
  return lower === upper ? pythonString(lower) : `${pythonString(lower)}..${pythonString(upper)}`
}

/**
 * Derive display-only classifier compartments from canonical ModelFeatures.
 *
 * This intentionally follows backend `feature_compartments` in order and spelling:
 * property groups are inserted on first occurrence, then operations, receptions,
 * constraints, and literals are appended when non-empty.
 */
export function featureCompartments(features: ModelFeatures | null | undefined): FeatureCompartment[] {
  if (!isRecord(features)) return []

  const grouped = new Map<string, string[]>()
  const properties = Array.isArray(features.properties) ? features.properties : []
  for (const value of properties) {
    if (!isRecord(value)) continue
    const name = trimmed(value.name || '')
    if (!name) continue

    const kind = pythonString(value.kind || 'property')
    const typeName = trimmed(value.type || '')
    const direction = trimmed(value.direction || '')
    const multiplicity = multiplicityText(value.multiplicity)
    let text = kind === 'flow' ? `${direction} ${name}`.trim() : name
    if (typeName) text += `: ${typeName}`
    if (multiplicity) text += ` [${multiplicity}]`
    if (value.default !== null && value.default !== undefined) text += ` = ${pythonString(value.default)}`

    const label = `${kind} properties`
    const items = grouped.get(label)
    if (items) items.push(text)
    else grouped.set(label, [text])
  }

  // `parameters` and `returnType` are accepted, validated and persisted, and used to be
  // dropped here — every operation drew as `name()`. A field that is valid, saved and
  // invisible is worse than a rejected one, because the author believes it was recorded.
  // Mirrors backend `feature_compartments`; the two must agree exactly.
  const operations = (Array.isArray(features.operations) ? features.operations : [])
    .filter(isRecord)
    .map((operation) => {
      const name = trimmed(operation.name || '')
      if (!name) return ''
      const parameters = (Array.isArray(operation.parameters) ? operation.parameters : [])
        .map((parameter) => {
          // Canonical parameters are objects; a draft supplies a plain string, which the
          // backend converts on the way in. Both shapes reach this function.
          if (typeof parameter === 'string') return trimmed(parameter)
          if (!isRecord(parameter)) return ''
          const parameterName = trimmed(parameter.name || '')
          if (!parameterName) return ''
          const parameterType = trimmed(parameter.type || '')
          return parameterType ? `${parameterName}: ${parameterType}` : parameterName
        })
        .filter(Boolean)
        .join(', ')
      const returnType = trimmed(operation.returnType || '')
      return `${name}(${parameters})${returnType ? `: ${returnType}` : ''}`
    })
    .filter(Boolean)
  if (operations.length) grouped.set('operations', operations)

  const receptions = (Array.isArray(features.receptions) ? features.receptions : [])
    .map(trimmed)
    .filter(Boolean)
  if (receptions.length) grouped.set('receptions', receptions)

  // UML writes a named constraint as `{name} expression`, which is how a reader tells
  // one invariant from another when a block carries several. The name was discarded.
  const constraints = (Array.isArray(features.constraints) ? features.constraints : [])
    .filter(isRecord)
    .map((constraint) => {
      const expression = trimmed(constraint.expression || '')
      if (!expression) return ''
      const name = trimmed(constraint.name || '')
      return name ? `{${name}} ${expression}` : expression
    })
    .filter(Boolean)
  if (constraints.length) grouped.set('constraints', constraints)

  const literals = (Array.isArray(features.literals) ? features.literals : [])
    .map(trimmed)
    .filter(Boolean)
  if (literals.length) grouped.set('literals', literals)

  return Array.from(grouped, ([label, items]) => ({ label, items }))
}

/**
 * The vertical space one compartment takes up when drawn.
 *
 * Mirrors `bdd_compartment_height` and, through it, the SVG renderer's
 * `_draw_classifier_compartments`: the italic heading's baseline sits `FONT_SIZE + 2`
 * below the compartment's top edge, then every row advances by one line.
 *
 * The size and the drawing used to be worked out separately and disagreed by 8px per
 * compartment, so a block with three of them lost its last line off the bottom.
 */
function compartmentHeight(itemCount: number): number {
  return FONT_SIZE + 2 + (1 + itemCount) * LINE_HEIGHT
}

/** Minimum classifier height for its derived, non-empty feature compartments. */
export function featureBlockMinHeight(features: ModelFeatures | null | undefined): number {
  const compartments = featureCompartments(features)
  if (compartments.length === 0) return EMPTY_MIN_HEIGHT

  let height = HEADER_HEIGHT
  for (const compartment of compartments) {
    height += compartmentHeight(compartment.items.length)
  }
  // The last row's descender falls below its baseline.
  height += COMPARTMENT_PAD
  return Math.round(Math.max(height, FILLED_MIN_HEIGHT) * 10) / 10
}

export function featureBlockMinSize(
  label: string,
  features: ModelFeatures | null | undefined,
): { width: number; height: number } {
  const compartments = featureCompartments(features)
  const longest = [label, ...compartments.flatMap((compartment) => [compartment.label, ...compartment.items])]
    .reduce((current, value) => value.length > current.length ? value : current, '')
  return {
    width: Math.min(320, Math.max(190, longest.length * 7.5 + 36)),
    height: featureBlockMinHeight(features),
  }
}
