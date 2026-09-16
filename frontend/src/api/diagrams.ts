import type {
  ApiErrorResponse,
  DiagramListResponse,
  DiagramLoadResponse,
  DiagramSaveResponse,
  DiagramSummary,
  DiagramValidateResponse,
  GraphPilotDiagram,
  OperationProblem,
  ValidationErrorDetail,
} from '@/types/diagram'
import { isGraphPilotDiagram } from '@/types/diagram'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '')
const REQUEST_TIMEOUT_MS = 15000

/** Error carrying the backend's shared OperationProblem plus HTTP status. */
export class DiagramApiError extends Error {
  code: string
  status: number
  retryable: boolean
  details?: OperationProblem['details']
  validationErrors?: ValidationErrorDetail[]

  constructor(
    code: string,
    message: string,
    status: number,
    retryable = false,
    details?: OperationProblem['details'],
  ) {
    super(message)
    this.name = 'DiagramApiError'
    this.code = code
    this.status = status
    this.retryable = retryable
    this.details = details
    this.validationErrors = details?.issues
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function invalidResponse(route: string): DiagramApiError {
  return new DiagramApiError('invalid_response', `The GraphPilot API returned an invalid ${route} response.`, 0)
}

function isValidationErrorDetail(value: unknown): value is ValidationErrorDetail {
  return isRecord(value) &&
    typeof value.code === 'string' &&
    typeof value.message === 'string' &&
    (typeof value.path === 'string' || value.path === null)
}

function isOperationProblem(problem: unknown): problem is OperationProblem {
  if (
    !isRecord(problem) ||
    typeof problem.code !== 'string' ||
    typeof problem.message !== 'string' ||
    typeof problem.retryable !== 'boolean' ||
    (problem.details !== undefined && !isRecord(problem.details))
  ) return false
  const issues = problem.details?.issues
  return issues === undefined || (Array.isArray(issues) && issues.every(isValidationErrorDetail))
}

function parseProblem(body: unknown, status: number): DiagramApiError {
  if (!isRecord(body) || !isRecord(body.error)) return invalidResponse('error')
  const response = body as unknown as ApiErrorResponse
  const problem = response.error
  if (!isOperationProblem(problem)) return invalidResponse('error')
  return new DiagramApiError(problem.code, problem.message, status, problem.retryable, problem.details)
}

/** Load a saved diagram via GET /api/diagrams/load. The frontend never reads files directly. */
export async function loadDiagram(diagramPath: string): Promise<DiagramLoadResponse> {
  const url = `${API_BASE_URL}/api/diagrams/load?path=${encodeURIComponent(diagramPath)}`

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(url, { signal: controller.signal })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new DiagramApiError('timeout', `The request to ${API_BASE_URL} timed out.`, 0, true)
    }
    throw new DiagramApiError(
      'network_error',
      `Could not reach the GraphPilot API at ${API_BASE_URL}. Is the backend running?`,
      0,
      true,
    )
  } finally {
    clearTimeout(timeoutId)
  }

  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) throw parseProblem(body, response.status)

  if (!isRecord(body) || typeof body.diagramPath !== 'string' || typeof body.revision !== 'string' || !isGraphPilotDiagram(body.diagram)) {
    throw invalidResponse('load')
  }
  return body as unknown as DiagramLoadResponse
}

/** Save a diagram via POST /api/diagrams/save. The backend validates before
 * overwriting; a blocking validation failure throws a DiagramApiError whose
 * `validationErrors` lists the issues. Workspace-path writes stay backend-owned;
 * picker-opened files use their explicit browser file handle. */
