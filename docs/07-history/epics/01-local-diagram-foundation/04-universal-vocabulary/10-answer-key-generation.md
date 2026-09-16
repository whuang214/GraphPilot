# Slice 10: Answer-Key Generation (regenerate the gold library)

## Purpose

Delete and regenerate the whole answer-key library — training **and** eval, for all three MVP
diagram types — from scratch on the **reusable-shapes** vocabulary (S07). The keys are the LLM's
few-shot context (training pool) and the held-out benchmark it is scored against (eval pool), so this
slice makes them (a) fully express the base + `data.stereotype` model, (b) give the best, most varied
context to the generator, and (c) stress-test the generator with harder structures, heavier vocab
usage, and valid edge cases.

## Background

- S07 regenerated the keys mechanically to the base+stereotype model, but kept the same set (4
  training + 8 eval per type). This slice enriches the library: it keeps the curated set and **adds a
  stress/edge-case tier** to the eval pool, growing it to **12 eval per type** (48 total: 4 training +
  12 eval × 3 types).
- Keys stay **agent-authored, offline, deterministic** — never via `diagram_generate` (the
  no-circularity design principle; see `../../../../02-design-and-features/06-answer-key-generation-design.md`).
  The seeder (`backend/assets/blueprints/_seed_examples.py`) is the single source of truth: it
  clears each type's `examples/{training,eval}/` pools and rebuilds every `output.gp.json` +
  `prompt.md` via conform → assemble (grandalf layout) → validate → render-check → write.

## Scope decision

- **Pool sizes:** 4 training + 12 eval per type (was 4 + 8). Chosen as a first step; the eval pool is
  **DOE-tunable** — a later run can add more eval cases and measure whether closeness scores improve.
- **Training unchanged in count** (4/type) to keep few-shot cost low; each training case already
  showcases the base+stereotype vocab (classifier + `data.stereotype`, dependency + `data.stereotype`).

## Design

- **Add a stress/edge-case eval tier (`09`–`12`) per type**, each a *valid but demanding* diagram
  (structurally clean — it must pass the deterministic structural critic, so "edge case" means
  boundary-of-valid, never invalid):
  - **activity** — wide fork/join (4 parallel branches); a multi-decision, multi-loop, multi-end
    process; a decision that *contains* a fork/join; a decision + fork + decision with two end states.
  - **use_case** — a max-vocab diagram (include + extend + actor-generalization + use-case-generalization
    + note); many actors sharing one included use case; a deep use-case generalization hierarchy; a
    large multi-actor system mixing every relationship.
  - **bdd** — a max-vocab diagram (all five classifier stereotypes + all six edge kinds:
    composition/aggregation/association/reference/generalization/dependency); a deep composition tree;
    a wide reference web with aggregation + dependency + enumeration; an enumeration/constraint/value +
    compartment-heavy model.
- **Full vocabulary coverage** across each pool is guarded by `test_samples.VocabularyCoverageTests`
  (every allowed node/edge `semanticType` **and** every allowed stereotype must appear).
- **Refresh the seeding docs** so the regeneration process (how to run it, what the pools/tiers are,
  the coverage + structural guards, the no-LLM principle) is clear.

## Included Work

- `backend/assets/blueprints/_seed_examples.py`: add the 12 new eval specs (4/type); refresh the
  module docstring to describe the training/eval tiers + the regeneration workflow.
- `backend/tests/generation/test_samples.py`: `EXPECTED_EVAL = 12`; coverage assertions unchanged (already cover
  stereotypes).
- Re-seed (delete + regenerate) every `examples/{training,eval}/<name>/{output.gp.json, prompt.md}`.
- Seeding docs: the answer-key design doc + the blueprints seeding notes.

## Not In Scope

- Any change to the generation engine, prompts, or the runtime vocabulary (S07 owns those).
- A live generation re-eval / DOE sweep (operator-triggered; needs an Azure key).
- New diagram types.

## Target Areas

- `backend/assets/blueprints/_seed_examples.py` + `*/examples/{training,eval}/`
- `backend/tests/generation/test_samples.py`
- `docs/02-design-and-features/06-answer-key-generation-design.md`

## Exit Criteria

- Every key (training + eval, all types) validates, renders, is structurally clean, and round-trips
  in the frontend; `test_samples` pool counts are 4 + 12; `VocabularyCoverageTests` green.
- `python manage.py test` green; the `render_example_gallery` contact sheet renders all 48.
- The seeding docs describe the regeneration process clearly.

## Previous Slice

- `09-reusable-shapes-docs.md`

## Next Slice

- End of Epic 1's `04-universal-vocabulary/` group. Follow-ons (operator-triggered, need an Azure key):
  the live generation re-eval / DOE sweep over the enlarged eval pool to record whether the richer keys
  improve closeness scores.

## Outcome

✅ **Completed.** The answer-key library was regenerated on the reusable-shapes vocabulary at
**4 training + 12 eval per type (48 total)**.

- **What shipped:** a stress / edge-case eval tier (`09`–`12`) per type in
  `backend/assets/blueprints/_seed_examples.py` — 12 new specs authored offline (no LLM):
  - *activity* — `09-trade-settlement` (wide 4-way fork/join), `10-grant-review` (3 decisions + a
    rework loop + 3 end states), `11-order-processing` (a decision whose branch contains a
    fork/join), `12-expense-approval` (decision → fork/join → decision, 2 ends).
  - *use_case* — `09-hospital-portal` (include + extend + actor- and use-case-generalization + note),
    `10-conference-management` (4 actors sharing one included use case), `11-payment-gateway` (a
    two-level use-case generalization hierarchy), `12-egov-portal` (large multi-actor, mixed).
  - *bdd* — `09-autonomous-vehicle` (**every** classifier stereotype + **every** edge kind),
    `10-aircraft` (deep composition tree), `11-streaming-catalog` (generalization + a wide reference
    web with aggregation/dependency/enumeration), `12-hvac-system` (two enumerations + a constraint +
    value properties + compartments).
- The seeder docstring now documents the two pools + the stress tier + the guards;
  `tests/generation/test_samples.py` `EXPECTED_EVAL = 12`; the eval/layout/render count assertions moved to
  12 / 48.
- **Verification:** seeder **48 ok / 0 failed**; `python manage.py test` → **384 OK** (structural
  critic + vocabulary-coverage + round-trip all green over the enlarged pool); the
  `render_example_gallery` contact sheet rendered all **48**; frontend `npm run verify` green (the
  keys still round-trip losslessly). The 36 pre-existing keys re-seeded **byte-identical**
  (determinism preserved).
- **Deviations:** none. Training stayed at 4/type (few-shot cost); eval grew to 12/type — a
  DOE-tunable first step. The live generation re-eval over the enlarged pool remains the one
  operator-triggered follow-up (needs an Azure key).
