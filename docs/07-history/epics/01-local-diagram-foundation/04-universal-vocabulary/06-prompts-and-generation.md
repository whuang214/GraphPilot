# Slice 06: Prompts Refresh + Generation (3 types)

## Purpose

Refresh the **3 MVP types'** `prompts.md` for the final vocabulary and verify generation end-to-end.
**Only needed if S05 changes a type's generation vocab** (Option B) — otherwise the 3 types' prompts
are unchanged and this slice is a light verification (or deferred). **No new diagram types.**

## Background

- Generation is data-driven (see `04-generation-design.md`): the vocab comes from the catalog, the
  guidance from each type's `prompts.md`, and the few-shot from its answer keys. So a prompt refresh
  is just editing the per-type `prompts.md` — no engine changes.

## Design

- If S05 admitted a new relationship into a type (Option B), update that type's `blueprints/<type>/
  prompts.md` to mention it, and tweak the `generate.md` / `repair.md` templates only if the fuller
  vocab needs it (the `{{vocabulary}}` + `{{structural_rules}}` placeholders already inject per-type
  content).
- Verify generation for the 3 types through the offline `FakeLLMClient` (+ optional live DOE).

## Not In Scope

- New diagram types' prompts (deferred post-MVP).

## Target Areas

- `backend/assets/blueprints/<type>/prompts.md`, `backend/assets/prompts/generate.md` +
  `repair.md`; `backend/tests/` (generation)

## Exit Criteria

- Each of the 3 types generates a valid, structurally-clean diagram offline; prompts reflect the
  final vocab. Backend `manage.py test` green.

## Previous Slice

- `05-answer-key-rebaseline.md`

## Next Slice

- `07-reusable-shapes-backend.md` — end of the MVP scope; Epic 1's `04-universal-vocabulary` group then **reopened post-MVP** for the
  reusable-shapes collapse + answer-key regeneration (S07–S10). **Deferred post-MVP:** the new diagram
  types (state machine, class, component, requirement, IBD) — each adds its type-specific vocab + a
  structural critic + `prompts.md` + answer keys on the existing catalog/engine. Their intended
  vocabulary is documented in `../../../../02-design-and-features/00-diagram-json-schema.md`.

## Outcome

✅ Completed. BDD prompt refreshed for `dependency`; generation verified offline. **Epic 1's `04-universal-vocabulary` group (MVP
scope) is complete (S01–S06).**

**Delivered.** `blueprints/bdd_diagram/prompts.md` gains a `dependency` rule (when to use a dashed
dependency vs composition/aggregation) + its vocabulary entry. Activity + use-case prompts are
unchanged (their vocab didn't change). No template changes were needed — the `{{vocabulary}}`
placeholder already injects each type's catalog subset.

**Verification.** backend `manage.py test` → **377** (incl. offline generation for all 3 types via
`FakeLLMClient`).

**Follow-up.** none for MVP. New diagram types (state machine, class, component, requirement, IBD)
remain deferred post-MVP — each added later as context (vocab subset + structural critic +
`prompts.md` + answer keys) on the now-modular engine; their vocab is in `00-diagram-json-schema.md` §7.
