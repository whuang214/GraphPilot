# Block 6 Integration and Documentation Plan

## Goal

Merge the paused Lane B checkpoint into the clean Lane A/master checkpoint, verify the combined runtime provider-free, reorganize Block 6 into one root plan plus separate Lane A/Lane B workspaces, and leave master ready to split into new lane worktrees.

## Inputs

| Input | Branch | Commit | State |
| --- | --- | --- | --- |
| Lane A | `master` | `09394613403ca762c5ad8c60a4d29028c0a27955` | clean; A04 complete and paused |
| Lane B | `lane-b-optimization` | `1e4600fcc01722dd800c0e2569b0b32466f35e1e` | clean; exit handoff complete |
| Common base | — | `4bd7ba4dcb278a251fe0bb87e4112ce39f42cdf9` | audited two-lane checkpoint |

Master is the local integration branch by user decision. Do not push, rewrite history, delete old branches/worktrees, or make provider calls.

## Bound Lane B Terms

These commits/files are verified inputs from `lane-b-optimization` at `1e4600f`; they are not expected on pre-merge master.

- **B0** — Windows live-path preflight, document `b0-windows-path-safety.md`, retained commit `4f02b0a866c3eb7a08efe64d7f983952b85d6ab4`.
- **g2** — retained generation candidate `run-live-workflow-anchor-g` and its package/run/workspace/browser/synthesis/guard evidence.
- **s1** — failed non-retryable semantic candidate `run-live-workflow-anchor-s` and its package/run/workspace/guard evidence.
- **Semantic baseline** — behavior at `5ec80b7ed4cd5eb24fbced0532079cb737ad58c4`; correction `b5ef42258cb9459db5d508e7e665a31712196b7e` remains reverted by `a6e7ad0779e36c636efb17394d8161d5ea3f338e`.
- **Artifact authority** — Lane B `evidence/lane-b-exit/exit-handoff.json` at `1e4600f`, including exact immutable paths, digests, accounting, and rollback map.

## Final Structure

```text
06-whole-workflow-optimization/
  README.md
  plan.md

  lane-a/
    README.md
    plan.md
    work/
    evidence/

  lane-b/
    README.md
    plan.md
    work/
    evidence/

  history/
    README.md
    lane-a/
    lane-b/
    shared/

  evidence/
    README.md        # combined integration/rebaseline only

  authorization/
    README.md        # legacy; existing files unchanged; no new entries
```

Lane READMEs link canonical `docs/01-*` and `docs/02-*` owners; no default lane `design.md` exists. `authorization/` stays at the root only because frozen g2/s1 manifests bind those exact paths; it is legacy compatibility storage, not active architecture.

Existing evidence ownership for migration:

- On master `0939461`: Lane A owns `evidence/lane-a-reference-host/`; the older semantic folders are superseded Lane B/history inputs.
- On `lane-b-optimization` `1e4600f`: Lane B owns `evidence/windows-path-safety/`, `semantic-review-diagnosis/`, `semantic-review-wave/`, `generation-endpoint-diagnosis/`, `generation-endpoint-wave/`, `semantic-review-retry-diagnosis/`, and `semantic-review-retry-wave/`.
- After merge: combined root owns `evidence/lane-b-exit/` plus the new integrated rebaseline evidence.

Verify the actual branch inventory before moves; do not silently omit an additional directory.

## Work-Package Rules

Each lane permanently owns only `README.md` and `plan.md`. Substantial work may create one `work/<nn>-<name>.md` containing its complete lifecycle: plan, plan audit, implementation, implementation audit, verification, optional live proof, decision, and Outcome. Minor work remains in the plan table. Procedural gates do not create separate documents.

Required order:

```text
Plan → Plan audit → resolve → implement
→ implementation audit → resolve → verify → Outcome
```

There is no fixed commit cadence. Package states are `proposed`, `planned`, `implementing`, `verifying`, `complete`, `blocked`, or `reverted`.

The parent agent owns lane state and documentation. Subagents receive bounded scopes and return work/findings; they do not create process documents, evidence/approval folders, change package state, or commit unless explicitly assigned an exact boundary. The root plan is Integration Captain-owned.

