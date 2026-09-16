/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { ToolbarMore } from './ToolbarMore'

afterEach(cleanup)

describe('ToolbarMore', () => {
  it('opens on click and invokes the chosen item, then closes', () => {
    const onPick = vi.fn()
    render(<ToolbarMore items={[{ label: 'Duplicate (Ctrl+D)', onClick: onPick }]} />)

    expect(screen.queryByRole('menu')).toBeNull()
    fireEvent.click(screen.getByLabelText('More actions'))
    expect(screen.getByRole('menu')).toBeTruthy()

    fireEvent.click(screen.getByText('Duplicate (Ctrl+D)'))
    expect(onPick).toHaveBeenCalledTimes(1)
    expect(screen.queryByRole('menu')).toBeNull()
  })

  it('closes on Escape', () => {
    render(<ToolbarMore items={[{ label: 'Fit view', onClick: vi.fn() }]} />)
    fireEvent.click(screen.getByLabelText('More actions'))
    expect(screen.getByRole('menu')).toBeTruthy()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('menu')).toBeNull()
  })
})
