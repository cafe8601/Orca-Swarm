"""
Base agent class for Big Three Realtime Agents.

Provides common functionality for all agent types.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """Abstract base class for all agent types."""

    def __init__(self, logger: Optional[logging.Logger] = None, session_id: Optional[str] = None):
        """
        Initialize base agent.

        Args:
            logger: Optional logger instance.
            session_id: Optional session ID. Generated if not provided.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.session_id = session_id or str(uuid.uuid4())

    @abstractmethod
    def setup(self):
        """Setup agent resources and connections."""
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup agent resources."""
        pass

    @abstractmethod
    def execute_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task with the agent.

        Args:
            task: Task description.
            **kwargs: Additional task parameters.

        Returns:
            Dictionary containing task results.
        """
        pass

    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def log_debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(message)
