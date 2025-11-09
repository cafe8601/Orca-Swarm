"""
UI formatting utilities for Big Three Realtime Agents.

Handles complex formatting operations for agent roster display.
"""

from pathlib import Path
from typing import Dict, Any, List


def format_relative_paths(files: List[str], working_directory: Path) -> List[str]:
    """
    Extract relative paths from working directory.

    Args:
        files: List of file paths.
        working_directory: Base working directory.

    Returns:
        List of relative path strings.
    """
    relative_paths = []
    for f in files:
        try:
            rel_path = Path(f).relative_to(working_directory)
            relative_paths.append(str(rel_path))
        except ValueError:
            # If path is not relative to working directory, use filename only
            relative_paths.append(Path(f).name)
    return relative_paths


def get_most_recent_file(relative_paths: List[str]) -> str:
    """
    Get most recent file from list (last item).

    Args:
        relative_paths: List of relative file paths.

    Returns:
        Most recent file path or em-dash if empty.
    """
    return relative_paths[-1] if relative_paths else "—"
