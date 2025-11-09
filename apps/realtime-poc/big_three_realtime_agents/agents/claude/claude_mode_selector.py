"""
Claude mode selector - Choose between API and Max subscription modes.

Provides unified interface that works with either Anthropic API
or Claude Max browser automation.
"""

import os
import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ClaudeMode(Enum):
    """Claude operation modes."""
    API = "api"                    # Use Anthropic API (requires API key)
    MAX = "max"                    # Use Claude Max subscription (browser)
    AUTO = "auto"                  # Auto-detect based on API key availability


class ClaudeModeSelector:
    """
    Select and configure Claude operation mode.

    Automatically detects available mode or allows manual selection.

    Example:
        >>> selector = ClaudeModeSelector()
        >>> mode = selector.detect_mode()
        >>> print(mode)  # ClaudeMode.API or ClaudeMode.MAX
    """

    def __init__(self):
        """Initialize mode selector."""
        self.logger = logger

    def detect_mode(self, preferred: ClaudeMode = ClaudeMode.AUTO) -> ClaudeMode:
        """
        Detect available Claude operation mode.

        Args:
            preferred: Preferred mode (AUTO for auto-detection)

        Returns:
            Available Claude mode
        """
        if preferred == ClaudeMode.API:
            if self._check_api_available():
                return ClaudeMode.API
            else:
                self.logger.warning("API mode requested but API key not available")
                return ClaudeMode.MAX

        elif preferred == ClaudeMode.MAX:
            return ClaudeMode.MAX

        else:  # AUTO
            if self._check_api_available():
                self.logger.info("Anthropic API key found - using API mode")
                return ClaudeMode.API
            else:
                self.logger.info("No API key - using Claude Max browser mode")
                return ClaudeMode.MAX

    def _check_api_available(self) -> bool:
        """Check if Anthropic API key is available."""
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        # Check if key exists and is not empty/placeholder
        if not api_key or api_key.startswith("sk-ant-placeholder"):
            return False

        return True

    def get_mode_info(self, mode: ClaudeMode) -> Dict[str, Any]:
        """
        Get information about a Claude mode.

        Args:
            mode: Claude mode

        Returns:
            Mode information dict
        """
        if mode == ClaudeMode.API:
            return {
                "mode": "api",
                "name": "Anthropic API",
                "requires": "ANTHROPIC_API_KEY environment variable",
                "benefits": [
                    "Faster response times",
                    "No browser overhead",
                    "Programmatic control",
                    "Multiple concurrent agents"
                ],
                "limitations": [
                    "Requires paid API subscription",
                    "API usage costs"
                ]
            }
        else:  # MAX
            return {
                "mode": "max",
                "name": "Claude Max Browser",
                "requires": "Claude Max subscription + browser login",
                "benefits": [
                    "Use existing Max subscription",
                    "No additional API costs",
                    "Access to latest Claude features"
                ],
                "limitations": [
                    "Slower (browser automation overhead)",
                    "Requires browser window",
                    "Single concurrent chat per browser",
                    "Manual login required"
                ]
            }

    def create_coder_instance(self, mode: ClaudeMode, **kwargs):
        """
        Create appropriate coder instance for mode.

        Args:
            mode: Claude operation mode
            **kwargs: Additional arguments for coder

        Returns:
            ClaudeCodeAgenticCoder or ClaudeMaxCoder instance
        """
        if mode == ClaudeMode.API:
            from .coder import ClaudeCodeAgenticCoder
            return ClaudeCodeAgenticCoder(**kwargs)
        else:  # MAX
            from .claude_max_coder import ClaudeMaxCoder
            return ClaudeMaxCoder(**kwargs)

    def get_recommended_mode(self) -> ClaudeMode:
        """
        Get recommended mode based on environment.

        Returns:
            Recommended Claude mode
        """
        if self._check_api_available():
            return ClaudeMode.API  # API is faster and more reliable
        else:
            return ClaudeMode.MAX  # Fallback to Max subscription
