# Slice 11: Answer-Key Quality and Review

## Purpose

Establish a repeatable **example-generation engine** — the method that turns a
scenario into a trustworthy gold-standard answer key — plus a **batch review**
workflow to verify keys *at a glance*. The engine keeps the **deterministic,
offline backbone** (reproducible) but fixes the three things that matter for
answer keys: they must be **independent** (non-circular), **realistic** (reflect
real systems, not toy diagrams), and **cover all the cases** that exercise the
system. Prove the engine on **one** key first; the *same* engine then drives the
training/eval **re-baseline** (Slice 12) and — per the backlog roadmap — serves
post-MVP diagram types (State Machine, Class/ER, C4).

## Background

- The eval answer keys are the **ground truth** every eval/DOE number rests on:
  the eval framework reads `examples/eval/*` and scores generated candidates
  against them (validity anchor + ground-truth matcher + LLM judge). Key quality
  therefore bounds the trustworthiness of every result. *(That eval framework was
  later removed — deferred post-MVP, pending an embeddings-based rebuild; the
  answer-key library it scores against is retained.)*
- Today all 36 keys (per type: 4 training + 8 eval) are assembled
  **deterministically and offline** by
  `backend/assets/blueprints/_seed_examples.py` from hand-written **logical
  specs**. The specs themselves were drafted with an LLM, so the eval ground
  truth shares lineage with the generator under test — a **circularity** risk
  (see decision rows on the Slice 05 library and the Slice 06 eval redesign).
- **Chosen method (operator decision):** *keep* the deterministic
  `_seed_examples.py` backbone — it is reproducible, offline, reviewable in one
  place, and auto-lays-out. The problem to fix is **not** the pipeline; it is
  (a) the **circularity** of LLM-drafted specs, (b) **realism** (today's keys lean
  toy/narrative), and (c) **coverage** (no explicit matrix proving every case is
  tested).
- The engine is defined as a **reusable** capability: the same
  source → assemble → tag → review → lock pipeline is the per-type recipe in the
  backlog's *Additional diagram types* roadmap, and it powers the Slice 12
  re-baseline.
- Reviewing a key today means opening each `output.gp.json` (or its `.svg`)
  individually — the friction this slice removes.

> **Numbering note.** The eval/DOE-hardening work committed as *"Epic 3 Slice
> 08–10"* (ground-truth matcher, structural critic, critique-refine loop, and the
> DOE refine-rounds/reasoning extension) shipped as **code without slice docs**.
> This slice is numbered **11** to clear the committed Slice 10. Backfilling
> docs for 08–10 and reconciling the commit-vs-doc numbering is tracked as
> separate doc-debt (see `../../00-current-state.md`).

## Design

### A. The engine — deterministic backbone, independently sourced

- **Backbone (unchanged, chosen):** the offline `_seed_examples.py` pipeline —
  logical spec → `conform` → `assemble` + grandalf layout → `validate` →
  render-check → write `output.gp.json` + `prompt.md`. Reproducible, key-free,
  reviewable in one place.
- **What changes is the *source* of each spec** (this is what breaks circularity
  and drives realism). An answer key is **never** produced by `diagram_generate`.
  Permitted sources, in preference order:
  1. **Grounded in an external reference** — a real published UML/SysML scenario
     or a real-world system, transcribed into a spec. Independence *and* realism
     come from the source.
  2. **Hand-authored** in `/editor` (draw + visually verify) for flagship or
     layout-sensitive keys.
  3. **Different-lineage LLM draft** (a model family other than the one under
     eval) used only as a *starting* draft.
  - All require a **mandatory human edit + sign-off**; the human owns the final
    gold.
- **Provenance + sign-off** are recorded per example in `prompt.md` via the
  `## Tags` block, extended with `source`, `reviewer`, and `reviewStatus`
  (`draft` / `approved`). Metadata-only: ignored by `_build_few_shot`, kept out of
  `output.gp.json`, no validation/render/round-trip impact.
- Each key still passes `DiagramValidationService` (no blocking errors) and a
  `DiagramRenderService` render-check.

### B. Realism — keys that reflect real systems

- Source from **real, named scenarios** (a real domain/system or a published
  reference), not invented toy flows. The prompt reads like a real request; the
  diagram is a plausible real design at a sensible size.
