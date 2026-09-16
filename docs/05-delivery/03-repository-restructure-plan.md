# Repository Restructure Plan

Stop Block 6 cleanly, restructure the repository, take fresh numbers, and restart
Block 6 small. Seven phases. Delete this file when Phase 7 opens.

## The idea in one paragraph

Block 6 worked but grew a documentation apparatus six times the size of the code it
changed, and its final measurement showed the optimization target was wrong anyway —
local compute is 92% of the wall, not provider round-trips. So: stop where we are,
keep the code that works, reorganize both `docs/` and `backend/` while nothing is in
flight, throw away every measurement bound to the old layout, and start the next
block against the real target with a rule that keeps the paperwork proportional.

## What we keep and what goes

**Keep — working code, already proven:**

| Commit | What |
| --- | --- |
| `a17bc40` | Generation endpoint fix — removed a 26 s repair call |
| `4f02b0a` | Windows path safety preflight |
| A03 / A04 | Backend-derived evidence values, allowed-property reporting |
| `8733022` | Test suite 12 min → 3.9 min (`perf-test-speedup`, unmerged) |

**Keep — sealed history, 372 KB, 19 Azure calls, cannot be regenerated:**

```text
.graphpilot/evaluation/live-workflow-anchor/runs/
  run-live-workflow-anchor-block5-cold-room-20260728-03    5 calls
  run-live-workflow-anchor-g                               3 calls, proves a17bc40
  run-live-workflow-anchor-s                               5 calls, terminal failure
```

**Delete — 6.8 MB of provider-free baselines.** Free to regenerate, and every one
records file paths the restructure is about to move.

## How you know a step was safe

No old baseline is kept. Performance numbers from the current structure describe
paths that are about to move, and they are re-ranked against the new baseline
anyway. If they are ever wanted, they are reproducible: check out the Phase 1 tag
and run the provider-free baseline again — it costs nothing.

What each restructure step must satisfy, checkable on the spot with no "before"
snapshot:

```text
backend tests      1111 passing
schema count       79
git diff           renames only, no content changes
```

The suite is the real guard. `git diff --stat` showing pure renames is the cheap
second one — a move that edits a file is a move that did more than move.

## Guardrails

- **Move, never delete** during restructuring. Deletion is Phase 3 only, and only
  for regenerable baselines.
- **`06-whole-workflow-optimization/authorization/` does not move.** Five frozen
  manifests bind its exact paths and digests.
- **No provider calls.** The entire restructure is provider-free.
- **No behavior, contract, schema `$id`, or public tool-name changes.**
- `git mv` so history follows the file.

---

## Phase 1 · Stop cleanly

**What:** Put everything in flight to bed so nothing is being written while files
move.

Commit the A05 planning document marked deferred. Confirm Lane B's `B1` produced no
work — `lane-b-post-integration` is at the same commit as `master`, so nothing is
lost. Merge `perf-test-speedup`. Prune the three superseded worktrees `GP-B0`,
`GP-LB`, `GP-S05`, whose commits already live in master's history. Tag the result.

**Why:** Restructuring while two lanes write documents is a merge conflict on every
file. And you will run the test suite dozens of times across the later phases — do
it at 3.9 minutes, not 12.

**Done when:** `git status` is clean, one worktree remains, and the tag exists.

## Phase 2 · Clear the old evidence

**What:** Archive the three live-anchor runs as sealed history. Delete the seven
provider-free baseline runs and the readiness-diagnosis runs.

**Why:** The paid evidence is 5% of the volume and all of the irreplaceable value —
it is the surviving proof that `a17bc40` works and that the semantic retry failed.
The provider-free runs are 6.8 MB of soon-to-be-wrong path records.

**Done when:** `.graphpilot/evaluation/` contains only the sealed archive.

## Phase 3 · Retire dead apparatus

**What:** Delete measurement machinery whose program is over — schemas, services,
tests, and management commands together. Candidates, each requiring its own proof:

```text
host-benchmark-*        3 schemas + service + artifact store + tests
                        benchmarks GitHub Copilot, a host retired in Lane A A02
full-effort-*           5 schemas incl. a 73 KB manifest, already named "historical"
readiness-diagnosis-*   4 schemas, Block 3, complete
evaluation-*           18 schemas, the DOE/judge epic
```

**Liveness proof required per item, no exceptions:**

1. nothing in `services/`, `api/`, or `mcp_server/` imports it;
2. no schema registry entry, scenario, or fixture references it;
3. the product test suite passes with it removed.

Fail any one and it stays. Retire in one commit per rig so a mistake reverts cleanly.

**Why:** `services/evaluation/` is 25,109 lines against 23,056 lines of product, and
44 of 79 schemas are measurement rather than product. The apparatus outgrew the
thing it measures. This phase runs before the restructure so nothing dead gets
carefully migrated first.

**Done when:** every retired rig has a recorded proof, the product suite passes, and
the remaining apparatus each names a program that is still open.

