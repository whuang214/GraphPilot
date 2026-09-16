# Slice 04: Toolbar and Editing

## Purpose

Make day-to-day editing fast and forgiving. Today the editor supports moving, connecting/ reconnecting, relabeling (via the panel), resizing, recoloring, and delete-key removal — but there is no undo, no duplicate/copy-paste, no bulk operations, no in-place renaming, and no keyboard shortcuts. This slice closes those gaps.

## Background

- `frontend/src/editor/EditorPage.tsx` tracks a single `dirty` flag and the loaded diagram as the baseline; there is no history stack, so a misstep cannot be undone.
- Relabeling requires selecting the element and editing the `PropertyPanel`; there is no double-click-to-rename on the canvas.
- These are the Tier A/B items from the backlog "Robust editor" theme (undo/redo, copy/paste, multi-select) that are promoted into Epic 2's `04-editor-ui-ux` group.
- Inline label editing touches `customNodes.tsx`, so this slice is sequenced after the Epic 2 renderer slices (S05-S08) land; everything stays frontend-only and does not change the save contract.

## Included Work

- A **floating toolbar** (React Flow `<Panel>`): zoom in/out/fit, undo, redo, duplicate, delete, and lock/unlock — built from the Slice 01 primitives and surfacing the Slice 03 zoom %.
- **Undo/redo**: a history-stack hook (e.g. `frontend/src/editor/hooks/useUndoRedo.ts`) snapshotting `nodes`/`edges` on each `markEdited`, with a capped depth. Frontend-only; the save payload is unchanged.
- **Inline label editing**: double-click a node to edit its label in place (writes back to `data.label`, consistent with the panel). This requires a small hook inside `customNodes.tsx`, so it lands **after Epic 2 S05-S08**.
- **Copy / paste / duplicate**: clone selected nodes/edges with **fresh ids** (reusing the palette's id helpers) and a position offset; preserve `type`/`data.semanticType`/`gpStyle`.
- **Multi-select bulk actions**: leverage React Flow's shift-drag selection box; support bulk move, bulk delete, and bulk style (applies a panel patch to all selected).
- **Keyboard shortcuts** (undo/redo, copy/paste/duplicate, delete, select-all, fit) plus a **shortcuts help modal** (Slice 01 `Modal`).
- Confirm new/cloned elements still convert through the reverse adapter with the correct `node.type` + `data.semanticType` (extend `frontend/src/adapters/reactFlow.test.ts` coverage).
- Update `docs/01-architecture/02-frontend-architecture.md` (editor capabilities) and `frontend/README.md`.

## Not In Scope

- Any new canonical schema fields or new supported style keys.
- Autosave and validation surfacing (Slice 05).
- Workspace browser / export (Slice 06).
- Changes to `customNodes.tsx` shape visuals beyond the inline-label-edit affordance (Epic 2 owns the renderers).
- Auto-layout / orthogonal edge routing (backlog).

## Target Areas

- `frontend/src/editor/EditorPage.tsx` (toolbar wiring, selection/clipboard, shortcuts)
- `frontend/src/editor/hooks/useUndoRedo.ts` (new), toolbar + shortcuts-help components (new)
- `frontend/src/editor/canvas/customNodes.tsx` (inline label editing — **after Epic 2 S05-S08**)
- `frontend/src/adapters/reactFlow.test.ts` (round-trip coverage for cloned/created elements)
- `docs/01-architecture/02-frontend-architecture.md`, `frontend/README.md`

## Exit Criteria

- Undo/redo, duplicate, copy/paste, multi-select bulk move/delete/style, inline label editing, and keyboard shortcuts all work; the shortcuts help modal lists them.
- Cloned/created elements save to canonical JSON with the correct `node.type`/`data.semanticType`; the reverse adapter still strips React Flow runtime/session fields (round-trip byte-stable).
- `npm run lint`, `npm run build`, and `npm run test` pass (including the extended adapter test).

## Previous Slice

- `03-canvas-polish.md`

## Next Slice

- `05-inspector-and-save.md`

## Outcome

✅ Completed (one scoped deviation on inline editing). Added a `useUndoRedo` history hook (snapshots taken before structural ops — connect/reconnect/drop/drag-start/duplicate/paste/delete — and coalesced per property-edit session so a label/colour edit is one undo step), a floating `Toolbar` (undo/redo, duplicate, delete, zoom in/out/fit, shortcuts) rendered inside the pane, duplicate + copy/paste + delete-selected over the current selection (via a shared `clone.ts` with fresh ids, position offset, and `parentId` remap), keyboard shortcuts (Ctrl/Cmd+Z / Shift+Z / Y / D / C / V, ignored while typing in a field), and a `ShortcutsHelp` modal (new `ui/Modal` primitive). Multi-select move/delete use React Flow's native box-select. A new `adapters/reactFlow.clone.test.ts` proves cloned elements round-trip to canonical JSON with the right `node.type`/`data.semanticType` and no runtime-field leakage (12 fixtures). Deviation: **on-canvas in-shape inline label editing was implemented as double-click → select the node + expand the inspector** (edit the label in the panel) rather than an in-shape `<input>`, to avoid unverified edits to the Epic 2-owned `customNodes.tsx`; tracked as a follow-up. Verified: `npm run lint`, `npm run build`, `npm run test` (52/52) pass; adapters/schema untouched. Follow-up: in-shape inline editing; bulk style across multi-selection.
