#!/usr/bin/env bash
# Start GraphPilot. Opens the app in your browser; Ctrl+C stops both servers.
# The macOS/Linux twin of dev.bat — mark it executable once with: chmod +x dev.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
  exec ".venv/bin/python" run.py "$@"
fi
exec python3 run.py "$@"
