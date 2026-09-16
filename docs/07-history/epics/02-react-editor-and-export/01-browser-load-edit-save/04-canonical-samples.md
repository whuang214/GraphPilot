# Slice 04: Canonical Samples

## Purpose

Confirm and finalize the three canonical sample diagrams for the MVP diagram types by exercising the real React Flow load → edit → save round-trip.

## Included Work

- author or refine the canonical sample diagrams for:
  - `activity_diagram`
  - `use_case_diagram`
  - `bdd_diagram`
- use the React Flow adapter and save API to confirm the persisted JSON shape
- update the canonical schema and mapping docs if the round-trip exposes gaps
- update the provisional Epic 1 blueprints if necessary
- place the confirmed samples in `backend/assets/blueprints/<type>/examples/sample.gp.json`

## Not In Scope

- new diagram types beyond the three MVP types
- generation or update workflows
- MCP tool implementation

## Target Areas

- `frontend/` adapter and editor round-trip
- `backend/assets/blueprints/<type>/examples/`
- `docs/02-design-and-features/00-diagram-json-schema.md`
- `docs/02-design-and-features/01-diagram-json-mapping-design.md`

## Exit Criteria

- all three sample diagrams exist as stable fixtures
- each sample loads in the editor and round-trips through save without data loss
- the canonical schema is updated to reflect the confirmed shape
- the Epic 1 blueprints are updated if needed

## Previous Slice

- `03-frontend-editing-and-save.md`

## Next Slice

- `../02-renderers-and-samples/05-node-shapes.md`

## Outcome

✅ Completed as planned (plus an adapter fix and automated round-trip coverage). Finalized the three canonical samples and confirmed the React Flow round-trip.

**Delivered.**

- Samples: authored `backend/assets/blueprints/<type>/examples/sample.gp.json` for `activity_diagram`, `use_case_diagram`, and `bdd_diagram` — concrete ids, inline styles from the blueprint defaults, declared sizes, `metadata.blueprintKey`, and labels only where meaningful.
- Round-trip confirmation (automated): added **Vitest** (`frontend` dev dep + `npm run test`) with `frontend/src/adapters/reactFlow.test.ts`, which proves each sample shape round-trips `graphPilotToReactFlow → reactFlowToGraphPilot` without data loss and that injected React Flow runtime fields (`selected`, `dragging`, `measured`, `positionAbsolute`, measured width/height) are stripped.
- Adapter fix (round-trip-driven): `reactFlowToGraphPilot()` no longer falls back to `rf.width`/`rf.height` (React Flow's measured runtime dimensions); size comes from the edited style or the original only, so measured dimensions cannot leak into saved JSON.
- Backend test: `backend/tests/generation/test_samples.py` asserts each sample exists, is schema-valid, passes `DiagramValidationService` with no blocking errors, and is canonically normalized (no empty labels / no runtime fields).
- Schema confirmed: lifted the "provisional" status in `backend/assets/schemas/diagram.json`, `docs/02-design-and-features/00-diagram-json-schema.md`, and `01-diagram-json-mapping-design.md`; no structural schema change was needed. Recorded the two findings (empty edge labels omitted; sizes are declared intent, not measured).
- Seed alignment: `samples/diagrams/activity_diagram.gp.json` mirrored the canonical activity sample (previously had empty-string edge labels); `samples/README.md` updated. *(Update: the repo-root `samples/` folder was retired in Slice 07 — seed the browser demo directly from a backend `examples/<name>/output.gp.json`.)*

**Deviations.** the `use_case_diagram` sample's `systemBoundary` is intentionally a disconnected container node, which yields a non-blocking advisory `disconnected_node` warning (validation still passes). The Vitest test validates the adapter against simulated React Flow output; a faithful browser E2E (Playwright) is backlogged.

**Verification.** backend `python manage.py test` (incl. `tests/generation/test_samples.py`); frontend `npm run test` (6 round-trip checks), `npm run build`, `npm run lint` all pass.

**Follow-up.** Slice 05 — type-specific node shapes (begins the folded-in editor-rendering + answer-key sample work, S05-S08).
