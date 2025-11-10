"""
Centralized timeout configuration for Big Three Realtime Agents.

All timeout values in seconds unless otherwise specified.
Provides consistent timeout behavior across the entire application.
"""

# ============================================================================
# Network Timeouts
# ============================================================================

# HTTP request timeouts
HTTP_REQUEST_TIMEOUT = 10  # Standard HTTP requests
HTTP_REQUEST_TIMEOUT_SHORT = 5  # Quick API checks
HTTP_REQUEST_TIMEOUT_LONG = 30  # Large file downloads

# WebSocket timeouts
WEBSOCKET_CONNECT_TIMEOUT = 15  # Initial connection
WEBSOCKET_MESSAGE_TIMEOUT = 30  # Message send/receive
WEBSOCKET_CLOSE_TIMEOUT = 5  # Graceful close

# API-specific timeouts
OPENAI_API_TIMEOUT = 30  # OpenAI Realtime API
ANTHROPIC_API_TIMEOUT = 60  # Claude API (can be slow for long responses)
GEMINI_API_TIMEOUT = 45  # Gemini API
GROQ_API_TIMEOUT = 20  # Groq API (fast inference)

# ============================================================================
# Agent Operation Timeouts
# ============================================================================

# Agent lifecycle timeouts
AGENT_CREATION_TIMEOUT = 60  # Agent initialization
AGENT_EXECUTION_TIMEOUT = 300  # 5 minutes for task execution
AGENT_CLEANUP_TIMEOUT = 10  # Cleanup operations

# Browser automation timeouts
BROWSER_STARTUP_TIMEOUT = 30  # Browser launch
BROWSER_PAGE_LOAD_TIMEOUT = 15  # Page load wait
BROWSER_AUTOMATION_TIMEOUT = 120  # 2 minutes for automation tasks
BROWSER_SCREENSHOT_TIMEOUT = 10  # Screenshot capture

# Claude Code integration timeouts
CLAUDE_CODE_CREATE_TIMEOUT = 90  # Agent creation via API or Max
CLAUDE_CODE_EXECUTE_TIMEOUT = 600  # 10 minutes for code execution
CLAUDE_CODE_CLEANUP_TIMEOUT = 15  # Cleanup after execution

# ============================================================================
# Database and Storage Timeouts
# ============================================================================

# Database operation timeouts
DB_QUERY_TIMEOUT = 5  # Single query
DB_TRANSACTION_TIMEOUT = 10  # Transaction block
DB_CONNECTION_TIMEOUT = 3  # Connection establishment

# Redis timeouts
REDIS_CONNECT_TIMEOUT = 3  # Connection
REDIS_COMMAND_TIMEOUT = 2  # Single command
REDIS_LOCK_TIMEOUT = 30  # Distributed lock

# ============================================================================
# File System Timeouts
# ============================================================================

# File operation timeouts
FILE_READ_TIMEOUT = 5  # Reading files
FILE_WRITE_TIMEOUT = 10  # Writing files
FILE_OPEN_TIMEOUT = 5  # Opening with external app (VS Code, etc.)

# ============================================================================
# Audio Timeouts
# ============================================================================

# Audio I/O timeouts
AUDIO_DEVICE_INIT_TIMEOUT = 5  # Audio device initialization
AUDIO_STREAM_START_TIMEOUT = 3  # Stream start
AUDIO_STREAM_STOP_TIMEOUT = 2  # Stream stop

# ============================================================================
# Observability Timeouts
# ============================================================================

# Event reporting timeouts
OBSERVABILITY_EVENT_TIMEOUT = 2  # Single event send (fast fail)
OBSERVABILITY_BATCH_TIMEOUT = 5  # Batch event send
OBSERVABILITY_HEALTH_CHECK_TIMEOUT = 1  # Health endpoint check

# ============================================================================
# System Timeouts
# ============================================================================

# Subprocess timeouts
SUBPROCESS_DEFAULT_TIMEOUT = 30  # Default for subprocess.run
SUBPROCESS_QUICK_TIMEOUT = 5  # Quick commands (ls, cat, etc.)
SUBPROCESS_LONG_TIMEOUT = 120  # Long-running processes

