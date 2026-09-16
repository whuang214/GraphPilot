import type { Node } from '@xyflow/react'
import type { ModelFeatures } from '@/types/diagram'
import type { NodePatch } from '@/editor/components/PropertyPanel'
import { featureBlockMinHeight } from './bddCompartments'
import { nodePrimitive } from './elementCatalog'

const hasOwn = (value: object, key: PropertyKey): boolean => Object.prototype.hasOwnProperty.call(value, key)

// Apply a NodePatch to a single React Flow node. Wrapper size stays in `style`,
// visual style stays in runtime `data.gpStyle`, and canonical semantic fields are
// merged into `data`. The helper is deliberately shallow/generic at the canonical
// data boundary; structured editors send a complete replacement for the one nested
// value they edit (features, port, ...), preserving its untouched members first.
export function applyNodePatch(node: Node, patch: NodePatch): Node {
  const style = { ...(node.style ?? {}) }
  if (patch.width !== undefined) style.width = patch.width
  if (patch.height !== undefined) style.height = patch.height

  const existingGpStyle = node.data?.gpStyle
  const gpStyle: Record<string, unknown> =
    existingGpStyle && typeof existingGpStyle === 'object' && !Array.isArray(existingGpStyle)
      ? { ...(existingGpStyle as Record<string, unknown>) }
      : {}
  let styleChanged = false
  if (patch.background !== undefined) {
    gpStyle.background = patch.background
    styleChanged = true
  }
  if (patch.color !== undefined) {
    gpStyle.color = patch.color
    styleChanged = true
  }
  if (patch.borderColor !== undefined) {
    gpStyle.borderColor = patch.borderColor
    styleChanged = true
  }
  if (patch.borderWidth !== undefined) {
    gpStyle.borderWidth = patch.borderWidth
    styleChanged = true
  }
  if (patch.borderStyle !== undefined) {
    gpStyle.borderStyle = patch.borderStyle
    styleChanged = true
  }

  const data: Record<string, unknown> = { ...(node.data ?? {}), ...(patch.data ?? {}) }
  if (existingGpStyle !== undefined || styleChanged) data.gpStyle = gpStyle
  if (patch.label !== undefined) data.label = patch.label
  if (patch.semanticType !== undefined) data.semanticType = patch.semanticType
  for (const key of patch.clearData ?? []) delete data[key]

  const featuresChanged =
    (patch.data !== undefined && hasOwn(patch.data, 'features')) || patch.clearData?.includes('features') === true
  const semanticBecameClassifier =
    patch.semanticType !== undefined && nodePrimitive(patch.semanticType) === 'classifier-box'
  if (
    nodePrimitive(typeof data.semanticType === 'string' ? data.semanticType : '') === 'classifier-box' &&
    (featuresChanged || semanticBecameClassifier)
  ) {
    style.height = featureBlockMinHeight(data.features as ModelFeatures | undefined)
  }

  return { ...node, data, style }
}
