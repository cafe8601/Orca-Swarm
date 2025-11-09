"""
Message processing for OpenAI Realtime Agent.

Handles WebSocket message processing, response assembly, token tracking,
and audio/text output routing for OpenAI Realtime API interactions.

Classes:
    MessageProcessor: Processes and routes WebSocket messages from API.

Dependencies:
    - json: Message parsing
    - websocket: WebSocket communication
    - function_handler: Tool/function execution
    - audio_manager: Audio playback management

Example:
    >>> processor = MessageProcessor(
    ...     logger=logger,
    ...     audio_manager=audio_mgr,
    ...     token_usage={},
    ...     audio_state={},
    ...     output_mode="text",
    ...     function_handler=func_handler,
    ...     cost_calculator=cost_calc,
    ...     ui_logger=ui_log
    ... )
    >>> processor.process_message(ws, message_json)
"""

import json
import logging
from typing import Dict, Any, List, Callable, Optional


class MessageProcessor:
    """
    Processes WebSocket messages from OpenAI Realtime API.

    Handles message parsing, event routing, response assembly, token tracking,
    and output rendering for both text and audio modes.

    Attributes:
        logger: Logger for debugging and error tracking.
        audio_manager: Manages audio encoding/decoding and playback.
        token_usage: Dictionary tracking cumulative token usage.
        audio_state: Dictionary tracking audio state (e.g., paused).
        output_mode: Output mode ("text" or "audio").
        function_handler: Handles function/tool execution requests.
        cost_calculator: Calculates API costs from token usage.
        ui_logger: Logs UI-formatted messages and panels.
        current_response_text: Accumulates text response chunks.
        current_function_calls: Tracks in-progress function calls.

    Supported Events:
        - response.text.delta: Text response chunks
        - response.audio.delta: Audio response chunks
        - response.function_call_arguments.delta: Function call arguments
        - response.done: Response completion with token usage
        - input_audio_buffer.speech_started: User speech detection
        - input_audio_buffer.speech_stopped: User speech end
        - session.created/updated: Session lifecycle events
        - error: API error messages
    """

    def __init__(
        self,
        logger: logging.Logger,
        audio_manager: Any,  # AudioManager type
        token_usage: Dict[str, Any],
        audio_state: Dict[str, Any],
        output_mode: str,
        function_handler: Any,  # FunctionHandler type
        cost_calculator: Callable[[Dict[str, Any]], float],
        ui_logger: Callable[..., None],
    ):
        """
        Initialize message processor.

        Args:
            logger: Logger instance for debugging.
            audio_manager: AudioManager instance for audio I/O.
            token_usage: Shared dict for tracking cumulative token usage.
            audio_state: Shared dict for tracking audio state.
            output_mode: Output mode - "text" or "audio".
            function_handler: FunctionHandler for tool execution.
            cost_calculator: Function to calculate API costs from usage.
            ui_logger: Function to log formatted UI messages.
        """
        self.logger = logger
        self.audio_manager = audio_manager
        self.token_usage = token_usage
        self.audio_state = audio_state
        self.output_mode = output_mode
        self.function_handler = function_handler
        self.cost_calculator = cost_calculator
        self.ui_logger = ui_logger

        # Response assembly state
        self.current_response_text: List[str] = []
        self.current_function_calls: Dict[str, Any] = {}

    def process_message(self, ws: Any, message: str) -> None:
        """
        Process incoming WebSocket message and route to appropriate handler.

        Args:
            ws: WebSocket connection instance.
            message: Raw JSON message string from WebSocket.

        Note:
            Errors during processing are logged but don't raise exceptions
            to maintain WebSocket connection stability.
        """
        try:
            event = json.loads(message)
            event_type = event.get("type", "")

            # Text delta - incremental text response
            if event_type == "response.text.delta":
                delta_text = event.get("delta", "")
                self.current_response_text.append(delta_text)
                if self.output_mode == "text":
                    print(delta_text, end="", flush=True)

            # Audio delta - incremental audio response
            elif event_type == "response.audio.delta":
                audio_b64 = event.get("delta", "")
                if audio_b64 and self.output_mode == "audio":
                    audio_bytes = self.audio_manager.decode_audio(audio_b64)
                    if self.audio_manager.audio_stream:
                        self.audio_manager.audio_stream.write(audio_bytes)

            # Function call delta - incremental function arguments
            elif event_type == "response.function_call_arguments.delta":
                self.function_handler.handle_function_call_delta(event)

            # Response done - finalize response and update tokens
            elif event_type == "response.done":
                self.function_handler.handle_response_done(event, ws)
                self._update_token_usage(event)
                self.current_response_text = []

            # Input audio buffer speech started
            elif event_type == "input_audio_buffer.speech_started":
                self.logger.debug("Speech started - auto-pausing output")
                self.audio_state["auto_paused"] = True

            # Input audio buffer speech stopped
            elif event_type == "input_audio_buffer.speech_stopped":
                self.logger.debug("Speech stopped - resuming output")
                self.audio_state["auto_paused"] = False

            # Response output audio transcript (optional logging)
            elif event_type == "response.audio_transcript.delta":
                pass  # Transcript updates available but not currently used

            # Session created
            elif event_type == "session.created":
                self.logger.info("Session created")

            # Session updated
            elif event_type == "session.updated":
                self.logger.debug("Session updated")

            # API errors
            elif event_type == "error":
                error_data = event.get("error", {})
                error_type = error_data.get("type", "unknown")
                error_msg = error_data.get("message", "No error message")
                self.logger.error(f"OpenAI API error [{error_type}]: {error_msg}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)

    def _update_token_usage(self, event: Dict[str, Any]) -> None:
        """
        Update cumulative token usage from response.done event.

        Tracks text and audio tokens separately for both input and output,
        and calculates incremental API cost.

        Args:
            event: Response done event containing usage statistics.

        Note:
            Token usage is accumulated in the shared token_usage dictionary
            which is accessible across the application for cost tracking.
        """
        usage = event.get("response", {}).get("usage", {})
        if not usage:
            return

        input_details = usage.get("input_token_details", {})
        output_details = usage.get("output_token_details", {})

        # Update cumulative token counts
        self.token_usage["text_input_tokens"] = (
            self.token_usage.get("text_input_tokens", 0)
            + input_details.get("text_tokens", 0)
        )
        self.token_usage["audio_input_tokens"] = (
            self.token_usage.get("audio_input_tokens", 0)
            + input_details.get("audio_tokens", 0)
        )
        self.token_usage["text_output_tokens"] = (
            self.token_usage.get("text_output_tokens", 0)
            + output_details.get("text_tokens", 0)
        )
        self.token_usage["audio_output_tokens"] = (
            self.token_usage.get("audio_output_tokens", 0)
            + output_details.get("audio_tokens", 0)
        )

        # Calculate and accumulate cost
        cost = self.cost_calculator(usage)
        self.token_usage["total_cost"] = (
            self.token_usage.get("total_cost", 0.0) + cost
        )
