"""Which running GraphPilot an `editUrl` should point at.

A diagram can be edited in two places — the dev server someone started by hand, or the
app they double-clicked — and the MCP server is a **third** process, spawned by the IDE,
that started neither and shares no environment with either. It has to guess, and a wrong
guess is silent: the URL is well-formed, the host clicks it, and nothing is there.

The rule, in priority order:

1. **An explicitly set `GRAPHPILOT_FRONTEND_BASE_URL` always wins.** Someone who states
   an origin means it.
2. **A GraphPilot dev server, if one is actually running.** Somebody with dev servers up
   is working on GraphPilot, and that is the instance they are looking at.
3. **Otherwise the launcher**, whether or not it is up yet — because it is what will be
   running once they double-click, and a link to the app they are about to start beats a
   link to a dev server they never run.

Step 2 is the only one that costs anything, and it is the only one that can be wrong in
an interesting way. **Port 5173 is Vite's default**, so any React project on the machine
could be sitting there; pointing a host at someone else's app would be worse than
pointing at nothing. So the probe is not "is the port open" but "does it answer as
GraphPilot", checked against the signature in `frontend/index.html`.

The probe is a localhost `GET` with a quarter-second budget, cached briefly so a burst of
tool calls pays for it once. Every failure means "not there", never an exception: an
`editUrl` is a convenience, and no diagram operation may fail because a probe did.
"""

from __future__ import annotations

import logging
import time
import urllib.error
import urllib.request
from typing import Optional

from django.conf import settings

from graphpilot import ports

logger = logging.getLogger(__name__)

#: Long enough that a live local server always answers, short enough that a wedged one
#: cannot stall a tool call. Refused connections return far faster than this.
PROBE_TIMEOUT_SECONDS = 0.25

#: A burst of `diagram_create` calls should probe once, while a dev server started
#: mid-session is still noticed promptly.
PROBE_CACHE_SECONDS = 5.0

#: Only the first few KB are read: the signature is in `<head>`, and a dev server can
#: stream a large document.
_PROBE_READ_BYTES = 4096

#: From `frontend/index.html`. Both must appear, so a page merely mentioning the word
#: does not qualify.
_SIGNATURE = ("<title>GraphPilot</title>", "GraphPilot local diagram editor")

_cache: dict[str, tuple[float, bool]] = {}


def _looks_like_graphpilot(origin: str) -> bool:
    """True when *origin* answers with GraphPilot's own index page."""
    now = time.monotonic()
    cached = _cache.get(origin)
    if cached and now - cached[0] < PROBE_CACHE_SECONDS:
        return cached[1]

    found = False
    try:
        with urllib.request.urlopen(origin, timeout=PROBE_TIMEOUT_SECONDS) as response:
            body = response.read(_PROBE_READ_BYTES).decode("utf-8", "replace")
        found = all(mark in body for mark in _SIGNATURE)
    except (urllib.error.URLError, OSError, ValueError):
        found = False        # refused, timed out, or not HTTP: not there.

    _cache[origin] = (now, found)
    return found


def clear_cache() -> None:
    """Forget probe results. For tests, and for a launcher changing state mid-process."""
    _cache.clear()


def launcher_origin() -> Optional[str]:
    """The origin the launcher is using, or would use, if that is discoverable."""
    recorded = getattr(settings, "GRAPHPILOT_RUNTIME_FRONTEND_ORIGIN", None)
    if isinstance(recorded, str) and recorded.strip():
        return recorded.strip().rstrip("/")
    return ports.app_frontend_origin()


def editor_base_url() -> str:
    """Resolve the base URL an `editUrl` should be built on."""
    explicit = getattr(settings, "GRAPHPILOT_FRONTEND_BASE_URL_EXPLICIT", None)
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip().rstrip("/")

    dev = ports.dev_frontend_origin()
    if _looks_like_graphpilot(dev):
        return dev

    return launcher_origin() or dev
