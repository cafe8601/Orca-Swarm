"""
Learning System - Pattern recognition and continuous improvement.

Tracks execution outcomes, identifies patterns, and provides
recommendations for improved agent and workflow performance.

Modules:
    learning_manager: Central learning coordinator
    outcome_tracker: Track success/failure patterns
    pattern_analyzer: Analyze and extract patterns
    recommender: Suggest approaches based on history

Example:
    >>> from .learning_manager import LearningManager
    >>> learning = LearningManager(memory_manager)
    >>> learning.record_outcome(task, agent, result)
    >>> recommendations = learning.get_recommendations(similar_task)
"""

from .learning_manager import LearningManager
from .outcome_tracker import OutcomeTracker
from .pattern_analyzer import PatternAnalyzer

__all__ = [
    "LearningManager",
    "OutcomeTracker",
    "PatternAnalyzer",
]
