"""
Agent naming logic for Claude Code agents.

Handles name generation, validation, and deduplication using LLM-based naming.
"""

import uuid
import logging
from typing import List

from .llm_name_generator import LLMNameGenerator


class AgentNaming:
    """Handles agent name generation and validation."""

    def __init__(self, logger: logging.Logger):
        """
        Initialize agent naming handler.

        Args:
            logger: Logger instance for diagnostic output.
        """
        self.logger = logger
        self.llm_generator = LLMNameGenerator(logger)

    async def generate_unique_name(
        self, existing_names: List[str], preferred_name: str = None
    ) -> str:
        """
        Generate a unique agent name.

        Args:
            existing_names: List of existing agent names to avoid collisions.
            preferred_name: Optional preferred name to use if available.

        Returns:
            A unique agent name.
        """
        if preferred_name:
            return await self._dedupe_agent_name(preferred_name, existing_names)

        candidate_name = await self._generate_agent_name(existing_names)
        return await self._dedupe_agent_name(candidate_name, existing_names)

    async def _generate_agent_name(self, existing_names: List[str]) -> str:
        """
        Generate creative agent name using Claude LLM.

        Args:
            existing_names: List of existing names to inform generation.

        Returns:
            Generated agent name or fallback UUID-based name.
        """
        try:
            name = await self.llm_generator.generate_name(existing_names)
            validated_name = self._validate_name(name)
            self.logger.debug(f"Generated agent name: {validated_name}")
            return validated_name
        except Exception as exc:
            self.logger.warning(f"Name generation failed: {exc}, using fallback")
            return self._generate_fallback_name()

    def _validate_name(self, name: str) -> str:
        """
        Validate and clean generated name.

        Args:
            name: Raw name from LLM.

        Returns:
            Validated name or fallback if invalid.
        """
        if not name or len(name) < 2 or len(name) > 50:
            return self._generate_fallback_name()

        # Remove potentially problematic characters
        cleaned = "".join(c for c in name if c.isalnum() or c in "_-")

        if not cleaned:
            return self._generate_fallback_name()

        return cleaned

    def _generate_fallback_name(self) -> str:
        """
        Generate fallback name when LLM generation fails.

        Returns:
            UUID-based fallback name.
        """
        return f"agent_{uuid.uuid4().hex[:8]}"

    async def _dedupe_agent_name(
        self, candidate: str, existing_names: List[str]
    ) -> str:
        """
        Ensure agent name uniqueness through deduplication.

        Args:
            candidate: Candidate name to check.
            existing_names: List of existing names to check against.

        Returns:
            Unique agent name (original or with numeric suffix).
        """
        if candidate not in existing_names:
            return candidate

        # Try numeric suffixes
        for i in range(2, 100):
            deduped = f"{candidate}_{i}"
            if deduped not in existing_names:
                self.logger.debug(f"Deduped name: {candidate} -> {deduped}")
                return deduped

        # Fallback to UUID suffix if all numeric suffixes exhausted
        uuid_suffix = uuid.uuid4().hex[:8]
        final_name = f"{candidate}_{uuid_suffix}"
        self.logger.warning(
            f"Exhausted numeric suffixes for {candidate}, using UUID: {final_name}"
        )
        return final_name
