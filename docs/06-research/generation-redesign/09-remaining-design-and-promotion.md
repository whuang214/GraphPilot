# Remaining Design and Promotion Plan

> **Status: active checklist.** This file identifies what has been discussed, what is accepted, what remains
> unresolved, and how a complete research package eventually moves into active authority. It is not an
> implementation plan yet.

## Coverage so far

| Topic | Research owner | State |
| --- | --- | --- |
| Direct versus context authority/use cases | `01-goals-and-mode-boundaries.md` | Accepted |
| One public routed generation workflow | `02-diagram-generation-workflow.md` | Accepted |
| Separate direct/context branch protocols and tools | `02-diagram-generation-workflow.md` | Accepted |
| Adaptive consultation and `interactionPreference` | `02-diagram-generation-workflow.md` | Accepted |
| Host routing of repository-truth requests | `01`, `02` | Accepted |
| Persisted direct request contract and shared request lifecycle | `03-direct-request-contract.md` | Accepted; formal schema pending |
| Typed requirements, authority fields, decisions, bounds | `03` | Accepted |
| Immutable mode/request ID/diagram name and finalized-after-generation V1 scope | `03` | Accepted |
| Shared `.graphpilot/requests/` and `diagram_request_save` | `02`, `03` | Accepted |
| Direct/context parallel JSON input layout | `04-generation-inputs-and-prompts.md` | Accepted architecture |
| Direct JSON user message and one LLM call | `04` | Accepted direction |
| Shared cleaned core semantic guidance and parallel packets | `04` | Accepted architecture |
| Logical outputs omit name; structured repairs omit examples | `04` | Accepted |
| Provider-enforced token capacity, fixed local byte ceilings, and exact example inclusion | `04`, `05`, `10` | Accepted |
| Complete fixtures -> compact mode-specific training pairs | `05-examples-and-answer-keys.md` | Accepted |
| Two fixed direct/context examples per type; separate pools/schemas | `05` | Accepted |
| Exact 12 scenarios, author/reviewer sign-off, six set versions, old-example replacement | `05` | Accepted |
| Future built-in eval size: 48 independent post-freeze cases (eight per mode/type) | `05`, `08` | Accepted |
| Built-in generator eval versus end-to-end RepoBench boundary | `05`, `08` | Accepted |
| Shared semantic candidate review over normalized logical projection | `06-semantic-review-and-quality-mode.md` | Accepted architecture |
| Composed rubric/facet catalog, hybrid scoring, typed actions, no force-save, host-routed blocking, 18-case calibration | `06` | Accepted |
| Reviewed production default, explicit standard ablation, one default semantic repair, optional reviewer deployment | `06`, `12` | Accepted |
| PyGraphviz 2.0 target layout and post-parity removal of old engines/config | `04` | Accepted direction |
| Namespace-first JSON naming and cold-turkey migration | `07-contract-naming-standard.md` | Accepted |
| Mechanical generation contracts/prompts/fixtures/PyGraphviz proof gates | `10`, `11` | Specified; implementation artifacts pending |
| Offline evaluation framework, rubric, thresholds, runs, reports, leakage | `08`, `12`, `evaluation-framework-approval.json` | User-approved 2026-07-17; implementation/live calls not approved |
| Generation/evaluation sequencing: joint promotion before implementation, hidden gold after freeze | `08`, `09`, `12` | Accepted |
| Complete seven-block generation-contract design | `01`–`07`, `generation-contract-approval.json` | User-approved 2026-07-17 |
| Direct-on-master migration, Phase 0 planning/promotion, 14 slices, rollback/gates | `13`, `migration-plan-approval.json` | Revised/user-approved 2026-07-17; Slice 14 is the full backend audit/remediation gate |

## Approved execution sequence

Generation contracts, evaluation framework, and direct-on-master migration/slice plan are approved/specified. Execute
only through the audit/commit cadence in `13`:

1. Phase 0A create/audit/commit the compatibility plus complete 14-slice redesign planning/research package;
2. Phase 0B promote/audit/commit active design/configuration owners;
3. implement current context workflow prompt/tool compatibility Slice 12 and record the pre-redesign code baseline;
4. implement redesign Slices 1–13 through per-slice implementation audits/checks/outcomes/commits;
5. execute Slice 14 full backend audit/remediation and final offline summary;
6. visible live calibration and generator/evaluator freeze only after user approval;
7. independent hidden authoring and explicit live certification;
8. separate production-promotion authorization only after pass.

No hidden gold, live evaluation call, push, destructive Git operation, or production promotion is implied by plan
approval.

## Likely active-doc promotion map

