"""
Event formatting utilities for observability.

Handles event data construction and context extraction for different tool types.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional
import logging


def build_event_data(
    agent_name: str,
    hook_type: str,
    session_id: str,
    payload: dict,
    summary: Optional[str] = None,
) -> dict:
    """
    Build event data payload for observability server.

    Args:
        agent_name: Name of the agent.
        hook_type: Type of hook event.
        session_id: Session ID.
        payload: Event payload data.
        summary: Optional AI-generated summary.

    Returns:
        Dictionary with formatted event data.
    """
    event_data = {
        "source_app": f"big-three-agents: {agent_name}",
        "session_id": session_id,
        "hook_event_type": hook_type,
        "payload": payload,
        "timestamp": int(datetime.now().timestamp() * 1000),
    }

    if summary:
        event_data["summary"] = summary

    return event_data


def extract_tool_context(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Extract key context from tool input based on tool type.

    Args:
        tool_name: Name of the tool.
        tool_input: Tool input parameters.

    Returns:
        Formatted context string.
    """
    context_parts = []

    if tool_name == "Bash":
        command = tool_input.get("command", "")[:100]
        context_parts.append(f"Command: {command}")
    elif tool_name in ["Read", "Edit", "Write"]:
        file_path = tool_input.get("file_path", "")
        context_parts.append(f"File: {file_path}")

    return " | ".join(context_parts) if context_parts else "No specific context"


def send_http_event(
    event_data: dict, logger: logging.Logger, agent_name: str
) -> None:
    """
    Send event data to observability server via HTTP (fails silently).

    Args:
        event_data: Formatted event data.
        logger: Logger instance for debug messages.
        agent_name: Agent name for logging context.
    """
    try:
        req = urllib.request.Request(
            "http://localhost:4000/events",
            data=json.dumps(event_data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "BigThreeAgents/1.0",
            },
        )

        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status != 200:
                logger.debug(
                    f"Observability event returned {response.status} for {agent_name}"
                )

    except urllib.error.URLError as e:
        logger.debug(f"Observability event failed for {agent_name}: {e}")
    except Exception as e:
        logger.debug(f"Observability event error for {agent_name}: {e}")