## Scope

Included:

- preserve both checkpoints and Lane B local-only artifacts;
- merge Lane B into master with normal history;
- retain B0 and generation correction; keep semantic correction reverted;
- verify the integrated runtime provider-free;
- move existing slice docs intact into history;
- move lane evidence to its lane;
- add root/lane navigation and plans;
- update `.devin/rules/graphpilot.md`, documentation indexes, status links, and relative links;
- audit and commit the local master checkpoint.

Excluded:

- new Lane A or Lane B feature/optimization work;
- Azure/provider calls, promotion, certification, or deployment;
- backend/frontend reorganization beyond integrating committed lane work;
- deleting or rewriting historical evidence, `.graphpilot` artifacts, authorization, branches, or worktrees;
- pushing.

## Plan Adoption

`0939461` is the clean Lane A runtime checkpoint; this plan is the only allowed pre-integration delta. Before committing it, create `pre-block6-lane-integration-20260730` at `0939461`. Commit the audited plan under the current project cadence. Implementation preflight then requires: the preservation branch still equals `0939461`; Lane B still equals `1e4600f`; the merge base is unchanged; and master differs from `0939461` only by this plan commit. The new work-package workflow takes effect only after the rules/documentation cutover.

## Execution

### 1. Preflight and preserve

- Verify exact inputs with `git rev-parse master`, `git rev-parse lane-b-optimization`, and `git merge-base master lane-b-optimization`; require the three hashes in the Inputs table.
- Verify Lane B is clean and master has only the committed plan delta described in Plan Adoption; stop on other drift.
- Verify Lane B-only commits with `git cat-file -e <commit>^{commit}` and Lane B-only paths with `git ls-tree -r --name-only 1e4600f -- <path>` before merge.
- Generate `evidence/block6-integration-preservation.json` with path, size, and SHA-256 for every file in the eight immutable g2/s1 package/run/workspace/guard trees and the Lane B ledger.
- Copy those eight trees to master at the same relative paths only when absent; reject collisions unless byte-identical, then verify source/destination equality.
- Preserve the Lane B ledger separately as `.graphpilot/evaluation/workflow-audit/baseline-ledger-lane-b-checkpoint.json`; after copying its guard runs, append its two accepted reports to master’s existing ledger through `WorkflowAuditLedgerService` with stale-write checks. Never overwrite either ledger.
- Confirm reserved ports/processes/browsers are free.
- Bind accounting at 18 controlled / 19 aggregate calls; this plan adds zero provider calls.

### 2. Merge

- Prepare `git merge --no-commit --no-ff lane-b-optimization`; no squash/rebase.
- Preserve Lane A A03/A04, Lane B B0/generation, the semantic revert, and authorization bytes.
- Audit the staged merge before commit; resolve every critical/high/medium finding and run all focused/full checks below except the clean-HEAD baseline.
- Resolve code conflicts by coherent behavior/evidence, not branch preference. Treat conflicting Block 6 prose as migration input.
- Commit a normal two-parent merge only after the staged audit/checks pass.

### 3. Verify the integrated runtime once

After the merge commit, run exactly one fresh clean-HEAD baseline: `run-workflow-audit-block6-integrated-01`. Require 19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake calls, 0 Azure calls, built-preview browser pass, and append-only ledger entry. If it fails, preserve the terminal identity and stop/revert; never rerun that identity. Begin document moves only after it passes.

Amendment 4 adds one required equality to this gate: the report `compatibilityKey` must equal `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`. `WorkflowAuditReportService.compatibility_key()` hashes only the scenario-set, run-manifest, observation, browser-evidence, and report schema digests; A04 changed validator messages and MCP issue bounding without touching those schemas, so the key is expected to hold. A different key is a blocking regression: stop, preserve the terminal identity, and never rerun it.

Exact pre-commit checks:

