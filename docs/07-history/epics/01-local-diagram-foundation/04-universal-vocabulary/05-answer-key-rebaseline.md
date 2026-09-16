# Slice 05: Regenerate the 3 Diagrams' Answer Keys

## Purpose

Regenerate the answer keys for the **3 MVP diagrams** (activity, use-case, BDD) on the final
universal catalog — **agent-authored, no LLM** — by refactoring `_seed_examples.py` (the Slice 12
method). This keeps the keys consistent with the shared catalog and fully covering each type's
vocabulary. **No new diagram types.**

## Background

- After S04 the catalog is the universal vocabulary; the 3 types' generation vocab is unchanged (the
  new generic shapes are **canvas-only**). Keys stay agent-written + offline so the eval is never
  contaminated by the model it scores.

## Scope decision (⚠️ confirm before authoring)

The new generic **classifiers** (`class` / `interface` / `component` / `package` / `requirement` /
`port`) stay **canvas-only** — they enter *generation* only when their diagram types are added
(post-MVP), so they do **not** appear in the 3 types' keys. The open question is whether any new
generic **relationship** (e.g. `dependency`) should be admitted into a type's generation vocab (say,
BDD or use-case) and used in that type's keys:
- **Option A (default):** keep all new generics canvas-only → this slice is a **consistency +
  full-coverage refresh** of the 3 types' keys on the final catalog (content stays within each
  type's existing vocab).
- **Option B:** admit specific relationships (e.g. `dependency` → BDD/use-case) into those types'
  `valid_in` and re-author their keys to use them.

## Design

- Refactor `_seed_examples.py` for the 3 types on the final catalog; re-seed all pools.
- (Option B only) add the confirmed relationship(s) to the relevant type's catalog `valid_in`.
- Extend `VocabularyCoverageTests` if the vocab changes; render the `render_example_gallery` contact
  sheet for review; keep the frontend round-trip green; stamp `reviewStatus`.

## Not In Scope

- New diagram types + their answer keys (deferred post-MVP). Prompts (S06).

## Target Areas

- `backend/assets/blueprints/_seed_examples.py` + `*/examples/`
- `backend/tests/generation/test_samples.py` (coverage), `render_example_gallery`

## Exit Criteria

- Every key (3 types) validates + renders + is structurally clean + round-trips; coverage assertion
  green; gallery rendered + operator-approved.

## Previous Slice

- `04-universal-shape-vocabulary.md`

## Next Slice

- `06-prompts-and-generation.md`

## Outcome

✅ Completed (Option B). `dependency` is now a BDD relationship, and a BDD key exercises it.

**Delivered.**
- `dependency` added to BDD's generation vocab (`element_catalog.py` `valid_in += bdd`; SysML-legit);
  it also stays available on the `custom` canvas.
- The `04-online-store` BDD training key regenerated to use it — an Order → Payment Gateway
  **dependency** (dashed open arrow) — with the prompt updated to match.
- BDD schema doc + the seed coverage comment + the unchanged-subset & contract baselines updated.

**Verification.** backend `manage.py test` → **377** (`VocabularyCoverageTests` green — BDD now covers
`dependency`); re-seed clean, only the `04-online-store` example changed; frontend `npm run test` →
**247** (round-trips the new dependency edge, which renders a dashed open arrow).

**Deviations.** Only BDD gained a relationship; **activity + use-case keys are unchanged** — no new
generic relationship is idiomatic for them (per the convention audit). `realization` + the classifier
shapes stay canvas-only.

**Follow-up.** none — Slice 06 (prompts refresh) next.
