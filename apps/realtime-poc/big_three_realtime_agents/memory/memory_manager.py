"""
Central memory manager coordinating different memory types.

Provides unified interface for session, workflow, and context memory.
"""

import logging
from typing import Any, Optional, Dict, List
from enum import Enum
from pathlib import Path

from .session_memory import SessionMemory
from .workflow_memory import WorkflowMemory
from .context_store import ContextStore

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Memory storage types."""
    SESSION = "session"          # In-memory session data
    WORKFLOW = "workflow"        # Workflow execution history
    CONTEXT = "context"          # Project context (persistent)
    LEARNING = "learning"        # Success/failure patterns


class MemoryManager:
    """
    Central memory management system.

    Coordinates different memory types and provides unified access.

    Attributes:
        session: In-memory session cache
        workflow: Workflow execution history
        storage_dir: Directory for persistent storage

    Example:
        >>> manager = MemoryManager()
        >>> manager.store("api_spec", spec_data, MemoryType.SESSION)
        >>> spec = manager.retrieve("api_spec", MemoryType.SESSION)
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize memory manager.

        Args:
            storage_dir: Directory for persistent storage
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path("memory_store")
        self.storage_dir.mkdir(exist_ok=True)

        # Initialize memory subsystems
        self.session = SessionMemory()
        self.workflow = WorkflowMemory(self.storage_dir / "workflows")
        self.context = ContextStore(self.storage_dir / "context")

        logger.info("Memory manager initialized")

    def store(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SESSION
    ) -> None:
        """
        Store value in specified memory type.

        Args:
            key: Storage key
            value: Value to store
            memory_type: Type of memory storage
        """
        if memory_type == MemoryType.SESSION:
            self.session.set(key, value)
        elif memory_type == MemoryType.WORKFLOW:
            self.workflow.store_execution(key, value)
        elif memory_type == MemoryType.CONTEXT:
            self.context.save_context(key, value)
        else:
            logger.warning(f"Memory type '{memory_type}' not yet implemented")

    def retrieve(
        self,
        key: str,
        memory_type: MemoryType = MemoryType.SESSION
    ) -> Optional[Any]:
        """
        Retrieve value from specified memory type.

        Args:
            key: Storage key
            memory_type: Type of memory storage

        Returns:
            Stored value or None if not found
        """
        if memory_type == MemoryType.SESSION:
            return self.session.get(key)
        elif memory_type == MemoryType.WORKFLOW:
            return self.workflow.get_execution(key)
        elif memory_type == MemoryType.CONTEXT:
            return self.context.load_context(key)
        else:
            logger.warning(f"Memory type '{memory_type}' not yet implemented")
            return None

    def get_session_context(self) -> Dict[str, Any]:
        """Get all session context for agent use."""
        return {
            "session_data": self.session.get_all(),
            "recent_workflows": self.workflow.get_recent(limit=5),
            "active_agents": self.session.get("active_agents", []),
        }

    def store_agent_context(self, agent_id: str, context: Dict[str, Any]) -> None:
        """Store agent-specific context."""
        agent_contexts = self.session.get("agent_contexts", {})
        agent_contexts[agent_id] = context
        self.session.set("agent_contexts", agent_contexts)

    def get_agent_context(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent-specific context."""
        agent_contexts = self.session.get("agent_contexts", {})
        return agent_contexts.get(agent_id)

    def clear_session(self) -> None:
        """Clear session memory."""
        self.session.clear()
        logger.info("Session memory cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "session_keys": len(self.session.storage),
            "workflow_count": self.workflow.count(),
            "context_count": len(self.context.list_contexts()),
            "storage_dir": str(self.storage_dir),
        }
