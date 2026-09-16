/** @vitest-environment jsdom */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { downloadPng, downloadSvg, svgToPngBlob } from './exportImage'

const SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80"></svg>'

// Capture every <a> the module creates so we can assert the download filename.
// Other tags (e.g. the <canvas> used for PNG raster) pass through to jsdom.
function captureAnchors(): HTMLAnchorElement[] {
  const anchors: HTMLAnchorElement[] = []
  const realCreate = document.createElement.bind(document)
  vi.spyOn(document, 'createElement').mockImplementation(((tag: string) => {
    const el = realCreate(tag)
    if (tag === 'a') anchors.push(el as HTMLAnchorElement)
    return el
  }) as typeof document.createElement)
  return anchors
}

// A fake Image whose `src` setter resolves `onload` (jsdom does not load blobs).
function mockLoadingImage(width: number, height: number) {
  class FakeImage {
    onload: (() => void) | null = null
    onerror: (() => void) | null = null
    naturalWidth = width
    naturalHeight = height
    width = width
    height = height
    set src(_value: string) {
      queueMicrotask(() => this.onload?.())
    }
  }
  vi.stubGlobal('Image', FakeImage as unknown as typeof Image)
}

// Stub the canvas 2D context + toBlob (jsdom has no real canvas backend).
function mockCanvas(result: Blob | null) {
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
    fillStyle: '',
    fillRect: vi.fn(),
    drawImage: vi.fn(),
  } as unknown as CanvasRenderingContext2D)
  vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((cb: BlobCallback) => cb(result))
}

beforeEach(() => {
  // jsdom does not implement URL.createObjectURL, so stub the whole global.
  vi.stubGlobal('URL', {
    createObjectURL: vi.fn(() => 'blob:fake'),
    revokeObjectURL: vi.fn(),
  })
})

afterEach(() => {
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('downloadSvg', () => {
  it('triggers a .svg download from the rendered SVG', () => {
    const anchors = captureAnchors()
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    downloadSvg(SVG, 'my-diagram')
    expect(clickSpy).toHaveBeenCalledTimes(1)
    expect(anchors.at(-1)?.download).toBe('my-diagram.svg')
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1)
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:fake')
  })

  it('does not double-append the .svg extension', () => {
    const anchors = captureAnchors()
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    downloadSvg(SVG, 'diagram.svg')
    expect(anchors.at(-1)?.download).toBe('diagram.svg')
  })
})

describe('svgToPngBlob / downloadPng', () => {
  it('rasterizes the SVG to a PNG blob', async () => {
    mockLoadingImage(120, 80)
    mockCanvas(new Blob(['png'], { type: 'image/png' }))
    const blob = await svgToPngBlob(SVG, 2)
    expect(blob.type).toBe('image/png')
  })

  it('downloadPng triggers a .png download', async () => {
    mockLoadingImage(120, 80)
    mockCanvas(new Blob(['png'], { type: 'image/png' }))
    const anchors = captureAnchors()
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    await downloadPng(SVG, 'my-diagram')
    expect(clickSpy).toHaveBeenCalledTimes(1)
    expect(anchors.at(-1)?.download).toBe('my-diagram.png')
  })

  it('rejects when the SVG image fails to load', async () => {
    class FailImage {
      onload: (() => void) | null = null
      onerror: (() => void) | null = null
      set src(_value: string) {
        queueMicrotask(() => this.onerror?.())
      }
    }
    vi.stubGlobal('Image', FailImage as unknown as typeof Image)
    await expect(svgToPngBlob(SVG)).rejects.toThrow(/Could not load the SVG/)
  })
})
