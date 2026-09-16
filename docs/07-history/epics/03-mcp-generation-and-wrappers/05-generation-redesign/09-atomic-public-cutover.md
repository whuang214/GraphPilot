# Slice 09: Atomic Public Cutover

## Purpose

Replace the current context-only workflow and raw direct-generation surface with one dual-namespace routed generation
workflow, shared request persistence, bounded direct/context generation tools, namespace-first schemas/results, and new
artifact paths in one cold-turkey public cutover with no aliases, dual acceptance, or partial rollback.

## Background

Slices 1–8 build and verify the redesigned contracts, request lifecycle, strict packets/logical outputs, fixtures,
deterministic/semantic review and repair, trace/debug services, and sole PyGraphviz layout internally while the current
public MCP surface remains available. The prerequisite context Slice 12 already proves that one private renderer can be
registered under the same public name in both MCP prompt and tool namespaces. This slice performs the intentionally
atomic point at which every public producer, consumer, registry, adapter, test, and active document moves to the new V1
surface together.

## Design

### Exact MCP names

The public-name migration is:

| Before | After |
| --- | --- |
| Prompt `context_backed_generation_workflow` | Prompt `diagram_generation_workflow` |
| Tool `context_backed_generation_workflow` | Tool `diagram_generation_workflow` |
| Tool `context_request_save` | Tool `diagram_request_save` |
| Tool `diagram_generate_from_prompt` | Tool `diagram_generate_direct` |
| Tool `diagram_generate_from_context` | Tool `diagram_generate_from_context` (retained name, new contract/result) |

`context_evidence_status`, `context_evidence_save`, and `context_readiness_assess` retain their bounded responsibilities.
No old generation/workflow/request-save name remains as an alias. The public prompt and model-callable tool share one
private renderer and identical arguments/defaults:

```text
workspaceDir              required
request                   required and preserved verbatim
interactionPreference     optional autonomous|balanced|collaborative; default balanced
persistGenerationTrace    optional boolean; default false
persistGenerationDebug    optional boolean; default false
```

The public renderer identity is `graphpilot.generation.workflow-prompt.v1`; its private, non-registered branch assets
are `graphpilot.direct.workflow-branch-prompt.v1` and `graphpilot.context.workflow-branch-prompt.v1`. The tool
description starts with “Call this first” and identifies the tool as instructions-only. Its structured content is exactly
`kind: diagramGenerationWorkflow`, `workflow: diagram_generation_workflow`, and the renderer's `instructions`; text
content is the same instruction string. Invocation does not inspect source, write artifacts, call Azure, apply readiness/
actions, execute generation, or expose internal branch/generation/readiness/repair/reviewer prompts.

The renderer routes requested authority to exactly one internal branch. Direct framing saves one complete
`graphpilot.direct.diagram-request.v1` through `diagram_request_save` and calls `diagram_generate_direct`. Context
framing retains evidence freshness, saves `graphpilot.context.diagram-request.v1` through the same tool, runs
readiness/actions, selects one exact generation policy, and calls `diagram_generate_from_context`. A blocked context
attempt never falls back to direct. The workflow propagates one safe debug run identity to reached stages and the
independent trace/debug toggles without changing acceptance.

### Exact schema and artifact cutover

The context ID migration activated at the public boundary is:

| Old ID | New ID |
| --- | --- |
| `graphpilot.evidence.v1` | `graphpilot.context.evidence-manifest.v1` |
| `graphpilot.diagram-request.v1` | `graphpilot.context.diagram-request.v1` |
| `graphpilot.resolved-diagram-request.v1` | `graphpilot.context.resolved-request.v1` |
| `graphpilot.readiness-input.v1` | `graphpilot.context.readiness-input.v1` |
| `graphpilot.context-readiness-review.v1` | `graphpilot.context.readiness-review.v1` |
| `graphpilot.context-readiness.v1` | `graphpilot.context.readiness-result.v1` |
| `graphpilot.readiness-debug.v1` | `graphpilot.context.readiness-debug.v1` |
| `graphpilot.context-generation-input.v1` | `graphpilot.context.generation-input.v1` |
| `graphpilot.logical-diagram.context.v1` | the three exact context logical IDs below |

