"""
Agent registry management for Claude Code agents.

Provides registry operations, session persistence, and thread-safe access
to agent metadata and directory management.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ...config import (
    CLAUDE_CODE_REGISTRY_PATH,
    AGENTS_BASE_DIR,
    CLAUDE_CODE_TOOL_SLUG,
    AGENTIC_CODING_TYPE,
)
from ...utils import AgentRegistry


class AgentRegistryManager:
    """
    Manages agent registry operations with thread-safe access.

    Provides high-level interface for agent lookup, listing, deletion,
    and directory management with session persistence.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize agent registry manager.

        Args:
            logger: Optional logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.registry = AgentRegistry(
            registry_path=CLAUDE_CODE_REGISTRY_PATH,
            base_dir=AGENTS_BASE_DIR,
            tool_slug=CLAUDE_CODE_TOOL_SLUG,
            agent_type=AGENTIC_CODING_TYPE,
            logger=self.logger,
        )

    def register_agent(self, name: str, session_id: str, metadata: Dict[str, Any]):
        """
        Register agent with session ID.

        Args:
            name: Agent name.
            session_id: Claude Code session ID.
            metadata: Additional metadata.
        """
        metadata["session_id"] = session_id
        self.registry.register_agent(name, metadata)
        self.logger.info(f"Registered agent '{name}' with session '{session_id}'")

    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get agent metadata by name.

        Args:
            agent_name: Name of the agent.

        Returns:
            Agent metadata dictionary or None if not found.
        """
        return self.registry.get_agent(agent_name)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered agents.

        Returns:
            Dictionary of agent names to metadata.
        """
        return self.registry.list_agents()

    def delete_agent(self, agent_name: str) -> bool:
        """
        Delete agent from registry.

        Args:
            agent_name: Name of the agent.

        Returns:
            True if agent was deleted, False if not found.
        """
        deleted = self.registry.delete_agent(agent_name)
        if deleted:
            self.logger.info(f"Deleted agent '{agent_name}' from registry")
        return deleted

    def get_agent_directory(self, agent_name: str) -> Path:
        """
        Get agent working directory path.

        Args:
            agent_name: Name of the agent.

        Returns:
            Path to agent directory.
        """
        return self.registry.get_agent_directory(agent_name)

    def get_existing_names(self) -> list[str]:
        """
        Get list of existing agent names.

        Returns:
            List of registered agent names.
        """
        return list(self.registry.list_agents().keys())

    def get_agent_session_id(self, agent_name: str) -> Optional[str]:
        """
        Get agent session ID.

        Args:
            agent_name: Name of the agent.

        Returns:
            Session ID or None if not found.
        """
        agent = self.get_agent(agent_name)
        return agent.get("session_id") if agent else None

    def agent_exists(self, agent_name: str) -> bool:
        """
        Check if agent exists in registry.

        Args:
            agent_name: Name of the agent.

        Returns:
            True if agent exists, False otherwise.
        """
        return self.get_agent(agent_name) is not None