## Phase 4 · Restructure the docs

**What:** Classify all 343 documents as active, history, or dead. Then reshape:

```text
docs/
  README.md          front door, two clicks to anything active
  product/           what and why
  architecture/      how it is built, including a runtime data-flow map
  design/            per-feature contracts and decisions
  delivery/          in-flight work only
  history/           everything completed, frozen
  research/          one summary per promoted research package
```

Collapse each completed block to one summary, with its slice documents retained
beneath `history/` rather than rewritten. Fold `archive/` into `history/`.

**Why:** Today 241 of 343 documents describe how the project was built and only ~42
describe the system. The active set should be small enough to trust and verify.

**Done when:** `docs/` has at most seven top-level entries, the active set is under
50 files, no completed-work document is within two clicks of `README.md`, and a
link scan is clean.

## Phase 5 · Restructure the backend

**What:** Domain-first migration. Today `core/`, `support/`, and `contracts/` are
grab-bags: `core/` mixes context validation, diagram persistence, and rendering;
`contracts/` holds every domain's contract in one folder. Contracts move to live
with the domain they describe.

Current → target:

`contracts/` is the worst of the grab-bags because one word covers three unrelated
things: domain vocabulary (enums and frozen result types), a version/identity
registry that is really a manifest, and HTTP transport DTOs. Split by what each file
actually is:

```text
services/
  support/        ->  shared/       canonical_json, schema_registry,
                                    workspace_storage_service, diagram_type_service
  contracts/operation_problem.py    -> shared/
  contracts/generation_contracts.py -> shared/schema_identities.py
                                       (SCHEMA_IDENTITIES, PROMPT_VERSIONS,
                                        LAYOUT/TRAINING/RUBRIC versions — a manifest,
                                        not a contract; belongs beside schema_registry)
  contracts/diagram_contract.py     -> api/    (HTTP load/save DTOs, not a service type)

  catalog/        ->  diagrams/catalog/      constants, diagram_shapes,
                                             diagram_types, element_catalog
  core/diagram_validation_service.py,
  core/structural_constraints.py,
  contracts/validation_contract.py
                  ->  diagrams/validation/
  core/diagram_persistence_service.py     -> diagrams/persistence/
  core/diagram_render_service.py          -> diagrams/rendering/

  core/context_document_validator.py,
  core/context_persistence_service.py,
  core/diagram_request_persistence_service.py,
  core/diagram_request_validator.py,
  contracts/context_*.py,
  contracts/diagram_request_contract.py   -> context/

  readiness/      ->  readiness/    unchanged + contracts/readiness_contract.py

  generation/     ->  generation/requests/     context_resolver, packet_builder,
                                               training_fixture_service
                      generation/pipeline/     diagram_generation_service,
                                               pre_layout_generation_service,
                                               generation_pipeline, layout_service
                      generation/review/       semantic_review_service,
                                               semantic_review_rubric,
                                               context_provenance_validator
                      generation/diagnostics/  diagnostics_service, observer,
                                               workflow_renderer

  evaluation/     ->  evaluation/   keep workflow_audit/ and historical/full_effort/
  llm/            ->  llm/          unchanged
```

Outside `services/`:

- **`backend/operations/`** — a new installed Django app holding every management
  command. Django only discovers `management/commands/` inside an installed app.
- **`backend/assets/`** — runtime assets currently under `graphpilot/`: 79 schemas,
  18 prompts, 137 blueprint files. Every registry, service, scenario, and test path
  that references them must be updated in the same step.
- **`mcp_server/tools/`** — `server.py` split into per-tool modules.
- **`tests/`** — mirrors the final `services/` tree.

Six steps, one commit each: shared → diagrams → context → readiness+generation →
evaluation → adapters/assets/tests. A failure then points at one step rather than a
400-file diff.

### Logic stays untouched here

Splitting `contracts/` by what each file *is* removes the naming confusion, but it is
still a move: no behavior, no consolidation, no deletion.

The real logic questions — whether the 79 JSON schemas and the Python domain types
overlap, whether the version registries should be data rather than code, whether
`readiness_calibration_service.py` is doing several jobs — are deliberately deferred.
They are currently unanswerable: `core/` holds three domains at once, so nobody can
see what a domain actually contains. Fix the placement first, then the duplication
becomes visible or disproves itself. That is a separate program with its own
evidence.

**Move only.** Five modules are oversized — `readiness_calibration_service.py` at
2,601 lines, `diagram_generation_service.py` at 1,455, `diagram_render_service.py`
at 1,415, `generation_diagnostics_service.py` at 1,173, `semantic_review_rubric.py`
at 1,139. Splitting them is a separate later program with its own before/after
proof. Do not split during this phase.

**Why:** This is the risky phase, which is why it comes after the docs are legible.
Doing it now — rather than after Block 6 restarts — means `B1` and `A05` land in the
final tree instead of being moved later.

**Done when:** every step passes the suite with a rename-only diff, and no stale
import, asset path, or registry reference remains.