The six exact logical IDs activated are:

```text
graphpilot.direct.logical-diagram.activity.v1
graphpilot.direct.logical-diagram.use-case.v1
graphpilot.direct.logical-diagram.bdd.v1
graphpilot.context.logical-diagram.activity.v1
graphpilot.context.logical-diagram.use-case.v1
graphpilot.context.logical-diagram.bdd.v1
```

The context readiness policy identities cut over in the same registry transaction:

```text
graphpilot.readiness-rubric.v1        → graphpilot.context.readiness-rubric.v1
graphpilot.readiness.activity.v1      → graphpilot.context.readiness-rubric.activity.v1
graphpilot.readiness.use_case.v1      → graphpilot.context.readiness-rubric.use-case.v1
graphpilot.readiness.bdd.v1           → graphpilot.context.readiness-rubric.bdd.v1
graphpilot.readiness-rating.v1        → graphpilot.context.readiness-rating.v1
graphpilot.context-generation.v1      → graphpilot.context.generation-prompt.v1
graphpilot.context-readiness.v1       → graphpilot.context.readiness-prompt.v1
```

The cutover also publicly activates the already-registered direct request/input, mode-specific generation repair/
review/semantic-repair contracts, `graphpilot.direct.generation-result.v1`,
`graphpilot.context.generation-result.v1`, `graphpilot.generation.trace.v1`, and generation debug contracts from
Slices 1–6. Every formal `$id` equals `schemaVersion`, every kind/path is unique, and all producers/consumers use the
registry rather than accepting a legacy constant.

Direct and context requests share `.graphpilot/requests/<diagramName>.gp-request.json` and exact complete-replacement/
expected-digest/immutable-identity/finalization behavior:

```text
diagram_request_save(workspaceDir, requestPath, expectedRequestDigest, candidate)
diagram_generate_direct(workspaceDir, requestPath)
diagram_generate_from_context(workspaceDir, requestPath, generationPolicy)
```

`diagram_request_save` discriminates the two schemas; both generation tools load only canonical requests. The workflow
translates `persistGenerationDebug` into one safe run ID plus strict tool-level diagnostics options for every reached
readiness/generation stage and passes `persistGenerationTrace` only to the selected generation attempt. Old local
artifacts are not deleted, rewritten, or silently migrated; old IDs/paths fail explicitly with a typed unsupported-
schema/path error.

Generated results use the mode-specific `graphpilot.<mode>.generation-result.v1` schemas and always identify mode,
request ref, compact generation/quality summary, nullable trace/diagnostics, and ordered operational warnings.
`outcome: blocked` is actionable with `isError: false` and no diagram/trace path. Canonical persistence defines
`outcome: generated`; render failure keeps the diagram, sets `svgPath: null`, and adds `render_failed` rather than
returning the old `partial_success`. Actual failures return top-level `error: OperationProblem` with `isError: true`.

### Atomicity and rollback

All prompt/tool registrations, tool schemas/descriptions, request/generation adapters, schema IDs/files/registry,
artifact paths, results, tests/smoke expectations, optional frontend types, and active documentation land in one
coherent implementation commit. No intermediate commit exposes a mixed surface.

Rollback is a dedicated ordinary revert of the complete Slice 9 implementation commit to the verified Slice 8 state.
It restores the prior prompt/tool names, old public schemas/adapters/results/tests/docs together; it never installs
aliases or reverts only one MCP namespace. New-format local artifacts created after cutover are left untouched and may
be unsupported by the restored runtime; rollback reports that fact rather than mutating/deleting them.

## Plan Audit

- **Dependencies:** require completed/audited Slices 1–8, both Phase 0 documentation commits, the context Slice 12
  same-name prompt/tool proof, and the recorded pre-redesign baseline characterization of exact prompt/tool names,
  discovery argument schemas/counts, request paths, schema IDs, and result/error payloads. Re-inventory all current
  public producers/consumers immediately before cutover.
