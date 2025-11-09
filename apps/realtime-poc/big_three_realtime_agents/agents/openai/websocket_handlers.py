"""
WebSocket event handlers for OpenAI Realtime Agent.

Manages WebSocket lifecycle events (open, message, error, close) and
configures OpenAI Realtime API session with tools and voice settings.

Classes:
    WebSocketHandlers: Handles WebSocket connection lifecycle events.

Dependencies:
    - websocket: WebSocket connection management
    - json: Message serialization
    - message_processor: Processes incoming API messages

Example:
    >>> handlers = WebSocketHandlers(
    ...     logger=logger,
    ...     running_flag={"running": False},
    ...     system_prompt_loader=load_prompt,
    ...     output_config={"voice": "shimmer", "tools": []},
    ...     message_processor=processor
    ... )
    >>> ws = WebSocketApp(url, on_open=handlers.on_open, ...)
"""

import json
import logging
from typing import Dict, Any, Callable, Optional


class WebSocketHandlers:
    """
    WebSocket connection event handlers for OpenAI Realtime API.

    Manages the WebSocket lifecycle, configures session parameters including
    voice settings, modalities, turn detection (VAD), and available tools.

    Attributes:
        logger: Logger for connection events and debugging.
        running_flag: Shared dict tracking connection state.
        system_prompt_loader: Function returning system instructions.
        output_config: Configuration dict for voice, tools, and modalities.
        message_processor: Processor for incoming WebSocket messages.

    Session Configuration:
        - instructions: System prompt defining agent behavior
        - modalities: Output types (text, audio, or both)
        - voice: Voice selection for audio output
        - turn_detection: Voice Activity Detection (VAD) settings
        - tools: Available functions/tools for agent use
    """

    def __init__(
        self,
        logger: logging.Logger,
        running_flag: Dict[str, bool],
        system_prompt_loader: Callable[[], str],
        output_config: Dict[str, Any],
        message_processor: Any,  # MessageProcessor type
    ):
        """
        Initialize WebSocket handlers.

        Args:
            logger: Logger instance for connection events.
            running_flag: Shared dictionary with 'running' boolean flag.
            system_prompt_loader: Callable returning system instructions.
            output_config: Configuration containing voice, tools, modalities.
            message_processor: MessageProcessor instance for message handling.
        """
        self.logger = logger
        self.running_flag = running_flag
        self.system_prompt_loader = system_prompt_loader
        self.output_config = output_config
        self.message_processor = message_processor

    def on_open(self, ws: Any) -> None:
        """
        Handle WebSocket connection opened event.

        Configures OpenAI Realtime API session with:
        - System instructions for agent behavior
        - Output modalities (text/audio)
        - Voice selection for audio output
        - Voice Activity Detection (VAD) parameters
        - Available tools for function calling

        Args:
            ws: WebSocket connection instance.

        Note:
            Sends two session.update messages:
            1. Configure instructions, modalities, voice, and VAD
            2. Configure available tools
        """
        self.logger.info("WebSocket connection established")
        self.running_flag["running"] = True

        instructions = self.system_prompt_loader()
        output_modalities = self.output_config.get(
            "default_modalities", ["text", "audio"]
        )

        session_config = {
            "type": "session.update",
            "session": {
                "instructions": instructions,
                "modalities": output_modalities,
                "voice": self.output_config.get("voice", "shimmer"),
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500,
                },
            },
        }

        self.logger.info("Sending session config...")
        ws.send(json.dumps(session_config))

        # Update tools
        tool_config = {
            "type": "session.update",
            "session": {"tools": self.output_config.get("tools", [])},
        }
        ws.send(json.dumps(tool_config))
        self.logger.info("Tools configured")

    def on_message(self, ws: Any, message: str) -> None:
        """
        Handle incoming WebSocket message.

        Delegates message processing to MessageProcessor which handles
        response assembly, token tracking, and function call routing.

        Args:
            ws: WebSocket connection instance.
            message: Raw JSON message string from API.
        """
        self.message_processor.process_message(ws, message)

    def on_error(self, ws: Any, error: Exception) -> None:
        """
        Handle WebSocket error event.

        Logs error details for debugging. Connection may automatically
        reconnect depending on error type and WebSocket configuration.

        Args:
            ws: WebSocket connection instance.
            error: Exception that occurred.
        """
        self.logger.error(f"WebSocket error: {error}", exc_info=True)

    def on_close(
        self,
        ws: Any,
        close_status_code: Optional[int],
        close_msg: Optional[str]
    ) -> None:
        """
        Handle WebSocket connection closed event.

        Updates running flag, logs closure reason, and displays token usage
        summary if display function is configured.

        Args:
            ws: WebSocket connection instance.
            close_status_code: WebSocket close status code (1000 = normal).
            close_msg: Optional close message from server.

        Note:
            Token display errors are silently caught to ensure cleanup
            completes even if display function fails.
        """
        self.running_flag["running"] = False
        self.logger.info(
            f"WebSocket connection closed. Code: {close_status_code}, "
            f"Message: {close_msg or 'None'}"
        )

        # Display token summary
        token_display_func = self.output_config.get("token_display_func")
        if token_display_func:
            try:
                token_display_func()
            except Exception as e:
                self.logger.debug(f"Token display failed: {e}")
