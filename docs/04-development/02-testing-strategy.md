# Testing Strategy

## Purpose

This document describes how GraphPilot is tested: the testing principles, the test layers and where they live, how to
run them, and what testing is expected per epic. It is the standing reference for the "testing direction" the
documentation set advertises. Per-slice verification is still recorded in each slice's `## Outcome` section; this doc is
the cross-cutting view that those outcomes plug into.

Commands and file maps labeled **current** describe runnable code today. The **final intended redesign** coverage is the
promoted contract implemented through the audited Epic 3 slices; delivery status belongs to the
[current-state board](../05-delivery/01-current-state.md). Component command details stay in `backend/README.md` /
`frontend/README.md`; this owner records the verification role and provider-safety boundary.

## Testing principles

- **Shared services are the source of truth.** The browser-facing API and the IDE MCP tools are thin layers over the same services in `backend/services/`. Tests cover core behavior once at the service layer and re-confirm each entry point's client-specific response contract at the edge.
- **No database for diagram logic.** Diagram persistence is local files under `.graphpilot/`, not a database. Diagram-related tests use Django's `SimpleTestCase` (no DB setup/teardown). Django's default tables exist only for framework internals.
- **File I/O uses temporary directories.** Tests that exercise `WorkspaceStorageService` (path safety, load, atomic write) operate against temp dirs so they never touch a real workspace.
- **Real artifacts where it matters.** MCP, validation, and render tests use the real schema artifact, type profiles, and curated examples rather than mocks, so the tests reflect production behavior.
- **There is no provider seam to fake.** GraphPilot calls no model, so every test is
  offline by construction rather than by discipline: no credentials, no fake client, no
  `--live` gate, no execution mode. Pinned PyGraphviz with its bundled plugin means no
  external Graphviz executable either. The stdio smoke test makes no network call of any
  kind.
- **The same draft must always produce the same diagram.** Determinism is the property
  that makes a materializer testable at all, and it is what a generator could never offer.
  A test asserts an exact canonical document, not that something plausible came back.
- **Trust boundaries are tested separately.** Draft validation, evidence resolution,
  materialization, canonical validation, persistence, renderer guards and frontend runtime
  guards keep separate tests, because each protects a different input against a different
  mistake.
- **A refusal is behaviour, so it is tested like behaviour.** Every rule that can refuse a
  draft has a test naming the rule, and a further test reads the refusal codes out of the
  services and fails if one is not explained in the authoring contract — a rule a host can
  only learn by failing is a rule we have not stated.

## Test layers

The backend tests live under `backend/tests/`, grouped into subpackages that mirror the implemented
`services/` groups (`tests/shared/`, `tests/diagrams/`, `tests/drafts/`, `tests/materialization/`)
plus `tests/api/` and `tests/mcp_server/`. Django discovers every package recursively.

| Layer | File(s) | What it covers |
| --- | --- | --- |
| Shared accessors | `tests/shared/` | `DiagramTypeService`, `SchemaRegistry`, canonical digests, `OperationProblem`, and `WorkspaceStorageService` path/storage primitives. |
| Catalog | `tests/diagrams/` | Element catalog and per-type profile vocabulary, and the curated example pool. |
| Validation | `tests/diagrams/test_validation_service.py`, `test_structural_constraints.py` | Canonical diagram validation and the per-type structural critic. |
| Persistence | `tests/diagrams/test_persistence_service.py` | Validation-gated canonical writes, no-ops, and conflicts. |
| Layout | `tests/diagrams/layout/` | PyGraphviz lifecycle, geometry, failure, platform, scale, and concurrency; per-type direction and `parentId` containment. |
| Rendering | `tests/diagrams/rendering/` | `DiagramRenderService` SVG/PNG shapes, saved-coordinate handling, and sibling output. |
| Drafts | `tests/drafts/` | Draft validation, evidence reading and digesting, freshness, and the authoring contract projection. |
| Materialization | `tests/materialization/` | Draft â†’ canonical golden fixtures per diagram type, covering every relationship kind and its notation rule. |
| MCP tool surface | `tests/mcp_server/` | The thin MCP handlers, confirming they are backed by the shared services so MCP and the API agree, and that the retired provider-backed tools stay absent. |
| API routes | `tests/api/` | The browser-facing DRF routes (load, save, list, validate, render). |

