# Slice 12: Training and Eval Vocabulary Re-Baseline

## Purpose

Apply the Slice 11 **example-generation engine** to the **whole** training + eval
pool: re-baseline every example so the set is **realistic** and **covers the
comprehensive notation vocabulary** — the `fork`/`join`, `generalization`,
`aggregation`/`association`/`enumeration` shipped in Epic 1 Slice 08 + Epic 2
Slice 09 but **absent from the current 36 examples**. This closes the
vocabulary-coverage gap so the eval actually tests generation of the full
supported notation, and refreshes the keys for realism and independence at the
same time.

## Background

- The comprehensive notation tier shipped **cross-cutting**: Epic 1 Slice 08
  (vocabulary + structural critic) added `fork`/`join` (activity),
  `generalization` (use-case), and `enumeration` + `aggregation`/`association`
  (bdd) to `backend/services/diagrams/catalog/diagram_types.py`; Epic 2 Slice 09 added the canvas +
  SVG renderers. `../../00-current-state.md` explicitly deferred **"the training/eval
  example re-baseline … to a separate chat"** — this slice is that work.
- The current 36 examples (Slice 05) **predate** the comprehensive vocab, so
  **none** of the new `semanticType`s appear in any training or eval example. Two
  consequences: generation gets **no few-shot exposure** to the new shapes, and
  the eval **never scores** whether generation can produce them — a blind spot in
  both training *and* measurement.
- Slice 11 defined the engine (deterministic backbone + independent sourcing +
  realism + coverage matrix + batch-review gallery) and proved it on one key.
  **This slice is the rollout.**

## Design

### A. Coverage-driven re-baseline (the whole pool)

- Drive from the Slice 11 **coverage matrix**, now with the comprehensive vocab as
  **required** cells. Every node + edge `semanticType` must appear ≥1 in the
  **training** pool and be represented in the **eval** pool, including:
  - **activity:** `fork` / `join` concurrency (plus canonical initial /
    activity-final usage).
  - **use_case:** `generalization` (actor↔actor and/or useCase↔useCase).
  - **bdd:** `enumeration`, `aggregation`, `association` (and the corrected
    composition-diamond direction).
- Re-author / extend the `_seed_examples.py` specs to fill the matrix while
  keeping **training/eval disjoint**, **domain spread** (no repeats), the **size**
  range (S/M/L), and **realism** (real, named scenarios).

### B. Engine-driven, independent, reviewed

- Every (re-)authored example goes through the **Slice 11 engine**: independent
  source → logical spec → deterministic assemble (grandalf) → validate →
  render-check → tag (`source`/`reviewer`/`reviewStatus`) → batch-review gallery →
  **human sign-off**. **No** example is produced by `diagram_generate`.

### C. Keep counts, or grow deliberately

- Default: keep the per-type pool sizes (**4 training + 8 eval**) but swap/extend
  *content* for coverage + realism. Grow counts only where coverage genuinely
  demands it, and record that as a decision.

### D. Guardrails

- Every example validates (no blocking errors) + render-checks, as today.
- Validation + the structural critic read the vocabulary from `diagram_types.py`
  (which already carries the comprehensive tier), so the new types are recognized.
  *(The deterministic eval anchor + matcher that also read it were later removed —
  pending an embeddings-based rebuild.)*
- The frontend round-trip (`test_samples` + the vitest sample tests) stays green.

## Included Work

- Re-baseline the `_seed_examples.py` specs across all three types to cover the
  comprehensive vocab + maintain diversity/realism; re-run the seed script to
  regenerate every `output.gp.json` + `prompt.md`.
- Tag every example (Slice 11 `## Tags`) with provenance + `reviewStatus`.
- Fill and verify the **coverage matrix** in
  `06-answer-key-generation-design.md` — no empty required cell.
