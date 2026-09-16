# Slice 08: Comprehensive Sample Library

## Purpose

Author 4–6 comprehensive examples per MVP diagram type, each as a `prompt.md` + `output.gp.json` pair, so the sample library covers realistic scenarios and exercises the full semantic surface of each diagram type. These become the answer keys for the (pending) generation eval.

## Background

- A single sample per type is not enough coverage to validate generation quality or to seed a future example/RAG library (Epic 5).
- Authoring rich samples is only meaningful once the editor renders type-specific visuals and containment (Slice 05) — otherwise the samples cannot be visually confirmed.
- The examples must demonstrate, not just be valid: each diagram type's semantic types and edge semantics should appear across the set.

## Coverage target

- **4–6 examples per type** (~12–18 total), ordered from simple to comprehensive, e.g.:
  - `activity_diagram`: linear flow; branch with `decision`/`merge`; loop/retry; multi-branch workflow; flow with `note`s.
  - `use_case_diagram`: single actor + use cases; multiple actors; `include`/`extend` relationships; `systemBoundary` containment (nested use cases); actor generalization.
  - `bdd_diagram`: simple block + parts; composition hierarchy; generalization; `value` / `constraint` properties; multi-block system.
- Each example must:
  - be authored against the Slice 05 renderers (visually confirmed in `/editor`),
  - round-trip load → save with no data loss,
  - be schema-valid and pass `DiagramValidationService` with no blocking errors,
  - have a `prompt.md` that plausibly describes the diagram a user would request.

## Planned examples (per type)

Ordered simple → comprehensive. `01` is the migrated minimal sample; `02-order-fulfillment` is the comprehensive model authored in Slice 07. Remaining folders are authored here (names are stable slugs):

- `activity_diagram/examples/`
  - `01-basic-approval` ✅ migrated
  - `02-order-fulfillment` ✅ model — branch + retry loop + merge + note
  - `03-…` multi-branch triage (several decision paths)
  - `04-…` flow with parallel actions rejoining at a merge
  - `05-…` (optional) flow annotated with notes
- `use_case_diagram/examples/`
  - `01-order-system` ✅ migrated — actor + boundary containment + include
  - `02-…` multiple actors + `extend`
  - `03-…` deeper `systemBoundary` containment (several nested use cases)
  - `04-…` actor generalization
- `bdd_diagram/examples/`
  - `01-vehicle` ✅ migrated — composition + generalization
  - `02-…` composition hierarchy with multiple `part`s
  - `03-…` `value` / `constraint` properties
  - `04-…` multi-block system using `reference`

Examples are canonical **answer keys** and do **not** carry the `metadata.authoring` marker (that is a runtime save/generate concern, not part of the stored answer key).

## Authoring workflow (diagram-first, prompt-second)

The existing canonical samples are intentionally minimal and are **not** sufficient coverage; this slice replaces/augments them with comprehensive examples authored in the React editor (Slices 05–06). Each example is built **diagram-first, then the prompt is written to match it**:

1. **Build the comprehensive diagram** in `/editor` — drag shapes from the palette, connect, label, size/position for a clean layout. Deliberately cover the type's full semantic surface (every node `semanticType` + every edge semantic for that type; use `parentId` containment where relevant).
2. **Visually confirm** it renders correctly (shapes, containment, markers).
3. **Save** the canonical JSON to `examples/<name>/output.gp.json`.
4. **Write `examples/<name>/prompt.md`** — the prompt that should generate it, the generation inputs, and what it demonstrates.
5. **Validate** — backend `test_samples` (schema-valid, no blocking errors, canonically normalized) + the frontend round-trip (no data loss).
6. **Repeat**, simple → comprehensive, ~4–6 per type.

`prompt.md` format:

```md
# <example name> — <diagram type>

## Prompt
<the natural-language request that should produce this diagram>

## Generation inputs
- diagramType: <type>
- style: <optional intent>

## Should demonstrate
- <semantic coverage / requirements>
```

> **Scope boundary:** `prompt.md` is the answer-key pairing for Epic 2 (the request + generation inputs + coverage). The richer format that mirrors exactly what `diagram_generate` receives (full tool inputs + the prompt assembly from `prompts.md` + type profile + example few-shots) is an **Epic 3** concern and is intentionally not encoded here yet.