export async function saveDiagram(
  diagramPath: string,
  diagram: GraphPilotDiagram,
  expectedRevision?: string,
): Promise<DiagramSaveResponse> {
  const url = `${API_BASE_URL}/api/diagrams/save`

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ diagramPath, diagram, ...(expectedRevision ? { expectedRevision } : {}) }),
      signal: controller.signal,
    })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new DiagramApiError('timeout', `The request to ${API_BASE_URL} timed out.`, 0, true)
    }
    throw new DiagramApiError(
      'network_error',
      `Could not reach the GraphPilot API at ${API_BASE_URL}. Is the backend running?`,
      0,
      true,
    )
  } finally {
    clearTimeout(timeoutId)
  }

  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) throw parseProblem(body, response.status)

  if (
    !isRecord(body) ||
    body.saved !== true ||
    typeof body.diagramPath !== 'string' ||
    typeof body.revision !== 'string' ||
    !isGraphPilotDiagram(body.diagram) ||
    (body.svgPath !== undefined && typeof body.svgPath !== 'string') ||
    (body.warning !== undefined && !isOperationProblem(body.warning))
  ) throw invalidResponse('save')
  return body as unknown as DiagramSaveResponse
}

/** List diagrams stored under the workspace of `path` via GET /api/diagrams/list.
 * `path` is any diagram path inside the target workspace (the backend derives the
 * `.graphpilot` root from it). Lists canonical `.graphpilot/diagrams/` files only. */
export async function listDiagrams(path: string): Promise<DiagramSummary[]> {
  const url = `${API_BASE_URL}/api/diagrams/list?path=${encodeURIComponent(path)}`

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(url, { signal: controller.signal })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new DiagramApiError('timeout', `The request to ${API_BASE_URL} timed out.`, 0, true)
    }
    throw new DiagramApiError(
      'network_error',
      `Could not reach the GraphPilot API at ${API_BASE_URL}. Is the backend running?`,
      0,
      true,
    )
  } finally {
    clearTimeout(timeoutId)
  }

  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) throw parseProblem(body, response.status)

  if (!isRecord(body) || !Array.isArray(body.diagrams)) throw invalidResponse('list')
  if (!body.diagrams.every((item) => isRecord(item) && typeof item.name === 'string' && typeof item.path === 'string')) {
    throw invalidResponse('list')
  }
  return (body as unknown as DiagramListResponse).diagrams
}

/** Render a diagram to an SVG string via POST /api/diagrams/render (path-free, no
 * write). Backs the editor's "Preview render" comparison: the browser posts the
 * canonical JSON it would save and gets back the backend-rendered SVG so the
 * server-rendered shapes can be compared against the React Flow canvas. */
export async function renderDiagram(diagram: GraphPilotDiagram): Promise<string> {
  const url = `${API_BASE_URL}/api/diagrams/render`

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ diagram }),
      signal: controller.signal,
    })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new DiagramApiError('timeout', `The request to ${API_BASE_URL} timed out.`, 0, true)
    }
    throw new DiagramApiError(
      'network_error',
      `Could not reach the GraphPilot API at ${API_BASE_URL}. Is the backend running?`,
      0,
      true,
    )
  } finally {
    clearTimeout(timeoutId)
  }

  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) throw parseProblem(body, response.status)

  if (!isRecord(body) || typeof body.svg !== 'string' || !body.svg.trim()) throw invalidResponse('render')
  return body.svg
}

/** Validate a diagram via POST /api/diagrams/validate (path-free, no write).
 * Used by the "open any file" flow to validate a file opened from disk before
 * writing it back through a File System Access handle. Returns the validation
 * result plus the normalized diagram the client should write. */
export async function validateDiagram(diagram: GraphPilotDiagram): Promise<DiagramValidateResponse> {
  const url = `${API_BASE_URL}/api/diagrams/validate`

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ diagram }),
      signal: controller.signal,
    })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new DiagramApiError('timeout', `The request to ${API_BASE_URL} timed out.`, 0, true)
    }
    throw new DiagramApiError(
      'network_error',
      `Could not reach the GraphPilot API at ${API_BASE_URL}. Is the backend running?`,
      0,
      true,
    )
  } finally {
    clearTimeout(timeoutId)
  }

  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) throw parseProblem(body, response.status)

  if (
    !isRecord(body) ||
    typeof body.valid !== 'boolean' ||
    !Array.isArray(body.validationErrors) ||
    !body.validationErrors.every(isValidationErrorDetail) ||
    !isGraphPilotDiagram(body.diagram)
  ) throw invalidResponse('validate')
  return body as unknown as DiagramValidateResponse
}
