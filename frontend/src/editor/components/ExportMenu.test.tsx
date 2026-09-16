/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { ExportMenu } from './ExportMenu'

afterEach(cleanup)

describe('ExportMenu', () => {
  it('opens on click and invokes the chosen format handler', () => {
    const onExportPng = vi.fn()
    const onExportSvg = vi.fn()
    render(<ExportMenu onExportPng={onExportPng} onExportSvg={onExportSvg} />)

    // Menu is closed initially.
    expect(screen.queryByRole('menu')).toBeNull()

    fireEvent.click(screen.getByText('Export'))
    expect(screen.getByRole('menu')).toBeTruthy()

    fireEvent.click(screen.getByText('PNG image'))
    expect(onExportPng).toHaveBeenCalledTimes(1)
    expect(onExportSvg).not.toHaveBeenCalled()
    // Choosing an item closes the menu.
    expect(screen.queryByRole('menu')).toBeNull()
  })

  it('exports SVG and closes on Escape', () => {
    const onExportSvg = vi.fn()
    render(<ExportMenu onExportPng={vi.fn()} onExportSvg={onExportSvg} />)

    fireEvent.click(screen.getByText('Export'))
    fireEvent.click(screen.getByText('SVG vector'))
    expect(onExportSvg).toHaveBeenCalledTimes(1)

    fireEvent.click(screen.getByText('Export'))
    expect(screen.getByRole('menu')).toBeTruthy()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('menu')).toBeNull()
  })
})
