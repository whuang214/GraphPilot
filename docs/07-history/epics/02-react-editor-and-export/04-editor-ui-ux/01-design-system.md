# Slice 01: Design System

## Purpose

Replace the editor's ad-hoc inline styling with a coherent, themeable design system so the rest of the `04-editor-ui-ux` group (Epic 2) can build polished UI consistently. Establish design tokens (color, spacing, typography, radii, shadows, z-index, focus ring) and a small primitive component set, then port the current chrome to them without changing any functionality.

## Background

- This is the `04-editor-ui-ux` group's **foundation slice** (Epic 2): a styling/structure base with no editor behavior changes, and it unblocks every later `04-editor-ui-ux` slice (Epic 2).
- The editor is styled almost entirely with **inline styles**: the header in `frontend/src/editor/EditorPage.tsx`, the `NodePalette`, and the `PropertyPanel` each hardcode their own colors, spacing, and borders. `frontend/src/index.css` and `frontend/src/App.css` are ~4 lines each, and there are no design tokens, theme, or shared components.
- This makes consistent polish (and dark mode in Slice 03) impractical and duplicative.
- The user has chosen **Tailwind CSS** as the styling approach. The toolchain is React 19 + Vite 8, which points cleanly at **Tailwind v4 with the `@tailwindcss/vite` plugin** (no PostCSS config needed). The linter is `oxlint` (no ESLint/Prettier), so no Tailwind ESLint plugin is involved and class ordering stays manual.

## Included Work

- Add Tailwind v4 via the `@tailwindcss/vite` plugin: wire it into `frontend/vite.config.ts` and add `@import "tailwindcss";` to `frontend/src/index.css`. Pin an explicit, vetted version (≥7 days old); no floating ranges (`latest`/`*`/unbounded `>=`).
- Define **design tokens** using Tailwind v4's `@theme` (CSS variables): surface/border/text/accent color scales plus semantic `success`/`warn`/`error`/`info`, spacing, radii, shadows, z-index, typography, and a focus-ring token. Seed the accent/stroke values from the canonical sample palette (e.g. the `#333333` edge stroke) so the chrome visually matches the diagrams.
- Build a small set of typed, accessible **UI primitives** under `frontend/src/ui/` styled with Tailwind: `Button`/`IconButton`, `Input`, `NumberInput`, `Select`, `ColorInput`, `Field` (label + control + hint/error), `Panel`, `Toolbar`, `Tooltip`, `Modal`, `Toast`/`Toaster`, `Badge`. (Whether to back these with a headless a11y lib like Radix is a decision to confirm; the default is hand-rolled.)
- Migrate the existing inline styles to Tailwind classes / primitives **without behavior or layout regressions**: the `EditorPage` header + `OpenControl`, `SaveBanner`, `Message`, `NodePalette`, and `PropertyPanel`.
- Keep the React Flow stylesheet import (`@xyflow/react/dist/style.css`); deeper canvas theming is Slice 03.
- Update `frontend/README.md` (styling/setup) and note the design-system foundation in `docs/01-architecture/02-frontend-architecture.md`.

## Not In Scope

- Layout / information-architecture restructure — the app shell, rails, and status bar (Slice 02).
- Minimap, snapping, zoom readout, and dark mode (Slice 03).
- New editing interactions: toolbar, undo/redo, multi-select, inline label editing (Slice 04).
- Inspector field restructure beyond a visual port (Slice 05).
- Any change to `customNodes.tsx` shape visuals (owned by Epic 2).
- Any change to the canonical schema, the supported style subset, or the save/load contract.

## Target Areas

- `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/index.css`, `frontend/src/App.css`
- `frontend/src/ui/` (new primitives)
- `frontend/src/editor/EditorPage.tsx` (style-only migration of header/banners/messages)
- `frontend/src/editor/components/NodePalette.tsx`, `frontend/src/editor/components/PropertyPanel.tsx` (style-only)
- `frontend/README.md`, `docs/01-architecture/02-frontend-architecture.md`

## Exit Criteria

- Tailwind v4 builds through Vite; `frontend/src/index.css` imports Tailwind and the tokens are defined via `@theme`.
- The UI primitive set exists under `frontend/src/ui/` and is used by the migrated chrome.
- The previously inline-styled header, palette, inspector, banners, and messages render via tokens / primitives with **no functional or visible regressions** to the existing flow.
- The load → edit → save round-trip is unchanged (adapters untouched; no canonical data changes).
- `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- Start of Epic 2's `04-editor-ui-ux/` group (a later phase, after `../03-comprehensive-shapes/10-bdd-block-compartments.md`).

## Next Slice

- `02-app-shell.md`

## Outcome

✅ Completed as planned. Added Tailwind v4 via `@tailwindcss/vite` (exact-pinned `tailwindcss`/`@tailwindcss/vite` 4.3.1), defined themeable design tokens in `index.css` (`@theme inline` + `:root` CSS vars, seeded from the prior inline colors, structured so a later `.dark` override works), added in-house primitives under `frontend/src/ui/` (`Button`, `Input`/`NumberInput`/`ColorInput`/`Select`/`Field`, `Badge`, plus a `cn` helper), and migrated the inline-styled chrome (`EditorPage` header/`OpenControl`/`SaveBanner`/`Message`, `NodePalette`, `PropertyPanel`) onto them. No behavior change; adapters/schema untouched. Deviation: `Panel`/`Modal`/`Toast`/`Toolbar`/`Tooltip` primitives are deferred to the slices that first use them (S02/S04/S05) to avoid unused code. Verified: `npm run lint`, `npm run build`, `npm run test` (40/40) pass; round-trip unaffected. Follow-up: none.
