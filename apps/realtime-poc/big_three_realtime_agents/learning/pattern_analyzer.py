"""
Pattern analyzer - Identify patterns in execution outcomes.

Analyzes outcome history to identify successful patterns
and failure modes.
"""

import logging
from typing import Dict, Any, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """
    Analyze patterns in task execution outcomes.

    Identifies which agents work best for which task types.

    Example:
        >>> analyzer = PatternAnalyzer(outcome_tracker)
        >>> patterns = analyzer.analyze_agent_task_patterns()
    """

    def __init__(self, outcome_tracker):
        """
        Initialize pattern analyzer.

        Args:
            outcome_tracker: OutcomeTracker instance
        """
        self.tracker = outcome_tracker
        self.logger = logger

    def analyze_agent_task_patterns(self) -> Dict[str, Any]:
        """
        Analyze which agents excel at which tasks.

        Returns:
            Dict with agent-task patterns
        """
        outcomes = self.tracker.get_recent_outcomes(limit=100)

        patterns = {
            "agent_success_rates": {},
            "task_keywords": Counter(),
            "best_agents_by_keyword": {},
        }

        # Analyze success rates by agent
        for outcome in outcomes:
            agent_id = outcome.get("agent_id", "unknown")
            status = outcome.get("status")

            if agent_id not in patterns["agent_success_rates"]:
                patterns["agent_success_rates"][agent_id] = {
                    "total": 0,
                    "successes": 0,
                    "rate": 0.0,
                }

            patterns["agent_success_rates"][agent_id]["total"] += 1
            if status == "success":
                patterns["agent_success_rates"][agent_id]["successes"] += 1

            # Extract task keywords
            task = outcome.get("task", "").lower()
            keywords = self._extract_keywords(task)
            patterns["task_keywords"].update(keywords)

        # Calculate success rates
        for agent_id, stats in patterns["agent_success_rates"].items():
            stats["rate"] = (
                stats["successes"] / stats["total"]
                if stats["total"] > 0 else 0.0
            )

        self.logger.info(
            f"Analyzed {len(outcomes)} outcomes, "
            f"{len(patterns['agent_success_rates'])} agents"
        )

        return patterns

    def find_similar_tasks(
        self,
        task: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar previously executed tasks.

        Args:
            task: Task description
            limit: Max results

        Returns:
            List of similar task outcomes
        """
        task_keywords = set(self._extract_keywords(task.lower()))
        outcomes = self.tracker.get_recent_outcomes(limit=50)

        # Score by keyword overlap
        scored = []
        for outcome in outcomes:
            outcome_task = outcome.get("task", "").lower()
            outcome_keywords = set(self._extract_keywords(outcome_task))

            overlap = len(task_keywords & outcome_keywords)
            if overlap > 0:
                scored.append((outcome, overlap))

        # Sort by relevance
        scored.sort(key=lambda x: x[1], reverse=True)

        return [outcome for outcome, _ in scored[:limit]]

    def get_best_agent_for_task(self, task: str) -> Tuple[str, float]:
        """
        Get best performing agent for task type.

        Args:
            task: Task description

        Returns:
            Tuple of (agent_id, confidence_score)
        """
        similar_tasks = self.find_similar_tasks(task, limit=10)

        if not similar_tasks:
            return ("unknown", 0.0)

        # Count successful agents
        agent_successes = Counter()
        agent_totals = Counter()

        for outcome in similar_tasks:
            if outcome.get("status") == "success":
                agent_id = outcome.get("agent_id")
                agent_successes[agent_id] += 1
                agent_totals[agent_id] += 1

        if not agent_successes:
            return ("unknown", 0.0)

        # Best agent
        best_agent = agent_successes.most_common(1)[0][0]
        confidence = agent_successes[best_agent] / len(similar_tasks)

        return (best_agent, confidence)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "as", "is", "was"
        }

        words = text.lower().split()
        keywords = [
            w for w in words
            if len(w) > 3 and w not in stop_words
        ]

        return keywords[:10]  # Top 10 keywords
