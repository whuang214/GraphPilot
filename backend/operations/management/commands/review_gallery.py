"""Serve the review galleries over HTTP, and say when they are out of date.

`render_example_gallery` draws the pages. This looks at them.

Splitting the two matters for one reason: **re-rendering and reviewing are different
acts**. Re-rendering answers "what does the code draw now"; reviewing answers "is that
right". Bundling them meant every look cost a rebuild, and the only way to see a page
twice was to build it twice.

Served rather than opened as `file://` because a served page behaves like a page — links
between the two galleries work, reloads work, and the browser does not treat every asset
as a cross-origin local file.

The risk of serving something already rendered is reviewing a stale page after changing
the code, which is the thing the auto-delete was guarding against. So the page is stamped
with the commit it was built at, and this reports loudly when that is not the commit you
are on.
"""

from __future__ import annotations

import functools
import http.server
import re
import socket
import socketserver
import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from operations.management.commands.render_example_gallery import REGEN_CHOICES

_STAMPED_COMMIT = re.compile(r"commit ([0-9a-f]{7,40})")


class Command(BaseCommand):
    help = "Serve the review gallery in a browser; --regen rebuilds the examples first."

    def add_arguments(self, parser):
        parser.add_argument(
            "--regen",
            choices=REGEN_CHOICES,
            default="",
            help="rebuild the examples and the page before serving. `eval` rematerializes "
                 "the answers and training examples from their drafts; `generated` pulls "
                 "the newest host drafts out of the corpus repositories; `all` does both. "
                 "Without it the page already on disk is served as it is",
        )
        parser.add_argument("--port", type=int, default=8123, help="port to serve on")
        parser.add_argument("--no-open", dest="open_browser", action="store_false",
                            help="serve without opening a browser")
        parser.set_defaults(open_browser=True)

    def handle(self, *args, **opts):
        root = Path(settings.BASE_DIR) / "review_galleries"

        # Claim the port before anything is rebuilt. `--regen` deletes the previous run,
        # so a bind that fails *after* it leaves a reviewer with no page at all and an
        # older server still holding the port, serving the directory that was just
        # removed. That is a 404 for someone who did nothing wrong, and it is what
        # happened: five orphaned servers had stacked up on 8123 across one session.
        _require_free_port(opts["port"])

        if opts["regen"]:
            call_command("render_example_gallery", "--regen", opts["regen"],
                         "--no-open", stdout=self.stdout)
        elif not _newest(root):
            self.stdout.write("No gallery on disk yet — rendering one.")
            call_command("render_example_gallery", "--no-open", stdout=self.stdout)

        self._report_staleness(root)

        # Serve the run itself, not the folder of runs: `/` should be the gallery rather
        # than a directory listing a reviewer has to click through.
        run = _newest(root)
        if run is None:
            raise CommandError(
                f"No gallery under {root}. Run with --render to build one."
            )
        url = f"http://127.0.0.1:{opts['port']}/"
        handler = functools.partial(_QuietHandler, directory=str(run))
        try:
            server = _Reusable(("127.0.0.1", opts["port"]), handler)
        except OSError as error:
            raise CommandError(
                f"Could not bind port {opts['port']} ({error}). Something is already "
                f"serving there — try --port."
            ) from error

        self.stdout.write(self.style.SUCCESS(f"Serving the review gallery at {url}"))
        self.stdout.write("  Ctrl+C to stop.")
        if opts["open_browser"]:
            threading.Timer(0.4, webbrowser.open, args=(url,)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write("\nStopped.")
        finally:
            server.server_close()

    def _report_staleness(self, root: Path) -> None:
        """A page built before your last commit is a page that can mislead you."""
        run = _newest(root)
        if run is None:
            return
        # The stylesheet is inlined ahead of the header, so a window over the start of the
        # file misses the stamp entirely and the page reads as "unknown".
        match = _STAMPED_COMMIT.search((run / "index.html").read_text(encoding="utf-8"))
        built_at = match.group(1) if match else "?"
        head = _git("rev-parse", "--short", "HEAD")
        if head and built_at not in {head, "?"} and not head.startswith(built_at):
            self.stdout.write(self.style.WARNING(
                f"  built at {built_at}, you are on {head} — "
                f"re-run with --regen eval to see what the code draws now"
            ))
        else:
            self.stdout.write(f"  current ({built_at})")


def _newest(root: Path) -> Optional[Path]:
    """The most recent run, or None. Runs are named by timestamp, so sorting is enough."""
    if not root.is_dir():
        return None
    runs = sorted(p for p in root.iterdir() if p.is_dir() and (p / "index.html").exists())
    return runs[-1] if runs else None


def _git(*args) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=settings.BASE_DIR, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _require_free_port(port: int) -> None:
    """Fail before any work if nothing can be served afterwards.

    Probed **without** ``SO_REUSEADDR`` deliberately. `_Reusable` sets it so a restart is
    not blocked by ``TIME_WAIT``, which is right on Unix — but on Windows that same option
    lets a second process bind a port another process is actively listening on. Both then
    "serve", one of them wins each request, and neither is obviously wrong. A plain probe
    is the only thing that answers "is somebody already there?" on both platforms.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as error:
            raise CommandError(
                f"Port {port} is already in use ({error.strerror or error}). An earlier "
                f"review_gallery is probably still running — stop it, or pass --port. "
                f"Nothing was rebuilt, so the gallery you already had is untouched."
            ) from error


class _Reusable(socketserver.TCPServer):
    allow_reuse_address = True


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    """A request line per SVG is noise when a page holds forty of them."""

    def log_message(self, fmt, *args):  # noqa: A003 - base class name
        pass
