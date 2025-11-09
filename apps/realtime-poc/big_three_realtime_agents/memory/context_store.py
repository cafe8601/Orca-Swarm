"""
Context store - Persistent project context storage.

Stores long-term project context, patterns, and knowledge
that persists across sessions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ContextStore:
    """
    Persistent context storage.

    Stores project-level context that persists across sessions.

    Example:
        >>> store = ContextStore(storage_dir="memory/context")
        >>> store.save_context("project_spec", spec_data)
        >>> spec = store.load_context("project_spec")
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize context store.

        Args:
            storage_dir: Directory for context storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_context(
        self,
        context_key: str,
        context_data: Dict[str, Any]
    ) -> None:
        """
        Save persistent context.

        Args:
            context_key: Context identifier
            context_data: Context data to store
        """
        context_file = self.storage_dir / f"{context_key}.json"

        try:
            context_file.write_text(json.dumps(context_data, indent=2))
            logger.info(f"Saved context: {context_key}")
        except Exception as exc:
            logger.error(f"Failed to save context {context_key}: {exc}")

    def load_context(self, context_key: str) -> Optional[Dict[str, Any]]:
        """
        Load persistent context.

        Args:
            context_key: Context identifier

        Returns:
            Context data or None if not found
        """
        context_file = self.storage_dir / f"{context_key}.json"

        if not context_file.exists():
            return None

        try:
            return json.loads(context_file.read_text())
        except Exception as exc:
            logger.error(f"Failed to load context {context_key}: {exc}")
            return None

    def list_contexts(self) -> List[str]:
        """List all available context keys."""
        return [
            f.stem for f in self.storage_dir.glob("*.json")
        ]

    def delete_context(self, context_key: str) -> bool:
        """Delete a context."""
        context_file = self.storage_dir / f"{context_key}.json"

        if context_file.exists():
            context_file.unlink()
            logger.info(f"Deleted context: {context_key}")
            return True

        return False

    def update_context(
        self,
        context_key: str,
        updates: Dict[str, Any]
    ) -> None:
        """
        Update existing context with new data.

        Args:
            context_key: Context identifier
            updates: Data to merge
        """
        existing = self.load_context(context_key) or {}
        existing.update(updates)
        self.save_context(context_key, existing)
