"""
System prompt management for OpenAI Realtime Agent.

Loads and renders system prompt with agent roster.
"""

from pathlib import Path
import logging

from ...config import PROMPTS_DIR, REALTIME_ORCH_AGENT_NAME, ENGINEER_NAME


class SystemPromptManager:
    """Manages system prompt for OpenAI Realtime Agent."""

    def __init__(self, logger: logging.Logger, agentic_coder):
        """
        Initialize system prompt manager.

        Args:
            logger: Logger instance.
            agentic_coder: ClaudeCodeAgenticCoder instance.
        """
        self.logger = logger
        self.agentic_coder = agentic_coder

    def load_system_prompt(self) -> str:
        """
        Load system prompt for the orchestrator.

        Returns:
            System prompt string with agent roster.
        """
        prompt_file = (
            PROMPTS_DIR / "super_agent" / "realtime_super_agent_system_prompt.md"
        )
        try:
            if prompt_file.exists():
                base_prompt = prompt_file.read_text(encoding="utf-8").strip()
                base_prompt = base_prompt.format(
                    AGENT_NAME=REALTIME_ORCH_AGENT_NAME, ENGINEER_NAME=ENGINEER_NAME
                )
            else:
                base_prompt = (
                    "You are a helpful voice assistant with advanced capabilities."
                )
        except Exception as e:
            self.logger.error(f"Error loading prompt file: {e}")
            base_prompt = (
                "You are a helpful voice assistant with advanced capabilities."
            )

        # Append active agent roster
        agents = self.agentic_coder.registry.list_agents()
        if agents:
            roster_lines = [
                "\n# Active Agents",
                *[
                    f"- {name} · session {data.get('session_id', 'unknown')}"
                    for name, data in agents.items()
                ],
            ]
            base_prompt = f"{base_prompt}\n\n{'\n'.join(roster_lines)}"

        return base_prompt
