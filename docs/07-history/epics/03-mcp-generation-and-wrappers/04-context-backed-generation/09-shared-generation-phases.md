# Slice 09: Shared Generation Phases

## Purpose

Extract the current direct-generation pipeline's reusable downstream phases so direct and context-backed
orchestration can share one conform/layout/validate/persist/render implementation.

## Background

`DiagramGenerationService` currently contains logical schemas, conformance, assembly, prompt helpers, and the
full direct orchestration path. This slice renames it to `PromptDiagramGenerationService` while extracting only
the downstream phases proven reusable by the second generation mode.

## Design

Separate input-specific prompt/preparation from shared logical-output processing, conformance, layout,
canonical assembly, validation/refinement, persistence, and render delivery. Preserve the existing direct tool's
behavior before adding context-backed orchestration.

## Plan Audit

- **Rename:** atomically rename `diagram_generation_service.py`/`DiagramGenerationService` to
  `prompt_diagram_generation_service.py`/`PromptDiagramGenerationService` with no compatibility shim. Update the
  MCP server, settings comments, generation/MCP tests, few-shot and structural tests, active owners, and service map;
  historical slice outcomes retain the name that existed when delivered. The public MCP tool remains
  `diagram_generate` until Slice 10 coordinates its contract rename.
- **Internal component:** add `generation_pipeline.py` as a package-internal component, not a
  `SharedGenerationService`. The current generation module exceeds one thousand lines and mixes direct prompt
  assets with reusable canonical mechanics; a focused module is a demonstrated responsibility boundary and still
  satisfies the architecture rule that shared phases stay internal to `services/generation/`.
- **Pipeline contract:** `GenerationPipeline.prepare(logical, diagram_type, name, model,
  generation_metadata=None)` performs one deterministic attempt: conform, layout, canonical assembly, canonical
  validation, and structural-finding extraction. It returns a frozen `GenerationCandidate` dataclass carrying
  `name`, `conformed`, `canonical`, `engine`, `validation`, and immutable `structural_findings`; its `accepted`
  property is true only when canonical validation is valid and structural findings are empty. It performs no LLM
  call, retry, path resolution, persistence, or rendering.
- **Mode boundaries:** direct and context logical schemas, system/user prompts, repair prompts, attempt loops,
  name/target policy, provenance acceptance, context stability, and result composition remain in their mode
  orchestrators. Do not add a callback-heavy generic refinement loop before the second mode demonstrates an exact
  common shape; both modes simply invoke the same per-attempt pipeline inside their bounded loop.
- **Logical contracts:** direct `LOGICAL_SCHEMA` and its strict schema fragments remain in the prompt service.
  Move only vocabulary-cleaning/conformance and canonical-assembly helpers to the internal pipeline module. Add
  optional canonical `ElementOrigin` to logical node/edge TypedDicts; conformance deep-copies its exact
  claim/assumption/schema-rule/rationale shape while sanitizing IDs/endpoints, and assembly preserves it as canonical
  top-level node/edge origin. Slice 10 owns the separate strict context logical schema.
- **Metadata seam:** canonical assembly accepts optional `generation_metadata` containing only
  `generationMode`/`generationContext` and deep-copies it over the existing generated metadata; the pipeline then
  validates the complete canonical diagram and metadata through `DiagramValidationService`. Its default is
  byte-for-byte current direct metadata, so this slice does not
  prematurely add mode/trace fields or permit callers to override source/model/timestamp identity. Slice 10 supplies
  exact prompt/context metadata in the coordinated public migration.
- **Publication boundary:** direct creation/name de-duplication and render-as-error semantics remain in
  `PromptDiagramGenerationService`. Context regeneration has different target ownership, digest recheck, atomic
  replacement, stale-SVG cleanup, and partial-success semantics, so no generic `persist_and_render` wrapper is
  introduced. Both modes already share the validated `DiagramPersistenceService` and `DiagramRenderService`
  implementations without duplicating their mechanics.
- **Injection:** preserve all existing direct constructor seams and defaults. The prompt service constructs one
  `GenerationPipeline` from its injected layout/validation services and shares the validation instance with the
  persistence gateway; context orchestration will construct its own pipeline from the same service types.
- **Imports/scripts:** `_build_few_shot` and `_blueprints_dir` move with the renamed
  `PromptDiagramGenerationService`; offline `_seed_examples.py` imports `conform_logical`/`assemble_canonical` from
  the pipeline. Update all monkeypatch/module targets and ensure there are no imports of the removed module/class.
  `render_example_gallery.py` retains its independent storage-root helper because it does not import generation
  internals and serves a separate management-command boundary.
- **Characterization:** before extraction, freeze representative direct conformance, assembly metadata, repair,
  structural hard-gate, naming, persistence/render, result, and MCP delegation behavior. Add origin/metadata-seam
  pipeline tests, then require all existing answer-key seeding/sample, backend, and stdio smoke checks to stay green.

## Included Work

- Rename `DiagramGenerationService` to `PromptDiagramGenerationService` and update imports/tests/docs atomically without changing direct-generation behavior.
- Extract the smallest coherent reusable generation phases from the current module into internal functions or `generation_pipeline.py`, not a `SharedGenerationService`.
- Preserve injectable layout, validation, persistence, render, prompt, and LLM seams.
- Keep generation acceptance validation and persistence-boundary validation separate.
- Maintain structural-critic advisory/hard-gate behavior.
- Add characterization tests proving direct prompt generation output and errors are unchanged.
- Update active generation/backend architecture docs if implementation reveals a better exact boundary.

## Not In Scope

- Context-backed generation behavior or MCP tool rename.
- Merging readiness into diagram validation.
- Broad service rewrites unrelated to the second consumer.

## Target Areas

- `backend/services/generation/prompt_diagram_generation_service.py`
- `backend/services/generation/pipeline/generation_pipeline.py` or smaller internal phase modules when justified
- `backend/mcp_server/` direct-generation consumer
- `backend/tests/generation/` and affected MCP tests
- active generation/backend architecture owners

## Exit Criteria

- Direct prompt-generation characterization tests remain green.
- Shared phases have one implementation and explicit inputs/outputs.
- No validation, persistence, rendering, or provenance safety invariant weakens.
- Full backend tests pass offline.

## Previous Slice

- [`08-context-population-and-provenance.md`](08-context-population-and-provenance.md)

## Next Slice

- [`10-context-generation-and-workflow.md`](10-context-generation-and-workflow.md)

## Outcome

**Completed.** Direct prompt generation now uses `PromptDiagramGenerationService`, while the internal
`GenerationPipeline` owns one deterministic conform/layout/assemble/validate/structural-review attempt for reuse
by prompt and context orchestrators. Logical origins and the bounded generation-metadata seam survive conformance
and canonical assembly without moving retries, publication, or render policy out of the mode-specific service.

**Verification.** `cd backend; uv run python manage.py test tests.generation.test_generation_service
tests.generation.test_samples tests.generation.test_structural_constraints tests.mcp_server.test_mcp_server` passed
105 tests; `cd backend; uv run python manage.py test` passed 578 tests with 3 skipped; `cd backend; uv run
python mcp_server/smoke_test.py` passed every stdio MCP check, including live direct generation under the configured
provider.

**Deviations.** None. Direct prompt metadata and the public `diagram_generate` tool remain unchanged; no
compatibility alias or generic publication/refinement service was added.

**Follow-up.** Slice 10 can build context-specific logical prompting, provenance acceptance, stability checks, and
publication over the shared per-attempt pipeline.
