# Lane A Slice Group: Host Workflow

## Goal

Make the GraphPilot-controlled host workflow completable by a cold host: the host authors only meaning, GraphPilot derives every value it can compute itself, and deterministic failures name their exact defect so a host can correct without external help.

## User Scenario

A user asks an agent host for a repository-grounded Todo system-design BDD. The host routes the request, obtains only the context/BDD authoring guidance it needs, authors one current evidence snapshot describing what it observed, saves one durable request, and invokes GraphPilot once. The host preparation path stops after request save without a provider call; a separately gated integration consumes the saved request and verifies the diagram/editor path.

## Design Principle

The host authors meaning; GraphPilot owns mechanics. One test decides where a field belongs: if the backend can derive it, the host must not be asked for it. Digests, fingerprints, timestamps, revisions, lifecycle status, canonicalization, and version tokens are backend responsibilities.

## Authority and Inputs

- The approved Lane A design is [`lane-a-host-workflow-design.md`](lane-a-host-workflow-design.md).
- The [Block 6 owner](../../../07-block-06-whole-workflow-optimization.md) owns optimization boundaries and the retain/revert gate.
- The [Block 6 group](../shared/00-group.md) owns Lane A/Lane B causal separation and current Lane B sequencing.
- The [Block 5 handoff](../../../05-complete-live-anchor-and-reaudit/04-reaudit-and-handoff.md) supplies the controlled anchor, provider-free baseline, and host opportunity.
- Todo source is fixed at commit `8627bac5169e3a8800ea7f3ddfb64e52b4fe92c7`, verified by `git rev-parse HEAD` with a clean tracked fixture; retired Copilot identities are terminal and never reused.
- The primary host is Devin CLI. A02 records that transition and the resulting claim limits: reference-host observations are provider-free characterization and never carry wall-time or percentage claims.
- The A02 baseline finding is that a cold host cannot complete JSON 1 authoring against the current interface. Required evidence fields are not derivable by a host, and every branch failure reports one generic `oneOf` rejection naming no defect.
- The user approved execution of this plan, but no live provider budget is authorized by that approval.
- Live status remains only in [`../../../00-current-state.md`](../../../../../../../05-delivery/01-current-state.md).

## Approved Boundary

Lane A owns only GraphPilot-controlled host/integration preparation:

- backend derivation of every evidence value a host cannot know;
- deterministic validation failures that name the intended branch's exact defects;
- a `diagram_generation_workflow` router and one `diagram_generation_get_authoring_contract` lookup;
- compact validated mode/type examples and conditional BDD guidance;
- a replaceable current JSON 1 snapshot with a semantic host draft;
- backend-issued freshness/version references;
- durable JSON 2 requests;
- provider-free reference observations and separately gated integration.

Lane A does not change the host agent, Lane B provider contracts, provider controls, semantic-review or generation-endpoint wave files, live identities, or evidence. Persistent MCP, generalized hosts/repos, representative matrices, promotion, and certification remain deferred.

## Execution Topology

```text
Audited Lane A plan
  -> A01 Host Benchmark Contract
  -> A02 Devin Host Transition
  -> A03 Evidence Authoring Unblock
  -> r1 cold-authoring retest (scoped A04)
  -> A04 Authoring Discoverability   [Lane A paused here]
       |-> A05 Snapshot Backend --|
       |-> A06 Host Interface ----|-> A07 Lane A Integration
                                         -> A08 Candidate Measurement
                                         -> A09 Wave Decision
```

A03 was sequenced before the contract work because its retest determined how much of A04 through A06 is justified. `r1` answered that: a cold host now completes the workflow, so the residual cost is guidance rather than impossibility, and A04 narrowed to discoverability accordingly.

**Lane A is paused after A04 for the planned Block 6 documentation reorganization.** A05 and A06 have not started. On current evidence the two should also be reordered when work resumes: `r1` shows guidance dominating and payload secondary, so A06's contract lookup is worth more than A05's snapshot redesign, and A05's true scope is best decided by a reference observation taken after A06.

