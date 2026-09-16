# Slice 01: Active Design Promotion

## Purpose

Promote the reviewed evidence-context research, refactor every affected main product/architecture/design owner
into one coherent final intended system, establish the Epic 3 extension plan, and retire research as implementation
authority without changing runtime behavior.

## Background

The research package defines the workflow, JSON 1, JSON 2, readiness, grounded generation/provenance, and MCP
surface. The approved transition matrix is
[`08-implementation-and-promotion.md`](../../../../06-research/evidence-based-diagram-context/08-implementation-and-promotion.md).
Code must not begin from research-only contracts.

## Design

Promotion is section-based and staged. A topic becomes active only after its destination, links, owner summary,
and cross-contract references are verified. Promotion establishes a living baseline: later implementation
findings update active owners, decisions, tests, dependent slices, and slice outcomes rather than rewriting
historical research.

## Included Work

- Create `docs/02-design-and-features/08-context-backed-generation/` and its readiness package.
- Create `docs/01-architecture/03-mcp-tools/` for existing tools, context tools, and host workflow.
- Refactor affected product, system, backend, frontend, API, MCP, schema, mapping, validation, rendering,
  generation, edit, testing, decision, and navigation owners so the full final design is primary rather than an
  appended planned extension.
- Add this Epic 3 group and synchronize the Epic 3 slice plan and live status.
- Reconcile the concurrent README simplification without restoring duplicated detail.
- Audit every research heading as promoted, merged, historical rationale, or explicit non-goal.
- Mark the research workspace historical only after every promotion gate passes.

## Not In Scope

- Backend, MCP, API, frontend, schema, or runtime behavior changes.
- Creating implementation assets from research before their active owner exists.
- Committing or pushing before user verification.

## Target Areas

- `docs/00-product-and-requirements/`
- `docs/01-architecture/`
- `docs/02-design-and-features/`
- `docs/03-development-and-delivery/`
- `docs/research/evidence-based-diagram-context/`
- `AGENTS.md` and affected navigation READMEs

## Exit Criteria

- Active feature and MCP packages exist with one owner per topic.
- Affected main design owners describe one coherent final intended system in present tense; implementation
  status appears only in delivery docs and runnable quickstarts.
- Cross-cutting owners contain their complete assigned design responsibility and link to exact feature contracts.
- All local links, complete JSON examples, and normative rubric JSON parse.
- No active doc uses research as current implementation authority.
- Research is clearly historical and points to active owners.
- `git diff --check` and the promotion coverage audit pass.
- The user has copy-paste documentation verification steps before any commit.

## Previous Slice

- Start of Epic 3's `04-context-backed-generation/` extension group.

## Next Slice

- [`02-readiness-rubric-and-policy.md`](02-readiness-rubric-and-policy.md)

## Outcome

Completed the documentation-only promotion and final-design integration. Created the active
`08-context-backed-generation/` feature package and final `03-mcp-tools/` architecture package, added this Epic 3
extension group, converted research into historical rationale, and refactored every affected main product,
architecture, schema, mapping, validation, rendering, generation, edit, decision, and navigation owner into one
coherent intended system. Implementation status now appears only in delivery owners and runnable quickstarts.

Deviations and refinements: user review expanded this slice from structural promotion to complete final-design
integration. The architecture audit retained readiness, canonical diagram validation, generation acceptance,
persistence validation, renderer guards, and frontend guards as separate trust boundaries. `WorkspaceStorageService`
remains the one low-level `.graphpilot` I/O owner and is extended rather than wrapped by another file service;
system design now describes that boundary generically, while backend architecture names every intended service.
Shared generation phases are extracted only when the second generation mode needs them. Promotion also specified
exact `generation_context_changed` digest fields, removed a stray non-contract `selectedClaimCount` example, and
removed the redundant single-file MCP pointer after updating its historical links.

Final user-review refinement established one shared transient `OperationProblem` value for handled failures,
expected generation-gate blockers, and nonfatal post-persistence warnings. All MCP tools share
`content`/`structuredContent`/`isError`, keep tool-specific success payloads, and set `isError: true` only for actual
failure. Direct/context generation share generated/partial/error semantics; context generation additionally owns
blocked. HTTP maps the same problem value under `error`, and render-on-save warnings do not misreport a successful
canonical save as failed. Delivery slices now coordinate the existing MCP/API/frontend migration before context
generation lands.

Verification: checked 170 documentation/root-navigation files and 657 local links with zero broken paths; checked
29 local Markdown anchors with zero broken anchors; parsed 150 JSON fences and six standalone JSON files with zero
failures; confirmed all Markdown fences balanced; validated 11 `error`/`blocker`/`warning` examples against required
`OperationProblem` fields; confirmed the three active normative rubric JSON files are byte-identical to research;
confirmed no stale canonical flat-path examples or transitional planned/current/target framing remains in affected
active design owners; fixed two pre-existing malformed research TOC anchors; `git diff --check` passes. Mermaid
render validation was not requested and remains opt-in. No runtime code, commit, or push was performed.

User approved the final integrated design on 2026-07-15. Follow-up:
[`02-readiness-rubric-and-policy.md`](02-readiness-rubric-and-policy.md).
