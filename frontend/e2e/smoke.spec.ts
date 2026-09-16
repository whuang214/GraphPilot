import { readFileSync, writeFileSync } from 'node:fs'
import { expect, test } from '@playwright/test'
import type { Locator, Page } from '@playwright/test'
import { allowedNodeSpecs } from '../src/editor/lib/elementCatalog.js'
import { authorableNodeFixtures, seedAuthorableDiagram, seedBddDiagram, seedDiagram, seedUseCaseDiagram } from './seed.js'

const e2eBackendPort = process.env.GRAPHPILOT_E2E_BACKEND_PORT ?? '18080'
const e2eApiBaseURL = `http://127.0.0.1:${e2eBackendPort}`

// Each test gets a fresh browser context (isolated localStorage) and a freshly
// re-seeded diagram file, so they are independent and order-free.
// The seed is the dedicated activity fixture at e2e/fixtures/device-repair-assessment.gp.json
// (10 nodes / 11 edges): Start -> Receive Device -> Fork
// -> {Run Hardware Diagnostics | Check Warranty} -> Join
// -> Covered? -> {Schedule Repair | Prepare Quotation} -> Assessment Complete.
test.beforeEach(async ({ page }) => {
  const path = seedDiagram()
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Receive Device')).toBeVisible()
})

async function setZoomPercent(page: Page, target: number) {
  const pane = page.locator('.react-flow__pane')
  const bounds = await pane.boundingBox()
  if (!bounds) throw new Error('expected canvas bounds')
  await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2)
  for (let attempt = 0; attempt < 80; attempt += 1) {
    const text = await page.getByTitle('Zoom level').textContent()
    const current = Number.parseInt(text ?? '', 10)
    if (current === target) return
    const difference = target - current
    await page.mouse.wheel(0, difference > 0 ? -Math.min(20, Math.max(1, difference)) : Math.min(20, Math.max(1, -difference)))
    await page.waitForTimeout(20)
  }
  throw new Error(`could not reach ${target}% zoom`)
}

async function nodeFlowPosition(node: Locator): Promise<{ x: number; y: number }> {
  return node.evaluate((element) => {
    const transform = (element as unknown as { style: { transform: string } }).style.transform
    const match = transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)/)
    if (!match) throw new Error(`expected node translate transform, received ${transform}`)
    return { x: Number(match[1]), y: Number(match[2]) }
  })
}

test('loads the seeded diagram with all nodes', async ({ page }) => {
  await expect(page.locator('.react-flow__node')).toHaveCount(10)
  await expect(page.getByText('Run Hardware Diagnostics')).toBeVisible()
  await expect(page.getByText('Assessment Complete')).toBeVisible()
})

