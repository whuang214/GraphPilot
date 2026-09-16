# Lane A Slice 06: Host Interface

## Purpose

Implement the committed structured route tool and selected mode/type authoring-contract lookup without changing context persistence, provider/runtime behavior, or shared MCP registration.

## Design

`diagram_generation_workflow` becomes one model-callable tool whose structured plan owns authority/type selection, next-tool guidance, high-level branch order, and critical safety invariants. `diagram_generation_get_authoring_contract` returns only the selected direct/context and diagram-type recipe, including complete validated examples, current/missing/stale guidance, conditional type checks, and code-keyed recovery references.

No second MCP prompt or Markdown workflow authority remains. MCP text is a minimal presentation of the structured plan, not a separate maintained contract.

## Included Work

- Immutable host workflow-plan value model and strict serialization.
- Side-effect-free route-tool service over the original request and interaction/observability arguments retained by A03.
- Selected direct/context authoring-contract service and mode/type dispatch.
- Copy-isolated loading of canonical leakage-disjoint examples/checklists.
- Selected-only output proof and full-schema/unrelated-content exclusion.
- Static/serialized UTF-8 byte-budget checks.
- Authority, no-fallback, unsupported-fact, no-rerun, timeout, and reporting invariants.
- Tool description/input/output contract tests without active MCP registration.
- The runtime discovery pointer required by the frozen contract in [`03-mcp-tools/README.md`](../../../../../../../02-architecture/01-mcp-tools/README.md): `context_evidence_save` and `diagram_request_save` rejections name where the authoring contract can be fetched. A04 froze this requirement but could not implement it, because a rejection naming an unregistered tool would send a host nowhere; it lands here with the tool that makes it true.
- Removal/retirement plan for the old prompt asset from active runtime, preserving only immutable historical evidence identities.

## Not In Scope

- Context persistence/request code, MCP server registration, schema registry, generation/readiness/provider behavior, canonical diagram metadata, benchmark execution, frontend, or shared docs integration.
- Copilot-specific automation or a generalized host adapter.

## Target Areas

A03 must replace this paragraph with an exact committed file list before A05 begins. The ownership boundary is the host workflow-plan/renderer model, authoring-contract service, selected example/checklist assets, and focused generation/MCP contract tests. A05 may not modify context/request persistence services owned by A04, shared schema registration, `mcp_server/server.py`, canonical diagram/frontend types, integration docs, or any Lane B file.

## Exit Criteria

- Stage 1 is one structured tool contract with minimal generated text and no separate MCP prompt authority.
- Stage 2 rejects unknown mode/type and returns only the selected contract.
- Complete examples pass canonical schemas/semantic validators and remain leakage-disjoint from Todo.
- Route plus selected contract meets the approved byte budgets.
- Rendering/lookup performs no workspace read, file write, provider construction/call, readiness, or generation.
- Critical authority/recovery/no-rerun rules are machine-checkable and cannot drift into an alternate text contract.
- Focused tests and independent implementation audit pass before commit.

## Previous Slice

[`lane-a-04-authoring-discoverability.md`](lane-a-04-authoring-discoverability.md)

## Next Slice

[`lane-a-07-integration.md`](lane-a-07-integration.md), after A05 also commits.

## Outcome

To be completed.
