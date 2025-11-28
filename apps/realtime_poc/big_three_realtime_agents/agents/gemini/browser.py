"""
Core GeminiBrowserAgent class for browser automation.

Handles browser setup, task execution, and registry management using
Gemini Computer Use API with Playwright integration.
"""

import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from playwright.sync_api import sync_playwright

from ...config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TOOL,
    GEMINI_TOOL_SLUG,
    AGENTIC_BROWSERING_TYPE,
    GEMINI_REGISTRY_PATH,
    AGENTS_BASE_DIR,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BROWSER_TOOL_STARTING_URL,
)
from ...utils import AgentRegistry
from ..base import BaseAgent
from .automation import BrowserAutomationLoop
from .screenshot_manager import ScreenshotManager


class GeminiBrowserAgent(BaseAgent):
    """
    Browser automation agent powered by Gemini Computer Use API.

    Handles web browsing, navigation, and interaction tasks using
    Gemini's vision and action planning capabilities with Playwright.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize browser agent."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        super().__init__(logger, session_id=session_id)

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        self.gemini_client = genai.GenerativeModel(GEMINI_MODEL)

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Initialize screenshot directory
        self.screenshot_dir = AGENTS_BASE_DIR / "gemini" / "screenshots" / self.session_id
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_counter = 0

        self.registry = AgentRegistry(
            registry_path=GEMINI_REGISTRY_PATH,
            base_dir=AGENTS_BASE_DIR,
            tool_slug=GEMINI_TOOL_SLUG,
            agent_type=AGENTIC_BROWSERING_TYPE,
            logger=self.logger,
        )

        self.logger.info(f"Browser session ID: {self.session_id}")
        self.logger.info(f"Screenshots: {self.screenshot_dir}")
        self.logger.info("Initialized GeminiBrowserAgent")

    def setup(self):
        """Initialize Playwright browser."""
        try:
            self.logger.info("Initializing browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.context = self.browser.new_context(
                viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
            )
            self.page = self.context.new_page()
            self.logger.info("Browser ready!")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    def cleanup(self):
        """Clean up Playwright browser resources."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Browser cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Browser cleanup error: {e}")

    def execute_task(
        self, task: str, agent_name: Optional[str] = None,
        url: Optional[str] = None, max_turns: int = 30
    ) -> Dict[str, Any]:
        """Execute a browser automation task."""
        try:
            self.logger.info(f"Task: {task}")
            self.logger.info(f"Starting URL: {url or BROWSER_TOOL_STARTING_URL}")
            self.logger.info(f"Session ID: {self.session_id}")

            if agent_name:
                # Register agent in registry
                self.registry.set_session(agent_name, self.session_id)

            if not self.page:
                self.setup()

            # Navigate to starting URL
            start_url = url or BROWSER_TOOL_STARTING_URL
            self.logger.info(f"Navigating to {start_url}")
            self.page.goto(start_url)

            automation_loop = BrowserAutomationLoop(
                gemini_client=self.gemini_client,
                page=self.page,
                screenshot_dir=self.screenshot_dir,
                logger=self.logger,
            )
            result = automation_loop.run(task, max_turns)
            self.logger.info(f"Task completed! Screenshots: {self.screenshot_dir}")

            return {
                "ok": True,
                "data": result,
                "screenshot_dir": str(self.screenshot_dir),
            }

        except Exception as exc:
            self.logger.exception("Browser automation failed")
            return {"ok": False, "error": str(exc)}