A05 and A06 are independent branches from A04; A07 waits for both committed results. They are the only parallel-safe write slices and require separate worktrees named `lane-a-a05-snapshot` and `lane-a-a06-host-interface`, exact disjoint file lists committed by A04, unique temporary workspace/run prefixes, and no shared registration/schema/diagram/docs edits. Before integration, the A07 owner verifies the two changed-file sets have no intersection and neither contains an A07-reserved or Lane B path, then integrates A05 before A06 and runs the combined gate. In one worktree A05 then A06 execute sequentially. Every observation, integration gate, provider operation, and retain/revert decision is sequential.

## Slice Concurrency and Gates

| Slice | Depends on | Inputs | Outputs | Exclusive write ownership | Forbidden/shared ownership | Parallel with | Resources | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 · Host Benchmark Contract | audited plan | workflow-audit external evidence, cold/warm diagnostics, Todo fixture | provider-free benchmark contracts, recorder boundary, fake proof | new host-benchmark evaluation modules/schemas/tests and A01 Outcome | production host/context behavior; Lane B; shared status/decision | none | temporary workspaces, no provider/browser required except fake proof | schema/security/equivalence audit, focused/full backend checks |
| A02 · Devin Host Transition | committed A01 | retired Copilot cells, transport skill, cold fixture | host retarget, claim limits, baseline finding | Lane A owner/status/decision updates and A02 Outcome | candidate implementation; Lane B | none | provider-free | owner coherence, no stale Copilot gate, link integrity |
| A03 · Evidence Authoring Unblock | committed A02 | recorded cold-authoring failure and its exact defects | backend-derived evidence fields, best-branch validation errors | `services/core` context validation/persistence and focused tests, plus A03 Outcome | schema/contract changes; host tools; Lane B | none | provider-free unit tests, temporary workspaces | host-authorable candidate promotes, derived values stable, no generic `oneOf`, full backend suite |
| A04 · Authoring Discoverability | committed A03 and its `r1` retest | `r1` cause classification | allowed-property reporting, breadth-preserving truncation, frozen authoring contract | context validator, MCP issue bounding, MCP public-surface owner, and A04 Outcome | schema changes; the authoring-contract tool; Lane B | none | provider-free unit tests | reporting-only proof, frozen-contract completeness, implementation audit, full backend suite |
| A05 · Snapshot Backend | committed A04 | frozen candidate/canonical snapshot and request contracts | current-snapshot validation/persistence, version refs, cleanup, internal adapter | context core/services and focused tests named by A04 | host renderer/tool; shared MCP/schema registration/diagram/docs; Lane B | A06 in separate worktree | isolated temp workspaces | failing-before/passing-after, persistence/concurrency/cleanup/security audit |
| A06 · Host Interface | committed A04 | frozen route/authoring contracts and examples | router tool, selected contract lookup, size/parity tests | host workflow/authoring services, new prompt/example assets, focused tests | context core; shared MCP/schema registration/diagram/docs; Lane B | A05 in separate worktree | no provider; in-memory/fake tool tests | selected-only output, byte budget, no-side-effect/security audit |
| A07 · Lane A Integration | committed A05+A06 | both candidate lanes and baseline | shared wiring, canonical grounding receipt, docs, full provider-free proof | shared MCP/schema/diagram/frontend-type/docs integration files and A07 Outcome | Lane B exclusive files/evidence/provider identities | none | full backend/frontend/MCP/browser provider-free gates | combined implementation audit, compatibility/security/recovery pass |
| A08 · Candidate Measurement | committed A07 | exact compatible controls, new identities | candidate reference observation and provider-free integration | new candidate run/evidence identities and A08 Outcome | code edits after freeze; old identities; Lane B live resources | none | reference host; sequential provider only if authorized | cold-completion criterion, quality/no-rerun audit |
| A09 · Wave Decision | terminal A08 | baseline/candidate evidence and guard results | retain/revert, cumulative handoff, Block 7 recommendation | Lane A decision/handoff and integration-owned shared status/decision updates | next-wave implementation; provider calls; evidence mutation | none | provider-free report/guard only | independent causal decision audit and final verification commit |

## Slice Plans

