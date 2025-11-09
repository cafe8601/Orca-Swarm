"""
Agent registry utilities for Big Three Realtime Agents.

Provides base class for managing agent registrations and metadata.
"""

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


class AgentRegistry:
    """Base class for managing agent registrations."""

    def __init__(
        self,
        registry_path: Path,
        base_dir: Path,
        tool_slug: str,
        agent_type: str,
        logger: logging.Logger = None,
    ):
        """
        Initialize agent registry.

        Args:
            registry_path: Path to registry JSON file.
            base_dir: Base directory for agent storage.
            tool_slug: Tool identifier slug.
            agent_type: Agent type identifier.
            logger: Optional logger instance.
        """
        self.registry_path = registry_path
        self.base_dir = base_dir
        self.tool_slug = tool_slug
        self.agent_type = agent_type
        self.logger = logger or logging.getLogger("AgentRegistry")

        self.registry_lock = threading.Lock()
        self.agent_registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry from disk."""
        if not self.registry_path.exists():
            return {"agents": {}}

        try:
            with self.registry_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "agents" not in data:
                    data["agents"] = {}
                return data
        except Exception as exc:
            self.logger.error(f"Failed to load registry: {exc}")
            return {"agents": {}}

    def _save_registry(self):
        """Save agent registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.registry_path.open("w", encoding="utf-8") as fh:
                json.dump(self.agent_registry, fh, indent=2)
        except Exception as exc:
            self.logger.error(f"Failed to save registry: {exc}")

    def register_agent(self, agent_name: str, metadata: Dict[str, Any]):
        """
        Register an agent in the registry.

        Args:
            agent_name: Name of the agent.
            metadata: Agent metadata dictionary.
        """
        with self.registry_lock:
            self.agent_registry.setdefault("agents", {})[agent_name] = {
                "tool": self.tool_slug,
                "type": self.agent_type,
                "created_at": metadata.get(
                    "created_at", datetime.now(timezone.utc).isoformat()
                ),
                "session_id": metadata.get("session_id"),
                **{k: v for k, v in metadata.items()
                   if k not in ["created_at", "session_id"]},
            }
            self._save_registry()

    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get agent metadata by name.

        Args:
            agent_name: Name of the agent.

        Returns:
            Agent metadata dictionary or None if not found.
        """
        return self.agent_registry.get("agents", {}).get(agent_name)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered agents.

        Returns:
            Dictionary of agent names to metadata.
        """
        return self.agent_registry.get("agents", {})

    def delete_agent(self, agent_name: str) -> bool:
        """
        Delete an agent from the registry.

        Args:
            agent_name: Name of the agent.

        Returns:
            True if agent was deleted, False if not found.
        """
        with self.registry_lock:
            if agent_name in self.agent_registry.get("agents", {}):
                del self.agent_registry["agents"][agent_name]
                self._save_registry()
                return True
            return False

    def get_agent_directory(self, agent_name: str) -> Path:
        """
        Get agent working directory path.

        Args:
            agent_name: Name of the agent.

        Returns:
            Path to agent directory.
        """
        return self.base_dir / self.tool_slug / agent_name
