"""
Learning manager - Coordinate pattern recognition and recommendations.

Central coordinator for learning system, integrating outcome tracking,
pattern analysis, and recommendation generation.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .outcome_tracker import OutcomeTracker
from .pattern_analyzer import PatternAnalyzer

logger = logging.getLogger(__name__)


class LearningManager:
    """
    Central learning system coordinator.

    Tracks outcomes, analyzes patterns, and provides recommendations
    for improved agent and workflow performance.

    Example:
        >>> learning = LearningManager(storage_dir="memory/learning")
        >>> learning.record_task_outcome(task, agent, result, success=True)
        >>> recommendations = learning.get_recommendations(new_task)
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize learning manager.

        Args:
            storage_dir: Directory for learning data storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.tracker = OutcomeTracker(self.storage_dir)
        self.analyzer = PatternAnalyzer(self.tracker)

        self.logger = logger
        self.logger.info("Learning manager initialized")

    def record_task_outcome(
        self,
        task: str,
        agent_id: str,
        result: Dict[str, Any],
        success: bool
    ) -> None:
        """
        Record task execution outcome.

        Args:
            task: Task description
            agent_id: Agent that executed task
            result: Execution result
            success: Whether task succeeded
        """
        if success:
            self.tracker.record_success(task, agent_id, result)
        else:
            error = result.get("error", "Unknown error")
            self.tracker.record_failure(task, agent_id, error)

    def get_recommendations(self, task: str) -> Dict[str, Any]:
        """
        Get recommendations for task execution.

        Args:
            task: Task description

        Returns:
            Dict with recommended agent and confidence
        """
        # Find best agent from history
        best_agent, confidence = self.analyzer.get_best_agent_for_task(task)

        # Find similar tasks
        similar_tasks = self.analyzer.find_similar_tasks(task, limit=3)

        recommendations = {
            "recommended_agent": best_agent,
            "confidence": confidence,
            "reason": "Based on historical performance",
            "similar_tasks": [
                {
                    "task": t.get("task", "")[:80],
                    "agent": t.get("agent_id"),
                    "status": t.get("status"),
                }
                for t in similar_tasks
            ],
        }

        if confidence > 0.7:
            recommendations["reason"] = (
                f"{best_agent} has {confidence*100:.0f}% success rate on similar tasks"
            )
        elif confidence > 0.0:
            recommendations["reason"] = (
                f"{best_agent} showed {confidence*100:.0f}% success on similar tasks "
                "(moderate confidence)"
            )
        else:
            recommendations["reason"] = "No historical data, using intelligent selection"

        self.logger.info(
            f"Recommendations for task: {best_agent} (confidence: {confidence:.2f})"
        )

        return recommendations

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning system statistics."""
        patterns = self.analyzer.analyze_agent_task_patterns()

        return {
            "total_outcomes": len(self.tracker._outcomes),
            "agents_tracked": len(patterns["agent_success_rates"]),
            "top_keywords": patterns["task_keywords"].most_common(10),
            "agent_performance": patterns["agent_success_rates"],
        }

    def suggest_agent_for_task(
        self,
        task: str,
        pool_selector
    ) -> str:
        """
        Suggest best agent combining history and pool selection.

        Args:
            task: Task description
            pool_selector: IntelligentAgentSelector instance

        Returns:
            Recommended agent ID
        """
        # Get historical recommendation
        best_from_history, confidence = self.analyzer.get_best_agent_for_task(task)

        # If high confidence from history, use it
        if confidence > 0.7:
            self.logger.info(
                f"Using historical recommendation: {best_from_history} "
                f"(confidence: {confidence:.2f})"
            )
            return best_from_history

        # Otherwise use intelligent selection
        best_from_pool = pool_selector.select_best_agent(task)

        self.logger.info(
            f"Using pool selection: {best_from_pool} "
            f"(low historical confidence: {confidence:.2f})"
        )

        return best_from_pool or best_from_history
