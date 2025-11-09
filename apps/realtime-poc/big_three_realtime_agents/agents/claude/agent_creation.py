"""
Agent creation logic for Claude Code agents.

Handles async agent creation, initialization, and operator file preparation.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
)

from ...utils import console
from rich.panel import Panel
from .agent_naming import AgentNaming
from .agent_option_builder import AgentOptionBuilder


class AgentCreator:
    """Handles Claude Code agent creation and initialization."""

    def __init__(
        self,
        logger: logging.Logger,
        prompt_manager,
        observability_manager,
        registry_saver: callable,
    ):
        """Initialize agent creator with dependencies."""
        self.logger = logger
        self.register_agent = registry_saver
        self.naming = AgentNaming(logger)
        self.option_builder = AgentOptionBuilder(
            logger, prompt_manager, observability_manager
        )

    async def create_new_agent(
        self,
        tool: str,
        agent_type: str,
        agent_name: Optional[str],
        existing_names: List[str],
        browser_agent,
        agent_directory_func: callable,
    ) -> Dict[str, Any]:
        """
        Create new Claude Code agent asynchronously.

        Returns dict with keys: name, session_id, directory.
        Raises RuntimeError if initialization fails.
        """
        final_name = await self.naming.generate_unique_name(
            existing_names, agent_name
        )

        agent_dir = agent_directory_func(final_name)
        agent_dir.mkdir(parents=True, exist_ok=True)

        session_holder = {"session_id": "unknown"}
        options = self.option_builder.build_options(
            final_name, browser_agent, session_holder
        )
        session_id = await self._initialize_agent(final_name, agent_type, options)
        self._register_created_agent(final_name, session_id, tool, agent_type)

        return {
            "name": final_name,
            "session_id": session_id,
            "directory": str(agent_dir),
        }

    async def _initialize_agent(
        self, agent_name: str, agent_type: str, options: ClaudeAgentOptions
    ) -> str:
        """Initialize agent and extract session_id. Raises RuntimeError on failure."""
        greeting = (
            f"Hi, you are {agent_name}, a {agent_type} agent. "
            f"Please acknowledge you're ready and briefly introduce yourself."
        )

        session_id = await self._run_greeting_query(agent_name, greeting, options)

        if not session_id:
            raise RuntimeError("Failed to obtain session_id from Claude agent.")

        return session_id

    async def _run_greeting_query(
        self, agent_name: str, greeting: str, options: ClaudeAgentOptions
    ) -> Optional[str]:
        """Execute greeting query and capture session_id."""
        session_id = None

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(greeting)

                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        session_id = message.session_id
                        self._display_agent_ready(agent_name, message.result)

        except Exception as exc:
            raise RuntimeError(f"Agent initialization failed: {exc}") from exc

        return session_id

    def _display_agent_ready(self, agent_name: str, result: str) -> None:
        """Display agent ready message in console."""
        console.print(
            Panel(
                f"{result}",
                title=f"Agent '{agent_name}' (ResultMessage)",
                border_style="green",
            )
        )

    def _register_created_agent(
        self, agent_name: str, session_id: str, tool: str, agent_type: str
    ) -> None:
        """Register agent in registry with metadata."""
        metadata = {
            "tool": tool,
            "type": agent_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "working_dir": str(AGENT_WORKING_DIRECTORY),
        }
        self.register_agent(agent_name, session_id, metadata)
        self.logger.info(f"Created agent '{agent_name}' - session_id: {session_id}")
