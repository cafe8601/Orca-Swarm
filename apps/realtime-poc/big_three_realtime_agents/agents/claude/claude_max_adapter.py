"""
Claude Max adapter - Use Claude via claude.ai web interface.

Provides API-compatible interface using browser automation
instead of Anthropic API, enabling use with Claude Max subscription.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Page, Browser
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ...exceptions import BrowserLaunchError, ClaudeError, BrowserNavigationError

logger = logging.getLogger(__name__)


class ClaudeMaxAdapter:
    """
    Claude Max browser automation adapter.

    Provides API-compatible interface using claude.ai web interface
    instead of Anthropic API.

    Example:
        >>> adapter = ClaudeMaxAdapter()
        >>> adapter.initialize()
        >>> response = adapter.send_message("Write a Python function")
        >>> print(response["content"])
    """

    def __init__(
        self,
        headless: bool = False,
        session_dir: Optional[Path] = None
    ):
        """
        Initialize Claude Max adapter.

        Args:
            headless: Run browser in headless mode
            session_dir: Directory for browser session persistence
        """
        self.headless = headless
        self.session_dir = Path(session_dir or "apps/content-gen/claude_sessions")
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.is_initialized = False

        self.logger = logger

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize browser and navigate to claude.ai.

        Returns:
            Initialization result
        """
        try:
            self.logger.info("Initializing Claude Max adapter (browser automation)")

            # Start Playwright
            self.playwright = sync_playwright().start()

            # Launch browser with persistent context
            user_data_dir = self.session_dir / "browser_data"
            user_data_dir.mkdir(exist_ok=True)

            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=self.headless,
                viewport={"width": 1280, "height": 1024},
                args=["--disable-blink-features=AutomationControlled"]
            )

            # Open claude.ai
            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
            self.page.goto("https://claude.ai", wait_until="networkidle", timeout=30000)

            self.is_initialized = True
            self.logger.info("Claude Max adapter initialized successfully")

            return {
                "ok": True,
                "message": "Browser initialized - Please login to claude.ai if needed",
                "url": self.page.url
            }

        except PlaywrightTimeoutError as exc:
            self.logger.error(f"Browser initialization timed out: {exc}")
            return {"ok": False, "error": f"Timeout: {exc}"}
        except (BrowserLaunchError, BrowserNavigationError) as exc:
            self.logger.error(f"Browser error during initialization: {exc}")
            return {"ok": False, "error": str(exc)}
        except Exception as exc:
            self.logger.error(f"Unexpected initialization error: {exc}", exc_info=True)
            raise BrowserLaunchError(f"Claude Max adapter initialization failed: {exc}") from exc

    def check_login_status(self) -> bool:
        """
        Check if user is logged into claude.ai.

        Returns:
            True if logged in, False otherwise
        """
        if not self.page:
            return False

        try:
            # Check for chat interface elements
            # If we see new chat button, we're logged in
            chat_button = self.page.query_selector('[data-testid="new-chat-button"]')
            if chat_button:
                return True

            # Alternative: check for login button absence
            login_button = self.page.query_selector('text="Login"')
            return login_button is None

        except Exception:
            return False

    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        Wait for user to login manually.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if login successful
        """
        self.logger.info("Waiting for user to login to claude.ai...")
        self.logger.info("Please login in the browser window")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_login_status():
                self.logger.info("Login successful!")
                return True
            time.sleep(2)

        self.logger.warning("Login timeout - please ensure you're logged in")
        return False

    def start_new_chat(self) -> bool:
        """
        Start a new chat conversation.

        Returns:
            True if successful
        """
        try:
            # Click new chat button
            new_chat = self.page.query_selector('[data-testid="new-chat-button"]')
            if not new_chat:
                # Try alternative selector
                new_chat = self.page.query_selector('button:has-text("New chat")')

            if new_chat:
                new_chat.click()
                self.page.wait_for_timeout(1000)
                return True

            return False

        except Exception as exc:
            self.logger.error(f"Failed to start new chat: {exc}")
            return False

    def send_message(
        self,
        message: str,
        wait_for_response: bool = True,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Send message to Claude and wait for response.

        Args:
            message: Message to send
            wait_for_response: Wait for Claude's response
            timeout: Maximum wait time in seconds

        Returns:
            Dict with response content
        """
        if not self.is_initialized:
            return {"ok": False, "error": "Adapter not initialized"}

        try:
            # Find message input field
            input_field = self.page.query_selector('div[contenteditable="true"]')
            if not input_field:
                input_field = self.page.query_selector('textarea')

            if not input_field:
                return {"ok": False, "error": "Could not find message input field"}

            # Type message
            input_field.click()
            input_field.fill(message)

            # Send message (press Enter or click send button)
            send_button = self.page.query_selector('button[aria-label="Send Message"]')
            if send_button:
                send_button.click()
            else:
                # Fallback: press Enter
                self.page.keyboard.press("Enter")

            if not wait_for_response:
                return {"ok": True, "message": "Message sent"}

            # Wait for response
            response_content = self._wait_for_response(timeout)

            return {
                "ok": True,
                "content": response_content,
                "model": "claude-max-web",
            }

        except Exception as exc:
            self.logger.error(f"Failed to send message: {exc}")
            return {"ok": False, "error": str(exc)}

    def _wait_for_response(self, timeout: int = 120) -> str:
        """
        Wait for Claude's response to complete.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            Response content as string
        """
        start_time = time.time()

        # Wait for response to appear and complete
        while time.time() - start_time < timeout:
            # Check if still generating (look for stop button)
            stop_button = self.page.query_selector('button:has-text("Stop")')
            if stop_button:
                # Still generating, wait
                time.sleep(1)
                continue

            # Response complete - extract content
            # Find the last assistant message
            messages = self.page.query_selector_all('[data-role="assistant"]')
            if messages:
                last_message = messages[-1]
                content = last_message.inner_text()
                return content

            time.sleep(1)

        # Timeout - return what we have
        self.logger.warning("Response timeout - returning partial response")
        return self._extract_current_response()

    def _extract_current_response(self) -> str:
        """Extract current response content."""
        try:
            messages = self.page.query_selector_all('[data-role="assistant"]')
            if messages:
                return messages[-1].inner_text()
            return ""
        except Exception:
            return ""

    def cleanup(self) -> None:
        """Cleanup browser resources."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            self.is_initialized = False
            self.logger.info("Claude Max adapter cleaned up")

        except Exception as exc:
            self.logger.error(f"Cleanup error: {exc}")
