# Slice 08: Integrated Parity

## Purpose

Prove the refinement set as one coherent workflow and close behavioral parity across source sessions, canonical round-trip, the React canvas, server SVG, and SVG-derived PNG.

## Design

- One representative BDD fixture combines empty and populated classifiers, marker variants, obstacle avoidance, conditional fan-out, manual anchors/waypoints, moved labels, and relationship presets.
- Geometry comparisons use canonical points, anchors, lanes, labels, and marker ends rather than brittle browser pixel snapshots.
- SVG is the canonical exported artifact and PNG is rasterized from that SVG; no canvas screenshot path is introduced.
- Legacy fixtures without route geometry remain first-class compatibility cases.
- Source-session tests prove persistence ownership and repository matching separately from render parity.

## Included Work

- Add integrated BDD parity fixtures and deterministic canvas/backend geometry assertions.
- Exercise automatic and manual routes through load → edit → validate → save → reload → render → PNG.
- Compare marker ownership/orientation, label positions, compact/expanded classifiers, route obstacle clearance, and conditional lanes across canvas and SVG.
- Exercise workspace, matched external, unmatched external, ambiguous match, dropped read-only, and Save As flows against the unified session model.
- Run schema/type parity, adapter round-trip, undo/redo, rendering, rasterization, unit, build, lint, and end-to-end gates.
- Update canonical architecture/design/notation owners and the Epic 2 plan/status only when implementation evidence supports those updates.

## Not In Scope

- New functionality beyond Slices 01–07.
- A second export renderer, DOM screenshot export, PDF, or browser-specific image semantics.
- Pixel-identical font rasterization between browser text and server SVG.
- Relaxing canonical validation to make parity fixtures pass.

## Target Areas

- Frontend unit tests and `frontend/e2e/` source/edit/export scenarios.
- `backend/tests/core/test_render_service.py` and schema/validation tests.
- Representative canonical fixtures and render-gallery/parity utilities already used by the repository.
- `frontend/src/adapters/reactFlow.ts`, routing/presentation helpers, and export helpers for integration-only fixes.
- Canonical frontend architecture, schema, rendering, editor UI, BDD notation, decision, epic-plan, and live-status owners when delivery occurs.

## Exit Criteria

- The representative BDD fixture has equivalent node structure, route geometry, marker ends, and label placement on the canvas and in SVG.
- PNG is demonstrably derived from the same SVG and preserves its visible geometry and notation.
- Legacy route-free diagrams validate, render automatically, and round-trip without new geometry.
- Manual overrides survive save/reload; snapped-back overrides remain omitted.
- Workspace and external session scenarios save only to their active persistence owner, including unmatched and ambiguous repository cases.
- Backend verification (`cd backend; uv run python manage.py test`) passes.
- Frontend verification (`cd frontend; npm run verify`) passes.
- Any deviations or follow-ups are recorded in this slice's outcome rather than presented as completed behavior elsewhere.

## Previous Slice

- [`07-relationship-presets-and-properties.md`](07-relationship-presets-and-properties.md)

## Next Slice

- End of Epic 2's `05-frontend-refinement/` group.

## Outcome

**Completed.** One refinement set now spans the optional route schema/runtime guard, exact adapter round-trip, frontend/backend shared route fixtures, obstacle and conditional-lane resolver, editable route controls, source-session lifecycle, BDD notation/presets/compact classifiers, and the three-tab inspector. Browser vertical slices compare canvas and SVG coordinates, persist/reload manual geometry, verify every custom marker, prove repository matching/revision conflicts and stale-completion isolation, and retain SVG-derived PNG export.

**Audit fixes.** The every-file frontend audit additionally closed resolve-request timeout/shape validation, picker/save completion races, reconnect anchor precedence/edge-ID stability, cloned-waypoint translation, collision-safe snap-back, pointer-listener cleanup, route-reset tests, validation-targeted inspector tabs, new/generated empty-block sizing, landmarks, category ARIA linkage, and dark/light contrast. DevTools found no console errors; Lighthouse accessibility and best-practices both score 100.

**Verification.** `cd backend; uv run python manage.py test` passes 534 tests (3 skipped). `cd frontend; npm run verify` passes lint with zero warnings/errors, production build/typecheck, 386 unit tests, and 24 Playwright tests. `git diff --check` is clean. No dependency, authentication, database, or second-renderer changes were introduced.
