import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from 'react'
import { cn } from './cn'

const CONTROL =
  'h-8 w-full rounded-md border border-line bg-surface px-2 text-sm text-fg ' +
  'placeholder:text-fg-subtle focus-visible:outline-none focus-visible:ring-2 ' +
  'focus-visible:ring-accent/50 disabled:opacity-50'

export function Input({ className, type, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input type={type ?? 'text'} className={cn(CONTROL, className)} {...props} />
}

export function NumberInput({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input type="number" className={cn(CONTROL, className)} {...props} />
}

export function ColorInput({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      type="color"
      className={cn('h-8 w-full cursor-pointer rounded-md border border-line bg-surface p-1', className)}
      {...props}
    />
  )
}

export function Select({ className, children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn(CONTROL, 'cursor-pointer', className)} {...props}>
      {children}
    </select>
  )
}

/** Vertical label + control group. Mirrors the prior PropertyPanel row layout. */
export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="mb-3 flex flex-col gap-1 text-sm">
      <span className="font-semibold text-fg-muted">{label}</span>
      {children}
    </label>
  )
}
