"""
Prompt management for Claude Code agents.

Handles reading and rendering prompt templates for agent creation and operation.
"""

from pathlib import Path
from typing import Any

from ...config import PROMPTS_DIR


class PromptManager:
    """Manages prompt templates for Claude Code agents."""

    @staticmethod
    def read_prompt(relative_path: str) -> str:
        """
        Read prompt file from super_agent directory.

        Args:
            relative_path: Relative path to prompt file.

        Returns:
            Prompt content as string.

        Raises:
            FileNotFoundError: If prompt file doesn't exist.
            RuntimeError: If file cannot be read.
        """
        prompt_path = PROMPTS_DIR / "super_agent" / relative_path
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        try:
            return prompt_path.read_text(encoding="utf-8").strip()
        except Exception as exc:
            raise RuntimeError(f"Failed to read prompt {relative_path}: {exc}") from exc

    @staticmethod
    def render_prompt(relative_path: str, **kwargs: Any) -> str:
        """
        Render prompt template with variables.

        Args:
            relative_path: Relative path to prompt file.
            **kwargs: Template variables.

        Returns:
            Rendered prompt string.
        """
        template = PromptManager.read_prompt(relative_path)
        if kwargs:
            return template.format(**kwargs)
        return template
