"""
Outcome tracker - Record task execution results.

Tracks success/failure outcomes for pattern analysis and learning.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class OutcomeTracker:
    """
    Track task execution outcomes.

    Records success/failure results for learning and pattern analysis.

    Example:
        >>> tracker = OutcomeTracker(storage_dir="memory/learning")
        >>> tracker.record_success("Build API", "backend-architect", result)
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize outcome tracker.

        Args:
            storage_dir: Directory for outcome storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._outcomes_file = self.storage_dir / "outcomes.json"
        self._outcomes = self._load_outcomes()

    def record_success(
        self,
        task: str,
        agent_id: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Record successful task execution.

        Args:
            task: Task description
            agent_id: Agent that executed task
            result: Execution result
        """
        outcome = {
            "outcome_id": f"success_{len(self._outcomes)}",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "task": task,
            "agent_id": agent_id,
            "duration": result.get("duration_seconds", 0),
            "metadata": result,
        }

        self._outcomes.append(outcome)
        self._save_outcomes()

        logger.info(f"Recorded success: {agent_id} on '{task[:50]}'")

    def record_failure(
        self,
        task: str,
        agent_id: str,
        error: str
    ) -> None:
        """
        Record failed task execution.

        Args:
            task: Task description
            agent_id: Agent that attempted task
            error: Error message
        """
        outcome = {
            "outcome_id": f"failure_{len(self._outcomes)}",
            "timestamp": datetime.now().isoformat(),
            "status": "failure",
            "task": task,
            "agent_id": agent_id,
            "error": error,
        }

        self._outcomes.append(outcome)
        self._save_outcomes()

        logger.warning(f"Recorded failure: {agent_id} on '{task[:50]}': {error}")

    def get_outcomes_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all outcomes for specific agent."""
        return [
            o for o in self._outcomes
            if o.get("agent_id") == agent_id
        ]

    def get_recent_outcomes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent outcomes."""
        return self._outcomes[-limit:] if self._outcomes else []

    def get_success_rate(self, agent_id: Optional[str] = None) -> float:
        """
        Calculate success rate.

        Args:
            agent_id: Optional agent filter

        Returns:
            Success rate (0.0 to 1.0)
        """
        outcomes = (
            self.get_outcomes_for_agent(agent_id)
            if agent_id
            else self._outcomes
        )

        if not outcomes:
            return 0.0

        successes = sum(1 for o in outcomes if o["status"] == "success")
        return successes / len(outcomes)

    def _load_outcomes(self) -> List[Dict[str, Any]]:
        """Load outcomes from storage."""
        if not self._outcomes_file.exists():
            return []

        try:
            return json.loads(self._outcomes_file.read_text())
        except Exception as exc:
            logger.error(f"Failed to load outcomes: {exc}")
            return []

    def _save_outcomes(self) -> None:
        """Save outcomes to storage."""
        try:
            self._outcomes_file.write_text(
                json.dumps(self._outcomes, indent=2)
            )
        except Exception as exc:
            logger.error(f"Failed to save outcomes: {exc}")
