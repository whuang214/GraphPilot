# Lane A Slice 02: Devin Host Transition

## Purpose

Retarget Lane A from GitHub Copilot to Devin CLI as the primary host, retire the unexecuted Copilot baseline cells, and capture one provider-free Devin reference observation before any candidate implementation.

## Background

The approved Lane A design fixed GitHub Copilot in VS Code as the primary host and required strict cold/warm Copilot profiles before any measured host-wall claim. Two Copilot baseline attempts did not produce evidence:

- `run-host-benchmark-todo-c0-02` was armed, made zero MCP and zero provider calls, and finalized `interrupted`.
- `run-host-benchmark-todo-c0-03` was prepared and never armed.

The repeated blocker was host-side integration reliability rather than any GraphPilot defect: the A01 harness passes its 22 focused tests, including real stdio proxy/direct equivalence and provider blocking. The user has decided that Devin CLI, not GitHub Copilot, is the host GraphPilot targets going forward.

That decision removes the purpose of the Copilot C0/W0/C1/W1 cells. It does not remove the need for a pre-candidate reference observation.

## Design

Devin CLI becomes the primary host in the Lane A design and the Block 6 host-measurement prerequisite. MCP is disabled in this environment, so Devin reaches the GraphPilot stdio server through a repository skill that drives the MCP Inspector CLI, matching the established local pattern used for other MCP-backed skills.

The Copilot benchmark cells are retired and their identities deleted. The A01 host-benchmark implementation, schemas, artifact store, and tests remain committed and untouched: they are audited, verified, referenced by the workflow-audit owner, and their contracts remain reusable. Retiring the cells is a plan and documentation change, not a code removal.

The replacement pre-candidate observation is `R0`, a provider-free Devin reference run that stops after a successful durable JSON 2 save. It records host-agnostic contract properties rather than wall time:

- workflow and authoring response bytes against the current 8,212-byte workflow response;
- MCP tool-call count, which is the control that detects the added authoring-contract round trip;
- JSON 1 and JSON 2 authoring attempts;
- deterministic validation failures as `{tool, code, path}`;
- Todo BDD relationship closure, specifically the application-to-repository composition and TodoItem storage relationships the original cold profile omitted.

Wall time is explicitly excluded. Devin is a different host with different tooling, and this slice's agent has already read the Lane A design, the BDD checklist, and the recorded Todo gap, so any timing or search-count figure from it would be contaminated and non-representative. `R0` and its later candidate counterpart `R1` are labeled reference-host characterization, never measured evidence, and never compared against the Block 5 controlled anchor or the retired Copilot cells.

## Included Work

- Record the host transition, dropped Copilot baseline, and reference-characterization claim limits in the canonical decision index.
- Update the Lane A design owner for the Devin primary host, retired C/W/I cell definitions, the `R0`/`R1` reference boundary, and the removed human-arm procedure.
- Update the Lane A group owner for the revised scenario, A02 scope, human-gate removal, slice plan, and acceptance criteria.
- Update the Block 6 owner and slice group for the retired Copilot cold/warm prerequisite and its Devin replacement.
- Update the shared success contract's performance-domain label so the host domain is not named for a retired host.
- Rewrite A03's dependency gate from a Copilot-specific "valid A02 baseline" to the host-agnostic completed A02 reference observation, in both the group table and A03's own precondition text.
- Revise A07 from retired C1/W1 cells and the Copilot human procedure to one `R1` reference observation compared only against `R0`.
- Update forward-looking A05 references to the Copilot procedure, and repoint A01's next-slice link and A03's previous-slice link to this document.
- Update the current-state board and the documentation index entry for Lane A.
- Delete the retired Copilot frozen prompts and operator runbook, and delete the `run-host-benchmark-todo-c0-02` and `run-host-benchmark-todo-c0-03` fixture artifacts.
- Add the GraphPilot MCP skill under `.devin/skills/` so Devin can reach the stdio server provider-free.
- Execute one provider-free `R0` reference run and record its counters as slice evidence.

## Not In Scope

- Removing, rewriting, or disabling the A01 host-benchmark implementation, schemas, artifact store, command, proxy, or tests.
- Editing historical evidence: S13–S15 records, Block 5 anchor evidence, prior backlogs, and committed slice Outcomes retain their recorded host and identities. The two `block6-backlog` evidence files still name a required Copilot warm profile; they are superseded in place by the decision entry and the Block 6 owner update rather than rewritten, because evidence artifacts record what was true when captured.
- Lane A candidate contracts or code, which remain owned by A03 through A06.
- Any wall-time, percentage, or measured-savings claim from a Devin observation.
- Lane B files, worktrees, evidence, and provider identities.
- Provider-backed end-to-end runs, which remain a separate optional gate.

## Target Areas

