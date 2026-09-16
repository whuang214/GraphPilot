# Slice 07: Classifier and Dependency Collapse

## Purpose

Collapse each family of look-alike vocabulary into a single **base type + `data.stereotype`**, so
one reusable element becomes many by changing a label — instead of many near-duplicate types that
differ only by their «stereotype». Nodes converge on a `classifier` base; the dashed-keyword
relationships converge on a `dependency` base. Object-oriented, leaner, and future-proof.

**This slice does the backend** (the atomic green unit — since there is no back-compat, the catalog,
its consumers, and the regenerated examples must land together). The editor is Slice 08; the
schema-doc rewrite + cleanup is Slice 09. The base+stereotype model below is the shared design for
all three.

## Background

- Epic 1's `04-universal-vocabulary` group (S01–S06) already unified *rendering* into one `gpNode` / one SVG dispatcher driven by the
  element catalog's **render primitives**. But the *vocabulary* still lists every classifier-box
  element (`block`/`part`/`value`/`constraint`/`enumeration`/`class`/`interface`/`component`/
  `package`/`requirement`) and every dashed-keyword relationship (`include`/`extend`/…) as its own
  `semanticType`, even though within each family they share one shape and differ only by the header
  keyword. The frontend re-encodes that membership by hand in several lists, which has already
  drifted (the property panel edits compartments for only 5 of the 10 classifier boxes).
- The standard already prescribes this collapse: the classifier-box primitive "reused for a dozen
  elements, just with a different «stereotype»" (§4) and the dependency-stereotype family as "one
  render path: `dependency` + `data.stereotype`" (§6).

## Design

### The base + stereotype model

- **Node base `classifier`** (renders as the classifier box). The specific kind moves to
  `data.stereotype`: `«block»`, `«class»`, `«interface»`, `«component»`, `«package»`,
  `«enumeration»`, `«requirement»`, `«part»`, `«value»`, `«constraint»` — and future
  `«state»`/`«object»`/`«artifact»`/`«node»` for free (no new shape).
- **Edge base `dependency`** (dashed, open arrow). The keyword moves to `data.stereotype`:
  `«include»`, `«extend»`, and the future `«use»`/`«import»`/`«allocate»`/`«satisfy»`/
  `«deriveReqt»`/`«verify»`/`«refine»`/`«trace»`/`«copy»`/`«containment»`.
- The header/label the renderer shows is `data.stereotype` when present, else derived from the base
  type (so pre-existing diagrams are byte-identical).

### Stays as distinct types (already written once, reused, meaning differs)

- `fork`/`join` (bar) and `decision`/`merge`/`choice` (diamond) — distinct control-flow nodes with
  opposite structural rules; already one shared draw path.
- `generalization`/`realization` (hollow triangle) and `aggregation`/`composition` (diamond) —
  distinct markers, not a shared "keyword" family.

### Categories = allowed stereotypes per type

Each diagram type's "category" becomes an **allowed-stereotype set** (e.g. `bdd` allows
`block`/`part`/`value`/`constraint`/`enumeration`). This replaces the per-type classifier vocab;
non-classifier node types (`start`/`actor`/…) keep their existing per-type membership. Off-category
stereotypes are advisory (never a save block), consistent with the `custom ⇄ generated` model.

### No backwards compatibility (clean slate)

Consistent with the `04-universal-vocabulary` group's no-v1-aliases approach (Epic 1): there is **no legacy `semanticType` normalizer**.
The specific classifier/dependency values are simply re-authored as base + stereotype. Off-vocab
input is coerced to the base + the type's default stereotype by conform, exactly as off-vocab is
handled today.

### Rollout (clean cutover)

Replace the specific classifier/dependency vocabulary with the base + stereotype model in one pass,
update every consumer, and **regenerate the examples**. Activity keys stay byte-identical (no
classifiers or collapsed edges); BDD and use-case (`include`/`extend`) keys are regenerated. Sequence
the code so the backend suite is green once the examples are re-seeded.

## Included Work (backend)

