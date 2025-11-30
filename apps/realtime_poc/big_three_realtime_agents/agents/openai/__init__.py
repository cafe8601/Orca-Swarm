"""
OpenAI Realtime API agent modules.

This package contains the OpenAIRealtimeVoiceAgent implementation for voice
interactions using OpenAI's Realtime API with WebSocket communication.

Modules:
    realtime: Core OpenAIRealtimeVoiceAgent class
    session_management: Session state and token tracking (SessionManager)
    audio_interface: Audio input/output coordination (AudioInterface)
    websocket_handlers: WebSocket connection event handlers
    message_processing: Message and event processing logic
    function_handling: Function call execution and routing
    input_loops: Text and audio input handling
    system_prompt: System prompt management
    tools_catalog: Tool specification builder
    tools_agents: Agent management tools
    tools_browser: Browser automation tools
    tools_filesystem: File operation tools
    tools_reporting: Cost and usage reporting tools
    tools_pool: Agent Pool integration tools (NEW from refactoring.md)
    tools_workflow: Workflow orchestration tools (NEW from refactoring.md)
"""

from .realtime import OpenAIRealtimeVoiceAgent
from .tools_pool import PoolTools
from .tools_workflow import WorkflowTools

__all__ = [
    "OpenAIRealtimeVoiceAgent",
    "PoolTools",
    "WorkflowTools",
]
