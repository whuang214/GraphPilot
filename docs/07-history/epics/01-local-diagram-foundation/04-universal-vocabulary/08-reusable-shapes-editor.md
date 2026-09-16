# Slice 08: Editor Base Type Collapse

## Purpose

Bring the React editor onto the base + stereotype model from Slice 07: one **Box** in the palette
that renders any classifier by its `data.stereotype`, an editable **Stereotype** control, and the
compartments editor available to every classifier (fixing the current drift where only 5 of the
box types can edit compartments).

## Background

- Slice 07 makes the backend, the saved JSON, and the examples use `classifier` + `data.stereotype`
  (nodes) and `dependency` + `data.stereotype` (edges). The editor must read/write that shape and
  stop re-encoding the classifier membership by hand.

## Design

- `customNodes.tsx`: the classifier branch keys on `semanticType === 'classifier'` and shows
  `data.stereotype` as the «header» (empty → plain box); the edge label shows the dependency
  stereotype. No per-kind lists.
- `palette.ts`: replace the six classifier items with one **Box** (`classifier`); a `DEFAULT_SIZES`
  entry for `classifier`. Edges keep their draw path (`dependency` already dashed).
- `PropertyPanel.tsx`: a **Stereotype** field (a dropdown of the current type's allowed stereotypes
  + free text) for classifier nodes and dependency edges; the compartments editor shows for every
  `classifier`.
- `adapters/reactFlow.ts`: carry `data.stereotype` on load and `recoverSemanticFields` on save.
- `types/diagram.ts`: add optional `stereotype` to node/edge data.

## Included Work

- The five files above + `NodePalette.tsx` (`ShapePreview` classifier case) and the affected tests
  (`palette.test`, `reactFlow` round-trip, `components`, `clone`).

## Not In Scope

- Backend (Slice 07). Schema-doc rewrite + cleanup (Slice 09).

## Target Areas

- `frontend/src/editor/{customNodes,palette,NodePalette,PropertyPanel}.tsx`,
  `frontend/src/adapters/reactFlow.ts`, `frontend/src/types/diagram.ts`, `frontend/src/**/*.test.*`

## Exit Criteria

- The palette shows one Box; dropping it + typing a stereotype renders the «header»; every classifier
  can edit compartments; a load→save round-trip of the Slice 07 examples is a no-op.
- `cd frontend; npm run verify` green (lint + build + unit + e2e).

## Previous Slice

- `07-reusable-shapes-backend.md`

## Next Slice

- `09-reusable-shapes-docs.md` — schema-doc §4 rewrite, current-state, and cleanup.

## Outcome

✅ Completed as planned. The editor is on the base + stereotype model.

**Delivered.** `customNodes` dispatches on `semanticType === 'classifier'` and reads `data.stereotype`
for the «header» (empty → plain box); the palette offers one **Classifier** box; `PropertyPanel`
gained a **Stereotype** field for classifier nodes + dependency edges and now shows the
**Compartments** editor for every classifier (fixing the 5-of-10 drift); the adapters carry
`stereotype` on load + save; `NodePalette` + `types/diagram.ts` updated.

**Deviations.** A stale e2e fixture (`activity_diagram/training/01-library-loan`, removed in a prior
re-baseline) left `npm run e2e` broken before this slice; repointed the seed to
`01-employee-onboarding` and updated the smoke assertions (unique labels to avoid case-insensitive
`hasText` collisions).

**Verification.** `npm run verify` → **lint 0 errors**, **build ok**, **247 unit**, **10 e2e**;
`tsc --noEmit -p tsconfig.app.json` clean.

**Follow-up.** Slice 09 (docs + cleanup).
