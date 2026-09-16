# Slice 10: Faithful BDD Block Compartments (render + edit)

> **Status: APPROVED — building Phase A + B.** Decisions locked (see *Open decisions* below):
> ordered `data.compartments: [{label, items[]}]`, free-string items, additive under the open
> `data` (no schema change), keep the standalone `part` box **and** add block `parts`
> compartments, and this pass ships **render + edit** (Phase A + B); generation (Phase C) follows.

## Purpose

Make the SysML **Block Definition Diagram** render and edit faithfully — a `block` (and
`value`/`constraint`/`enumeration`) shows its **labeled compartments** (parts, references,
values, operations, constraints, literals) the way real BDD tools do, on **both** the React
canvas and the SVG export, and those compartments are **editable in the UI** (not just the
node label). This must land **before** the next answer-key authoring pass so the BDD answer
keys can be comprehensive and non-buggy.

## Background

Today every BDD node renders as a single box: a `«stereotype»` + name header over an **empty
body compartment**, and on the canvas **only the label is editable**. So a `block` cannot show
its owned properties/values, an `enumeration` cannot show its literals, and a `constraint`
cannot show its expression. This is the deliberate MVP simplification recorded in
`docs/02-design-and-features/diagram-schemas/bdd-diagram-blueprints.md` (Epic 2 Slice 09
notes it as a follow-up).

### Canonical notation (verified)

SysML 1.6 BDD reuses **UML 2 class-diagram notation** (confirmed against uml-diagrams.org's
class reference, which describes the compartment model; SysML adds the block stereotypes):

- A **block** is a rectangle. **Name compartment** (top): the `«block»` keyword (guillemets)
  above the block **name** (bold, centered).
- Below it, zero or more **feature compartments**, each separated by a horizontal line and
  headed by an *italic compartment label*. SysML block compartments: **parts** (composite
  properties), **references** (shared properties), **values** (value properties),
  **operations**, **constraints**. **Empty compartments are suppressed.**
- Property line syntax: `name : Type [multiplicity] = default` (multiplicity/default optional).
  Operation line: `name(params) : ReturnType`.
- **valueType** (`value`) — `«valueType»` + name; a quantity kind, often with a unit/dimension.
- **enumeration** — `«enumeration»` + name in the name compartment; **literals listed one per
  line** in a compartment below (per the class reference's enumeration rule).
- **constraint block** (`constraint`) — `«constraint»` + name; a **constraints** compartment
  holding the `{boolean/parametric expression}` and (optionally) a **parameters** compartment.
- **part / reference** are strictly *properties inside a block's compartments* (composition /
  aggregation to the typing block, detailed in an IBD). GraphPilot keeps standalone `part`
  boxes as a simplification; this slice keeps that **and** adds the in-block compartments.

## Design

### 1. Data model (the key decision) — store compartments under the open `data` object

`diagram.json`'s `data` is `additionalProperties: true`, so structured compartment content can
be added **with no schema change**. Proposed generic, ordered shape (works for every BDD kind):

```jsonc
"data": {
  "label": "Vehicle",
  "semanticType": "block",
  "compartments": [
    { "label": "parts",  "items": ["engine: Engine", "wheel: Wheel [4]"] },
    { "label": "values", "items": ["mass: kg", "topSpeed: km/h"] }
  ]
}
```

- `compartments` is an **ordered list**; each has a `label` (italic header) + `items` (display
  lines). Order is preserved and authoring is uniform.
- `enumeration` → `[{ "label": "literals", "items": ["RED","GREEN","BLUE"] }]`.
- `constraint` → `[{ "label": "constraints", "items": ["{ power = torque * rpm }"] }]`.
- **No hard schema change.** Optionally add an *optional* `compartments` definition to
  `graphpilot/schemas/diagram.json` for documentation + light validation (see Open decisions).

### 2. Rendering — canvas ↔ SVG parity (must match)

- **SVG** (`backend/services/context/diagram_render_service._draw_bdd_block`): after the name header,
  iterate `data.compartments`; per compartment draw a separator line, the italic label, then
  the item lines via the existing `_fit_text`/`_label` machinery. Suppress empty compartments.
- **Canvas** (`frontend/src/editor/canvas/customNodes.tsx` `BddNode`): mirror it — the header, then a
  stack of labeled compartments in the (currently empty) body div; identical suppression rules.
- **Sizing.** A block's height must fit `header + Σ(compartment label + n items)·lineHeight`.
  Add a shared height heuristic (`backend/services/diagrams/catalog/constants.py`) used by (a) the layout base
  size and (b) the seed-authoring helper, and mirror the per-line height on both renderers so
  the two never disagree. The renderer trusts the saved `height`; the heuristic sets it.

### 3. Editing — property panel compartment editor (the "edit inside the block" ask)

- `frontend/src/editor/components/PropertyPanel.tsx`: for a BDD node, add a **Compartments** editor — add
  / rename / remove a compartment, and add / edit / remove item lines. Writes to
  `data.compartments` through the existing `updateNode` patch path (one undo step per edit).
- **Reverse-adapter change (important).** `reactFlowToGraphPilot` currently rebuilds a loaded
  node's `data` from the **original** loaded diagram and only reads `label` from live state
  (`{ ...orig.data, label }`). To persist compartment edits it must also read
  `data.compartments` from the **live** React Flow node (the same way edge `data.arrow` is read
  back). Round-trip must stay byte-stable when nothing changed.

### 4. Generation + answer keys

- `backend/assets/blueprints/bdd_diagram/prompts.md`: document the compartment model +
  line syntax so generated diagrams use it.
- The LLM logical-diagram contract allows an optional per-node `compartments`; **conform**
  preserves it (it is content, not vocabulary); block sizing is applied post-generation.
