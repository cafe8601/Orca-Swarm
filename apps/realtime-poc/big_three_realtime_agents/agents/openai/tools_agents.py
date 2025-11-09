"""
Agent management tools for OpenAI Realtime Agent.

Handles list_agents, create_agent, command_agent, check_agent_result, delete_agent.
"""

import shutil
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ...config import (
    CLAUDE_CODE_TOOL,
    GEMINI_TOOL,
    AGENTIC_CODING_TYPE,
    AGENTIC_BROWSERING_TYPE,
)
from .agent_validators import (
    validate_tool_type_combination,
    route_agent_by_tool_type,
    find_agent_in_registries,
    format_browser_agents_list,
    generate_browser_agent_name,
)


class AgentTools:
    """Agent management tools for OpenAI Realtime Agent."""

    def __init__(self, logger: logging.Logger, agentic_coder, browser_agent, ui_logger):
        """
        Initialize agent tools.

        Args:
            logger: Logger instance.
            agentic_coder: ClaudeCodeAgenticCoder instance.
            browser_agent: GeminiBrowserAgent instance.
            ui_logger: UI logging function.
        """
        self.logger = logger
        self.agentic_coder = agentic_coder
        self.browser_agent = browser_agent
        self.ui_logger = ui_logger

    def list_agents(self) -> Dict[str, Any]:
        """List all registered agents from both registries."""
        claude_result = self.agentic_coder.list_agents()
        claude_agents = claude_result.get("data", [])
        browser_agents = format_browser_agents_list(self.browser_agent.registry)

        all_agents = claude_agents + browser_agents
        self.ui_logger(all_agents)
        return {"ok": True, "agents": all_agents}

    def create_browser_agent(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Create and register a browser agent."""
        browser_name = generate_browser_agent_name(agent_name)

        if self.browser_agent.registry.get_agent(browser_name):
            return {
                "ok": False,
                "error": f"Browser agent '{browser_name}' already exists. Choose a different name.",
            }

        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "session_id": self.browser_agent.session_id,
        }
        self.browser_agent.registry.register_agent(browser_name, metadata)

        return {
            "ok": True,
            "agent_name": browser_name,
            "session_id": self.browser_agent.session_id,
            "type": AGENTIC_BROWSERING_TYPE,
        }

    def create_agent(
        self,
        tool: str = CLAUDE_CODE_TOOL,
        type: str = AGENTIC_CODING_TYPE,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new agent - routes to appropriate handler based on tool/type."""
        handler = route_agent_by_tool_type(tool, type)

        if handler == "browser":
            return self.create_browser_agent(agent_name)
        elif handler == "claude":
            return self.agentic_coder.create_agent(tool=tool, agent_name=agent_name)
        else:
            is_valid, error_msg = validate_tool_type_combination(tool, type)
            return {"ok": False, "error": error_msg}

    def command_agent(self, agent_name: str, prompt: str) -> Dict[str, Any]:
        """Command an agent - routes to appropriate handler based on agent type."""
        _, _, handler = find_agent_in_registries(
            agent_name, self.agentic_coder.registry, self.browser_agent.registry
        )

        if handler == "claude":
            return self.agentic_coder.command_agent(agent_name, prompt)
        elif handler == "browser":
            try:
                result = self.browser_agent.execute_task(task=prompt, agent_name=agent_name)
                return result
            except Exception as exc:
                self.logger.exception("Browser agent command failed")
                return {"ok": False, "error": f"Browser task failed: {exc}"}
        else:
            return {
                "ok": False,
                "error": f"Agent '{agent_name}' not found in either registry. Create it first.",
            }

    def check_agent_result(
        self, agent_name: str, operator_file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check agent result."""
        return self.agentic_coder.check_agent_result(agent_name, operator_file_name)

    def delete_agent(self, agent_name: str) -> Dict[str, Any]:
        """Delete an agent - routes to appropriate handler based on agent type."""
        _, _, handler = find_agent_in_registries(
            agent_name, self.agentic_coder.registry, self.browser_agent.registry
        )

        if handler == "claude":
            return self.agentic_coder.delete_agent(agent_name)
        elif handler == "browser":
            if not self.browser_agent.registry.delete_agent(agent_name):
                return {"ok": False, "error": f"Failed to delete agent '{agent_name}'"}

            agent_dir = self.browser_agent.registry.get_agent_directory(agent_name)
            warnings = []
            if agent_dir.exists():
                try:
                    shutil.rmtree(agent_dir)
                except Exception as exc:
                    warnings.append(f"Failed to remove directory {agent_dir}: {exc}")

            payload: Dict[str, Any] = {"ok": True, "agent_name": agent_name}
            if warnings:
                payload["warnings"] = warnings
            return payload
        else:
            return {
                "ok": False,
                "error": f"Agent '{agent_name}' not found in either registry. Nothing to delete.",
            }
