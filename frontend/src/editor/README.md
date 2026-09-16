# editor/

The diagram editing surface. `EditorPage.tsx` is the composition root (imported by
`src/App.tsx`); everything else is grouped **by kind** into subfolders. Tests are
**co-located** with the code they cover (`foo.ts` + `foo.test.ts`).

## Import convention

Cross-folder imports use the **`@/` alias** (`@` → `src/`), e.g.
`import { clone } from '@/editor/lib/clone'`. Same-folder imports stay relative
(`./sibling`). The alias is configured in `tsconfig.app.json` (`paths`),
`vite.config.ts`, and `vitest.config.ts`.

## Layout

```text
editor/
  EditorPage.tsx     composition root (the page App.tsx renders)
  components/        feature UI (React components)
  canvas/            the React Flow rendering surface
  shell/             app chrome (top bar, status bar, rails)
  lib/               pure logic / helpers (no JSX)
  hooks/             React hooks + contexts
```

## `components/` — feature UI
`Home` (landing/empty state + searchable descriptor-driven New Diagram chooser), `Toolbar` + `ToolbarMore` (actions + responsive overflow),
`PropertyPanel` (Content/Appearance/Advanced core semantic, Content-tab edge identity, BDD primary-stereotype/structured-data, route mode, and style inspector), `NodePalette` (bounded Current/All scope, Diagram/Notation shape organization, unified search, and one selected/next-edge relationship/mode tray),
`ExportMenu` (SVG/PNG), `PreviewMenu` (server render + diff), `JsonDiffView` (pending-change diff), `ShortcutsHelp`; the retained `WorkspaceBrowser` module has no product-surface entry point.

## `canvas/` — rendering surface
`customNodes` (core plus compatibility render primitives, full-side connection strips, overlapping diamond slope/cardinal targets, display-tiered containers/content, Block headings, complete Note dog-ears, and compact/derived feature compartments), `FloatingEdge`
(primitive-aware straight plus minimal automatic/editable orthogonal routing, anchors/soft cardinal aim-lock/semantic markers/labels/end adornments), `HelperLines` (alignment guides overlay), `nodeTypes` (React
Flow node registry), `EmptyOverlay`, `ZoomStatus`, `miniMap`.

## `shell/` — app chrome
`TopBar` (document identity + source-information popover + actions), `StatusBar` (node/edge counts + save state), `Rail`
(collapsible, drag-resizable palette/inspector rails), `useColorMode` (light/dark),
`useRail` (rail width/collapse state).

## `lib/` — pure logic / helpers
`elementCatalog` (typed backend-catalog presentation mirror), `bddCompartments` (derived
feature rows/sizing), `edgePresentation`, `palette`, `nodePatch`, `alignmentGuides`,
`clone`, `containment`, `edgeRouting`/`edgeRouteEdit`, `relationshipPresets`, `exportImage`, `fileSystem`, `inlineLabel`,
`diagramTypes`/`diagramFactory`, `jsonDiff`, `nodeStyle`, `recents`, `resize`, and `validation`.

## `hooks/` — hooks + contexts
`useUndoRedo` (undo/redo stack), `editorColorMode` (editor color-mode context + hook).