| Gate | Command |
| --- | --- |
| Lane A focused | `cd backend; uv run python manage.py test tests.core.test_context_document_validator tests.core.test_context_persistence_service tests.mcp_server.test_context_tools` |
| Lane B focused | `cd backend; uv run python manage.py test tests.evaluation.workflow_audit.test_live_anchor_service tests.management.test_live_workflow_anchor_command tests.generation.test_generation_packet_builder tests.generation.test_pre_layout_generation_service` |
| Backend | `cd backend; uv run python manage.py test` |
| Frontend | `cd frontend; npm run verify` |
| Baseline after merge | `cd backend; uv run python manage.py run_workflow_audit baseline --run-id run-workflow-audit-block6-integrated-01 --control-workspace <absolute-master-root> --json` |
| Semantic baseline | `git diff --exit-code 5ec80b7 -- <semantic service, four V1 prompts, four V1 input/repair schemas>` |
| Retained Lane B | Compare the B0 and generation-correction path manifests from commits `4f02b0a` and `a17bc40` byte-for-byte with `1e4600f` |
| Merge history | `git rev-list --parents -n 1 <merge-commit>` must show master and `1e4600f` parents |

The semantic comparison covers `backend/services/generation/review/semantic_review_service.py`, the four `backend/assets/prompts/{direct,context}-semantic-review{-response-repair}-v1.md` files, and the four `backend/assets/schemas/{direct,context}-semantic-review{-repair}-input.json` files. Also run compatibility, path-safety, authorization-byte, security, no-rerun, and secret-scope checks. A material regression blocks the refactor and requires fixing before merge commit or reverting the committed merge.

### 4. Reorganize documentation

Before moves, generate and audit `history/relocation-map.json` from the union of both checkpoint trees. It must classify every group-root document/evidence directory with exactly one old path, new path, owner, and action; reject omissions, duplicate destinations, overwrites, and unclassified paths. Embedded path strings in immutable machine evidence remain historical and are interpreted through this map.

Use batched Git moves; do not rewrite historical prose except links/navigation, the Amendment 1 status correction, and the Amendment 5 rename.

- Correct `00-group.md` before archiving it (Amendment 1), then move it to `history/shared/`.
- Move this integration plan to `history/shared/` as the one-time integration record and author a separate permanent root `plan.md` (Amendment 3).
- Rename the drifted A04 document with `git mv` so its filename matches its title (Amendment 5).
- Move Lane A slice-model docs intact to `history/lane-a/`.
- Move B0 and Lane B S01–S12 docs intact to `history/lane-b/`.
- Move superseded cross-lane group/design plans to `history/shared/`.
- Move Lane A evidence into `lane-a/evidence/`.
- Move Lane B evidence into `lane-b/evidence/`.
- Move only combined integration/handoff evidence into root `evidence/`.
- Create root and lane READMEs/plans from current checkpoints.
- Never rewrite/delete pre-existing `.graphpilot/evaluation` artifacts; additive copies, the one fresh integrated run, and append-only ledger updates defined above are permitted.
- Keep existing `authorization/*` files at exact paths; add only a legacy README and prohibit new entries. Provider/live work remains prohibited until a separately audited structure/rules amendment defines a parent-owned immutable lane run-record location.
- Move self-digested evidence as whole directories without changing machine content. Add one relocation index for old-to-new tracked paths.

Existing history becomes read-only. Future completed work documents stay at stable paths under lane `work/`; agents do not move them after every milestone.

### 5. Apply rules and navigation

Update the single `.devin/rules/graphpilot.md` ruleset with the accepted lane ownership, work-package model, parent/subagent restrictions, workflow order, package states, evidence criteria, no-new-authorization rule, and Integration Captain ownership. Per Amendment 2 the work-package model is **scoped**, not global: the `00-epic.md` + `NN-*.md` slice model remains the repository default for every other epic and Block 6 sibling folder, and the work-package section carries an explicit "applies to" line naming `06-whole-workflow-optimization` only. Update `AGENTS.md` only to keep its terse source-of-truth/workflow summary aligned. Archive or reduce `11-block-execution-and-parallelism.md` to a link so it cannot remain a competing policy, and record the accepted ownership/document-model change in `docs/02-design-and-features/decision-decisions.md`.

