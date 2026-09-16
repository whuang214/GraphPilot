#!/usr/bin/env python3
"""Start GraphPilot — both halves, one window, on ports that never fight the dev servers.

Using GraphPilot used to mean two terminals held open: `manage.py runserver 8000` in one,
`npm run dev` in the other, then browsing to localhost by hand. Close the wrong window and
half the app is gone. That is fine for someone working *on* GraphPilot and hopeless for
the analysts and PMs this is also meant for.

So: double-click `dev.bat` (or run `python run.py`) and the app opens.

**It takes its own ports.** The dev servers own 8000 and 5173; the launcher starts at 8010
and 5210 and scans upward from there. Somebody mid-task with dev servers up can double-click
this without either instance disturbing the other — which is the whole reason for a separate
pair rather than "use 8000 unless it is busy".

Whichever ports it settles on are written to `runtime.json` beside this file, because the
MCP server is started by the IDE and shares no environment with us. Without that file an
agent's `editUrl` would point at a dev server that may not be running. It is deleted on the
way out.

Stdlib only, by design: this is the first thing a new user runs, and it must not require a
dependency to tell them a dependency is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import queue
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))

from graphpilot import ports  # noqa: E402  (path is set immediately above)

RUNTIME_FILE = ROOT / ports.RUNTIME_FILENAME
IS_WINDOWS = platform.system() == "Windows"
VENV_PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


# -- ports --------------------------------------------------------------------------


def _free(port: int) -> bool:
    """True when nothing holds *port*.

    `SO_REUSEADDR` is deliberately **not** set: it would let this bind a port another
    process is already listening on, which is the exact question being asked.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _claim(preferred: int, taken: set[int]) -> int:
    for candidate in range(preferred, preferred + ports.PORT_SCAN_RANGE):
        if candidate not in taken and _free(candidate):
            taken.add(candidate)
            return candidate
    raise SystemExit(
        f"No free port between {preferred} and {preferred + ports.PORT_SCAN_RANGE - 1}. "
        f"Something is holding an unusual number of ports; close it and try again."
    )


# -- preflight ----------------------------------------------------------------------


def _preflight() -> None:
    """Fail with an instruction, never a traceback. This is somebody's first run."""
    problems = []
    if not VENV_PYTHON.is_file():
        problems.append(
            f"No Python environment at {VENV_PYTHON.relative_to(ROOT)}.\n"
            f"    Fix: run  uv venv  then  uv pip install -r requirements.txt"
        )
    if not (ROOT / "frontend" / "node_modules").is_dir():
        problems.append(
            "Frontend dependencies are not installed.\n"
            "    Fix: run  npm install  inside the frontend folder"
        )
    if shutil.which("npm") is None:
        problems.append(
            "npm is not on PATH. Install Node 20.19+ or 22.12+ from https://nodejs.org"
        )
    if problems:
        print("GraphPilot cannot start yet:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}\n", file=sys.stderr)
        raise SystemExit(1)


def _migrate() -> None:
    """Create Django's own SQLite tables. Idempotent, and silent unless it fails."""
    done = subprocess.run(
        [str(VENV_PYTHON), "manage.py", "migrate", "--no-input"],
        cwd=ROOT / "backend", capture_output=True, text=True,
    )
    if done.returncode != 0:
        print(done.stdout + done.stderr, file=sys.stderr)
        raise SystemExit("Database migration failed; GraphPilot did not start.")


# -- child processes ----------------------------------------------------------------


def _spawn(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(
        command, cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )


def _pump(name: str, process: subprocess.Popen, sink: queue.Queue) -> None:
    for line in process.stdout:
        sink.put(f"[{name}] {line.rstrip()}")
    sink.put(f"[{name}] exited with {process.wait()}")


def _wait_for(port: int, timeout: float = 40.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.25)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.25)
    return False


