"""
Gemini Computer Use agent modules.

This package contains the GeminiBrowserAgent implementation for browser automation
using Google's Gemini Computer Use API with Playwright integration.

Modules:
    browser: Core GeminiBrowserAgent class
    functions: Gemini function call handlers and execution logic
    coordinate_utils: Coordinate transformation utilities for browser automation
    automation: Browser automation loop with turn-based interaction
"""

from .browser import GeminiBrowserAgent
from .coordinate_utils import (
    denormalize_x,
    denormalize_y,
    denormalize_coordinates,
    calculate_scroll_amount,
)

__all__ = [
    "GeminiBrowserAgent",
    "denormalize_x",
    "denormalize_y",
    "denormalize_coordinates",
    "calculate_scroll_amount",
]
