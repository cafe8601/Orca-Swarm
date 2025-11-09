"""
Claude Code agent modules.

This package contains the ClaudeCodeAgenticCoder implementation for software
development automation using Anthropic's Claude Agent SDK.

Modules:
    coder: Core ClaudeCodeAgenticCoder class
    agent_registry_manager: Registry operations and session persistence
    agent_creation: Agent creation and initialization logic
    agent_naming: Agent name generation, validation, and deduplication
    agent_execution: Agent command execution and threading
    tools: Tool definitions (browser_use)
    prompts: Prompt template management
    observability: Event tracking and hooks
"""

from .coder import ClaudeCodeAgenticCoder

__all__ = [
    "ClaudeCodeAgenticCoder",
]
