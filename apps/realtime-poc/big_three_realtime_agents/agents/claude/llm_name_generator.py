"""
LLM-based agent name generation using Claude SDK.

Handles Claude API interaction for creative agent name generation.
"""

import logging
from typing import List

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)


class LLMNameGenerator:
    """Generates agent names using Claude LLM."""

    def __init__(self, logger: logging.Logger):
        """
        Initialize LLM name generator.

        Args:
            logger: Logger instance for diagnostic output.
        """
        self.logger = logger

    async def generate_name(self, existing_names: List[str]) -> str:
        """
        Generate creative agent name using Claude LLM.

        Args:
            existing_names: List of existing names to inform generation.

        Returns:
            Generated agent name.
        """
        prompt = self._build_prompt(existing_names)

        try:
            name = await self._query_llm(prompt)
            self.logger.debug(f"LLM generated name: {name}")
            return name
        except Exception as exc:
            self.logger.warning(f"LLM name generation failed: {exc}")
            raise

    def _build_prompt(self, existing_names: List[str]) -> str:
        """
        Build prompt for LLM name generation.

        Args:
            existing_names: List of existing names to avoid.

        Returns:
            Formatted prompt string.
        """
        existing_display = ", ".join(existing_names) if existing_names else "none"
        return (
            f"Generate a creative, memorable name for a coding agent. "
            f"Existing names: {existing_display}. "
            f"Just output the name, nothing else."
        )

    async def _query_llm(self, prompt: str) -> str:
        """
        Query Claude LLM for name generation.

        Args:
            prompt: Name generation prompt.

        Returns:
            Generated name from LLM response.
        """
        options = ClaudeAgentOptions(model="claude-3-5-haiku-20241022")
        chunks = []

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)

        return "".join(chunks).strip()
