"""
Claude Max Coder - Agentic coder using Claude Max subscription.

Provides Claude Code agent functionality using claude.ai web interface
instead of Anthropic API.
"""

import logging
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .claude_max_adapter import ClaudeMaxAdapter
from ...utils.registry import AgentRegistry

logger = logging.getLogger(__name__)


class ClaudeMaxCoder:
    """
    Claude Code agent using Max subscription (browser-based).

    Provides same interface as ClaudeCodeAgenticCoder but uses
    claude.ai web interface instead of API.

    Example:
        >>> coder = ClaudeMaxCoder()
        >>> coder.initialize()
        >>> result = coder.create_agent("backend_dev")
        >>> coder.command_agent("backend_dev", "Build REST API")
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        headless: bool = False
    ):
        """
        Initialize Claude Max coder.

        Args:
            logger: Optional logger instance
            headless: Run browser in headless mode
        """
        self.logger = logger or logging.getLogger(__name__)

        # Agent registry
        registry_path = Path("apps/content-gen/agents/claude_max/registry.json")
        self.registry = AgentRegistry(registry_path)

        # Browser adapter
        self.adapter = ClaudeMaxAdapter(
            headless=headless,
            session_dir=Path("apps/content-gen/claude_sessions")
        )

        self.is_initialized = False

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize browser and prepare for agent operations.

        Returns:
            Initialization result
        """
        # Initialize browser
        result = self.adapter.initialize()
        if not result.get("ok"):
            return result

        # Check if logged in
        if not self.adapter.check_login_status():
            self.logger.info("Not logged in to claude.ai")
            self.logger.info("Please login in the browser window")

            # Wait for manual login
            if not self.adapter.wait_for_login(timeout=120):
                return {
                    "ok": False,
                    "error": "Login timeout - please login to claude.ai"
                }

        self.is_initialized = True
        self.logger.info("Claude Max Coder initialized and ready")

        return {
            "ok": True,
            "message": "Claude Max Coder ready (using claude.ai web interface)",
            "mode": "browser_automation"
        }

    def create_agent(
        self,
        agent_name: str,
        agent_type: str = "agentic_coding",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Claude Max agent.

        Args:
            agent_name: Agent name
            agent_type: Agent type
            system_prompt: Optional system prompt

        Returns:
            Agent creation result
        """
        if not self.is_initialized:
            return {"ok": False, "error": "Adapter not initialized"}

        # Check for duplicate
        if self.registry.get_agent_by_name(agent_name):
            return {"ok": False, "error": f"Agent '{agent_name}' already exists"}

        try:
            # Start new chat for this agent
            if not self.adapter.start_new_chat():
                return {"ok": False, "error": "Failed to start new chat"}

            # Generate session ID
            session_id = f"max_session_{uuid.uuid4().hex[:16]}"

            # Send system prompt if provided
            if system_prompt:
                intro_message = f"""You are {agent_name}, an expert AI coding assistant.

{system_prompt}

Please confirm you understand your role and are ready to help with coding tasks.
Respond with a brief acknowledgment."""

                response = self.adapter.send_message(intro_message)
                if not response.get("ok"):
                    return {"ok": False, "error": "Failed to send intro message"}

            # Register agent
            agent_data = {
                "tool": "claude_max",
                "type": agent_type,
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "mode": "browser_automation",
                "operators": []
            }

            self.registry.register_agent(agent_name, agent_data)

            self.logger.info(f"Created Claude Max agent: {agent_name}")

            return {
                "ok": True,
                "agent_name": agent_name,
                "session_id": session_id,
                "tool": "claude_max",
                "mode": "browser_automation",
                "message": f"Agent '{agent_name}' created using Claude Max subscription"
            }

        except Exception as exc:
            self.logger.error(f"Failed to create agent: {exc}")
            return {"ok": False, "error": str(exc)}

    def command_agent(
        self,
        agent_name: str,
        prompt: str,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Send command to Claude Max agent.

        Args:
            agent_name: Agent name
            prompt: Command/prompt to send
            timeout: Maximum wait time for response

        Returns:
            Command execution result
        """
        if not self.is_initialized:
            return {"ok": False, "error": "Adapter not initialized"}

        # Get agent
        agent = self.registry.get_agent_by_name(agent_name)
        if not agent:
            return {"ok": False, "error": f"Agent '{agent_name}' not found"}

        try:
            # Send message to Claude
            response = self.adapter.send_message(
                message=prompt,
                wait_for_response=True,
                timeout=timeout
            )

            if not response.get("ok"):
                return response

            # Create operator file for tracking
            operator_file = self._create_operator_file(agent_name, prompt, response)

            # Update agent operators list
            agent_data = self.registry.get_agent_by_name(agent_name)
            agent_data["operators"].append(operator_file)
            self.registry.update_agent(agent_name, agent_data)

            self.logger.info(f"Command sent to {agent_name}: {prompt[:50]}...")

            return {
                "ok": True,
                "agent_name": agent_name,
                "response": response.get("content"),
                "operator_file": operator_file,
                "mode": "browser_automation"
            }

        except Exception as exc:
            self.logger.error(f"Failed to command agent: {exc}")
            return {"ok": False, "error": str(exc)}

    def list_agents(self) -> Dict[str, Any]:
        """List all Claude Max agents."""
        agents_data = self.registry.list_agents()

        agents = [
            {
                "name": name,
                "session_id": data.get("session_id"),
                "tool": "claude_max",
                "type": data.get("type"),
                "created_at": data.get("created_at"),
                "operators": data.get("operators", []),
                "mode": "browser_automation"
            }
            for name, data in agents_data.items()
        ]

        return {
            "ok": True,
            "agents": agents,
            "total": len(agents)
        }

    def delete_agent(self, agent_name: str) -> Dict[str, Any]:
        """Delete a Claude Max agent."""
        if self.registry.delete_agent(agent_name):
            self.logger.info(f"Deleted agent: {agent_name}")
            return {"ok": True, "message": f"Agent '{agent_name}' deleted"}
        else:
            return {"ok": False, "error": f"Agent '{agent_name}' not found"}

    def _create_operator_file(
        self,
        agent_name: str,
        prompt: str,
        response: Dict[str, Any]
    ) -> str:
        """Create operator file for command tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_slug = prompt[:30].replace(" ", "_").replace("/", "_")
        operator_file = f"{timestamp}_{task_slug}.md"

        # Create operator directory
        operator_dir = Path(f"apps/content-gen/agents/claude_max/{agent_name}/operators")
        operator_dir.mkdir(parents=True, exist_ok=True)

        # Write operator file
        operator_path = operator_dir / operator_file
        content = f"""# Claude Max Agent Operation

**Agent**: {agent_name}
**Timestamp**: {datetime.now().isoformat()}
**Mode**: Browser Automation (Claude Max)

## Task
{prompt}

## Response
{response.get('content', 'No response')}

## Metadata
- Session ID: {self.registry.get_agent_by_name(agent_name).get('session_id')}
- Tool: claude_max (browser automation)
- Status: Completed
"""

        operator_path.write_text(content)

        return str(operator_path.relative_to(Path("apps/content-gen")))

    def cleanup(self) -> None:
        """Cleanup browser resources."""
        self.adapter.cleanup()
        self.is_initialized = False
        self.logger.info("Claude Max Coder cleaned up")