| Slice | Plan | Status |
| --- | --- | --- |
| A01 · Host Benchmark Contract | [`lane-a-01-host-benchmark-contract.md`](lane-a-01-host-benchmark-contract.md) | Complete · audit/full verification pass |
| A02 · Devin Host Transition | [`lane-a-02-devin-host-transition.md`](lane-a-02-devin-host-transition.md) | Implementing · baseline finding recorded |
| A03 · Evidence Authoring Unblock | [`lane-a-03-evidence-authoring-unblock.md`](lane-a-03-evidence-authoring-unblock.md) | Complete · retest completed the workflow in 7+4 attempts |
| A04 · Authoring Discoverability | [`lane-a-04-authoring-discoverability.md`](lane-a-04-authoring-discoverability.md) | Complete · Lane A paused here for documentation reorganization |
| A05 · Snapshot Backend | [`lane-a-05-snapshot-backend.md`](lane-a-05-snapshot-backend.md) | Blocked on A04 |
| A06 · Host Interface | [`lane-a-06-host-interface.md`](lane-a-06-host-interface.md) | Blocked on A04 |
| A07 · Lane A Integration | [`lane-a-07-integration.md`](lane-a-07-integration.md) | Blocked on A05+A06 |
| A08 · Candidate Measurement | [`lane-a-08-candidate-measurement.md`](lane-a-08-candidate-measurement.md) | Blocked on A07 |
| A09 · Wave Decision | [`lane-a-09-wave-decision.md`](lane-a-09-wave-decision.md) | Blocked on A08 |

## Host and Live Gates

- Reference-host observations run provider-free, use only what MCP returns, and stop after durable JSON 2 save.
- Integration first runs provider-free. Any provider-backed integration requires a separate exact package, short fresh identities, path-length proof, explicit user budget authorization, and exclusive Lane B provider-resource release.
- A04 may begin only after A03's cold-authoring retest classifies the remaining failures.
- A09 is the only retain/revert authority; a narrow successful proof does not authorize Block 7, promotion, or certification automatically.

## Cold Completion Criterion

Lane A's exit condition replaces measured host-wall claims, which the reference host cannot produce:

> A cold host, using only what MCP returns, produces a valid JSON 1 and JSON 2 in at most two attempts each, without authoring any value the backend could derive.

This is binary, reproducible by any host, and currently failing.

## Security and Evidence Rules

- Persist only bounded safe metrics, relative paths, identities, version tokens, counts, durations, and validation `{code,path}` detail.
- Never persist raw source, search queries, prompts, provider messages/responses, hidden reasoning, credentials, `.env` values, or hidden gold.
- Reference-host observations record contract properties such as response bytes, tool-call counts, authoring attempts, and validation codes. They never record wall time, because the reference host is not the measured host and its operator has repository knowledge.
- Existing Block 3–6 authorization/evidence folders remain immutable and outside Lane A ownership.
- Completed, failed, invalid, interrupted, or uncertain identities are terminal and never reused.

## Risks and Rollback

- Backend-derived evidence values could differ from what a host would have supplied; A03 proves derivation is deterministic and leaves the canonical manifest shape unchanged so existing writers stay valid.
- Best-branch error selection could mislead when no branch is intended; the discriminator rule runs first and the fewest-errors fallback is deterministic.
- The extra authoring-contract call may cost more than it saves; A08 counts it in the candidate observation.
- The snapshot redesign may weaken quality or recovery; A07/A08 fail closed and A09 reverts the candidate if any guard fails.
- Flat persisted claims could leak into Lane B provider contracts; A05 uses an internal adapter where practical and A07 serializes any unavoidable shared change after Lane B release.
- One Todo observation is not representative stability; Block 7 owns repetition/generalization.
- Rollback reverts A04–A07 candidate behavior as one coherent host-authoring wave while retaining A01–A03 and A08 evidence and provider-free tooling that proved noninfluencing.

## Plan Audit

