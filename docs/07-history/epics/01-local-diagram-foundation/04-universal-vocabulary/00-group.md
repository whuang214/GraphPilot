# Group: Universal Vocabulary (Epic 1 phase)

> **Folded into Epic 1 (Local Diagram Foundation).** This was a *technical refactor* of Epic 1's
> notation vocabulary into one universal element catalog + a reusable-shapes model, so it now lives as
> the `04-universal-vocabulary/` group of Epic 1 rather than a standalone epic. Historical slices retain their original numbering; the core-vocabulary reset continues with S12–S13.
>
> **Current semantic contract:** S12 supersedes the metamodel-complete exact-identity MVP profiles with bounded core authoring/generation vocabularies. The catalog may retain specialist compatibility identities, while BDD core authoring intentionally returns to one Block plus a primary stereotype. Historical slice outcomes retain the model delivered at that time.

## Goal

Keep one shared element catalog and reusable renderer while exposing only small, reliable core vocabularies to the three MVP generators and editor palettes. Preserve retained compatibility knowledge without turning the editor into a UML/SysML metamodel browser.

## User Scenario

A user or agent creates an ordinary Activity, Use Case, or BDD diagram from a short comprehensible vocabulary, refines labels/stereotypes/properties in the editor, and saves canonical JSON without choosing among specialist metaclasses. Existing specialist documents still open and render safely.

## Scope

- One backend element catalog separating supported compatibility knowledge from authorable/generatable core entries.
- One `gpNode` render family and shared canvas/SVG primitives.
- Exact bounded Activity and Use Case identities plus one BDD Block identity with primary stereotype.
- First-class part-to-whole BDD Composition, universal Comment Link inference, and structured Block properties.
- Core-only generation, palettes, Show all, semantic selectors, prompts, examples, and coverage checks.
- Safe load/render compatibility for retained specialist documents without new authoring.

## Out of Scope

- **New diagram types** (state machine, class, component, requirement, IBD) — **deferred post-MVP.**
  The generic shapes they'll use are added to the catalog now (canvas-only); each *type* is added
  later as context (a vocab subset + structural critic + `prompts.md` + answer keys) on the existing
  engine. Their intended vocabulary is documented in the standard (`00-diagram-json-schema.md`).
- **Special-rendering diagrams** — sequence, timing, communication (need a different renderer; a
  separate future effort). See the standard §14.
- Register / complexity / paraphrase prompt diversity (an Epic 3 follow-on; the DOE framework is removed pending redesign).

## Slice Plan

Layered so each phase builds on a working one below it: **design (done) → enable the code → regenerate
the answer keys → refresh the prompts.** Scope is the **3 MVP diagram types on a universal catalog** —
**no new diagram types** (those are deferred post-MVP; see Out of Scope).

**Phase B — Code enablement** (make the app capable)

1. `01-vocabulary-catalog.md` - backend element catalog + per-type subsets; behavior-preserving. ✅
2. `02-catalog-driven-palette-and-node.md` - single `gpNode` render family + Common/UML/SysML palette; `gpNode` cutover + mechanical re-seed. ✅
3. `03-catalog-conform-render-and-authoring.md` - render + conform read the catalog; `custom`/`generated` switch, metadata identity block, `custom` canvas, unknown-type fallback. ✅
4. `04-universal-shape-vocabulary.md` - add the common UML/SysML shapes (relationships + classifiers + `port`) to the catalog + palette, **canvas-only** (reusable by future types; the 3 MVP types' generation is unchanged). ✅

**Phase C — Answer keys** (regenerate the gold content)

5. `05-answer-key-rebaseline.md` - regenerate the **3 MVP diagrams'** answer keys on the final catalog (agent-authored, no LLM); gallery review + coverage assertion + frontend round-trip. ✅

**Phase D — Generation prompts**

6. `06-prompts-and-generation.md` - refresh the 3 types' `prompts.md` + verify generation (light; only if S05 changes a type's vocab). ✅

**Phase E — Reusable shapes** (historical implementation; superseded by exact semantic identities)

7. `07-reusable-shapes-backend.md` - introduced the base-plus-stereotype backend model; completed historically, now superseded by exact catalog identities. ✅
8. `08-reusable-shapes-editor.md` - introduced matching editor fields/adapters; completed historically, now superseded by structured features and `appliedStereotypes`. ✅
9. `09-reusable-shapes-docs.md` - documented that historical model; current design docs supersede it. ✅

**Phase F — Answer-key regeneration**

10. `10-answer-key-generation.md` - expanded the library to 4 training + 12 eval per type. The deterministic seeder and 48 outputs have since been re-baselined onto exact semantic types and structured model data. ✅

**Phase G — Exact semantic model sync**

11. `11-semantic-model-frontend-sync.md` - React catalog mirror, complete primitive/edge rendering, structured inspector authoring, and canonical round-trip parity for the semantic-model correction. Complete historically; superseded for core authoring by S12.

**Phase H — Core vocabulary reset**

12. `12-core-vocabulary-contract.md` - freeze the user-approved bounded profiles, one-Block BDD model, Composition direction, Comment Link inference, compatibility boundary, and Note parity. **Complete.**
13. `13-core-vocabulary-runtime.md` - atomic backend/frontend core-vocabulary cutover, answer-key rebaseline, compatibility boundary, and parity verification. **Complete.**

## Dependencies

- **Depends on:** Epic 1 (type profile / validation / schema), Epic 2 (canvas renderers + palette),
  Epic 3 (generation-conform + the answer-key engine + eval). Slices 01–03 refactor those subsystems
  onto the catalog before the shape-vocabulary + key-regeneration slices build on them.
- **Unblocks:** richer Epic 4 edits (`diagram_update` uses the metadata identity block) and Epic 5 RAG
  over more diagram types.

## Research / Inputs

- **The standard:** `docs/02-design-and-features/00-diagram-json-schema.md` (universal catalog,
  per-type subsets, palette model, authoring model, extensibility, React Flow alignment).
- **Sources:** `docs/research/uml-sysml-vocabulary/` (OMG UML 2.5.1 + SysML 1.6 PDFs, the
  uml-diagrams.org element inventory, mermaid / PlantUML / React Flow references).
- **Prior art in-repo:** the comprehensive-notation tier (Epic 1 S08 + Epic 2 S09), BDD compartments
  (Epic 2 S10), the answer-key rebaseline (Epic 3 S12), and the subsystem design docs
  (`02-validation`, `03-rendering`, `04-generation-design`, `05-generation`) aligned to the standard.

## Acceptance Criteria

- The catalog is the single source for supported element/render knowledge and identifies which entries are core-authorable.
- The three MVP generation/palette/selector profiles exactly match the bounded lists in the canonical standard.
- BDD Block primary stereotype, structured features, first-class Composition, Comment Links, and Note dog-ears render in canvas/SVG parity.
- Retained specialist documents load/render safely but cannot create new specialist elements.
- Realistic answer keys cover every core identity without synthetic specialist padding.
- Unknown/custom compatibility behavior remains safe and does not expand the MVP palettes.

## Related Docs

- `../../../../02-design-and-features/00-diagram-json-schema.md` - the standard this epic implements.
- `../../../../02-design-and-features/04-generation-design.md` - the `custom ⇄ generated` model + per-type context.
- `../../../../02-design-and-features/06-answer-key-generation-design.md` - the answer-key engine reused per new type.
- `../../00-current-state.md` - cross-epic status.
