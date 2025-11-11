"""
Context store - Persistent project context storage.

Stores long-term project context, patterns, and knowledge
that persists across sessions.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..exceptions import ValidationError, MemoryStoreError

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

    def _sanitize_key(self, key: str) -> str:
        """
        Sanitize context key to prevent path traversal attacks.

        Args:
            key: Raw context key

        Returns:
            Sanitized key

        Raises:
            ValidationError: If key is invalid or dangerous
        """
        # Only allow alphanumeric, underscore, hyphen
        safe_key = re.sub(r'[^a-zA-Z0-9_-]', '', key)

        if not safe_key:
            raise ValidationError(f"Invalid context key: '{key}' - must contain alphanumeric characters")

        if safe_key != key:
            raise ValidationError(
                f"Invalid context key: '{key}' contains forbidden characters. "
                f"Allowed: alphanumeric, underscore, hyphen"
            )

        # Prevent path traversal attempts
        if '..' in key or '/' in key or '\\' in key:
            raise ValidationError(f"Path traversal detected in context key: '{key}'")

        return safe_key

    def save_context(
        self,
        context_key: str,
        context_data: Dict[str, Any]
    ) -> None:
        """
        Save persistent context.

        Args:
            context_key: Context identifier (alphanumeric, underscore, hyphen only)
            context_data: Context data to store

        Raises:
            ValidationError: If context_key contains invalid characters
            MemoryStoreError: If save operation fails
        """
        # Sanitize key to prevent path traversal
        safe_key = self._sanitize_key(context_key)
        context_file = self.storage_dir / f"{safe_key}.json"

        # Verify path stays within storage_dir (defense in depth)
        try:
            resolved_path = context_file.resolve()
            if not resolved_path.is_relative_to(self.storage_dir.resolve()):
                raise ValidationError(f"Path traversal attempt detected: {context_key}")
        except ValueError as e:
            raise ValidationError(f"Invalid path: {context_key}") from e

        try:
            context_file.write_text(json.dumps(context_data, indent=2))
            logger.info(f"Saved context: {safe_key}")
        except Exception as exc:
            logger.error(f"Failed to save context {safe_key}: {exc}")
            raise MemoryStoreError(f"Cannot save context: {exc}") from exc

    def load_context(self, context_key: str) -> Optional[Dict[str, Any]]:
        """
        Load persistent context.

        Args:
            context_key: Context identifier

        Returns:
            Context data or None if not found

        Raises:
            ValidationError: If context_key is invalid
        """
        # Sanitize key
        safe_key = self._sanitize_key(context_key)
        context_file = self.storage_dir / f"{safe_key}.json"

        # Verify path (defense in depth)
        try:
            if not context_file.resolve().is_relative_to(self.storage_dir.resolve()):
                raise ValidationError(f"Path traversal attempt: {context_key}")
        except ValueError as e:
            raise ValidationError(f"Invalid path: {context_key}") from e

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
        safe_key = self._sanitize_key(context_key)
        context_file = self.storage_dir / f"{safe_key}.json"

        if context_file.exists():
            context_file.unlink()
            logger.info(f"Deleted context: {safe_key}")
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