- Realism is an explicit **review criterion** in the gallery ("would a
  practitioner accept this as correct *and* realistic?"), recorded via
  `reviewStatus`.

### C. Coverage — a matrix that tests the whole system

- Maintain an explicit **coverage matrix** so "cover all the cases" is concrete
  and visible; empty required cells are the to-do list. Axes per diagram type:
  - **Structure** — every structural shape the type supports (e.g. activity:
    linear, decision+merge, loop, **fork/join** concurrency, multi-end).
  - **Vocabulary** — **every** node + edge `semanticType` appears at least once,
    including the comprehensive tier (activity `fork`/`join`; use-case
    `generalization`; bdd `aggregation`/`association`/`enumeration`).
  - **Size** — S / M / L (node + edge buckets) to test scaling.
  - **Domain** — a wide spread, no repeats, to avoid memorization.
  - *(Later layer — prompt realism)* **register** + **complexity** from
    `06-answer-key-generation-design.md`.
- The matrix is the **demand** the engine fills, and doubles as the "am I testing
  everything?" guarantee for the eval. Filling it across the whole pool is the
  Slice 12 re-baseline.

### D. Batch review — a single contact sheet

- A new **offline** management command (working name `render_example_gallery`)
  renders **every** example (training + eval, all types) to inline SVG via
  `DiagramRenderService.to_svg` (pure, no file I/O, no key) and emits **one
  self-contained static HTML** "contact sheet". Each card shows: the rendered
  diagram, the `## Prompt`, the `## Tags` (source / register / complexity /
  `reviewStatus`), and the validity + render status. The page also surfaces the
  **coverage-matrix status** (which cells are filled / empty) so realism *and*
  completeness are reviewed in one place.
- Output goes to a **gitignored** dir (working name
  `backend/review_galleries/<timestamp>/index.html`), mirroring the
  gitignored `backend/review_galleries/` convention; the dir is added to `.gitignore`.
- The reviewer scans one page, flags problems, and updates `reviewStatus` in the
  offending `prompt.md`. **No new runtime dependency** — `drawsvg` is already
  pinned.
- A `/review` route in the React editor (reusing the same render) is a possible
  later enhancement and is **out of scope here**.

### E. Pilot on one key

- Re-author **one** existing eval key end-to-end through the engine (independent
  source → spec → assemble → tag → gallery → human sign-off) and place it in the
  coverage matrix — the worked proof the engine yields a **better, more realistic**
  key before the Slice 12 rollout.

## Included Work

- **Overhaul the generation prompts** (operator-added scope): a master-prompt-engineer
  pass on `backend/assets/prompts/generate.md` + `repair.md` and the shared
  system message (expert role, an explicit approach, hard-constraint framing for
  vocabulary + structural rules, stricter JSON-only output discipline, sharper
  few-shot framing), keeping every `{{placeholder}}` intact.
- Document the **engine** (deterministic backbone + sourcing/independence rules)
  and the **realism** criterion in `06-answer-key-generation-design.md` (the
  design doc is the source of truth and wins).
- Define the **coverage matrix** (axes + target cells per type) in
  `06-answer-key-generation-design.md`; seed it with the current 36 keys so gaps
  are visible.
- Extend the `## Tags` block with `source` / `reviewer` / `reviewStatus`.
- Add the `render_example_gallery` management command (renders all examples +
  coverage status to one HTML) + its gitignored output dir.
- **Prove the setup:** render the whole pool to the gallery and tag **one** eval key
  with its honest provenance (`source: llm-draft`, `reviewStatus: draft`) to
  demonstrate the tag→gallery flow. (Re-authoring content for realism is Slice 12.)
- **Tests (Track A, offline):** the gallery command renders all examples + coverage
  and writes well-formed HTML; unit tests cover tag parsing, coverage, and card
  rendering.

## Not In Scope

- The **full pool re-baseline** (re-authoring every example to fill the matrix +
  cover the comprehensive vocab) — that is **Slice 12**; this slice proves the
  engine on one key and defines the matrix.
- The **prompt-variation DOE factor** and full register/complexity/paraphrase-set
  authoring (a follow-on; the matrix reserves the axes).
- A React `/review` UI route.
- Any change to runtime save-blocking validation, the canonical schema, or the
  supported diagram **vocabulary** (kept as-is per the current decision).

## Target Areas

- `backend/assets/prompts/generate.md` + `repair.md` (prompt overhaul) and
  `backend/services/generation/pipeline/diagram_generation_service.py` (shared system message)
- `docs/02-design-and-features/06-answer-key-generation-design.md` (engine,
  sourcing/independence rules, realism criterion, coverage matrix, extended tags)
- `backend/operations/management/commands/render_example_gallery.py` (new)
- `backend/assets/blueprints/<type>/examples/**/prompt.md` (tags + provenance;
  one demonstration key)
- `.gitignore` (gallery output dir)
- `backend/tests/api/test_render_example_gallery.py` (new)

## Exit Criteria

- The **generation prompts** (`generate.md` / `repair.md` / system message) are
  overhauled, with every `{{placeholder}}` still filled (prompt-service tests green).
- The **engine** (backbone + independent sourcing + human sign-off), the
  **realism** criterion, and the **coverage matrix** are documented; the matrix is
  seeded with the current keys so gaps are visible.
- `python manage.py render_example_gallery` produces a **single** offline HTML
  contact sheet of all examples + coverage status, scannable in one view.
- **One** eval key carries a `## Tags` block with honest provenance
  (`source` / `reviewer` / `reviewStatus`), demonstrating the tag→gallery flow;
  full content re-authoring for realism is deferred to Slice 12.
- Track-A tests stay green offline (`python manage.py test`).

## Previous Slice

- `09-critique-refine-loop.md` (the retained generation slice; the eval/DOE slices
  formerly 06/07/08/10 were removed — see the slice-index note in `../00-epic.md`).

## Next Slice

- `12-training-eval-vocabulary-rebaseline.md` — apply this engine to the **whole
  pool**: re-baseline every training + eval example so the set is realistic and
  **covers the comprehensive notation vocabulary** (the new `fork`/`join`,
  `generalization`, `aggregation`/`association`/`enumeration` shipped in Epic 1
  Slice 08 + Epic 2 Slice 09). Then layer in register/complexity/paraphrase-sets +
  the prompt-variation DOE factor; the same engine later powers the post-MVP
  diagram types (State Machine → Class/ER → C4). Epic 4 (`diagram_update`) is the
  broader next epic.

## Outcome

✅ **Delivered.** Slice 11 built the generation-side engine + review tooling; the full
content re-bake remains Slice 12.

**What shipped**
- **Generation-prompt overhaul** (operator-added scope): `generate.md` + `repair.md`
  rewritten as a master-prompt-engineer pass (expert role, an explicit "how to approach
  it", hard-constraint framing for vocabulary + structural rules, stricter JSON-only
  output discipline, sharper few-shot framing) and the shared system message
  strengthened in `diagram_generation_service.py`. Every `{{placeholder}}` preserved.
- **Engine + realism + coverage** documented in `06-answer-key-generation-design.md`:
  independent-sourcing preference order (external reference › hand-authored ›
  different-lineage LLM draft), mandatory human sign-off, the realism criterion, and a
  **corrected vocabulary-coverage table** matching the gallery's actual output.
- **`## Tags`** extended with `source` / `reviewer` / `reviewStatus` (metadata-only).
- **`render_example_gallery`** management command → one self-contained, styled HTML
  contact sheet: per card the diagram (inline SVG), prompt, tag chips, and validity /
  structural / render badges, plus a per-type vocabulary-coverage panel. Output is
  gitignored (`backend/review_galleries/`).
- **Proof:** the gallery renders all **36** examples (36 SVGs, all valid + structurally
  clean) and auto-reports the real gaps; one eval key (`activity/eval/01-ecommerce-checkout`)
  tagged with honest provenance (`llm-draft` / `draft`) demonstrates the tag→gallery flow.

**Coverage truth (correction).** The Slice 12 premise ("none of the new vocab appears")
was only partly right. The gallery-computed gaps are: activity `fork`/`join`; use_case
`generalization` (edge); bdd `aggregation` + `enumeration` + `association` (edge) + `note`.
Use-case `association` and bdd `generalization` are already covered. The design-doc gap
table now matches this exactly.

**Deviations**
- Adopted the operator's **11 = generate-side / 12 = content** split: Slice 11 does **no**
  content re-authoring. The originally-planned "re-author one key for realism" became a
  metadata-only provenance tag on one key; realism re-authoring is Slice 12.
- The **generation-prompt overhaul** was added to this slice at operator request (not in
  the original plan). Its effect on generation quality is only measurable in a **live DOE**
  (operator-triggered, needs a key); offline tests confirm no regression.

**Verification**
- `python manage.py test` → **357 passing** (344 + 13 new gallery tests), fully offline.
- `python manage.py render_example_gallery` → one HTML over 36 examples; a browser DOM
  check confirmed the responsive grid, embedded SVGs, badges, and coverage panel.

**Follow-ups**
- **Slice 12** — re-baseline the whole pool to fill the coverage gaps + realism +
  provenance tags, reviewed via this gallery.
- Live token DOE to measure the prompt overhaul's effect on generation quality
  (operator-triggered).
