"""
Audio interface management for OpenAI Realtime API.

Handles audio input/output coordination, microphone/speaker management,
and audio stream processing.
"""

import logging
from typing import Optional

from ...utils import AudioManager


class AudioInterface:
    """
    Manages audio input/output interface for voice interactions.

    Coordinates microphone and speaker resources, handles audio state
    management, and provides audio setup/cleanup functionality.
    """

    def __init__(
        self,
        logger: logging.Logger,
        input_mode: str,
        output_mode: str,
    ):
        """
        Initialize audio interface.

        Args:
            logger: Logger instance for audio events.
            input_mode: Input mode ("text" or "audio").
            output_mode: Output mode ("text" or "audio").
        """
        self.logger = logger
        self.input_mode = input_mode
        self.output_mode = output_mode

        # Audio state management
        self.audio_state = {
            "enabled": input_mode == "audio" or output_mode == "audio",
            "paused": False,
            "auto_paused": False,
        }

        # Audio manager instance
        self.audio_manager = AudioManager(logger=self.logger)

    def is_audio_enabled(self) -> bool:
        """
        Check if audio is enabled for this session.

        Returns:
            True if audio input or output is enabled.
        """
        return self.audio_state["enabled"]

    def is_paused(self) -> bool:
        """
        Check if audio is currently paused.

        Returns:
            True if audio is paused.
        """
        return self.audio_state["paused"]

    def pause_audio(self):
        """Pause audio input/output."""
        self.audio_state["paused"] = True
        self.logger.info("Audio paused")

    def resume_audio(self):
        """Resume audio input/output."""
        self.audio_state["paused"] = False
        self.logger.info("Audio resumed")

    def set_auto_paused(self, paused: bool):
        """
        Set auto-pause state for audio.

        Args:
            paused: Whether audio should be auto-paused.
        """
        self.audio_state["auto_paused"] = paused

    def setup_audio(self):
        """Setup audio resources (microphone/speaker)."""
        if not self.audio_state["enabled"]:
            return

        self.logger.info("Setting up audio resources...")
        self.audio_manager.setup(
            input_enabled=(self.input_mode == "audio"),
            output_enabled=(self.output_mode == "audio"),
        )
        self.logger.info("Audio resources initialized")

    def cleanup_audio(self):
        """Cleanup audio resources."""
        if not self.audio_state["enabled"]:
            return

        self.logger.info("Cleaning up audio resources...")
        self.audio_manager.cleanup()
        self.logger.info("Audio resources released")

    def get_audio_manager(self) -> AudioManager:
        """
        Get the audio manager instance.

        Returns:
            AudioManager instance for direct audio operations.
        """
        return self.audio_manager

    def get_audio_state(self) -> dict:
        """
        Get current audio state.

        Returns:
            Dictionary containing audio state information.
        """
        return self.audio_state
