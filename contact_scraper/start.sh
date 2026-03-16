#!/bin/bash

################################################################################
# Contact Scraper - Enterprise Edition
# Complete Setup and Start Script
# 
# This script will:
# 1. Check Python installation
# 2. Create virtual environment (if not exists)
# 3. Install all dependencies
# 4. Check/install Redis (optional but recommended)
# 5. Create required directories
# 6. Start the Flask application
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Contact Scraper - Enterprise Edition Setup          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# Function: Print status messages
################################################################################
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

################################################################################
# Step 1: Check Python Installation
################################################################################
print_status "Step 1/7: Checking Python installation..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

################################################################################
# Step 2: Create Virtual Environment
################################################################################
print_status "Step 2/7: Setting up virtual environment..."

if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

################################################################################
# Step 3: Install Python Dependencies
################################################################################
print_status "Step 3/7: Installing Python dependencies..."

# Upgrade pip first
print_status "Upgrading pip..."
pip install --upgrade pip --quiet

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt --quiet
    print_success "All Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

################################################################################
# Step 4: Check/Install Redis (Optional)
################################################################################
print_status "Step 4/7: Checking Redis installation..."

REDIS_AVAILABLE=false

if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis is running"
        REDIS_AVAILABLE=true
    else
        print_warning "Redis is installed but not running"
        print_status "Attempting to start Redis..."
        
        # Try to start Redis based on OS
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || true
        elif command -v brew &> /dev/null; then
            brew services start redis 2>/dev/null || true
        else
            redis-server --daemonize yes 2>/dev/null || true
        fi
        
        sleep 2
        
        if redis-cli ping &> /dev/null; then
            print_success "Redis started successfully"
            REDIS_AVAILABLE=true
        else
            print_warning "Could not start Redis. Application will run without caching."
        fi
    fi
else
    print_warning "Redis is not installed"
    echo ""
    echo "Redis is recommended for rate limiting and caching."
    echo "Install Redis:"
    echo "  Ubuntu/Debian: sudo apt-get install redis-server"
    echo "  macOS: brew install redis"
    echo "  CentOS/RHEL: sudo yum install redis"
    echo ""
    echo "Skipping Redis installation (continuing without it)..."
fi

################################################################################
# Step 5: Create Required Directories
################################################################################
print_status "Step 5/7: Creating required directories..."

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir -p logs
    print_success "Created logs/ directory"
else
    print_success "logs/ directory already exists"
fi

# Create results directory
if [ ! -d "results" ]; then
    mkdir -p results
    print_success "Created results/ directory"
else
    print_success "results/ directory already exists"
fi

# Create templates directory
if [ ! -d "templates" ]; then
    mkdir -p templates
    print_success "Created templates/ directory"
else
    print_success "templates/ directory already exists"
fi

# Create static directory
if [ ! -d "static" ]; then
    mkdir -p static
    print_success "Created static/ directory"
else
    print_success "static/ directory already exists"
fi

################################################################################
# Step 6: Set Permissions
################################################################################
print_status "Step 6/7: Setting file permissions..."

chmod +x start.sh 2>/dev/null || true
chmod 755 logs 2>/dev/null || true
chmod 755 results 2>/dev/null || true

print_success "Permissions set"

################################################################################
# Step 7: Start Flask Application
################################################################################
print_status "Step 7/7: Starting Flask application..."

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Setup Complete! Starting Server...        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${GREEN}✓${NC} Application URL: ${BLUE}http://localhost:5000${NC}"
echo ""
echo -e "  ${GREEN}✓${NC} Login Credentials:"
echo -e "      ${YELLOW}Username:${NC} techforge"
echo -e "      ${YELLOW}Password:${NC} 2026"
echo ""
echo -e "  ${GREEN}✓${NC} Redis Status: ${REDIS_AVAILABLE:+${GREEN}Connected${NC}}${REDIS_AVAILABLE:-${YELLOW}Not Available (Running without caching)${NC}}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start Flask application
python app.py

################################################################################
# Cleanup on Exit
################################################################################
cleanup() {
    echo ""
    print_status "Shutting down..."
    deactivate 2>/dev/null || true
    print_success "Server stopped"
}

trap cleanup EXIT
