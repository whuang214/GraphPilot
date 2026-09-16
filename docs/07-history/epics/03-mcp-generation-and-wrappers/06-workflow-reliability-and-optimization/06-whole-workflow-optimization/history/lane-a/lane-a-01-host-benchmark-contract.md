# Lane A Slice 01: Host Benchmark Contract

## Purpose

Create the smallest provider-free measurement boundary around a real human-initiated GitHub Copilot session so current and candidate host preparation can be compared without automating Copilot or calling Azure.

## Design

Reuse `graphpilot.evaluation.workflow-audit-external-evidence.v1` and `ExternalHostEvidenceAdapter` unchanged for normalized W01–W03 values that genuinely fit. Add narrow companion run-manifest, event, result, and deterministic Markdown-report contracts for host/model/repository/cache/request metadata, detailed counters, artifact references, validity, and compatibility.

A benchmark-only stdio proxy observes GraphPilot MCP startup/discovery/calls without persisting raw payloads. C/W allow only provider-free host preparation and stop after successful request save. One post-save benchmark summary records host-reported searches/read paths after the primary timer; source bytes are derived and labeled.

## Included Work

- Strict host-benchmark manifest/event/result contracts with new identities and bounded examples.
- Immutable run/terminal storage and no-rerun identity checks.
- Provider-free stdio timing for startup, discovery, calls, bytes, safe errors, and validation `{code,path}`.
- Artifact/token/size verification for JSON 1/JSON 2.
- Existing external-evidence adapter emission/import for supported normalized values.
- Post-save host summary with relative path/range validation and explicit evidence status.
- C/W provider guard and inherited-environment boundary that constructs no Azure client and reads no `.env`.
- Deterministic result/Markdown parity and compatible-pair rules.
- Fake/scripted host proof, interruption/failure/security tests, and proxy/direct equivalence.

The fake proof covers five exact provider-free scenarios:

1. cold preparation executes route -> missing status -> evidence save -> request save and stops before generation;
2. warm preparation executes route -> current status -> request save with zero source read and zero evidence save;
3. deterministic evidence/request failures retain safe `{code,path}` detail and a corrected candidate succeeds without hidden retry;
4. a provider-capable C/W call is blocked before child/provider dispatch and terminalizes invalid;
5. interrupted/completed identities refuse rerun, while proxied and direct successful tool results and canonical writes remain equivalent.

## Not In Scope

- Production workflow, JSON 1/JSON 2, prompt, generation, readiness, frontend, or provider behavior.
- Copilot automation, VS Code extension development, native search/read interception, persistent MCP, live provider calls, or generalized hosts/repos.
- Capturing the real C0/W0 observations; A02 owns execution.

## Target Areas

- New modules under `backend/services/workflow_audit/` for host benchmark contracts, storage, capture, and reporting.
- New strict schemas under `backend/assets/schemas/` and registry entries reserved for this slice's integration scope.
- A benchmark-only MCP proxy/entry point and operator command or equivalent bounded launch surface.
- Focused workflow-audit, management, and MCP tests.
- The canonical workflow-audit design owner and this Outcome.

## Exit Criteria

- Provider-free fake C/W runs produce schema-valid immutable manifests/events/results/reports and zero Azure construction/calls.
- Proxy/direct calls return byte/semantic-equivalent tool results and writes.
- A provider-capable C/W call is blocked before dispatch and terminalizes the run invalid.
- Search/read evidence is labeled host-reported; source bytes are derived; unavailable tokens/credits/cache remain null with reasons.
- Existing external-evidence schema/adapter is unchanged and validates emitted W01–W03 evidence.
- Raw source, prompts, secrets, absolute private paths, and provider payloads are rejected.
- Interrupted/completed identities cannot rerun.
- Independent implementation audit and required backend checks pass before commit.

## Previous Slice

Audited [`lane-a-00-group.md`](lane-a-00-group.md) plan commit.

## Next Slice

[`lane-a-02-devin-host-transition.md`](lane-a-02-devin-host-transition.md)

## Outcome

**Status:** Complete · provider-free capture boundary implemented, audited, and verified.

**Implementation:** Added strict host-benchmark manifest/event/result contracts, immutable canonical storage, prepare/arm/finalize lifecycle, deterministic Markdown reporting, unchanged external W01–W03 evidence adaptation, a no-dotenv/provider-blank MCP child, and a raw stdio proxy that preserves normal responses, injects only the post-save summary tool, and blocks provider-capable C/W tools before dispatch. Todo/Copilot execution remains human-initiated and A02-owned.

**Deviations and corrections:** The implementation uses three JSON authorities plus deterministic Markdown rather than a fourth report schema. Audit found and corrected a silent successful-artifact capture gap, separated artifact `capture_failure` from real `mcp_child_process_failed`, added workspace mismatch and concurrent-freeze coverage, and removed cell/treatment identities from the compatibility key so C0/C1 and W0/W1 can compare while model/repository/request controls still invalidate compatibility. Completed, invalid, and interrupted results all terminalize their identities.

**Verification:** Focused host-benchmark tests pass 22 tests, including real proxy/direct stdio equivalence, provider blocking, no-dotenv ordering, safe summary-byte derivation, strict examples/digests, interruption/no-rerun, external evidence, capture/child failure separation, and compatibility controls. The broader workflow-audit/schema/live-harness set passed 155 tests. The final backend suite passed 1,069 tests with 5 skipped; `uv run python mcp_server/smoke_test.py`, `uv run python manage.py check`, compileall, link/diff checks, and independent implementation re-audit pass. Zero Azure/Copilot calls were made.

**Follow-up:** A02 freezes new C0/W0 identities and prompts, then stops for the user's human Copilot sessions before any snapshot/interface candidate implementation.
