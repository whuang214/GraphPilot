// Minimal className combiner: filters out falsy parts and joins with spaces.
// Kept dependency-free (no clsx/tailwind-merge) for the small in-house primitive set.
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ')
}