- **Exact registry transaction:** replace prompt and tool workflow registrations together, rename request/direct tools,
  retain the context generation name only with its new contract, and update discovery schemas/counts/descriptions in
  one commit. No alias, duplicate registration, or mixed old/new adapter is allowed.
- **Prompt/tool parity:** both namespaces invoke one side-effect-free renderer with byte-identical instructions and
  argument/default/verbatim-request behavior. The tools-only description says to call it first without exposing or
  executing internal prompts.
- **Authority routing:** preserve one direct or context branch, balanced default consultation, complete persisted
  requests, mandatory context readiness/policy, no authority mixing, no blocked-context fallback, and no unchanged
  reroll.
- **Contract migration:** atomically update `$id`/`schemaVersion`/kind/path registries, formal files, Python constants,
  all producers/consumers, fixtures, diagnostics, traces, tests, and affected frontend types. Old artifacts fail
  explicitly and remain untouched; no dual read/write or hidden migration exists.
- **Result semantics:** activate generated/blocked/error contracts, explicit quality, separate semantic/operational
  warnings, trace/debug propagation, and render-warning success. Remove the old `partial_success` generation outcome
  everywhere in active code/contracts/docs.
- **MCP enforcement boundary:** generation tools require complete canonical mode-specific requests even if a caller did
  not fetch the workflow. No raw prompt-only or polymorphic optional-authority tool survives.
- **Frontend coordination:** limit changes to optional canonical metadata/origin/request-reference types/adapters and
  parity tests. Recheck status immediately before editing, agree exact file ownership with the concurrent frontend agent,
  avoid overlapping edits, and stage only this slice's settled changes; never absorb editor feature/UI redesign.
- **Stale-reference proof:** search active code/config/tests/docs for every old name/ID/path/result. Permit only explicit
  historical research/archive and this migration/rollback table; runtime registries and supported docs contain none.
- **Rollback:** keep the cutover in one dedicated commit and test/document one complete ordinary revert. Never restore
  only prompt or tool namespace, add an alias, rewrite history, or delete post-cutover local artifacts.
- **Verification:** require fake direct/context public E2E, schema/registry parity, no-side-effect workflow tests, exact
  13-tool/dual-prompt discovery and real stdio invocation, old-surface absence, full backend/frontend gates, and no live
  Azure call or production-promotion claim.

Plan audit result: **Pass after correction.** The audit confirmed exact baseline characterization, same-name prompt/tool parity, authority routing, request/tool/schema/result transaction, named legacy prompt/schema removal, untouched unsupported old artifacts, 13-tool target, frontend ownership protocol, and complete atomic rollback.

## Included Work

- Replace the old workflow prompt and compatibility tool with same-name prompt/tool registrations for
  `diagram_generation_workflow` using one private renderer and exact shared arguments/defaults/output.
- Add the tools-only “Call this first” description and guard the renderer against filesystem, context/readiness,
  generation, provider, and internal-prompt side effects.
- Rename `context_request_save` to `diagram_request_save` and support strict direct/context candidates through the
  Slice 2 shared path/digest/identity/finalization service.
- Rename `diagram_generate_from_prompt` to `diagram_generate_direct`; retain `diagram_generate_from_context` while
  switching it to the new request/input/result contracts.
- Wire direct/context branch routing, exact generation policy, compact quality, host actions, operation warnings,
  trace sidecars, and one safe numbered-debug run through public adapters.
- Activate all namespace-first schema IDs/kinds/files/registry paths and six mode/type logical contracts; remove old
  public schema constants/paths and explicitly reject old artifacts without mutation. Existing
  `.graphpilot/context/requests/` files remain untouched and unsupported; no migration, rewrite, move, or deletion occurs.
- Remove the specifically approved legacy `backend/assets/prompts/generate.md`,
  `backend/assets/prompts/repair.md`, `backend/assets/schemas/evidence-manifest.json`, and
  `backend/assets/schemas/diagram-request.json` in this same public-caller/registry cutover after replacement and
  stale-reference proof; no other prompt/schema file is removed.
