"""
Logging configuration for Big Three Realtime Agents.

Provides centralized logging setup with file-based output.
"""

import logging
from datetime import datetime
from pathlib import Path


def setup_logging(base_dir: Path = None) -> logging.Logger:
    """
    Setup logging to file only (no stdout).

    Args:
        base_dir: Base directory for log output. Defaults to parent directory.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("BigThreeAgents")
    logger.setLevel(logging.DEBUG)

    # Return existing logger if already configured
    if logger.handlers:
        return logger

    logger.propagate = False

    # Create log directory
    if base_dir is None:
        base_dir = Path(__file__).parent.parent
    log_dir = base_dir / "output_logs"
    log_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    now = datetime.now()
    log_filename = log_dir / f"{now.strftime('%Y-%m-%d_%H')}.log"

    # Configure file handler
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    logger.addHandler(file_handler)
    logger.info(f"Logging initialized. Log file: {log_filename}")

    return logger
