# AGENTS.md

> **Agent entry point.** If you are an AI coding agent, **start here**, then follow the read
> order below. This is the portable, tool-agnostic front door. To avoid drift, each topic has a
> **single owner** (see *Source of truth per topic* below) — other docs link to the owner rather
> than restating it.

## What GraphPilot is

An internal, **local-first** AI diagramming tool with two entry points over one shared core:
IDE-driven generate / render / validate via **MCP**, and browser-based editing / export via a
**React** UI — both read/write the same local `<name>.gp.json`. Django + DRF backend, React 19
+ React Flow frontend. MVP is local-first, database-free, no auth. MVP diagram types:
`activity_diagram`, `use_case_diagram`, `bdd_diagram`. The element vocabulary is a shared **element catalog** with bounded per-type core authoring/generation profiles and retained compatibility entries, drawn by one `gpNode` render family on the canvas and mirrored by the SVG export. The intended design supports both direct
prompt generation and a local evidence-manifest → request-context → readiness → grounded-generation path;
runtime delivery status stays in the current-state board.

## Source of truth per topic

Each topic has **one** owner; everything else links to it (don't restate → don't drift).

| Topic | Canonical owner | Others |
| --- | --- | --- |
| Live delivery status | `docs/05-delivery/01-current-state.md` | link only; never restate a status |
| Completed work | `docs/07-history/` (frozen) and git history | never updated after a program closes |
| Setup / run / verify commands | **this file** (below) — the few you need most | `docs/04-development/05-command-reference.md` has **every** command and flag, guarded by a test; `README.md` has the human quickstart |
| Always-on agent rules (the MUSTs, the Windows traps, verification discipline) | **this file** | portable across development environments |
| Delivery workflow (packages, tiers, states, file caps, rigs, subagents) | `docs/04-development/06-delivery-workflow.md` | read when a program starts, not every turn |
| Human quickstart / pitch / repo layout | `README.md` | — |
| Final intended design + behavior | `docs/03-design/**` | no runtime-status prose; slice docs implement and defer to it |
| Decision log | `docs/05-delivery/04-decisions.md` | appended over time; not design canon |
| Per-type notation | `docs/03-design/02-diagram-schemas/` | keep canvas ↔ SVG export in parity |
| Judging whether a diagram is any good — the review gallery, the single-host audit prompt, the nine frozen corpus prompts | `docs/04-development/04-reviewing-diagrams.md` | the `corpus-run` skill automates its commands, but the prompts live there |
| The draft contract, materialization, assurance, and provenance | `docs/03-design/01-generation/` | architecture/MCP/testing owners link to detail |
| MCP tool and host-prompt contracts | `docs/02-architecture/01-mcp-tools/` | runtime status belongs to delivery docs |
| Shared backend service names and `OperationProblem` contract | `docs/02-architecture/03-backend.md` | MCP/API owners define only their transport mapping |

## Read order (do this first)

1. `README.md` — quickstart, repo layout, integration surface (MCP tools + REST routes)
2. `docs/README.md` — documentation index; `docs/` is the **source of truth**
3. `docs/05-delivery/01-current-state.md` — **live status: what's done / what's next**
4. `docs/05-delivery/04-decisions.md` — active design decisions
5. The nearest `README.md` (`backend/`, `frontend/`, or the relevant `docs/**` folder) **before editing there**

## Setup & run

