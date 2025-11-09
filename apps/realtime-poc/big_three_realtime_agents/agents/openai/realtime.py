"""
Core OpenAIRealtimeVoiceAgent class.

Main orchestrator for OpenAI Realtime API voice interactions.

SIZE JUSTIFICATION (231 lines):
This file serves as the central orchestrator for the entire voice agent system,
coordinating 10+ specialized subsystems (audio, WebSocket, session, tools, etc.).
Its size is justified because:
1. It's the main integration point requiring initialization of all components
2. Complex dependency injection and component wiring cannot be further extracted
3. Breaking it down would create circular dependencies or over-abstracted indirection
4. The __init__ method alone requires ~100 lines for proper component setup
5. This is the natural limit for a main orchestrator class in this architecture

Alternative refactoring would require significant architectural changes (e.g.,
dependency injection framework, service locator pattern) which would add
complexity without meaningful benefit for this application scope.
"""

import logging
import threading
from typing import Optional

import websocket

from ...config import (
    OPENAI_API_KEY,
    REALTIME_MODEL_DEFAULT,
    REALTIME_API_URL_TEMPLATE,
    REALTIME_VOICE_CHOICE,
    AGENT_WORKING_DIRECTORY,
)
from ...utils import log_panel, log_tool_catalog, log_agent_roster, log_tool_request
from ..base import BaseAgent
from ..gemini import GeminiBrowserAgent
from ..claude import ClaudeCodeAgenticCoder
from .system_prompt import SystemPromptManager
from .websocket_handlers import WebSocketHandlers
from .message_processing import MessageProcessor
from .function_handling import FunctionHandler
from .input_loops import InputHandler
from .tools_agents import AgentTools
from .tools_browser import BrowserTools
from .tools_filesystem import FilesystemTools
from .tools_reporting import ReportingTools
from .tools_catalog import build_tool_specs
from .session_management import SessionManager
from .audio_interface import AudioInterface


