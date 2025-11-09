"""Filesystem tools for OpenAI Realtime Agent."""

import subprocess
import logging
from pathlib import Path
from typing import Dict, Any

from ...config import AGENT_WORKING_DIRECTORY


class FilesystemTools:
    """Filesystem operation tools."""

    def __init__(self, logger: logging.Logger, ui_logger):
        self.logger = logger
        self.ui_logger = ui_logger

    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open a file in VS Code or default system application."""
        try:
            full_path = AGENT_WORKING_DIRECTORY / file_path

            if not full_path.exists():
                return {"ok": False, "error": f"File not found: {file_path}"}

            # Determine if it's a media file
            media_extensions = {
                ".mp3", ".mp4", ".wav", ".m4a", ".aac", ".flac", ".ogg",
                ".mov", ".avi", ".mkv", ".webm", ".wmv", ".flv", ".m4v",
            }

            file_ext = full_path.suffix.lower()
            is_media = file_ext in media_extensions

            # Choose command based on file type
            if is_media:
                command = f'open "{full_path}"'
                app_name = "default system application"
            else:
                command = f'code "{full_path}"'
                app_name = "VS Code"

            self.ui_logger(
                f"Opening: {file_path}\nFull path: {full_path}\nUsing: {app_name}",
                title="Open File",
                style="cyan",
            )

            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                self.ui_logger(
                    f"Successfully opened {file_path} in {app_name}",
                    title="Open File - Success",
                    style="green",
                )
                return {
                    "ok": True,
                    "file_path": str(full_path),
                    "opened_with": app_name,
                }
            else:
                error_msg = result.stderr or "Unknown error"
                self.ui_logger(
                    f"Failed to open file: {error_msg}",
                    title="Open File - Error",
                    style="red",
                    level="error",
                )
                return {"ok": False, "error": error_msg}

        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Command timed out after 5 seconds"}
        except Exception as exc:
            self.logger.exception("Failed to open file")
            return {"ok": False, "error": str(exc)}

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read and return the contents of a file."""
        try:
            full_path = AGENT_WORKING_DIRECTORY / file_path

            if not full_path.exists():
                return {"ok": False, "error": f"File not found: {file_path}"}

            if full_path.is_dir():
                return {
                    "ok": False,
                    "error": f"Path is a directory, not a file: {file_path}",
                }

            try:
                content = full_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return {"ok": False, "error": f"File is not a text file: {file_path}"}

            self.ui_logger(
                f"File: {file_path}\nSize: {len(content)} characters\nLines: {len(content.splitlines())}",
                title="Read File",
                style="cyan",
            )

            return {
                "ok": True,
                "file_path": str(full_path),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
            }

        except Exception as exc:
            self.logger.exception("Failed to read file")
            return {"ok": False, "error": str(exc)}