> Authoring friction (MVP): there is no blank-canvas/new-file flow yet, so an example is authored by opening a starter file via `?diagramPath=`, building it out, saving, then placing the result under `examples/<name>/`. A backend `create`/save-new endpoint (deferred) would make this a true "New diagram" flow.

## Included Work

- Author the `prompt.md` + `output.gp.json` pairs per type under the Slice 07 folder layout.
- Visually confirm each `output.gp.json` in `/editor` (renders as intended; containment correct; edge semantics correct).
- Extend `backend/tests/generation/test_samples.py` to validate **every** example (schema-valid, no blocking errors, canonically normalized — no empty labels, no runtime fields).
- Ensure the frontend round-trip test continues to cover all examples (it discovers them via the Slice 07 glob).
- Record any semantic-type or edge-semantic coverage decisions (e.g. how `extend` vs `include` are represented) in the diagram-schema notes if they clarify authoring rules.

## Not In Scope

- The generation eval harness / LLM judge (pending redesign).
- `diagram_generate` / `diagram_render` implementation (later Epic 3 slices).
- New diagram types beyond the three MVP types.
- New canonical schema fields or new supported style keys.

## Target Areas

- `backend/assets/blueprints/<type>/examples/<name>/` (new example pairs)
- `backend/tests/generation/test_samples.py`
- `frontend/src/adapters/reactFlow.test.ts` (coverage only; glob already updated in Slice 07)
- `docs/02-design-and-features/diagram-schemas/*.md` (authoring/coverage notes if needed)
- `docs/02-design-and-features/01-diagram-json-mapping-design.md` (semantic-type coverage if clarified)

## Exit Criteria

- Each MVP type has 4–6 example pairs; every `output.gp.json` is schema-valid, passes shared validation with no blocking errors, and is canonically normalized.
- Each example renders as intended in `/editor` (type-specific visuals + containment).
- Every example round-trips load → save without data loss.
- The example set demonstrably covers each type's semantic node types and edge semantics.
- `python manage.py test`, `npm run test`, `npm run build`, and `npm run lint` pass.

## Previous Slice

- `07-sample-layout.md`

## Next Slice

- End of the `02-renderers-and-samples/` group. Next: `../03-comprehensive-shapes/09-comprehensive-node-and-edge-shapes.md`. (These answer keys also unblock **Epic 3**; its generation eval harness — pending redesign — will consume them, see `../../03-mcp-generation-and-wrappers/00-epic.md`.)

## Outcome

✅ Completed as planned (4 examples per type; visual confirmation is the reviewer's manual step).

**Delivered.** Each MVP type now has **4** prompt + output answer-key pairs (12 total), ordered simple → comprehensive:

- `activity_diagram`: `01-basic-approval`, `02-order-fulfillment` (branch + retry loop + merge + note), `03-document-review-loop` (revision loop rejoining at a merge), `04-incident-triage` (nested decisions → shared merge).
- `use_case_diagram`: `01-order-system`, `02-library-system` (2 actors, include + extend), `03-atm-services` (shared `include`d Authenticate), `04-helpdesk` (include + extend). All nest use cases in a `systemBoundary` via `parentId`.
- `bdd_diagram`: `01-vehicle`, `02-computer-system` (composition hierarchy), `03-thermostat` (`value` + `constraint` via composition/reference), `04-vehicle-family` (generalization + composition + reference, multi-block).

Each example is authored within its type's vocabulary (`test_contracts` enforces this), is schema-valid, passes `DiagramValidationService` with no blocking errors, is canonically normalized, and round-trips losslessly. The frontend round-trip test now exercises **every** example (not one per type).

**Deviations.**

- Authored **4 per type** (the lower bound of the 4–6 target); a 5th/6th can be added later with the same workflow.
- Examples carry no `metadata.authoring` marker (they are stored answer keys, not UI saves).
- "Actor generalization" from the original coverage sketch was dropped: the `use_case` type profile's allowed edges are `association`/`include`/`extend` only (no `generalization`), so using it would violate the vocabulary. Revisit only if the profile is widened.
- **Visual confirmation in `/editor` is the reviewer's manual step** (the harness validates structure/round-trip but not the rendered look).

**Verification.** `python manage.py test` (142 OK — `test_samples` validates all 12, `test_contracts` checks profile conformance), `npm run test` (40 passed), `npm run build`, `npm run lint` (0/0).

**Follow-up.** The eval harness that consumes these answer keys is pending redesign (post-MVP).
