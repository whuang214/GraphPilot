/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { PreviewMenu } from './PreviewMenu'

afterEach(cleanup)

describe('PreviewMenu', () => {
  it('opens on click and invokes the chosen action', () => {
    const onRender = vi.fn()
    const onJson = vi.fn()
    render(<PreviewMenu onRender={onRender} onJson={onJson} />)

    // Menu is closed initially.
    expect(screen.queryByRole('menu')).toBeNull()

    fireEvent.click(screen.getByText('Preview'))
    expect(screen.getByRole('menu')).toBeTruthy()

    fireEvent.click(screen.getByText('JSON'))
    expect(onJson).toHaveBeenCalledTimes(1)
    expect(onRender).not.toHaveBeenCalled()
    // Choosing an item closes the menu.
    expect(screen.queryByRole('menu')).toBeNull()
  })

  it('invokes the SVG render and closes on Escape', () => {
    const onRender = vi.fn()
    render(<PreviewMenu onRender={onRender} onJson={vi.fn()} />)

    fireEvent.click(screen.getByText('Preview'))
    fireEvent.click(screen.getByText('Render (SVG)'))
    expect(onRender).toHaveBeenCalledTimes(1)

    fireEvent.click(screen.getByText('Preview'))
    expect(screen.getByRole('menu')).toBeTruthy()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('menu')).toBeNull()
  })
})