- Replace old generated/blocked/partial-success transport with new mode-specific generated/blocked/error results and
  render warnings.
- Update MCP unit/contract tests and real stdio smoke for exact discovery schemas, 13 tools, dual namespace parity,
  direct/context fake E2E, old-name absence, and no internal-prompt exposure.
- Update only required frontend canonical types/adapters/parity tests and all active MCP/backend/generation/schema/
  environment/testing/README/decision/delivery owners in the same implementation cutover.
- Record the exact cutover commit, pre-cutover rollback target, verification, and local-artifact caveat in this slice
  outcome.

## Not In Scope

- Aliases, deprecation periods, dual schema acceptance/write, automatic migration, silent artifact rewrite/deletion, or
  a partial prompt-only/tool-only cutover.
- Reopening request, generation, semantic-review, trace/debug, or PyGraphviz behavior delivered by Slices 1–8 except for
  a proven integration defect.
- Executing repository inspection/readiness/generation inside the workflow instruction tool.
- A raw prompt-only generation tool, one polymorphic generation tool, or direct fallback from blocked context.
- Frontend generation UI/editor redesign, chatbot behavior, or browser-side repository gathering.
- Evaluation capture/matcher/judge/runner work (Slices 10–13), hidden gold, live provider calls, certification, or
  production promotion.
- Push, destructive Git operations, or deletion of existing local old/new artifacts.

## Target Areas

- `backend/mcp_server/server.py`
- `backend/mcp_server/smoke_test.py`
- `backend/tests/mcp_server/test_mcp_server.py` and `backend/tests/mcp_server/test_context_tools.py`
- `backend/services/`, `backend/services/context/context_persistence_service.py`, and shared operation problems
- `backend/services/generation/` — direct/context orchestrators, request adapters, result/trace/debug assembly
- `backend/services/readiness/` where namespace-first readiness contracts are consumed
- `backend/services/shared/schema_registry.py` and safe workspace/request path services
- `backend/assets/schemas/`
- `backend/assets/prompts/` — one public workflow renderer/template plus private branch assets
- backend generation/context/readiness/schema/LLM/MCP tests and approved fixtures
- `frontend/src/types/diagram.ts`, affected adapters, and parity/preservation tests only where the canonical contract
  requires them
- `README.md`, `backend/README.md`, and canonical MCP/backend/generation/validation/schema/context/environment/testing/
  decision/delivery owners under `docs/`
- this slice document

## Exit Criteria

- MCP prompt and tool registries both expose only `diagram_generation_workflow`; the old workflow name is absent from
  both, and identical arguments produce byte-identical renderer instructions.
- The workflow tool has the exact instructions-only structured/text payload, “Call this first” description, and tests
  proving zero filesystem/context/readiness/generation/provider side effects and no internal prompt exposure.
- Discovery requires `workspaceDir`/`request`, accepts only the three interaction preferences, defaults to `balanced`,
  defaults both trace/debug booleans to `false`, and preserves request whitespace/punctuation verbatim.
- Public tools expose only `diagram_request_save`, `diagram_generate_direct`, and
  `diagram_generate_from_context` for the redesigned request/generation path; old request/direct tool names and raw
  prompt-only input are absent.
- Direct and context fake E2E prove correct authority routing, canonical request loading, context readiness/policy, no
  blocked-context fallback, generated/blocked/error transport, render warning, host actions, and trace/debug propagation.
- Every new `$id` equals `schemaVersion`; schema IDs/kinds/files/registry accessors are unique and all producers,
  consumers, fixtures, diagnostics, results, and affected frontend types use the new contracts.
- Old IDs/paths return explicit safe unsupported-contract/path errors and do not rewrite/delete local artifacts; no
  alias, dual acceptance/write, or hidden migration exists.
- Successful persistence returns `generated` even when render adds `render_failed`; blockers are `isError: false` with
  no diagram/trace, and actual failures are `OperationProblem` with `isError: true`; active `partial_success` generation
  handling is absent.
