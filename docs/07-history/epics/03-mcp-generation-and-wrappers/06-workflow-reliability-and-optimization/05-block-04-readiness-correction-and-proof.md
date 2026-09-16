# Block 4: Readiness Correction or Redesign and Proof

## Goal

Implement the approved Block 3 readiness correction, component redesign, or workflow redesign and prove that GraphPilot can
make trustworthy, durable go/no-go generation decisions without duplicate work or weakened authority.

## Question This Block Owns

Does the selected design reliably produce correct ready and blocked outcomes, preserve complete safe evidence for repair,
failure, and interruption, and remain compatible with the workflow invariants?

## Implementation Boundary

Block 4 implements only the approved Block 3 direction. If implementation reveals a different root-cause boundary or requires
a materially broader contract/architecture change, stop and return to Block 3 for review instead of expanding silently.

The implementation may be a focused correction or a broader redesign. Scope is judged by root-cause fit, not line count.

## Implementation Slice Plan

The focused correction and proof slices live in [`04-readiness-correction-and-proof/00-group.md`](04-readiness-correction-and-proof/00-group.md). The nested group owns sequencing and Outcomes; this block owner retains the correction/proof question and Block 5 gate.

## Proof Boundary

Prove readiness across newly identified, engineering-reviewed visible cases—without treating them as calibration/certification human labels—that cover at least:

- sufficient context that must permit generation;
- insufficient context with a mandatory non-overrideable blocker;
- first-response-valid behavior;
- bounded repaired-valid behavior through offline/fake proof and naturally live when reached;
- completed-invalid repair;
- provider failure;
- interruption before/after durable call and validation checkpoints;
- exact terminalization/resume without provider rerun.

A ready result reaches the first generation-provider boundary only through a local guard; this block makes no generation or
semantic-review Azure call. A blocked result reaches no generation boundary.

## Evidence Durability

Every definitely started call counts against the exact budget. Persist full safe call records immediately after provider
return/failure, persist validation events atomically when emitted, and create a schema-valid observation for final, failed, or
terminal outcomes. A process lost between provider completion and durable local write remains attempted/uncertain; no metric
or outcome is invented. Resume materializes or references the terminal observation and never calls the provider again.

## Result Classes

- **clean pass:** reviewed ready/blocked outcomes are exact and initial responses are valid;
- **repair dependent:** final reviewed outcomes are exact but at least one bounded response repair is required;
- **quality failed:** status, blocker, score/facet band, ref, or action violates reviewed expectations;
- **contract failed:** no final readiness result after the bounded response path;
- **provider failed:** typed provider failure with safe call evidence;
- **interrupted:** uncertain terminal state with no rerun.

Only a clean pass or an explicitly accepted repair-dependent result can hand off to Block 5. No result promotes an effort,
prompt, schema, or runtime setting automatically.

## Outputs

- Implemented and documented readiness correction/redesign.
- Offline/fake, failure, crash/resume, security, compatibility, and full-suite evidence.
- Separately authorized minimal live proof when required.
- Before/after readiness validity, quality, call, token, duration, repair, and reliability report.
- Decision to proceed to Block 5, return to Block 3, or remain blocked.

## Exit Gate

Readiness must reliably return reviewed-correct ready and blocked decisions; preserve all available safe call/validation
evidence; prevent false ready, missing non-overrideable blockers, invalid refs/actions, duplicate calls, and downstream
provider use; and pass complete regression/security/compatibility gates. Failed or uncertain live identities remain terminal.

## Not Owned Here

- Complete provider-backed generation/review measurement.
- Broad diagram-type/readiness stability matrices.
- Whole-workflow performance optimization beyond what the selected readiness design requires.
- Production promotion or release certification.

## Block-Agent Handoff

The implementation agent reports the exact Block 3 design implemented, deviations requiring review, proof results, live
actuals versus budget, remaining repair dependence, checks/commits, rollback, and whether Block 5 is safe to begin.
