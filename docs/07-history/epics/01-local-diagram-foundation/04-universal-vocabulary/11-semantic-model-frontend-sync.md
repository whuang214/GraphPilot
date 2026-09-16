# Slice 11: Exact Semantic Model Frontend Sync

## Purpose

Bring the React editor onto the exact UML 2.5.1 / SysML 1.6 semantic identities and structured data model delivered by backend commit `5dc1378`. The browser must load, render, author, save, and preview the same canonical model as generation, validation, and SVG export.

## Included Work

- Add one typed frontend presentation mirror of the backend element catalog and guard every committed example against it.
- Drive the per-type palette, primitive dispatch, minimap, default sizes, edge defaults, containers, markers, and line styles from that catalog.
- Render the complete primitive set, derived feature compartments, extension points, port adornments, relationship keywords/guards, association-end adornments, and item flows.
- Replace legacy `classifier`/`dependency` stereotype and free-text compartment editing with exact semantic selectors and structured node/edge editors.
- Whitelist every canonical structured data field through loaded, edited, canvas-created, and cloned React Flow round-trips.
- Keep the optional directional override while preventing it from relocating fixed UML/SysML markers.

## Not In Scope

- New diagram types or a new-file workflow.
- A browser-facing catalog API; the frontend mirror remains a typed presentation concern guarded against all committed examples.
- Changes to backend semantic behavior from `5dc1378`.

## Exit Criteria

- All 48 committed examples resolve to known frontend catalog entries and round-trip without semantic loss.
- Activity, use-case, and BDD examples render their exact node/relationship identities and structured adornments on the canvas.
- Palette-created and inspector-edited elements save canonical structured JSON.
- Canvas and server SVG notation remain in parity for the changed semantic families.
- Backend tests and `frontend` `npm run verify` pass; representative diagrams are checked in a real browser.

## Outcome

✅ Completed. The React editor now consumes exact UML/SysML semantic identities through a typed 97-entry frontend catalog mirror, with per-type palette subsets plus a universal toggle. `gpNode` covers every backend render primitive; edges derive catalog markers/dashes and structured association-end, keyword, guard, condition, item-flow, and containment notation.

**Authoring and round-trip.** The inspector edits exact node/relationship types and canonical structured fields (features, extension points, definition/constraint/port/join data, association ends, flows, metadata, and applied stereotypes). The reverse adapter whitelists those fields for loaded, canvas-created, and cloned elements; all 48 committed examples are catalog-checked and round-trip guarded.

**Deviation/fix.** Real-browser preview exposed a backend SVG duplication when a first-class `include`/`extend` edge already carried its canonical keyword label. The renderer now derives the keyword only when absent and honors permitted `data.arrow` overrides without moving fixed structural markers; regression tests restore canvas/SVG parity.

**Verification.** Backend `python manage.py test` → **372 OK**. Frontend `npm run verify` → lint **0 errors** (5 pre-existing warnings), production build clean, **331 unit tests**, and **12 Playwright e2e tests**. Headless real-browser checks covered activity, structured BDD live editing, use-case extension points/`extend`, console cleanliness, and server SVG preview parity.
