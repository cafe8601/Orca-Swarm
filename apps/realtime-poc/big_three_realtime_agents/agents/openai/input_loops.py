"""
Input loop handlers for OpenAI Realtime Agent.

Manages text and audio input loops, keyboard controls for voice activity,
and message dispatching to OpenAI Realtime API.

Classes:
    InputHandler: Handles user input collection and transmission.

Dependencies:
    - pynput: Keyboard event listening for hotkey controls
    - pyaudio: Audio capture from microphone
    - websocket: Message transmission to API

Features:
    - Text input with quit commands
    - Audio input with real-time streaming
    - Keyboard hotkey (Shift+Space) for audio pause/resume
    - Automatic pause detection during user speech

Example:
    >>> handler = InputHandler(
    ...     logger=logger,
    ...     audio_manager=audio_mgr,
    ...     ws=websocket,
    ...     running_flag={"running": True},
    ...     audio_state={"enabled": True, "paused": False}
    ... )
    >>> threading.Thread(target=handler.text_input_loop, daemon=True).start()
"""

import json
import time
import logging
import threading
from typing import Dict, Any, Callable, Optional

from pynput import keyboard

from ...config import CHUNK_SIZE
from ...utils import AudioManager


class InputHandler:
    """
    Handles user input loops and keyboard controls for OpenAI Realtime Agent.

    Manages two input modes:
    1. Text mode: Terminal-based text input with quit commands
    2. Audio mode: Continuous microphone streaming with pause/resume

    Attributes:
        logger: Logger for debugging and event tracking.
        audio_manager: AudioManager for audio capture and encoding.
        ws: WebSocket connection for sending input to API.
        running_flag: Shared dict with 'running' boolean flag.
        audio_state: Shared dict tracking audio state (paused, auto_paused).
        keyboard_listener: pynput keyboard listener for hotkeys.
        shift_pressed: Tracks shift key state for hotkey detection.

    Keyboard Controls (Audio Mode):
        Shift+Space: Toggle audio input pause/resume
    """

    def __init__(
        self,
        logger: logging.Logger,
        audio_manager: AudioManager,
        ws: Any,  # WebSocket type
        running_flag: Dict[str, bool],
        audio_state: Dict[str, Any],
    ):
        """
        Initialize input handler.

        Args:
            logger: Logger instance for debugging.
            audio_manager: AudioManager instance for audio I/O.
            ws: WebSocket connection instance.
            running_flag: Shared dict with 'running' boolean flag.
            audio_state: Shared dict for audio state tracking.
        """
        self.logger = logger
        self.audio_manager = audio_manager
        self.ws = ws
        self.running_flag = running_flag
        self.audio_state = audio_state
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.shift_pressed: bool = False

    def text_input_loop(self) -> None:
        """
        Handle text input from terminal (blocking loop).

        Continuously reads text input from stdin, processes quit commands,
        and dispatches messages to API. Runs until user quits or error occurs.

        Quit Commands:
            'quit', 'exit', 'q': Close connection and exit loop

        Raises:
            EOFError: When stdin is closed (e.g., pipe input ends).
            Exception: On unexpected errors in input handling.

        Note:
            This method blocks until connection closes. Run in daemon thread
            to allow main thread to handle other events.
        """
        self.logger.info("Text input mode active. Type your messages (or 'quit' to exit):")

        while self.running_flag.get("running"):
            try:
                user_input = input("\nYou: ")

                if user_input.lower() in ["quit", "exit", "q"]:
                    self.logger.info("User requested exit")
                    self.ws.close()
                    break

                if not user_input.strip():
                    continue

                self._dispatch_text_message(user_input)

            except EOFError:
                self.logger.info("EOF received, closing connection")
                break
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt, closing connection")
                break
            except Exception as e:
                self.logger.error(f"Error in text input loop: {e}", exc_info=True)
                break

    def audio_input_loop(self) -> None:
        """
        Handle audio input from microphone (blocking loop).

        Continuously captures audio chunks from microphone, encodes to base64,
        and streams to API. Respects pause state from keyboard hotkey or
        automatic pause during agent speech.

        Audio Capture:
            - Chunk size: Defined by CHUNK_SIZE config
            - Format: PCM 16-bit mono at configured RATE
            - Overflow handling: Drops overflow frames without exception

        Pause Behavior:
            - Manual pause: User pressed Shift+Space hotkey
            - Auto pause: Agent is currently speaking (prevents echo)

        Raises:
            Exception: On audio capture or transmission errors.

        Note:
            This method blocks until connection closes. Run in daemon thread
            to allow main thread to handle other events.
        """
        self.logger.info(
            "Audio input mode active. Speak into your microphone "
            "(press SHIFT+SPACE to pause/resume):"
        )

        while self.running_flag.get("running"):
            try:
                # Skip audio capture when paused
                if self.audio_state.get("paused") or self.audio_state.get("auto_paused"):
                    time.sleep(0.1)
                    continue

                audio_data = self.audio_manager.audio_stream.read(
                    CHUNK_SIZE, exception_on_overflow=False
                )
                audio_base64 = self.audio_manager.encode_audio(audio_data)
                event = {"type": "input_audio_buffer.append", "audio": audio_base64}
                self.ws.send(json.dumps(event))

            except Exception as e:
                self.logger.error(f"Error in audio input loop: {e}", exc_info=True)
                break

    def start_keyboard_listener(self, beep_func: Callable[[int], None]) -> None:
        """
        Start keyboard listener for Shift+Space hotkey.

        Enables audio pause/resume toggle via Shift+Space hotkey combination.
        Plays beep tone as audio feedback when toggling state.

        Args:
            beep_func: Function to play beep tone, accepts frequency parameter.

        Beep Frequencies:
            520 Hz: Audio input resumed (higher pitch)
            380 Hz: Audio input paused (lower pitch)

        Note:
            Does nothing if audio is not enabled in audio_state.
            Keyboard listener runs in daemon thread and logs errors without
            crashing the main application.

        Example:
            >>> handler.start_keyboard_listener(
            ...     lambda freq: audio_mgr.play_beep(frequency=freq)
            ... )
        """
        if not self.audio_state.get("enabled"):
            return

        def on_key_press(key: keyboard.Key) -> None:
            """Handle key press events."""
            try:
                if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    self.shift_pressed = True
                elif key == keyboard.Key.space and self.shift_pressed:
                    self.audio_state["paused"] = not self.audio_state["paused"]
                    status = "PAUSED" if self.audio_state["paused"] else "LIVE"
                    beep_freq = 520 if not self.audio_state["paused"] else 380
                    threading.Thread(
                        target=beep_func,
                        args=(beep_freq,),
                        daemon=True
                    ).start()
                    self.logger.info(f"Audio input {status}")
            except Exception as e:
                self.logger.error(f"Error handling shift+space: {e}")

        def on_key_release(key: keyboard.Key) -> None:
            """Handle key release events."""
            try:
                if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    self.shift_pressed = False
            except Exception as e:
                self.logger.error(f"Error handling key release: {e}")

        try:
            self.keyboard_listener = keyboard.Listener(
                on_press=on_key_press,
                on_release=on_key_release
            )
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            self.logger.info("Keyboard listener started (shift+space to pause/resume)")
        except Exception as e:
            self.logger.warning(f"Could not start keyboard listener: {e}")

    def _dispatch_text_message(self, text: str) -> None:
        """
        Send text message to API and request response.

        Creates a conversation item with user message and immediately
        requests a response from the agent.

        Args:
            text: User message text to send.

        Note:
            Sends two WebSocket messages:
            1. conversation.item.create: Adds user message to conversation
            2. response.create: Triggers agent response generation
        """
        if not self.ws:
            self.logger.warning("No WebSocket connection, message not sent")
            return

        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        }

        self.logger.info(f"Sending text message: {text}")
        self.ws.send(json.dumps(event))

        response_event = {"type": "response.create", "response": {}}
        self.ws.send(json.dumps(response_event))