- Catalog: `classifier` node base + stereotype specs; `dependency` edge base + edge stereotypes;
  `allowed_stereotypes()` helper. **(done)**
- Type profiles: `allowed_stereotypes` + `default_stereotype`.
- Render/sizing, validation, and the structural critic become stereotype-aware (the eval minimums
  + matcher this originally included were later removed with the eval framework).
- Generation: `LOGICAL_SCHEMA` gains `stereotype`; conform coerces off-vocab to base + default
  stereotype; `_vocabulary_text` + `prompts.md`/`generate.md`/`repair.md` describe base + stereotypes.
- Examples: `_seed_examples.py` (nodes + edges) authored as base + stereotype; re-seed BDD +
  use-case `include`/`extend`.
- Design-doc + notation-doc updates (schema doc §4–§7 + `diagram-schemas/`) are consolidated in
  Slice 09 with the rest of the docs (one cohesive rewrite); this slice is code + regenerated examples.

## Not In Scope

- Frontend/editor (Slice 08) and the schema-doc §4 rewrite + renames + current-state (Slice 09).
- New diagram *types* (still deferred). Making `package` a real container frame (stays a classifier
  stereotype for now). Collapsing the marker-distinct edges or the control-flow shape pairs.

## Target Areas

- `backend/services/diagrams/catalog/{element_catalog,diagram_types,constants}.py`, `backend/services/context/{diagram_validation_service,diagram_render_service}.py`, `backend/services/generation/{diagram_generation_service,structural_constraints}.py`
- `backend/assets/blueprints/_seed_examples.py` + `*/examples/` + `*/prompts.md`, `backend/assets/prompts/{generate,repair}.md`, `backend/assets/schemas/diagram.json`
- `backend/tests/*` (catalog/samples/contracts/critic/generation/validation/render)
- `docs/02-design-and-features/00-diagram-json-schema.md` (§5–§7 rows) + `diagram-schemas/`

## Exit Criteria

- The catalog exposes one `classifier` node base + one `dependency` edge base with a stereotype
  vocabulary per type (no legacy `semanticType` aliases — examples re-authored).
- Generation emits base + stereotype; conform coerces off-vocab; the structural critic reads
  the stereotype. *(The eval that also read it — anchor + matcher — was later removed, pending rebuild.)*
- Activity example geometry is byte-identical; BDD + use-case keys regenerated and gallery-reviewed;
  backend `python manage.py test` green (catalog, samples/coverage, contracts, critic, eval,
  generation, validation, render).

## Previous Slice

- `06-prompts-and-generation.md`

## Next Slice

- `08-reusable-shapes-editor.md` — the editor (one Box palette, stereotype field,
  compartments fix, adapters).

## Outcome

✅ Completed as planned. The backend runs on the base + stereotype model: one `classifier` node and
one `dependency` edge, with a per-type stereotype vocabulary.

**Delivered.** `element_catalog.py` collapses the classifier-box family to a single `classifier` node
+ a `STEREOTYPE_CATALOG` (BDD: block/part/value/constraint/enumeration; canvas-only:
class/interface/component/package/requirement) and folds include/extend into `dependency` +
stereotype; type profiles gained `allowed_node/edge_stereotypes` + `default_stereotype`; render reads
`data.stereotype`; validation and the structural critic are stereotype-aware (the eval minimums + matcher that were
too have since been removed, pending rebuild); generation (`LOGICAL_SCHEMA` + `conform_logical` + `_vocabulary_text` +
`prompts.md`/`generate.md`/`repair.md`) emits base + stereotype; the 12 BDD + 8 include/extend
use-case answer keys were regenerated.

**Deviations.** No back-compat normalizer (clean slate, per the decision). Design-doc/notation updates
were consolidated into Slice 09.

**Verification.** `python manage.py test` → **377 OK**; `render_example_gallery` re-rendered all 36;
git shows **0 activity example changes** (byte-identical) and only the BDD + include/extend use-case
keys changed.

**Follow-up.** Slice 08 (editor); Slice 09 (docs + cleanup).