Update `docs/README.md`, Epic 3 indexes, `00-current-state.md`, and affected links. `00-current-state.md` owns cross-project live status/next step; lane plans own bounded package state and detailed execution records. Do not duplicate canonical design.

### 6. Audit and checkpoint

Documentation checks only after the moves:

- `git diff --check`;
- all JSON parses and moved self-digests remain valid;
- authorization bytes and g2/s1 bound paths are unchanged;
- no broken relative Markdown links;
- no active lane slice docs remain at the group root;
- exactly one root, Lane A, and Lane B plan owner exists;
- no unrelated runtime source changed during the documentation phase;
- fresh read-only agents using only their README and plan report: Lane A is paused after A04 and may not start its next package before this checkpoint is adopted; Lane B is blocked on accepted integrated rebaseline/re-ranking and may not start provider/live work; the Integration Captain must finish audit/review before creating new lane worktrees;
- independent documentation audit has zero unresolved critical/high/medium findings.

Update this plan’s Outcome, commit locally on master, and stop for review. Do not push or create new lane worktrees yet.

## Conflict and Rollback Rules

- Canonical `docs/02-*` design wins over delivery history.
- Immutable failed/reverted evidence remains preserved.
- If a move would invalidate frozen machine evidence, retain the bound path and mark it legacy.
- Abort an uncommitted failed merge or revert a committed merge normally; never reset over work.
- Documentation reorganization commits remain separately revertible.
- Old branches/worktrees remain until explicit deletion approval.

## Exit Criteria

- Integrated Lane A and retained Lane B behavior pass one complete provider-free baseline.
- The accepted root/lane/history/evidence hierarchy and single ruleset exist.
- Existing history/evidence is preserved and authorization is visibly legacy/closed.
- Fresh-agent navigation and all documentation checks pass.
- Master is clean, local, unpushed, and ready for review before new lane worktrees are created.

## Amendments (2026-07-30)

Accepted after sections 1–3 were verified; they bind sections 3–6. Sections 1–2 are unchanged.

| # | Severity | Section | Amendment |
| --- | --- | --- | --- |
| 1 | High | 4 | `00-group.md` is factually wrong at HEAD: its Slice Plans table still shows S05 "Ready · plan audit pass" and S06–S08 "Blocked" and has no S09–S12 rows, because no `lane-b-optimization` commit touched it (shared docs were reserved for the Integration Captain). Correct it to truth **before** archiving — S06 implemented and retained, S07 dispatched candidate g2 and passed, S08 decided retain, S09–S12 semantic retry failed and was reverted — then move it to `history/shared/`. Preserve all other prose. |
| 2 | Medium | 5 | Scope the rules change. The slice model (`00-epic.md` + Slice Plan + `NN-*.md` in fixed section order) stays the repository default; Epics 1, 2, 4, 5 and Block 6 siblings `01-*`–`05-*` conform and must not be silently invalidated. The work-package model applies **only** to `06-whole-workflow-optimization`, declared by an explicit "applies to" line. Promoting it globally is a separate decision with its own migration, not a clause inside this refactor. |
| 3 | Medium | 4 | This document is a one-time integration record, not the permanent root navigation plan, and the two must not share a path. It moves to `history/shared/` (carrying its Outcome) and a new, separate root `plan.md` is authored for ongoing navigation. Decided before `history/relocation-map.json` is generated. |
| 4 | Low | 3 | The integrated baseline additionally requires `compatibilityKey` == `sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`. A mismatch is a blocking regression; preserve the terminal identity and never rerun it. |
| 5 | Low | 4 | `lane-a-04-snapshot-and-interface-contracts.md` is titled "A04 · Authoring Discoverability" after the r1 rescope. `git mv` it to a filename matching its title and update the link in `lane-a-00-group.md`, so permanent history does not carry a misleading name. |

Unchanged constraints: no provider calls, no push, no history rewrite, no branch/worktree deletion, accounting stays 18 controlled / 19 aggregate, and the independent documentation audit must reach zero unresolved critical/high/medium findings before the checkpoint commit.

