"""
Screenshot management for Gemini browser automation.

Handles screenshot capture, saving, and tracking for browser automation sessions.
"""

import logging
from pathlib import Path
from datetime import datetime

from playwright.sync_api import Page


class ScreenshotManager:
    """Manages screenshot capture and storage."""

    def __init__(
        self,
        page: Page,
        screenshot_dir: Path,
        logger: logging.Logger,
    ):
        """
        Initialize screenshot manager.

        Args:
            page: Playwright page instance.
            screenshot_dir: Directory for saving screenshots.
            logger: Logger instance.
        """
        self.page = page
        self.screenshot_dir = screenshot_dir
        self.logger = logger
        self.counter = 0

    def capture_and_save(self, label: str) -> bytes:
        """
        Capture screenshot and save to disk.

        Args:
            label: Label for the screenshot (e.g., "initial", "final", "turn_1").

        Returns:
            Screenshot bytes.
        """
        screenshot_bytes = self.page.screenshot(type="png")
        self._save_to_disk(label)
        return screenshot_bytes

    def capture_only(self) -> bytes:
        """
        Capture screenshot without saving.

        Returns:
            Screenshot bytes.
        """
        return self.page.screenshot(type="png")

    def _save_to_disk(self, label: str) -> None:
        """
        Save screenshot to disk with timestamp.

        Args:
            label: Label for the screenshot.
        """
        timestamp = datetime.now().strftime("%H%M%S")
        screenshot_path = (
            self.screenshot_dir
            / f"step_{self.counter:02d}_{label}_{timestamp}.png"
        )
        self.page.screenshot(path=str(screenshot_path))
        self.logger.info(f"Saved screenshot: {screenshot_path}")
        self.counter += 1

    def get_current_url(self) -> str:
        """
        Get current page URL.

        Returns:
            Current page URL.
        """
        return self.page.url
