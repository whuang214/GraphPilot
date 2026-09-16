# Slice 11: Schema/Type Parity Guard

## Purpose

Guard the one place the canonical shape is declared twice — the backend JSON Schema and the React
editor's TypeScript types — so they can't silently drift. The last hardening follow-on from the
Epic 1 validation review.

## Background

`backend/assets/schemas/diagram.json` is the source of truth the validator enforces, but the
editor re-declares the same shape in `frontend/src/types/diagram.ts` (React Flow state is derived
from GraphPilot JSON). The frontend wisely does **not** re-validate — it just maps backend issues
to canvas elements — but the two *shape definitions* are parallel and hand-maintained, so a schema
change not mirrored in the TS types (or vice versa) goes unnoticed until runtime. The chosen fix is
a **parity test, no new dependency** (not schema→TS codegen), matching the repo's existing
canvas ↔ SVG "parity" discipline.

## Design

A small **field manifest** bridges the schema and the types, checked from both sides:

- `CANONICAL_REQUIRED_FIELDS` in `diagram.ts` lists the canonical required fields (diagram, node,
  node.data, edge, viewport). It is `as const satisfies { … readonly RequiredKeys<Interface>[] }`,
  so `tsc` (part of `npm run build`) fails if a listed field isn't a required key of its interface
  — the **compile-time** half.
- `diagram.parity.test.ts` reads `diagram.json` (via `node:fs`, so no bundler fs-allow rule or
  `resolveJsonModule` is needed to reach outside the frontend) and asserts the manifest equals the
  schema's `required` arrays — the **runtime** half.

Together they force the schema, the manifest, and the interfaces to move as one: a schema-side
change fails the runtime test; a type-side change fails `tsc`.

## Included Work

- `frontend/src/types/diagram.ts` — the `RequiredKeys<T>` helper + the `CANONICAL_REQUIRED_FIELDS`
  manifest with its `satisfies` guard.
- `frontend/src/types/diagram.parity.test.ts` — new vitest that compares the manifest to
  `diagram.json`'s `required` arrays (and a light diagramType-enum presence check).
- Docs: `02-design-and-features/02-validation-design.md` (parity note), `decision-decisions.md`.

## Not In Scope

- Schema→TypeScript **codegen** (would add a devDependency + build step; deferred unless the shape
  grows much larger).
- Generating or validating the API contract types (`DiagramLoadResponse`, etc.) — only the
  canonical diagram shape is guarded.
- Any runtime validation in the frontend (it still delegates to the backend).

## Target Areas

- `frontend/src/types/diagram.ts`, `frontend/src/types/diagram.parity.test.ts`

## Exit Criteria

- The parity test passes for the current schema + types.
- Renaming/removing a canonical field on either side fails the guard (runtime test or `tsc`).
- No new dependency; runs inside `npm run verify`.

## Previous Slice

- `10-validated-write-enforcement.md`

## Next Slice

- End of the Epic 1 validation-hardening follow-on (S09–S11). Next epic-level work is unchanged
  (see `../../00-current-state.md`).

## Outcome

✅ Completed as planned. Added a `CANONICAL_REQUIRED_FIELDS` manifest (compile-time `satisfies`
guard) in `diagram.ts` and a runtime parity test that reads `diagram.json`; the schema and the
editor's TS types can no longer drift unnoticed. No new dependency.

**Verification.** `npx tsc --noEmit -p tsconfig.app.json` clean; `npx vitest run
src/types/diagram.parity.test.ts` → 6 passed. Drift proven caught: temporarily dropping a manifest
field failed the runtime test (reverted). Full frontend `npm run verify` run with the S09–S11 batch.

**Follow-up.** None.
