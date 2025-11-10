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

from ...config import OBSERVABILITY_SERVER_URL
from ...timeouts import OBSERVABILITY_EVENT_TIMEOUT
from ...utils.retry import retry_with_backoff
from ...utils.circuit_breaker import get_circuit_breaker, CircuitBreakerError


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


@retry_with_backoff(
    max_attempts=2,  # Quick retries for observability events
    initial_delay=0.5,  # Short delay for fast failure
    exceptions=(urllib.error.URLError, ConnectionError, TimeoutError),
)
def send_http_event(
    event_data: dict, logger: logging.Logger, agent_name: str
) -> None:
    """
    Send event data to observability server via HTTP with retry logic and circuit breaker.

    Features:
    - Circuit breaker prevents cascading failures
    - Automatic retry on transient failures (network errors)
    - Fast failure with short delays (0.5s initial, 2 attempts max)
    - Silent failure on non-retryable errors or circuit open

    Args:
        event_data: Formatted event data.
        logger: Logger instance for debug messages.
        agent_name: Agent name for logging context.
    """
    # Get circuit breaker for observability service
    breaker = get_circuit_breaker(
        name="observability_service",
        failure_threshold=5,
        recovery_timeout=30.0,
        logger=logger
    )

    try:
        # Execute with circuit breaker protection
        def send_request():
            req = urllib.request.Request(
                OBSERVABILITY_SERVER_URL,
                data=json.dumps(event_data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "BigThreeAgents/1.0",
                },
            )

            with urllib.request.urlopen(req, timeout=OBSERVABILITY_EVENT_TIMEOUT) as response:
                if response.status != 200:
                    logger.debug(
                        f"Observability event returned {response.status} for {agent_name}"
                    )

        breaker.call(send_request)

    except CircuitBreakerError as e:
        # Circuit is open - fail silently for observability
        logger.debug(f"Circuit breaker open for observability: {e}")
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        # Retryable errors - let decorator handle retry
        logger.debug(f"Observability event failed for {agent_name}: {e}")
        raise  # Re-raise for retry decorator
    except Exception as e:
        # Non-retryable errors - fail silently
        logger.debug(f"Observability event error for {agent_name}: {e}")
