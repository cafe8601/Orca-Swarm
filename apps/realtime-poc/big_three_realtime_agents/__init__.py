"""
Big Three Realtime Agents - Unified Agent System
=================================================

Unified system combining three powerful agent types:
1. OpenAIRealtimeVoiceAgent - OpenAI Realtime API for voice interactions
2. ClaudeCodeAgenticCoder - Claude Code SDK agents for software development
3. GeminiBrowserAgent - Gemini Computer Use for browser automation

Each agent class is modular and self-contained with focused utility modules.

Package Structure:
    config: Configuration and constants
    logging_setup: Logging configuration
    utils: Utility modules (audio, registry, UI)
    agents: Agent implementations (gemini, claude, openai)

Usage:
    from big_three_realtime_agents import setup_logging
    from big_three_realtime_agents.config import OPENAI_API_KEY
    from big_three_realtime_agents.utils import AudioManager, console
    from big_three_realtime_agents.agents.openai import OpenAIRealtimeVoiceAgent
    from big_three_realtime_agents.agents.claude import ClaudeCodeAgenticCoder
    from big_three_realtime_agents.agents.gemini import GeminiBrowserAgent
"""

__version__ = "2.0.0-modular"
__author__ = "Big Three Realtime Agents Team"

from . import config
from .logging_setup import setup_logging
from .agents.gemini import GeminiBrowserAgent
from .agents.claude import ClaudeCodeAgenticCoder
from .agents.openai import OpenAIRealtimeVoiceAgent

__all__ = [
    "config",
    "setup_logging",
    "GeminiBrowserAgent",
    "ClaudeCodeAgenticCoder",
    "OpenAIRealtimeVoiceAgent",
]
