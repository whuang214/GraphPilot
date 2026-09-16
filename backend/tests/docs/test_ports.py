"""Every port number agrees with `graphpilot.ports`.

The frontend port was written in five places — the Vite config, two `.env.example` lines,
the Django setting, and a second fallback inside the MCP server — and nothing compared
them. Changing one meant editing three files correctly or the app half-worked: CORS blocks
loudly, but a stale `editUrl` fails **silently**, handing a host a well-formed link to a
port nothing is serving.

So the numbers live in `graphpilot/ports.py` and this compares everything else to it.
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from graphpilot import ports

ROOT = Path(settings.BASE_DIR).parent


class PortConsistencyTests(SimpleTestCase):
    def test_vite_serves_the_dev_frontend_port(self):
        config = (ROOT / "frontend" / "vite.config.ts").read_text(encoding="utf-8")
        found = re.search(r"port:\s*(\d+)", config)

        self.assertIsNotNone(found, "vite.config.ts no longer pins a port")
        self.assertEqual(int(found.group(1)), ports.DEV_FRONTEND_PORT)

    def test_vite_refuses_to_drift(self):
        """`strictPort` is why the other four numbers can be trusted.

        Without it Vite silently moves to the next free port when 5173 is taken, and the
        backend keeps allowing CORS for an origin nobody is serving.
        """
        config = (ROOT / "frontend" / "vite.config.ts").read_text(encoding="utf-8")

        self.assertIn("strictPort: true", config)

    def test_the_frontend_env_points_at_the_dev_backend(self):
        example = (ROOT / "frontend" / ".env.example").read_text(encoding="utf-8")

        self.assertIn(
            f"VITE_API_BASE_URL={ports.origin(ports.DEV_BACKEND_PORT)}", example
        )

    def test_cors_allows_the_dev_frontend(self):
        example = (ROOT / "backend" / ".env.example").read_text(encoding="utf-8")
        line = next(
            l for l in example.splitlines()
            if l.startswith("GRAPHPILOT_CORS_ALLOWED_ORIGINS=")
        )

        self.assertIn(ports.dev_frontend_origin(), line)

    def test_the_shipped_editor_base_url_does_not_count_as_a_pin(self):
        """A template value is not a decision.

        `.env` describes the dev setup, so it names the dev origin like everything else
        in it. Treating that as an explicit pin is what broke this first: every install
        shipped the line, so the resolver never ran and a launcher-only user got a
        well-formed link to a port nothing was serving. Found by running it, not reading
        it — the resolver looked correct.
        """
        example = (ROOT / "backend" / ".env.example").read_text(encoding="utf-8")
        shipped = next(
            line.split("=", 1)[1] for line in example.splitlines()
            if line.startswith("GRAPHPILOT_FRONTEND_BASE_URL=")
        )

        self.assertIn(shipped, ("", ports.dev_frontend_origin()))
        # And the setting layer must agree that this exact value is not a pin.
        self.assertEqual(settings.GRAPHPILOT_FRONTEND_BASE_URL_EXPLICIT, "")

    def test_no_port_literal_survives_outside_the_one_module(self):
        """The five copies are the defect; this is what stops a sixth."""
        offenders = []
        for relative in (
            "backend/mcp_server/server.py",
            "backend/services/shared/editor_origin.py",
            "backend/graphpilot/settings.py",
            "run.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                code = line.split("#")[0]
                if re.search(r"localhost:(5173|8000|5210|8010)", code):
                    offenders.append(f"{relative}:{number}")

        self.assertEqual(offenders, [], "use graphpilot.ports instead of a literal")

    def test_the_launcher_pair_cannot_collide_with_the_dev_pair(self):
        """Including the range each scans into."""
        dev = {ports.DEV_BACKEND_PORT, ports.DEV_FRONTEND_PORT}
        app = set(range(ports.APP_BACKEND_PORT,
                        ports.APP_BACKEND_PORT + ports.PORT_SCAN_RANGE))
        app |= set(range(ports.APP_FRONTEND_PORT,
                         ports.APP_FRONTEND_PORT + ports.PORT_SCAN_RANGE))

        self.assertEqual(dev & app, set())

    def test_the_runtime_file_is_not_committed(self):
        """It records a live process; a checked-in copy would be a lie by definition."""
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(ports.RUNTIME_FILENAME, ignore)

    def test_the_launcher_starts_from_the_shared_defaults(self):
        launcher = (ROOT / "run.py").read_text(encoding="utf-8")

        for name in ("APP_BACKEND_PORT", "APP_FRONTEND_PORT", "RUNTIME_FILENAME"):
            with self.subTest(constant=name):
                self.assertIn(f"ports.{name}", launcher)

    def test_dotenv_never_overrides_the_launchers_environment(self):
        """The launcher's whole design rests on this one default.

        `run.py` hands its children `GRAPHPILOT_CORS_ALLOWED_ORIGINS` and
        `VITE_API_BASE_URL` for the ports it actually claimed, while `backend/.env` still
        names 5173 and `frontend/.env` still names 8000. `load_dotenv()` defaults to
        `override=False`, so the passed values win — verified in a browser: with the dev
        backend down, the launcher's editor loaded a diagram, which it could only have
        done by reaching the launcher's own API and passing its CORS check.

        Adding `override=True` here would silently point the double-clicked app at the
        dev servers and block its own API. Nothing else would fail.
        """
        settings_text = (ROOT / "backend" / "graphpilot" / "settings.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("load_dotenv()", settings_text)
        self.assertNotIn("override=True", settings_text)

    def test_the_launcher_passes_both_overrides_to_the_right_child(self):
        launcher = (ROOT / "run.py").read_text(encoding="utf-8")

        backend_block = launcher.split("backend_env = {")[1].split("}")[0]
        frontend_block = launcher.split("frontend_env = {")[1].split("}")[0]
        self.assertIn("GRAPHPILOT_CORS_ALLOWED_ORIGINS", backend_block)
        self.assertIn("GRAPHPILOT_FRONTEND_BASE_URL", backend_block)
        self.assertIn("VITE_API_BASE_URL", frontend_block)

    def test_the_runtime_contract_is_what_the_launcher_writes(self):
        """Two processes, one file, and no type checker between them."""
        launcher = (ROOT / "run.py").read_text(encoding="utf-8")
        settings_text = (ROOT / "backend" / "graphpilot" / "settings.py").read_text(
            encoding="utf-8"
        )

        self.assertIn('"frontendOrigin"', launcher)
        self.assertIn("'frontendOrigin'", settings_text)
        json.loads('{"frontendOrigin": "http://localhost:5210"}')
