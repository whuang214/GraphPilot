# Slice 06: New Diagram Chooser

## Purpose

Replace one landing-page button per diagram type with a searchable chooser that remains usable as the supported type catalog grows.

## Background

The landing page currently hardcodes Activity, Use Case, BDD, and Custom in a fixed two-column grid. The card is already 448 pixels wide and 417 pixels tall with only four types, so adding one button per future type will not scale.

The Diagram vs Notation organization control is intentionally limited to the shape palette. The New Diagram chooser needs search and a compact list, not the same grouping UI.

## Design

- Replace the four-card New blank section with one primary **New diagram…** action.
- Open an accessible modal containing a search field and scrollable type list.
- Centralize diagram type label, description, notation badge, keywords, and default blank name in one frontend descriptor source consumed by Home and `createBlankDiagram`.
- Search type label, canonical ID, description, notation, and keywords; preserve deterministic display order for an empty query.
- Selecting a type immediately starts the same valid unsaved canonical blank and closes the chooser.
- Preserve Open file, drop-to-open, Recents, Clear recents, IDE-link bypass, and error recovery unchanged.

## Included Work

- Add centralized diagram-type descriptors and pure filtering tests.
- Refactor Home into one New diagram action plus chooser state.
- Implement keyboard focus management, Escape/cancel, empty search, and screen-reader labels using existing UI primitives.
- Update blank-diagram factory tests to consume the centralized descriptors without changing canonical output.
- Update landing component and browser E2E coverage.
- Update `editor-ui-design.md` (*Opening or starting a diagram*), `02-frontend-architecture.md` (blank-session entry), `decision-decisions.md` (searchable type chooser), and this slice's Outcome when implemented.

## Not In Scope

- New diagram types, generation calls, templates, favorites, or recent type history.
- Diagram/notation grouping or sorting controls in the chooser.
- Project/workspace browsing.
- Changes to Open/drop/Recents persistence or file ownership.

## Target Areas

- `frontend/src/editor/components/Home.tsx` and component tests
- `frontend/src/editor/lib/diagramFactory.ts` and tests
- New frontend diagram-type descriptor helper under `frontend/src/editor/lib/`
- Existing modal/UI primitives
- `frontend/e2e/smoke.spec.ts`
- Active landing/editor/decision owners

## Exit Criteria

- The landing page shows one New diagram action rather than one button per type.
- The chooser lists and searches Activity, Use Case, BDD, and Custom and can scale without increasing landing-page height.
- Keyboard users can open, search, choose, cancel, and return focus correctly.
- Every selection creates the same valid unsaved canonical diagram and first-save behavior remains Save As.
- IDE links, Open file, drop, Recents, Clear recents, and load-error recovery are unchanged.
- Focused tests and `npm run verify` pass.

## Previous Slice

- [`05-palette-organization.md`](05-palette-organization.md)

## Next Slice

- None — this closes the Editor Usability group.

## Outcome

**Completion:** Replaced four landing cards with one primary **New diagram…** action and an accessible searchable, scrollable modal. A new ordered descriptor source owns type label, description, notation badge, keywords, and default blank name; Home and `createBlankDiagram` consume the same source without changing canonical blank output.

**Deviation:** Added a reusable `data-modal-initial-focus` preference to the existing modal so this chooser opens directly in search while retaining its focus trap, Escape/backdrop close, and opener restoration. Open file is now visually secondary to the single primary New diagram action; behavior is unchanged.

**Verification:** `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build, 454 unit/component tests, and 40 Chromium E2E tests. Pure tests cover descriptor completeness/order and label/ID/description/notation/keyword search; factory tests prove all four canonical blanks are unchanged. Component/browser coverage proves initial focus, search, empty state, keyboard selection, Escape/cancel restoration, unsaved Save As, and unchanged Open/Recents/error behavior. A read-only implementation audit found no code or scope defect.

**Follow-up:** None. This closes the six-slice Editor Usability group.
