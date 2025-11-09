"""
Core ClaudeCodeAgenticCoder class for managing Claude Code agents.

Handles agent lifecycle, command dispatch, and result retrieval with
session continuity for context-aware development.
"""

import asyncio
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from ...config import CLAUDE_CODE_TOOL, AGENTIC_CODING_TYPE
from ..base import BaseAgent
from .prompts import PromptManager
from .observability import ObservabilityManager
from .agent_creation import AgentCreator
from .agent_execution import AgentExecutor
from .agent_registry_manager import AgentRegistryManager
from .operator_file_manager import OperatorFileManager
from .agent_lifecycle import AgentLifecycleManager


class ClaudeCodeAgenticCoder(BaseAgent):
    """
    Manages Claude Code agents for software development tasks.

    Handles agent creation, command dispatch, and result retrieval.
    Each agent maintains session continuity for context-aware development.
    """

    def __init__(
        self, logger: Optional[logging.Logger] = None, browser_agent=None
    ):
        """
        Initialize agentic coder manager.

        Args:
            logger: Optional logger instance.
            browser_agent: Optional browser agent instance.
        """
        super().__init__(logger)
        self.browser_agent = browser_agent

        # Initialize registry manager
        self.registry_manager = AgentRegistryManager(self.logger)

        # Initialize sub-managers
        self.prompt_manager = PromptManager()
        self.observability_manager = ObservabilityManager(self.logger)
        self.agent_executor = AgentExecutor(self.logger)
        self.operator_file_manager = OperatorFileManager(
            self.logger, self.agent_executor
        )

        # Agent creator with registry callback
        self.agent_creator = AgentCreator(
            self.logger,
            self.prompt_manager,
            self.observability_manager,
            self.registry_manager.register_agent,
        )

        self.background_threads: list[threading.Thread] = []

        # Lifecycle manager for agent operations
        self.lifecycle_manager = AgentLifecycleManager(
            self.logger,
            self.registry_manager,
            self.agent_creator,
            self.agent_executor,
            self.operator_file_manager,
            self.background_threads,
        )

        self.logger.info("Initialized ClaudeCodeAgenticCoder")

    def setup(self):
        """Setup is handled during agent creation."""
        pass

    def cleanup(self):
        """Cleanup resources."""
        for t in self.background_threads:
            if t.is_alive():
                t.join(timeout=1.0)

    def execute_task(self, task: str, agent_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute a coding task.

        Args:
            task: Task description.
            agent_name: Optional agent name. Creates new if not provided.
            **kwargs: Additional arguments.

        Returns:
            Task result dictionary.
        """
        if agent_name:
            return self.lifecycle_manager.command_agent(agent_name, task)
        else:
            result = self.lifecycle_manager.create_agent(
                CLAUDE_CODE_TOOL, AGENTIC_CODING_TYPE, agent_name, self.browser_agent
            )
            if result.get("ok"):
                return self.lifecycle_manager.command_agent(result["data"]["name"], task)
            return result

    def list_agents(self) -> Dict[str, Any]:
        """List all registered agents."""
        return self.lifecycle_manager.list_agents()

    def create_agent(
        self, tool: str = CLAUDE_CODE_TOOL, agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Claude Code agent."""
        return self.lifecycle_manager.create_agent(
            tool, AGENTIC_CODING_TYPE, agent_name, self.browser_agent
        )

    def command_agent(self, agent_name: str, prompt: str) -> Dict[str, Any]:
        """Send command to existing agent."""
        return self.lifecycle_manager.command_agent(agent_name, prompt)

    def check_agent_result(
        self, agent_name: str, operator_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check agent result from operator file."""
        return self.lifecycle_manager.check_agent_result(agent_name, operator_file_path)

    def delete_agent(self, agent_name: str) -> Dict[str, Any]:
        """Delete an agent from registry."""
        return self.lifecycle_manager.delete_agent(agent_name)
