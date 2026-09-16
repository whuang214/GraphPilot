# Slice 07: Relationship Presets and Properties

## Purpose

Make common BDD relationships fast to configure and make node/edge properties easier to scan by combining semantic presets with a compact three-tab property panel.

## Design

- BDD presets are named UI compositions over canonical relationship identity and structured association ends; they do not create synthetic edge types.
- Presets cover the common plain association, shared aggregation, composition, generalization, dependency, and containment configurations supported by the BDD catalog.
- A preset makes its marker-bearing/owning end explicit and never silently swaps `source` and `target`.
- Applying a preset sets and clears the semantic/end fields it owns so stale aggregation or navigability cannot survive an incompatible choice; labels, styles, metadata, and unrelated valid detail remain intact.
- The inspector has three stable tabs grouping primary identity/common properties, structured semantic details, and layout/appearance.
- Repeated properties, parameters, qualifiers, stereotypes, item flows, constraints, and literals use compact rows with progressive detail rather than tall nested cards.
- Tab changes are presentation-only: drafts, validation flags, selection, and undo semantics remain intact.

## Included Work

- Add BDD relationship preset definitions, previews/names, application logic, and tests.
- Keep direct semantic-type and association-end editing available for configurations beyond the presets.
- Reorganize node, edge, and multi-selection inspector content into three tabs.
- Introduce reusable compact row/list controls with accessible add, remove, expand, and keyboard behavior.
- Preserve every supported structured node/edge field and existing friendly style control.
- Cover preset switching, incompatible-field cleanup, source/target end choice, tab switching, compact-row editing, validation markers, and multi-selection style behavior.

## Not In Scope

- New relationship semantics, feature kinds, or schema fields.
- Inferring a BDD relationship from node names or feature text.
- Hiding advanced canonical fields or replacing direct editing with presets only.
- Route manipulation beyond exposing already-supported route reset/details where appropriate.

## Target Areas

- `frontend/src/editor/components/PropertyPanel.tsx`.
- Reusable controls in `frontend/src/ui/` and property/preset helpers under `frontend/src/editor/lib/`.
- `frontend/src/editor/lib/elementCatalog.ts` and `frontend/src/editor/lib/edgePresentation.ts` where display metadata is needed.
- `frontend/src/editor/EditorPage.tsx` patch application and undo integration.
- Property-panel, preset, adapter, and accessibility-focused component tests.

## Exit Criteria

- Each supported BDD preset produces the intended canonical `semanticType` and source/target end data, including correct marker ownership.
- Switching presets removes incompatible preset-owned fields without erasing unrelated canonical data.
- Advanced direct editing remains available after a preset is applied.
- Node, edge, and multi-selection inspectors use the same three-tab structure and retain all supported fields.
- Repeated structured values can be added, edited, expanded, and removed in compact rows with keyboard-operable controls.
- Tab switching does not lose edits, reset validation markers, or create undo entries by itself.
- Component, adapter, and relevant frontend verification pass.

## Previous Slice

- [`06-bdd-visual-cleanup.md`](06-bdd-visual-cleanup.md)

## Next Slice

- [`08-integrated-parity.md`](08-integrated-parity.md)

## Outcome

**Completed.** The BDD palette and edge Content tab expose canonical presets for plain/navigable association, shared aggregation, composition, generalization, dependency, containment, and supported callout links. Preset transitions preserve unrelated description/metadata/stereotypes and clear incompatible end/flow data. Node, edge, and bulk inspectors use fixed Content/Appearance/Advanced tabs; compact structured rows share one expanded key, empty feature groups collapse behind one Add content control, content-fit and route resets are explicit, identifiers are copyable, and status dots/validation paths mark and open the responsible tab.

**Verification.** Component tests cover tab keyboard behavior/persistence, multi-selection, validation targeting, compact rows, all-field editing, whole-end preset application, route resets, content-fit, and palette preset selection; Playwright exercises structured BDD inspection. Final aggregate gate evidence is recorded in Slice 08.
