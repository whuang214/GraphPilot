interface StatusBarProps {
  nodeCount: number
  edgeCount: number
  saveText: string
  // Optional trailing slot (currently the zoom percentage readout).
  extra?: import('react').ReactNode
}

// Bottom status strip: element counts on the left, save state + optional extras
// on the right.
export function StatusBar({ nodeCount, edgeCount, saveText, extra }: StatusBarProps) {
  return (
    <footer className="flex items-center gap-4 border-t border-line bg-surface px-4 py-1 text-xs text-fg-subtle">
      <span>
        {nodeCount} {nodeCount === 1 ? 'node' : 'nodes'}
      </span>
      <span>
        {edgeCount} {edgeCount === 1 ? 'edge' : 'edges'}
      </span>
      <div className="ml-auto flex items-center gap-4">
        {extra}
        <span>{saveText}</span>
      </div>
    </footer>
  )
}
