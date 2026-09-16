# Command reference

Every command a person actually runs, with each flag and what it means.

`AGENTS.md` has the two or three you need most, inline, where an agent will trip over them.
This is the whole set, and it is the only place that has ever had all of it — `a5.8` added
it because the fragments were spread across `AGENTS.md`, three `README.md` files and two
design documents, and no two agreed on the flags.

Run backend commands from `backend/`, frontend commands from `frontend/`.

---

## Backend

### Setup

```powershell
uv venv                              # from the repository root
uv pip install -r requirements.txt
cd backend
copy .env.example .env
uv run python manage.py migrate
```

`uv run` selects the virtual environment itself, so there is no `activate` step. If a tool
needs the interpreter path directly it is `.venv\Scripts\python.exe`.

### Run

| Command | What it does |
| --- | --- |
| `uv run python manage.py runserver 8000` | The REST API the browser editor talks to |
| `uv run python mcp_server/server.py` | The MCP server an IDE host connects to |

### Test

| Command | When |
| --- | --- |
| `uv run python manage.py test --parallel 24` | **The gate.** Run before calling a change done |
| `uv run python manage.py test tests.drafts --parallel 1` | One area, serially, when a traceback is hard to attribute |

The suite is CPU-bound and parallel-safe. Django distributes by `TestCase` class, so a
large class is one serialized bucket however many workers are free — split by concern
rather than growing a class. The parallel runner reports an error as a `PicklingError`
that hides the real cause, which is the only reason to drop `--parallel`.

### Look at the diagrams

**After any layout, rendering or notation change.** Numbers do not catch a diagram that is
legible and wrong.

| Command | What it does |
| --- | --- |
| `uv run python manage.py review_gallery` | Serves the page already on disk at `http://127.0.0.1:8123/` |
| `uv run python manage.py review_gallery --regen eval` | **Rebuilds every example from its stored draft**, through the real pipeline, then serves |
| `uv run python manage.py review_gallery --regen edited` | **Replays every edit scenario** — create, arrange, read, edit, update — and rewrites both halves of each before/after pair |
| `uv run python manage.py review_gallery --regen generated` | Re-syncs the nine host diagrams out of the corpus repositories |
| `uv run python manage.py review_gallery --regen all` | Both |
| `uv run python manage.py render_example_gallery --no-open` | Builds without serving. What the tests call |

| Flag | Applies to | Meaning |
| --- | --- | --- |
| `--regen` | both | `eval`, `generated`, or `all`. Without it you are looking at a file that parses, which is a much weaker claim than a diagram the current code produces |
| `--port` | `review_gallery` | Serve somewhere other than 8123 |
| `--no-open` | both | Do not launch a browser |
| `--types` | `render_example_gallery` | Restrict to given diagram types |
| `--pools` | `render_example_gallery` | Restrict to `answers`, `generated` or `training` |
| `--out` | `render_example_gallery` | Write the page somewhere other than `review_galleries/<timestamp>/` |
| `--corpus` | `render_example_gallery` | Where the corpus repositories are, for `--regen generated` |
| `--keep` | `render_example_gallery` | Keep older gallery folders instead of pruning them |

**Always give the URL to whoever asked.** An agent reporting a number about a picture is
not the same as a person seeing it — that is a rule, not a nicety.

---

## Running the app

| Command | What it does |
| --- | --- |
| `python run.py` | **Start both halves in one window.** Its own ports (`8010`/`5210`, scanning up if busy), browser opened, Ctrl+C stops both. Double-click `dev.bat` / `./dev.sh` for the same thing |
| `python run.py --no-browser` | As above, without opening a browser |
| `python run.py --backend-port N --frontend-port N` | Start the scan somewhere else |

The launcher writes `runtime.json` at the repo root while it runs, so the IDE-spawned MCP
server can point `editUrl` at the app that is actually up. It is removed on shutdown.

---

## Frontend

| Command | What it does |
| --- | --- |
| `npm install` | Once. **Does not fetch browsers** — see below |
| `npx playwright install chromium` | Once, and only if you will run `e2e`. Playwright keeps browsers in a machine-level cache outside `node_modules`, so `npm install` cannot have got them; without this, `e2e` fails with `Executable doesn't exist` |
| `npm run dev` | The editor at `http://localhost:5173` |
| `npm run verify` | **The gate:** `lint && build && test && e2e`, in that order |
| `npm run lint` | `oxlint`, on its own |
| `npm run build` | `tsc -b && vite build` — the typecheck and the production bundle |
| `npm run test` | `vitest run` — unit tests on their own |
| `npm run e2e` | `playwright test` — the end-to-end suite, the last leg of `verify` |
| `npm run preview` | Serve an already-built bundle |
| `npx tsc --noEmit -p tsconfig.app.json` | Types only, which `npm run lint` does not check |

Using GraphPilot needs none of this — `npm install` and `npm run dev` are enough. The
rest is for changing it.

---

## Configuration

`backend/.env`, copied from `.env.example`. Full reference in
[`01-environment.md`](01-environment.md).

The MCP server needs no environment of its own: every tool takes `workspaceDir` as an
argument, so which repository is being diagrammed is a property of the call.

---

## Things that are not commands

Two pieces of work here cannot be automated, and looking for a command is the wrong move:

- **A corpus run** needs three cold agents reading three real applications. A diagram is
  authored by something that has read the source and decided what it means, so there is no
  way to fake it that measures anything. The procedure is
  [`04-reviewing-diagrams.md`](04-reviewing-diagrams.md).
- **Judging whether a diagram is correct** needs a person looking at it, against
  `_truth/<repo>.md`. The gallery narrows what you have to look at; it cannot do the
  looking.

---

## Windows notes

- **Never edit a tracked file with PowerShell `Set-Content` or `Out-File`.** In Windows
  PowerShell 5.1, `-Encoding UTF8` writes a BOM, and a `Get-Content`/`Set-Content`
  round-trip mangles every non-ASCII character. `tests/docs/test_source_encoding.py` fails
  when it happens, which is how the one BOM in the repository was found — and how a second
  was caught ten minutes after that guard was written.
- PowerShell has no heredoc. Write a long commit message to a file and use `git commit -F`.
- Use `curl.exe --ssl-no-revoke` for HTTPS fetches.
- **Worktree roots must be 44 characters or fewer.** The longest tracked path is 214, so a
  longer root breaks the 260-character limit and silently produces a partial checkout.