## Outcome

**Completed.** Lane B merged into Lane A/master with normal two-parent history, the
combined runtime verified provider-free, and Block 6 reorganized into root / lane /
history / evidence / legacy-authorization folders. Master is local and unpushed.

**Commits.** `e1b6c58` audited plan → `8e710f9` merge (parents `e1b6c58` +
`1e4600f`, automatic, zero conflicts) → `cd19323` amendments + preservation manifest
→ this documentation checkpoint. Preservation branch
`pre-block6-lane-integration-20260730` pins the pre-merge checkpoint `0939461`.

**Verification.** Lane A focused 90 OK (2 skipped); Lane B focused 77 OK; backend
1107 OK (6 skipped); frontend `npm run verify` pass (lint + build + 419 unit + 43
e2e). Baseline `run-workflow-audit-block6-integrated-01` hit every required value —
19 observations, 16 generated, 1 blocked, 2 expected errors, 56 fake calls, 0 Azure
calls, built-preview browser pass, ledger appended to 7 entries — and its
`compatibilityKey` equals the Amendment 4 value
`sha256:d77f21f801006fe95a436171697ac1d38869bde834c619b802971fde5529ebd1`.
Accounting stayed 18 controlled / 19 aggregate; this work added zero provider calls.

**Retention proved by diff.** Semantic files are byte-identical to `5ec80b7`, so
`b5ef422` stays reverted by `a6e7ad0`; Lane B runtime files match `1e4600f`; Lane A
files match `0939461`; the 12 `authorization/` files match both source branches.
406 Lane B local artifacts were copied byte-for-byte with 0 problems, the Lane B
ledger was preserved as a separate checkpoint snapshot rather than overwriting
master's, and its two accepted guard baselines were appended through
`WorkflowAuditLedgerService`.

**Audits.** Independent read-only audits covered the plan, the staged merge, link
integrity, evidence integrity, and fresh Lane A / Lane B / Captain navigation. Every
critical, high, and medium finding is resolved. The merge audit's sole finding
(unused `WorkflowAuditMetricStore` imports) was false — all three files use the
symbol. The Lane A navigation audit correctly found the lane never stated that
provider work was unauthorized, omitted root-plan ownership, and omitted the
lifecycle order; all three were fixed, making Lane A symmetric with Lane B. Final
state: 23/23 self-digests verify, both frozen `g2`/`s1` anchor and approval bindings
resolve with matching digests, 40 relocation entries with 40 unique destinations,
and zero broken relative links introduced.

**Deviations.**

1. `11-block-execution-and-parallelism.md` was **scoped, not reduced to a link.**
   Section 5 called for reducing it, but Amendment 2 keeps the slice model as the
   repository default and that policy still governs every other block; gutting it
   would have invalidated ten conforming folders. It now carries an explicit scope
   note excluding this group.
2. `.devin/` is **gitignored**, so `.devin/rules/graphpilot.md` is updated on disk
   but is not version-controlled. The scoping boundary is therefore also recorded in
   the tracked `AGENTS.md`. Tracking `.devin/rules/` is a repository policy decision
   left to the user.
3. One extra Lane B artifact outside the exit handoff's bound eight trees
   (`packages/pkg-b6g1-20260729-01/manifest.json`, a superseded package) was
   preserved additively and flagged `bound=false` so nothing remained worktree-only.
4. The four A04 link **labels** in archived Lane A documents were updated to the new
   filename, serving Amendment 5's intent that history not carry the misleading name.
5. One pre-existing broken link remains at
   `docs/research/evidence-based-diagram-context/08-implementation-and-promotion.md:100`
   (stale `backend/services/generation/llm_client.py`; the file lives at
   `backend/services/llm/llm_client.py`). It predates this work and was left alone.

**Follow-ups.** Root gates G1–G4 remain open: adopt this checkpoint, re-rank the
backlog against the integrated baseline, obtain a new live authorization before any
provider call, and only then create fresh lane worktrees. The `GP-LB`, `GP-B0`, and
`GP-S05` worktrees and their branches are retained pending explicit deletion
approval.
