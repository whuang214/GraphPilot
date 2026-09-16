# Lane B B0: Windows Path Safety

## Purpose

Prevent another live-anchor identity from being frozen before GraphPilot knows that every package, run, observation, event, result, terminal, diagnostics, generated-output, and browser-evidence path is usable on the active Windows host. Add one reusable provider-free preflight that rejects unsafe identities and paths before the harness creates any runtime identity, while preserving strict terminal/no-rerun behavior after a path-safe identity is accepted.

## Background

The only authorized Block 6 semantic-review candidate froze its manifest and staged source before `events.jsonl` failed at an absolute Windows path length of 267 characters; the corresponding successful Block 5 path was 235 characters. Because the same long run and observation identities also made the strict result, observation, and terminal paths unusable, the attempt required a shorter package-level terminal and could not reach MCP, provider, quality, or browser proof.

The current live-anchor harness validates workspace containment and schema identity, but its schema ceilings still permit a 160-character run ID, a 192-character observation ID, and a 128-character diagnostics run ID. `LiveAnchorService.run()` currently freezes `manifest.json` before staging, event-ledger creation, and checkpointing. Path derivation is also distributed across `LiveAnchorArtifactStore`, `LiveAnchorService`, `WorkflowAuditMetricStore`, generation diagnostics, and browser evidence, so checking only `outputRoot` or only the first write would remain incomplete.

B0 is an evaluation-harness safety correction, not a generation endpoint change. It must preserve the accepted Block 5 short identities, reject the failed longer Block 6 shape before freeze, and remain independent of Lane B S05/S06 contract diagnosis/correction and all Lane A work.

## Design

### Reusable pre-freeze path plan

Add a frozen in-memory `LiveAnchorPathPlan` and one pure two-tier derivation/check API to `LiveAnchorArtifactStore`. The runtime tier accepts a validated manifest and always derives every control-workspace/evaluated-workspace path needed by `LiveAnchorService`; `freeze_manifest()` invokes this tier defensively before its first write. The command tier calls the same API before service construction and additionally supplies the exact package-manifest path and repository root so package/repository reads join the same plan. Optional command-edge paths extend—not replace or fork—the runtime entries. Repeated runtime checking is allowed, but every role is derived by this one function so formulas cannot drift. Derivation may resolve and inspect paths but must not call `mkdir`, open/create a file, freeze a manifest, claim diagnostics ownership, append an event, or start a process.

The plan has a stable role for every path and records its normalized absolute path, path kind (`file` or `directory`), and measured UTF-16 code-unit length. Absolute paths remain process-local and are never persisted or emitted in a safe error; rejection reports only the role, measured length, and active limit.

| Family | Paths that must be derived before freeze |
| --- | --- |
| Package | exact `--manifest` input and parent; repository-bound `anchor.path`, `approval.path`, sibling `approval.schema.json`, every source/evidence/request path, and every compatibility-asset path read by the command/service |
| Run | control run root, `manifest.json`, evaluated-workspace root, and `synthesis.json` |
| Observation | observation root, `checkpoint.json`, and `observation.json` |
| Event | exact `events.jsonl` path used by `WorkflowAuditMetricStore` |
| Result | exact strict `result.json` path |
| Terminal | exact strict `terminal.json` path |
| Diagnostics | collection root/README, request root, run root, owner marker, `00-run.json`, `08-result.json`, every numbered stage directory, and the longest concrete artifact filename reachable from the current live-anchor generation/debug call sites |
| Generated output | staged source destinations, canonical evidence/request paths, diagram JSON, SVG, compact trace, and the longest sibling temporary-write envelope used by generated output persistence |
| Browser | exact `browser-evidence.json` path and the generated diagram path consumed by the API/browser adapter |

Fixed paths must be derived exactly from the same manifest fields and roots used at runtime. B0 first inventories every diagnostics `write_stage`/provider/result call reachable from the live-anchor pipeline and derives the maximum current concrete stage-directory plus artifact-filename combination. The read-only diagnostics service remains authoritative for its syntax/bounds. If that inventory is not finite and complete without changing diagnostics ownership, implementation stops for integration redesign rather than reserving the general 128-character schema envelope, which would reject safe practical runs. Focused tests compare planned event, result, terminal, diagnostics, generated-output, and browser roles with paths actually used by a provider-free fake run; a future longer diagnostics call-site name must fail the parity/envelope test before live use.

### Active Windows-safe boundary

