#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "Launching background search control from base port 8421"
/usr/bin/env python3 "$SCRIPT_DIR/scripts/primitive_queue_control_server.py" --host 127.0.0.1 --port 8421 --open-browser
