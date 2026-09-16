/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { TopBar } from './TopBar'

afterEach(cleanup)

describe('TopBar source information', () => {
  it('keeps transport details behind one information button', () => {
    render(
      <TopBar
        name="Order Flow"
        diagramType="activity_diagram"
        dirty={false}
        sourceInfo={{ location: 'C:/work/.graphpilot/order.gp.json', state: 'Writable path', revision: 'abcdef123456', copyPath: 'C:/work/.graphpilot/order.gp.json' }}
        actions={<button type="button">Save</button>}
      />,
    )
    expect(screen.queryByText('Workspace')).toBeNull()
    expect(screen.queryByText('ⓘ')).toBeNull()
    expect(screen.queryByText('C:/work/.graphpilot/order.gp.json')).toBeNull()
    const trigger = screen.getByRole('button', { name: 'Diagram information' })
    expect(trigger.className).toContain('w-7')
    expect(trigger.querySelector('svg')).toBeTruthy()
    fireEvent.click(trigger)
    expect(screen.getByText('C:/work/.graphpilot/order.gp.json')).toBeTruthy()
    expect(screen.getByText('Writable path')).toBeTruthy()
    expect(screen.getByText('abcdef123456')).toBeTruthy()
  })

  it('copies a path only when one is available', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
    render(
      <TopBar
        name="Order Flow"
        diagramType="activity_diagram"
        dirty
        sourceInfo={{ location: 'C:/order.gp.json', state: 'Writable path', copyPath: 'C:/order.gp.json' }}
        actions={null}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: 'Diagram information' }))
    fireEvent.click(screen.getByRole('button', { name: 'Copy path' }))
    expect(writeText).toHaveBeenCalledWith('C:/order.gp.json')
  })

  it('dismisses diagram information on Escape or an outside click', () => {
    render(
      <TopBar
        name="Order Flow"
        diagramType="activity_diagram"
        dirty={false}
        sourceInfo={{ location: 'C:/order.gp.json', state: 'Writable path', copyPath: 'C:/order.gp.json' }}
        actions={<button type="button">Save</button>}
      />,
    )
    const trigger = screen.getByRole('button', { name: 'Diagram information' })
    fireEvent.click(trigger)
    screen.getByRole('button', { name: 'Copy path' }).focus()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('dialog', { name: 'Diagram information' })).toBeNull()
    expect(document.activeElement).toBe(trigger)

    fireEvent.click(trigger)
    fireEvent.mouseDown(screen.getByRole('button', { name: 'Save' }))
    expect(screen.queryByRole('dialog', { name: 'Diagram information' })).toBeNull()
  })
})