Every backend test is offline and deterministic. **There is no provider seam to fake**,
because there is no provider: the removal of the LLM client, readiness, and semantic review
took their fake clients, strict-schema projections, and call-budget fixtures with them.

### What the suite must prove

| Concern | Required proof |
| --- | --- |
| Draft acceptance | Unique IDs, resolvable endpoints, real evidence references, assurance pairing, and per-type notation legality — each rejected with an exact path |
| Evidence | Locator resolution, region digesting, unreadable-locator and past-EOF errors, and stale detection scoped to cited regions only |
| Materialization | Determinism (same draft, same bytes), ID preservation, relationship-end construction per semantic type, and feature normalization |
| Notation rules | Composition carries a source end; generalization and dependency carry none; a forbidden end is rejected rather than dropped |
| Canonical output | Every materialized fixture passes `DiagramValidationService` and renders to SVG |
| Create pipeline | Refusal to overwrite, atomic persistence, render-failure isolation, and editor-URL shape |
| Layout | Native lifecycle lock and close-on-error, malformed and non-finite failures, containment, repeatability, and the 256-node boundary |
| Parity | Canvas and SVG derive the same notation from the same canonical fields |


The frontend suite lives under `frontend/` and is run with Vitest (unit) and Playwright (E2E):

| Layer | Location | What it covers |
| --- | --- | --- |
| Unit (Vitest + RTL, jsdom) | `frontend/src/**/*.test.{ts,tsx}` | The adapters (canonical ↔ React Flow round-trip, runtime-field stripping), the API client (mocked `fetch`), editor logic (`clone`, `recents`, `palette`, `containment`, `edgeRouting`, `jsonDiff`, `nodePatch`, `nodeStyle`, `resize`, `validation`), the hooks (`useUndoRedo`, `useColorMode`, `useRail`), the export/file-system helpers, and UI/editor components. |
| E2E smoke (Playwright, Chromium) | `frontend/e2e/` | Boots Django + Vite and drives load/edit/save, real-pointer movement/save/reload for all 17 authorable node identities with console/network health checks, undo including keyboard deletion, failed-autosave backoff, preview cancellation, browsing, connector identity/modes/boundaries, duplicate/delete, structured notation, and PNG/SVG export. |

## Where tests live and naming

- Backend tests live under `backend/tests/` — in subpackages mirroring `services/`, plus `tests/api/`, `tests/docs/`, and `tests/mcp_server/` — and are named `test_*.py`.
- Diagram-logic test cases extend `django.test.SimpleTestCase` (no DB).
- File-backed tests build their fixtures in temporary directories.
- `tests/docs/` holds the guards that compare a document to the code it describes. They are tests because every drift found here had the same cause: a hand-maintained description of a machine-readable thing, with nothing comparing the two.
- To drive the MCP surface over the real stdio transport, use the `graphpilot-mcp` skill. *(There was a `backend/mcp_server/smoke_test.py` doing this; it went with the provider pipeline, and two documents kept telling readers to run it.)*
- Frontend unit tests sit next to the code they cover (`*.test.ts(x)`); the Playwright specs live under `frontend/e2e/`.

## How to run the current repository

**Backend, the whole gate:**

```text
cd backend
uv run python manage.py test --parallel 24
```

595 tests in about eight seconds, fully offline. There is no inner-loop/full-gate split and
nothing is tagged `slow`: the provider pipeline that made the suite slow is gone, and a
suite this fast does not need a faster subset.

The suite is CPU-bound and parallel-safe. Django distributes work by `TestCase` class, so
one large class is a single serialized bucket however many workers are idle — split by
concern rather than growing a class. Drop `--parallel` only when a traceback is hard to
attribute; the parallel runner reports failures as a `PicklingError` that hides the cause.

