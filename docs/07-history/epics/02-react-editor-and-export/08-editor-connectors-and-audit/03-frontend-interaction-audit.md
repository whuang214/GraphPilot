# Slice 03: Frontend Interaction Audit

## Purpose

Audit the complete frontend after the connector changes, exercise every authorable node through real browser movement and persistence, and close or explicitly report every observed defect.

## Background

The connector changes touch palette state, selection, custom handles, canonical route data, edge controls, and backend render parity. Existing tests are broad but no single browser matrix moves all 17 deduplicated authorable node identities (19 profile entries because Note is shared by three core profiles). A focused post-change audit is required before treating the editor as fully verified.

## Design

- Audit all frontend source, configuration, unit/component tests, and E2E flows for correctness, parity, stale behavior, accessibility, and missing high-value coverage.
- Build a deterministic browser fixture containing the 17 unique authorable nodes across Activity, Use Case, BDD, and Custom profiles.
- Move every node by a real pointer gesture, verify the node—not a connection handle—moves, save, inspect canonical positions, reload, and confirm all nodes remain usable.
- Exercise representative resize, inline rename, multi-select, undo/redo, duplicate/delete, containment, reconnect, relationship identity, route mode, anchors, labels, validation, theme, rail resizing/collapse, preview/export, and responsive overflow flows.
- Recheck every catalog relationship tool family, primitive boundary family, diamond cardinal/sloped areas, and straight/orthogonal marker family without duplicating lower-level tests unnecessarily.
- Inspect browser console/network state and use DevTools for DOM/interaction evidence where browser automation alone is insufficient.
- Fix regressions and bounded adjacent defects that have an unambiguous root-cause correction; report unresolved or product-expanding findings instead of silently broadening scope.

## Included Work

- Add the all-authorable movement/save/reload browser matrix and any focused regression tests exposed by the audit.
- Run independent bounded code-review passes over editor state/persistence, palette/inspector/accessibility, canvas geometry/routing, and test coverage.
- Drive real Chromium/Edge sessions for interaction, console, network, and visual checks; clean up every automation session.
- Address in-scope findings across frontend code/tests and parity-sensitive backend code when required.
- Update testing/frontend/editor docs, current-state status, this slice's `## Outcome`, and report all findings by severity and disposition.

## Not In Scope

- New product features unrelated to the connector work.
- Live LLM/provider calls, generation certification, or unrelated Epic 3 evaluation changes.
- Native file-picker automation beyond the existing documented manual boundary.
- Claims that every browser/OS combination is certified; the supported automated target remains Chromium on Windows.

## Target Areas

- Complete `frontend/src/`, `frontend/e2e/`, and frontend tool configuration
- `frontend/e2e/seed.ts` and `frontend/src/editor/lib/elementCatalog.test.ts`
- Affected backend schema/render parity tests
- `frontend/README.md` and `frontend/src/editor/README.md`
- `docs/03-development-and-delivery/01-testing-strategy.md`
- Active editor architecture/design/decision owners
- Epic 2 plan, current-state board, and this slice outcome

## Exit Criteria

- A browser test moves all 17 unique authorable nodes and proves canonical save/reload position persistence.
- Every authorable node remains selectable and does not accidentally start a connection from its interior.
- Connector identity/mode, diamond cardinal/sloped boundaries, primitive anchors, reconnect, labels, containment, and route controls have passing focused coverage.
- Full source/config/test review finds no unresolved high-severity or in-scope medium-severity defect.
- Browser console/network inspection shows no unexplained application errors or failed requests in exercised success paths.
- `npm run verify`, affected backend tests, the full backend test command, and `git diff --check` pass or any unrelated pre-existing failure is proven and reported.
- The final report lists every finding, fix, deferred item, exact command, and result without overstating untested platforms or native picker behavior.

## Previous Slice

- [`02-straight-and-orthogonal-routing.md`](02-straight-and-orthogonal-routing.md)

## Next Slice

- No further slice is planned in this group; findings that require product expansion return to the backlog or a separately audited plan.

## Outcome

**Completion:** Audited the complete frontend source/configuration/test surface through four bounded review passes plus Chromium/Edge interaction and DevTools inspection. Added a deterministic Custom fixture for all 17 deduplicated authorable node identities and a browser matrix that moves each node by a real pointer gesture, proves selection rather than connection creation, saves and inspects canonical positions, reloads the rendered positions, reselects every node, and rejects console warnings/errors or failed success-path responses.

**Deviations:** No planned coverage was removed. The audit fixed three bounded defects: Diagram Information now closes on Escape/outside click and restores trigger focus; pointer-only non-cardinal connection samples are hidden from assistive technology while cardinal controls remain keyboard-addressable; and the inline help button exposes the meaningful `Keyboard shortcuts` name. A narrow-window policy was not invented inside the audit: with both rails expanded, 640px collapses the canvas to zero width and 680px leaves about 11px, while 760px remains overflow-free but narrow. That product choice is recorded in the backlog.

**Verification:** `cd frontend; npm run verify` passed lint with 0 warnings/errors, production build/typecheck, 419 unit/component tests, and 43 Chromium E2E tests. The live Edge session exercised all-authorable rendering, rail keyboard resizing/collapse, modal and popover focus/dismissal, multi-select, duplicate/delete/undo, inline rename, node resize/undo, theme, responsive overflow, and backend SVG preview; expected success-path requests returned 200 and final DevTools inspection found no unexplained console error. `git diff --check` passed. The canonical backend command ran 849 tests with 5 skipped and two errors confined to concurrent unstaged context/readiness changes whose tests still call the removed `ContextPersistenceService.save_diagram_request`; this slice changes no backend file, and the last independently clean backend baseline remains 848 passed with 5 skipped.

**Follow-up:** Design and schedule the deferred narrow-window rail behavior before claiming narrow/mobile support. Native picker behavior remains the documented manual boundary, and the automated certification target remains Chromium on Windows rather than a cross-browser matrix.
