# Slice 03: Frontend Editing and Save

## Purpose

Turn the display-first editor into an editable surface and wire the browser save flow end to end, so a user can open a saved diagram, make light visual edits, and persist valid GraphPilot JSON through the Django save API.

## Included Work

- enable light editing in the React Flow editor:
  - move nodes
  - resize nodes
  - relabel nodes and edges
  - recolor nodes and edges
  - connect and reconnect edges
- add a minimal property panel for the selected node or edge (label and supported style subset)
- retain the full loaded `GraphPilotDiagram` in editor state (Slice 01's `EditorPage` keeps only `name`/`diagramType`/`nodes`/`edges`); the reverse adapter needs the original canonical diagram to round-trip metadata/semantic fields on save
- implement the reverse adapter (React Flow state -> GraphPilot JSON)
- strip React Flow runtime/session-only fields (for example `selected`, `dragging`, `resizing`, `measured`, `positionAbsolute`) before save so the saved JSON stays schema-valid under the canonical schema's strict node/edge shape
- track dirty state and add a save action that prompts before overwrite
- call `POST /api/diagrams/save` and surface success, validation failure, and save-error states clearly

## Not In Scope

- new diagram types beyond the three MVP types
- finalizing the canonical sample fixtures and round-trip confirmation (Slice 04)
- autosave
- export flows (SVG/PNG/PDF)
- frontend-to-MCP communication

## Target Areas

- `frontend/` editor, property panel, and adapter
- `frontend/README.md`
- frontend architecture or mapping docs if implementation clarifies them

## Exit Criteria

- a loaded diagram can be moved, resized, relabeled, recolored, and reconnected in the browser
- the reverse adapter produces canonical GraphPilot JSON with no React Flow runtime-only fields
- a valid edit saves through `POST /api/diagrams/save` and the file is overwritten
- an invalid edit is rejected by the backend and does not overwrite the existing file, with the failure shown in the UI
- GraphPilot JSON remains the source of truth across the load -> edit -> save flow

## Previous Slice

- `02-save-and-validate-api.md`

## Next Slice

- `04-canonical-samples.md`

## Outcome

✅ Completed as planned. Turned the display-first editor into an editable surface and wired the browser save flow end to end.

**Delivered.**

- Editor (`frontend/src/editor/EditorPage.tsx`): split into a loader (`EditorPage`) and an editable `DiagramEditor` so React Flow hooks stay unconditional. The full loaded `GraphPilotDiagram` is retained as the source of truth; the canvas supports moving nodes, connecting and reconnecting edges, selection, and delete. Added dirty tracking, a confirm-before-overwrite **Save** button, and a banner surfacing success / per-issue validation failure / save-error states.
- Property panel (`frontend/src/editor/components/PropertyPanel.tsx`, new): edits the selected node (label, width/height, background/text/border color, border width/style) or edge (label, stroke color/width, dash array).
- Reverse adapter (`frontend/src/adapters/reactFlow.ts`): added `reactFlowToGraphPilot()` which merges edited React Flow state back into canonical JSON by **whitelisting** schema fields and pulling non-visual fields (semanticType, description, metadata, node.type, parentId) from the originally loaded diagram by id, so React Flow runtime-only fields never reach saved JSON. Positive sizes only are persisted and node labels fall back to the original to stay schema-valid.
- API client (`frontend/src/api/diagrams.ts`): added `saveDiagram()` and extended `DiagramApiError` to carry `validationErrors` from a 422 save failure. Added the matching save response/failure types to `frontend/src/types/diagram.ts`.

**Deviations.** node **resize** is done via the property panel (deterministic width/height inputs) rather than an on-canvas resize handle, which keeps the round-trip schema-safe; viewport pan/zoom is not persisted on save (the original viewport is preserved), consistent with the display-first decision. No frontend test runner exists, so verification is build + lint rather than unit tests.

**Verification.** `npm run build` (tsc -b + vite build) passes; `npm run lint` (oxlint) reports 0 warnings / 0 errors. Manual load → edit → save round-trip to be exercised by the user against a seeded workspace.

**Post-review.** (done during Slice 04 review) the save flow now tracks an edit generation so a completed save only clears the dirty flag when no edits occurred while the request was in flight (prevents silently dropping concurrent edits), and the success/error banner is cleared as soon as the user edits again (no stale "Saved." state).

**Follow-up.** Slice 04 — finalize the canonical per-type samples and confirm the provisional schema against this round-trip.
