# Core Vocabulary Contract

## Purpose

Replace metamodel-complete MVP authoring/generation profiles with the smallest practical Activity, Use Case, and BDD vocabularies, while retaining separate compatibility knowledge for existing specialist documents.

## Background

The neutral UML/SysML research intentionally catalogues visually meaningful concepts and concrete metaclasses but explicitly does not require every metamodel class to become a palette item. Runtime reuse of one `valid_in` set for generation, palettes, Show all, and semantic selectors exposed dozens of specialist Activity actions and BDD definitions without realistic default consumers. The user approved a core-first reset on 2026-07-16 after a source-backed audit of the research, active contracts, historical MVP vocabulary, prompts, and answer-key usage.

## Design

- Activity exposes Initial, Action, Decision, Merge, Fork, Join, Activity Final, Note, Control Flow, and Comment Link only.
- Use Case retains Actor, Use Case, System Boundary (`subject`), Note, Association, Include, Extend, Generalization, and Comment Link.
- BDD exposes Block and Note only. Optional Block `data.stereotype` controls its primary visible heading; additional `appliedStereotypes` remain separate.
- BDD properties remain structured `part`, `reference`, `value`, `constraint`, or `flow` rows. A property type shown as another Block uses Association or Composition.
- BDD relationships are Association, Composition, Generalization, Dependency, and Comment Link. Composition is first-class and always points part source to whole target, with a target filled diamond and atomic Swap ends behavior.
- Any newly drawn edge incident to a Note becomes Comment Link.
- Specialist catalog entries may remain load/render compatible but are not available through generation, palettes, Show all, or semantic selectors.
- Canvas and SVG both render the Note's complete top-right dog-ear and the BDD Block's primary stereotype heading.

## Included Work

- Promote the core vocabulary into the canonical schema, mapping, rendering, generation, editor, validation, answer-key, context-generation, notation, and decision owners.
- Define the compatibility/authorability boundary without claiming runtime delivery.
- Add the runtime implementation slice to this group's plan.

## Not In Scope

- Runtime catalog, schema, generator, renderer, editor, sample, or test changes.
- Automatic migration or deletion of existing specialist documents.
- New diagram types or a general-purpose drawing palette.

## Target Areas

- `docs/02-design-and-features/00-diagram-json-schema.md`
- `docs/02-design-and-features/01-diagram-json-mapping-design.md`
- `docs/02-design-and-features/02-validation-design.md`
- `docs/02-design-and-features/03-rendering-design.md`
- `docs/02-design-and-features/04-generation-design.md`
- `docs/02-design-and-features/06-answer-key-generation-design.md`
- `docs/02-design-and-features/editor-ui-design.md`
- `docs/02-design-and-features/diagram-schemas/`
- `docs/02-design-and-features/decision-decisions.md`
- `docs/01-architecture/02-frontend-architecture.md`

## Exit Criteria

- All active design owners state the same exact node/edge lists and BDD representation.
- Composition direction, target marker, Swap ends behavior, Note linking, and Note dog-ear parity are unambiguous.
- Runtime status remains in the current-state board and a separate implementation slice.

## Previous Slice

- [`11-semantic-model-frontend-sync.md`](11-semantic-model-frontend-sync.md)

## Next Slice

- [`13-core-vocabulary-runtime.md`](13-core-vocabulary-runtime.md)

## Outcome

**Completion.** The approved bounded profiles, one-Block BDD stereotype model, first-class part-to-whole Composition, universal Comment Link inference, retained compatibility boundary, and Note dog-ear parity are specified across the active owners.

**Verification.** The contract was cross-checked against the normative research extraction, current catalog/profile/prompt/editor behavior, all three notation owners, historical MVP vocabulary, and realistic training/example usage. No runtime claim is made.

**Deviations.** Composition intentionally becomes a GraphPilot edge identity rather than UML association-end aggregation, prioritizing one unambiguous AI/editor representation. BDD primary `stereotype` intentionally restores a dedicated display field instead of overloading additional `appliedStereotypes`.

**Follow-up.** Slice 13 implements and verifies the atomic backend/frontend/runtime cutover after the parallel generation and editor work is integrated.