## Phase 6 · Take fresh numbers

**What:** Run a provider-free baseline on the finished structure. This becomes the
only baseline in the repository.

**Why:** Every measurement now describes the repository as it actually is. No
inherited numbers, no stale paths, nothing to reconcile against a dead layout.

**Done when:** one baseline exists, and its accounting is the sole reference for
ranking future work.

## Phase 7 · Restart Block 6, small

**What:** Open one package against the corrected target. B1's local cost attribution
(`lane-b/work/01-local-cost-attribution.md`, commit `512ad01`) established three cost
tiers and only two are real product cost:

```text
process init      ~1,300 ms   paid ONCE per server start   (harness pays it 12×)
service construct   ~220 ms   paid EVERY request           ← largest per-request cost
example_loading     119.4 ms  paid EVERY request           reducible to 41.6 ms
```

The 920.2 ms `example_loading` figure in the integrated baseline is cold-start
initialisation, not per-request work — the same call costs 76.3 ms warm. Every
Lane B rank is measured in that inflated denominator, so **the backlog must be
re-ranked on a per-request column before any package opens.**

Note that `perf-test-speedup` (merged in Phase 1) already removed ~50 ms of the
per-request service construction cost, so tier 2 must be re-measured rather than
assumed.

**Why:** The old Block 6 was framed around provider round-trips, then re-framed
around local compute, and B1 showed most of that local compute is harness cold-start.
Getting the denominator right is the package — optimisation follows from it.

**Done when:** the package is complete and produced fewer than 20 documents. If it
produced 96 again, the structure was never the problem.

---

## Effort

Agent-executed, largely unattended. The work is not the moving — it is the number of
verification cycles, and each cycle is a full test-suite run.

```text
Phase 1  stop cleanly            ~20 min
Phase 2  clear old evidence      ~10 min
Phase 3  retire dead apparatus   1-2 hours  ← the phase that actually shrinks it
Phase 4  restructure docs        1-2 hours  classification is the slow part
Phase 5  restructure backend     2-4 hours  ~6 gated steps    ← the risky one
Phase 6  fresh numbers           ~10 min
Phase 7  restart Block 6         separate
                                 ≈ one day
```

Suite time governs the total. Merging `perf-test-speedup` in Phase 1 takes the suite
from 12 minutes to 3.9, which across roughly a dozen gated runs is the difference
between half a day and two.

Speed does not change the risk profile. Phase 5 still commits one step at a time — a
fast agent that batches six moves into one commit gives you no way to tell which move
broke the suite.

## What is deliberately not here

- Epic 4 (`diagram_update`) — **not in MVP**. The current-state board still calls it
  the main remaining MVP gap; correct that in Phase 4.
- Frontend restructuring.
- Any live provider work. That needs its own authorization after Phase 7 opens.
- Block 7 representative validation — the real ship gate, and the right next thing
  after Block 6 closes.

## Outcome

Phases 1–6 complete. Phase 7 is open next; delete this file when it does.

| Phase | Result |
| --- | --- |
| 1 · stop cleanly | perf merged, tagged |
| 2 · clear old evidence | 6.8 MB of provider-free baselines removed; 19 paid calls sealed |
| 3 · retire dead apparatus | 4 rigs gone — schemas 79 → 50, tests 1111 → 928 |
| 4 · restructure docs | 345 files → 51 active, lifetime-separated |
| 5 · restructure backend | `core/` `contracts/` `catalog/` `support/` `evaluation/` dissolved into 7 domains; `assets/` and `operations/` split out |
| 5b · test refactor (added) | inner loop 116 s → 69 s; large `TestCase` classes split for parallelism |
| 6 · fresh numbers | `run-workflow-audit-post-restructure`, key `sha256:d77f21f8…29ebd1` |

**Deviations.** Phase 5b was not in the plan; it came from a separate request and is
recorded here because it changed the verify commands. The plan's step check
(`1111 tests / 79 schemas / renames only`) was written before Phase 3 deleted the
apparatus, so the real gate was 928 → 933 tests and 50 schemas, with renames-only diffs
per commit.

**What the gates caught during Phase 5**, all in move-only commits: two import forms a
dotted-path substitution misses (`from services.x import y`), `parents[N]` depth in
*production* code (the spawned MCP child could not import `mcp_server`), a substitution
that also rewrote the runtime `.graphpilot/evaluation/` path, multi-line path
constructions invisible to line-based replacement, and a latent Phase 4 break in a test
fixture that had gone unnoticed for four commits. `parents[N]` is the single most
fragile construct in a move-based refactor and is worth replacing with a `BASE_DIR`
helper.

**Not done, deferred to [`02-backlog.md`](02-backlog.md):** the live-anchor/workflow-audit
rig consolidation, the `benchmark_readiness_effort` decision, `mcp_server/server.py`
decomposition, and the five oversized modules — all splits rather than moves, so all
outside this plan's move-only rule.
