# Slice 07: Per-Example Sample Layout

## Purpose

Move from a single canonical sample per type to a per-example folder layout where each example pairs a **prompt** (the natural-language request) with an **output** (the expected canonical GraphPilot diagram). This turns the sample library into a set of generation "answer keys" without yet authoring new content or wiring generation.

## Background

- Today each MVP type has exactly one canonical sample at `backend/assets/blueprints/<type>/examples/sample.gp.json`.
- The user wants each example isolated in its own folder, with the prompt that should produce it stored alongside the expected output, so the pair can later serve as a generation answer key (for the pending generation eval).
- The single-sample paths are referenced in several places that must be updated together so nothing breaks.

## Blueprint Retirement (folded-in scope)

Decided during Slice 06 review: the per-type `default.json` **blueprints are retired** in favour of the example library + a per-type prompts file. Rationale: nothing in production code loads `default.json` (only `test_contracts.py` checks its shape); its `promptGuidance` and starter graph are redundant with `prompt.md` + `output.gp.json` examples, which is the RAG-style context the generator (Epic 3) and the pending eval will actually use.

Folded-in work for this slice:

- **Delete** `backend/assets/blueprints/<type>/default.json` (all three).
- **Add** a per-type `backend/assets/blueprints/<type>/prompts.md` carrying the former `promptGuidance` (layout hint + required rules) as plain prose for the generator/LLM.
- **Update `backend/tests/contracts/test_contracts.py`** — stop loading `default.json`; assert the new `prompts.md` + at least one example pair exist and that examples are schema-valid.
- **Keep the type profiles** (`backend/services/diagrams/catalog/diagram_types.py`) as the canonical per-type vocabulary; they stay **advisory-only** (mixed/generic-shape diagrams are not blocked and produce only non-surfaced advisory warnings — not relaxed for now). `expected_blueprint_key_prefix` and `metadata.blueprintKey` are kept as a harmless advisory tag to limit blast radius.
- **No schema change for `parentId`** — containment is already part of the canonical node schema (`schemas/diagram.json`); nothing to add.
- **Stamp the authoring marker on UI save** — the UI save path (`DiagramPersistenceService` / `/api/diagrams/save`) sets `metadata.authoring = "custom"` as an informational provenance marker (strictness is decided by `diagramType`, not `authoring` — see `decision-decisions.md`). No schema change (`metadata` is an open object). This makes a UI save no longer a pure no-op (it sets the marker); update `test_persistence_service.py` / `test_api.py` accordingly.
- **Docs**: rewrite/supersede `04-generation-design.md` to the "examples + prompts.md" design, log the retirement + authoring-mode decisions in `decision-decisions.md`, and update `00-development-environment.md` + this epic's docs where blueprints are referenced.

The rest of the slice (per-example `examples/<name>/{prompt.md, output.gp.json}` layout + migration + glob/test updates) is unchanged from the original plan below.

## Target layout

```text
backend/
  graphpilot/
    blueprints/
      <type>/
        default.json                 # blueprint template (unchanged)
        examples/
          <example-name>/
            prompt.md                 # the prompt that should generate this diagram
            output.gp.json            # the expected canonical GraphPilot diagram
```

- `<example-name>` is a stable, ordered, kebab/numeric slug (e.g. `01-basic-approval`).
- `prompt.md` records the natural-language prompt, the `diagramType`, and any optional `style` intent — the inputs a future `diagram_generate` call would receive.
- `output.gp.json` is the canonical, schema-valid expected diagram (the answer key).

## Included Work

- Define and document the per-example folder contract (`prompt.md` + `output.gp.json`) in the blueprint design doc.
- Migrate each existing `examples/sample.gp.json` into a first example folder (e.g. `examples/01-<name>/output.gp.json`) and author its `prompt.md` to match the existing diagram content.
- Update every reference to the old single-sample path:
  - `backend/tests/generation/test_samples.py` — discover examples under `<type>/examples/*/output.gp.json` instead of a fixed `sample.gp.json`.
  - `frontend/src/adapters/reactFlow.test.ts` — update the Vite glob to `.../blueprints/*/examples/*/output.gp.json`.
  - **Retire the repo-root `samples/` folder** (`samples/README.md` + `samples/diagrams/`): it only duplicated the activity example as a browser-demo seed. The backend `examples/` are the single source of truth; the demo-seed step now copies directly from an `examples/<name>/output.gp.json` (documented in `frontend/README.md`).
