import type { ButtonHTMLAttributes } from 'react'
import { cn } from './cn'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
export type ButtonSize = 'sm' | 'md'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
}

// Hover/active feedback. `bg-surface-2` was nearly identical
// to the surface, so hover read as nothing; use a theme-aware foreground tint that
// darkens further on press, and darken the accent/danger on press too.
const VARIANT: Record<ButtonVariant, string> = {
  primary: 'bg-accent text-accent-fg hover:bg-accent-hover active:brightness-90',
  secondary: 'bg-surface text-fg border border-line hover:bg-fg/10 active:bg-fg/20',
  ghost: 'bg-transparent text-fg hover:bg-fg/10 active:bg-fg/20',
  danger: 'bg-danger text-danger-fg hover:opacity-90 active:opacity-80',
}

const SIZE: Record<ButtonSize, string> = {
  sm: 'h-7 px-2 text-xs',
  md: 'h-8 px-3 text-sm',
}

export function Button({ variant = 'secondary', size = 'md', className, type, ...props }: ButtonProps) {
  return (
    <button
      // Default to type="button" so a button inside a <form> does not submit by accident.
      type={type ?? 'button'}
      className={cn(
        'inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors',
        'disabled:opacity-50 disabled:pointer-events-none',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50',
        VARIANT[variant],
        SIZE[size],
        className,
      )}
      {...props}
    />
  )
}
