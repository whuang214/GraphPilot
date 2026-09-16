/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { GraphPilotDiagram } from '@/types/diagram'
import { isFileSystemAccessSupported, openLocalDiagram, saveAsLocalDiagram, writeHandle } from './fileSystem'

const diagram: GraphPilotDiagram = {
  schemaVersion: 'graphpilot.diagram.v1',
  kind: 'diagram',
  diagramType: 'activity_diagram',
  id: 'd',
  name: 'D',
  metadata: {},
  viewport: { x: 0, y: 0, zoom: 1 },
  nodes: [],
  edges: [],
}

const win = window as unknown as Record<string, unknown>

afterEach(() => {
  delete win.showOpenFilePicker
  delete win.showSaveFilePicker
  vi.restoreAllMocks()
})

describe('fileSystem', () => {
  it('reports unsupported when the File System Access API is absent', () => {
    expect(isFileSystemAccessSupported()).toBe(false)
  })

  it('openLocalDiagram reads and parses the picked file', async () => {
    const handle = {
      name: 'order.gp.json',
      getFile: async () => ({ text: async () => JSON.stringify(diagram) }) as unknown as File,
      createWritable: async () => ({ write: async () => {}, close: async () => {} }),
    }
    win.showOpenFilePicker = vi.fn().mockResolvedValue([handle])
    const res = await openLocalDiagram()
    expect(res?.handle.name).toBe('order.gp.json')
    expect(res?.diagram.diagramType).toBe('activity_diagram')
    expect(res?.revision).toHaveLength(64)
  })

  it('returns null only for picker cancellation and propagates other open failures', async () => {
    win.showOpenFilePicker = vi.fn().mockRejectedValueOnce(new DOMException('cancelled', 'AbortError'))
    expect(await openLocalDiagram()).toBeNull()

    win.showOpenFilePicker = vi.fn().mockRejectedValueOnce(new DOMException('denied', 'NotAllowedError'))
    await expect(openLocalDiagram()).rejects.toMatchObject({ name: 'NotAllowedError' })
  })

  it('rejects parsed JSON that is not a renderable GraphPilot document', async () => {
    const handle = {
      name: 'bad.gp.json',
      getFile: async () => ({ text: async () => '{}' }) as unknown as File,
      createWritable: async () => ({ write: async () => {}, close: async () => {} }),
    }
    win.showOpenFilePicker = vi.fn().mockResolvedValue([handle])
    await expect(openLocalDiagram()).rejects.toThrow(/GraphPilot diagram/)
  })

  it('writeHandle writes pretty-printed JSON to the handle', async () => {
    const writes: string[] = []
    const handle = {
      name: 'x',
      getFile: async () => ({}) as File,
      createWritable: async () => ({
        write: async (d: string) => {
          writes.push(d)
        },
        close: async () => {},
      }),
    }
    const revision = await writeHandle(handle, diagram)
    expect(JSON.parse(writes[0]).id).toBe('d')
    expect(revision).toHaveLength(64)
  })

  it('saveAsLocalDiagram returns null when the API is unsupported', async () => {
    expect(await saveAsLocalDiagram(diagram, 'x.gp.json')).toBeNull()
  })

  it('returns null only for Save As cancellation and propagates other picker failures', async () => {
    win.showSaveFilePicker = vi.fn().mockRejectedValueOnce(new DOMException('cancelled', 'AbortError'))
    expect(await saveAsLocalDiagram(diagram, 'x.gp.json')).toBeNull()

    win.showSaveFilePicker = vi.fn().mockRejectedValueOnce(new DOMException('denied', 'NotAllowedError'))
    await expect(saveAsLocalDiagram(diagram, 'x.gp.json')).rejects.toMatchObject({ name: 'NotAllowedError' })
  })
})
