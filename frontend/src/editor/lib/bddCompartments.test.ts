import { describe, expect, it } from 'vitest'
import type { ModelFeatures } from '@/types/diagram'
import { featureBlockMinHeight, featureBlockMinSize, featureCompartments } from './bddCompartments'

describe('featureCompartments', () => {
  it('returns no display compartments for absent or empty features', () => {
    expect(featureCompartments(undefined)).toEqual([])
    expect(featureCompartments(null)).toEqual([])
    expect(featureCompartments({})).toEqual([])
    expect(
      featureCompartments({
        properties: [],
        operations: [],
        receptions: [],
        constraints: [],
        literals: [],
      }),
    ).toEqual([])
  })

  it('groups properties by kind in first-seen order and preserves item order', () => {
    const features: ModelFeatures = {
      properties: [
        { kind: 'value', name: ' mass ', type: ' kg ' },
        { kind: 'part', name: ' engine ', type: ' Engine ' },
        { kind: 'value', name: ' speed ', type: ' m/s ' },
        { kind: 'reference', name: ' driver ', type: ' Person ' },
        { kind: 'part', name: ' wheels ', type: ' Wheel ' },
      ],
    }

    expect(featureCompartments(features)).toEqual([
      { label: 'value properties', items: ['mass: kg', 'speed: m/s'] },
      { label: 'part properties', items: ['engine: Engine', 'wheels: Wheel'] },
      { label: 'reference properties', items: ['driver: Person'] },
    ])
  })

  it('formats flow direction, type, multiplicity, and defaults like the backend', () => {
    const features: ModelFeatures = {
      properties: [
        {
          kind: 'flow',
          direction: 'inout',
          name: ' coolant ',
          type: ' Fluid ',
          multiplicity: { lower: 0, upper: '*' },
          default: false,
        },
        {
          kind: 'value',
          name: 'count',
          type: 'Integer',
          multiplicity: { lower: 1, upper: 1 },
          default: 0,
        },
        {
          kind: 'value',
          name: 'range',
          multiplicity: { lower: 2, upper: 5 },
          default: '',
        },
        { kind: 'flow', name: 'untyped' },
      ],
    }

    expect(featureCompartments(features)).toEqual([
      {
        label: 'flow properties',
        items: ['inout coolant: Fluid [0..*] = False', 'untyped'],
      },
      {
        label: 'value properties',
        items: ['count: Integer [1] = 0', 'range [2..5] = '],
      },
    ])
  })

  it('uses Python-style spelling for structured JSON defaults', () => {
    const features: ModelFeatures = {
      properties: [
        {
          kind: 'value',
          name: 'settings',
          default: { enabled: true, names: ['primary', null], retries: 2 },
        },
      ],
    }

    expect(featureCompartments(features)).toEqual([
      {
        label: 'value properties',
        items: ["settings = {'enabled': True, 'names': ['primary', None], 'retries': 2}"],
      },
    ])
  })

  it('appends operations, receptions, constraints, and literals in backend order', () => {
    const features: ModelFeatures = {
      properties: [{ kind: 'part', name: ' engine ', type: ' Engine ' }],
      operations: [
        {
          name: ' start ',
          parameters: [{ name: 'mode', direction: 'in', type: 'Mode' }],
          returnType: 'Boolean',
        },
        { name: ' stop ' },
      ],
      receptions: [' started ', ' stopped '],
      constraints: [
        { name: 'positiveMass', expression: ' mass > 0 ' },
        { expression: ' speed <= limit ' },
      ],
      literals: [' PARK ', ' DRIVE '],
    }

    // `g6`. An operation used to draw as `start()` and a constraint as its bare
    // expression, so `parameters`, `returnType` and a constraint's `name` were accepted,
    // saved, and invisible — the author believes they were recorded and a reader never
    // sees them. UML writes the signature and braces the constraint name.
    expect(featureCompartments(features)).toEqual([
      { label: 'part properties', items: ['engine: Engine'] },
      { label: 'operations', items: ['start(mode: Mode): Boolean', 'stop()'] },
      { label: 'receptions', items: ['started', 'stopped'] },
      { label: 'constraints', items: ['{positiveMass} mass > 0', 'speed <= limit'] },
      { label: 'literals', items: ['PARK', 'DRIVE'] },
    ])
  })

  it('renders a parameter left as a plain string by a hand-edited file', () => {
    // The type says a canonical parameter is an object, and the backend converts the
    // draft's string form on the way in — so this cast is deliberate. A `.gp.json` is a
    // file on someone's disk that they may well edit, and drawing `start()` because a
    // parameter was a string rather than an object would silently lose their work.
    const handEdited = {
      operations: [{ name: 'start', parameters: ['mode: Mode'] }],
    } as unknown as ModelFeatures

    expect(featureCompartments(handEdited)).toEqual([
      { label: 'operations', items: ['start(mode: Mode)'] },
    ])
  })

  it('suppresses blank names and empty feature groups', () => {
    const features: ModelFeatures = {
      properties: [
        { kind: 'value', name: '' },
        { kind: 'part', name: '   ' },
        { kind: 'value', name: 'mass' },
      ],
      operations: [{ name: '' }, { name: '   ' }],
      receptions: ['', '   '],
      constraints: [{ expression: '' }, { expression: '   ' }],
      literals: ['', '   '],
    }

    expect(featureCompartments(features)).toEqual([
      { label: 'value properties', items: ['mass'] },
    ])
  })

  it('defensively ignores malformed collections and entries at runtime', () => {
    const malformed = {
      properties: [5, null, {}, { kind: 'part', name: 'engine', multiplicity: 'many' }],
      operations: [5, 'start', {}, { name: 'run' }],
      receptions: 'started',
      constraints: [false, {}, { expression: 'valid' }],
      literals: null,
    } as unknown as ModelFeatures

    expect(featureCompartments(malformed)).toEqual([
      { label: 'part properties', items: ['engine'] },
      { label: 'operations', items: ['run()'] },
      { label: 'constraints', items: ['valid'] },
    ])
  })
})

