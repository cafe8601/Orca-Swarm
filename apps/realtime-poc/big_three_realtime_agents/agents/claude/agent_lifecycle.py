"""
Agent lifecycle management for Claude Code agents.

Handles agent listing, creation, deletion, command dispatch, and result checking.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


class AgentLifecycleManager:
    """Manages agent lifecycle operations."""

    def __init__(
        self,
        logger: logging.Logger,
        registry_manager,
        agent_creator,
        agent_executor,
        operator_file_manager,
        background_threads: list,
    ):
        """
        Initialize lifecycle manager.

        Args:
            logger: Logger instance.
            registry_manager: Registry management instance.
            agent_creator: Agent creation instance.
            agent_executor: Agent execution instance.
            operator_file_manager: Operator file management instance.
            background_threads: List to track background threads.
        """
        self.logger = logger
        self.registry_manager = registry_manager
        self.agent_creator = agent_creator
        self.agent_executor = agent_executor
        self.operator_file_manager = operator_file_manager
        self.background_threads = background_threads

    def list_agents(self) -> Dict[str, Any]:
        """
        List all registered agents.

        Returns:
            Dictionary with ok status and agent list.
        """
        agents = self.registry_manager.list_agents()
        agents_list = [
            {"name": name, **metadata} for name, metadata in agents.items()
        ]
        return {"ok": True, "data": agents_list}

    def create_agent(
        self,
        tool: str,
        agent_type: str,
        agent_name: Optional[str],
        browser_agent,
    ) -> Dict[str, Any]:
        """
        Create a new Claude Code agent.

        Args:
            tool: Tool identifier.
            agent_type: Agent type.
            agent_name: Optional agent name.
            browser_agent: Browser agent instance.

        Returns:
            Dictionary with ok status and agent info.
        """
        try:
            existing_names = self.registry_manager.get_existing_names()
            result = asyncio.run(
                self.agent_creator.create_new_agent(
                    tool,
                    agent_type,
                    agent_name,
                    existing_names,
                    browser_agent,
                    self.registry_manager.get_agent_directory,
                )
            )
            return {"ok": True, "data": result}
        except Exception as exc:
            self.logger.exception("Agent creation failed")
            return {"ok": False, "error": str(exc)}

    def command_agent(
        self, agent_name: str, prompt: str
    ) -> Dict[str, Any]:
        """
        Send command to existing agent.

        Args:
            agent_name: Name of the agent.
            prompt: Command prompt.

        Returns:
            Dictionary with ok status and command result.
        """
        if not self.registry_manager.agent_exists(agent_name):
            return {"ok": False, "error": f"Agent '{agent_name}' not found"}

        session_id = self.registry_manager.get_agent_session_id(agent_name)
        if not session_id:
            return {"ok": False, "error": f"Agent '{agent_name}' has no session_id"}

        # Prepare operator file
        agent_dir = self.registry_manager.get_agent_directory(agent_name)
        operator_file = asyncio.run(
            self.operator_file_manager.prepare_operator_file(agent_dir, prompt)
        )

        # Run in background thread
        self.agent_executor.run_command_thread(
            agent_name,
            session_id,
            prompt,
            str(operator_file),
            self.background_threads,
        )

        return {
            "ok": True,
            "data": {
                "message": f"Command dispatched to '{agent_name}' in background",
                "operator_file": str(operator_file),
            },
        }

    def check_agent_result(
        self, agent_name: str, operator_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check agent result from operator file.

        Args:
            agent_name: Name of the agent.
            operator_file_path: Optional operator file path.

        Returns:
            Dictionary with ok status and result content.
        """
        if not self.registry_manager.agent_exists(agent_name):
            return {"ok": False, "error": f"Agent '{agent_name}' not found"}

        if operator_file_path:
            op_file = Path(operator_file_path)
        else:
            # Get most recent operator file
            agent_dir = self.registry_manager.get_agent_directory(agent_name)
            op_file = self.operator_file_manager.get_latest_operator_file(agent_dir)
            if not op_file:
                return {"ok": False, "error": "No operator files found"}

        content = self.operator_file_manager.read_operator_file(op_file)
        if content is None:
            return {"ok": False, "error": f"Failed to read operator file: {op_file}"}

        return {"ok": True, "data": {"file": str(op_file), "content": content}}

    def delete_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Delete an agent from registry.

        Args:
            agent_name: Name of the agent.

        Returns:
            Dictionary with ok status.
        """
        if self.registry_manager.delete_agent(agent_name):
            return {"ok": True, "data": {"message": f"Agent '{agent_name}' deleted"}}
        return {"ok": False, "error": f"Agent '{agent_name}' not found"}
