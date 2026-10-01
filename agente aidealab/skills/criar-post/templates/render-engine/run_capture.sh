#!/bin/bash
# Wrapper: points capture.py at the sandbox's pre-installed Chromium (revision
# mismatch between pip playwright's expected bundled browser and what's on disk).
export CAPTURE_CHROMIUM_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
exec python3 "$(dirname "$0")/capture.py" "$@"
