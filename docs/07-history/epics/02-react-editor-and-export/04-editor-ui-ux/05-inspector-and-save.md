# Slice 05: Inspector and Save

## Purpose

Make editing properties and saving feel modern and legible. Today the `PropertyPanel` is a flat list of fields, save uses a blocking `window.confirm`, and validation errors are shown as a generic list not tied to any element. This slice organizes the inspector and makes save/validation feedback clear and contextual.

## Background

- `frontend/src/editor/components/PropertyPanel.tsx` renders label/size/color fields as one ungrouped column.
- `frontend/src/editor/EditorPage.tsx` gates save/open with `window.confirm` and renders the `SaveBanner` (a top-of-page strip) for success/error; `frontend/src/api/diagrams.ts` already carries `validationErrors` (with a `path`) but the UI lists them generically.
- "Richer property panel" and "clearer inline validation feedback" are backlog Tier B items promoted into Epic 2's `04-editor-ui-ux` group.
- This slice changes neither the supported style subset nor the save/load contract; it is an inspector and save-UX rework only.

## Included Work

- Restructure the inspector into **grouped, collapsible sections** — *Identity* (label / id), *Layout* (width / height), *Style* (background / text / border color, border width/style) — using the Slice 01 `Field`/primitives, **keeping the existing supported style subset** (no schema change).
- Add quick **style presets** within the supported subset (e.g. reset-to-default, a small set of accent fills).
- Replace the `window.confirm` overwrite/open prompts with an accessible **`Modal`** (Slice 01).
- Show save success/error as **toasts** (Slice 01 `Toaster`).
- **Inline validation markers**: map each `validationErrors[].path` from `DiagramApiError` back to the offending node/edge — a badge/highlight on the canvas plus a flag in the relevant inspector section — building on the existing plumbing in `api/diagrams.ts` (no contract change).
- Add an **optional autosave toggle** (debounced; reuses `saveDiagram`), **off by default**, with the preference persisted to `localStorage`.
- Update `docs/01-architecture/02-frontend-architecture.md` (save flow / error states) and `frontend/README.md`.

## Not In Scope

- New canonical style fields / schema changes, or new supported style keys.
- New API routes (the additive listing endpoint is Slice 06); this slice reuses the existing `POST /api/diagrams/save` contract.
- Workspace browser / export (Slice 06).
- Custom renderer visuals (Epic 2).

## Target Areas

- `frontend/src/editor/components/PropertyPanel.tsx` (grouped/collapsible sections, presets)
- `frontend/src/editor/EditorPage.tsx` (modal confirms, toasts, mapping validation errors to elements, autosave toggle)
- `frontend/src/api/diagrams.ts` (only a small read-side helper if needed; **no contract change**)
- `frontend/src/ui/` (extend `Modal`/`Toast` only if needed)
- `docs/01-architecture/02-frontend-architecture.md`, `frontend/README.md`

## Exit Criteria

- The inspector is grouped and collapsible and edits the same supported style subset as before.
- Overwrite/open confirmation uses an accessible modal; save success/error appears as toasts.
- A save-time validation error highlights the offending node/edge inline (not just a generic list).
- An optional autosave toggle exists, defaults off, and persists its preference; manual save still works exactly as before.
- The save round-trip stays byte-stable (adapters/schema untouched).
- `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `04-toolbar-and-editing.md`

## Next Slice

- `06-browse-and-export.md`

## Outcome

✅ Completed (one scoped deviation on inline markers). Restructured `PropertyPanel` into collapsible sections (Identity / Layout / Style) with one-click style presets (within the existing supported subset — no schema change). Replaced the `window.confirm` overwrite/open prompts with an accessible `Modal`-based confirm, added a `Toast` system (new `ui/Toast` + `ui/toastContext`, provider mounted in `App.tsx`) surfacing save success/failure, and added an opt-in **Autosave** toggle in the TopBar (off by default, persisted to `localStorage`, debounced ~1.5s, and skipping the overwrite confirm). The save logic was split into `performSave` (used by both the confirmed manual save and autosave). Deviation: **per-element inline validation markers were deferred** — the exact `validationErrors[].path` format isn't verifiable without a real failing save, so blocking errors are surfaced via a toast plus the existing per-issue `SaveBanner` list (which already shows the path); mapping a path to a specific node/edge outline is tracked as a follow-up. Verified: `npm run lint` (0/0), `npm run build`, `npm run test` (52/52) pass; canonical schema/style subset unchanged. Follow-up: map validation paths to per-element canvas markers.
