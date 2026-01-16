#!/bin/bash
#
# AlphaMapping Startup Script (Linux/macOS)
# Automates the setup and execution of the AlphaMapping system.
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info() { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

info "Initializing AlphaMapping System..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 1. Check Python Environment
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    error "Python is not installed. Please install Python 3.8+."
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
info "Detected Python: $PYTHON_VERSION"

# 2. Setup Backend
info "Setting up Backend..."
cd "$PROJECT_ROOT/backend"

# Check/Create Virtual Environment
if [ ! -d "venv" ]; then
    info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate Virtual Environment
source venv/bin/activate

# Install Dependencies
info "Installing dependencies..."
pip install -r requirements.txt -q

# Environment Config
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        warn "Created .env from template. Please update backend/.env with your API keys!"
    else
        warn ".env.example not found!"
    fi
fi

# Create necessary directories
info "Setting up data directories..."
DATA_DIR="$PROJECT_ROOT/data"
REPORTS_DIR="$DATA_DIR/reports"

mkdir -p "$DATA_DIR" && success "Data directory ready"
mkdir -p "$REPORTS_DIR" && success "Reports directory ready"

# 3. Start Backend Service
info "Starting Backend API (Port 8000)..."
cd "$PROJECT_ROOT/backend"
nohup $PYTHON_CMD -m uvicorn app.main:app --reload --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"

# 4. Start Frontend Service
info "Starting Frontend Service (Port 3000)..."
cd "$PROJECT_ROOT/frontend"
nohup $PYTHON_CMD -m http.server 3000 > /dev/null 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend.pid"

# Wait a moment for services to start
sleep 2

# 5. Display Success Message
echo ""
success "AlphaMapping is taking off!"
success "Dashboard: http://localhost:3000"
info "Backend API: http://localhost:8000/docs"
echo ""
warn "Services are running in background."
info "To stop: ./scripts/stop.sh"

# Open browser (optional, works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:3000" 2>/dev/null &
elif command -v open &> /dev/null; then
    open "http://localhost:3000" 2>/dev/null &
fi
