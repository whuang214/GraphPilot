# Windows Path Safety Proof

- Machine evidence: [`path-proof.json`](path-proof.json)
- JSON self-digest: `sha256:dd504dfda9448c0600b7f5327f1042cb72078aa824aafaac01ad5a8f8d0e35be`
- Base source: `cd3b57e2427969e7ad0df41916391a69e7cee667`
- Status: **pass**
- Provider calls / provider objects / browser processes: **0 / 0 / 0**
- Absolute paths or secret values persisted: **none**

## Implemented Boundary

The preflight now builds one frozen runtime plan and an extending command plan before any live-anchor identity write. The plans carry stable roles, file/directory kinds, normalized process-local paths, and UTF-16 lengths. The command tier adds the exact package manifest, package parent, repository source and approval files, approval schema, and compatibility assets. Absolute values remain in memory and safe rejection text reports only role, measured length, and limit. The command checks the exact package path before its first read, preventing an operating-system path error from disclosing it.

On Windows the code-owned policy allows at most 259 UTF-16 units for files, 247 for creatable directories, and 255 per component. Other hosts retain the component check. The focused suite injects the Windows policy and proves exact-limit acceptance, one-unit-over rejection, astral-character UTF-16 measurement, no-write rejection, and path-free errors. There is no environment override or extended-path opt-in.

## Identity Evidence

All eight selected Block 5-shaped path-bearing identity lengths are at most 64 ASCII characters (maximum 61). The failed Block 6 shape includes lengths 73, 69, and 77, so it is rejected before freeze. Dedicated boundary coverage accepts 64 and rejects 65 without persisting the rejected identity.

## Complete Runtime Envelope

The representative manifest produces 42 runtime roles (22 files and 20 directories); the command tier extends this to 53 roles. Coverage includes strict manifest/event/result/observation/terminal paths, staged source and canonical context paths, generated JSON/SVG/trace and sibling temporary-write envelopes, all seven diagnostics stage directories, diagnostics ownership/envelope/result files, and browser evidence.

The finite diagnostics maximum is the current concrete semantic-review response-repair artifact at 81 filename UTF-16 units. Provider-free natural repair scenarios prove every produced diagnostics artifact fits that planned envelope and that the expected maximum is reached. A longer future call-site filename will fail this parity check.

## Strict Local Failure Closure

After path-safe freeze, injected staging and host-event persistence failures produce the existing schema-valid failed result, observation, and terminal with zero calls, `providerStartState: not_started`, non-retryable allowlisted codes, and completed timestamps. Resume reuses the terminal without dispatch. Exception text is not persisted. A frozen identity with incomplete strict state is fail-closed and non-rerunnable.

## Verification

- Failing before implementation: focused discovery failed as expected with 2 import errors for the not-yet-implemented B0 symbols.
- Passing after implementation and audit correction: **40 tests in 51.693s**, provider-free.
- Full backend: **1,060 tests passed, 5 skipped, in 531.862s**.
- Independent implementation audit: pass after correcting the package-path-before-read ordering; 0 critical/high/medium remain.
- `git diff --check`: pass.

No live package, provider call, browser subprocess, promotion, or certification run was performed.
