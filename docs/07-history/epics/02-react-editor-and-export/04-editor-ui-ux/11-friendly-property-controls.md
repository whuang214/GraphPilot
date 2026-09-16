# Slice 11: Friendly Property Controls

## Purpose

Replace the inspector's raw, technical inputs with friendly controls (feature-list #4) — for example a Solid / Dashed / Dotted dropdown instead of a raw `strokeDasharray` array — while staying strictly within the supported style subset. **No schema change.** This is the second half of the design doc's **P1** pass.

## Background

- The grouped inspector shipped in Slice 05, but some fields are unfriendly: the dashed-line field asks for a raw array (`strokeDasharray`) instead of a simple choice, and a few size/color inputs are rawer than they need to be.
- The supported style subset is fixed; this slice only changes how existing values are *entered*, not which properties exist or how they serialize.

## Design

- Map the dashed-line control to a small, fixed set — **Solid / Dashed / Dotted** — each emitting the exact `strokeDasharray` string the renderer and schema already accept (e.g. `""`, `"6 4"`, `"2 4"`). Round-trip the current value back to the right option on load.
- Audit the remaining inspector fields and give the rawest ones friendlier controls within the subset: a color swatch + hex for fills/strokes, steppers/units for size, all reusing the shared `ui/controls.tsx` primitives.
- Keep emitted JSON identical in shape to what the inspector produces today for the equivalent value (so the round-trip stays byte-stable).

## Included Work

- Add a Solid/Dashed/Dotted select to `PropertyPanel.tsx` that reads/writes `strokeDasharray` within the supported subset.
- Replace other raw inputs (as identified) with friendlier shared controls; no new style properties.
- Extend the shared primitives in `ui/controls.tsx` if a needed control type is missing.
- Unit tests covering value → control and control → emitted-JSON mapping (including the load-existing-value case).

## Not In Scope

- Any new style property, schema change, or expansion of the supported subset.
- Bulk styling across a multi-selection (#12 — deferred to Slice 15).
- Node-renderer fidelity (#1/#8/#6 — Slice 10) and edge styling UX (Slice 12).

## Target Areas

- `frontend/src/editor/components/PropertyPanel.tsx` (control wiring).
- `frontend/src/ui/controls.tsx` (shared control primitives, if extended).
- Frontend unit tests (`editor/components/components.test.tsx` / `ui/ui.test.tsx`).

## Exit Criteria

- Dashed/dotted styling is set via a friendly dropdown (no raw array entry), and the emitted `strokeDasharray` stays within the supported subset (#4).
- Any other restyled fields use friendlier controls without adding properties or changing the schema.
- The load → edit → save round-trip stays byte-stable; `npm run lint`, `npm run build`, and `npm run test` pass.

## Previous Slice

- `10-node-fidelity.md`

## Next Slice

- `12-edge-editing-and-routing.md`

## Outcome

Implemented on `epic-6-refinements`; pending manual confirm.

**Delivered (#4).** The edge inspector's raw "Dash array" text field (where you typed a `strokeDasharray` like "6 4") is replaced by a friendly **Line style** dropdown (Solid / Dashed / Dotted) in `PropertyPanel.tsx`. Each option maps to a canonical dash value within the supported style subset; an existing value is classified back to the nearest option for display and only rewritten when the user picks one, so an unedited diagram stays byte-stable. The node controls (color swatches, number steppers, the Border-style dropdown) were already friendly and are unchanged.

**Verification.** npm run lint (0/0), npm run build (tsc + vite), npm run test (191 passed; added a PropertyPanel test that the Line style dropdown emits the canonical `strokeDasharray` and that the raw field is gone).
