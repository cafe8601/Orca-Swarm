"""
Operator file management for Claude Code agents.

Handles operator file creation, path generation, and slug generation
for task logging and result tracking.
"""

import asyncio
from pathlib import Path
from typing import Optional
import logging


class OperatorFileManager:
    """Manages operator file creation and organization."""

    def __init__(self, logger: logging.Logger, agent_executor):
        """
        Initialize operator file manager.

        Args:
            logger: Logger instance.
            agent_executor: Agent executor for LLM queries.
        """
        self.logger = logger
        self.agent_executor = agent_executor

    async def prepare_operator_file(
        self, agent_dir: Path, prompt: str
    ) -> Path:
        """
        Prepare operator log file for task.

        Args:
            agent_dir: Agent directory path.
            prompt: Task prompt.

        Returns:
            Path to operator file.
        """
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Generate slug from prompt
        slug = await self._generate_slug(prompt)

        filename = f"{slug}.md"
        operator_file = agent_dir / filename

        self.logger.debug(f"Prepared operator file: {operator_file}")
        return operator_file

    async def _generate_slug(self, prompt: str) -> str:
        """
        Generate filename slug from prompt using LLM.

        Args:
            prompt: Task prompt.

        Returns:
            Cleaned slug string.
        """
        slug_prompt = (
            f"Generate a short filename slug (3-5 words, lowercase, hyphens) "
            f"for: {prompt[:100]}"
        )

        slug = await self.agent_executor.collect_text_from_query(slug_prompt)
        return self._clean_slug(slug)

    def _clean_slug(self, raw_slug: str) -> str:
        """
        Clean and normalize slug string.

        Args:
            raw_slug: Raw slug from LLM.

        Returns:
            Cleaned slug (max 50 chars, lowercase, hyphens).
        """
        cleaned = raw_slug.strip().replace(" ", "-").lower()
        # Remove any non-alphanumeric except hyphens
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "-")
        return cleaned[:50]

    def get_latest_operator_file(self, agent_dir: Path) -> Optional[Path]:
        """
        Get most recent operator file in agent directory.

        Args:
            agent_dir: Agent directory path.

        Returns:
            Path to latest operator file or None if none exist.
        """
        op_files = sorted(
            agent_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime
        )

        if not op_files:
            self.logger.warning(f"No operator files found in {agent_dir}")
            return None

        latest = op_files[-1]
        self.logger.debug(f"Latest operator file: {latest}")
        return latest

    def read_operator_file(self, operator_file: Path) -> Optional[str]:
        """
        Read operator file content.

        Args:
            operator_file: Path to operator file.

        Returns:
            File content or None if read fails.
        """
        if not operator_file.exists():
            self.logger.error(f"Operator file not found: {operator_file}")
            return None

        try:
            content = operator_file.read_text(encoding="utf-8")
            return content
        except Exception as exc:
            self.logger.error(f"Failed to read operator file: {exc}")
            return None