- The hand-authored keys (`_seed_examples.py`) can use compartments immediately once render +
  sizing land — this is the piece the user needs before the next authoring pass.

## Phasing (ship incrementally; each phase is independently useful)

- **Phase A — data model + faithful render (gating for answer keys).** `data.compartments`
  shape; SVG `_draw_bdd_block` + canvas `BddNode` render compartments with parity; sizing
  heuristic. Backend render tests + frontend unit tests + a parity check.
- **Phase B — in-UI editing.** Property-panel compartment editor + the reverse-adapter read of
  `data.compartments`; byte-stable round-trip test.
- **Phase C — generation support.** `prompts.md` + conform preservation + (optional) a couple
  of seed keys that exercise compartments end to end.

## Included Work (by area)

- **Backend:** `services/diagrams/rendering/diagram_render_service.py` (`_draw_bdd_block` compartments),
  `services/diagrams/catalog/constants.py` (BDD height heuristic), `services/generation/pipeline/diagram_layout_service.py` (size a
  block to its compartments), `graphpilot/blueprints/bdd_diagram/prompts.md`, and (Phase C)
  the generation conform path. Tests in `tests/core/test_render_service.py`.
- **Frontend:** `editor/canvas/customNodes.tsx` (`BddNode` compartments), `editor/components/PropertyPanel.tsx`
  (compartment editor), `adapters/reactFlow.ts` (read back `data.compartments`). Tests in
  `editor/components/components.test.tsx` + `adapters/reactFlow.test.ts`.
- **Docs:** `diagram-schemas/bdd-diagram-blueprints.md` (replace the "simplified box" note with
  the compartment model), `00-diagram-json-schema.md` (document `data.compartments`),
  `decision-decisions.md` (the data-model decision), `../../00-current-state.md`.

## Not In Scope

- Internal Block Diagram (IBD), ports/interfaceBlocks, `«allocate»`/dependency.
- Structured/typed property validation (items stay free display strings for MVP).
- New node/edge **vocabulary** (this is content + rendering only; the Slice 08/09 vocab stands).
- Auto-layout of compartment contents beyond the height heuristic.

## Open decisions (need sign-off before build)

1. **Data-model shape** — ordered `data.compartments: [{label, items[]}]` (recommended, generic)
   vs. named keys (`data.parts`, `data.values`, …). *Recommendation: ordered list.*
2. **Items: free strings vs. structured** — `"wheel: Wheel [4]"` as one string (recommended,
   simplest for render/edit/authoring) vs. `{name, type, multiplicity, default}` objects
   (enables validation/eval later). *Recommendation: strings now; structure later if eval needs it.*
3. **Schema** — keep compartments purely additive under the open `data` (no schema edit,
   recommended) vs. add an optional `compartments` definition to `diagram.json` for docs +
   light validation. *Recommendation: additive now; document only.*
4. **`part` element** — keep the standalone `«part»` box **and** add block `parts` compartments
   (recommended, back-compatible), or migrate parts to compartments only. *Recommendation: keep both.*
5. **Scope for "now"** — Phase A only (render + data, unblocks answer keys) this pass, with
   B/C to follow, or A+B together (render + editing)? *Recommendation: A+B (editing is the
   explicit ask); C right after.*

## Exit Criteria

- A `block` with parts/values (and an `enumeration` with literals, a `constraint` with an
  expression) renders **identically** on the canvas and in the SVG export, with correct
  compartment separators and suppression of empty compartments.
- Compartment content is editable in the property panel and **round-trips byte-stably**.
- Backend + frontend suites green; `tsc` + `oxlint` clean; a canvas↔export parity check passes.
- `bdd-diagram-blueprints.md` documents the compartment model authors will follow.

## Previous Slice

- `09-comprehensive-node-and-edge-shapes.md`

## Outcome

✅ **Phase A + B delivered** (render + edit). A `block`/`value`/`constraint`/`enumeration`
now shows labeled feature compartments below the name header, drawn identically on the React
canvas and the SVG export (empty compartments suppressed), and editable in the property panel
(add / rename / remove compartments + item lines). Compartments are stored additively under
`data.compartments` (ordered `[{label, items[]}]`, free-string items) — **no schema change**.
Blocks auto-fit their height via a shared helper (`bdd_block_min_height` /
`bddBlockMinHeight`); the reverse adapter reads edited compartments back and drops blank
lines / empty compartments on save, keeping the round-trip byte-stable.

**Changes.** Backend: `diagram_render_service._draw_bdd_block` + `_draw_bdd_compartments`,
`constants.py` (`bdd_block_min_height` + tunables). Frontend: `types/diagram.ts`
(`BddCompartment` + `data.compartments`), `editor/canvas/customNodes.tsx` (`BddNode` compartment
stack), `editor/lib/bddCompartments.ts` (height helper), `editor/components/PropertyPanel.tsx`
(`CompartmentsEditor` + NodePatch), `editor/lib/nodePatch.ts` (apply + auto-fit),
`adapters/reactFlow.ts` (`normalizeCompartments` + read-back). Docs: bdd blueprint, schema
doc, decision log, current-state.

**Verification.** Backend `manage.py test` → **360 passed** (render + suppression + height
helper tests); frontend `vitest` → **246 passed** (compartment round-trip + blank-line
cleanup); `tsc --noEmit` clean; `oxlint` 0 errors.

**Deviations / follow-ups.** Item lines are free display strings (no typed-property
validation). **Phase C** (generation `prompts.md` + conform emitting compartments, and seed
keys that exercise them) is the remaining follow-up — decoupled from this pass because the
next answer-key authoring can use the editor's auto-fit or the `bdd_block_min_height` helper
directly.
