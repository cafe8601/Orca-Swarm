#!/usr/bin/env bash
#
# Environment Variable Validation Script
# Validates required environment variables before starting the application
#
# Usage:
#   ./validate_env.sh
#   or
#   source validate_env.sh (to export variables in current shell)
#
# Exit codes:
#   0 - All validations passed
#   1 - Required variable missing
#   2 - Invalid variable value

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Counters
errors=0
warnings=0

# ============================================================================
# Helper Functions
# ============================================================================

log_error() {
    echo -e "${RED}✗ ERROR: $1${NC}" >&2
    ((errors++))
}

log_warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}" >&2
    ((warnings++))
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

check_required() {
    local var_name="$1"
    local var_value="${!var_name:-}"

    if [ -z "$var_value" ]; then
        log_error "$var_name is not set (REQUIRED)"
        return 1
    else
        log_success "$var_name is set"
        return 0
    fi
}

check_optional() {
    local var_name="$1"
    local default_value="$2"
    local var_value="${!var_name:-}"

    if [ -z "$var_value" ]; then
        log_warning "$var_name not set, using default: $default_value"
        return 1
    else
        log_success "$var_name is set: $var_value"
        return 0
    fi
}

check_url() {
    local var_name="$1"
    local var_value="${!var_name:-}"

    if [ -z "$var_value" ]; then
        log_error "$var_name is not set"
        return 1
    fi

    # Basic URL validation
    if [[ ! "$var_value" =~ ^https?:// ]] && [[ ! "$var_value" =~ ^ws:// ]]; then
        log_error "$var_name has invalid URL format: $var_value"
        return 1
    fi

    log_success "$var_name is valid: $var_value"
    return 0
}

check_boolean() {
    local var_name="$1"
    local var_value="${!var_name:-}"

    if [ -n "$var_value" ] && [[ ! "$var_value" =~ ^(true|false)$ ]]; then
        log_warning "$var_name should be 'true' or 'false', got: $var_value"
        return 1
    fi

    log_success "$var_name is valid: ${var_value:-not set}"
    return 0
}

# ============================================================================
# Validation Checks
# ============================================================================

echo "=================================================="
echo "  Environment Variable Validation"
echo "=================================================="
echo ""

# Load .env if it exists
if [ -f .env ]; then
    echo "Loading .env file..."
    set -a
    source .env
    set +a
    log_success ".env file loaded"
else
    log_warning ".env file not found, checking system environment"
fi

echo ""
echo "Checking REQUIRED variables..."
echo "--------------------------------------------------"

# API Keys (At least one required)
has_openai=false
has_anthropic=false
has_gemini=false

if check_required "OPENAI_API_KEY"; then
    has_openai=true
fi

if check_required "ANTHROPIC_API_KEY"; then
    has_anthropic=true
fi

if check_required "GOOGLE_API_KEY"; then
    has_gemini=true
fi

# Verify at least one API key is present
if ! $has_openai && ! $has_anthropic && ! $has_gemini; then
    log_error "At least one API key required (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)"
fi

echo ""
echo "Checking OPTIONAL variables..."
echo "--------------------------------------------------"

# Observability
check_optional "OBSERVABILITY_SERVER_URL" "http://localhost:4000/events"

# OpenAI Realtime
check_optional "REALTIME_MODEL" "gpt-realtime-2025-08-28"
check_optional "REALTIME_AGENT_VOICE" "shimmer"
check_optional "BROWSER_TOOL_STARTING_URL" "localhost:3333"

# Claude Agent
check_optional "CLAUDE_AGENT_MODEL" "claude-sonnet-4-5-20250929"
check_optional "ENGINEER_NAME" "Dan"
check_optional "REALTIME_ORCH_AGENT_NAME" "ada"

# Claude Mode
check_optional "CLAUDE_MODE" "auto"
check_boolean "CLAUDE_MAX_HEADLESS"
check_optional "CLAUDE_MAX_LOGIN_TIMEOUT" "120"

# Advanced Systems
check_boolean "ENABLE_AGENT_POOL"
check_boolean "ENABLE_WORKFLOW"
check_boolean "ENABLE_MEMORY"
check_boolean "ENABLE_LEARNING"
check_boolean "ENABLE_SECURITY"

check_optional "MAX_INSTANCES_PER_EXPERT" "3"
check_optional "AGENT_IDLE_TIMEOUT_MINUTES" "30"

# Ollama (optional)
if [ -n "${OLLAMA_MODEL:-}" ]; then
    check_optional "OLLAMA_MODEL" "gpt-oss:20b"
fi

echo ""
echo "=================================================="
echo "  Validation Summary"
echo "=================================================="

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    log_success "All validations passed! ✓"
    exit 0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validations passed with $warnings warning(s)${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation failed with $errors error(s) and $warnings warning(s)${NC}"
    echo ""
    echo "Please fix the errors above and try again."
    echo "Refer to .env.sample for configuration examples."
    exit 1
fi
