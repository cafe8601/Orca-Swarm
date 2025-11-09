"""
Browser action execution handlers for Gemini Computer Use.

Implements Playwright-based browser automation actions for Gemini function calls.
"""

import time
import logging
from playwright.sync_api import Page

from .coordinate_utils import denormalize_x, denormalize_y, calculate_scroll_amount


class BrowserActionExecutor:
    """Executes browser actions using Playwright."""

    def __init__(self, page: Page, logger: logging.Logger):
        """
        Initialize action executor.

        Args:
            page: Playwright page instance.
            logger: Logger instance.
        """
        self.page = page
        self.logger = logger

    def execute_action(self, function_name: str, args: dict) -> dict:
        """
        Execute a browser action.

        Args:
            function_name: Name of the action to execute.
            args: Action arguments.

        Returns:
            Result dictionary (empty on success, error key on failure).
        """
        try:
            self._dispatch_action(function_name, args)

            # Wait for potential navigations/renders
            self.page.wait_for_load_state(timeout=5000)
            time.sleep(1)

            return {}
        except Exception as e:
            self.logger.error(f"Error executing {function_name}: {e}")
            return {"error": str(e)}

    def _dispatch_action(self, function_name: str, args: dict) -> None:
        """
        Dispatch action to appropriate handler.

        Args:
            function_name: Action name.
            args: Action arguments.
        """
        action_map = {
            "open_web_browser": lambda: None,  # Already open
            "wait_5_seconds": lambda: time.sleep(5),
            "go_back": lambda: self.page.go_back(),
            "go_forward": lambda: self.page.go_forward(),
            "search": lambda: self.page.goto("https://www.google.com"),
            "navigate": lambda: self._navigate(args),
            "click_at": lambda: self._click_at(args),
            "hover_at": lambda: self._hover_at(args),
            "type_text_at": lambda: self._type_text_at(args),
            "key_combination": lambda: self._key_combination(args),
            "scroll_document": lambda: self._scroll_document(args),
            "scroll_at": lambda: self._scroll_at(args),
            "drag_and_drop": lambda: self._drag_and_drop(args),
        }

        handler = action_map.get(function_name)
        if handler:
            handler()
        else:
            self.logger.warning(f"Unimplemented action: {function_name}")

    def _navigate(self, args: dict) -> None:
        """Navigate to URL."""
        self.page.goto(args["url"], wait_until="networkidle", timeout=10000)

    def _click_at(self, args: dict) -> None:
        """Click at normalized coordinates."""
        actual_x = denormalize_x(args["x"])
        actual_y = denormalize_y(args["y"])
        self.page.mouse.click(actual_x, actual_y)

    def _hover_at(self, args: dict) -> None:
        """Hover at normalized coordinates."""
        actual_x = denormalize_x(args["x"])
        actual_y = denormalize_y(args["y"])
        self.page.mouse.move(actual_x, actual_y)

    def _type_text_at(self, args: dict) -> None:
        """Type text at normalized coordinates."""
        actual_x = denormalize_x(args["x"])
        actual_y = denormalize_y(args["y"])
        text = args["text"]
        press_enter = args.get("press_enter", True)
        clear_before = args.get("clear_before_typing", True)

        self.page.mouse.click(actual_x, actual_y)
        if clear_before:
            self.page.keyboard.press("Meta+A")
            self.page.keyboard.press("Backspace")
        self.page.keyboard.type(text)
        if press_enter:
            self.page.keyboard.press("Enter")

    def _key_combination(self, args: dict) -> None:
        """Press key combination."""
        keys = args["keys"]
        self.page.keyboard.press(keys)

    def _scroll_document(self, args: dict) -> None:
        """Scroll entire document."""
        direction = args["direction"]
        key_map = {
            "down": "PageDown",
            "up": "PageUp",
            "left": "ArrowLeft",
            "right": "ArrowRight",
        }
        key = key_map.get(direction)
        if key:
            self.page.keyboard.press(key)

    def _scroll_at(self, args: dict) -> None:
        """Scroll at specific normalized coordinates."""
        actual_x = denormalize_x(args["x"])
        actual_y = denormalize_y(args["y"])
        direction = args["direction"]
        magnitude = args.get("magnitude", 800)

        # Move to position and scroll
        self.page.mouse.move(actual_x, actual_y)
        scroll_amount = calculate_scroll_amount(magnitude)

        if direction == "down":
            self.page.mouse.wheel(0, scroll_amount)
        elif direction == "up":
            self.page.mouse.wheel(0, -scroll_amount)
        elif direction == "left":
            self.page.mouse.wheel(-scroll_amount, 0)
        elif direction == "right":
            self.page.mouse.wheel(scroll_amount, 0)

    def _drag_and_drop(self, args: dict) -> None:
        """Drag and drop between normalized coordinates."""
        x = denormalize_x(args["x"])
        y = denormalize_y(args["y"])
        dest_x = denormalize_x(args["destination_x"])
        dest_y = denormalize_y(args["destination_y"])

        self.page.mouse.move(x, y)
        self.page.mouse.down()
        self.page.mouse.move(dest_x, dest_y)
        self.page.mouse.up()
