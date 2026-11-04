#!/bin/sh
# Second-machine check on macOS / Linux; see scripts/run_portable.py (on Windows: run_windows.bat).
cd "$(dirname "$0")/.." || exit 1
exec python3 scripts/run_portable.py "$@"
