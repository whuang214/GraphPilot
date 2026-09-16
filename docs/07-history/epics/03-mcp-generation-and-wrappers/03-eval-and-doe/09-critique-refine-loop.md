# Slice 09: Structural Critique-Refine Loop

> **Backfilled doc.** This slice shipped as code first (commit `a36eea0`); this doc was
> reconstructed from that commit to close the 07→11 numbering gap. See the slice-index
> table in `../00-epic.md`.

## Purpose

Generalize generation's single repair pass into a **bounded critique-refine loop** driven by
both deterministic validation **and** the structural critic, and turn model **reasoning on by
default** so candidates are structurally cleaner before they are saved.

## Included Work

- A bounded critique-refine loop in `DiagramGenerationService` (**default 1 round**; `0` =
  baseline single pass). Validation stays the **hard gate**; residual *structural* issues are
  tolerated (advisory), so the loop improves quality without blocking on soft findings.
- Inject **per-type structural rules** into the generate + repair prompts.
- **Reasoning on by default** (`AZURE_OPENAI_REASONING_EFFORT=medium`) with `off`/`none`
  sentinels and automatic **drop-on-reject** for deployments that don't accept the parameter.
- `.env.example` + prompt templates updated; tests for the loop, the client, and prompts.

## Not In Scope

- Sweeping refine-rounds / reasoning as DOE factors (Slice 10).
- New eval signals (Slice 08) or answer-key changes (Slices 11–12).

## Target Areas

- `services/generation/pipeline/diagram_generation_service.py`, `services/llm/llm_client.py`, `graphpilot/settings.py`
- `graphpilot/prompts/generate.md`, `graphpilot/prompts/repair.md`, `backend/.env.example`
- `tests/generation/test_generation_service.py`, `tests/llm/test_llm_client.py`, `tests/llm/test_prompt_service.py`

## Exit Criteria

- Generation runs a bounded critique-refine loop; `refine=0` reproduces the baseline.
- Validation remains the hard gate; structural findings are advisory.
- Reasoning defaults to `medium`, degrades gracefully on non-reasoning deployments.
- `python manage.py test` passes offline.

## Previous Slice

- `../02-generation/05-example-library-overhaul.md`

## Next Slice

- `11-answer-key-quality-and-review.md`

## Outcome

✅ Delivered as code in `a36eea0`; documented here after the fact.

**Delivered.** Bounded critique-refine loop (validation + structural critic, default 1 round),
per-type structural rules injected into generate/repair, reasoning-on-by-default with
off/none sentinels + drop-on-reject; `.env.example`, prompts, and tests updated.

**Deviations.** Doc backfilled after the commit (numbering reconciliation); no scope change.

**Verification.** Covered by the offline backend suite (`python manage.py test`).

**Follow-up.** The loop's `refine_max_rounds` + `reasoning_effort` become DOE factors in Slice 10.
