# Slice 09: Vocabulary Docs and Cleanup

## Purpose

Finish the collapse: rewrite the standard's shape/vocabulary sections to the base + stereotype model,
refresh cross-cutting status docs, apply the naming cleanup deferred from Slice 07, and run the full
end-to-end verification.

## Background

- Slices 07–08 land the behavior (backend + editor). This slice makes the design docs match, does the
  rename churn in one pass (kept out of the earlier slices to keep their diffs focused), and closes
  out the epic.

## Included Work

- **Schema doc** `00-diagram-json-schema.md`: rewrite §4 (primitives → base elements), §5/§6 headers,
  and §7 so the classifier + dependency families read as one base each + a stereotype vocabulary;
  align the §8/§15 examples.
- **Status docs**: `../../00-current-state.md` (Epic 1's `04-universal-vocabulary` group reopened + delivered S07–S09), the epic
  `00-group.md` slice plan, and the `07/08/09` slice `## Outcome` sections.
- **Renames** (deferred from S07): `_draw_bdd_block` → `_draw_classifier`,
  `bdd_block_min_height`/`_min_size` → `classifier_*`, and the frontend `bddCompartments.ts`
  counterparts — mechanical, behavior-preserving.
- **Final verification** (below) + flag the operator generation re-eval.

## Not In Scope

- Any behavior change (that is Slices 07–08). New diagram types; a real `package` container.

## Target Areas

- `docs/02-design-and-features/00-diagram-json-schema.md` + `diagram-schemas/`
- `docs/03-development-and-delivery/epics/00-current-state.md` + `01-local-diagram-foundation/04-universal-vocabulary/00-group.md`
- `backend/services/diagrams/rendering/diagram_render_service.py`, `backend/services/diagrams/catalog/constants.py`, `frontend/src/editor/lib/bddCompartments.ts` (renames)

## Exit Criteria

- The standard describes one `classifier` + one `dependency` base with a stereotype vocabulary; no
  stale per-kind element rows.
- Full re-verify green: `cd backend; python manage.py test`; `cd frontend; npm run verify`; gallery
  re-rendered and reviewed.
- The operator generation re-eval (needs the Azure key) is flagged as the one follow-up to run.

## Previous Slice

- `08-reusable-shapes-editor.md`

## Next Slice

- `10-answer-key-generation.md` — regenerate the whole answer-key library (training + eval) on the
  reusable-shapes vocabulary, with richer variety + stereotype coverage + valid edge cases.

## Outcome

✅ Completed as planned. The design docs match the base + stereotype model and the epic is closed out.

**Delivered.** Schema doc §4 (primitives), §5 (node catalog note), and §7 (subset matrix + build
status) rewritten to one `classifier` node + one `dependency` edge with a stereotype vocabulary; the
BDD + use-case notation docs updated; the decision-log entry was added in Slice 07; `../../00-current-state.md`
and the epic `00-group.md` updated; the 07/08/09 slice Outcomes recorded. Renamed the file-local
`_draw_bdd_block`/`_draw_bdd_compartments` → `_draw_classifier`/`_draw_classifier_compartments`.

**Deviations.** The cross-cutting `bdd_block_min_height`/`bdd_block_min_size` (backend) and
`bddBlockMinHeight` (frontend) renames were **deferred** — they are functional and widely imported, so
the rename is a low-value/higher-risk cosmetic change; tracked as a follow-up.

**Verification.** `python manage.py test` → **377 OK** (after the render rename); frontend unaffected
(`npm run verify` green in Slice 08).

**Follow-up.** Operator generation **re-eval** (needs the Azure key) since the prompts + output shape
changed; the deferred `classifier_*` renames; a real `package` container frame; new diagram types on
the now-leaner base.
