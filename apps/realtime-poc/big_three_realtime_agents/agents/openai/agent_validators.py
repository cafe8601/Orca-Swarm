"""
Agent validation utilities for OpenAI Realtime Agent.

Handles agent routing, validation, registry lookup, and browser agent creation.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from ...config import CLAUDE_CODE_TOOL, GEMINI_TOOL, AGENTIC_CODING_TYPE, AGENTIC_BROWSERING_TYPE


def validate_tool_type_combination(tool: str, type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate tool and type combination.

    Args:
        tool: Tool identifier.
        type: Agent type identifier.

    Returns:
        Tuple of (is_valid, error_message).
    """
    valid_combinations = [
        (CLAUDE_CODE_TOOL, AGENTIC_CODING_TYPE),
        (GEMINI_TOOL, AGENTIC_BROWSERING_TYPE),
    ]

    if (tool, type) in valid_combinations:
        return True, None

    return False, f"Invalid tool/type combination: tool='{tool}', type='{type}'"


def route_agent_by_tool_type(tool: str, type: str) -> str:
    """
    Determine agent handler based on tool and type.

    Args:
        tool: Tool identifier.
        type: Agent type identifier.

    Returns:
        Handler identifier: 'browser', 'claude', or 'invalid'.
    """
    if tool == GEMINI_TOOL and type == AGENTIC_BROWSERING_TYPE:
        return "browser"
    elif tool == CLAUDE_CODE_TOOL and type == AGENTIC_CODING_TYPE:
        return "claude"
    return "invalid"


def find_agent_in_registries(
    agent_name: str, claude_registry, browser_registry
) -> Tuple[Optional[Any], Optional[Any], str]:
    """
    Find agent in either Claude or Browser registry.

    Args:
        agent_name: Name of agent to find.
        claude_registry: Claude Code agent registry instance.
        browser_registry: Browser agent registry instance.

    Returns:
        Tuple of (claude_agent, browser_agent, handler_type).
        handler_type is 'claude', 'browser', or 'not_found'.
    """
    claude_agent = claude_registry.get_agent(agent_name)
    browser_agent = browser_registry.get_agent(agent_name)

    if claude_agent:
        return claude_agent, None, "claude"
    elif browser_agent:
        return None, browser_agent, "browser"
    else:
        return None, None, "not_found"


def format_browser_agents_list(browser_registry) -> List[Dict[str, Any]]:
    """
    Format browser agents from registry into list of dictionaries.

    Args:
        browser_registry: Browser agent registry instance.

    Returns:
        List of browser agent metadata dictionaries.
    """
    browser_agents_list = []
    for name, data in sorted(browser_registry.list_agents().items()):
        browser_agents_list.append(
            {
                "name": name,
                "session_id": data.get("session_id"),
                "tool": data.get("tool"),
                "type": data.get("type"),
                "created_at": data.get("created_at"),
            }
        )
    return browser_agents_list


def generate_browser_agent_name(agent_name: Optional[str]) -> str:
    """
    Generate browser agent name with timestamp if not provided.

    Args:
        agent_name: Optional custom agent name.

    Returns:
        Agent name (custom or auto-generated).
    """
    return agent_name or f"BrowserAgent_{datetime.now(timezone.utc).strftime('%H%M%S')}"
