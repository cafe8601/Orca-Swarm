"""
Configuration module for Big Three Realtime Agents.

Centralizes all environment variables, constants, and configuration settings.
"""

import os
from pathlib import Path

# ================================================================
# OpenAI Realtime API Configuration
# ================================================================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
REALTIME_MODEL_DEFAULT = os.environ.get("REALTIME_MODEL", "gpt-realtime-2025-08-28")
REALTIME_MODEL_MINI = "gpt-realtime-mini-2025-10-06"
REALTIME_API_URL_TEMPLATE = "wss://api.openai.com/v1/realtime?model={model}"
REALTIME_VOICE_CHOICE = os.environ.get("REALTIME_AGENT_VOICE", "shimmer")
BROWSER_TOOL_STARTING_URL = os.environ.get(
    "BROWSER_TOOL_STARTING_URL", "localhost:3333"
)

# ================================================================
# Audio Configuration
# ================================================================

CHUNK_SIZE = 1024
FORMAT = 16  # pyaudio.paInt16
CHANNELS = 1
RATE = 24000

# ================================================================
# Claude Code Configuration
# ================================================================

DEFAULT_CLAUDE_MODEL = os.environ.get(
    "CLAUDE_AGENT_MODEL", "claude-sonnet-4-5-20250929"
)
ENGINEER_NAME = os.environ.get("ENGINEER_NAME", "Dan")
REALTIME_ORCH_AGENT_NAME = os.environ.get("REALTIME_ORCH_AGENT_NAME", "ada")
CLAUDE_CODE_TOOL = "claude_code"
CLAUDE_CODE_TOOL_SLUG = "claude_code"
AGENTIC_CODING_TYPE = "agentic_coding"

# ================================================================
# Gemini Computer Use Configuration
# ================================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-computer-use-preview-10-2025"
GEMINI_TOOL = "gemini"
GEMINI_TOOL_SLUG = "gemini"
AGENTIC_BROWSERING_TYPE = "agentic_browsering"
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

# ================================================================
# Directory Configuration
# ================================================================

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

# Agent working directory - set to content-gen app
AGENT_WORKING_DIRECTORY = BASE_DIR.parent / "content-gen"

# Set AGENTS_BASE_DIR relative to working directory for consolidated outputs
AGENTS_BASE_DIR = AGENT_WORKING_DIRECTORY / "agents"
CLAUDE_CODE_REGISTRY_PATH = AGENTS_BASE_DIR / CLAUDE_CODE_TOOL_SLUG / "registry.json"
GEMINI_REGISTRY_PATH = AGENTS_BASE_DIR / GEMINI_TOOL_SLUG / "registry.json"

# ================================================================
# OpenAI Model Pricing (per 1M tokens)
# ================================================================

OPENAI_PRICING = {
    "gpt-realtime-2025-08-28": {
        "text_input": 10.0,
        "text_output": 40.0,
        "audio_input": 200.0,
        "audio_output": 800.0,
    },
    "gpt-realtime-mini-2025-10-06": {
        "text_input": 1.0,
        "text_output": 4.0,
        "audio_input": 20.0,
        "audio_output": 80.0,
    },
}

# ================================================================
# Claude Mode Configuration
# ================================================================

# Claude operation mode: "api" or "max" or "auto"
CLAUDE_MODE = os.environ.get("CLAUDE_MODE", "auto")

# Claude Max browser settings
CLAUDE_MAX_HEADLESS = os.environ.get("CLAUDE_MAX_HEADLESS", "false").lower() == "true"
CLAUDE_MAX_LOGIN_TIMEOUT = int(os.environ.get("CLAUDE_MAX_LOGIN_TIMEOUT", "120"))

# ================================================================
# Advanced Systems Configuration
# ================================================================

# Enable advanced systems
ENABLE_AGENT_POOL = os.environ.get("ENABLE_AGENT_POOL", "true").lower() == "true"
ENABLE_WORKFLOW = os.environ.get("ENABLE_WORKFLOW", "true").lower() == "true"
ENABLE_MEMORY = os.environ.get("ENABLE_MEMORY", "true").lower() == "true"
ENABLE_LEARNING = os.environ.get("ENABLE_LEARNING", "true").lower() == "true"
ENABLE_SECURITY = os.environ.get("ENABLE_SECURITY", "true").lower() == "true"

# Agent pool directory
AGENT_POOL_DIR = BASE_DIR.parent.parent / "agentpool"

# Performance configuration
MAX_INSTANCES_PER_EXPERT = int(os.environ.get("MAX_INSTANCES_PER_EXPERT", "3"))
AGENT_IDLE_TIMEOUT_MINUTES = int(os.environ.get("AGENT_IDLE_TIMEOUT_MINUTES", "30"))

# Storage for advanced systems
STORAGE_BASE_DIR = AGENT_WORKING_DIRECTORY / "storage"


# ================================================================
# Helper Functions
# ================================================================

def get_claude_mode() -> str:
    """
    Determine which Claude mode to use.

    Returns:
        "api" if API key available, "max" otherwise
    """
    if CLAUDE_MODE == "max":
        return "max"
    elif CLAUDE_MODE == "api":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        return "api" if api_key and not api_key.startswith("sk-ant-placeholder") else "max"
    else:  # auto
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        has_valid_key = api_key and not api_key.startswith("sk-ant-placeholder")
        return "api" if has_valid_key else "max"


def is_api_mode() -> bool:
    """Check if using API mode."""
    return get_claude_mode() == "api"


def is_max_mode() -> bool:
    """Check if using Max browser mode."""
    return get_claude_mode() == "max"