# Shutdown timeouts
GRACEFUL_SHUTDOWN_TIMEOUT = 10  # Max time to wait for graceful shutdown
THREAD_JOIN_TIMEOUT = 5  # Thread.join() timeout
EXECUTOR_SHUTDOWN_TIMEOUT = 30  # ThreadPoolExecutor shutdown

# ============================================================================
# Auto-prompt Timeouts
# ============================================================================

# Auto-prompt mode timeouts
AUTO_PROMPT_DEFAULT_TIMEOUT = 300  # 5 minutes default
AUTO_PROMPT_RESPONSE_TIMEOUT = 60  # Wait for agent response

# ============================================================================
# Helper Functions
# ============================================================================


def get_timeout(operation: str, default: float = 30.0) -> float:
    """
    Get timeout value for a specific operation.

    Args:
        operation: Operation name (e.g., 'http_request', 'agent_creation').
        default: Default timeout if operation not found.

    Returns:
        Timeout value in seconds.
    """
    timeout_map = {
        # Network
        'http_request': HTTP_REQUEST_TIMEOUT,
        'http_request_short': HTTP_REQUEST_TIMEOUT_SHORT,
        'http_request_long': HTTP_REQUEST_TIMEOUT_LONG,
        'websocket_connect': WEBSOCKET_CONNECT_TIMEOUT,
        'websocket_message': WEBSOCKET_MESSAGE_TIMEOUT,
        'websocket_close': WEBSOCKET_CLOSE_TIMEOUT,

        # APIs
        'openai_api': OPENAI_API_TIMEOUT,
        'anthropic_api': ANTHROPIC_API_TIMEOUT,
        'gemini_api': GEMINI_API_TIMEOUT,
        'groq_api': GROQ_API_TIMEOUT,

        # Agents
        'agent_creation': AGENT_CREATION_TIMEOUT,
        'agent_execution': AGENT_EXECUTION_TIMEOUT,
        'agent_cleanup': AGENT_CLEANUP_TIMEOUT,

        # Browser
        'browser_startup': BROWSER_STARTUP_TIMEOUT,
        'browser_page_load': BROWSER_PAGE_LOAD_TIMEOUT,
        'browser_automation': BROWSER_AUTOMATION_TIMEOUT,
        'browser_screenshot': BROWSER_SCREENSHOT_TIMEOUT,

        # Database
        'db_query': DB_QUERY_TIMEOUT,
        'db_transaction': DB_TRANSACTION_TIMEOUT,
        'db_connection': DB_CONNECTION_TIMEOUT,
        'redis_connect': REDIS_CONNECT_TIMEOUT,
        'redis_command': REDIS_COMMAND_TIMEOUT,

        # File System
        'file_read': FILE_READ_TIMEOUT,
        'file_write': FILE_WRITE_TIMEOUT,
        'file_open': FILE_OPEN_TIMEOUT,

        # Audio
        'audio_device_init': AUDIO_DEVICE_INIT_TIMEOUT,
        'audio_stream_start': AUDIO_STREAM_START_TIMEOUT,
        'audio_stream_stop': AUDIO_STREAM_STOP_TIMEOUT,

        # Observability
        'observability_event': OBSERVABILITY_EVENT_TIMEOUT,
        'observability_batch': OBSERVABILITY_BATCH_TIMEOUT,
        'observability_health': OBSERVABILITY_HEALTH_CHECK_TIMEOUT,

        # System
        'subprocess': SUBPROCESS_DEFAULT_TIMEOUT,
        'subprocess_quick': SUBPROCESS_QUICK_TIMEOUT,
        'subprocess_long': SUBPROCESS_LONG_TIMEOUT,
        'graceful_shutdown': GRACEFUL_SHUTDOWN_TIMEOUT,
        'thread_join': THREAD_JOIN_TIMEOUT,
        'executor_shutdown': EXECUTOR_SHUTDOWN_TIMEOUT,
    }

    return timeout_map.get(operation, default)


def validate_timeout(timeout: float, min_timeout: float = 0.1, max_timeout: float = 600.0) -> float:
    """
    Validate and clamp timeout value.

    Args:
        timeout: Timeout value to validate.
        min_timeout: Minimum allowed timeout (default: 0.1s).
        max_timeout: Maximum allowed timeout (default: 600s / 10 minutes).

    Returns:
        Clamped timeout value.
    """
    if timeout < min_timeout:
        return min_timeout
    if timeout > max_timeout:
        return max_timeout
    return timeout
