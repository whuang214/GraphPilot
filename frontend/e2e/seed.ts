import { randomUUID } from 'node:crypto'
import { cpSync, mkdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const blueprintRoot = join(here, '..', '..', 'backend', 'assets', 'blueprints')
const runRoot = join(tmpdir(), `graphpilot-e2e-${randomUUID()}`)

function seedFrom(source: string, destination: string): string {
  const dir = join(runRoot, '.graphpilot', 'diagrams')
  mkdirSync(dir, { recursive: true })
  const dest = join(dir, `${destination}.gp.json`)
  cpSync(source, dest)
  return dest
}

// The curated pool is `answers`. It was called `eval` until the gallery was reorganised
// into answers / generated / training, and this line kept the old name — so every e2e
// test that seeds a committed diagram has failed with ENOENT ever since, and nobody
// noticed because the suite was not re-run. Twelve of forty-three.
function seedFixture(diagramType: string, name: string, destination: string): string {
  return seedFrom(join(blueprintRoot, diagramType, 'examples', 'answers', name, 'output.gp.json'), destination)
}

// Seed throwaway workspace diagrams under the OS temp dir. Re-seeding restores
// pristine committed examples after save/edit tests overwrite a destination.
//
// The activity smoke seed is a dedicated e2e fixture rather than a curated backend
// example: 26 assertions in smoke.spec.ts read its exact labels and topology, so it
// must be stable against churn in the example pool. Adapter round-trip drift is
// covered separately, against all 36 real examples, in reactFlow.test.ts.
export function seedDiagram(): string {
  return seedFrom(join(here, 'fixtures', 'device-repair-assessment.gp.json'), 'smoke')
}

export function seedBddDiagram(): string {
  return seedFixture('bdd_diagram', '01-spacecraft', 'bdd-smoke')
}

export function seedUseCaseDiagram(): string {
  return seedFixture('use_case_diagram', '04-airline-booking', 'use-case-smoke')
}

export const authorableNodeFixtures = [
  { semanticType: 'initialNode', width: 90, height: 60 },
  { semanticType: 'opaqueAction', width: 160, height: 60 },
  { semanticType: 'decisionNode', width: 140, height: 80 },
  { semanticType: 'mergeNode', width: 120, height: 50 },
  { semanticType: 'forkNode', width: 120, height: 30 },
  { semanticType: 'joinNode', width: 120, height: 30 },
  { semanticType: 'activityFinalNode', width: 90, height: 60 },
  { semanticType: 'note', width: 160, height: 80 },
  { semanticType: 'actor', width: 90, height: 120 },
  { semanticType: 'useCase', width: 200, height: 70 },
  { semanticType: 'subject', width: 320, height: 240 },
  { semanticType: 'block', width: 180, height: 90 },
  { semanticType: 'class', width: 140, height: 60 },
  { semanticType: 'interface', width: 140, height: 60 },
  { semanticType: 'component', width: 140, height: 60 },
  { semanticType: 'package', width: 320, height: 240 },
  { semanticType: 'requirement', width: 140, height: 60 },
] as const

export function seedAuthorableDiagram(): string {
  const dir = join(runRoot, '.graphpilot', 'diagrams')
  mkdirSync(dir, { recursive: true })
  const dest = join(dir, 'all-authorable.gp.json')
  const nodes = authorableNodeFixtures.map((fixture, index) => ({
    id: `audit-${fixture.semanticType}`,
    type: 'gpNode',
    position: { x: 80 + (index % 5) * 360, y: 80 + Math.floor(index / 5) * 280 },
    width: fixture.width,
    height: fixture.height,
    data: { label: `Audit ${fixture.semanticType}`, semanticType: fixture.semanticType },
  }))
  writeFileSync(dest, JSON.stringify({
    schemaVersion: 'graphpilot.diagram.v1',
    kind: 'diagram',
    diagramType: 'custom',
    id: 'all-authorable-audit',
    name: 'All Authorable Nodes',
    metadata: {},
    viewport: { x: 0, y: 0, zoom: 1 },
    nodes,
    edges: [],
  }, null, 2))
  return dest
}