def _speak_utf8() -> None:
    """Let this window print what the child processes actually say.

    Vite's banner contains `➜`, and a Windows console defaults to cp1252, so relaying a
    perfectly healthy startup line killed the launcher with a `UnicodeEncodeError` — the
    app running fine behind a crashed supervisor. `errors="replace"` is the belt: a
    console that still cannot encode something prints a placeholder instead of taking
    both servers down over a decorative arrow.

    `line_buffering` is not incidental either: this is a **log window**, and
    reconfiguring a stream resets its buffering, so without it a piped or redirected
    launcher shows nothing for 8 KB and then everything at once. Someone watching for
    "ready" sees a dead window.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except (AttributeError, OSError, ValueError):
            pass


def _say(line: str) -> None:
    try:
        print(line)
    except (UnicodeEncodeError, OSError):
        print(line.encode("ascii", "replace").decode("ascii"))


def main() -> int:
    _speak_utf8()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backend-port", type=int, default=ports.APP_BACKEND_PORT)
    parser.add_argument("--frontend-port", type=int, default=ports.APP_FRONTEND_PORT)
    parser.add_argument("--no-browser", action="store_true",
                        help="start the servers but do not open a browser")
    args = parser.parse_args()

    _preflight()

    claimed: set[int] = set()
    backend_port = _claim(args.backend_port, claimed)
    frontend_port = _claim(args.frontend_port, claimed)
    frontend_origin = ports.origin(frontend_port)
    backend_origin = ports.origin(backend_port)

    _say(f"GraphPilot -> {frontend_origin}   (api {backend_origin})")
    if backend_port != args.backend_port or frontend_port != args.frontend_port:
        _say("  default ports were busy; using the next free pair")
    _say("  Ctrl+C stops both.\n")

    _migrate()

    # The launcher's own instance is self-consistent: its backend is told its frontend's
    # origin for CORS and for edit links, and its frontend is told where the API is.
    # `127.0.0.1` and `localhost` are distinct origins to a browser, so both are allowed.
    backend_env = {
        **os.environ,
        "GRAPHPILOT_CORS_ALLOWED_ORIGINS": ",".join(
            (frontend_origin, ports.origin(frontend_port, "127.0.0.1"))
        ),
        "GRAPHPILOT_FRONTEND_BASE_URL": frontend_origin,
        "PYTHONUNBUFFERED": "1",
    }
    frontend_env = {**os.environ, "VITE_API_BASE_URL": backend_origin}

    RUNTIME_FILE.write_text(
        json.dumps({"frontendOrigin": frontend_origin,
                    "backendOrigin": backend_origin,
                    "pid": os.getpid()}, indent=2) + "\n",
        encoding="utf-8",
    )

    lines: queue.Queue = queue.Queue()
    children: list[tuple[str, subprocess.Popen]] = []
    try:
        children.append(("api", _spawn(
            [str(VENV_PYTHON), "manage.py", "runserver", str(backend_port), "--noreload"],
            ROOT / "backend", backend_env)))
        # `--strictPort` matters: without it Vite silently moves when the port is taken,
        # and the backend would keep allowing CORS for an origin nobody is serving.
        children.append(("web", _spawn(
            [("npm.cmd" if IS_WINDOWS else "npm"), "run", "dev", "--",
             "--port", str(frontend_port), "--strictPort"],
            ROOT / "frontend", frontend_env)))

        for name, process in children:
            threading.Thread(target=_pump, args=(name, process, lines),
                             daemon=True).start()

        if not args.no_browser and _wait_for(frontend_port):
            webbrowser.open(frontend_origin)

        while any(process.poll() is None for _, process in children):
            try:
                _say(lines.get(timeout=0.3))
            except queue.Empty:
                continue
    except KeyboardInterrupt:
        _say("\nstopping...")
    finally:
        # Order matters. The first version drained the log *before* removing the runtime
        # file, and a crash while printing left the file behind claiming a launcher was
        # up — which would have sent every later `editUrl` to a dead port. Release the
        # claim first; it is the only side effect anyone else can see.
        RUNTIME_FILE.unlink(missing_ok=True)
        for _, process in children:
            if process.poll() is None:
                process.terminate()
        for _, process in children:
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
        while not lines.empty():
            _say(lines.get_nowait())
        _say("stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