- Real stdio smoke discovers the expected 13-tool target registry and both prompt/tool workflow namespaces, invokes
  both surfaces for exact parity, exercises offline direct/context failure/block paths, and confirms every old public
  name is absent.
- Active-code/config/test/doc stale searches find no old name/ID/path/result outside the explicit migration/history
  allowlist.
- Focused schema/request/generation/MCP/frontend tests, stale-surface searches, and the required PowerShell verification
  pass without a provider call:

  ```powershell
  cd backend
  uv run python manage.py test
  uv run python mcp_server/smoke_test.py
  cd ..\frontend
  npm run verify
  cd ..
  git diff --check
  ```

- Plan and implementation audits have no unresolved findings; the complete ordinary-revert command/target and
  post-cutover-artifact caveat are recorded, and no partial rollback state is supported.

## Previous Slice

[`08-pygraphviz-cutover.md`](08-pygraphviz-cutover.md)

## Next Slice

[`10-evaluation-capture-foundation.md`](10-evaluation-capture-foundation.md)

## Outcome

**Completion:** Performed the cold-turkey public transaction. MCP now exposes exactly 13 tools and one public prompt,
with `diagram_generation_workflow` registered in both prompt/tool namespaces through one side-effect-free renderer,
`diagram_request_save` sharing one strict direct/context lifecycle, and only `diagram_generate_direct` plus the redesigned
`diagram_generate_from_context` as generation primitives. Direct/context requests use `.graphpilot/requests/`; context
readiness remains mandatory and a blocked context attempt has no direct fallback.

**Pipeline and contracts:** Added the unified request-scoped generation orchestrator over strict packet construction,
pre-layout validation/repair, reviewed-default semantic review/repair, sole PyGraphviz layout, canonical validation,
exclusive persistence, render-warning success, and exact generated/blocked/error transport. Activated namespace-first
context/readiness contracts and minimal canonical request/manifest ownership with mode-specific origin enforcement.
Prompt/tool workflow arguments preserve exact request text and independently propagate trace/debug options. Numbered
debug runs can begin at readiness and resume safely through generation; compact traces remain successful-diagram-only.

**Removal and safety:** Removed the specifically approved generate/repair prompt assets, legacy evidence/request schemas,
raw-prompt/context generation adapters, their obsolete adapter tests, old request-path APIs, and all public aliases. Old
`.graphpilot/context/requests/` artifacts are neither read, moved, rewritten, nor deleted; focused tests prove explicit
path/schema rejection and byte preservation. Rollback is one ordinary revert of this complete Slice 09 implementation to
verified Slice 08 commit `ee394c3`; post-cutover new-format local artifacts remain untouched.

**Verification:** Implementation audit passed with no blocker/important findings. The complete backend suite passed 729
tests (4 skipped). Real stdio smoke passed exact discovery, schema/defaults, prompt/tool byte parity, bounded context
lifecycle, shared request save, and offline typed generation failures. Public fake direct/context E2E reached canonical
generated results. Frontend `npm run verify` passed lint, build, 406 Vitest tests, and all 40 Playwright canvas/SVG flows.
Python compilation and `git diff --check` passed; stale runtime/active-owner searches found no old public name, path,
result, or schema identity outside explicit migration history and negative rejection tests.

**Deviations:** The implementation uses one `DiagramGenerationService` and one `GenerationPacketBuilder` with strict
mode branches rather than duplicating direct/context orchestrator and input-builder classes. The public/result/authority
contracts and all acceptance boundaries are unchanged. The specifically superseded adapter-only tests were replaced by
strict service, public transport, cutover, diagnostics, fake-E2E, and real-stdio coverage. The unregistered pre-cutover
compatibility template remains inert on disk because the approved deletion set explicitly prohibited removing any other
prompt file; no registry, renderer, or runtime consumer references it.

**Follow-up:** Slices 10–13 add the downstream offline evaluation framework without changing generation acceptance or
the public MCP surface.