- Update docs that describe the old layout:
  - `docs/02-design-and-features/04-generation-design.md` (folder structure section)
  - `docs/03-development-and-delivery/epics/02-react-editor-and-export/01-browser-load-edit-save/04-canonical-samples.md` (note the layout evolved; do not rewrite history)
  - `docs/02-design-and-features/diagram-schemas/README.md`
- Log the layout decision in `docs/02-design-and-features/decision-decisions.md`.

## Not In Scope

- Authoring new comprehensive samples (Slice 08) — this slice only migrates the existing three.
- The generation eval harness and LLM judge (pending redesign).
- Custom renderer work (Slice 05) and canvas-authoring / reverse-direction work (Slice 06).
- Any change to the canonical diagram schema or the blueprint `default.json` templates.

## Target Areas

- `backend/assets/blueprints/<type>/examples/` (new folder layout + migrated content)
- `backend/tests/generation/test_samples.py`
- `frontend/src/adapters/reactFlow.test.ts`
- `samples/` (retired) and `frontend/README.md` (relocated demo-seed instructions)
- `docs/02-design-and-features/04-generation-design.md`
- `docs/02-design-and-features/diagram-schemas/README.md`
- `docs/02-design-and-features/decision-decisions.md`
- `docs/03-development-and-delivery/epics/02-react-editor-and-export/01-browser-load-edit-save/04-canonical-samples.md`

## Exit Criteria

- Each MVP type has at least one example folder with both `prompt.md` and `output.gp.json`.
- `output.gp.json` files are schema-valid and pass `DiagramValidationService` with no blocking errors (parity with the prior canonical samples).
- `backend/tests/generation/test_samples.py` discovers and validates examples under the new layout.
- `frontend/src/adapters/reactFlow.test.ts` round-trips every `output.gp.json` under the new glob without data loss.
- `python manage.py test`, `npm run test`, `npm run build`, and `npm run lint` pass.
- All docs referencing the old `examples/sample.gp.json` path are updated and consistent.

## Previous Slice

- `06-canvas-authoring.md`

## Next Slice

- `08-sample-library.md`

## Outcome

✅ Completed as planned. The per-type fixtures are restructured into the per-example answer-key layout, and the unused `default.json` blueprints are retired.

**Delivered.**

- Restructured each type's fixtures into `examples/<name>/{prompt.md, output.gp.json}`, migrating the three existing samples with `git mv` (`activity_diagram/01-basic-approval`, `bdd_diagram/01-vehicle`, `use_case_diagram/01-order-system`) and authoring a `prompt.md` for each.
- Retired the unused per-type `default.json` blueprints (all three) in favour of a per-type `prompts.md` (the former `promptGuidance` as prose) plus the examples library as the RAG/few-shot generation context. The type profile (`backend/services/diagrams/catalog/diagram_types.py`) stays the per-type vocabulary.
- Stamped `metadata.authoring = "custom"` on the UI save path (`_stamp_custom_authoring` in `backend/api/views.py`, shared by `/api/diagrams/save` and `/api/diagrams/validate`) — an informational provenance marker (strictness is decided by `diagramType`, not `authoring` — see `decision-decisions.md`). No schema change (`metadata` is an open object).
- Retired the repo-root `samples/` demo-seed folder; the browser demo now seeds directly from a backend `examples/<name>/output.gp.json` (see `frontend/README.md`).
- Updated `test_contracts.py` / `test_samples.py` / `test_api.py` and the frontend example glob (`frontend/src/adapters/reactFlow.test.ts`); synced the blueprint-design, Epic 3/4, and decision docs.

**Deviations.** A comprehensive `activity_diagram` example (`02-order-fulfillment` — decision branches, retry loop, merge, note) was authored here as the diagram-first template, slightly ahead of the bulk comprehensive authoring in Slice 08.

**Verification.** `python manage.py test` passes (151 tests); the contract/sample/API suites were migrated to the new layout and the frontend round-trip glob discovers every `examples/*/output.gp.json`.

**Follow-up.** Slice 08 — author the remaining comprehensive answer-key examples (4-6 per type) against the new layout.
