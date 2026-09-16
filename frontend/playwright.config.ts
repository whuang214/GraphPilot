import { fileURLToPath } from 'node:url'
import { defineConfig, devices } from '@playwright/test'

// Chromium-only end-to-end smoke suite for the editor. Playwright boots
// the Django backend and the Vite dev server, then drives a real browser through
// the load -> edit -> save round-trip plus a few UI checks. Run with:
//   npm run e2e            (headless)
//   npm run e2e -- --headed  (watch it)

// CI puts Python on PATH; local runs use the repo virtualenv on either Windows
// or POSIX platforms.
const isCI = !!process.env.CI
const backendPort = process.env.GRAPHPILOT_E2E_BACKEND_PORT ?? '18080'
const frontendPort = process.env.GRAPHPILOT_E2E_FRONTEND_PORT ?? '15173'
const backendURL = `http://127.0.0.1:${backendPort}`
const frontendURL = `http://127.0.0.1:${frontendPort}`
const frontendDir = fileURLToPath(new URL('.', import.meta.url))
const backendDir = fileURLToPath(new URL('../backend/', import.meta.url))
const pythonCmd = isCI
  ? 'python'
  : process.platform === 'win32'
    ? '..\\.venv\\Scripts\\python.exe'
    : '../.venv/bin/python'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  timeout: 30_000,
  use: {
    baseURL: frontendURL,
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: `${pythonCmd} manage.py runserver 127.0.0.1:${backendPort} --noreload`,
      cwd: backendDir,
      env: { GRAPHPILOT_CORS_ALLOWED_ORIGINS: frontendURL },
      url: `${backendURL}/api/health`,
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
      cwd: frontendDir,
      env: { VITE_API_BASE_URL: backendURL },
      url: frontendURL,
      reuseExistingServer: false,
      timeout: 60_000,
    },
  ],
})