**Frontend:**

```text
cd frontend
npm run verify          # lint + build + test + e2e
npx tsc --noEmit -p tsconfig.app.json
```

**Look at the diagrams.** Numbers do not catch a diagram that is legible but wrong, and
this is the only check that involves a person:

```text
cd backend
uv run python manage.py review_gallery --regen eval
```

That rebuilds all 48 examples from their stored drafts and serves one page at
`http://127.0.0.1:8123/` — 36 answers, 9 host-generated, 3 training. Plain `review_gallery`
re-renders what is on disk; `--regen generated` re-syncs the corpus from the test
repositories. Each card carries its own badges — valid, structural, legible, miscited, and
whether this run could rebuild it — so the page names the diagram to open rather than
reporting a total. `render_example_gallery` draws without serving, which is what the tests
use.

Those two are **the only management commands in the repository**. This section previously
documented five more — `calibrate_readiness`, `benchmark_readiness_effort`, `run_evaluation`,
`run_generation_evaluation`, `calibrate_generation_evaluation` — plus a workflow-audit
browser service. None of them exists; all went with the provider pipeline.

## What the suite actually proves

Grouped by the claim each group defends, because a test that does not defend a claim is
maintenance with no reader.

| Area | The claim |
| --- | --- |
| `tests/drafts/` | A draft is accepted only if it is honest — ids resolve, evidence is cited by something, a `grounded` element has evidence, an `assumed` one has an assumption, and the notation permits what it says |
| `tests/materialization/` | Nothing a host authored is lost, and nothing it did not author is invented. Markers, ends, dashing, containment, `origin`, evidence digests, and the assumption bodies behind assumed elements all survive to disk |
| `tests/diagrams/` | The catalog, layout, rendering and legibility rules hold, and the SVG export draws what the canvas draws |
| `tests/mcp_server/` | The published tool surface is exact — a tool cannot reappear implicitly, and a retired one stays retired |
| `tests/api/` | The browser routes load, validate and save canonical JSON without a database |
| `tests/generation/` | Every committed example is a valid canonical diagram |
| Frontend Vitest | The canonical ↔ React Flow round-trip is byte-stable, display-only fields never leak into saved JSON, and an assumed element is marked on the canvas |
| Playwright | The editor loads, edits and saves a real diagram in Chromium |

Two properties are worth naming because they are easy to lose:

- **Round-trip stability.** Loading a diagram and saving it unchanged must produce the
  same bytes. A frontend adapter that reordered nodes broke this and produced diffs for
  edits nobody made.
- **Parity.** `frontend/src/editor/canvas/customNodes.tsx` and
  `backend/services/diagrams/rendering/diagram_render_service.py` draw the same notation.
  Two implementations of one rule is the defect class this repository keeps finding.

This section previously listed four epics and a Slice-14 backend audit gate covering
strict packets, provider handling, semantic repair and evaluation judges. That program
closed and its subject was removed; the history is in `docs/07-history/` and git.

## Relationship to slice outcomes

Every slice doc ends with an `## Outcome` section that records the exact verification run for that slice (commands and results). This testing doc is the durable description of the overall approach; the slice outcomes are the point-in-time evidence. When a slice changes how testing works, update this doc in the same task.

## Known gaps

- No CI pipeline yet; tests are run locally.
- No coverage-measurement tooling yet.
- The Playwright E2E suite is Chromium-only; a cross-browser matrix is optional.
- `diagram_validate` (MCP) is tested with inline diagram JSON; path-based validation is covered through the file-backed API/save flows.

## Related docs

- `docs/04-development/01-environment.md`
- `docs/05-delivery/01-current-state.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/03-design/03-validation/README.md`
- `docs/03-design/01-generation/README.md`
- `docs/04-development/04-reviewing-diagrams.md`

*(This list also carried the generation design, the evaluation/DOE design, and a
backend-audit release gate. All three went with the provider pipeline.)*