For ordinary, non-`\\?\` paths on Windows, enforce the current cross-process legacy-safe boundary: at most 259 UTF-16 code units for a file path (260 including the terminating NUL), at most 247 for a directory that GraphPilot may create, and at most 255 per component. Measure UTF-16 units rather than Python code points.

This is a code-owned evaluation safety policy selected when `os.name == "nt"`; it has no environment override. Do not infer safety from the registry's `LongPathsEnabled` value alone: the live path spans Python, stdio, Django, npm/Chromium, and existing storage normalization deliberately does not preserve an extended-path prefix. Non-Windows execution still performs identity/component validation, while focused tests inject the Windows policy so safe, exact-limit, and over-limit behavior runs provider-free on every development platform.

### Short identities and ordering

Before accepting a new live package, apply a B0-specific runtime precheck requiring every path-bearing identity to retain its existing syntax and contain no more than 64 ASCII characters:

- `anchor.packageId` and `anchor.anchorId`;
- `approval.approvalId`;
- `runId` and `observationId`;
- `generation.diagnosticsRunId`;
- `source.request.requestId`;
- `generation.expectedDiagramName`.

The 64-character component cap keeps the accepted Block 5 path-bearing identities valid while rejecting the failed candidate's 69-character run ID and 77-character observation ID; the separate exact package-manifest path check covers its longer package-directory component in the actual absolute context. It is intentionally stricter than the unchanged historical JSON-schema ceilings: B0 owns a live-execution safety precheck, not a persisted/public schema change. Historical manifests remain readable and immutable; a historical identity that exceeds the new live precheck is simply non-dispatchable. The cap is only a first bound; the complete absolute-path plan remains authoritative for a particular control/repository root, and a Block 5-shaped identity may still be rejected in a deeper root if diagnostics/generated envelopes do not fit. Never truncate, hash, rename, or silently substitute an approved identity. The operator must choose short wholly new identities before package approval/freeze and keep richer semantic labels in package/manifest evidence rather than path components.

Enforce this order at both reusable storage and command boundaries:

```text
read existing package manifest without mutation
-> validate manifest content/digest
-> derive the complete path plan
-> validate short identities + active Windows-safe limits
-> verify package/repository/approval/HEAD/provider prerequisites
-> freeze manifest and claim the runtime identity
-> stage, append events, checkpoint, dispatch, and terminalize
```

`LiveAnchorArtifactStore.freeze_manifest()` recomputes and validates the runtime tier before its first write even when a caller bypasses the management command; it does not require mutable hidden state or trust a caller-supplied plan. The command separately validates the extended command tier with exact input-package/repository paths, then `LiveAnchorService` defensively repeats the same runtime-tier function through `freeze_manifest()`. A failed preflight creates no `.graphpilot` run/workspace/observation/diagnostics/browser path, no checkpoint or terminal, and no provider-facing object. The already-authored input package remains read-only; correction requires a new short identity, not mutation or reuse of a failed identity.

### Path-safe terminalization

Once preflight passes and the manifest is frozen, all strict terminal artifact paths are known to fit. Extend the existing lifecycle so a provider-free failure during source staging, host-summary event persistence, or other pre-checkpoint local preparation writes the existing schema-valid `status/state: failed` `result.json`, `observation.json`, and `terminal.json` with zero calls, `providerStartState: not_started`, a non-retryable allowlisted safe error code, and a real completed timestamp, then reuses that terminal on resume without dispatch. Persist neither exception text nor private absolute paths. Tests bind result → observation → terminal digests through the existing artifact store rather than inventing a new terminal contract.

Do not create a package-level fallback terminal for a preflight rejection: no runtime identity was accepted. S03's package-level terminal remains a one-time historical recovery record because its identity had already frozen before B0 existed; B0 does not generalize that fallback. Future preflight rejection leaves only the unchanged input package, while a path-safe post-freeze local failure must use strict artifacts. If storage itself prevents strict terminalization after a path-safe freeze, fail closed, treat the frozen identity as non-rerunnable, and require filesystem audit rather than a second attempt.

### Rollback

B0 has no schema, registry, public interface, migration, or live-evidence write. Before implementation, the integration owner verifies every owned production/test file is unchanged from base `4bd7ba4`; the only pre-implementation delta is this committed plan. Implementation lands as one later B0 commit, so rollback is `git revert <B0-implementation-commit>` on the B0 branch (or omission of that commit during later integration), followed by focused tests proving baseline behavior. No other call site may import a new B0 API outside the declared owned files. Leave all historical Block 5/6 artifacts untouched and keep S07 blocked on path safety. Never delete or rewrite a manifest, terminal, authorization package, or prior candidate as rollback.

## Execution Contract

- **Depends on / inputs:** base `4bd7ba4`; the accepted Block 5 live-anchor harness and provider-free fake seams; the immutable 267-versus-235-character failure evidence; the S07 pre-freeze requirement.
- **Outputs:** reusable pure path plan/checks, short-identity enforcement, pre-freeze command/storage guards, provider-free pre-checkpoint terminalization, focused regressions, and this B0 Outcome.
- **Exclusive write ownership:** only the exact production/test files listed in Target Areas and this document's Outcome.
- **Forbidden/shared ownership:** `backend/services/shared/schema_identities.py`; all `backend/assets/schemas/**`; `backend/services/shared/schema_registry.py`; any GraphPilot schema/registry or MCP tool/prompt/registration file; every Lane A code/test/doc/evidence file; current-state, decision, top-group, navigation/README, Captain, ledger, backlog, authorization, prior evidence, `.env`, and provider-owned files/resources.
- **Parallelism/resources:** provider-free B0 may run in its dedicated worktree in parallel with read/evidence-only S05 because ownership does not overlap. It uses only unique temporary control/repository roots and injected fake executor/browser seams; no shared ports, browser profile, Azure client, provider setting, or live identity.
- **Integration gate:** merge B0 before any S07 package is approved or frozen. S05/S06 do not consume B0 and must not edit B0-owned files; S07 consumes the committed preflight and must still obtain separate live authorization.
- **Cancellation:** any need for schema/public-contract changes, environment configuration, extended-path opt-in, automatic identity rewriting, provider access, prior-evidence mutation, or weakening terminal/no-rerun behavior stops for redesign rather than expanding this slice.

## Included Work

- Add the pure, copy-isolated path-plan API and a typed safe rejection under the live-anchor artifact-store owner.
- Derive all package/runtime/evaluated/diagnostics/browser paths and bounded dynamic envelopes named in Design from validated manifest inputs.
- Enforce the Windows-safe UTF-16 file/directory/component limits and 64-character path-bearing identity cap before any identity write.
- Make the management command run package/repository path preflight before provider prerequisite checks and before constructing `LiveAnchorService`.
- Make `freeze_manifest()` a defensive final no-write-before-pass boundary for direct service/store callers.
- Route runtime event-ledger/result/terminal/browser checks through or compare them against the same plan so duplicate path formulas cannot drift silently.
- Add strict zero-call pre-checkpoint failure terminalization after a successful path preflight and prove terminal resume does not dispatch.
- Add provider-free regressions for:
  - accepted Block 5-shaped and selected short identities;
  - exact-limit pass and one-unit-over-limit rejection using UTF-16 measurement;
  - overlong identity and deep control/package root rejection before `.graphpilot` creation;
  - complete planned-role coverage, including worst-case diagnostics and browser/generated-output paths;
  - safe fake generated execution plus injected browser proof at the planned paths;
  - host-event/staging failure strict terminalization and terminal reuse;
  - command gate ordering, zero Azure construction/calls, safe errors, and unchanged input packages.
- Produce B0-only self-digested `path-proof.json` plus a readable proof and independent audit record under `evidence/windows-path-safety/`; record identities/lengths/roles and test outcomes only, never absolute paths or secrets.
- Run the focused service/command tests, then the full offline backend suite and `git diff --check`; audit the diff against the exact ownership/forbidden list.

## Not In Scope

- Generation endpoint diagnosis/correction/proof, semantic-review behavior, prompts, projections, validators, quality policy, provider roles, or performance measurement.
- `generation_contracts.py`, generation diagnostics contract/schema redesign, any JSON schema or `SchemaRegistry` edit, or any MCP/public API/registration change.
- Enabling Windows long paths, adding `\\?\` prefixes, changing registry/group policy, shortening the user's repository/control root automatically, or adding an environment/configuration override.
- Lane A host benchmark/snapshot/interface code, tests, plans, evidence, identities, or resources.
- Any live call, provider client construction, `.env` read/write, authorization/package creation, S07 execution, browser subprocess, promotion, certification, deployment, S15, or Stage C.
- Editing current-state, active decisions, either Block 6 `00-group.md`, navigation/README files, Captain reports, optimization ledgers/backlogs, authorization, or historical/current evidence.

## Target Areas

### Proposed exclusive implementation ownership

| File | Planned change |
| --- | --- |
| `backend/services/workflow_audit/live_anchor_artifact_store.py` | own `LiveAnchorPathPlan`, UTF-16/Windows-safe checks, short identity validation, complete path derivation, safe typed rejection, and defensive pre-freeze guard |
| `backend/services/workflow_audit/live_anchor_service.py` | invoke the no-write preflight before freeze, keep runtime paths aligned with the plan, and strictly terminalize path-safe pre-checkpoint failures |
| `backend/operations/management/commands/run_live_workflow_anchor.py` | pass exact package/repository roots into preflight and preserve local-gates-before-service/provider ordering |
| `backend/tests/evaluation/workflow_audit/test_live_anchor_service.py` | provider-free safe/boundary/over-limit/no-write/path-parity/terminalization/browser regressions |
| `backend/tests/management/test_live_workflow_anchor_command.py` | package-path and command-order/no-provider/no-service-construction regressions |
| `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/06-whole-workflow-optimization/b0-windows-path-safety.md` | future implementation Outcome only |
| `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/06-whole-workflow-optimization/evidence/windows-path-safety/path-proof.{json,md}` | B0-only self-digested provider-free proof |
| `docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/06-whole-workflow-optimization/evidence/windows-path-safety/audit.md` | independent B0 implementation audit record |

`backend/services/workflow_audit/capture_service.py`, `live_anchor_browser_service.py`, and `backend/services/generation/diagnostics/generation_diagnostics_service.py` are read-only behavioral anchors for derivation/parity tests, not B0 write ownership. No other file is recommended or permitted for this slice.

## Exit Criteria

- One pure preflight deterministically derives every required path/envelope and reports the active Windows-safe policy without filesystem mutation or private-path persistence.
- Accepted Block 5 identities pass the 64-character compatibility bound; the failed Block 6 long run/observation/package shape fails before freeze.
- On Windows, every selected package/run/observation/event/result/terminal/diagnostics/generated/browser file is at most 259 UTF-16 units, every creatable directory at most 247, and every component at most 255.
- Safe and exact-limit provider-free cases pass; one-unit-over-limit, deep-root, and long-identity cases fail with a safe typed error and leave no runtime identity or `.graphpilot` tree.
- A path-safe pre-checkpoint local failure produces immutable strict failed result/observation/terminal artifacts with zero calls and `not_started`, and resume returns that terminal without executor/provider dispatch.
- A provider-free fake generated run and injected browser proof use paths equal to the preflight plan, including diagnostics coverage.
- No test constructs Azure, reads `.env`, starts browser/provider processes, or touches non-temporary live identities.
- Focused live-anchor service/command tests, the full backend suite, diff check, and implementation audit pass with no unresolved critical/high/medium finding.
- The final diff is limited exactly to the five code/test files, this Outcome, and three B0-specific evidence files in proposed exclusive ownership; rollback remains a clean code revert with no artifact migration or prior-evidence mutation.

## Previous Slice

[`04-wave-decision.md`](04-wave-decision.md) established the failed candidate's Windows path root cause and the mandatory pre-freeze prerequisite.

## Next Slice

Provider-free [`05-generation-endpoint-diagnosis.md`](05-generation-endpoint-diagnosis.md) may proceed independently in its disjoint worktree. B0's first hard consumer is [`07-generation-endpoint-proof.md`](07-generation-endpoint-proof.md), which remains blocked on S06, this path-safety gate, and separate explicit live authorization.

## Outcome

**Completion.** Implemented the pure frozen runtime/command path plan, stable role inventory, UTF-16 Windows legacy-safe policy with injected test seam, component checks on every host, and the code-only 64-ASCII-character live identity cap. The command now checks the exact package path before its first read, then extends preflight with package/repository reads before HEAD, approval, provider, or service gates; the service and `freeze_manifest()` independently repeat the no-write runtime preflight. The finite diagnostics envelope is bound to the longest current concrete semantic-review response-repair artifact, and focused natural-repair coverage will expose a longer future call-site name.

**Lifecycle.** Path-safe source-staging, host-summary, host-event, and checkpoint-persistence failures now close through the existing failed result/observation/terminal schemas with zero calls, `not_started`, a completed timestamp, and allowlisted non-retryable codes. Resume reuses strict terminal state without dispatch; partial strict state or an otherwise unclaimed existing frozen manifest is fail-closed and non-rerunnable. Exception text and absolute paths are not persisted.

**Verification.** Test-first focused discovery failed before implementation with two expected missing-symbol import errors; the final focused service/command gate passed 40 tests in 51.693 seconds after resolving the audit's pre-read package-path finding, the self-digest/safe-proof check passed, the full backend passed 1,060 tests with 5 skipped, independent implementation audit passed after one package-path-before-read correction with zero material findings, and `git diff --check` passed. The provider-free [`path-proof.json`](../../lane-b/evidence/windows-path-safety/path-proof.json) and [`path-proof.md`](../../lane-b/evidence/windows-path-safety/path-proof.md) retain safe identity lengths, role counts, boundary outcomes, lifecycle evidence, commands, and limitations without absolute paths or secrets.

**Deviations / follow-up.** Per the execution instruction, the independent audit record remains B0-specific and this branch is returned without shared integration edits. No schema, registry, MCP, generation contract, Lane A, shared status/navigation, environment, provider, live-package, prior-evidence, promotion, or certification file/resource changed or ran.
