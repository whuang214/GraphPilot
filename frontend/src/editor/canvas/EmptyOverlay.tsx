// Non-interactive hint shown over an empty canvas (no nodes). `pointer-events-none`
// so it never blocks drops onto the pane.
export function EmptyOverlay() {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
      <div className="rounded-lg border border-dashed border-line bg-surface/80 px-4 py-3 text-sm text-fg-subtle">
        Drag a shape from the palette to begin.
      </div>
    </div>
  )
}
