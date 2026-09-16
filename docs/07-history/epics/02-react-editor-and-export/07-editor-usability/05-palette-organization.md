# Slice 05: Palette Organization

## Purpose

Let the shape palette scale across a larger catalog by scoping and organizing nodes and relationships without weakening bounded authoring profiles.

## Background

The palette is implicitly filtered by the active diagram and hard-grouped as Common/UML/SysML. Its Show all checkbox switches to every authorable entry, but there is no explicit organization control. BDD relationship tools disappear during search instead of participating in it.

Per user decision, Diagram vs Notation organization belongs only in the shape palette, not the New Diagram chooser.

## Design

- Replace the ambiguous Show all checkbox with an explicit scope control: **Current diagram** (default) or **All authorable**.
- Add an **Organize by** control with **Diagram** (default) and **Notation**.
- Diagram organization uses deterministic groups: Shared, Activity, Use Case, BDD, and Custom-only. A semantic type appears once; entries authorable in multiple core diagrams belong to Shared.
- Notation organization uses Common, UML, and SysML.
- Each group separates Shapes and Relationships while sharing one search query.
- Search matches label, semantic type, category, diagram family, and notation; it forces matching groups open.
- Sort labels alphabetically within each subsection while preserving deliberate group order.
- Keep drag, double-click, keyboard add, selected next-relationship tool, and bounded authorability intact.

## Included Work

- Add palette scope/grouping types and pure catalog grouping/filtering helpers.
- Refactor `NodePalette` rendering for nodes and relationship tools from Slice 04.
- Add accessible labels, persisted-in-session control state, empty states, and collapsed-group behavior.
- Replace/update existing Show all tests and add the complete grouping/search matrix.
- Add browser coverage for Current/All, Diagram/Notation, search, drag, keyboard add, and relationship selection.
- Update `editor-ui-design.md` (*The workspace at a glance* Shapes palette description), `decision-decisions.md` (bounded Current/All organization), and this slice's Outcome when implemented.

## Not In Scope

- Diagram/notation grouping in the landing-page New Diagram chooser.
- Exposing retained compatibility-only or non-authorable specialist entries.
- User-defined categories, persisted palette preferences across browser restarts, favorites, or recent shapes.
- Backend catalog or schema changes.

## Target Areas

- `frontend/src/editor/lib/palette.ts` and tests
- `frontend/src/editor/lib/elementCatalog.ts` and tests
- `frontend/src/editor/components/NodePalette.tsx` and component tests
- `frontend/e2e/smoke.spec.ts`
- Active editor/palette/decision owners

## Exit Criteria

- Current diagram scope exposes exactly that type's bounded node and relationship set.
- All authorable scope exposes every authorable semantic and no compatibility-only semantic.
- Diagram organization produces Shared/Activity/Use Case/BDD/Custom-only without duplicate semantic entries.
- Notation organization produces Common/UML/SysML consistently.
- Search finds both shapes and relationships and keeps all matching groups visible.
- Existing drag, double-click, keyboard, and relationship-tool behavior remains intact.
- Focused tests and `npm run verify` pass.

## Previous Slice

- [`04-relationship-authoring.md`](04-relationship-authoring.md)

## Next Slice

- [`06-new-diagram-chooser.md`](06-new-diagram-chooser.md)

## Outcome

**Completion:** Replaced the ambiguous Show all checkbox with explicit Current diagram/All authorable scope and Diagram/Notation organization. One pure catalog projection groups shapes and relationships into Shared/Activity/Use Case/BDD/Custom-only or Common/UML/SysML, sorts each subsection alphabetically, deduplicates semantics, and searches labels, identities, categories, diagram families, and notation.

**Deviation:** Scope, organization, and collapsed groups persist in `sessionStorage` so editor remounts retain the working view without creating a cross-browser preference. Custom current scope intentionally equals the bounded all-authorable union established by the catalog; compatibility-only entries remain excluded.

**Verification:** `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build, 446 unit/component tests, and 40 Chromium E2E tests. Pure coverage verifies exact current profiles, the 26-entry all-authorable union, both group orders, no duplicates/leakage, unified search, and sorting. Component/browser coverage verifies remount/reload session persistence, collapse/search behavior, drag, keyboard add, canonical payloads, and stable relationship selection. Two read-only implementation audits found no remaining material issue.

**Follow-up:** Slice 06 owns the searchable New Diagram type chooser; palette organization does not transfer to that landing control.
