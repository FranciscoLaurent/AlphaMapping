#!/bin/bash
#
# AlphaMapping Stop Script (Linux/macOS)
# Stops all AlphaMapping services.
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

info "Stopping AlphaMapping Services..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

STOPPED=0

# Stop backend using PID file
if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/.backend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null
        info "Stopped Backend (PID: $PID)"
        STOPPED=$((STOPPED + 1))
    fi
    rm -f "$PROJECT_ROOT/.backend.pid"
fi

# Stop frontend using PID file
if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/.frontend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null
        info "Stopped Frontend (PID: $PID)"
        STOPPED=$((STOPPED + 1))
    fi
    rm -f "$PROJECT_ROOT/.frontend.pid"
fi

# Also kill any uvicorn/http.server processes related to this project
pkill -f "uvicorn app.main:app" 2>/dev/null && STOPPED=$((STOPPED + 1))
pkill -f "http.server 3000" 2>/dev/null && STOPPED=$((STOPPED + 1))

if [ $STOPPED -gt 0 ]; then
    success "AlphaMapping stopped successfully"
else
    warn "No AlphaMapping processes found running"
fi

echo ""
info "To restart, run: ./scripts/run.sh"
