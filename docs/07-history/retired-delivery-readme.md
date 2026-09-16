# Development and Delivery

This folder contains the active delivery-planning and implementation-tracking docs for GraphPilot.

## Start here

When you are planning or executing delivery work, read in this order:

1. `00-development-environment.md`
2. `01-testing-strategy.md`
3. `epics/README.md`
4. `epics/00-current-state.md`
5. the active epic folder
6. the epic's `00-epic.md`
7. the current active slice doc for that epic

## Folder structure

- `00-development-environment.md` - current local setup plus promoted generation/evaluation configuration, fixed byte
  bounds, and clearly labeled final layout/provider policy
- `01-testing-strategy.md` - current commands plus offline/fake-client policy, final evaluation gates, visible/hidden
  separation, and the required backend audit
- `02-backlog.md` - consolidated, categorized backlog of deferred, out-of-scope, and potential features
- `03-deployment-and-distribution-options.md` - prospective hosting/distribution and LLM-access options, final
  chat/embedding routing constraints, PyGraphviz packaging, and certification gates
- `epics/README.md` - entry point for epic and slice planning
- `epics/00-current-state.md` - single live cross-epic status board
- `epics/<epic-folder>/00-epic.md` - stable epic scope, goals, and acceptance criteria
- `epics/<epic-folder>/01-*.md` onward - numbered slice docs for implementation phases

Epic definitions now live only inside their folder-based `00-epic.md` files. Do not treat old flat epic pointer files as active sources of truth.

## Generation and workflow navigation

- Final intended generation behavior: [`../02-design-and-features/04-generation-design.md`](../03-design/07-generation.md)
- Final intended evaluation/certification behavior: [`../02-design-and-features/07-evaluation-and-doe-design.md`](retired-evaluation-and-doe-design.md)
- Audited generation-redesign implementation slices: [`epics/03-mcp-generation-and-wrappers/05-generation-redesign/00-group.md`](epics/03-mcp-generation-and-wrappers/05-generation-redesign/00-group.md)
- Approved high-level reliability/optimization roadmap and block-agent handoffs: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/00-group.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/00-group.md)
- Block 1 executable audit/baseline slices: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/01-workflow-audit-and-measurement/00-group.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/01-workflow-audit-and-measurement/00-group.md)
- Block 2 executable architecture/parity slices: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/02-repository-architecture-and-enablement/00-group.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/02-repository-architecture-and-enablement/00-group.md)
- Block 3 executable readiness-diagnosis slices: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/03-readiness-diagnosis-and-architecture/00-group.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/03-readiness-diagnosis-and-architecture/00-group.md)
- Block 4 focused readiness correction/proof: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/04-readiness-correction-and-proof/00-group.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/04-readiness-correction-and-proof/00-group.md)
- Block 5 complete live anchor/re-audit: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/05-complete-live-anchor-and-reaudit/00-group.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/05-complete-live-anchor-and-reaudit/00-group.md)
- Block 6 causal optimization waves: [`epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/06-whole-workflow-optimization/README.md`](epics/03-mcp-generation-and-wrappers/06-workflow-reliability-and-optimization/06-whole-workflow-optimization/README.md) — lane work-package model, not the slice model
- Live implementation/certification state: [`epics/00-current-state.md`](../05-delivery/01-current-state.md)

The active design links describe the coherent final system. The environment, testing, and component quickstarts label
current runnable behavior separately and never turn intended contracts into implementation claims.

## Working rules

- Use the higher-level `README.md` files as the main navigation entry points.
- Inside an epic folder, start with `00-epic.md` before reading slice docs.
- Use `epics/00-current-state.md` to track the active epic, active slice, and next recommended step.
- Keep slice docs focused on execution units rather than broad brainstorming notes.
- When the planning structure changes, update the relevant README navigation files in the same task.
- Epic/slice document shapes and the `## Outcome` convention are owned by
  [`.devin/rules/graphpilot.md`](../../.devin/rules/graphpilot.md#epic-and-slice-document-shapes).

## Live status

Use [`epics/00-current-state.md`](../05-delivery/01-current-state.md) for the active epic, active slice, blockers, and
next work. This README does not duplicate that status.
