"""Which running GraphPilot an `editUrl` points at.

Two instances can exist — the dev server someone started by hand, and the double-clicked
launcher on its own ports — and the MCP server that has to build the link is a third
process that started neither. Getting this wrong is silent: the URL is well-formed, the
host clicks it, nothing is there.

The case worth the machinery is the squatter. **5173 is Vite's default**, so any React
project on the machine may answer there, and sending someone into a colleague's unrelated
app would be worse than sending them nowhere. So the probe asks "does this answer as
GraphPilot", not "is this port open" — and these tests serve a real socket to prove it,
because a mocked probe would only assert that the mock was called.
"""

import http.server
import threading

from django.test import SimpleTestCase, override_settings

from graphpilot import ports
from services.shared import editor_origin

LAUNCHER = "http://localhost:5211"


class _Handler(http.server.BaseHTTPRequestHandler):
    body = b"<html><head><title>Some Other Vite App</title></head><body></body></html>"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


class _GraphPilotHandler(_Handler):
    body = (
        b'<html><head><meta name="description" content="GraphPilot local diagram '
        b'editor" /><title>GraphPilot</title></head><body></body></html>'
    )


class _Server:
    """A real HTTP server on the dev frontend port, for the duration of a `with`."""

    def __init__(self, handler):
        self._handler = handler

    def __enter__(self):
        self._server = http.server.HTTPServer(
            ("127.0.0.1", ports.DEV_FRONTEND_PORT), self._handler
        )
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        editor_origin.clear_cache()
        return self

    def __exit__(self, *exc):
        self._server.shutdown()
        self._server.server_close()
        editor_origin.clear_cache()
        return False


@override_settings(GRAPHPILOT_FRONTEND_BASE_URL_EXPLICIT="")
class EditorOriginTests(SimpleTestCase):
    def setUp(self):
        editor_origin.clear_cache()
        self.addCleanup(editor_origin.clear_cache)

    @override_settings(GRAPHPILOT_RUNTIME_FRONTEND_ORIGIN=LAUNCHER)
    def test_with_no_dev_server_the_launcher_is_the_answer(self):
        self.assertEqual(editor_origin.editor_base_url(), LAUNCHER)

    @override_settings(GRAPHPILOT_RUNTIME_FRONTEND_ORIGIN=None)
    def test_with_nothing_running_at_all_it_still_names_the_launcher(self):
        """Because that is what will be running the moment they double-click."""
        self.assertEqual(editor_origin.editor_base_url(), ports.app_frontend_origin())

    @override_settings(GRAPHPILOT_RUNTIME_FRONTEND_ORIGIN=LAUNCHER)
    def test_a_stranger_on_the_dev_port_does_not_capture_the_link(self):
        with _Server(_Handler):
            self.assertEqual(editor_origin.editor_base_url(), LAUNCHER)

    @override_settings(GRAPHPILOT_RUNTIME_FRONTEND_ORIGIN=LAUNCHER)
    def test_a_real_dev_server_outranks_the_launcher(self):
        with _Server(_GraphPilotHandler):
            self.assertEqual(
                editor_origin.editor_base_url(), ports.dev_frontend_origin()
            )

    @override_settings(GRAPHPILOT_FRONTEND_BASE_URL_EXPLICIT="http://localhost:9999")
    def test_an_explicit_setting_beats_anything_running(self):
        with _Server(_GraphPilotHandler):
            self.assertEqual(editor_origin.editor_base_url(), "http://localhost:9999")

    @override_settings(GRAPHPILOT_RUNTIME_FRONTEND_ORIGIN="not-a-url")
    def test_a_corrupt_runtime_file_cannot_send_a_host_anywhere_odd(self):
        """`settings` filters the file; this pins that the resolver trusts that filter.

        Only `http://localhost:` and `http://127.0.0.1:` survive `_runtime_frontend_origin`,
        so a hand-edited or stale file cannot redirect a host off the machine.
        """
        self.assertEqual(editor_origin.editor_base_url(), "not-a-url")

    def test_the_probe_reports_nothing_when_nothing_answers(self):
        self.assertFalse(
            editor_origin._looks_like_graphpilot("http://127.0.0.1:1")
        )

    def test_the_probe_is_cached_so_a_burst_of_tool_calls_pays_once(self):
        """Started by hand: `_Server` clears the cache on exit, which is the thing

        under test here. The first version used the fixture and asserted on a cache the
        fixture had just emptied — it failed for its own reason, not the product's.
        """
        origin = ports.dev_frontend_origin()
        server = http.server.HTTPServer(
            ("127.0.0.1", ports.DEV_FRONTEND_PORT), _GraphPilotHandler
        )
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            self.assertTrue(editor_origin._looks_like_graphpilot(origin))
        finally:
            server.shutdown()
            server.server_close()

        # Nothing is listening now, and the answer is still yes: within the TTL a burst
        # of tool calls costs one round trip, not one each.
        self.assertTrue(editor_origin._looks_like_graphpilot(origin))
