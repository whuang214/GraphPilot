# Slice 12: Workflow Client Compatibility

## Purpose

Expose GraphPilot's existing public context-backed host workflow through both MCP prompt and MCP tool discovery so
prompt-capable clients and tools-only agents receive exactly the same workflow instructions without duplicating or
executing the workflow.

## Background

GraphPilot already registers and real-stdio verifies the standards-compliant MCP prompt
`context_backed_generation_workflow`. The active VS Code Copilot CLI-backed MCP gateway discovers tools/resources but
does not request `prompts/list`, so the workflow is invisible to that tools-only agent loop even though the server
implementation is correct.

FastMCP prompt and tool registries use separate namespaces and permit the same public name. The approved compatibility
pattern is:

```text
one private workflow renderer
├── MCP prompt: context_backed_generation_workflow
└── MCP tool:   context_backed_generation_workflow
```

This current-workflow bridge is also the implementation proof for the future generation redesign's dual
`diagram_generation_workflow` prompt/tool surface. It does not implement or promote that future workflow.

## Design

Extract one private renderer from the current prompt handler:

```python
def _render_context_backed_generation_workflow(
    workspace_dir: str,
    request: str,
    interaction_preference: Optional[str],
    persist_readiness_debug: bool,
) -> str:
    ...
```

Keep the existing prompt registration and add a separately named Python handler registered as a tool under the same
public MCP name. Both accept the same four arguments and invoke only the private renderer.

The tool returns:

```json
{
  "kind": "contextBackedGenerationWorkflow",
  "workflow": "context_backed_generation_workflow",
  "instructions": "<exact renderer output>"
}
```

Its public description states:

> Call this first when the user requests a repository-grounded GraphPilot diagram. It returns the public host workflow
> instructions; follow them using GraphPilot's bounded context tools.

The tool returns instructions only. It does not inspect files, write artifacts, call Azure, apply readiness actions,
replace any one-shot context tool, or expose internal evidence-authoring/readiness/generation/repair/provider prompts.

Active MCP documentation must narrow the current broad statement that no tool returns prompts: the bridge intentionally
returns public host workflow instructions while internal prompts remain private.

## Plan Audit

The plan audit must verify:

- **Public compatibility only:** scope is one current workflow renderer with dual registry exposure; no unified
  generation redesign, direct-generation change, chatbot, frontend, Agent Skill, or source-gathering implementation.
- **Exact parity:** prompt and tool use the same renderer and identical argument/default handling; there is no copied
  template logic or independently maintained instruction text.
- **No side effects:** tool invocation cannot reach filesystem persistence, context services, readiness/generation
  services, or the LLM client. Unit tests patch/guard those boundaries.
- **MCP transport:** same public name is present in both registries; tool schema requires `workspaceDir`/`request` and
  optionally accepts `interactionPreference`/`persistReadinessDebug`; structured payload is exact and text content is
  the same instruction string.
- **Verbatim authority:** request whitespace/punctuation and workspace/preference/debug values render identically for
  prompt and tool.
- **Real stdio proof:** smoke test updates expected tool count, lists both registries, invokes prompt/tool with the same
  arguments, asserts exact parity/payload, and retains existing workflow-content checks.
- **Canonical docs:** MCP public surface and context-workflow owner explain user-invoked prompt versus model-callable
  compatibility tool; backend README, decision log, group/epic plans, current-state board, and slice outcome remain
  consistent without exposing internal prompts.
- **Reversibility:** rollback removes the tool registration/private renderer and restores the current prompt handler's
  inline `_prompt_service.render(...)` argument/default handling. Existing bounded context tools, template content,
  and prompt output remain unchanged.
- **Verification:** focused MCP unit/stdio tests and the complete offline backend suite are required; no live Azure call
  or frontend change belongs to this slice.

Plan audit result: **Pass.** The audited plan clarifies the 13-total-tool count, adds an explicit private-renderer
preservation test, verifies exact required/optional discovery schema, requires verbatim whitespace/punctuation,
specifies prompt-handler rollback, and makes the context-workflow documentation change explicit. No scope was added
beyond the approved compatibility bridge.

## Included Work

