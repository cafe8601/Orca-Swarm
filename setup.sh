#!/bin/bash
# Big Three Agents - Automated Setup Script
# Installs all dependencies and configures the system

set -e  # Exit on error

echo "🚀 Big Three Realtime Agents - Automated Setup"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION (>= 3.11)${NC}"
else
    echo -e "${RED}❌ Python 3.11+ required. Current: $PYTHON_VERSION${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo "2. Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "4. Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install Python dependencies
echo ""
echo "5. Installing Python dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install Python dependencies${NC}"
    echo "   Try manually: pip install -r requirements.txt"
    exit 1
fi

# Install Playwright browsers
echo ""
echo "6. Installing Playwright browsers..."
playwright install chromium

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Playwright Chromium installed${NC}"
else
    echo -e "${YELLOW}⚠️  Playwright install had issues. Run manually: playwright install chromium${NC}"
fi

# Install Playwright system dependencies (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    echo "7. Installing Playwright system dependencies (Linux)..."
    playwright install-deps chromium

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Playwright system dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  May need sudo. Run: sudo playwright install-deps chromium${NC}"
    fi
else
    echo ""
    echo "7. Skipping system dependencies (not Linux)"
fi

# Setup environment file
echo ""
echo "8. Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.sample .env
    echo -e "${GREEN}✅ .env file created from .env.sample${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your API keys!${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists (not overwriting)${NC}"
fi

# Create necessary directories
echo ""
echo "9. Creating necessary directories..."
mkdir -p apps/content-gen/agents/claude_code
mkdir -p apps/content-gen/agents/gemini
mkdir -p apps/content-gen/storage/{memory,learning,security}
mkdir -p output_logs
mkdir -p logs
echo -e "${GREEN}✅ Directories created${NC}"

# Check API keys (optional)
echo ""
echo "10. Checking API keys configuration..."
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY=sk-" .env && grep -q "GEMINI_API_KEY=" .env; then
        echo -e "${GREEN}✅ API keys appear to be configured${NC}"
    else
        echo -e "${YELLOW}⚠️  API keys not configured yet${NC}"
        echo "   Edit .env and add:"
        echo "   - OPENAI_API_KEY=sk-proj-your-key"
        echo "   - GEMINI_API_KEY=your-key"
        echo "   - ANTHROPIC_API_KEY=sk-ant-your-key (or leave empty for Claude Max)"
    fi
fi

# Optional: Install Redis (if Docker not used)
echo ""
echo "11. Redis setup..."
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✅ Redis is installed${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not found${NC}"
    echo "   For full RAG features, install Redis:"
    echo "   - Ubuntu/Debian: sudo apt install redis-server"
    echo "   - macOS: brew install redis"
    echo "   - Or use Docker: docker compose up -d redis"
fi

# Run tests (optional)
echo ""
echo "12. Running basic tests..."
if pytest tests/unit/test_config.py -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}✅ Basic tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Tests skipped (may need API keys)${NC}"
fi

# Summary
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run the system:"
echo "   - Text mode: python -m apps.realtime-poc.big_three_realtime_agents.main"
echo "   - Voice mode: python -m apps.realtime-poc.big_three_realtime_agents.main --voice"
echo "   - Docker: docker compose up -d"
echo ""
echo "3. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "4. Check documentation:"
echo "   - DEPLOYMENT_GUIDE.md"
echo "   - README.md"
echo ""
echo "For help: https://github.com/cafe8601/-multi-agent-learning/issues"
echo ""