| Research document | Active promotion targets |
| --- | --- |
| `01-goals-and-mode-boundaries.md` | Product scenarios/requirements; generation design; decision log |
| `02-diagram-generation-workflow.md` | MCP workflow docs; generation design |
| `03-direct-request-contract.md` | Generation design; MCP tool contract; schema registry docs |
| `04-generation-inputs-and-prompts.md` | Generation design; backend architecture; environment reference |
| `05-examples-and-answer-keys.md` | Answer-key design; generation design; evaluation design |
| `06-semantic-review-and-quality-mode.md` | Generation/validation designs; backend architecture; environment; decision log |
| `07-contract-naming-standard.md` | Every changed schema/contract owner; decision log |
| `08-evaluation-plan.md` | Generation evaluation design and testing strategy |
| `10-mechanical-generation-specification.md` | Schema/prompt/trace/error owners; backend architecture; environment reference |
| `11-training-fixture-specification.md` | Answer-key generation design and fixture implementation slices |
| `12-evaluation-framework-specification.md` | Evaluation/matcher/judge/report design; testing strategy; release gates |
| `13-migration-promotion-and-implementation-plan.md` | Epic 3 generation-redesign group/slices; active-doc promotion; rollback/verification |

Research content should be reconciled and promoted once; active owners should not link back to research as runtime
authority.

## Cold-turkey migration impact areas

Expected areas, to be confirmed by symbol/contract impact analysis before slicing:

- formal JSON schemas and registry;
- context persistence/validation;
- readiness rubrics/reviewer/results/diagnostics;
- context resolver/generator/provenance traces;
- direct generation service and prompts;
- MCP prompt and tool contracts;
- tests and context/example fixtures;
- frontend types/adapters only where renamed canonical metadata is consumed;
- active docs, decision tracker, and delivery plan.

No existing local artifact is silently deleted or rewritten. Old IDs fail explicitly after cutover.

## Proof before implementation

Recommended smallest proofs:

1. Hand-build one complete `DirectRequest` and direct generation projection.
2. Render current Markdown and proposed JSON input for the same request; compare size and semantics.
3. Author one context-native activity example and validate all origins.
4. Replay one good and one semantically wrong fixed candidate through a prototype reviewer contract.
5. Confirm `standard` bypass and `reviewed` fail-closed behavior with fakes.
6. Produce one synthetic evaluator report proving capture, attribution, metric, and bounds behavior; it is not a
   generation-quality result.

If a proof fails, revise the smallest failed assumption instead of reopening unrelated accepted boundaries. Real
reviewed-mode certification waits for independently authored post-freeze hidden cases; historical-baseline runs are
optional informational artifacts.

## Promotion gates

1. Research docs contain no unresolved material contract ambiguity.
2. User explicitly approves the complete design package.
3. Accepted decisions are entered once into the active decision owner.
4. Generation and evaluation designs are both complete and active design/architecture/MCP/schema/testing docs are
   updated coherently.
5. Delivery slices define capture/matcher infrastructure and the post-freeze held-out-authoring milestone; live
   status is updated.
6. Implementation begins only from promoted active owners and cannot bypass the evaluation interfaces.
7. Prompts, schemas, and training examples freeze before independent held-out authoring begins.
8. Frozen reviewed-mode redesign passes absolute hidden certification; optional historical-baseline runs are
   reported separately and never retain old runtime code.
9. Tests and verification prove implementation; research then becomes historical with an ownership map similar to
   the prior context research package.

## Next design review

The user approved the generation contract (`generation-contract-approval.json`), offline evaluation framework
(`evaluation-framework-approval.json`), and execution plan (`migration-plan-approval.json`) on 2026-07-17.
Completed blocks need no reopening unless the user requests it or new evidence conflicts:

1. Authority/mode boundary and unified MCP routing.
2. Persisted direct/context request lifecycle and shared save tool.
3. MCP prompt/tool/result outcomes and warnings.
4. Direct/context LLM packet architecture, repair boundary, and token direction.
5. Exact 12-scenario training set, sign-off/versioning, 48-case post-freeze eval scope, and leakage boundary.
6. Semantic-review target, composed rubric/facets/scoring, typed actions, bounded repair, no force-save, host-routed
   blocking, single-chat-deployment behavior, result visibility, and calibration architecture.
7. PyGraphviz 2.0 target layout and supported-platform policy.

Continue in the approved execution order:

1. Phase 0A complete planning/research audit/commit, then Phase 0B canonical-design audit/commit;
2. current workflow compatibility implementation/audit/checks/commit and code baseline;
3. implement formal schema/prompt/fixture/PyGraphviz and evaluation infrastructure through Slices 1–13;
4. complete Slice 14 backend audit/remediation and final offline report;
5. freeze generator/evaluator identities after separately approved visible live calibration;
6. independently author/seal hidden built-in/RepoBench golds and run explicit live certification.
