import { createContext, useContext } from 'react'
import type { RouteGeometry } from './edgeRouting'

export interface EdgeRouteEditApi {
  start: () => void
  setRoute: (edgeId: string, route: RouteGeometry | undefined) => void
}

export const EdgeRouteEditContext = createContext<EdgeRouteEditApi | null>(null)

export function useEdgeRouteEdit(): EdgeRouteEditApi | null {
  return useContext(EdgeRouteEditContext)
}
