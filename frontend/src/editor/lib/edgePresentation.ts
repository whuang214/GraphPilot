import type { GraphPilotEdgeData, RelationshipEnd } from '@/types/diagram'

function multiplicityText(end: RelationshipEnd | undefined): string {
  const multiplicity = end?.multiplicity
  if (!multiplicity) return ''
  return multiplicity.lower === multiplicity.upper
    ? String(multiplicity.lower)
    : `${multiplicity.lower}..${multiplicity.upper}`
}

export function relationshipEndLabel(end: RelationshipEnd | undefined): string {
  return [end?.role?.trim(), multiplicityText(end)].filter(Boolean).join(' ')
}

export function edgeDisplayLabel(label: unknown, data: GraphPilotEdgeData | undefined): string {
  const semanticType = data?.semanticType
  let text = typeof label === 'string' ? label.trim() : ''
  if (semanticType === 'include' || semanticType === 'extend') {
    const keyword = `«${semanticType}»`
    if (!text.startsWith(keyword)) text = `${keyword}${text ? ` ${text}` : ''}`
  }
  if (data?.condition) text = `${text} [${data.condition}]`.trim()
  if (data?.guard) text = `${text} [${data.guard}]`.trim()
  return text
}
