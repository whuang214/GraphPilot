# GraphPilot Documentation

The single front door. Everything active is at most two clicks from here.

Folders are numbered in reading order: `01`–`05` are the active set and describe the
intended system; `06`–`07` are not active. Inside a folder, subfolders take the leading
numbers because they sort first.

Implementation status lives only on the
[board](05-delivery/01-current-state.md) — a design doc may describe a contract the code
has not reached yet, and the board says which.

| Question | Go to |
| --- | --- |
| What does the system do, and where does its data come from? | [`01-generation/README.md`](03-design/01-generation/README.md) |
| What is being worked on right now? | [`01-current-state.md`](05-delivery/01-current-state.md) |
| How do I set up and run it? | [`01-environment.md`](04-development/01-environment.md) |
| How do I tell whether a diagram is any good? | [`04-reviewing-diagrams.md`](04-development/04-reviewing-diagrams.md) |
| Why is it built this way? | [`04-decisions.md`](05-delivery/04-decisions.md) |

## Active authority

These describe the system **as it is**. They must match the code.

### `01-product/` — what and why

- [`01-overview.md`](01-product/01-overview.md) — what GraphPilot is
- [`02-user-scenarios.md`](01-product/02-user-scenarios.md)
- [`03-requirements.md`](01-product/03-requirements.md)

### `02-architecture/` — how it is built

- [`01-mcp-tools/`](02-architecture/01-mcp-tools/README.md) — tool and host-prompt contracts
- [`02-system-design.md`](02-architecture/02-system-design.md) — the whole shape
- [`03-backend.md`](02-architecture/03-backend.md) — services, `OperationProblem` contract
- [`04-frontend.md`](02-architecture/04-frontend.md)
- [`05-api-routes.md`](02-architecture/05-api-routes.md)

### `03-design/` — per-feature contracts

- [`01-generation/`](03-design/01-generation/README.md) — **the draft contract, materialization, and lifecycle**
- [`02-diagram-schemas/`](03-design/02-diagram-schemas/README.md) — canonical JSON and per-type notation
- [`03-validation/`](03-design/03-validation/README.md) · [`04-rendering.md`](03-design/04-rendering.md)
- [`05-edit/`](03-design/05-edit/README.md) — **editing a saved diagram**: the draft round trip, field classes, geometry
- [`06-editor-ui.md`](03-design/06-editor-ui.md)

### `04-development/` — how to work on it

- [`01-environment.md`](04-development/01-environment.md) — setup, run, env vars
- [`02-testing-strategy.md`](04-development/02-testing-strategy.md) — what the automated suite proves
- [`03-deployment-options.md`](04-development/03-deployment-options.md)
- [`04-reviewing-diagrams.md`](04-development/04-reviewing-diagrams.md) — the review gallery, and how to re-run the corpus. **Owns the nine frozen prompts**
- [`05-command-reference.md`](04-development/05-command-reference.md) — every command and flag, in one place
- [`06-delivery-workflow.md`](04-development/06-delivery-workflow.md) — packages, ceremony tiers, file caps, rig lifecycle

### `05-delivery/` — what is in flight, and the running record

- [`01-current-state.md`](05-delivery/01-current-state.md) — **the only live-status document**
- [`02-backlog.md`](05-delivery/02-backlog.md)
- [`03-repository-restructure-plan.md`](05-delivery/03-repository-restructure-plan.md) — active program
- [`04-decisions.md`](05-delivery/04-decisions.md) — the decision log; appended over time, not design canon

## Not active

- [`06-research/`](06-research/) — investigation records
- [`07-history/`](07-history/README.md) — completed work, frozen, never updated

## Conventions

One owner per topic; everything else links rather than restating. Active documents are
present tense and describe the intended system — implementation status lives only in
[`05-delivery/01-current-state.md`](05-delivery/01-current-state.md). The agent entry
point is `AGENTS.md` at the repository root; how work is organised is
[`04-development/06-delivery-workflow.md`](04-development/06-delivery-workflow.md), and
[`AGENTS.md`](../AGENTS.md) holds the portable working rules. Local tooling folders,
including the retired `.devin/` environment, are excluded from Git.
