#!/bin/bash
#
# AlphaMapping Restart Script (Linux/macOS)
# Restarts all AlphaMapping services.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] Restarting AlphaMapping..."

# Stop existing services
"$SCRIPT_DIR/stop.sh"

# Wait a moment
sleep 1

# Start services
"$SCRIPT_DIR/run.sh"
