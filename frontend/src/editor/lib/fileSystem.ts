import type { GraphPilotDiagram } from '@/types/diagram'
import { isGraphPilotDiagram } from '@/types/diagram'

// Minimal local typings for the File System Access API so we don't depend on a
// global lib/types package. Only the surface we use is declared. The API is
// Chromium-only; callers must feature-detect with isFileSystemAccessSupported().
interface WritableLike {
  write: (data: string) => Promise<void>
  close: () => Promise<void>
}

export interface LocalFileHandle {
  name: string
  getFile: () => Promise<File>
  createWritable: () => Promise<WritableLike>
}

export interface LocalDiagramResult {
  handle: LocalFileHandle | null
  diagram: GraphPilotDiagram
  revision: string
  name: string
}

interface FsaWindow {
  showOpenFilePicker?: (options?: unknown) => Promise<LocalFileHandle[]>
  showSaveFilePicker?: (options?: unknown) => Promise<LocalFileHandle>
}

const PICKER_OPTS = {
  types: [{ description: 'GraphPilot diagram', accept: { 'application/json': ['.gp.json', '.json'] } }],
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

function parseDiagram(text: string): GraphPilotDiagram {
  const value: unknown = JSON.parse(text)
  if (!isGraphPilotDiagram(value)) throw new Error('The file is not a valid GraphPilot diagram document.')
  return value
}

/**
 * A revision is the hash of the bytes that were read, never of a re-serialized document.
 *
 * There was a `diagramRevision(diagram)` beside this that stringified and then hashed. It
 * was exported, called by nothing, and would have been wrong if it had been: the backend
 * compares `expectedRevision` against the file it holds, and a hash taken after a
 * round-trip through `JSON.parse`/`JSON.stringify` differs from the file's own whenever
 * indentation or key order does. Every caller here already hashes the text.
 */
async function contentRevision(text: string): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('')
}

export async function readHandleDiagram(handle: LocalFileHandle): Promise<LocalDiagramResult & { handle: LocalFileHandle }> {
  const file = await handle.getFile()
  const text = await file.text()
  return { handle, diagram: parseDiagram(text), revision: await contentRevision(text), name: file.name || handle.name }
}

export function isFileSystemAccessSupported(): boolean {
  if (typeof window === 'undefined') return false
  const w = window as unknown as FsaWindow
  return typeof w.showOpenFilePicker === 'function' && typeof w.showSaveFilePicker === 'function'
}

/** Open any .gp.json from disk via the native picker. Returns null if the user
 * cancels. Throws if the file is not valid JSON (caller should surface that). */
export async function openLocalDiagram(): Promise<(LocalDiagramResult & { handle: LocalFileHandle }) | null> {
  const w = window as unknown as FsaWindow
  if (!w.showOpenFilePicker) return null
  let handles: LocalFileHandle[]
  try {
    handles = await w.showOpenFilePicker(PICKER_OPTS)
  } catch (error) {
    if (isAbortError(error)) return null
    throw error
  }
  const handle = handles[0]
  return handle ? readHandleDiagram(handle) : null
}

/** Open a `.gp.json` that was dropped onto the app. Prefers a
 * writable `FileSystemFileHandle` (Chromium) so Save works in place; otherwise
 * falls back to reading the dropped `File` read-only (the user can Save As).
 * Returns null when nothing usable was dropped; throws on a wrong extension or
 * invalid JSON so the caller can surface it. */
export async function openDroppedDiagram(
  dataTransfer: DataTransfer,
): Promise<LocalDiagramResult | null> {
  // Capture everything synchronously — a DataTransfer is neutered once the drop
  // event handler yields (the first await below).
  const item = dataTransfer.items && dataTransfer.items.length ? dataTransfer.items[0] : null
  const droppedFile = dataTransfer.files && dataTransfer.files.length ? dataTransfer.files[0] : null
  const handleGetter = item as { getAsFileSystemHandle?: () => Promise<unknown> } | null
  const handlePromise =
    handleGetter && typeof handleGetter.getAsFileSystemHandle === 'function'
      ? handleGetter.getAsFileSystemHandle()
      : null

  let handle: LocalFileHandle | null = null
  let file: File | null = droppedFile
  if (handlePromise) {
    try {
      const resolved = (await handlePromise) as (LocalFileHandle & { kind?: string }) | null
      if (resolved && resolved.kind === 'file') {
        handle = resolved
        file = await resolved.getFile()
      }
    } catch {
      // Fall back to the plain File captured above.
    }
  }
  if (!file) return null
  if (!/\.json$/i.test(file.name)) {
    throw new Error('Not a .gp.json diagram file.')
  }
  const text = await file.text()
  return { handle, diagram: parseDiagram(text), revision: await contentRevision(text), name: file.name }
}

/** Write a diagram back to an already-open handle (the default Save for a
 * picker-opened file). */
export async function writeHandle(handle: LocalFileHandle, diagram: GraphPilotDiagram): Promise<string> {
  let writable: WritableLike
  try {
    // Opening the writable is where Chromium re-checks (and can deny) write
    // permission for the handle.
    writable = await handle.createWritable()
  } catch {
    throw new Error(
      'Could not write to the file — its write permission may have been lost. Use “Save As…” to pick it again.',
    )
  }
  const text = JSON.stringify(diagram, null, 2)
  await writable.write(text)
  await writable.close()
  return contentRevision(text)
}

/** Save As: pick a new location, write the diagram there, and return the new
 * handle to adopt. Returns null if the user cancels. */
export async function saveAsLocalDiagram(
  diagram: GraphPilotDiagram,
  suggestedName: string,
): Promise<{ handle: LocalFileHandle; revision: string } | null> {
  const w = window as unknown as FsaWindow
  if (!w.showSaveFilePicker) return null
  let handle: LocalFileHandle
  try {
    handle = await w.showSaveFilePicker({ ...PICKER_OPTS, suggestedName })
  } catch (error) {
    if (isAbortError(error)) return null
    throw error
  }
  return { handle, revision: await writeHandle(handle, diagram) }
}
