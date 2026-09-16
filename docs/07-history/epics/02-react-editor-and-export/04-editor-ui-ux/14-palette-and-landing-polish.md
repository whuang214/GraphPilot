# Slice 14: Palette and Landing Polish

## Purpose

Upgrade the shape palette from a plain text list to visual previews with collapsible categories and search (feature-list #7), tighten the landing/home layout and visual hierarchy (#2), and auto-dismiss the lingering "Saved." banner (#15). This is the design doc's **P3** polish pass; #15 rides along as a small, self-contained fix.

## Background

- The shape palette lists shapes as text with no visual preview, which feels underwhelming (#7).
- The landing/home screen (introduced in Slice 08) works but could be neater — its layout and visual hierarchy can be tightened (#2).
- The "Saved." banner never clears: `SaveBanner` renders while `saveState.status === 'saved'`, which is only reset to `idle` on the next edit, so it stays up indefinitely (#15). A success toast already fires, so the banner can auto-clear (or be reserved for errors).

## Design

- **Palette (#7):** render a small visual preview for each shape (reuse the node glyphs / a lightweight SVG per shape), group shapes into collapsible categories, and add a search filter; drive it from the existing `palette.ts` definitions so the drag payload is unchanged.
- **Landing (#2):** tighten spacing, hierarchy, and alignment of the Open-file + recents landing in `Home.tsx` using the existing primitives — layout polish only, no change to the two open flows.
- **Save banner (#15):** auto-clear the `saved` state after a short delay (or keep the banner for errors only), matching the design's "brief toast" intent; errors remain until addressed.

## Included Work

- Add shape previews, collapsible categories, and search to `NodePalette.tsx`, backed by `palette.ts`.
- Tighten the landing layout/hierarchy in `Home.tsx` (and any shared landing used by the missing-path / load-error states).
- Auto-dismiss the success `SaveBanner` in `EditorPage.tsx` (timer → `idle`), leaving error banners.
- Update/extend unit tests (`palette.test.ts`, `editor/components/components.test.tsx`).

## Not In Scope

- New shapes or diagram types; any change to the drag payload format or the open flows (owned by Slice 08).
- Node-renderer fidelity (Slice 10) and inspector controls (Slice 11).

## Target Areas

- `frontend/src/editor/components/NodePalette.tsx`, `frontend/src/editor/lib/palette.ts`.
- `frontend/src/editor/components/Home.tsx`.
- `frontend/src/editor/EditorPage.tsx` (SaveBanner auto-dismiss).
- Frontend unit tests (`editor/lib/palette.test.ts`, `editor/components/components.test.tsx`).

## Exit Criteria

- The palette shows visual shape previews with collapsible categories and a working search (#7).
- The landing/home layout is visibly tightened with clearer hierarchy (#2).
- After a successful save the "Saved." banner auto-dismisses (errors persist) (#15).
- The load → edit → save round-trip stays byte-stable; `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `13-container-un-trapping.md`

## Next Slice

- `15-deferred-editor-polish.md`

## Outcome

Complete on `epic-6-refinements` — the bug-first re-prioritization split this slice: #15 + #2 shipped in Phase 1, and #7 (the palette feature) shipped in Phase 2.

**Delivered (Phase 1).** #15 saved-banner auto-dismiss (a ~2.5s timer clears the success state; errors persist), and #2 landing/home polish — the landing is now a centered card with clearer hierarchy, and the recents list shows each file's name (bold) over its directory (muted) instead of one long truncated path (`Home.tsx`). Behavior/props unchanged; the landing test was updated for the new recents layout.

**Delivered (Phase 2 — #7 palette).** The palette now shows a monochrome SVG preview glyph per shape, groups shapes into collapsible categories (Activity / Use case / Block / Annotation), and adds a search box that filters by label/type and auto-expands categories while searching. Driven by a new `groupedPaletteItems()` over the existing `palette.ts` catalog (each item gained a `category` field); the drag payload (`type`/`semanticType`/`label`) is unchanged, so the canvas drop / save behavior is identical. The Rail still owns scrolling, so the palette stays layout-agnostic.

**Verification.** npm run lint (0/0), npm run build (tsc + vite), npm run test (203 passed — added `groupedPaletteItems` + `NodePalette` tests).