describe('featureBlockMinHeight', () => {
  it('uses the compact backend minimum for absent, empty, or suppressed features', () => {
    expect(featureBlockMinHeight(undefined)).toBe(48)
    expect(featureBlockMinHeight({})).toBe(48)
    expect(featureBlockMinHeight({ properties: [{ kind: 'value', name: '   ' }] })).toBe(48)
  })

  it('keeps the existing filled-classifier minimum when content is shorter', () => {
    expect(featureBlockMinHeight({ properties: [{ kind: 'value', name: 'mass' }] })).toBe(90)
  })

  it('counts one label line and every item line for each non-empty compartment', () => {
    const features: ModelFeatures = {
      properties: [
        { kind: 'part', name: 'a' },
        { kind: 'part', name: 'b' },
        { kind: 'part', name: 'c' },
        { kind: 'part', name: 'd' },
      ],
    }

    // 34px header, then the compartment as the renderer draws it: its first baseline
    // sits FONT_SIZE + 2 below the top, then a line each for the heading and the four
    // items. Plus 6px so the last row's descender is inside the box.
    // 34 + (12 + 2 + 5 * 14.4) + 6 = 126.
    expect(featureBlockMinHeight(features)).toBeCloseTo(126)
  })

  it('matches the backend compact content-fit size', () => {
    expect(featureBlockMinSize('Vehicle', {})).toEqual({ width: 190, height: 48 })
    expect(featureBlockMinSize('Vehicle', {
      properties: [{ kind: 'value', name: 'aVeryLongPropertyNameThatNeedsMoreWidth', type: 'kg' }],
    })).toEqual({ width: 320, height: 90 })
  })

  it('adds padding and a label line independently for every derived group', () => {
    const features: ModelFeatures = {
      properties: [
        { kind: 'part', name: 'engine' },
        { kind: 'value', name: 'mass' },
      ],
      operations: [{ name: 'start' }],
      receptions: ['started'],
      constraints: [{ expression: 'mass > 0' }],
      literals: ['PARK'],
    }

    // Six groups, each with one item: 34 + 6 * (12 + 2 + 2 * 14.4) + 6 = 296.8.
    expect(featureBlockMinHeight(features)).toBeCloseTo(296.8)
  })

  it('agrees with the backend, which agrees with what the renderer draws', () => {
    // The two used to be worked out separately and drifted by 8px per compartment, so a
    // block with three of them lost its last line off the bottom edge.
    const perCompartment = (items: number) => 12 + 2 + (1 + items) * 14.4
    const features: ModelFeatures = {
      properties: [{ kind: 'value', name: 'a' }, { kind: 'value', name: 'b' }],
      operations: [{ name: 'run' }],
      constraints: [{ expression: 'a > 0' }],
    }

    expect(featureBlockMinHeight(features)).toBeCloseTo(
      34 + perCompartment(2) + perCompartment(1) + perCompartment(1) + 6,
    )
  })
})
