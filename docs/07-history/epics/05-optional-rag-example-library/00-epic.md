# Epic 5: Optional — RAG / Example Library Extension

> **Optional / post-MVP.** Epic 5 is explicitly outside the MVP Definition of Done — the base definition lists "RAG Local Examples / `diagram_search_examples`" under *MVP Out of Scope*. It is captured here so the deferred backlog theme has a stable epic definition; its slices are not yet planned as numbered docs and it does **not** block Epics 1–4.

## Goal

Improve `diagram_generate_from_prompt` quality by adding **optional example retrieval (RAG)** over a curated local example library, exposed as a `diagram_search_examples` MCP tool, so generation can be grounded in the most relevant prior examples for a prompt rather than a fixed per-type few-shot set.

## User Scenario

A user asks the IDE agent to generate a diagram. Before generating, GraphPilot retrieves the most relevant curated examples for the prompt + `diagramType` from the local example library and feeds them to `diagram_generate_from_prompt` as additional few-shot context, so the generated diagram more closely follows the conventions of similar prior diagrams. A developer evaluating generation quality can also call `diagram_search_examples` directly to inspect which examples a prompt retrieves, and compare generation output **with vs. without** retrieval.

## Scope

- **Curated example corpus** — reuse and extend the **16 curated examples per type** (4 training + 12 held-out eval) under `backend/assets/blueprints/<type>/examples/<pool>/<name>/{prompt.md, output.gp.json}` as a retrieval corpus tagged/queryable by `diagramType`.
- **`diagram_search_examples` MCP tool** — input: a query (prompt text) + optional `diagramType` and result count; output: the top matching examples (prompt + `output.gp.json` references). The tool is listed today under *Deferred Tools* in `03-mcp-tools/README.md`; this epic would define its contract.
- **Retrieval store** — a local retrieval index over the curated examples. The base definition names an **MSSQL-backed RAG** store as the option; the concrete backend (lightweight file/embedding index vs. MSSQL) is a decision to confirm when the epic is scheduled.
- **Retrieval-augmented generation** — `diagram_generate_from_prompt` (Epic 3) can optionally consume the retrieved examples as few-shot context in place of, or in addition to, the fixed per-type example set, then strict-check / conform the result against the type vocabulary as it does today.
- **With/without comparison** — use the planned embeddings-based rebuild of generation evaluation to compare quality **with vs. without** example retrieval, so the extension is adopted only if it measurably helps.

## Out of Scope

- Anything in the MVP itself — Epic 5 is post-MVP and does not block Epics 1–4.
- New MCP tools beyond `diagram_search_examples` (`diagram_edit` and `diagram_export` remain deferred — see `03-mcp-tools/README.md`).
- New diagram types beyond `activity_diagram`, `use_case_diagram`, `bdd_diagram`.
- Changes to the canonical diagram schema, the supported style subset, or the `load` / `save` / `generate` / `update` contracts.
- A general-purpose vector-search / embeddings platform; retrieval stays scoped to GraphPilot's own curated examples.
- Hosting the retrieval store as a shared/remote service (MVP persistence stays local; an MSSQL store, if adopted, is a local/optional backend choice to confirm when scheduled).

## Dependencies

Epic 5 depends on **Epic 3** (`diagram_generate_from_prompt` + `PromptDiagramGenerationService`) as the consumer of retrieved examples, on the curated example / answer-key library as the retrieval corpus, and on the planned embeddings-based generation-evaluation rebuild to prove the with/without-retrieval value. See `../03-mcp-generation-and-wrappers/00-epic.md`, `../../../02-design-and-features/06-answer-key-generation-design.md`, and `../../../02-design-and-features/07-evaluation-and-doe-design.md`. It **blocks** nothing — it is an optional quality extension layered on top of a working generation flow.

The retrieval slices proper (`diagram_search_examples` + the retrieval store, then wiring retrieval into `diagram_generate_from_prompt`, then the with/without comparison after the evaluation rebuild) are not yet planned as numbered docs.

## Research / Inputs

- `docs/03-development-and-delivery/02-backlog.md` — the active post-MVP RAG / example-library backlog.
- `docs/02-design-and-features/07-evaluation-and-doe-design.md` — the pending embeddings-based generation-evaluation rebuild needed for the with/without comparison.
- `docs/01-architecture/03-mcp-tools/README.md` — `diagram_search_examples` is listed under *Deferred Tools* ("Example retrieval or RAG is outside current MVP scope").
- `docs/02-design-and-features/04-generation-design.md` — the current generation-context model (examples library + per-type `prompts.md` + type profile) that retrieval augments.

## Acceptance Criteria

- The retained curated corpus (currently 16 examples per type) is indexed and queryable by `diagramType`.
- `diagram_search_examples` can be called from an IDE MCP client and returns the most relevant curated examples for a query + `diagramType`.
- `diagram_generate_from_prompt` can optionally consume retrieved examples as generation context.
- The rebuilt generation evaluator can produce a **with-retrieval vs. without-retrieval** quality comparison for the MVP diagram types.
- Retrieval is fully optional: with the extension disabled, Epic 3 generation behaves exactly as before.
- Unsafe or missing paths / inputs are rejected (consistent with the other MCP tools).

## Related Docs

- `../README.md`
- `../00-current-state.md`
- `../02-react-editor-and-export/00-epic.md`
- `../03-mcp-generation-and-wrappers/00-epic.md`
- `../04-mcp-edit-workflow-and-hardening/00-epic.md`
- `../../02-backlog.md`
- `../../00-development-environment.md`
- `../../../01-architecture/03-mcp-tools/README.md`
- `../../../02-design-and-features/04-generation-design.md`
- `../../../00-product-and-requirements/02-requirements.md`
