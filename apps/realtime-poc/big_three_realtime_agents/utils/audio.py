"""
Audio utilities for Big Three Realtime Agents.

Provides audio encoding/decoding and playback functionality for real-time
voice interactions with OpenAI Realtime API.

Classes:
    AudioManager: Manages audio I/O, encoding, decoding, and playback.

Dependencies:
    - pyaudio: Cross-platform audio I/O
    - numpy: Audio signal generation
    - base64: Audio data encoding for API transmission

Example:
    >>> audio_mgr = AudioManager()
    >>> audio_mgr.setup(input_enabled=True, output_enabled=True)
    >>> encoded = AudioManager.encode_audio(audio_bytes)
    >>> decoded = AudioManager.decode_audio(encoded)
    >>> audio_mgr.cleanup()
"""

import base64
import logging
from typing import Optional

import numpy as np
import pyaudio

from ..config import CHUNK_SIZE, FORMAT, CHANNELS, RATE


class AudioManager:
    """
    Manages audio interface and audio utilities.

    Handles PyAudio initialization, audio stream management, encoding/decoding
    for API transmission, and beep tone generation for user feedback.

    Attributes:
        logger: Logger instance for debugging and error reporting.
        audio_interface: PyAudio instance for audio I/O operations.
        audio_stream: Active audio stream for real-time processing.

    Example:
        >>> audio_mgr = AudioManager()
        >>> audio_mgr.setup(input_enabled=True, output_enabled=True)
        >>> # Record and encode audio
        >>> audio_data = audio_mgr.audio_stream.read(CHUNK_SIZE)
        >>> encoded = AudioManager.encode_audio(audio_data)
        >>> # Decode and play audio
        >>> decoded = AudioManager.decode_audio(encoded)
        >>> audio_mgr.audio_stream.write(decoded)
        >>> audio_mgr.cleanup()
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize audio manager.

        Args:
            logger: Optional logger instance. Creates default if not provided.
        """
        self.logger = logger or logging.getLogger("AudioManager")
        self.audio_interface: Optional[pyaudio.PyAudio] = None
        self.audio_stream: Optional[pyaudio.Stream] = None

    def setup(self, input_enabled: bool = True, output_enabled: bool = True) -> None:
        """
        Initialize PyAudio for audio input/output.

        Args:
            input_enabled: Enable audio input (microphone).
            output_enabled: Enable audio output (speakers).

        Raises:
            RuntimeError: If audio initialization fails.
            OSError: If audio device is not available.

        Note:
            If both input_enabled and output_enabled are False, this method
            returns immediately without initializing audio resources.
        """
        if not input_enabled and not output_enabled:
            self.logger.debug("Audio disabled, skipping setup")
            return

        self.logger.info("Setting up audio interface...")
        try:
            self.audio_interface = pyaudio.PyAudio()
            self.audio_stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=input_enabled,
                output=output_enabled,
                frames_per_buffer=CHUNK_SIZE,
            )
            self.logger.info("Audio interface ready")
        except OSError as e:
            self.logger.error(f"Audio device not available: {e}")
            raise RuntimeError(f"Failed to access audio device: {e}") from e
        except Exception as e:
            self.logger.error(f"Failed to setup audio: {e}")
            raise RuntimeError(f"Audio initialization failed: {e}") from e

    def cleanup(self) -> None:
        """
        Clean up audio resources.

        Safely stops and closes audio stream, then terminates PyAudio interface.
        Handles missing resources gracefully. Always call this before program exit.

        Example:
            >>> try:
            ...     audio_mgr.setup()
            ...     # Use audio_mgr
            ... finally:
            ...     audio_mgr.cleanup()
        """
        try:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            if self.audio_interface:
                self.audio_interface.terminate()
                self.audio_interface = None
            self.logger.info("Audio interface cleaned up")
        except Exception as e:
            self.logger.warning(f"Error during audio cleanup: {e}")

    @staticmethod
    def encode_audio(audio_bytes: bytes) -> str:
        """
        Encode audio bytes to base64 for API transmission.

        Args:
            audio_bytes: Raw audio bytes in PCM format.

        Returns:
            Base64-encoded ASCII string suitable for JSON transmission.

        Raises:
            TypeError: If audio_bytes is not bytes type.

        Example:
            >>> audio_data = b'\\x00\\x01\\x02\\x03'
            >>> encoded = AudioManager.encode_audio(audio_data)
            >>> isinstance(encoded, str)
            True
        """
        if not isinstance(audio_bytes, bytes):
            raise TypeError(f"Expected bytes, got {type(audio_bytes)}")
        return base64.b64encode(audio_bytes).decode("ascii")

    @staticmethod
    def decode_audio(base64_str: str) -> bytes:
        """
        Decode base64 audio to bytes for playback.

        Args:
            base64_str: Base64-encoded audio string from API.

        Returns:
            Decoded audio bytes in PCM format.

        Raises:
            TypeError: If base64_str is not string type.
            ValueError: If base64_str is not valid base64.

        Example:
            >>> encoded = "AAECAw=="
            >>> decoded = AudioManager.decode_audio(encoded)
            >>> isinstance(decoded, bytes)
            True
        """
        if not isinstance(base64_str, str):
            raise TypeError(f"Expected str, got {type(base64_str)}")
        try:
            return base64.b64decode(base64_str)
        except Exception as e:
            raise ValueError(f"Invalid base64 string: {e}") from e

    def play_beep(
        self,
        frequency: int = 440,
        duration: float = 0.12,
        volume: float = 0.15
    ) -> None:
        """
        Play a soft beep tone (blocking operation).

        Generates and plays a pure sine wave tone for user feedback.
        Uses separate PyAudio instance to avoid interfering with main audio stream.

        Args:
            frequency: Tone frequency in Hz. Default 440Hz (A4 note).
            duration: Tone duration in seconds. Default 0.12s.
            volume: Volume level from 0.0 (silent) to 1.0 (max). Default 0.15.

        Note:
            This is a blocking operation. The method will not return until
            the beep has finished playing.

        Example:
            >>> audio_mgr = AudioManager()
            >>> audio_mgr.play_beep(frequency=880, duration=0.2, volume=0.3)
        """
        try:
            sample_rate = RATE

            # Generate sine wave
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            beep = (np.sin(frequency * t * 2 * np.pi) * volume * 32767).astype(np.int16)

            # Play using separate pyaudio instance
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True
            )
            stream.write(beep.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            self.logger.debug(f"Beep playback failed: {e}")
