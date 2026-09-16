import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Vitest is restricted to the unit/component tests under src/. The Playwright
// E2E specs in e2e/ use a different runner and are run via `npm run e2e`, so
// they must be excluded here (otherwise Vitest's default glob picks up the
// `*.spec.ts` files and fails on the @playwright/test import).
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  test: {
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
