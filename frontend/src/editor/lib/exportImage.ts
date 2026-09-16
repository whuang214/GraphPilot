// Image export for the editor. The canonical, full-fidelity
// source is the server-side renderer (`DiagramRenderService` -> SVG, via
// `POST /api/diagrams/render`): the editor posts the canonical JSON it would
// save and gets back an SVG. This module turns that SVG into a download —
// either the SVG directly or a client-side PNG rasterization of it. No native
// dependency, and it avoids the DOM-screenshot black-label bug of the old
// `html-to-image` path.

function withExtension(fileName: string, ext: '.svg' | '.png'): string {
  return fileName.toLowerCase().endsWith(ext) ? fileName : `${fileName}${ext}`
}

function triggerDownload(href: string, fileName: string): void {
  const link = document.createElement('a')
  link.download = fileName
  link.href = href
  link.click()
}

/** Download the server-rendered SVG string as a `.svg` file. */
export function downloadSvg(svg: string, fileName: string): void {
  const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }))
  try {
    triggerDownload(url, withExtension(fileName, '.svg'))
  } finally {
    URL.revokeObjectURL(url)
  }
}

/** Rasterize an SVG string to a PNG `Blob` client-side: load it into an
 * `Image`, draw it onto a `<canvas>` over a white background at a fixed scale,
 * and read back a PNG blob. Resolves once the image has loaded and drawn. */
export function svgToPngBlob(svg: string, scale = 2): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const svgUrl = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }))
    const image = new Image()
    image.onload = () => {
      try {
        const width = Math.max(1, Math.round((image.naturalWidth || image.width) * scale))
        const height = Math.max(1, Math.round((image.naturalHeight || image.height) * scale))
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('Could not get a 2D canvas context for PNG export.'))
          return
        }
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(0, 0, width, height)
        ctx.drawImage(image, 0, 0, width, height)
        canvas.toBlob((blob) => {
          if (blob) resolve(blob)
          else reject(new Error('Could not rasterize the SVG to a PNG.'))
        }, 'image/png')
      } finally {
        URL.revokeObjectURL(svgUrl)
      }
    }
    image.onerror = () => {
      URL.revokeObjectURL(svgUrl)
      reject(new Error('Could not load the SVG for PNG export.'))
    }
    image.src = svgUrl
  })
}

/** Rasterize the server-rendered SVG to a PNG and download it as a `.png` file. */
export async function downloadPng(svg: string, fileName: string, scale = 2): Promise<void> {
  const blob = await svgToPngBlob(svg, scale)
  const url = URL.createObjectURL(blob)
  try {
    triggerDownload(url, withExtension(fileName, '.png'))
  } finally {
    URL.revokeObjectURL(url)
  }
}
