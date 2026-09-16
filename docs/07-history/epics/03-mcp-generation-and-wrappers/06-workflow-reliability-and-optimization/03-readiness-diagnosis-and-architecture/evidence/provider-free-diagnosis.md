# Provider-Free Readiness Diagnosis

> Historical provider-free evidence from S02. Measurements, lifecycle proof, and hypotheses remain inputs; the final three-human recommendation was superseded by the active S05 causal diagnosis plan. The JSON remains immutable historical machine evidence.

Machine authority: [`provider-free-diagnosis.json`](provider-free-diagnosis.json)

Diagnosis identity: `diagnosis-readiness-block3-provider-free-20260724-01`

Source base: audited Block 3 plan commit `643de67f96dc64ed772d85eb7c946998134ccdc7` (verified through Git commit identity).

Digest methods: JSON assets use canonical sorted compact UTF-8 SHA-256; prompt/service/test files use raw UTF-8/file SHA-256. The metadata document digest `sha256:4b891a91424c6b015859e621f269f06554a8c0fe92479df9d840b8f038d36f52` is distinct from its declared runtime input digest `sha256:f353f287d15425db674dcae1f558be923a62b2b30243f8fc0b2f64bc52656592`.

Historical sources: Context S13, S14, and S15 `## Outcome` sections; Block 2 S04 `## Outcome`; current readiness service/validator source.

## Boundary

- Evidence mode: `provider_free`; Azure calls: **0**.
- Expected: a valid review passes first response; one invalid response may receive one bounded repair; checkpointed/terminal work never reruns.
- Observed: S13 high repaired; S14 medium was first-response valid on the same BDD request but changed blocker/score detail; S15 high and medium Activity-ready attempts both repaired and lost exact validation diagnostics.
- Result: the complete-projection repair is a confirmed **cost amplifier**, but current evidence does not identify its trigger.

## Exact Visible Bridge

| Item | Value |
| --- | --- |
| Scenario | `scenario-workflow-audit-activity-basic` |
| Fixture | `activity_diagram/context-examples/training/return-authorization` |
| Scenario-set digest | `sha256:f31a02716885dd2b7a51e4a17c016bf0bcda1d5274dc374659f172d7807484c2` |
| Evidence digest | `sha256:ebf789e449a50c24ee2688101c80d7d29fdc47b6a93a19a0fe3b4d86ec5d6da2` |
| Request digest | `sha256:629632f0855575187e8305a650705a54eef192f8106560f72b6dc458ae32b867` |
| Projection | 22,911 bytes; `sha256:80eefe74df7ce2c10b3b804a0e701982c48b7fd1faf4902d7f663d0f52d9c9e8` |
| Strict wire | 32,727 bytes; `sha256:021c0cb93fae7d8e94ae03f5b1deff70ab83d0be32f90fa600f0be7fdae34fa8` |

This is a visible diagnostic bridge only. It is not a calibration/holdout fixture, hidden gold, generation-certification case, or live authorization.

## Historical Evidence

| Evidence | Calls / validity | Result / limit |
| --- | --- | --- |
| S13 high BDD | 2 calls; first invalid | 112,631.031 ms + 349,535.310 ms repair; `needs_context`, score 81; diagnostics absent |
| S14 medium same BDD | 1 valid call | 77,941.939 ms; `needs_context`, score 61 with three additional conservative blockers |
| S15 Activity-ready pair | 4 calls; both efforts repaired | stopped without evaluable pair; validation diagnostics lost |
| Block 2 provider-free | 19 observations; 56 fake / 0 Azure | mechanics, quality, recovery, and no-rerun pass; no real-provider trigger evidence |

## Hypotheses

| Hypothesis | Level | Confidence | Decisive status |
| --- | --- | --- | --- |
| Prompt/schema/projection/validator mismatch | local defect | low | plausible; same BDD contract passed first response under medium |
| Complete-projection repair | component design | high as cost amplifier | does not explain trigger |
| High-effort first-response invalidity | provider/control | low | one same-input pair; S15 both efforts repaired and semantics drifted |
| Host/readiness responsibility mismatch | broader workflow | low | validation failed before a proven authority/policy defect |
| Historical S15 durability defect | local historical defect | confirmed | fixed offline; not current provider trigger |
| Missing decisive diagnostics/human authority | insufficient evidence | high | only uniquely supported current recommendation |

## Provider-Free Lifecycle Proof

The 77-test focused gate passes, including eight new tests for first-response valid, repaired valid, completed-invalid repair, provider failure, checkpoint failure before dispatch, uncertain checkpoint resume, terminal no-rerun, and identity conflict. The additive injected-client service constructs no Azure client, exposes no management command, and cannot reach generation or semantic review.

## Recommendation

Exactly one provisional Block 3 recommendation is supported:

```text
additional_evidence
```

Two genuine independent readiness reviews and adjudication are required for the visible bridge case. Only then may Block 3 freeze and independently audit one new readiness-only maximum-two-call live package. Block 4 remains unauthorized.
