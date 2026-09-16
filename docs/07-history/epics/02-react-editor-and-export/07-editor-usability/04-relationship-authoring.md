# Slice 04: Relationship Authoring

## Purpose

Expose the current diagram's supported relationship identities directly in the palette and make relationship type a primary edge property.

## Background

Only BDD currently shows relationship buttons, backed by a hardcoded preset list. Activity and Use Case show none even though the element catalog already defines their complete authorable edge subsets. A selected edge's Content tab shows only a read-only type label, while the editable Semantic Type field and semantic validation routing live in Advanced.

## Design

- Replace BDD-only next-edge state with one catalog-driven selected relationship semantic.
- Build palette relationship tools from `allowedEdgeSpecs(diagramType)` for Activity, Use Case, BDD, and Custom.
- Retain the current BDD glyph treatment and derive equivalent glyphs from dashed/source/target marker metadata for other diagram types.
- Reset the selected tool to the diagram type's default when opening a different diagram; keep selection stable while editing one diagram.
- Preserve Note incidence as a higher-priority Comment Link inference regardless of selected tool.
- Move editable edge identity into Content as **Relationship type** and route semantic-type validation there. Keep node identity behavior unchanged; the tab placement is reversible if later usability evidence contradicts it.
- Generalize semantic transitions so switching relationship type clears incompatible structured fields while preserving common description/metadata/applied stereotypes.

## Included Work

- Replace/generalize `RelationshipPresetId`, preset lookup, and edge-creation integration.
- Add catalog-driven relationship entries to the palette for every applicable diagram type.
- Move the edge semantic field and update tab indicators/error routing.
- Preserve BDD Composition direction/marker behavior and existing Swap ends.
- Add focused unit/component tests and browser create/edit/save coverage for each type, plus backend SVG verification for every newly exposed relationship tool's line and markers.
- Update `editor-ui-design.md` (*Relationships and labels* and *Properties panel*), `01-diagram-json-mapping-design.md` (semantic transitions), each affected per-type notation owner, `decision-decisions.md` (catalog-driven relationship tools), and this slice's Outcome when implemented.

## Not In Scope

- New edge semantic types or changes to backend authoring profiles.
- Dragging a relationship item onto the canvas as a standalone object; relationship buttons select the next-edge tool.
- Removing deterministic Note → Comment Link inference.
- Semantic endpoint validation during the gesture; typed validation remains authoritative after editing.
- Palette organization controls (Slice 05).

## Target Areas

- `frontend/src/editor/lib/relationshipPresets.ts` and tests
- `frontend/src/editor/lib/elementCatalog.ts`
- `frontend/src/editor/components/NodePalette.tsx`
- `frontend/src/editor/components/PropertyPanel.tsx` and component tests
- `frontend/src/editor/EditorPage.tsx`
- `frontend/e2e/smoke.spec.ts`
- Active editor/mapping/per-type notation/decision owners

## Exit Criteria

- Activity exposes Control Flow and Comment Link; Use Case exposes Association, Generalization, Include, Extend, and Comment Link; BDD retains its five current tools; Custom exposes its authorable generic relationships.
- The selected tool determines the next non-Note edge and renders the correct line/markers on canvas and SVG.
- Note incidence always creates Comment Link.
- A selected edge exposes editable Relationship type in Content; changing it removes incompatible data and persists clean canonical JSON.
- Semantic-type validation opens/marks Content rather than Advanced.
- Existing BDD preset, Composition, and Swap ends tests remain green.
- Focused tests and `npm run verify` pass.

## Previous Slice

- [`03-container-layering.md`](03-container-layering.md)

## Next Slice

- [`05-palette-organization.md`](05-palette-organization.md)

## Outcome

**Completion:** Replaced BDD-only preset aliases with exact catalog semantic identities and derived per-type relationship tools/glyphs for Activity, Use Case, BDD, and the Custom authorable union. The selected tool drives every non-Note edge; Note incidence still forces Comment Link. Editable **Relationship type** and edge semantic validation now live in Content, while node identity remains unchanged in Advanced.

**Deviation:** None. Semantic transitions preserve description/metadata/applied stereotypes, retain only compatible end/extend/control-flow fields, clear stale structured data, and re-derive markers/dashing immediately. No schema, backend profile, or endpoint-validation change was required.

**Verification:** `cd backend; uv run python manage.py test` passed 683 tests (4 skipped), including all authorable relationship line/dash/marker combinations. `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build, 439 unit/component tests, and 39 Chromium E2E tests. Browser coverage creates and saves selected relationships for Activity/Use Case/BDD/Custom, confirms default reset per opened diagram, edits Extend to Generalization from Content, verifies stale condition removal plus live dash/marker change, and retains Note inference, BDD Composition, and Swap ends. Two read-only implementation audits found no remaining material issue.

**Follow-up:** Slice 05 owns scope, organization, and unified node/relationship search in the palette.