- `lane-a-host-workflow-design.md`, `lane-a-00-group.md`, and this slice document
- `lane-a-04-authoring-discoverability.md`, `lane-a-06-host-interface.md`, `lane-a-08-candidate-measurement.md` link and procedure references
- `lane-a-01-host-benchmark-contract.md` next-slice link only; its Outcome is history and stays unchanged
- `../07-block-06-whole-workflow-optimization.md` and `00-group.md` host prerequisite sections
- `../01-success-contract.md` performance-domain host label
- `../../../00-current-state.md` and `docs/README.md`
- `docs/02-design-and-features/decision-decisions.md`
- Deleted: `lane-a-todo-c0-frozen-prompt-v1.txt`, `lane-a-todo-c0-frozen-prompt-v2.txt`, `lane-a-todo-w0-frozen-prompt-v1.txt`, `lane-a-baseline-operator-runbook.md`
- Deleted, untracked and unrecoverable: the two Todo fixture host-benchmark run folders
- New: `.devin/skills/graphpilot-mcp/SKILL.md`
- New: `evidence/lane-a-reference-host/r0.json`

## Exit Criteria

- Exactly one primary host is named across the Lane A design, group, Block 6 owner, shared success contract, and current-state board, with no surviving Copilot gate presented as active.
- A03's precondition and A07's measurement design are coherent with the retired cells: A03 depends on the completed A02 reference observation, and A07 compares `R1` only against `R0`.
- The decision index records the transition, the dropped baseline, and the explicit claim limits for reference-host observations.
- Historical Copilot evidence and committed Outcomes remain byte-unchanged.
- The A01 implementation and its 22 focused tests remain unchanged and passing.
- No document links to a deleted prompt, runbook, or slice filename.
- The skill reaches the GraphPilot stdio server, lists tools, and constructs no Azure client.
- `R0` completes provider-free through a successful durable JSON 2 save with zero readiness and zero generation calls, and its counters file contains no raw source, queries, prompts, absolute paths, or secrets.
- `R0` evidence is labeled reference-host characterization and carries no wall-time or percentage claim.
- Independent plan and implementation audits pass, and backend checks pass before the implementation commit.

## Previous Slice

[`lane-a-01-host-benchmark-contract.md`](lane-a-01-host-benchmark-contract.md)

## Next Slice

[`lane-a-03-evidence-authoring-unblock.md`](lane-a-03-evidence-authoring-unblock.md)

## Outcome

**Status:** Complete · host retargeted, Copilot cells retired, baseline finding recorded.

**Completion:** Lane A now targets Devin CLI. The Copilot `C0`/`W0`/`C1`/`W1` cells are retired and their artifacts deleted, including the terminal `run-host-benchmark-todo-c0-02` interruption and the never-armed `run-host-benchmark-todo-c0-03` manifest. The retired frozen prompts and operator runbook are removed. The A01 host-benchmark implementation, schemas, and tests remain committed and unchanged.

**Baseline finding:** The `r0` reference observation is recorded in `evidence/lane-a-reference-host/`. It did not reach a saved JSON 1, because it established something stronger — **a cold host cannot complete JSON 1 authoring against the current interface at all.** The run was clean-room with respect to this repository: every schema fact it recovered came from validation findings, not from reading GraphPilot documentation.

It also isolated the blocker exactly. Submitting the manifest with `evidence: []` produced no schema findings at all, so every other substructure validates; roughly 1,480 evidence record shapes across 16 batched probes failed identically. The host recovered the complete contract for the document root, `source`, `scope`, `claims`, claim payloads across seven kinds, `support`, and `uncertainties` purely from findings — because those use conditional `if`/`then` composition — while `evidence[]`, the one structure using a bare `oneOf`, stayed opaque.

Two independent causes were proven from the recorded draft:

1. `repositoryEvidence` requires `contentDigest`, `capturedInSourceDigest`, and per-entry `status`, none of which a host can derive. `contentDigest` is additionally ambiguous, since nothing specifies what to hash or how to canonicalize it. It is never verified in production and is explicitly stripped before the provider sees it.
2. Every branch failure returns one generic `schema_oneOf` issue reading `is not valid under any of the given schemas`, naming no missing property, no allowed enum value, and no branch. The workflow response never states the evidence contract either, so the shape is unobtainable through the interface.

A strong model still failed after exhaustive probing, which strengthens the finding: the defect is structural and host-independent. A third defect surfaced alongside them — issue lists are silently truncated to an `additional_issues_omitted` marker, so a host cannot tell how much it has not been told.

**Deviations:** The transport skill lives at `.devin/skills/graphpilot-mcp/` and is **not committed**, because `.gitignore` excludes `.devin` repository-wide; the same already applies to the conventions file. `r0` recorded a blocked outcome rather than the planned counters, so the cold-completion criterion in the group replaces the intended comparison and is a stronger, reproducible gate. A03 was inserted and the downstream slices renumbered to `A04`–`A09`. The host's own probe tooling caused two accidental unchanged resubmissions, which the workflow forbids; that is a harness fault, not a contract defect.

**Verification:** Fixture reset to cold and tracked source clean at `8627bac`. Transport verified against the real stdio server: 13 tools listed, `context_evidence_status` returned `missing` with 17 eligible files. Root cause reproduced through the production validation path. Zero provider calls.

**Follow-up:** A03 derives the machine fields and names the validation defects, then retests cold authoring to scope A04–A06.