- Batch-review the whole pool via the gallery; record sign-off.
- **Tests:** `test_samples` + the eval loader + the frontend round-trip stay
  green; add a **coverage assertion** that every node/edge `semanticType` in
  `diagram_types.py` appears in the example set.

## Not In Scope

- Changing the supported **vocabulary** (fixed; this slice only ensures the
  examples *cover* it).
- New diagram types (the post-MVP backlog roadmap).
- The **prompt-variation DOE factor** / register-complexity / paraphrase-set
  authoring (a follow-on that can layer on top).
- The live token DOE sweep (operator-triggered, separate).

## Target Areas

- `backend/assets/blueprints/_seed_examples.py` (spec re-baseline)
- `backend/assets/blueprints/<type>/examples/{training,eval}/**` (regenerated
  outputs + `## Tags`)
- `docs/02-design-and-features/06-answer-key-generation-design.md` (coverage
  matrix filled)
- `backend/tests/generation/test_samples.py` (coverage assertions)

## Exit Criteria

- Every node + edge `semanticType` in `diagram_types.py` (including the
  comprehensive tier) appears in ≥1 **training** example and is represented in the
  **eval** pool; the coverage matrix has **no empty required cell**.
- All training + eval examples validate + render, are tagged with provenance, and
  carry an `approved` `reviewStatus`.
- Backend + frontend suites green; the gallery shows the full pool with coverage
  all-filled.

## Previous Slice

- `11-answer-key-quality-and-review.md` (the example-generation engine + batch
  review + one-key pilot).

## Next Slice

- Follow-on (separate slice): layer in **register / complexity / paraphrase-sets**
  + the **prompt-variation DOE factor** from `06-answer-key-generation-design.md`;
  then the post-MVP diagram types per the backlog roadmap (State Machine →
  Class/ER → C4). Epic 4 (`diagram_update`) is the broader next epic.

## Outcome

✅ **Delivered — operator-approved.** The whole 36-key pool was re-authored on the
comprehensive vocabulary + BDD compartments — all offline and LLM-free — and signed off
(`reviewStatus: approved`). *(Later regenerated on the final catalog by `04-universal-vocabulary` S05, Epic 1.)*

**What shipped**
- **Compartment pipeline wiring (the Phase-C backend half):** `conform_logical` now preserves
  an optional per-node `compartments` list, and `assemble_canonical` sizes block-family nodes
  to their compartments via a new `bdd_block_min_size` (height from `bdd_block_min_height`).
  This is shared by the seed script **and** `diagram_generate`, so a hand-authored key and a
  generated diagram size a block identically. (Making `diagram_generate` actively *emit*
  compartments — LLM schema + prompt — stays an optional follow-on.)
- **Re-baselined 36 keys** in `_seed_examples.py` (4 training + 8 eval per type) from real,
  named, non-repeating domains, covering the full vocab: activity `fork`/`join`; use-case
  actor + useCase `generalization`; bdd `aggregation`/`association`/`enumeration`/`note` and
  block **compartments**. Sizes span S/M/L; training/eval stay disjoint.
- **Provenance tags** on every key (`## Tags`: `source: hand-authored` /
  `reviewStatus: approved`), emitted by the seed template.
- **Coverage guard:** `tests/generation/test_samples.py::VocabularyCoverageTests` fails if any
  `semanticType` is left uncovered.

**Verification**
- `python graphpilot/blueprints/_seed_examples.py` → **36 ok, 0 failed** (each validates +
  render-checks).
- `render_example_gallery` → all three types **"all semanticTypes present"**, every card valid
  + structurally clean, compartments rendered.
- Backend `manage.py test` → **364**; frontend `vitest` → **246** (round-trips every
  regenerated key, compartments included).

**Pending / follow-ups**
- **Human sign-off** — completed via the gallery; every key is tagged `reviewStatus: approved`.
- Live token **DOE** against these richer keys (operator-triggered); register/complexity +
  paraphrase-set prompt diversity; optional Phase-C generation (emit compartments).
