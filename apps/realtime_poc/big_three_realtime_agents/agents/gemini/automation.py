"""
Browser automation loop logic for Gemini agent.

Manages turn-based interaction with Gemini API, screenshot capture,
and conversation flow for browser automation tasks.
"""

import logging
from pathlib import Path

from playwright.sync_api import Page
from google.genai import types
from google.genai.types import Content, Part
from rich.panel import Panel

from ...config import GEMINI_MODEL
from ...utils import console
from ...utils.retry import retry_with_backoff
from ...utils.circuit_breaker import get_circuit_breaker, CircuitBreakerError
from ...timeouts import GEMINI_API_TIMEOUT
from .functions import GeminiFunctionHandler
from .screenshot_manager import ScreenshotManager


class BrowserAutomationLoop:
    """Manages turn-based browser automation with Gemini."""

    def __init__(
        self,
        gemini_client,
        page: Page,
        screenshot_dir: Path,
        logger: logging.Logger,
    ):
        """
        Initialize automation loop.

        Args:
            gemini_client: Gemini API client.
            page: Playwright page instance.
            screenshot_dir: Directory for saving screenshots.
            logger: Logger instance.
        """
        self.gemini_client = gemini_client
        self.page = page
        self.logger = logger

        # Initialize managers
        self.function_handler = GeminiFunctionHandler(page, logger)
        self.screenshot_manager = ScreenshotManager(page, screenshot_dir, logger)

    @retry_with_backoff(
        max_attempts=3,
        initial_delay=2.0,
        exceptions=(ConnectionError, TimeoutError, OSError, Exception),
    )
    def _call_gemini_api_with_retry(self, contents, config):
        """
        Call Gemini API with retry logic, timeout, and circuit breaker.

        Features:
        - Circuit breaker prevents cascading failures
        - Automatic retry on transient failures
        - Exponential backoff (2s, 4s, 8s)

        Args:
            contents: Conversation contents.
            config: Generation config.

        Returns:
            API response.

        Raises:
            CircuitBreakerError: If circuit is open.
            Exception: If all retry attempts fail.
        """
        self.logger.debug(f"Calling Gemini API (timeout: {GEMINI_API_TIMEOUT}s)")

        # Get circuit breaker for Gemini API
        breaker = get_circuit_breaker(
            name="gemini_api",
            failure_threshold=5,
            recovery_timeout=60.0,  # Longer for API recovery
            logger=self.logger
        )

        # Execute with circuit breaker protection
        def api_call():
            return self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            )

        return breaker.call(api_call)

    def run(self, task: str, max_turns: int = 30) -> str:
        """
        Run the Gemini Computer Use agent loop to complete the task.

        Args:
            task: The browsing task to complete.
            max_turns: Maximum number of agent turns.

        Returns:
            The final result as a string.
        """
        # Configure Gemini with Computer Use
        config = types.GenerateContentConfig(
            tools=[
                types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER
                    )
                )
            ],
        )

        # Initial screenshot
        initial_screenshot = self.screenshot_manager.capture_and_save("initial")

        # Build initial contents
        contents = [
            Content(
                role="user",
                parts=[
                    Part(text=task),
                    Part.from_bytes(data=initial_screenshot, mime_type="image/png"),
                ],
            )
        ]

        self.logger.info(f"Starting browser automation loop for task: {task}")

        # Agent loop
        for turn in range(max_turns):
            self.logger.info(f"Turn {turn + 1}/{max_turns}")

            try:
                # Get response from Gemini with retry logic
                response = self._call_gemini_api_with_retry(contents, config)

                candidate = response.candidates[0]
                contents.append(candidate.content)

                # Check if there are function calls
                has_function_calls = any(
                    part.function_call for part in candidate.content.parts
                )

                if not has_function_calls:
                    # No more actions - extract final text response
                    text_response = " ".join(
                        [part.text for part in candidate.content.parts if part.text]
                    )
                    self.logger.info(f"Agent finished: {text_response}")

                    console.print(Panel(text_response, title="GeminiBrowserAgent"))

                    # Save final screenshot
                    self.screenshot_manager.capture_and_save("final")

                    return text_response

                # Execute function calls
                self.logger.info("Executing browser actions...")
                results = self.function_handler.execute_function_calls(candidate)

                # Get function responses with new screenshot
                function_responses = self.function_handler.get_function_responses(results)

                # Save screenshot after actions
                self.screenshot_manager.capture_and_save(f"turn_{turn + 1}")

                # Add function responses to contents
                contents.append(
                    Content(
                        role="user",
                        parts=[Part(function_response=fr) for fr in function_responses],
                    )
                )

            except Exception as e:
                self.logger.error(f"Error in browser automation loop: {e}")
                raise

        # If we hit max turns, return what we have
        return f"Task reached maximum turns ({max_turns}). Please check browser state."
