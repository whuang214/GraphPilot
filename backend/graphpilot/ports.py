"""The ports GraphPilot uses, in one place, importable without Django.

There are two ways to run this app and they must not fight over a socket:

* **Dev servers** — `manage.py runserver 8000` and `npm run dev` on 5173, started by
  hand in two terminals while working on GraphPilot itself.
* **The launcher** — `run.py` (or a double-clicked `dev.bat`), for someone who just
  wants to use the app. It takes its own pair so double-clicking while dev servers are
  up does not fail, and neither instance disturbs the other.

`run.py` imports this module before Django exists, so it must stay dependency-free and
must not import anything from the wider project.

Every other copy of a port number is a place the two can disagree. The frontend port
alone was written in five: the Vite config, two `.env.example` lines, the Django
setting, and a second fallback inside the MCP server. `tests/docs/test_ports.py` keeps
them agreeing with this file.
"""

#: Where the hand-started dev servers live. `frontend/vite.config.ts` pins the frontend
#: one with `strictPort`, so Vite fails loudly rather than drifting to another port and
#: leaving the backend's CORS and edit URLs pointing somewhere nothing is listening.
DEV_BACKEND_PORT = 8000
DEV_FRONTEND_PORT = 5173

#: Where the launcher starts looking. Deliberately clear of the dev pair *and* of the
#: ports either would drift onto, so "is the launcher up?" is never confused with "is
#: the dev server up?".
APP_BACKEND_PORT = 8010
APP_FRONTEND_PORT = 5210

#: How far `run.py` scans upward when its own defaults are taken — enough for several
#: launchers at once, small enough that a wedged machine fails rather than silently
#: landing somewhere unrecognisable.
PORT_SCAN_RANGE = 20

#: Written by the launcher into the storage root while it runs, so a *separate* process
#: — the IDE-spawned MCP server — can discover which port the app actually got. Removed
#: on shutdown.
RUNTIME_FILENAME = "runtime.json"


def origin(port: int, host: str = "localhost") -> str:
    """The origin string used for CORS entries and for the editor base URL."""
    return f"http://{host}:{port}"


def dev_frontend_origin() -> str:
    return origin(DEV_FRONTEND_PORT)


def app_frontend_origin(port: int | None = None) -> str:
    return origin(port if port is not None else APP_FRONTEND_PORT)
