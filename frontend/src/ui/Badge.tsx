import type { ReactNode } from 'react'
import { cn } from './cn'

export function Badge({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex shrink-0 items-center whitespace-nowrap rounded-full border border-line bg-surface-2 px-2 py-0.5 text-xs font-medium text-fg-muted',
        className,
      )}
    >
      {children}
    </span>
  )
}
