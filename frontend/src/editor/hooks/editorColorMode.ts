import { createContext, useContext } from 'react'
import type { ColorMode } from '@/editor/shell/useColorMode'

// The editor's current color mode, shared with the custom node renderers so they
// can theme the DEFAULT (unauthored) shape look for dark mode while preserving
// authored colors. Provided by EditorPage from useColorMode.
export const EditorColorModeContext = createContext<ColorMode>('light')

export function useEditorColorMode(): ColorMode {
  return useContext(EditorColorModeContext)
}
