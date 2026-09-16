# Slice 10: Node Fidelity

## Purpose

Make the custom node renderers read cleanly in dark mode (feature-list #1) and render the note shape's folded corner as a true SVG fold (#8), and bundle on-canvas resize handles (#6) since all three changes touch the same custom renderers. This is the **P1 node-fidelity pass** from the design doc's *Feature Requests and Known Issues* list.

## Background

- The app chrome already re-themes via React Flow v12 `colorMode` (Slice 03), but authored node visuals read poorly on a dark canvas — node shapes, some text, and diagram content aren't contrasted correctly in dark mode (#1).
- The note shape's top-right corner still renders as a cut-off, not a fold (#8).
- Nodes can only be resized via the inspector's width/height fields; there is no on-canvas resize (#6, P3 — bundled here because it touches the same renderers).
- The design doc is explicit that **authored diagram colors stay as-authored in either theme — only the surrounding app changes**; this slice must not recolor the user's diagram.

## Design

- Treat dark-mode legibility as a chrome/contrast problem around the nodes (borders, default text, handles, selection outline), not a recolor of authored fills. Where a node has no authored color, fall back to theme-aware tokens; where it has one, preserve it.
- Re-draw the note's folded corner as an inline SVG path (a visible diagonal fold with a subtle shadow) rather than the current CSS corner.
- Add React Flow `NodeResizer` to the resizable custom nodes; the resulting `width`/`height` flow back through the existing reverse adapter unchanged (no new fields).

## Included Work

- Dark-mode legibility pass across the shapes in `customNodes.tsx` (activity, use-case, BDD), pairing color with theme-aware tokens for chrome while preserving authored fills/strokes.
- Re-render the note's folded corner as SVG (visible fold) and tighten the other shapes' rendering.
- Add `NodeResizer` to the custom nodes with min-size constraints; ensure size round-trips to JSON.
- Add/extend unit tests in `editor/components/components.test.tsx` for the note fold and the resize → size mapping; visually confirm dark mode.

## Not In Scope

- New shapes or diagram types, or any change to authored color semantics.
- Auto-layout / smart edge routing (separate, out of scope per the design doc).
- Friendly inspector controls (#4 — Slice 11) and edge work (#3/#14 — Slice 12).

## Target Areas

- `frontend/src/editor/canvas/customNodes.tsx` (shape rendering, note fold, `NodeResizer`).
- `frontend/src/editor/shell/useColorMode.ts` + Tailwind tokens / CSS (dark-mode chrome).
- `frontend/src/editor/components/components.test.tsx`.

## Exit Criteria

- Node shapes, text, and handles are legible in both light and dark themes; authored diagram colors are unchanged in either theme (#1).
- The note shape shows a real folded corner (#8).
- Nodes can be resized on the canvas via handles, and the resulting size round-trips byte-stable to the saved JSON (#6).
- The load → edit → save round-trip stays byte-stable (no adapter/schema change, no runtime-field leak); `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `09-server-rendered-export.md`

## Next Slice

- `11-friendly-property-controls.md`

## Outcome

Complete on `epic-6-refinements` for the shipped riders (#8 note fold + #6 on-canvas resize); #1 dark-mode legibility remains parked (deferred to last).

**Delivered (#8 note fold).** The note draws a real folded corner: the cut top-right plus an SVG flap triangle (shaded underside + a border-color crease).

**Reverted / deferred (#1 dark-mode legibility).** The first token-based attempt was not legible on review (use-case actor too dark with its label blending in; block interiors too white since authored light fills are preserved by design). Reverted; #1 deferred until after the feature fixes. Future direction: draw.io-style transparent node interiors plus theme-aware outlines. Light mode is unchanged.

**Delivered (#6 on-canvas resize).** Selected nodes now show React Flow `NodeResizer` handles. A small `resize.ts` holds a pure `applyNodeResize` helper (clamps to a 40x30 minimum, writes the size into the node `style`) plus a `NodeResizeContext`; the custom nodes render a shared `ResizeControls` (visible only when selected) wired to the context, and `EditorPage` provides the handler (one undo snapshot on `onResizeStart`, live `style.width`/`height` update + `markEdited` on `onResize`). Size is kept in `style` — not React Flow's measured `width`/`height` — so the reverse adapter persists it and the save round-trip stays byte-stable.

**Verification.** npm run lint (0/0), npm run build (tsc + vite), npm run test (200 passed, incl. new `resize` tests; the adapter tests already cover style-size persistence + ignoring measured dims). Live drag-resize confirmed manually.

**Interaction correction.** Resize grabbers are 9×9 pixels instead of React Flow's 5×5 default. Initial/final control nodes default to 90×60, compact legacy 50-pixel nodes remove internal padding/gap so labels no longer clip, and SVG control glyphs keep the same capped radius as the canvas. Browser measurement confirmed legacy content at 50/50 with no overflow and all four grabbers at 9×9; full gates pass with backend 680 tests (3 skipped), frontend 412 unit/component tests, 33 E2E tests, lint clean, and production build.

**Follow-up.** Slice 10 is complete (#8 + #6 done; #1 dark mode still parked). Next: #7 shape-palette previews (Slice 14).
