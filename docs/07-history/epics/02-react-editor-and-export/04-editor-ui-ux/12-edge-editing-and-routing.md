# Slice 12: Edge Editing and Routing

## Purpose

Let users edit an existing edge in place — reconnect its endpoints, relabel, and restyle it without delete-and-redraw (feature-list #3) — and fix poor handle/anchor selection so edges route sensibly on the canvas (#14). This is the design doc's **P2** editing pass; #14 is paired here because it lives in the same handle/anchor logic as edge editing.

## Background

- Today, to change a connection you must delete the edge and draw a new one (#3); there is no in-place reconnect or edge inspector.
- Edges also take poor paths: e.g. in the library use-case diagram the *Return Book → Pay Fine* relationship attaches left-of-source to right-of-target instead of routing through the middle (#14).
- The **saved JSON is correct** — the Epic 3 `diagram_render` SVG draws these edges perfectly — so #14 is a React Flow handle/anchor-selection issue on the custom nodes, **not** a data issue. Fixing it must keep the saved JSON byte-stable.

## Design

- **Edge editing (#3):** enable React Flow edge reconnection (`onReconnect` / `reconnectEdge`) so an endpoint can be dragged to a new node; make edges selectable and surface their label/style in the inspector for in-place relabel/restyle (reusing the friendly controls from Slice 11).
- **Routing (#14):** revisit the floating-edge / handle-position logic on the custom nodes so the source/target anchors pick the nearest sensible sides based on relative geometry, instead of fixed handles. The change is presentation-only; the persisted `edges[]` entries (source/target/label/ style) are unchanged.

## Included Work

- Wire `onReconnect` in `EditorPage.tsx` (and `reconnectEdge` from the adapter state) so endpoints can be re-dragged; keep `parentId`/containment untouched.
- Add edge selection + an edge section in `PropertyPanel.tsx` for label and the supported edge styles.
- Improve handle/anchor selection on the custom nodes (`customNodes.tsx`) so floating edges route through sensible sides; verify against the *Return Book → Pay Fine* case.
- Unit tests for reconnect (endpoint change → updated `edges[]`) and a routing-geometry assertion.

## Not In Scope

- Smart/orthogonal auto-routing or waypoints (out of scope per the design doc).
- New edge types or any schema change to `edges[]`.
- Editor-vs-server render parity beyond the handle-anchor fix (the server SVG is already correct).

## Target Areas

- `frontend/src/editor/canvas/customNodes.tsx` (handle positions / floating-edge anchoring).
- `frontend/src/editor/EditorPage.tsx` (`onReconnect`, edge selection).
- `frontend/src/editor/components/PropertyPanel.tsx` (edge label/style section).
- Frontend unit tests.

## Exit Criteria

- An existing edge can be reconnected to a different node, relabeled, and restyled in place — no delete-and-redraw (#3).
- The known use-case routing case (*Return Book → Pay Fine*) attaches through sensible sides on the canvas (#14), with the saved JSON unchanged.
- The load → edit → save round-trip stays byte-stable (no adapter/schema change, no runtime-field leak); `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `11-friendly-property-controls.md`

## Next Slice

- `13-container-un-trapping.md`

## Outcome

Implemented on `epic-6-refinements`; pending manual visual confirm.

**#14 routing (done).** Added a floating edge (`FloatingEdge.tsx`) registered as the `default` edge type, so every edge anchors to the nearest node sides from geometry (like the server SVG) instead of the fixed primary handle. No runtime edge `type` is set (the built-in `default` type is overridden), so the save round-trip stays byte-stable; the per-side source+target handles are unchanged, so connect-from-any-side still works.

**#3 editing (already wired, verified in code).** Reconnection (`onReconnect` / `reconnectEdge`), edge selection, and the inspector's edge label/style editing were already present, and the floating edge preserves them.

**Verification.** npm run lint (0/0), npm run build (tsc + vite), npm run test (186 passed). Visual confirmation (canvas vs server SVG via the editor's Preview render) pending the user.
