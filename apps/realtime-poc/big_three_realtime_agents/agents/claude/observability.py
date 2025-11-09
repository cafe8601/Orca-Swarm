"""
Observability hooks for Claude Code agents.

Handles event tracking, hook creation, and AI-powered event summarization.
"""

import logging
from typing import Dict, Any, Optional

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookContext,
    AssistantMessage,
    TextBlock,
)

from .prompts import PromptManager
from .event_formatting import build_event_data, extract_tool_context, send_http_event


class ObservabilityManager:
    """Manages observability events and hooks for Claude Code agents."""

    def __init__(self, logger: logging.Logger):
        """
        Initialize observability manager.

        Args:
            logger: Logger instance.
        """
        self.logger = logger
        self.prompt_manager = PromptManager()

    def send_event(
        self,
        agent_name: str,
        hook_type: str,
        session_id: str,
        payload: dict,
        summary: Optional[str] = None,
    ) -> None:
        """
        Send observability event to monitoring server (fails silently).

        Args:
            agent_name: Name of the agent.
            hook_type: Type of hook event.
            session_id: Session ID.
            payload: Event payload data.
            summary: Optional AI-generated summary.
        """
        event_data = build_event_data(agent_name, hook_type, session_id, payload, summary)
        send_http_event(event_data, self.logger, agent_name)

    def create_hook(
        self,
        agent_name: str,
        hook_type: str,
        session_id_holder: dict,
        summarize: bool = True,
    ) -> callable:
        """
        Create observability hook for any hook type with optional summarization.

        Args:
            agent_name: Name of the agent.
            hook_type: Type of hook to create.
            session_id_holder: Dictionary holding session_id.
            summarize: Whether to generate AI summary.

        Returns:
            Async hook function.
        """

        async def hook(
            input_data: Dict[str, Any],
            tool_use_id: str | None,
            context: HookContext,
        ) -> Dict[str, Any]:
            session_id = session_id_holder.get("session_id", "unknown")

            # Generate summary if enabled
            event_summary = None
            if summarize:
                event_summary = await self.generate_event_summary(
                    agent_name, hook_type, input_data
                )

            # Send event with optional summary
            self.send_event(
                agent_name, hook_type, session_id, input_data, event_summary
            )
            return {}  # Allow all operations

        return hook

    async def generate_event_summary(
        self, agent_name: str, hook_type: str, input_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate AI summary of event using Claude Agent SDK.

        Args:
            agent_name: Name of the agent.
            hook_type: Type of hook event.
            input_data: Event input data.

        Returns:
            Generated summary string or None if generation fails.
        """
        try:
            # Build summary prompt
            tool_name = input_data.get("tool_name", "N/A")
            tool_input = input_data.get("tool_input", {})
            context = extract_tool_context(tool_name, tool_input)

            # Load prompts from files
            system_prompt = self.prompt_manager.read_prompt(
                "event_summarizer_system_prompt.md"
            )
            user_prompt = self.prompt_manager.render_prompt(
                "event_summarizer_user_prompt.md",
                AGENT_NAME=agent_name,
                HOOK_TYPE=hook_type,
                TOOL_NAME=tool_name,
                CONTEXT=context,
            )

            # Use Claude Agent SDK query for fast summary
            options = ClaudeAgentOptions(
                model="claude-3-5-haiku-20241022",  # Fast model
                system_prompt=system_prompt,
            )

            chunks = []
            async for message in query(prompt=user_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            chunks.append(block.text)

            summary = "".join(chunks).strip()
            return summary if summary else None

        except Exception as e:
            self.logger.debug(f"Summary generation failed: {e}")
            return None