- **Backend** (from repo root): `uv venv` → `uv pip install -r requirements.txt` → `cd backend` → `copy .env.example .env` → `uv run python manage.py migrate` → `uv run python manage.py runserver 8000` (no `activate` needed — `uv run` auto-selects the venv)
- **Frontend**: `cd frontend` → `npm install` → `npm run dev` (http://localhost:5173)
- **Both at once, for someone who just wants the app:** `python run.py` (or double-click `dev.bat`). It claims its **own** ports — `8010`/`5210`, scanning up if busy — so it never collides with the dev servers above, and writes `runtime.json` while it runs. **Every port number lives in `backend/graphpilot/ports.py`**; the frontend port used to be written in five places with nothing comparing them, and a stale one makes `editUrl` a well-formed link to nothing. `GRAPHPILOT_FRONTEND_BASE_URL` now ships **empty on purpose** — empty lets `services/shared/editor_origin.py` resolve the answer at call time (a running GraphPilot dev server, else the launcher), which the MCP server cannot do any other way since your IDE starts it.
- **Windows/PowerShell:** run Python via `uv run python …` (auto-selects the venv); the venv interpreter itself is `.venv\Scripts\python.exe` if a tool needs the direct path. Use `curl.exe --ssl-no-revoke` for HTTPS fetches. PowerShell has no heredoc — write long commit messages to a temp file and use `git commit -F`. **Write that file with Python, not `Out-File`**: in PS 5.1 `Out-File -Encoding utf8` prepends a BOM and `git commit -F` puts those three bytes at the front of the subject line, so `git log` shows an invisible character before the type prefix. This has happened; recover with `--amend -F` after rewriting the file properly.
- **Never edit a tracked file with PowerShell `Set-Content` / `Out-File`.** In Windows PowerShell 5.1 `-Encoding UTF8` writes a **BOM**, and a `Get-Content`/`Set-Content` round-trip mangles every non-ASCII character — `—` becomes `â€"`. This corrupted source and docs three times in one session before being caught. Use the editing tools, or a short Python script, both of which round-trip UTF-8 correctly. To check: `git diff` and look for non-ASCII on lines you did not intend to touch.
- **Worktree roots must be ≤44 characters.** The longest tracked path is 214 chars, so a longer root breaks the 260-char Windows limit and silently produces a partial checkout. `…\Projects\GraphPilot` is exactly 44; keep new worktrees short (e.g. `…\Projects\GP-LB2`).
- **No provider to configure.** GraphPilot calls no model — a host authors the draft and the backend materializes it deterministically. There is no endpoint, no key, and `openai` is not a dependency. Full env reference: `docs/04-development/01-environment.md`.

## Verify before calling a change done

- **Backend:** `cd backend; uv run python manage.py test --parallel 24` — around 690 tests in under ten seconds, fully offline. **Run this before calling a change done.** There is no inner-loop/full-gate split: the provider pipeline that made the suite slow is gone, nothing is tagged `slow`, and a suite this fast does not need one. (The count is approximate on purpose; an exact one here goes stale every commit.)
- The suite is CPU-bound and parallel-safe. Django distributes by `TestCase` class, so a large class is one serialized bucket no matter how many workers are free — split by concern rather than growing a class. Drop `--parallel` only when a failure's traceback is hard to attribute; the parallel runner reports errors as a `PicklingError` that hides the real cause.
- **Frontend:** `cd frontend; npm run verify` (lint + build + test + e2e), or individually `npm run lint` / `npm run test` / `npx tsc --noEmit -p tsconfig.app.json`. **`npm install` does not fetch browsers** — the e2e leg needs a one-time `npx playwright install chromium`, because Playwright keeps them in a machine-level cache outside `node_modules`. Without it `verify` fails at the last step on a fresh machine.
- **Look at the diagrams after any layout or rendering change.** `cd backend; uv run python manage.py review_gallery --regen eval` rebuilds every example from its stored draft and serves one page at `http://127.0.0.1:8123/` — 54 cards: 36 answers, 9 host-generated, 3 training, and 6 `edited` before/after pairs showing that changing a diagram does not destroy the arrangement somebody made. Plain `review_gallery` re-renders what is on disk; `--regen generated` re-syncs the corpus from the test repositories. Each card carries its own badges — valid, structural, **`N lost`** (the draft said something the diagram does not), legible, miscited, provenance — so the page names the diagram to open rather than reporting a total. **Always pass the URL on to the user.** Numbers do not catch a diagram that is legible but wrong. Every flag: [`05-command-reference.md`](docs/04-development/05-command-reference.md).
- **After changing the authoring contract, the workflow text, or the draft schema, run a single-host audit** — one agent, minutes, and it catches what the suite cannot: a rule the tools enforce and explain nowhere. The prompt is in [`docs/04-development/04-reviewing-diagrams.md`](docs/04-development/04-reviewing-diagrams.md), which also owns the review gallery and the nine frozen corpus prompts. Do not improvise either prompt.
- **Commit each coherent slice after its required checks pass.** The user granted standing permission on 2026-07-15, so no separate pre-commit confirmation is required; report exact PowerShell verification commands/results and never push without an explicit request.

## How to work here (conventions summary)

This file owns the portable working conventions:

- **Docs are part of the change.** Update the nearest relevant doc in the **same** change (README-first); when a delivery doc and a design doc disagree, the **design doc wins**.
- **Docs split by lifetime.** `docs/01-product .. 05-delivery` describe the system **as it is** and must match code. `docs/07-history/` is frozen and never updated. Never mix them.
- **Status:** live status goes only in `docs/05-delivery/01-current-state.md` (a lean board); log decisions in `docs/05-delivery/04-decisions.md`.
- **One document model.** Work is organised into **packages** listed in one `plan.md` per program. A package produces at most one document, and only when it changes a contract or spends a provider call — most work is code, tests, and a commit. Ceremony scales with what a mistake costs, not with how important the work feels.
- **Parity:** keep the canvas (`frontend/src/editor/canvas/customNodes.tsx`) and the SVG export (`backend/services/diagrams/rendering/diagram_render_service.py`) in parity; this includes BDD primary stereotype headings, Composition markers, and the Note dog-ear. Per-type notation lives in `docs/03-design/02-diagram-schemas/`.
- Prefer **minimal, pattern-matching** changes; reuse existing utilities; don't add dependencies casually; never commit secrets or edit `.env`.
- Dot folders, including legacy `.devin/` configuration and skills, are local-only and excluded from Git. Real `.env` and `.env.*` files stay local; only non-secret `.env.example`, `.env.sample`, and `.env.template` files may be shared. Do not read or modify real environment files. Keep shared instructions in this file and `docs/`.
- Never discard uncommitted work to clean up an experiment, bypass hooks, or rewrite history without explicit authorization.

## Keep this file current

`AGENTS.md` owns the agent read order + the terse setup/run/verify above. If those change, update
this file in the same change. For everything else, update the **owner** named in *Source of truth
per topic* — this file links, it does not duplicate.
