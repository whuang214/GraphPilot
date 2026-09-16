# Block 8: Promotion and Certification

## Goal

Decide explicitly whether the optimized, representative-validated workflow should become GraphPilot's supported default,
with current canonical documentation, complete verification, compatibility, rollback, and truthful separate certification
state.

## Question This Block Owns

Has each proposed runtime, prompt, schema, architecture, host-workflow, caching, effort, lifecycle, or UX change earned
promotion through complete evidence, and are all release/certification prerequisites honestly satisfied or still separate?

## Promotion Package

For each candidate change, present:

- baseline and promoted behavior/configuration identities;
- measured complete user-visible benefit and cumulative contribution;
- representative quality, reliability, stability, failure, and recovery results;
- host/provider/MCP/local/browser resource impact;
- compatibility, migration, security/privacy, maintenance, and operational impact;
- strongest alternative and decisive trade-off;
- rollback procedure and trigger;
- canonical docs/config/code/tests affected;
- proposal, implementation, verification, promotion, and certification state.

The user approves or rejects promotion explicitly. A block/slice completion, audit pass, or favorable provider result does not
promote anything by itself.

## Final Verification

Before promotion:

- rerun complete backend/frontend/MCP/browser gates required by affected scope;
- rerun the current Block 1 audit and Block 5 anchor against the exact candidate;
- confirm Block 7 representative package and no unresolved hard failure;
- inspect diffs, artifacts, secrets, dynamic entry points, and compatibility;
- update canonical product/architecture/MCP/feature/environment/testing/decision owners;
- verify rollback against a realistic fixture or dry run;
- commit coherently and never push without explicit request.

## Certification Boundary

Readiness and generation certification remain separate programs with their own human labels/golds, repeats, freeze,
provider/embedding authorization, gates, and reports. Block 8 records `not_run`, `incomplete`, `failed`, or `passed` truthfully.
Representative workflow validation cannot silently substitute for certification, and certification cannot rewrite runtime
observations or optimization results.

## Outputs

- Approved/rejected promotion record per change.
- Promoted canonical code/config/docs/tests or unchanged current defaults.
- Verified rollback plan.
- Final current Block 1 audit and before/after cumulative report.
- Truthful readiness/generation certification status and remaining release blockers.
- Supported-workflow handoff for maintenance and future reruns.

## Exit Gate

Every promoted change has explicit approval, complete current evidence, passing verification, synchronized canonical owners,
compatible migration/rollback, and no unresolved hard failure. Certification claims match their actual separate gate. Rejected
or deferred changes remain unpromoted with clear reconsideration triggers.

## Not Owned Here

- Fixing an evidence or quality failure by weakening its gate.
- Implementing a new unreviewed optimization during promotion.
- Treating documentation or configuration edits as proof of runtime behavior.
- Pushing, deployment, or destructive migration without their own explicit authorization.

## Block-Agent Handoff

The promotion agent assembles evidence and applies only approved promotions. Its final handoff distinguishes retained,
rejected, deferred, promoted, verified, and certified states; names exact commits/checks/rollback; updates current-state; and
leaves future workflow/audit rerun triggers explicit.