test('moves and reloads every authorable node without starting connections', async ({ page }) => {
  test.setTimeout(60_000) // The 17-node trace also needs time to finish during browser teardown.
  const prepareCanvas = async () => {
    await expect(page.locator('.react-flow__node')).toHaveCount(authorableNodeFixtures.length)
    const viewport = page.locator('.react-flow__viewport')
    // The initial 100% is a default, before the asynchronous fit of this large fixture.
    await expect(viewport).not.toHaveCSS('transform', 'matrix(1, 0, 0, 1, 0, 0)')
    const settle = () => expect.poll(async () => {
      const before = await viewport.getAttribute('style')
      await page.waitForTimeout(100)
      return (await viewport.getAttribute('style')) === before
    }).toBe(true)
    await settle()
    await setZoomPercent(page, 100)
    await settle()
  }
  const consoleProblems: string[] = []
  const failedResponses: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') consoleProblems.push(message.text())
  })
  page.on('response', (response) => {
    if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`)
  })
  expect(authorableNodeFixtures.map((fixture) => fixture.semanticType).sort()).toEqual(
    allowedNodeSpecs('custom').map((spec) => spec.semanticType).sort(),
  )
  await page.setViewportSize({ width: 2800, height: 1700 })
  const path = seedAuthorableDiagram()
  const original = JSON.parse(readFileSync(path, 'utf8')) as {
    nodes: Array<{ id: string; position: { x: number; y: number } }>
  }
  const originalById = new Map(original.nodes.map((node) => [node.id, node.position]))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await prepareCanvas()

  for (const [index, fixture] of authorableNodeFixtures.entries()) {
    const id = `audit-${fixture.semanticType}`
    const node = page.locator(`.react-flow__node[data-id="${id}"]`)
    await expect(node).toContainText(`Audit ${fixture.semanticType}`)
    expect(await nodeFlowPosition(node)).toEqual(originalById.get(id))
    const before = await node.boundingBox()
    if (!before) throw new Error(`expected ${fixture.semanticType} bounds`)
    await page.mouse.move(before.x + before.width / 2, before.y + before.height / 2)
    await page.mouse.down()
    await page.mouse.move(before.x + before.width / 2 + 32 + index % 3, before.y + before.height / 2 + 20 + index % 2, { steps: 5 })
    await page.mouse.up()
    await expect.poll(async () => (await nodeFlowPosition(node)).x).toBeGreaterThan((originalById.get(id)?.x ?? 0) + 10)
    await expect.poll(async () => (await nodeFlowPosition(node)).y).toBeGreaterThan((originalById.get(id)?.y ?? 0) + 10)
    await expect(node).toHaveClass(/selected/)
  }
  await expect(page.locator('.react-flow__edge')).toHaveCount(0)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as typeof original
  const savedById = new Map(saved.nodes.map((node) => [node.id, node.position]))
  for (const fixture of authorableNodeFixtures) {
    const id = `audit-${fixture.semanticType}`
    const before = originalById.get(id)
    const after = savedById.get(id)
    expect(after?.x).toBeGreaterThan((before?.x ?? 0) + 10)
    expect(after?.y).toBeGreaterThan((before?.y ?? 0) + 10)
  }

  await page.reload()
  await prepareCanvas()
  for (const fixture of authorableNodeFixtures) {
    const id = `audit-${fixture.semanticType}`
    const node = page.locator(`.react-flow__node[data-id="${id}"]`)
    const reloaded = await nodeFlowPosition(node)
    const expected = savedById.get(id)
    expect(reloaded.x).toBeCloseTo(expected?.x ?? Number.NaN, 1)
    expect(reloaded.y).toBeCloseTo(expected?.y ?? Number.NaN, 1)
    const box = await node.boundingBox()
    if (!box) throw new Error(`expected reloaded ${fixture.semanticType} bounds`)
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2)
    await expect(node).toHaveClass(/selected/)
  }
  await expect(page.locator('.react-flow__edge')).toHaveCount(0)
  expect(consoleProblems).toEqual([])
  expect(failedResponses).toEqual([])
})

test('edits a node label and saves (load -> edit -> save round-trip)', async ({ page }) => {
  await page.getByText('Receive Device').click()
  const label = page.getByLabel('Label', { exact: true })
  await expect(label).toHaveValue('Receive Device')
  await label.fill('Receive the Device')
  await expect(page.locator('.react-flow__node').filter({ hasText: 'Receive the Device' })).toBeVisible()

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()

  await page.getByRole('button', { name: 'Preview' }).click()
  await page.getByRole('menuitem', { name: 'JSON' }).click()
  await expect(page.getByText(/no changes since last save/i)).toBeVisible()
  await page.keyboard.press('Escape')

  await page.getByRole('button', { name: 'Undo' }).click()
  await expect(page.getByText('Unsaved changes', { exact: true })).toBeVisible()
})

test('adopts the normalized custom type returned by save', async ({ page }) => {
  await page.getByLabel('Palette scope').selectOption('all')
  const paletteBlock = page.getByTitle('gpNode · block')
  const pane = page.locator('.react-flow__pane')
  await paletteBlock.dragTo(pane, { targetPosition: { x: 300, y: 300 } })
  await expect(page.locator('.react-flow__node')).toHaveCount(11)
  const block = page.locator('.react-flow__node').filter({ hasText: 'Block' }).last()
  await expect(block).toHaveCSS('height', '48px')

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  await expect(page.getByText('custom', { exact: true })).toBeVisible()
})

test('toggles dark mode', async ({ page }) => {
  await expect(page.locator('html')).not.toHaveClass(/dark/)
  await page.getByRole('button', { name: 'Toggle light/dark theme' }).click()
  await expect(page.locator('html')).toHaveClass(/dark/)
})

test('undo reverts a label change', async ({ page }) => {
  await page.getByText('Receive Device').click()
  await page.getByLabel('Label', { exact: true }).fill('Temporary')
  await expect(page.locator('.react-flow__node').filter({ hasText: 'Temporary' })).toBeVisible()

  await page.getByRole('button', { name: 'Undo' }).click()
  await expect(page.locator('.react-flow__node').filter({ hasText: 'Receive Device' })).toBeVisible()
})

test('searches the New Diagram chooser and starts a typed blank with the keyboard', async ({ page }) => {
  await page.goto('/editor')
  const opener = page.getByRole('button', { name: 'New diagram…' })
  await expect(opener).toBeVisible()
  await expect(page.getByRole('button', { name: 'Create Activity diagram' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Browse' })).toHaveCount(0)

  await opener.press('Enter')
  const search = page.getByLabel('Search diagram types')
  await expect(search).toBeFocused()
  await expect(page.getByLabel('Diagram types').getByRole('button')).toHaveCount(4)
  await search.fill('sysml')
  await expect(page.getByRole('button', { name: 'Create BDD diagram' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Create Activity diagram' })).toHaveCount(0)
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog', { name: 'New diagram' })).toHaveCount(0)
  await expect(opener).toBeFocused()

  await opener.press('Enter')
  await search.fill('workflow')
  await page.getByRole('button', { name: 'Create Activity diagram' }).press('Enter')
  await expect(page.getByLabel('Diagram name')).toHaveValue('Untitled Activity Diagram')
  await expect(page.locator('.react-flow__node')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Save As', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Diagram information' }).click()
  await expect(page.getByRole('dialog', { name: 'Diagram information' })).toContainText('Unsaved — Save As required')
})

test('returns home and clears reopenable recents', async ({ page }) => {
  await page.getByRole('button', { name: 'Home' }).click()
  await expect(page.getByText('smoke.gp.json')).toBeVisible()
  await page.getByRole('button', { name: 'Clear recents' }).click()
  await expect(page.getByText('smoke.gp.json')).toHaveCount(0)
})

test('treats a plain dropped file as a read-only local source', async ({ page }) => {
  const text = readFileSync(seedDiagram(), 'utf8')
  await page.locator('.react-flow__pane').evaluate((pane, contents) => {
    const browser = globalThis as unknown as {
      DataTransfer: new () => { items: { add: (file: object) => void } }
      File: new (bits: string[], name: string, options: { type: string }) => object
      DragEvent: new (type: string, init: Record<string, unknown>) => never
    }
    const dataTransfer = new browser.DataTransfer()
    dataTransfer.items.add(new browser.File([contents], 'dropped.gp.json', { type: 'application/json' }))
    pane.dispatchEvent(new browser.DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer }))
  }, text)

  await page.getByRole('button', { name: 'Diagram information' }).click()
  await expect(page.getByRole('dialog', { name: 'Diagram information' })).toContainText('Read-only — Save As required')
  await expect(page.getByRole('button', { name: 'Browse' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Save As', exact: true })).toBeEnabled()
})

test('keeps a picker-opened file session-owned without changing the URL', async ({ page }) => {
  const path = seedDiagram()
  const text = readFileSync(path, 'utf8')
  await page.addInitScript(({ contents }) => {
    const file = new File([contents], 'smoke.gp.json', { type: 'application/json' })
    Object.defineProperty(globalThis, 'showOpenFilePicker', {
      configurable: true,
      value: async () => [{ name: file.name, getFile: async () => file, createWritable: async () => ({ write: async () => {}, close: async () => {} }) }],
    })
    Object.defineProperty(globalThis, 'showSaveFilePicker', { configurable: true, value: async () => null })
  }, { contents: text })
  await page.reload()

  await page.getByRole('button', { name: 'Open file…' }).click()
  await page.getByRole('button', { name: 'Diagram information' }).click()
  await expect(page.getByRole('dialog', { name: 'Diagram information' })).toContainText('Writable for this browser session')
  await expect(page.getByRole('button', { name: 'Browse' })).toHaveCount(0)
  expect(new URL(page.url()).searchParams.get('diagramPath')).toBeNull()
})

test('reloads a clean workspace session when its file changes on disk', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as { nodes: Array<{ data: { label: string } }> }
  diagram.nodes[1].data.label = 'Receive Updated Device'
  writeFileSync(path, JSON.stringify(diagram, null, 2))

  await page.evaluate(() => {
    const browser = globalThis as unknown as { dispatchEvent: (event: Event) => boolean }
    browser.dispatchEvent(new Event('focus'))
  })
  await expect(page.getByText('Receive Updated Device')).toBeVisible()
})

test('blocks a stale workspace overwrite and offers conflict review', async ({ page }) => {
  const path = seedDiagram()
  await page.getByText('Receive Device').click()
  await page.getByLabel('Label', { exact: true }).fill('Browser Edit')
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as { nodes: Array<{ data: { label: string } }> }
  diagram.nodes[1].data.label = 'Disk Edit'
  writeFileSync(path, JSON.stringify(diagram, null, 2))

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText('The source diagram changed on disk while this canvas has unsaved edits.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Review changes' })).toBeVisible()
  expect(readFileSync(path, 'utf8')).toContain('Disk Edit')
})

test('ignores a late save completion after another file opens', async ({ page }) => {
  const bddText = readFileSync(seedBddDiagram(), 'utf8')
  let releaseSave: (() => void) | undefined
  const saveGate = new Promise<void>((resolve) => {
    releaseSave = resolve
  })
  await page.route('**/api/diagrams/save', async (route) => {
    await saveGate
    await route.continue()
  })
  await page.getByText('Receive Device').click()
  await page.getByLabel('Label', { exact: true }).fill('Saving old session')
  const saveRequest = page.waitForRequest((request) => request.url().endsWith('/api/diagrams/save'))
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await saveRequest

  await page.locator('.react-flow__pane').evaluate((pane, contents) => {
    const browser = globalThis as unknown as {
      DataTransfer: new () => { items: { add: (file: object) => void } }
      File: new (bits: string[], name: string, options: { type: string }) => object
      DragEvent: new (type: string, init: Record<string, unknown>) => never
    }
    const dataTransfer = new browser.DataTransfer()
    dataTransfer.items.add(new browser.File([contents], 'spacecraft.gp.json', { type: 'application/json' }))
    pane.dispatchEvent(new browser.DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer }))
  }, bddText)
  await page.getByRole('button', { name: 'Discard & open' }).click()
  await expect(page.getByText('Spacecraft', { exact: true })).toBeVisible()
  const saveResponse = page.waitForResponse((response) => response.url().endsWith('/api/diagrams/save'))
  releaseSave?.()
  await saveResponse
  await expect(page.getByText('Spacecraft', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Diagram information' }).click()
  await expect(page.getByRole('dialog', { name: 'Diagram information' })).toContainText('Read-only')
  expect(new URL(page.url()).searchParams.get('diagramPath')).toBeNull()
})

test('connects and persists exact positions anywhere on node boundaries', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    diagramType: string
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.diagramType = 'custom'
  diagram.nodes = [
    { id: 'source-use-case', type: 'gpNode', position: { x: 120, y: 120 }, width: 200, height: 70, data: { label: 'Source Use Case', semanticType: 'useCase' } },
    { id: 'target-action', type: 'gpNode', position: { x: 140, y: 400 }, width: 160, height: 60, data: { label: 'Target Action', semanticType: 'opaqueAction' } },
  ]
  diagram.edges = []
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  const edges = page.locator('.react-flow__edge')
  await expect(edges).toHaveCount(0)

  const initialNode = page.locator('.react-flow__node[data-id="source-use-case"]')
  const endNode = page.locator('.react-flow__node[data-id="target-action"]')
  const startBox = await initialNode.boundingBox()
  const endBox = await endNode.boundingBox()
  const source = await initialNode.getAttribute('data-id')
  const target = await endNode.getAttribute('data-id')
  if (!startBox || !endBox || !source || !target) throw new Error('expected node boundary data')

  const sample = initialNode.locator('.react-flow__handle.source[aria-label*="bottom curved boundary"]').first()
  const sampleBox = await sample.boundingBox()
  if (!sampleBox) throw new Error('expected non-cardinal source handle')
  const sourcePoint = { x: sampleBox.x + sampleBox.width / 2, y: sampleBox.y + sampleBox.height / 2 }
  await page.mouse.move(1, 1)
  await page.mouse.move(sourcePoint.x, sourcePoint.y, { steps: 4 })
  const indicator = initialNode.getByTestId('boundary-indicator')
  await expect(indicator).toBeVisible()
  const expected = await initialNode.evaluate((node) => {
    const width = Number(Reflect.get(node, 'offsetWidth'))
    const height = Number(Reflect.get(node, 'offsetHeight'))
    const match = (node.getAttribute('style') ?? '').match(/translate\(([-\d.]+)px, ([-\d.]+)px\)/)
    const marker = node.querySelector('[data-testid="boundary-indicator"]')
    const markerStyle = marker?.getAttribute('style') ?? ''
    const left = Number.parseFloat(markerStyle.match(/left: ([-\d.]+)px/)?.[1] ?? '')
    const top = Number.parseFloat(markerStyle.match(/top: ([-\d.]+)px/)?.[1] ?? '')
    return {
      localX: left,
      localY: top,
      flowX: Number(match?.[1] ?? 0) + left,
      flowY: Number(match?.[2] ?? 0) + top,
      width,
      height,
    }
  })
  expect(((expected.localX - expected.width / 2) / (expected.width / 2)) ** 2 + ((expected.localY - expected.height / 2) / (expected.height / 2)) ** 2).toBeCloseTo(1, 5)
  const indicatorBox = await indicator.boundingBox()
  if (!indicatorBox) throw new Error('expected boundary indicator bounds')
  expect(indicatorBox.x + indicatorBox.width / 2).toBeCloseTo(startBox.x + startBox.width * expected.localX / expected.width, 0)
  expect(indicatorBox.y + indicatorBox.height / 2).toBeCloseTo(startBox.y + startBox.height * expected.localY / expected.height, 0)

  const activeSource = initialNode.locator('.react-flow__handle.source:hover')
  await expect.poll(() => activeSource.count()).toBeGreaterThan(0)
  const targetHandle = endNode.getByLabel('Finish relationship on top boundary')
  const targetHandleBox = await targetHandle.boundingBox()
  if (!targetHandleBox) throw new Error('expected target handle bounds')
  await page.mouse.down()
  await page.mouse.move(targetHandleBox.x + targetHandleBox.width / 2, targetHandleBox.y + targetHandleBox.height / 2, { steps: 2 })
  const preview = await page.locator('.react-flow__connection-path').getAttribute('d')
  const previewStart = preview?.match(/^M\s*([\d.-]+)[, ]+([\d.-]+)/)
  expect(Number(previewStart?.[1])).toBeCloseTo(expected.flowX, 0)
  expect(Number(previewStart?.[2])).toBeCloseTo(expected.flowY, 0)
  await expect(endNode.locator('.react-flow__handle.connectingto.valid')).toHaveCount(1)
  await page.mouse.up()
  await expect(edges).toHaveCount(1)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ source: string; target: string; sourceHandle?: string; targetHandle?: string; route?: { sourceAnchor?: { side: string; offset: number }; targetAnchor?: { side: string; offset: number } } }>
  }
  const created = saved.edges.find((edge) => edge.source === source && edge.target === target)
  const rayScale = (expected.height / 2) / (expected.localY - expected.height / 2)
  const expectedOffset = (expected.width / 2 + (expected.localX - expected.width / 2) * rayScale) / expected.width
  expect(created?.route?.sourceAnchor?.side).toBe('bottom')
  expect(created?.route?.sourceAnchor?.offset).toBeCloseTo(expectedOffset, 2)
  expect(created?.route?.targetAnchor?.side).toBe('top')
  expect(created?.route?.targetAnchor?.offset).toBeCloseTo(0.5, 1)
  expect(created?.sourceHandle).toBeUndefined()
  expect(created?.targetHandle).toBeUndefined()
})

test('connects from and to every sloped edge of a diamond node', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.nodes = [
    { id: 'merge', type: 'gpNode', position: { x: 300, y: 220 }, width: 140, height: 80, data: { label: 'Merge Hit Area', semanticType: 'mergeNode' } },
    { id: 'upper-left', type: 'gpNode', position: { x: 60, y: 20 }, width: 160, height: 60, data: { label: 'Upper Left', semanticType: 'opaqueAction' } },
    { id: 'upper-right', type: 'gpNode', position: { x: 500, y: 20 }, width: 160, height: 60, data: { label: 'Upper Right', semanticType: 'opaqueAction' } },
    { id: 'lower-right', type: 'gpNode', position: { x: 500, y: 380 }, width: 160, height: 60, data: { label: 'Lower Right', semanticType: 'opaqueAction' } },
    { id: 'lower-left', type: 'gpNode', position: { x: 60, y: 380 }, width: 160, height: 60, data: { label: 'Lower Left', semanticType: 'opaqueAction' } },
  ]
  diagram.edges = []
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByRole('button', { name: 'Fit View' }).click()
  const viewport = page.viewportSize()
  await expect.poll(async () => {
    const box = await page.locator('.react-flow__node').filter({ hasText: 'Lower Right' }).boundingBox()
    return Boolean(box && viewport && box.y + box.height <= viewport.height)
  }).toBe(true)

  const merge = page.locator('.react-flow__node').filter({ hasText: 'Merge Hit Area' })
  const mergeBox = await merge.boundingBox()
  if (!mergeBox) throw new Error('expected Merge bounds')
  const starts = [[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75]]
  const targets = ['Upper Left', 'Upper Right', 'Lower Right', 'Lower Left']
  const targetSides = ['right', 'left', 'left', 'right']
  const edges = page.locator('.react-flow__edge')
  for (let index = 0; index < starts.length; index += 1) {
    const [x, y] = starts[index]
    const start = { x: mergeBox.x + mergeBox.width * x, y: mergeBox.y + mergeBox.height * y }
    await page.mouse.move(start.x, start.y)
    await expect(merge.getByTestId('boundary-indicator')).toBeVisible()
    const target = page.locator('.react-flow__node').filter({ hasText: targets[index] })
    const targetBox = await target.boundingBox()
    if (!targetBox) throw new Error(`expected ${targets[index]} bounds`)
    const endX = targetSides[index] === 'left' ? targetBox.x : targetBox.x + targetBox.width
    await page.mouse.down()
    await page.mouse.move(endX, targetBox.y + targetBox.height / 2, { steps: 16 })
    await page.mouse.up()
    await expect(edges, `source ${targets[index]}`).toHaveCount(index + 1)
  }
  await expect(edges).toHaveCount(4)
  const targetPoints = [[0.35, 0.15], [0.65, 0.15], [0.65, 0.85], [0.35, 0.85]]
  for (let index = 0; index < targetPoints.length; index += 1) {
    const source = page.locator('.react-flow__node').filter({ hasText: targets[index] })
    const sourceBox = await source.boundingBox()
    if (!sourceBox) throw new Error(`expected ${targets[index]} bounds`)
    const startX = targetSides[index] === 'left' ? sourceBox.x : sourceBox.x + sourceBox.width
    const [x, y] = targetPoints[index]
    const end = { x: mergeBox.x + mergeBox.width * x, y: mergeBox.y + mergeBox.height * y }
    await page.mouse.move(startX, sourceBox.y + sourceBox.height / 2)
    await page.mouse.down()
    await page.mouse.move(end.x, end.y, { steps: 16 })
    await page.mouse.up()
    await expect(edges, `target ${targets[index]}`).toHaveCount(starts.length + index + 1)
  }
  await expect(edges).toHaveCount(8)
  await page.mouse.move(mergeBox.x + mergeBox.width / 2, mergeBox.y + mergeBox.height / 2)
  await expect(merge.getByTestId('boundary-indicator')).not.toBeVisible()
})

test('connects from every diamond cardinal vertex without moving the node', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    diagramType: string
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.diagramType = 'custom'
  diagram.nodes = [
    { id: 'decision-cardinal', type: 'gpNode', position: { x: 280, y: 240 }, width: 140, height: 80, data: { label: 'Decision Cardinal', semanticType: 'decisionNode' } },
    { id: 'merge-cardinal', type: 'gpNode', position: { x: 450, y: 240 }, width: 140, height: 80, data: { label: 'Merge Cardinal', semanticType: 'mergeNode' } },
    { id: 'target-top', type: 'gpNode', position: { x: 440, y: 80 }, width: 160, height: 60, data: { label: 'Target Top', semanticType: 'opaqueAction' } },
    { id: 'target-right', type: 'gpNode', position: { x: 650, y: 250 }, width: 160, height: 60, data: { label: 'Target Right', semanticType: 'opaqueAction' } },
    { id: 'target-bottom', type: 'gpNode', position: { x: 440, y: 410 }, width: 160, height: 60, data: { label: 'Target Bottom', semanticType: 'opaqueAction' } },
    { id: 'target-left', type: 'gpNode', position: { x: 80, y: 250 }, width: 160, height: 60, data: { label: 'Target Left', semanticType: 'opaqueAction' } },
  ]
  diagram.edges = []
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByRole('button', { name: 'Fit View' }).click()

  const decision = page.locator('.react-flow__node[data-id="decision-cardinal"]')
  const merge = page.locator('.react-flow__node[data-id="merge-cardinal"]')
  for (const zoom of [50, 100, 200]) {
    await setZoomPercent(page, zoom)
    for (const diamond of [decision, merge]) {
      const box = await diamond.boundingBox()
      if (!box) throw new Error(`expected diamond bounds at ${zoom}%`)
      const vertices = [
        { x: box.x + box.width / 2, y: box.y },
        { x: box.x + box.width, y: box.y + box.height / 2 },
        { x: box.x + box.width / 2, y: box.y + box.height },
        { x: box.x, y: box.y + box.height / 2 },
      ]
      for (const vertex of vertices) {
        await page.mouse.move(vertex.x, vertex.y)
        await expect(diamond.getByTestId('boundary-indicator')).toBeVisible()
        await expect(diamond.locator('.react-flow__handle.source:hover')).toHaveCount(1)
      }
    }
  }

  await page.getByRole('button', { name: 'Fit View' }).click()
  await setZoomPercent(page, 100)
  const mergeBox = await merge.boundingBox()
  if (!mergeBox) throw new Error('expected merge bounds')
  const connections = [
    { side: 'top', start: { x: mergeBox.x + mergeBox.width / 2, y: mergeBox.y }, target: 'target-top', end: 'bottom' },
    { side: 'right', start: { x: mergeBox.x + mergeBox.width, y: mergeBox.y + mergeBox.height / 2 }, target: 'target-right', end: 'left' },
    { side: 'bottom', start: { x: mergeBox.x + mergeBox.width / 2, y: mergeBox.y + mergeBox.height }, target: 'target-bottom', end: 'top' },
    { side: 'left', start: { x: mergeBox.x, y: mergeBox.y + mergeBox.height / 2 }, target: 'target-left', end: 'right' },
  ] as const
  const edges = page.locator('.react-flow__edge')
  for (let index = 0; index < connections.length; index += 1) {
    const connection = connections[index]
    const target = page.locator(`.react-flow__node[data-id="${connection.target}"]`)
    const targetBox = await target.boundingBox()
    if (!targetBox) throw new Error(`expected ${connection.target} bounds`)
    const end = connection.end === 'top'
      ? { x: targetBox.x + targetBox.width / 2, y: targetBox.y }
      : connection.end === 'right'
        ? { x: targetBox.x + targetBox.width, y: targetBox.y + targetBox.height / 2 }
        : connection.end === 'bottom'
          ? { x: targetBox.x + targetBox.width / 2, y: targetBox.y + targetBox.height }
          : { x: targetBox.x, y: targetBox.y + targetBox.height / 2 }
    await page.mouse.move(connection.start.x, connection.start.y)
    await page.mouse.down()
    await page.mouse.move(end.x, end.y, { steps: 16 })
    await page.mouse.up()
    await expect(edges).toHaveCount(index + 1)
  }

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    nodes: Array<{ id: string; position: { x: number; y: number } }>
    edges: Array<{ route?: { sourceAnchor?: { side: string; offset: number } } }>
  }
  expect(saved.nodes.find((node) => node.id === 'decision-cardinal')?.position).toEqual({ x: 280, y: 240 })
  expect(saved.nodes.find((node) => node.id === 'merge-cardinal')?.position).toEqual({ x: 450, y: 240 })
  expect(saved.edges.map((edge) => edge.route?.sourceAnchor?.side)).toEqual(connections.map((connection) => connection.side))
  for (const edge of saved.edges) expect(edge.route?.sourceAnchor?.offset).toBeCloseTo(0.5, 4)
  await page.reload()
  await expect(page.locator('.react-flow__edge')).toHaveCount(4)
})

test('connects on visible control, use-case, and actor profiles with save and render parity', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    diagramType: string
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.diagramType = 'custom'
  const curved = [
    ['initial', 'Initial', 'initialNode', 90, 60, 'control'],
    ['final', 'Final', 'activityFinalNode', 90, 60, 'control'],
    ['flow-final', 'Flow Final', 'flowFinalNode', 90, 60, 'control'],
    ['use-case', 'Use Case', 'useCase', 200, 70, 'ellipse'],
    ['actor', 'Actor', 'actor', 90, 120, 'actor'],
  ] as const
  diagram.nodes = curved.flatMap(([id, label, semanticType, width, height], index) => [
    { id, type: 'gpNode', position: { x: index * 220, y: 100 }, width, height, data: { label, semanticType } },
    { id: `target-${id}`, type: 'gpNode', position: { x: index * 220, y: 400 }, width: 140, height: 60, data: { label: `Target ${label}`, semanticType: 'opaqueAction' } },
  ])
  diagram.edges = []
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByRole('button', { name: 'Fit View' }).click()
  const viewport = page.viewportSize()
  await expect.poll(async () => {
    const box = await page.locator('.react-flow__node').filter({ hasText: 'Target Actor' }).boundingBox()
    return Boolean(box && viewport && box.y + box.height <= viewport.height)
  }).toBe(true)

  const edges = page.locator('.react-flow__edge')
  for (let index = 0; index < curved.length; index += 1) {
    const [id, label, , , , profile] = curved[index]
    const node = page.locator(`.react-flow__node[data-id="${id}"]`)
    const target = page.locator(`.react-flow__node[data-id="target-${id}"]`)
    const nodeBox = await node.boundingBox()
    const targetBox = await target.boundingBox()
    if (!nodeBox || !targetBox) throw new Error(`expected ${label} bounds`)
    await page.mouse.move(nodeBox.x + nodeBox.width / 2, nodeBox.y + nodeBox.height / 2)
    await expect(node.locator('.react-flow__handle:hover')).toHaveCount(0)
    const glyphBox = profile === 'ellipse' ? nodeBox : await node.locator('svg').first().boundingBox()
    if (!glyphBox) throw new Error(`expected ${label} glyph bounds`)
    const boundary = profile === 'control'
      ? { x: glyphBox.x + glyphBox.width / 2, y: glyphBox.y + glyphBox.height * 32 / 34 }
      : profile === 'actor'
        ? { x: glyphBox.x + glyphBox.width / 2, y: glyphBox.y + glyphBox.height * 44 / 46 }
        : { x: glyphBox.x + glyphBox.width / 2, y: glyphBox.y + glyphBox.height }
    const start = profile === 'control'
      ? { x: boundary.x, y: glyphBox.y + glyphBox.height * 29 / 34 }
      : profile === 'actor'
        ? { x: boundary.x, y: glyphBox.y + glyphBox.height * 41 / 46 }
        : { x: boundary.x, y: boundary.y - 3 }
    await page.mouse.move(1, 1)
    await page.mouse.move(start.x, start.y, { steps: 4 })
    const activeHandle = node.locator('.react-flow__handle.source:hover')
    await expect(activeHandle).toHaveCount(1)
    await activeHandle.dispatchEvent('pointermove', { clientX: start.x, clientY: start.y })
    const indicator = node.getByTestId('boundary-indicator')
    await expect(indicator).toBeVisible()
    const indicatorBox = await indicator.boundingBox()
    if (!indicatorBox) throw new Error(`expected ${label} indicator bounds`)
    expect(indicatorBox.x + indicatorBox.width / 2).toBeCloseTo(boundary.x, 0)
    expect(indicatorBox.y + indicatorBox.height / 2).toBeCloseTo(boundary.y, 0)
    await page.mouse.down()
    await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y, { steps: 16 })
    await page.mouse.up()
    await expect(edges).toHaveCount(index + 1)
  }

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as { edges: Array<{ route?: { sourceAnchor?: { side: string; offset: number } } }> }
  expect(saved.edges).toHaveLength(curved.length)
  for (const edge of saved.edges) {
    expect(edge.route?.sourceAnchor?.side).toBe('bottom')
    expect(Math.abs((edge.route?.sourceAnchor?.offset ?? 0) - 0.5)).toBeLessThan(0.06)
  }

  await page.reload()
  await expect(page.locator('.react-flow__edge')).toHaveCount(curved.length)
  await page.getByRole('button', { name: 'Preview' }).click()
  await page.getByRole('menuitem', { name: 'Render (SVG)' }).click()
  await expect(page.getByRole('heading', { name: 'Backend render preview' })).toBeVisible()
})

test('keeps the control attachment halo stable at common zoom levels', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    diagramType: string
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.diagramType = 'custom'
  diagram.nodes = [
    { id: 'zoom-initial', type: 'gpNode', position: { x: 300, y: 220 }, width: 90, height: 60, data: { label: 'Zoom Initial', semanticType: 'initialNode' } },
  ]
  diagram.edges = []
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  const node = page.locator('.react-flow__node[data-id="zoom-initial"]')
  await expect(node).toBeVisible()

  for (const zoom of [150, 100, 76, 50]) {
    await setZoomPercent(page, zoom)
    await expect(page.getByTitle('Zoom level')).toHaveText(`${zoom}%`)
    const glyph = await node.locator('svg').first().boundingBox()
    if (!glyph) throw new Error('expected control glyph bounds')
    const boundary = { x: glyph.x + glyph.width / 2, y: glyph.y + glyph.height * 2 / 34 }
    const pointer = { x: boundary.x, y: boundary.y - 10 }
    await page.mouse.move(1, 1)
    await page.mouse.move(pointer.x, pointer.y, { steps: 4 })
    const activeHandles = node.locator('.react-flow__handle.source:hover')
    await expect.poll(() => activeHandles.count()).toBeGreaterThan(0)
    await activeHandles.first().dispatchEvent('pointermove', { clientX: pointer.x, clientY: pointer.y })
    const indicator = node.getByTestId('boundary-indicator')
    await expect(indicator).toBeVisible()
    const indicatorBox = await indicator.boundingBox()
    if (!indicatorBox) throw new Error('expected control boundary indicator')
    expect(indicatorBox.x + indicatorBox.width / 2).toBeCloseTo(boundary.x, 0)
    expect(indicatorBox.y + indicatorBox.height / 2).toBeCloseTo(boundary.y, 0)
  }
})

test('guides valid targets and softly snaps cardinal attachment without losing custom anchors', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    diagramType: string
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.diagramType = 'custom'
  diagram.nodes = [
    { id: 'guide-source', type: 'gpNode', position: { x: 120, y: 220 }, width: 160, height: 60, data: { label: 'Guide Source', semanticType: 'opaqueAction' } },
    { id: 'guide-target', type: 'gpNode', position: { x: 460, y: 200 }, width: 200, height: 100, data: { label: 'Guide Target', semanticType: 'useCase' } },
  ]
  diagram.edges = [{
    id: 'existing-custom',
    source: 'guide-source',
    target: 'guide-target',
    type: 'default',
    data: { semanticType: 'association' },
    route: { sourceAnchor: { side: 'right', offset: 0.5 }, targetAnchor: { side: 'top', offset: 0.7 } },
  }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await setZoomPercent(page, 100)
  const source = page.locator('.react-flow__node[data-id="guide-source"]')
  const target = page.locator('.react-flow__node[data-id="guide-target"]')
  const edges = page.locator('.react-flow__edge')
  await expect(edges).toHaveCount(1)

  let targetBox = await target.boundingBox()
  if (!targetBox) throw new Error('expected guide target bounds')
  const topCardinal = target.locator('.react-flow__handle.source[data-attachment-side="top"][data-attachment-cardinal="true"]')
  const topCardinalBox = await topCardinal.boundingBox()
  if (!topCardinalBox) throw new Error('expected top cardinal handle')
  const cardinalPointer = { x: topCardinalBox.x + topCardinalBox.width / 2 + 6, y: topCardinalBox.y + topCardinalBox.height / 2 }
  await page.mouse.move(1, 1)
  await page.mouse.move(cardinalPointer.x, cardinalPointer.y, { steps: 4 })
  const cardinalHandle = target.locator('.react-flow__handle.source:hover')
  await expect.poll(() => cardinalHandle.count()).toBeGreaterThan(0)
  await cardinalHandle.first().dispatchEvent('pointermove', { clientX: cardinalPointer.x, clientY: cardinalPointer.y })
  await expect(target.getByTestId('boundary-indicator')).toHaveAttribute('data-anchor-kind', 'cardinal')

  let sourceBox = await source.boundingBox()
  if (!sourceBox) throw new Error('expected guide source bounds')
  await page.mouse.move(sourceBox.x + sourceBox.width - 2, sourceBox.y + sourceBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(sourceBox.x + sourceBox.width / 2, sourceBox.y + 2, { steps: 8 })
  await expect(source.locator('.react-flow__handle.connectingto.valid')).toHaveCount(0)
  await expect(source).toHaveCSS('outline-style', 'none')
  await page.mouse.up()
  await expect(edges).toHaveCount(1)

  sourceBox = await source.boundingBox()
  targetBox = await target.boundingBox()
  if (!sourceBox || !targetBox) throw new Error('expected connection guidance bounds')
  await page.mouse.move(sourceBox.x + sourceBox.width - 2, sourceBox.y + sourceBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(targetBox.x + targetBox.width / 2 + 6, targetBox.y - 19, { steps: 12 })
  const validTarget = target.locator('.react-flow__handle.connectingto.valid')
  await expect(validTarget).toHaveCount(1)
  await expect(validTarget).toHaveCSS('opacity', '1')
  await expect(target).toHaveCSS('outline-style', 'solid')
  await expect(source).toHaveCSS('outline-style', 'none')
  const preview = await page.locator('.react-flow__connection-path').getAttribute('d')
  const previewStart = preview?.match(/^M\s*([\d.-]+)[, ]+([\d.-]+)/)
  expect(Number(previewStart?.[1])).toBeCloseTo(280, 2)
  expect(Number(previewStart?.[2])).toBeCloseTo(250, 2)
  await page.mouse.up()
  await expect(edges).toHaveCount(2)

  await setZoomPercent(page, 76)
  sourceBox = await source.boundingBox()
  if (!sourceBox) throw new Error('expected guide source bounds')
  const customHandle = target.locator('.react-flow__handle.target[data-attachment-side="top"][data-attachment-cardinal="false"]').first()
  const customHandleBox = await customHandle.boundingBox()
  if (!customHandleBox) throw new Error('expected custom target handle')
  await page.mouse.move(sourceBox.x + sourceBox.width - 2, sourceBox.y + sourceBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(customHandleBox.x + customHandleBox.width / 2, customHandleBox.y + customHandleBox.height / 2, { steps: 12 })
  await expect(target.locator('.react-flow__handle.connectingto.valid')).toHaveCount(1)
  await page.mouse.up()
  await expect(edges).toHaveCount(3)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ id: string; source: string; target: string; route?: { targetAnchor?: { side: string; offset: number } } }>
  }
  expect(saved.edges.find((edge) => edge.id === 'existing-custom')?.route?.targetAnchor).toEqual({ side: 'top', offset: 0.7 })
  const created = saved.edges.filter((edge) => edge.id !== 'existing-custom' && edge.source === 'guide-source' && edge.target === 'guide-target')
  expect(created).toHaveLength(2)
  expect(created.some((edge) => edge.route?.targetAnchor?.side === 'top' && Math.abs((edge.route.targetAnchor.offset ?? 0) - 0.5) < 0.001)).toBe(true)
  expect(created.some((edge) => edge.route?.targetAnchor?.side === 'top' && Math.abs((edge.route.targetAnchor.offset ?? 0) - 0.5) > 0.03)).toBe(true)
  await page.reload()
  await expect(page.locator('.react-flow__edge')).toHaveCount(3)
})

test('keeps added containers behind content without changing explicit containment', async ({ page }) => {
  const path = seedUseCaseDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    diagramType: string
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.diagramType = 'use_case_diagram'
  diagram.nodes = [
    { id: 'layer-actor', type: 'gpNode', position: { x: 300, y: 230 }, width: 90, height: 120, data: { label: 'Layer Actor', semanticType: 'actor' } },
    { id: 'layer-use-case', type: 'gpNode', position: { x: 430, y: 250 }, width: 200, height: 70, data: { label: 'Layer Use Case', semanticType: 'useCase' } },
  ]
  diagram.edges = [{ id: 'layer-edge', source: 'layer-actor', target: 'layer-use-case', data: { semanticType: 'association' } }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await setZoomPercent(page, 100)
  const actor = page.locator('.react-flow__node[data-id="layer-actor"]')
  const useCase = page.locator('.react-flow__node[data-id="layer-use-case"]')
  let actorBox = await actor.boundingBox()
  const useCaseBox = await useCase.boundingBox()
  const pane = page.locator('.react-flow__pane')
  const paneBox = await pane.boundingBox()
  if (!actorBox || !useCaseBox || !paneBox) throw new Error('expected layering setup bounds')
  const midpoint = {
    x: (actorBox.x + actorBox.width / 2 + useCaseBox.x + useCaseBox.width / 2) / 2,
    y: (actorBox.y + actorBox.height / 2 + useCaseBox.y + useCaseBox.height / 2) / 2,
  }
  await page.getByRole('button', { name: 'Add System Boundary' }).dragTo(pane, {
    targetPosition: { x: midpoint.x - paneBox.x, y: midpoint.y - paneBox.y },
  })
  await expect(page.locator('.react-flow__node')).toHaveCount(3)
  const boundary = page.locator('.react-flow__node').filter({ hasText: 'System Boundary' })
  const boundaryId = await boundary.getAttribute('data-id')
  if (!boundaryId) throw new Error('expected boundary id')
  await expect(boundary).toHaveCSS('z-index', '0')
  await expect(page.locator('.react-flow__edge').first().locator('xpath=..')).toHaveCSS('z-index', '1')
  await expect(actor).toHaveCSS('z-index', '2')
  await expect(useCase).toHaveCSS('z-index', '2')

  let boundaryBox = await boundary.boundingBox()
  actorBox = await actor.boundingBox()
  if (!boundaryBox || !actorBox) throw new Error('expected layered node bounds')
  const boundaryBeforeActorDrag = { x: boundaryBox.x, y: boundaryBox.y }
  await page.mouse.move(actorBox.x + actorBox.width / 2, actorBox.y + actorBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(actorBox.x + actorBox.width / 2 + 30, actorBox.y + actorBox.height / 2 + 20, { steps: 6 })
  await page.mouse.up()
  await expect(actor).toHaveClass(/selected/)
  await expect(actor).toHaveCSS('z-index', '3')
  const movedActorBox = await actor.boundingBox()
  boundaryBox = await boundary.boundingBox()
  if (!movedActorBox || !boundaryBox) throw new Error('expected moved actor bounds')
  expect(movedActorBox.x).toBeGreaterThan(actorBox.x + 20)
  expect(boundaryBox.x).toBeCloseTo(boundaryBeforeActorDrag.x, 0)
  expect(boundaryBox.y).toBeCloseTo(boundaryBeforeActorDrag.y, 0)

  const boundaryDragStart = { x: boundaryBox.x + 12, y: boundaryBox.y + boundaryBox.height - 12 }
  await page.mouse.move(boundaryDragStart.x, boundaryDragStart.y)
  await page.mouse.down()
  await page.mouse.move(boundaryDragStart.x + 20, boundaryDragStart.y + 16, { steps: 6 })
  await page.mouse.up()
  await expect(boundary).toHaveClass(/selected/)
  await expect(boundary).toHaveCSS('z-index', '0')
  const movedBoundaryBox = await boundary.boundingBox()
  if (!movedBoundaryBox) throw new Error('expected moved boundary bounds')
  expect(movedBoundaryBox.x).toBeGreaterThan(boundaryBeforeActorDrag.x + 10)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
  let saved = JSON.parse(readFileSync(path, 'utf8')) as { nodes: Array<{ id: string; parentId?: string }> }
  expect(saved.nodes.find((node) => node.id === 'layer-actor')?.parentId).toBeUndefined()
  expect(saved.nodes.find((node) => node.id === 'layer-use-case')?.parentId).toBeUndefined()

  let currentUseCaseBox = await useCase.boundingBox()
  if (!currentUseCaseBox) throw new Error('expected use-case bounds')
  await page.mouse.move(currentUseCaseBox.x + currentUseCaseBox.width / 2, currentUseCaseBox.y + currentUseCaseBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(currentUseCaseBox.x + currentUseCaseBox.width / 2 + 10, currentUseCaseBox.y + currentUseCaseBox.height / 2 + 8, { steps: 4 })
  await page.mouse.up()
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
  saved = JSON.parse(readFileSync(path, 'utf8')) as typeof saved
  expect(saved.nodes.find((node) => node.id === 'layer-use-case')?.parentId).toBe(boundaryId)

  currentUseCaseBox = await useCase.boundingBox()
  boundaryBox = await boundary.boundingBox()
  if (!currentUseCaseBox || !boundaryBox) throw new Error('expected contained node bounds')
  await page.mouse.move(currentUseCaseBox.x + currentUseCaseBox.width / 2, currentUseCaseBox.y + currentUseCaseBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(boundaryBox.x + boundaryBox.width + 180, boundaryBox.y + boundaryBox.height / 2, { steps: 8 })
  await page.mouse.up()
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
  saved = JSON.parse(readFileSync(path, 'utf8')) as typeof saved
  expect(saved.nodes.find((node) => node.id === 'layer-use-case')?.parentId).toBeUndefined()
})

test('authors catalog relationships for every diagram type and edits identity from Content', async ({ page }) => {
  const cases = [
    {
      diagramType: 'activity_diagram',
      nodes: [
        { id: 'source', type: 'gpNode', position: { x: 160, y: 220 }, width: 160, height: 60, data: { label: 'Source Action', semanticType: 'opaqueAction' } },
        { id: 'target', type: 'gpNode', position: { x: 480, y: 220 }, width: 160, height: 60, data: { label: 'Target Action', semanticType: 'opaqueAction' } },
      ],
      labels: ['Control Flow', 'Comment Link'],
      selectedLabel: 'Control Flow',
      expectedSemantic: 'controlFlow',
      expectedMode: 'orthogonal',
    },
    {
      diagramType: 'use_case_diagram',
      nodes: [
        { id: 'source', type: 'gpNode', position: { x: 140, y: 210 }, width: 200, height: 100, data: { label: 'Source Use Case', semanticType: 'useCase' } },
        { id: 'target', type: 'gpNode', position: { x: 480, y: 210 }, width: 200, height: 100, data: { label: 'Target Use Case', semanticType: 'useCase' } },
      ],
      labels: ['Association', 'Generalization', 'Include', 'Extend', 'Comment Link'],
      selectedLabel: 'Extend',
      expectedSemantic: 'extend',
      expectedMode: 'straight',
    },
    {
      diagramType: 'bdd_diagram',
      nodes: [
        { id: 'source', type: 'gpNode', position: { x: 160, y: 210 }, width: 180, height: 90, data: { label: 'Part', semanticType: 'block' } },
        { id: 'target', type: 'gpNode', position: { x: 500, y: 210 }, width: 180, height: 90, data: { label: 'Whole', semanticType: 'block' } },
      ],
      labels: ['Association', 'Composition', 'Generalization', 'Dependency', 'Comment Link'],
      selectedLabel: 'Composition',
      expectedSemantic: 'composition',
      expectedMode: 'orthogonal',
    },
    {
      diagramType: 'custom',
      nodes: [
        { id: 'source', type: 'gpNode', position: { x: 160, y: 220 }, width: 160, height: 60, data: { label: 'Class', semanticType: 'class' } },
        { id: 'target', type: 'gpNode', position: { x: 480, y: 220 }, width: 160, height: 60, data: { label: 'Interface', semanticType: 'interface' } },
      ],
      labels: ['Association', 'Control Flow', 'Composition', 'Generalization', 'Include', 'Extend', 'Dependency', 'Realization', 'Comment Link'],
      selectedLabel: 'Realization',
      expectedSemantic: 'realization',
      expectedMode: 'orthogonal',
    },
  ] as const

  for (const current of cases) {
    const path = seedDiagram()
    const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
      diagramType: string
      nodes: Array<Record<string, unknown>>
      edges: Array<Record<string, unknown>>
    }
    diagram.diagramType = current.diagramType
    diagram.nodes = [...current.nodes]
    diagram.edges = []
    writeFileSync(path, JSON.stringify(diagram, null, 2))
    await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
    await setZoomPercent(page, 100)
    for (const label of current.labels) await expect(page.getByRole('button', { name: label })).toBeVisible()
    await expect(page.getByRole('button', { name: current.labels[0] })).toHaveAttribute('aria-pressed', 'true')
    await expect(page.getByRole('button', { name: current.expectedMode === 'straight' ? 'Straight' : 'Orthogonal' })).toHaveAttribute('aria-pressed', 'true')
    await page.getByRole('button', { name: current.selectedLabel }).click()
    await expect(page.getByRole('button', { name: current.selectedLabel })).toHaveAttribute('aria-pressed', 'true')

    const source = page.locator('.react-flow__node[data-id="source"]')
    const target = page.locator('.react-flow__node[data-id="target"]')
    const sourceBox = await source.boundingBox()
    const targetBox = await target.boundingBox()
    if (!sourceBox || !targetBox) throw new Error(`expected ${current.diagramType} relationship bounds`)
    await page.mouse.move(sourceBox.x + sourceBox.width - 2, sourceBox.y + sourceBox.height / 2)
    await page.mouse.down()
    await page.mouse.move(targetBox.x + 2, targetBox.y + targetBox.height / 2, { steps: 12 })
    await page.mouse.up()
    await expect(page.locator('.react-flow__edge')).toHaveCount(1)

    if (current.diagramType === 'use_case_diagram') {
      await page.getByRole('group', { name: 'Edge from source to target' }).locator('.react-flow__edge-path').click({ force: true })
      const relationshipType = page.getByLabel('Relationship type')
      await expect(relationshipType).toHaveValue('extend')
      await page.getByLabel('Condition').fill('optional')
      await page.getByRole('button', { name: 'Generalization' }).click()
      await expect(page.getByRole('button', { name: 'Generalization' })).toHaveAttribute('aria-pressed', 'true')
      await expect(relationshipType).toHaveValue('generalization')
      await expect(page.getByLabel('Condition')).toHaveCount(0)
      const edgePath = page.getByRole('group', { name: 'Edge from source to target' }).locator('.react-flow__edge-path')
      await expect(edgePath).not.toHaveAttribute('stroke-dasharray')
      await expect(edgePath).toHaveAttribute('marker-end', /gp-generalization/)
    }

    await page.getByRole('button', { name: 'Save', exact: true }).click()
    await page.getByRole('button', { name: 'Overwrite' }).click()
    await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
    const saved = JSON.parse(readFileSync(path, 'utf8')) as {
      edges: Array<{ data?: { semanticType?: string; condition?: string }; route?: { mode?: string } }>
    }
    expect(saved.edges[0].data?.semanticType).toBe(current.diagramType === 'use_case_diagram' ? 'generalization' : current.expectedSemantic)
    expect(saved.edges[0].route?.mode).toBe(current.expectedMode)
    if (current.diagramType === 'use_case_diagram') expect(saved.edges[0].data?.condition).toBeUndefined()
  }
})

test('organizes and searches the unified authoring palette without breaking add gestures', async ({ page }) => {
  const scope = page.getByLabel('Palette scope')
  const organization = page.getByLabel('Organize palette by')
  const search = page.getByLabel('Search shapes and relationships')
  await expect(scope).toHaveValue('current')
  await expect(organization).toHaveValue('diagram')
  await expect(page.getByRole('button', { name: 'Shared', exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Activity', exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'BDD', exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: 'Control Flow' }).click()
  await expect(page.getByRole('button', { name: 'Control Flow' })).toHaveAttribute('aria-pressed', 'true')

  await scope.selectOption('all')
  for (const group of ['Shared', 'Activity', 'Use Case', 'BDD', 'Custom-only']) {
    await expect(page.getByRole('button', { name: group, exact: true })).toBeVisible()
  }
  await expect(page.getByRole('button', { name: 'Add Block' })).toBeVisible()
  await organization.selectOption('notation')
  for (const group of ['Common', 'UML', 'SysML']) await expect(page.getByRole('button', { name: group, exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Control Flow' })).toHaveAttribute('aria-pressed', 'true')
  await page.getByRole('button', { name: 'UML', exact: true }).click()
  await page.reload()
  await expect(scope).toHaveValue('all')
  await expect(organization).toHaveValue('notation')
  await expect(page.getByRole('button', { name: 'UML', exact: true })).toHaveAttribute('aria-expanded', 'false')

  await expect(page.getByRole('button', { name: 'Control Flow' })).toBeVisible()
  await search.fill('include')
  await expect(page.getByRole('button', { name: 'Include' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'UML', exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Add Block' })).toHaveCount(0)
  await search.fill('')
  await expect(page.getByRole('button', { name: 'UML', exact: true })).toHaveAttribute('aria-expanded', 'false')

  await scope.selectOption('current')
  await organization.selectOption('diagram')
  await expect(page.getByRole('button', { name: 'Control Flow' })).toHaveAttribute('aria-pressed', 'true')
  const nodes = page.locator('.react-flow__node')
  const before = await nodes.count()
  const pane = page.locator('.react-flow__pane')
  await page.getByRole('button', { name: 'Add Opaque Action' }).dragTo(pane, { targetPosition: { x: 420, y: 320 } })
  await expect(nodes).toHaveCount(before + 1)
  await page.getByRole('button', { name: 'Add Decision Node' }).press('Enter')
  await expect(nodes).toHaveCount(before + 2)
  await expect(scope).toHaveValue('current')
  await expect(organization).toHaveValue('diagram')
})

test('preserves parallel relationships from a Fork to the same target', async ({ page }) => {
  const path = seedDiagram()
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByRole('button', { name: 'Zoom Out' }).click()
  const fork = page.locator('.react-flow__node').filter({ hasText: 'Fork' })
  const target = page.locator('.react-flow__node').filter({ hasText: 'Run Hardware Diagnostics' })
  const forkBox = await fork.boundingBox()
  const targetBox = await target.boundingBox()
  if (!forkBox || !targetBox) throw new Error('expected Fork connection bounds')
  const edges = page.locator('.react-flow__edge')
  await expect(edges).toHaveCount(11)

  for (const offset of [0.35, 0.7]) {
    await page.mouse.move(forkBox.x + forkBox.width * offset, forkBox.y + forkBox.height - 2)
    await page.mouse.down()
    await page.mouse.move(targetBox.x + targetBox.width * offset, targetBox.y + 2, { steps: 16 })
    await page.mouse.up()
  }
  await expect(edges).toHaveCount(13)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ source: string; target: string; route?: { sourceAnchor?: { offset: number } } }>
  }
  const parallel = saved.edges.filter((edge) => edge.source === 'assessment-fork' && edge.target === 'hardware-diagnostics')
  const authoredOffsets = parallel.flatMap((edge) => edge.route?.sourceAnchor?.offset ?? [])
  expect(parallel).toHaveLength(3)
  expect(authoredOffsets).toHaveLength(2)
  expect(new Set(authoredOffsets).size).toBe(2)
})

test('draws Note links as commentLink and shows the complete dog-ear', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as {
    nodes: Array<Record<string, unknown>>
    edges: Array<{ source: string; target: string; data?: { semanticType?: string } }>
  }
  diagram.nodes.push({
    id: 'note-s13',
    type: 'gpNode',
    position: { x: 720, y: 0 },
    width: 160,
    height: 80,
    data: { label: 'S13 Comment', semanticType: 'note' },
  })
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByRole('button', { name: 'Zoom Out' }).click()

  const note = page.locator('.react-flow__node').filter({ hasText: 'S13 Comment' })
  const action = page.locator('.react-flow__node').filter({ hasText: 'Receive Device' })
  await expect(note.locator('svg path')).toHaveAttribute('d', 'M0 0 L14 14 M0 0 V14 H14')
  const noteBox = await note.boundingBox()
  const actionBox = await action.boundingBox()
  if (!noteBox || !actionBox) throw new Error('expected Note connection bounds')
  await page.mouse.move(noteBox.x + 2, noteBox.y + noteBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(actionBox.x + actionBox.width - 2, actionBox.y + actionBox.height / 2, { steps: 16 })
  await page.mouse.up()
  await expect(page.locator('.react-flow__edge')).toHaveCount(12)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as typeof diagram
  const noteEdge = saved.edges.find((edge) => edge.source === 'note-s13' || edge.target === 'note-s13')
  expect(noteEdge?.data?.semanticType).toBe('commentLink')
})

test('reconnects an endpoint at an exact boundary without reversing the fixed end', async ({ page }) => {
  const path = seedDiagram()
  const original = JSON.parse(readFileSync(path, 'utf8')) as { edges: Array<{ source: string; target: string }> }
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  const updater = page.locator('.react-flow__edgeupdater-target').first()
  const targetNode = page.locator('.react-flow__node').filter({ hasText: 'Assessment Complete' })
  const updaterBox = await updater.boundingBox()
  const targetBox = await targetNode.boundingBox()
  const targetGlyph = await targetNode.locator('svg').first().boundingBox()
  const target = await targetNode.getAttribute('data-id')
  if (!updaterBox || !targetBox || !targetGlyph || !target) throw new Error('expected reconnect boundary data')

  await page.mouse.move(updaterBox.x + updaterBox.width / 2, updaterBox.y + updaterBox.height / 2)
  await page.mouse.down()
  await page.mouse.move(targetGlyph.x + targetGlyph.width * 5 / 34, targetGlyph.y + targetGlyph.height / 2, { steps: 16 })
  await page.mouse.up()
  await expect(page.getByRole('group', { name: new RegExp(`Edge from ${target} to`) })).toBeVisible()

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ source: string; target: string; sourceHandle?: string; route?: { sourceAnchor?: { side: string; offset: number } } }>
  }
  const reconnected = saved.edges.find((item) => item.source === target)
  expect(original.edges.some((edge) => edge.target === reconnected?.target)).toBe(true)
  expect(reconnected?.sourceHandle).toBeUndefined()
  expect(reconnected?.route?.sourceAnchor?.side).toBe('left')
  expect(reconnected?.route?.sourceAnchor?.offset).toBeCloseTo(0.38, 1)
})

test('keeps node interiors available for movement', async ({ page }) => {
  const node = page.locator('.react-flow__node').filter({ hasText: 'Receive Device' })
  const edges = page.locator('.react-flow__edge')
  const before = await node.boundingBox()
  if (!before) throw new Error('expected node bounds')
  await page.mouse.move(before.x + before.width / 2, before.y + before.height / 2)
  await page.mouse.down()
  await page.mouse.move(before.x + before.width / 2 + 32, before.y + before.height / 2 + 18, { steps: 6 })
  await page.mouse.up()
  const after = await node.boundingBox()
  expect(after?.x).toBeGreaterThan(before.x + 10)
  await expect(edges).toHaveCount(11)
})

test('edits and persists anchors, orthogonal detours, and label placement', async ({ page }) => {
  const path = seedDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ id: string; source: string; target: string; label?: string; route?: { sourceAnchor?: object; waypoints?: object[]; labelOffset?: { x: number; y: number } } }>
  }
  const edgeIndex = 1
  const edgeAriaLabel = `Edge from ${diagram.edges[edgeIndex].source} to ${diagram.edges[edgeIndex].target}`
  diagram.edges[edgeIndex].label = 'Editable route'
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Editable route', { exact: true })).toBeVisible()

  await page.getByRole('group', { name: edgeAriaLabel }).dispatchEvent('click')
  await expect(page.getByLabel(/Move route segment/).first()).toBeVisible()
  await expect(page.getByRole('button', { name: 'Add route waypoint' })).toHaveCount(0)

  const segment = page.getByLabel(/Move route segment/).first()
  const segmentBox = await segment.boundingBox()
  if (!segmentBox) throw new Error('expected route segment grip')
  const segmentStart = { x: segmentBox.x + segmentBox.width / 2, y: segmentBox.y + segmentBox.height / 2 }
  await segment.dispatchEvent('pointerdown', { clientX: segmentStart.x, clientY: segmentStart.y, pointerId: 2, button: 0 })
  await page.evaluate(({ x, y }) => {
    const browser = globalThis as unknown as {
      PointerEvent: new (type: string, init: Record<string, unknown>) => Event
      dispatchEvent: (event: Event) => boolean
    }
    browser.dispatchEvent(new browser.PointerEvent('pointermove', { clientX: x + 20, clientY: y + 20, pointerId: 2 }))
    browser.dispatchEvent(new browser.PointerEvent('pointerup', { clientX: x + 20, clientY: y + 20, pointerId: 2 }))
  }, segmentStart)

  const anchor = await page.getByLabel('Move source anchor').boundingBox()
  if (!anchor) throw new Error('expected source anchor grip')
  await page.mouse.move(anchor.x + anchor.width / 2, anchor.y + anchor.height / 2)
  await page.mouse.down()
  await page.mouse.move(anchor.x + anchor.width / 2 + 18, anchor.y + anchor.height / 2 + 8, { steps: 4 })
  await page.mouse.up()

  const label = page.locator('.react-flow__edgelabel-renderer').getByText('Editable route', { exact: true })
  const labelBox = await label.boundingBox()
  if (!labelBox) throw new Error('expected relationship label')
  const labelStart = { x: labelBox.x + labelBox.width / 2, y: labelBox.y + labelBox.height / 2 }
  await label.dispatchEvent('pointerdown', { clientX: labelStart.x, clientY: labelStart.y, pointerId: 1, button: 0 })
  await page.evaluate(({ x, y }) => {
    const browser = globalThis as unknown as {
      PointerEvent: new (type: string, init: Record<string, unknown>) => Event
      dispatchEvent: (event: Event) => boolean
    }
    browser.dispatchEvent(new browser.PointerEvent('pointermove', { clientX: x + 28, clientY: y - 20, pointerId: 1 }))
    browser.dispatchEvent(new browser.PointerEvent('pointerup', { clientX: x + 28, clientY: y - 20, pointerId: 1 }))
  }, labelStart)

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as typeof diagram
  expect(saved.edges[edgeIndex].route?.sourceAnchor).toBeTruthy()
  expect(saved.edges[edgeIndex].route?.waypoints?.length).toBeGreaterThan(0)
  expect(Math.abs(saved.edges[edgeIndex].route?.labelOffset?.x ?? 0)).toBeGreaterThan(0)
  const renderedPath = await page.getByRole('group', { name: edgeAriaLabel }).locator('.react-flow__edge-path').getAttribute('d')

  await page.reload()
  await expect(page.getByText('Editable route', { exact: true })).toBeVisible()
  await expect(page.getByRole('group', { name: edgeAriaLabel }).locator('.react-flow__edge-path')).toHaveAttribute('d', renderedPath ?? '')
})

test('preserves a manual bend when node movement makes the route straight', async ({ page }) => {
  const path = seedBddDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.nodes = [
    { id: 'source', type: 'gpNode', position: { x: 0, y: 0 }, width: 100, height: 60, data: { label: 'Source', semanticType: 'block' } },
    { id: 'target', type: 'gpNode', position: { x: 300, y: 120 }, width: 100, height: 60, data: { label: 'Target', semanticType: 'block' } },
  ]
  diagram.edges = [{
    id: 'manual',
    source: 'source',
    target: 'target',
    route: {
      sourceAnchor: { side: 'right', offset: 0.5 },
      targetAnchor: { side: 'left', offset: 0.5 },
      waypoints: [{ x: 180, y: 30 }],
      labelOffset: { x: 4, y: -8 },
    },
    data: { semanticType: 'association' },
  }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  const source = page.locator('.react-flow__node').filter({ hasText: 'Source' })
  const target = page.locator('.react-flow__node').filter({ hasText: 'Target' })
  const sourceBox = await source.boundingBox()
  const targetBox = await target.boundingBox()
  if (!sourceBox || !targetBox) throw new Error('expected route nodes')
  const start = { x: targetBox.x + targetBox.width / 2, y: targetBox.y + targetBox.height / 2 }
  const alignedY = sourceBox.y + sourceBox.height / 2
  await page.mouse.move(start.x, start.y)
  await page.mouse.down()
  await page.mouse.move(start.x, alignedY, { steps: 8 })
  await page.mouse.up()
  const movedTargetBox = await target.boundingBox()
  if (!movedTargetBox) throw new Error('expected moved target bounds')
  const correction = sourceBox.y + sourceBox.height / 2 - (movedTargetBox.y + movedTargetBox.height / 2)
  if (Math.abs(correction) > 1) {
    const movedCenter = { x: movedTargetBox.x + movedTargetBox.width / 2, y: movedTargetBox.y + movedTargetBox.height / 2 }
    await page.mouse.move(movedCenter.x, movedCenter.y)
    await page.mouse.down()
    await page.mouse.move(movedCenter.x, movedCenter.y + correction, { steps: 4 })
    await page.mouse.up()
  }

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ route?: { waypoints?: object[]; sourceAnchor?: object; targetAnchor?: object; labelOffset?: object } }>
  }
  expect(saved.edges[0].route?.waypoints).toEqual([{ x: 180, y: 30 }])
  expect(saved.edges[0].route?.sourceAnchor).toBeTruthy()
  expect(saved.edges[0].route?.targetAnchor).toBeTruthy()
  expect(saved.edges[0].route?.labelOffset).toEqual({ x: 4, y: -8 })
})

test('deletes corner detours and straightens an explicit route with undo and render parity', async ({ page }) => {
  const path = seedBddDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.nodes = [
    { id: 'source', type: 'gpNode', position: { x: 0, y: 80 }, width: 100, height: 60, data: { label: 'Source', semanticType: 'block' } },
    { id: 'target', type: 'gpNode', position: { x: 400, y: 180 }, width: 100, height: 60, data: { label: 'Target', semanticType: 'block' } },
  ]
  diagram.edges = [{
    id: 'manual',
    source: 'source',
    target: 'target',
    route: {
      sourceAnchor: { side: 'right', offset: 0.5 },
      targetAnchor: { side: 'left', offset: 0.5 },
      waypoints: [{ x: 160, y: 110 }, { x: 160, y: 40 }, { x: 320, y: 40 }, { x: 320, y: 210 }],
      labelOffset: { x: 12, y: -6 },
    },
    data: { semanticType: 'association' },
  }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Target', { exact: true })).toBeVisible()

  const edge = page.getByTestId('rf__edge-manual')
  const edgePath = edge.locator('.react-flow__edge-path')
  const originalPath = await edgePath.getAttribute('d')
  await edge.dispatchEvent('click')
  const corners = page.getByRole('button', { name: /Delete detour at corner/ })
  await expect(corners).toHaveCount(2)
  await corners.first().click()
  const deletedPath = await edgePath.getAttribute('d')
  expect(deletedPath).toBe('M 100 110 L 160 110 L 160 210 L 400 210')
  await page.getByRole('button', { name: 'Undo' }).click()
  await expect(edgePath).toHaveAttribute('d', originalPath ?? '')
  const restoredCorners = page.getByRole('button', { name: /Delete detour at corner/ })
  await restoredCorners.last().focus()
  await page.keyboard.press('Enter')
  await expect(edgePath).toHaveAttribute('d', deletedPath ?? '')

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const savedDetour = JSON.parse(readFileSync(path, 'utf8')) as typeof diagram
  const response = await page.request.post(`${e2eApiBaseURL}/api/diagrams/render`, { data: { diagram: savedDetour } })
  expect(response.ok()).toBe(true)
  const svg = (await response.json()) as { svg: string }
  const serverPath = svg.svg.match(/<path d="(M[^"]+)" fill="none"/)?.[1]
  const coordinates = (value: string | null | undefined) => value?.match(/-?\d+(?:\.\d+)?/g)?.map(Number)
  expect(coordinates(deletedPath)).toEqual(coordinates(serverPath))

  await page.reload()
  await expect(page.getByTestId('rf__edge-manual').locator('.react-flow__edge-path')).toHaveAttribute('d', deletedPath ?? '')
  await page.getByTestId('rf__edge-manual').dispatchEvent('click')
  await page.getByRole('tab', { name: 'Appearance' }).click()
  await page.getByRole('button', { name: 'Straighten route' }).click()
  const straightPath = await page.getByTestId('rf__edge-manual').locator('.react-flow__edge-path').getAttribute('d')
  expect(straightPath).not.toBe(deletedPath)
  await page.getByRole('button', { name: 'Undo' }).click()
  await expect(page.getByTestId('rf__edge-manual').locator('.react-flow__edge-path')).toHaveAttribute('d', deletedPath ?? '')
  await page.getByRole('button', { name: 'Straighten route' }).click()

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const savedStraight = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ route?: { sourceAnchor?: object; targetAnchor?: object; waypoints?: object[]; labelOffset?: object } }>
  }
  expect(savedStraight.edges[0].route?.waypoints).toBeUndefined()
  expect(savedStraight.edges[0].route?.sourceAnchor).toEqual({ side: 'right', offset: 0.5 })
  expect(savedStraight.edges[0].route?.targetAnchor).toEqual({ side: 'left', offset: 0.5 })
  expect(savedStraight.edges[0].route?.labelOffset).toEqual({ x: 12, y: -6 })
})

test('switches a selected edge between orthogonal and straight routing with parity', async ({ page }) => {
  const path = seedUseCaseDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.nodes = [
    { id: 'source', type: 'gpNode', position: { x: 100, y: 100 }, width: 200, height: 70, data: { label: 'Source Use Case', semanticType: 'useCase' } },
    { id: 'target', type: 'gpNode', position: { x: 450, y: 300 }, width: 200, height: 70, data: { label: 'Target Use Case', semanticType: 'useCase' } },
  ]
  diagram.edges = [{
    id: 'route-mode',
    source: 'source',
    target: 'target',
    label: 'reuse',
    data: { semanticType: 'include' },
    route: {
      mode: 'orthogonal',
      sourceAnchor: { side: 'right', offset: 0.5 },
      targetAnchor: { side: 'top', offset: 0.5 },
      waypoints: [{ x: 360, y: 135 }],
      labelOffset: { x: 8, y: -12 },
    },
  }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  const edge = page.getByTestId('rf__edge-route-mode')
  await edge.dispatchEvent('click')
  await expect(page.getByRole('button', { name: 'Orthogonal' })).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByLabel('Move route segment 1')).toBeVisible()

  await page.getByRole('button', { name: 'Straight' }).click()
  await expect(page.getByRole('button', { name: 'Straight' })).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByLabel(/Move route segment/)).toHaveCount(0)
  const straightPath = await edge.locator('.react-flow__edge-path').getAttribute('d')
  expect((straightPath?.match(/ L /g) ?? []).length).toBe(1)

  await page.getByRole('button', { name: 'Undo' }).click()
  await expect(page.getByRole('button', { name: 'Orthogonal' })).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByLabel('Move route segment 1')).toBeVisible()
  await page.getByRole('button', { name: 'Redo' }).click()
  await expect(page.getByRole('button', { name: 'Straight' })).toHaveAttribute('aria-pressed', 'true')

  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/).last()).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ route?: { mode?: string; sourceAnchor?: object; targetAnchor?: object; waypoints?: object[]; labelOffset?: object } }>
  }
  expect(saved.edges[0].route).toEqual({
    mode: 'straight',
    sourceAnchor: { side: 'right', offset: 0.5 },
    targetAnchor: { side: 'top', offset: 0.5 },
    labelOffset: { x: 8, y: -12 },
  })

  await page.reload()
  const reloadedPath = await page.getByTestId('rf__edge-route-mode').locator('.react-flow__edge-path').getAttribute('d')
  expect(reloadedPath).toBe(straightPath)
  const savedDiagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown>
  const response = await page.request.post(`${e2eApiBaseURL}/api/diagrams/render`, { data: { diagram: savedDiagram } })
  expect(response.ok()).toBe(true)
  const svg = (await response.json()) as { svg: string }
  const serverPath = svg.svg.match(/<path d="(M[^"]+)" fill="none"/)?.[1]
  const coordinates = (value: string | null | undefined) => value?.match(/-?\d+(?:\.\d+)?/g)?.map(Number)
  expect(coordinates(reloadedPath)).toEqual(coordinates(serverPath))
})

test('ignores unrelated nodes and matches the server SVG geometry', async ({ page }) => {
  const path = seedBddDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.nodes = [
    { id: 'source', type: 'gpNode', position: { x: 0, y: 80 }, width: 100, height: 60, data: { label: 'Source', semanticType: 'block' } },
    { id: 'unrelated', type: 'gpNode', position: { x: 240, y: 60 }, width: 120, height: 100, data: { label: 'Unrelated', semanticType: 'block' } },
    { id: 'target', type: 'gpNode', position: { x: 500, y: 80 }, width: 100, height: 60, data: { label: 'Target', semanticType: 'block' } },
  ]
  diagram.edges = [{ id: 'routed', source: 'source', target: 'target', data: { semanticType: 'dependency' } }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Unrelated', { exact: true })).toBeVisible()

  const canvasPath = await page.getByRole('group', { name: 'Edge from source to target' }).locator('.react-flow__edge-path').getAttribute('d')
  const response = await page.request.post(`${e2eApiBaseURL}/api/diagrams/render`, { data: { diagram } })
  expect(response.ok()).toBe(true)
  const svg = (await response.json()) as { svg: string }
  const serverPath = svg.svg.match(/<path d="(M[^"]+)" fill="none"/)?.[1]
  const coordinates = (value: string | null | undefined) => value?.match(/-?\d+(?:\.\d+)?/g)?.map(Number)
  expect(coordinates(canvasPath)).toEqual(coordinates(serverPath))
  expect(coordinates(canvasPath)).toEqual([100, 110, 500, 110])
})

test('routes sibling relationships independently with canvas and SVG parity', async ({ page }) => {
  const path = seedBddDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown> & {
    nodes: Array<Record<string, unknown>>
    edges: Array<Record<string, unknown>>
  }
  diagram.nodes = [
    { id: 'services', type: 'gpNode', position: { x: 200, y: 0 }, width: 120, height: 60, data: { label: 'Services', semanticType: 'block' } },
    { id: 'eval', type: 'gpNode', position: { x: 0, y: 240 }, width: 100, height: 60, data: { label: 'EvalService', semanticType: 'block' } },
    { id: 'file', type: 'gpNode', position: { x: 220, y: 240 }, width: 100, height: 60, data: { label: 'FileService', semanticType: 'block' } },
    { id: 'validation', type: 'gpNode', position: { x: 440, y: 240 }, width: 100, height: 60, data: { label: 'ValidationService', semanticType: 'block' } },
  ]
  diagram.edges = ['eval', 'file', 'validation'].map((target) => ({
    id: `dependency-${target}`,
    source: 'services',
    target,
    data: { semanticType: target === 'file' ? 'generalization' : 'dependency' },
  }))
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('ValidationService', { exact: true })).toBeVisible()

  const edgeIds = diagram.edges.map((edge) => String(edge.id))
  const pathsById = async (): Promise<Record<string, string>> => Object.fromEntries(await Promise.all(edgeIds.map(async (id) => [
    id,
    await page.getByTestId(`rf__edge-${id}`).locator('.react-flow__edge-path').getAttribute('d') ?? '',
  ])))
  const originalPaths = await pathsById()
  expect(Object.values(originalPaths).every((pathValue) => (pathValue.match(/ L /g) ?? []).length <= 2)).toBe(true)

  diagram.edges.reverse()
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.reload()
  await expect(page.locator('.react-flow__edge-path')).toHaveCount(3)
  expect(await pathsById()).toEqual(originalPaths)

  const canvasPaths = await Promise.all(diagram.edges.map((edge) =>
    page.getByTestId(`rf__edge-${String(edge.id)}`).locator('.react-flow__edge-path').getAttribute('d').then((value) => value ?? ''),
  ))
  const response = await page.request.post(`${e2eApiBaseURL}/api/diagrams/render`, { data: { diagram } })
  const svg = (await response.json()) as { svg: string }
  const serverPaths = Array.from(svg.svg.matchAll(/<path d="(M[^"]+)" fill="none"/g), (match) => match[1]).slice(0, 3)
  const coordinates = (value: string) => value.match(/-?\d+(?:\.\d+)?/g)?.map(Number)
  expect(canvasPaths.map(coordinates)).toEqual(serverPaths.map(coordinates))
})

test('duplicates the selected node with Ctrl+D', async ({ page }) => {
  const nodes = page.locator('.react-flow__node')
  await expect(nodes).toHaveCount(10)
  await page.getByText('Receive Device').click()
  await page.keyboard.press('Control+d')
  await expect(nodes).toHaveCount(11)
})

test('deletes the selected node with the Delete key', async ({ page }) => {
  const nodes = page.locator('.react-flow__node')
  await expect(nodes).toHaveCount(10)
  await page.getByText('Run Hardware Diagnostics').click({ force: true })
  await page.keyboard.press('Delete')
  await expect(nodes).toHaveCount(9)
  await page.getByRole('button', { name: 'Undo' }).click()
  await expect(nodes).toHaveCount(10)
})

test('autosave stops retrying until another edit after a validation failure', async ({ page }) => {
  let saves = 0
  page.on('request', (request) => {
    if (request.method() === 'POST' && request.url().endsWith('/api/diagrams/save')) saves += 1
  })
  await page.getByText('Receive Device').click()
  await page.getByLabel('Label', { exact: true }).fill('')
  await page.getByLabel('Autosave').check()
  await expect.poll(() => saves).toBe(1)
  await page.waitForTimeout(2200)
  expect(saves).toBe(1)

  await page.getByLabel('Label', { exact: true }).fill('Receive Device')
  await expect.poll(() => saves).toBe(2)
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
})

test('closing an in-flight render preview does not reopen it', async ({ page }) => {
  await page.route('**/api/diagrams/render', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 800))
    await route.continue()
  })
  await page.getByRole('button', { name: 'Preview' }).click()
  await page.getByRole('menuitem', { name: 'Render (SVG)' }).click()
  await expect(page.getByRole('heading', { name: 'Backend render preview' })).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('heading', { name: 'Backend render preview' })).not.toBeVisible()
  await page.waitForTimeout(1000)
  await expect(page.getByRole('heading', { name: 'Backend render preview' })).not.toBeVisible()
})

test('exports the canvas as a PNG download (server render)', async ({ page }) => {
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export' }).click()
  await page.getByRole('menuitem', { name: 'PNG image' }).click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain('.png')
})

test('exports the canvas as an SVG download (server render)', async ({ page }) => {
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export' }).click()
  await page.getByRole('menuitem', { name: 'SVG vector' }).click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain('.svg')
})

test('renders and inspects structured BDD features', async ({ page }) => {
  const path = seedBddDiagram()
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Spacecraft', { exact: true })).toBeVisible()
  await expect(page.getByText('value properties', { exact: true })).toBeVisible()
  await expect(page.getByText('dryMass: 12 t [1]', { exact: true })).toBeVisible()
  await page.getByText('Spacecraft', { exact: true }).click()
  await page.getByRole('button', { name: /Edit Property 1/i }).click()
  await expect(page.getByLabel('Property 1 name')).toHaveValue('dryMass')
  await page.getByRole('tab', { name: 'Advanced' }).click()
  await expect(page.getByLabel('Semantic type')).toHaveValue('block')
})

test('persists and renders a BDD Block primary stereotype', async ({ page }) => {
  const path = seedBddDiagram()
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByText('Spacecraft', { exact: true }).click()
  await page.getByLabel('Primary stereotype').fill('interfaceBlock')
  await expect(page.getByText('«interfaceBlock»', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as { nodes: Array<{ id: string; data: { stereotype?: string } }> }
  expect(diagram.nodes.find((node) => node.id === 'craft')?.data.stereotype).toBe('interfaceBlock')
})

test('swaps Composition endpoints and authored route direction atomically', async ({ page }) => {
  const path = seedBddDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as {
    nodes: Array<{ id: string }>
    edges: Array<Record<string, unknown>>
  }
  const [part, whole] = diagram.nodes
  diagram.edges = [{
    id: 'composition-swap',
    source: part.id,
    target: whole.id,
    route: {
      sourceAnchor: { side: 'right', offset: 0.25 },
      targetAnchor: { side: 'left', offset: 0.75 },
      waypoints: [{ x: 100, y: 20 }, { x: 140, y: 20 }],
    },
    data: {
      semanticType: 'composition',
      sourceEnd: { role: 'part' },
      targetEnd: { role: 'whole' },
    },
  }]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await page.getByRole('group', { name: `Edge from ${part.id} to ${whole.id}` }).evaluate((edge) => {
    const browser = globalThis as unknown as { MouseEvent: new (type: string, init: Record<string, unknown>) => never }
    edge.dispatchEvent(new browser.MouseEvent('click', { bubbles: true }))
  })
  await page.getByRole('tab', { name: 'Appearance' }).click()
  await page.getByRole('button', { name: 'Swap ends' }).click()
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await page.getByRole('button', { name: 'Overwrite' }).click()
  await expect(page.getByText(/Diagram saved/)).toBeVisible()
  const saved = JSON.parse(readFileSync(path, 'utf8')) as {
    edges: Array<{ source: string; target: string; route?: { sourceAnchor?: unknown; targetAnchor?: unknown; waypoints?: unknown[] }; data?: { sourceEnd?: { role?: string }; targetEnd?: { role?: string } } }>
  }
  const swapped = saved.edges[0]
  expect([swapped.source, swapped.target]).toEqual([whole.id, part.id])
  expect(swapped.data?.sourceEnd?.role).toBe('whole')
  expect(swapped.data?.targetEnd?.role).toBe('part')
  expect(swapped.route?.sourceAnchor).toEqual({ side: 'left', offset: 0.75 })
  expect(swapped.route?.targetAnchor).toEqual({ side: 'right', offset: 0.25 })
  expect(swapped.route?.waypoints).toEqual([{ x: 140, y: 20 }, { x: 100, y: 20 }])
})

test('renders every BDD custom relationship marker as a valid SVG reference', async ({ page }) => {
  const path = seedBddDiagram()
  const diagram = JSON.parse(readFileSync(path, 'utf8')) as {
    nodes: Array<{ id: string }>
    edges: Array<Record<string, unknown>>
  }
  const [source, target] = diagram.nodes
  diagram.edges = [
    { id: 'composition', source: source.id, target: target.id, data: { semanticType: 'composition' } },
    { id: 'aggregation', source: source.id, target: target.id, data: { semanticType: 'association', sourceEnd: { aggregation: 'shared' } } },
    { id: 'generalization', source: source.id, target: target.id, data: { semanticType: 'generalization' } },
    { id: 'containment', source: source.id, target: target.id, data: { semanticType: 'containment' } },
  ]
  writeFileSync(path, JSON.stringify(diagram, null, 2))
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Spacecraft', { exact: true })).toBeVisible()
  const markers = await page.locator('.react-flow__edge-path').evaluateAll((paths) =>
    paths.flatMap((edge) => [edge.getAttribute('marker-start'), edge.getAttribute('marker-end')].filter(Boolean)),
  )
  for (const marker of ['gp-composition', 'gp-aggregation', 'gp-generalization', 'gp-crosshair']) {
    expect(markers.some((value) => value?.includes(marker))).toBe(true)
  }
  expect(markers.every((marker) => !marker?.includes('url(#url'))).toBe(true)
})

test('renders use-case extension points and first-class extend relationships', async ({ page }) => {
  const path = seedUseCaseDiagram()
  await page.goto(`/editor?diagramPath=${encodeURIComponent(path)}`)
  await expect(page.getByText('Airline System', { exact: true })).toBeVisible()
  await expect(page.getByText('extension points', { exact: true })).toBeVisible()
  await expect(page.getByText('«extend» [optional]', { exact: true })).toBeVisible()
  await page.getByText('Book Flight', { exact: true }).click()
  await expect(page.getByLabel('Semantic type')).toHaveValue('useCase')
  await expect(page.getByLabel('Extension points')).toHaveValue('extensionPoint')
})
