# Slice 03: Generation Service (core pipeline)

## Purpose

Implement `DiagramGenerationService`: turn a prompt into a saved, validated, rendered canonical diagram. Design: `docs/02-design-and-features/04-generation-design.md`.

## Included Work

- implement an injectable LLM client seam: an `LLMClient` protocol, an `AzureLLMClient` wrapping the `openai` SDK `AzureOpenAI`, and a `FakeLLMClient` (canned per-type logical output) for offline tests. Config from env — **`AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_DEPLOYMENT`** (default `gpt-5.4`, the Azure deployment name; `gpt-5.4-mini` also available); the SDK-required `api_version` has a built-in default (optional `AZURE_OPENAI_API_VERSION` override). `is_configured()` so a missing key fails cleanly.
- add a small `PromptService` loader that reads Markdown templates from `backend/assets/prompts/` and fills `{{placeholder}}` tokens (no new templating dependency)
- author the externalized `generate` + `repair` templates under `backend/assets/prompts/`; build the prompt by filling them (type vocabulary + per-type `prompts.md` + static 2–3 few-shot projected to logical form + user prompt + optional style); request a **logical** diagram (`{nodes:[{id,semanticType,label,parentId?}], edges:[{source,target,semanticType?,label?}], name?}`) as **`json_schema` structured output, with a `json_object` + parse fallback** when the deployment / api-version doesn't support strict schemas
- conform/repair the logical output to the type vocabulary — **vocabulary + structural only**: coerce `semanticType`s to the allowed set, drop edges with missing endpoints, ensure unique ids + present labels (no per-type semantic rules for MVP); stamp `metadata.authoring = "generated"`
- assign sizes + lay out (Slice 02), assemble canonical JSON, validate (one repair round on failure), name + save (`create_diagram`), render (Slice 01)
- the service signature accepts an **optional `name`**; naming precedence is **caller/MCP-provided `name` → LLM-suggested `name` → slug of the prompt** (then `create_diagram` sanitizes + de-dupes)
- add the `openai` dependency (pinned); add the env vars to settings + `.env.example` (real key only in local `.env`)
- unit tests with the fake client: full pipeline offline — conform, sizing, layout fallback, validation gating (invalid → no write), name precedence + dedupe, render called, structured-output fallback path

## Not In Scope

- the `diagram_generate` MCP tool surface (Slice 04)
- the eval framework + DOE (removed — pending an embeddings-based rebuild)
- editing existing diagrams (Epic 4)

## Target Areas

- backend generation service + LLM client + `PromptService` loader + tests
- `backend/assets/prompts/` (new: `generate` + `repair` templates)
- `requirements.txt`, settings, `.env.example`
- generation + blueprint design docs

## Exit Criteria

- the service generates a valid, type-conformant, `generated`-stamped diagram for all three types and saves + renders it
- invalid output (after one repair round) is not written
- unit tests pass offline with a fake LLM client (no key / network)
- `python manage.py test` passes

## Previous Slice

- `../01-render-and-layout/02-layout.md`

## Next Slice

- `04-generate-tool.md`

## Outcome

> Historical outcome: verification below used the original layout subsystem. Redesign Slice 08 removed that subsystem;
> current generation uses only the pinned `PyGraphvizLayoutEngine`.

✅ Completed.

**Delivered.** `DiagramGenerationService` (`backend/services/generation/pipeline/diagram_generation_service.py`) turns a prompt into a saved, validated, rendered canonical diagram, fully offline-testable.

- **LLM seam** (`services/llm/llm_client.py`): `LLMClient` protocol + `AzureLLMClient` (lazy `openai` import; `json_schema` structured output with a `json_object`+parse fallback; `is_configured()`) + `FakeLLMClient` (dict / queue / callable responses) for offline tests.
- **Prompts** (`services/llm/prompt_service.py` + `graphpilot/prompts/{generate,repair}.md`): externalized `{{placeholder}}` templates filled with the type vocabulary, per-type `prompts.md` guidance, 2 few-shot answer keys projected to logical form, the user prompt, and optional style.
- **Pipeline:** ask LLM for a logical diagram → `conform_logical` (vocabulary + structural only: coerce off-vocab semantic types to a per-type default, drop dangling edges, unique ids + non-empty labels, remap/drop `parentId`) → `assemble_canonical` (sizes + layout via Slice 02, per-type `node_type`, default styles, `metadata.authoring="generated"`) → validate → **one repair round** on failure → name + `create_diagram` → render (Slice 01).
- **Naming precedence:** caller `name` → LLM `name` → prompt slug (then sanitize + de-dupe).
- **Config/deps:** `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_DEPLOYMENT` (default `gpt-5.4`; `api_version` defaulted `2024-10-21`) in settings + `.env.example`; `openai==2.42.0` pinned.

**Verification.** `python manage.py test` → 227 OK (offline; fake client + grandalf — no key, network, or Graphviz binary). **Verified live** against the real Azure `gpt-5.4` deployment (activity + use-case diagrams generated, saved + rendered; containment preserved via `parentId`).

**Fix during bring-up.** A present-but-empty `.env` value (e.g. `AZURE_OPENAI_API_VERSION=`) was becoming an empty string and causing a live Azure `404`; settings + the client now treat empty values as "use the default" (`.strip() or <default>`).

**Post-review fixes (`/review`).** (1) `LOGICAL_SCHEMA` is now **OpenAI-strict-compliant** (all `properties` keys in `required`, optionals nullable) — the `json_schema` structured-output path now succeeds on the **first** call (verified live), instead of being rejected and silently falling back to `json_object` on every generation (a wasted extra round-trip). (2) The fallback heuristic is narrowed to genuine response-format errors so unrelated bad requests surface. (3) Conform keeps `parentId` only when it points at a **container** semantic type (`systemBoundary`), and **sanitizes node ids** to safe identifiers. Added tests for all three (schema strict-compliance, non-container parent dropped, id sanitization).

**Backend bug-audit fixes.** A full backend audit surfaced two issues, now fixed: (1) `GraphvizLayoutEngine` crashed parsing `dot -Tplain` when a node id contained a space (the quoted name split into two tokens) — ids are now mapped to safe DOT tokens (`n0`, `n1`, …) and reversed on output, so any id is safe; (2) `DiagramRenderService._num` now rejects non-finite values (NaN/inf), so a malformed coordinate from the pre-validation preview route can't leak `nan`/`inf` into the SVG. Regression tests added (spaced-id Graphviz layout, `_num` finiteness, token-only DOT).

**Deviations.** Render failure after save raises `GenerationRenderError` (the file is already saved), matching the `diagram_generate` "render fails after save" error case. Conform is deliberately minimal (no per-type semantic rules); the validation gate + one repair round are the backstop. The `diagram_generate` MCP tool surface is **Slice 04**.

**Follow-ups.** Slice 04 exposes this over MCP (paths + `editUrl`); a live run needs real `AZURE_OPENAI_*` in `backend/.env`.
