"""
Coordinate transformation utilities for browser automation.

Handles conversion between normalized coordinates (0-999) and actual
screen pixel coordinates based on configured viewport dimensions.
"""

from ...config import SCREEN_WIDTH, SCREEN_HEIGHT


def denormalize_x(x: int) -> int:
    """
    Convert normalized x coordinate (0-999) to actual pixel coordinate.

    Gemini Computer Use API uses normalized coordinates in the range [0, 999]
    for position-independent interaction. This function transforms those
    coordinates to actual screen pixels based on the configured viewport width.

    Args:
        x: Normalized x coordinate in range [0, 999].

    Returns:
        Actual pixel x coordinate based on SCREEN_WIDTH.

    Example:
        >>> denormalize_x(500)  # Assuming SCREEN_WIDTH=1280
        640
    """
    return int(x / 1000 * SCREEN_WIDTH)


def denormalize_y(y: int) -> int:
    """
    Convert normalized y coordinate (0-999) to actual pixel coordinate.

    Gemini Computer Use API uses normalized coordinates in the range [0, 999]
    for position-independent interaction. This function transforms those
    coordinates to actual screen pixels based on the configured viewport height.

    Args:
        y: Normalized y coordinate in range [0, 999].

    Returns:
        Actual pixel y coordinate based on SCREEN_HEIGHT.

    Example:
        >>> denormalize_y(500)  # Assuming SCREEN_HEIGHT=720
        360
    """
    return int(y / 1000 * SCREEN_HEIGHT)


def denormalize_coordinates(x: int, y: int) -> tuple[int, int]:
    """
    Convert normalized coordinate pair to actual pixel coordinates.

    Convenience function that transforms both x and y coordinates
    simultaneously from normalized [0, 999] range to actual screen pixels.

    Args:
        x: Normalized x coordinate in range [0, 999].
        y: Normalized y coordinate in range [0, 999].

    Returns:
        Tuple of (pixel_x, pixel_y) coordinates.

    Example:
        >>> denormalize_coordinates(500, 500)
        (640, 360)  # Assuming 1280x720 viewport
    """
    return denormalize_x(x), denormalize_y(y)


def calculate_scroll_amount(magnitude: int) -> int:
    """
    Calculate scroll distance in pixels from normalized magnitude.

    Converts a normalized scroll magnitude (typically 0-1000) to actual
    pixel distance based on screen height for consistent scroll behavior
    across different viewport sizes.

    Args:
        magnitude: Normalized scroll magnitude value.

    Returns:
        Scroll distance in pixels.

    Example:
        >>> calculate_scroll_amount(800)  # Assuming SCREEN_HEIGHT=720
        576
    """
    return int(magnitude * SCREEN_HEIGHT / 1000)
