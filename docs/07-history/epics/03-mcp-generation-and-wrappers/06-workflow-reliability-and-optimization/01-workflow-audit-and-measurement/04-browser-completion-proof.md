# Slice 04: Browser Completion Proof

## Purpose

Measure and verify the W22 user-visible completion boundary against one exact generated observation using the built frontend,
Django API, and a real Chromium browser.

## Design

Add a dedicated Playwright audit configuration that builds the frontend, serves `npm run preview` on the existing isolated
frontend port `15173`, and starts Django with `--noreload` on backend port `18080`. A focused spec accepts exact run,
observation, diagram-path, expected identity/counts, and bounded output path through validated environment values.

The evidence clock covers navigation to visible diagram completion and records API load timing/status, final URL/path identity,
expected node/edge identity/counts, console errors, page errors, failed responses, and browser/runtime identity. Browser evidence
is written as a bounded contract artifact and merged only when run/observation/diagram digests match.

## Execution Contract

- **Depends on / inputs:** committed S03 generated representative observation, diagram path/digest, expected node/edge
  identities, and browser-evidence schema.
- **Outputs:** exact built-preview W22 evidence consumed by S05 reports/command and S06 baseline eligibility.
- **Exclusive write ownership:** dedicated Playwright audit config/spec, browser adapter/tests, and audit-only package script.
- **Forbidden/shared ownership:** runner/report/ledger behavior and shared status/docs are forbidden; production editor/API code
  remains unchanged unless a separately evidenced defect blocks the proof.
- **Parallelism/resources:** no parallel write slice because its proof needs S03 artifacts and S05 needs its committed evidence;
  reserve ports `15173`/`18080`, unique Playwright session/profile names, temporary roots, and browser-evidence path.
- **Merge/integration gate:** W22 run/observation/diagram binding, visible identity, API/network/console, cleanup, and full frontend
  gate must pass before S05.

## Included Work

- Add the dedicated built-preview Playwright audit configuration and focused spec.
- Add a script/adapter that invokes the proof with exact validated inputs and bounded output.
- Measure one representative generated anchor cold and warm without modifying the diagram.
- Validate and merge browser evidence into the exact immutable run observation/package.
- Fail closed on path/digest/identity/count mismatch, console/page/network failure, malformed output, wrong ports, or stale run.
- Keep diagnostic no-browser runs explicit; such runs retain W22 `not_measured` and are baseline-ineligible.
- Add focused successful, malformed, mismatch, failure, and baseline-eligibility tests.

## Not In Scope

- General frontend performance optimization, browser profiling, UI behavior changes, or dev-server timing claims.
- Browser coverage for every scenario; one exact representative anchor proves the shared editor boundary.
- Report ranking, ledger mutation, or provider-backed execution.

## Target Areas

- `frontend/playwright.audit.config.ts`
- `frontend/audit/workflow-audit.spec.ts`
- `frontend/package.json`
- workflow-audit browser adapter/service and focused tests
- testing/backend/frontend documentation owners where the command surface changes

## Exit Criteria

- The built frontend and Django start only on isolated audit ports and do not reuse development servers.
- The exact representative diagram reaches visible completion cold and warm with expected identity/counts.
- API status/timing and navigation-to-visible duration are finite, nonnegative, and bound to the observation.
- Console/page/failed-network collections are empty on success and cause typed proof failure when populated.
- Browser evidence is bounded, schema-valid, digest-bound, path-safe, and cannot be merged into another run/observation.
- A missing/failed browser proof prevents baseline eligibility while remaining truthful in diagnostic reports.
- Focused browser tests and `cd frontend; npm run verify` pass, with no Playwright session/server left running.

## Previous Slice

[`03-audit-runner-and-recovery.md`](03-audit-runner-and-recovery.md)

## Next Slice

[`05-reports-and-baseline-ledger.md`](05-reports-and-baseline-ledger.md)

## Outcome

**Status:** Complete. Slice 04 added an input-bound Playwright configuration/spec that builds and serves Vite preview, starts
Django on isolated ports `15173`/`18080`, blocks external requests, and measures exact cold-then-warm editor completion in one
browser context. `WorkflowAuditBrowserService` binds the single browser representative to immutable S03 observations and
canonical diagram artifacts, invokes npm without a shell or provider configuration, validates canonical schema/digest/private-
content constraints, and reuses only exact existing evidence without rerunning the browser.

**Evidence:** Final proof run `run-workflow-audit-s04-browser-proof-02` under
`.graphpilot/evaluation/workflow-audit/runs/` used two generated Activity observations and six fake/zero Azure calls. Cold W22
was 234 ms with a 94 ms API load and digest
`sha256:9946fe50b5c2c616e20f93730ac899b65d3537b4166ca46e519db5e164f87b84`; warm W22 was 182 ms with a
112 ms API load and digest `sha256:ecbb9c000e762eaccd272b88c4fd664dd880aaded6c459483c3c1f672d5ade22`.
Both showed the exact 8-node/7-edge identity with empty console/page/failed-response evidence. No server, port listener, or
browser session remained afterward.

**Audit and corrections:** Initial partial implementation lacked one link helper and incorrectly assumed cold/warm outputs
shared a path/digest; focused tests exposed both before proof. The final contract correctly requires distinct cold/warm diagrams
with identical semantic structure. Audit timing/race concerns were reviewed against actual order; completion precedes the late-
error drain, and active event ownership is cleared between observations. POSIX/Windows private paths, traversal, unexpected
outputs, subprocess failure, mismatch, and exact-reuse regressions were added. Independent re-audit passed with no critical,
high, or medium finding.

**Verification:** Six focused backend browser-service tests, backend Django check/compile, frontend lint/build, the complete
backend suite (971 tests, 5 skipped), and `npm run verify` (419 unit/component and 43 normal E2E tests) passed. The separate
fresh built-preview proof above passed with zero external/provider calls and `git diff --check` passed.

**Follow-up:** Slice 05 consumes these separate immutable browser-evidence artifacts with S03 observations to produce reports,
ranked findings, compatibility ledger entries, and the independent command.