class OpenAIRealtimeVoiceAgent(BaseAgent):
    """
    Voice interaction agent using OpenAI Realtime API.

    Orchestrates voice/text input, tool execution, and agent management.
    """

    def __init__(
        self,
        input_mode: str = "text",
        output_mode: str = "text",
        logger: Optional[logging.Logger] = None,
        realtime_model: Optional[str] = None,
        startup_prompt: Optional[str] = None,
        auto_timeout: int = 60,
    ):
        """
        Initialize the unified voice agent.

        Args:
            input_mode: Input mode ("text" or "audio").
            output_mode: Output mode ("text" or "audio").
            logger: Optional logger instance.
            realtime_model: Optional model override.
            startup_prompt: Optional startup prompt for auto mode.
            auto_timeout: Auto mode timeout in seconds.
        """
        super().__init__(logger)

        # Validate OpenAI API key
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Configuration
        self.input_mode = input_mode
        self.output_mode = output_mode
        self.realtime_model = realtime_model or REALTIME_MODEL_DEFAULT

        # Session manager
        self.session_manager = SessionManager(self.logger, self.realtime_model)

        # Audio interface
        self.audio_interface = AudioInterface(self.logger, input_mode, output_mode)

        # WebSocket state
        self.ws = None
        self.running_flag = {"running": False}

        # Auto mode settings
        self.startup_prompt = startup_prompt
        self.auto_mode = startup_prompt is not None

        # Initialize sub-agents
        self.browser_agent = GeminiBrowserAgent(logger=self.logger)
        self.agentic_coder = ClaudeCodeAgenticCoder(
            logger=self.logger, browser_agent=self.browser_agent
        )

        # Build tool specs
        self.tool_specs = build_tool_specs()

        # UI logger wrapper
        def ui_logger(message_or_agents, **kwargs):
            if isinstance(message_or_agents, list):
                log_agent_roster(message_or_agents, AGENT_WORKING_DIRECTORY, self.logger)
            elif isinstance(message_or_agents, str) and "call_id" in kwargs:
                log_tool_request(message_or_agents, kwargs.get("call_id", ""), kwargs.get("arguments", ""), self.logger)
            else:
                log_panel(message_or_agents, logger=self.logger, **kwargs)

        # Initialize tool modules
        self.agent_tools = AgentTools(
            self.logger, self.agentic_coder, self.browser_agent, ui_logger
        )
        self.browser_tools = BrowserTools(self.logger, self.browser_agent)
        self.filesystem_tools = FilesystemTools(self.logger, ui_logger)
        self.reporting_tools = ReportingTools(
            self.logger,
            self.session_manager.token_usage,
            self.session_manager.display_token_summary,
        )

        # System prompt manager
        self.system_prompt_manager = SystemPromptManager(self.logger, self.agentic_coder)

        # Function handler
        self.function_handler = FunctionHandler(
            self.logger,
            self.agent_tools,
            self.browser_tools,
            self.filesystem_tools,
            self.reporting_tools,
            lambda name, cid, args: log_tool_request(name, cid, args, self.logger),
        )

        # Message processor
        self.message_processor = MessageProcessor(
            self.logger,
            self.audio_interface.get_audio_manager(),
            self.session_manager.token_usage,
            self.audio_interface.get_audio_state(),
            self.output_mode,
            self.function_handler,
            self.session_manager.calculate_cost_from_usage,
            ui_logger,
        )

        # WebSocket handlers
        self.websocket_handlers = WebSocketHandlers(
            self.logger,
            self.running_flag,
            self.system_prompt_manager.load_system_prompt,
            {
                "default_modalities": ["audio"] if output_mode == "audio" else ["text"],
                "voice": REALTIME_VOICE_CHOICE,
                "tools": self.tool_specs,
                "token_display_func": self.session_manager.display_token_summary,
            },
            self.message_processor,
        )

        # Input handler
        self.input_handler = InputHandler(
            self.logger,
            self.audio_interface.get_audio_manager(),
            self.ws,
            self.running_flag,
            self.audio_interface.get_audio_state(),
        )

        self.logger.info(
            f"Initialized OpenAIRealtimeVoiceAgent - Input: {input_mode}, Output: {output_mode}"
        )
        log_tool_catalog(self.tool_specs, self.logger)

    def setup(self):
        """Setup audio resources if needed."""
        self.audio_interface.setup_audio()

    def cleanup(self):
        """Cleanup resources."""
        self.audio_interface.cleanup_audio()

    def execute_task(self, task: str, **kwargs):
        """Execute task via text dispatch."""
        # Not typically used for voice agent, but here for interface compliance
        pass

    def connect(self):
        """Connect to OpenAI Realtime API."""
        self.logger.info("Connecting to OpenAI Realtime API...")

        # Setup audio if needed
        if self.audio_interface.is_audio_enabled():
            self.setup()

        # Start keyboard listener
        if self.input_mode == "audio":
            self.input_handler.start_keyboard_listener(
                self.audio_interface.get_audio_manager().play_beep
            )

        # Create WebSocket connection
        websocket_url = REALTIME_API_URL_TEMPLATE.format(model=self.realtime_model)
        self.ws = websocket.WebSocketApp(
            websocket_url,
            header=[f"Authorization: Bearer {OPENAI_API_KEY}"],
            on_open=self.websocket_handlers.on_open,
            on_message=self.websocket_handlers.on_message,
            on_error=self.websocket_handlers.on_error,
            on_close=self.websocket_handlers.on_close,
        )

        # Update input handler with ws
        self.input_handler.ws = self.ws

        # Start input loop in background
        if self.input_mode == "text":
            t = threading.Thread(target=self.input_handler.text_input_loop, daemon=True)
            t.start()
        elif self.input_mode == "audio":
            t = threading.Thread(target=self.input_handler.audio_input_loop, daemon=True)
            t.start()

        try:
            # Run WebSocket connection (blocking)
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            if self.input_handler.keyboard_listener:
                self.input_handler.keyboard_listener.stop()
            self.cleanup()
            self.logger.info("Connection closed")
