/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { Button, Modal, ToastProvider, useToast } from './index'
import { AppErrorBoundary } from '@/App'

afterEach(cleanup)

describe('Button', () => {
  it('fires onClick and reflects the disabled prop', () => {
    const onClick = vi.fn()
    const { rerender } = render(<Button onClick={onClick}>Go</Button>)
    fireEvent.click(screen.getByText('Go'))
    expect(onClick).toHaveBeenCalledTimes(1)
    rerender(
      <Button onClick={onClick} disabled>
        Go
      </Button>,
    )
    expect((screen.getByText('Go') as HTMLButtonElement).disabled).toBe(true)
  })
})

describe('Modal', () => {
  it('renders children when open and closes on Escape', () => {
    const onClose = vi.fn()
    const { rerender } = render(
      <Modal open onClose={onClose} title="Title">
        body-content
      </Modal>,
    )
    expect(screen.getByText('body-content')).toBeTruthy()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
    rerender(
      <Modal open={false} onClose={onClose}>
        body-content
      </Modal>,
    )
    expect(screen.queryByText('body-content')).toBeNull()
  })

  it('applies the size prop max-width class', () => {
    render(
      <Modal open onClose={() => {}} size="xl">
        wide-body
      </Modal>,
    )
    const panel = screen.getByRole('dialog')
    expect(panel.className).toContain('max-w-4xl')
  })
})

describe('AppErrorBoundary', () => {
  it('shows a recovery screen when a child render fails', () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    function Broken(): never {
      throw new Error('boom')
    }
    try {
      render(
        <AppErrorBoundary>
          <Broken />
        </AppErrorBoundary>,
      )
      expect(screen.getByText(/could not display this diagram/i)).toBeTruthy()
      expect(screen.getByRole('button', { name: 'Reload' })).toBeTruthy()
      expect(screen.getByRole('button', { name: 'Return home' })).toBeTruthy()
    } finally {
      errorSpy.mockRestore()
    }
  })
})

describe('Toast', () => {
  it('renders a notified message via the provider', () => {
    function Trigger() {
      const { notify } = useToast()
      return (
        <button type="button" onClick={() => notify('success', 'Saved!')}>
          go
        </button>
      )
    }
    render(
      <ToastProvider>
        <Trigger />
      </ToastProvider>,
    )
    expect(screen.queryByText('Saved!')).toBeNull()
    fireEvent.click(screen.getByText('go'))
    expect(screen.getByText('Saved!')).toBeTruthy()
  })

  it('clears the pending auto-dismiss timer on unmount', () => {
    // The 4s auto-dismiss timer must be cleared when the provider unmounts, so it
    // never fires (and updates state) against a dead component.
    function Trigger() {
      const { notify } = useToast()
      return (
        <button type="button" onClick={() => notify('info', 'Bye')}>
          go
        </button>
      )
    }
    const setSpy = vi.spyOn(globalThis, 'setTimeout')
    const clearSpy = vi.spyOn(globalThis, 'clearTimeout')
    try {
      const { unmount } = render(
        <ToastProvider>
          <Trigger />
        </ToastProvider>,
      )
      fireEvent.click(screen.getByText('go'))
      // Identify the toast's own timer (the 4000ms auto-dismiss) — React's
      // scheduler also schedules unrelated timers, so match on the delay.
      const idx = setSpy.mock.calls.findIndex((c) => c[1] === 4000)
      expect(idx).toBeGreaterThanOrEqual(0)
      const timerId = setSpy.mock.results[idx]?.value
      unmount()
      expect(clearSpy).toHaveBeenCalledWith(timerId)
    } finally {
      setSpy.mockRestore()
      clearSpy.mockRestore()
    }
  })
})