- Extract the one private renderer used by both registrations.
- Preserve `context_backed_generation_workflow` as an MCP prompt.
- Register a tool under the same public name with matching arguments/defaults.
- Return exact structured kind/workflow/instructions fields and the renderer output as text content.
- Add failing unit tests before implementation for the private renderer's exact preservation of the current prompt
  handler output, dual discovery, list-tools required/optional argument schema, parity, structured payload, verbatim
  whitespace/punctuation preservation, and no side effects.
- Extend real stdio smoke coverage for 13 tools, dual registry presence, prompt/tool invocation parity, and payload.
- Update active MCP public-surface docs and add an explicit context-workflow section distinguishing the user-invoked
  prompt from the model-callable same-name bridge, their identical arguments/instructions, and their instructions-only
  behavior; update backend README, decision log, group/epic plans, current-state board, and this slice outcome.

## Not In Scope

- Agent Skill files.
- Frontend/browser changes or frontend MCP client work.
- Chatbot implementation.
- Direct prompt-generation redesign.
- The future unified `diagram_generation_workflow` implementation.
- Repository-context gathering in the frontend.
- Any filesystem, JSON 1/JSON 2, readiness, generation, or provider execution inside the bridge.
- Azure/live tests or readiness calibration changes.
- Renaming/removing existing one-shot tools.

## Target Areas

- `backend/mcp_server/server.py`
- `backend/tests/mcp_server/test_mcp_server.py`
- `backend/mcp_server/smoke_test.py`
- `docs/01-architecture/03-mcp-tools/README.md`
- `docs/01-architecture/03-mcp-tools/03-context-workflow.md`
- `backend/README.md`
- `docs/02-design-and-features/decision-decisions.md`
- `docs/03-development-and-delivery/epics/00-current-state.md`
- `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/00-epic.md`
- `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/04-context-backed-generation/00-group.md`
- this slice document

## Exit Criteria

- Prompt and tool registries both expose exact public name `context_backed_generation_workflow`.
- Required/optional argument schemas match the approved contract and preserve current defaults.
- Prompt and tool return byte-identical instructions for identical arguments.
- Tool structured content is exactly kind/workflow/instructions and text content is the instruction string.
- The original request, including all whitespace and punctuation, remains verbatim and all other values render
  identically.
- `list_tools` confirms exact required fields `workspaceDir`/`request` and optional
  `interactionPreference`/`persistReadinessDebug`.
- Tests prove invocation performs no filesystem or Azure/provider call.
- Real stdio smoke lists 13 total registered tools (the current 12 including `health`/`echo`, plus the bridge),
  discovers both namespaces, invokes both surfaces, and verifies parity.
- Active MCP/backend/decision/delivery docs distinguish public instructions from internal prompts and remain coherent.
- Focused MCP tests, stdio smoke, `git diff --check`, and `cd backend; uv run python manage.py test` pass.
- Plan and implementation audits have no unresolved findings.

## Previous Slice

[`11-diagnostics-and-release-gate.md`](11-diagnostics-and-release-gate.md)

## Next Slice

Phase 0A planning and Phase 0B active-design promotion are committed before this implementation. After the compatibility
implementation commit, record it as the exact pre-redesign code baseline, then begin generation-redesign Slice 01. This
slice has no direct successor inside the current context group.

## Outcome

**Completion:** Implemented one private current-workflow renderer and exposed its exact instructions through same-name MCP
prompt and instructions-only tool registrations. The tool returns the approved structured payload plus identical text,
requires no existing workspace, and executes no context, readiness, generation, persistence, or provider operation.

**Deviations:** Canonical MCP design docs had already been cold-turkey promoted to the final unified workflow before this
transitional bridge, so current-runtime compatibility wording was updated in the root/backend READMEs and delivery
owners rather than reintroducing the old workflow as final canonical design. Implementation commit `1f14546` is the
exact final pre-redesign code baseline recorded in redesign Slice 01.

**Verification:** Added failing-first private-renderer, dual-discovery schema, parity, verbatim, structured/text payload,
and no-side-effect unit tests. The focused six-test class passes; real stdio smoke lists 13 tools and verifies exact
prompt/tool parity; the implementation audit passed with no finding. `git diff --check` and the complete provider-free
backend suite pass.

**Follow-up:** Generation-redesign Slice 01 consumes this dual-namespace proof without changing the current public
surface until the atomic unified cutover in redesign Slice 09.
