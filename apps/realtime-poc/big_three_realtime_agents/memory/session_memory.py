"""
Session memory - In-memory cache for current session context.

Provides fast access to session-scoped data like active agents,
user preferences, and temporary context.
"""

import logging
from typing import Any, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionMemory:
    """
    In-memory session cache.

    Fast access to session-scoped data with automatic timestamps.

    Example:
        >>> session = SessionMemory()
        >>> session.set("user_prefs", {"theme": "dark"})
        >>> prefs = session.get("user_prefs")
    """

    def __init__(self):
        """Initialize session memory."""
        self.storage: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()

    def set(self, key: str, value: Any) -> None:
        """
        Store value in session memory.

        Args:
            key: Storage key
            value: Value to store (must be JSON-serializable)
        """
        self.storage[key] = {
            "value": value,
            "updated_at": datetime.now(),
        }
        logger.debug(f"Session memory set: {key}")

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieve value from session memory.

        Args:
            key: Storage key
            default: Default value if key not found

        Returns:
            Stored value or default
        """
        entry = self.storage.get(key)
        if entry:
            return entry["value"]
        return default

    def get_all(self) -> Dict[str, Any]:
        """Get all session data."""
        return {
            key: entry["value"]
            for key, entry in self.storage.items()
        }

    def delete(self, key: str) -> bool:
        """
        Delete key from session memory.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if not found
        """
        if key in self.storage:
            del self.storage[key]
            logger.debug(f"Session memory deleted: {key}")
            return True
        return False

    def clear(self) -> None:
        """Clear all session memory."""
        self.storage.clear()
        logger.info("Session memory cleared")

    def has(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.storage

    def keys(self) -> List[str]:
        """Get all storage keys."""
        return list(self.storage.keys())

    def size(self) -> int:
        """Get number of stored items."""
        return len(self.storage)

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a key."""
        entry = self.storage.get(key)
        if entry:
            return {
                "updated_at": entry["updated_at"],
                "age_seconds": (datetime.now() - entry["updated_at"]).total_seconds()
            }
        return None
