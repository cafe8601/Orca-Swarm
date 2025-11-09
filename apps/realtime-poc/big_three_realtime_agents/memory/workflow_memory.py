"""
Workflow memory - Execution history and task tracking.

Stores workflow execution records for learning and debugging.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowMemory:
    """
    Workflow execution history storage.

    Tracks workflow executions for learning and pattern analysis.

    Example:
        >>> workflow_mem = WorkflowMemory(storage_dir="memory/workflows")
        >>> workflow_mem.store_execution("task_123", execution_data)
        >>> recent = workflow_mem.get_recent(limit=5)
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize workflow memory.

        Args:
            storage_dir: Directory for workflow storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.storage_dir / "index.json"
        self._index: List[Dict[str, Any]] = self._load_index()

    def store_execution(
        self,
        execution_id: str,
        execution_data: Dict[str, Any]
    ) -> None:
        """
        Store workflow execution record.

        Args:
            execution_id: Unique execution identifier
            execution_data: Execution details and results
        """
        # Add timestamp
        execution_data["stored_at"] = datetime.now().isoformat()
        execution_data["execution_id"] = execution_id

        # Write execution file
        exec_file = self.storage_dir / f"{execution_id}.json"
        exec_file.write_text(json.dumps(execution_data, indent=2))

        # Update index
        self._index.append({
            "execution_id": execution_id,
            "timestamp": execution_data["stored_at"],
            "task": execution_data.get("task", "")[:100],
            "status": execution_data.get("status", "unknown"),
        })
        self._save_index()

        logger.info(f"Stored workflow execution: {execution_id}")

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve workflow execution record.

        Args:
            execution_id: Execution identifier

        Returns:
            Execution data or None if not found
        """
        exec_file = self.storage_dir / f"{execution_id}.json"
        if not exec_file.exists():
            return None

        try:
            return json.loads(exec_file.read_text())
        except Exception as exc:
            logger.error(f"Failed to load execution {execution_id}: {exc}")
            return None

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions."""
        return self._index[-limit:] if self._index else []

    def count(self) -> int:
        """Get total number of stored workflows."""
        return len(self._index)

    def search_by_task(self, keyword: str) -> List[Dict[str, Any]]:
        """Search workflows by task keyword."""
        keyword_lower = keyword.lower()
        return [
            entry for entry in self._index
            if keyword_lower in entry.get("task", "").lower()
        ]

    def _load_index(self) -> List[Dict[str, Any]]:
        """Load workflow index."""
        if not self._index_file.exists():
            return []

        try:
            return json.loads(self._index_file.read_text())
        except Exception as exc:
            logger.error(f"Failed to load workflow index: {exc}")
            return []

    def _save_index(self) -> None:
        """Save workflow index."""
        try:
            self._index_file.write_text(json.dumps(self._index, indent=2))
        except Exception as exc:
            logger.error(f"Failed to save workflow index: {exc}")
