"""
Unified Claude coder interface supporting both API and Max modes.

Provides transparent switching between Anthropic API and Claude Max
browser automation based on configuration.
"""

import logging
from typing import Dict, Any, Optional

from ...config import get_claude_mode, is_api_mode, is_max_mode

logger = logging.getLogger(__name__)


class UnifiedClaudeCoder:
    """
    Unified interface for Claude coding agents.

    Automatically uses API or Max mode based on configuration.

    Example:
        >>> coder = UnifiedClaudeCoder()
        >>> coder.initialize()  # Auto-detects mode
        >>> result = coder.create_agent("backend_dev")
    """

    def __init__(self, logger: Optional[logging.Logger] = None, **kwargs):
        """
        Initialize unified coder.

        Args:
            logger: Optional logger instance
            **kwargs: Additional arguments passed to underlying coder
        """
        self.logger = logger or logging.getLogger(__name__)
        self.mode = get_claude_mode()
        self.backend = None
        self.kwargs = kwargs

        self.logger.info(f"Unified Claude Coder initializing in '{self.mode}' mode")

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize appropriate Claude backend.

        Returns:
            Initialization result
        """
        try:
            if is_api_mode():
                from .coder import ClaudeCodeAgenticCoder
                self.backend = ClaudeCodeAgenticCoder(
                    logger=self.logger,
                    **self.kwargs
                )
                self.logger.info("Using Anthropic API mode")
                return {"ok": True, "mode": "api", "backend": "Anthropic API"}

            else:  # Max mode
                from .claude_max_coder import ClaudeMaxCoder
                self.backend = ClaudeMaxCoder(
                    logger=self.logger,
                    headless=self.kwargs.get("headless", False)
                )

                # Initialize browser
                result = self.backend.initialize()
                if result.get("ok"):
                    self.logger.info("Using Claude Max browser mode")
                    return {
                        "ok": True,
                        "mode": "max",
                        "backend": "Claude Max Browser",
                        "message": "Browser initialized - ensure you're logged in to claude.ai"
                    }
                else:
                    return result

        except Exception as exc:
            self.logger.error(f"Failed to initialize: {exc}")
            return {"ok": False, "error": str(exc)}

    def create_agent(
        self,
        agent_name: str,
        agent_type: str = "agentic_coding",
        tool: str = "claude_code",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create agent using current backend.

        Args:
            agent_name: Agent name
            agent_type: Agent type
            tool: Tool identifier
            system_prompt: Optional system prompt override

        Returns:
            Agent creation result
        """
        if not self.backend:
            return {"ok": False, "error": "Backend not initialized"}

        if is_api_mode():
            # API mode - use full create_agent signature
            return self.backend.create_agent(
                agent_name=agent_name,
                agent_type=agent_type,
                tool=tool
            )
        else:
            # Max mode - use simplified signature
            return self.backend.create_agent(
                agent_name=agent_name,
                agent_type=agent_type,
                system_prompt=system_prompt
            )

    def command_agent(
        self,
        agent_name: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Command agent (works with both modes).

        Args:
            agent_name: Agent name
            prompt: Command prompt
            **kwargs: Additional arguments

        Returns:
            Command result
        """
        if not self.backend:
            return {"ok": False, "error": "Backend not initialized"}

        return self.backend.command_agent(agent_name, prompt, **kwargs)

    def list_agents(self) -> Dict[str, Any]:
        """List all agents."""
        if not self.backend:
            return {"ok": False, "error": "Backend not initialized"}

        result = self.backend.list_agents()

        # Add mode information
        if result.get("ok"):
            result["mode"] = self.mode

        return result

    def delete_agent(self, agent_name: str) -> Dict[str, Any]:
        """Delete agent."""
        if not self.backend:
            return {"ok": False, "error": "Backend not initialized"}

        return self.backend.delete_agent(agent_name)

    def get_mode_info(self) -> Dict[str, Any]:
        """Get current mode information."""
        return {
            "mode": self.mode,
            "backend": type(self.backend).__name__ if self.backend else None,
            "initialized": self.backend is not None,
        }

    def cleanup(self) -> None:
        """Cleanup backend resources."""
        if self.backend and hasattr(self.backend, 'cleanup'):
            self.backend.cleanup()
            self.logger.info("Unified coder cleaned up")
