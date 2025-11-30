"""Filesystem tools for OpenAI Realtime Agent."""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any

from ...config import AGENT_WORKING_DIRECTORY

# Security constants
MAX_FILE_SIZE_MB = 10  # Maximum file size to read (10 MB)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class FilesystemTools:
    """Filesystem operation tools."""

    def __init__(self, logger: logging.Logger, ui_logger):
        self.logger = logger
        self.ui_logger = ui_logger

    def open_file(self, file_path: str) -> Dict[str, Any]:
        """
        Open a file in VS Code or default system application with security validations.

        Security features:
        - Path traversal prevention
        - Command injection prevention (shell=False)
        """
        try:
            full_path = AGENT_WORKING_DIRECTORY / file_path

            # Security: Path traversal prevention
            real_path = full_path.resolve()
            base_path = AGENT_WORKING_DIRECTORY.resolve()

            if not str(real_path).startswith(str(base_path)):
                return {
                    "ok": False,
                    "error": f"Access denied: Path traversal attempt detected"
                }

            if not full_path.exists():
                return {"ok": False, "error": f"File not found: {file_path}"}

            # Determine if it's a media file
            media_extensions = {
                ".mp3", ".mp4", ".wav", ".m4a", ".aac", ".flac", ".ogg",
                ".mov", ".avi", ".mkv", ".webm", ".wmv", ".flv", ".m4v",
            }

            file_ext = full_path.suffix.lower()
            is_media = file_ext in media_extensions

            # Build command safely (no shell injection)
            if is_media:
                command = ["open", str(real_path)]
                app_name = "default system application"
            else:
                command = ["code", str(real_path)]
                app_name = "VS Code"

            self.ui_logger(
                f"Opening: {file_path}\nFull path: {full_path}\nUsing: {app_name}",
                title="Open File",
                style="cyan",
            )

            # Security: shell=False prevents command injection
            result = subprocess.run(
                command, shell=False, capture_output=True, text=True, timeout=5
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
        except PermissionError as e:
            self.logger.exception("Permission denied")
            return {"ok": False, "error": f"Permission denied: {e}"}
        except Exception as exc:
            self.logger.exception("Failed to open file")
            return {"ok": False, "error": str(exc)}

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and return the contents of a file with security validations.
        
        Security features:
        - Path traversal prevention
        - File size limit (10 MB)
        - Permission error handling
        """
        try:
            full_path = AGENT_WORKING_DIRECTORY / file_path

            # Security: Path traversal prevention
            real_path = full_path.resolve()
            base_path = AGENT_WORKING_DIRECTORY.resolve()
            
            if not str(real_path).startswith(str(base_path)):
                return {
                    "ok": False,
                    "error": f"Access denied: Path traversal attempt detected"
                }

            if not full_path.exists():
                return {"ok": False, "error": f"File not found: {file_path}"}

            if full_path.is_dir():
                return {
                    "ok": False,
                    "error": f"Path is a directory, not a file: {file_path}",
                }

            # Security: File size validation
            file_size = os.path.getsize(real_path)
            if file_size > MAX_FILE_SIZE_BYTES:
                file_size_mb = file_size / (1024 * 1024)
                return {
                    "ok": False,
                    "error": f"File too large: {file_size_mb:.1f}MB (max {MAX_FILE_SIZE_MB}MB)"
                }

            try:
                content = full_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return {"ok": False, "error": f"File is not a text file: {file_path}"}
            except PermissionError as e:
                return {"ok": False, "error": f"Permission denied: {e}"}

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

        except PermissionError as e:
            self.logger.exception("Permission denied")
            return {"ok": False, "error": f"Permission denied: {e}"}
        except Exception as exc:
            self.logger.exception("Failed to read file")
            return {"ok": False, "error": str(exc)}
