"""
ClaudeAgentOptions configuration builder for agent creation.

Handles system prompt rendering, hook creation, and tool configuration.
"""

import logging
from typing import Dict, Any, List

from claude_agent_sdk import (
    ClaudeAgentOptions,
    HookMatcher,
    create_sdk_mcp_server,
)

from ...config import DEFAULT_CLAUDE_MODEL, AGENT_WORKING_DIRECTORY
from .prompts import PromptManager
from .tools import create_browser_tool


class AgentOptionBuilder:
    """Builds ClaudeAgentOptions configuration for agent creation."""

    HOOK_TYPES = [
        "PreToolUse", "PostToolUse", "Notification", "UserPromptSubmit",
        "Stop", "SubagentStop", "PreCompact", "SessionStart", "SessionEnd"
    ]

    BASE_TOOLS = [
        "Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task",
        "WebFetch", "WebSearch", "BashOutput", "SlashCommand", "TodoWrite"
    ]

    DISALLOWED_TOOLS = ["KillShell", "NotebookEdit", "ExitPlanMode"]

    def __init__(
        self,
        logger: logging.Logger,
        prompt_manager: PromptManager,
        observability_manager,
    ):
        """
        Initialize option builder.

        Args:
            logger: Logger instance.
            prompt_manager: Prompt template manager.
            observability_manager: Observability manager for hooks.
        """
        self.logger = logger
        self.prompt_manager = prompt_manager
        self.observability_manager = observability_manager

    def build_options(
        self,
        agent_name: str,
        browser_agent,
        session_holder: Dict[str, str],
    ) -> ClaudeAgentOptions:
        """
        Build ClaudeAgentOptions configuration.

        Args:
            agent_name: Agent name.
            browser_agent: Browser agent instance or None.
            session_holder: Session ID holder dict.

        Returns:
            Configured ClaudeAgentOptions instance.
        """
        system_prompt = self._render_system_prompt()
        hooks = self._create_hooks(agent_name, session_holder)
        mcp_servers, tools = self._configure_tools(agent_name, browser_agent)

        return ClaudeAgentOptions(
            system_prompt={"type": "preset", "preset": "claude_code", "append": system_prompt},
            model=DEFAULT_CLAUDE_MODEL,
            cwd=str(AGENT_WORKING_DIRECTORY),
            permission_mode="bypassPermissions",
            setting_sources=["project"],
            hooks=hooks,
            mcp_servers=mcp_servers,
            allowed_tools=tools,
            disallowed_tools=self.DISALLOWED_TOOLS,
        )

    def _render_system_prompt(self) -> str:
        """
        Render system prompt template.

        Returns:
            Rendered system prompt string.
        """
        return self.prompt_manager.render_prompt(
            "agentic_coder_system_prompt_system_prompt.md",
            OPERATOR_FILE="(assigned per task)",
            WORKING_DIR=str(AGENT_WORKING_DIRECTORY),
        )

    def _create_hooks(
        self, agent_name: str, session_holder: Dict[str, str]
    ) -> Dict[str, List[HookMatcher]]:
        """
        Create observability hooks for lifecycle events.

        Args:
            agent_name: Agent name.
            session_holder: Session ID holder dict.

        Returns:
            Dictionary mapping hook types to HookMatchers.
        """
        return {
            hook_type: [
                HookMatcher(
                    hooks=[
                        self.observability_manager.create_hook(
                            agent_name, hook_type, session_holder
                        )
                    ]
                )
            ]
            for hook_type in self.HOOK_TYPES
        }

    def _configure_tools(
        self, agent_name: str, browser_agent
    ) -> tuple[Dict[str, Any], List[str]]:
        """
        Configure MCP servers and tool permissions.

        Args:
            agent_name: Agent name.
            browser_agent: Browser agent instance or None.

        Returns:
            Tuple of (mcp_servers dict, allowed_tools list).
        """
        mcp_servers = {}
        allowed_tools = list(self.BASE_TOOLS)

        if browser_agent:
            browser_tool = create_browser_tool(agent_name, browser_agent, self.logger)
            mcp_servers["browser"] = create_sdk_mcp_server(
                name="browser", version="1.0.0", tools=[browser_tool]
            )
            allowed_tools.append("mcp__browser__browser_use")

        return mcp_servers, allowed_tools
