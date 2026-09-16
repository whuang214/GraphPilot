import { Component } from 'react'
import type { ReactNode } from 'react'
import EditorPage from '@/editor/EditorPage'
import { Button, ToastProvider } from '@/ui'

export class AppErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  render() {
    if (this.state.failed) {
      return (
        <main className="flex min-h-screen items-center justify-center bg-surface-2 p-6">
          <div className="max-w-md rounded-xl border border-line bg-surface p-8 text-center shadow-sm">
            <h1 className="text-xl font-semibold text-fg">GraphPilot could not display this diagram</h1>
            <p className="mt-2 mb-4 text-sm text-fg-muted">Reload the editor, or return without the current diagram link.</p>
            <div className="flex justify-center gap-2">
              <Button variant="secondary" onClick={() => window.location.reload()}>Reload</Button>
              <Button
                variant="primary"
                onClick={() => {
                  const url = new URL(window.location.href)
                  url.searchParams.delete('diagramPath')
                  window.location.assign(url)
                }}
              >
                Return home
              </Button>
            </div>
          </div>
        </main>
      )
    }
    return this.props.children
  }
}

// The editor owns its own empty/landing state (shown when no diagram is open), so
// there is no separate Home route: every path renders the editor. An MCP agent
// link opens a specific diagram via `?diagramPath=`.
function App() {
  return (
    <AppErrorBoundary>
      <ToastProvider>
        <EditorPage />
      </ToastProvider>
    </AppErrorBoundary>
  )
}

export default App