An independent read-only audit reviewed the A04 plan after `r1` rescoped it from contract freezing to authoring discoverability. Its critical findings were accepted: the truncation algorithm is now specified step by step and provably bounded, and the allowed-property lookup names its mechanism. Its objection to an exit criterion depending on a later observation was accepted and that criterion moved to A08. The audit also challenged the claim that recomposing `evidence[]` preserves the accepted document set; rather than specify and prove that conversion, the recomposition was **dropped**, because A03's best-branch reporting already removed the opacity it existed to fix and `r1` contains no `schema_oneOf` at all.

An independent read-only audit then reviewed the A03 validation-feedback plan. It confirmed correct scope bounding, document shape, and the deferral of the diagram validator. Its critical claim that `$ref`-based `oneOf` branches do not expose their index at `schema_path[0]` was rejected by empirical probe: `jsonschema` resolves the refs and emits sub-errors as `[0, 'required']` and `[1, 'required']`, grouping cleanly, and the fewest-errors rule selects `repositoryEvidence` at 6 sub-errors over `userClarificationEvidence` at 8. Its valid findings — the incomplete renumbering reference list, the second mixed `$ref`/inline `oneOf` at `multiplicity.upper`, a missing discriminator-match test, unclear design ownership, and the determinism assumption — are all resolved in the plan.

A later independent read-only audit reviewed the A02 replacement plan after the user retargeted Lane A from GitHub Copilot to Devin CLI. It confirmed correct scope bounding, Lane B isolation, historical-evidence protection, evidence-integrity limits on reference-host observations, and document shape. It required the shared success contract's host-domain label, A03's dependency gate wording, A07's retired C1/W1 design, A01's next-slice link, and the superseded `block6-backlog` assertions to be handled explicitly; those corrections are in the plan. Two findings were rejected with evidence: `docs/README.md` was already listed, and the `../07-block-06-whole-workflow-optimization.md` relative path resolves correctly and matches this document's existing links.

An independent read-only audit verified the scope, canonical owners, baseline-before-candidate order, dependency DAG, reversibility, acceptance/verification coverage, Lane B isolation, human/live gates, and A04/A05 as the maximum safe parallelism. Its first pass required completion of this audit record, current-state visibility for both causal lanes, verified Todo commit provenance, explicit A04/A05 worktree/ownership/merge controls, an exact A01 fake-proof matrix, an A03 owner-path precondition, and a clearer parallel topology. Those findings were corrected in the plan and slice docs. Focused re-audit confirmed every critical/high/medium finding resolved and the plan ready for commit.

## Acceptance Criteria

- A01 produces a strict provider-free capture boundary without changing production behavior.
- A02 retargets the host coherently, records the cold-authoring baseline finding, and leaves no stale Copilot gate presented as active.
- A03 lets a host-authorable candidate promote without authoring any derivable value, replaces generic `oneOf` rejection with named defects, and changes no schema or contract.
- A03's retest classifies the remaining failures and scopes A04 accordingly.
- A04 freezes one coherent snapshot/host contract with validated leakage-disjoint examples and exact canonical owners.
- A05/A06 independently pass their focused gates and touch no shared or Lane B files.
- A07 proves the integrated candidate provider-free with complete backend/frontend/MCP/browser/security/recovery checks.
- A08 satisfies the cold completion criterion and produces only separately authorized provider evidence.
- A09 retains only a candidate that lowers correction work with unchanged or improved readiness, quality, provenance, recovery, and browser behavior; otherwise it reverts.
- No reference-host observation is presented as a measured wall-time or percentage result.

## Related Docs

- [`lane-a-host-workflow-design.md`](lane-a-host-workflow-design.md)
- [`00-group.md`](../shared/00-group.md)
- [`../07-block-06-whole-workflow-optimization.md`](../../../07-block-06-whole-workflow-optimization.md)
- [`../11-block-execution-and-parallelism.md`](../../../11-block-execution-and-parallelism.md)
- [`../05-complete-live-anchor-and-reaudit/04-reaudit-and-handoff.md`](../../../05-complete-live-anchor-and-reaudit/04-reaudit-and-handoff.md)
- [`../../../../../02-design-and-features/09-workflow-audit-design.md`](../../../../../../../03-design/11-workflow-audit.md)
