"""
Gemini function call handlers for browser automation.

Handles execution of Gemini Computer Use function calls using Playwright
and formats responses with screenshots.
"""

import logging
from typing import List, Tuple, Dict, Any

from playwright.sync_api import Page
from google.genai import types

from .browser_actions import BrowserActionExecutor


class GeminiFunctionHandler:
    """Handles Gemini Computer Use function call execution."""

    def __init__(self, page: Page, logger: logging.Logger):
        """
        Initialize function handler.

        Args:
            page: Playwright page instance.
            logger: Logger instance.
        """
        self.page = page
        self.logger = logger
        self.action_executor = BrowserActionExecutor(page, logger)

    def execute_function_calls(self, candidate) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Execute Gemini Computer Use function calls using Playwright.

        Args:
            candidate: Gemini API response candidate with function calls.

        Returns:
            List of (function_name, result_dict) tuples.
        """
        results = []
        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call
        ]

        for function_call in function_calls:
            fname = function_call.name
            args = function_call.args
            self.logger.info(f"Executing Gemini action: {fname}")

            action_result = self.action_executor.execute_action(fname, args)
            results.append((fname, action_result))

        return results

    def get_function_responses(
        self, results: List[Tuple[str, Dict[str, Any]]]
    ) -> List[types.FunctionResponse]:
        """
        Generate function responses with current screenshot.

        Args:
            results: List of (function_name, result_dict) tuples.

        Returns:
            List of Gemini FunctionResponse objects.
        """
        screenshot_bytes = self.page.screenshot(type="png")
        current_url = self.page.url
        function_responses = []

        for name, result in results:
            response_data = {"url": current_url}
            response_data.update(result)
            function_responses.append(
                types.FunctionResponse(
                    name=name,
                    response=response_data,
                    parts=[
                        types.FunctionResponsePart(
                            inline_data=types.FunctionResponseBlob(
                                mime_type="image/png", data=screenshot_bytes
                            )
                        )
                    ],
                )
            )

        return function_responses
