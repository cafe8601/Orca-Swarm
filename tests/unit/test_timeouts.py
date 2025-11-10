"""
Unit tests for timeout configuration.

Tests timeout constants, get_timeout function, and validate_timeout function.
"""

import pytest
from apps.realtime_poc.big_three_realtime_agents.timeouts import (
    # Network timeouts
    HTTP_REQUEST_TIMEOUT,
    WEBSOCKET_CONNECT_TIMEOUT,
    OPENAI_API_TIMEOUT,
    ANTHROPIC_API_TIMEOUT,
    GEMINI_API_TIMEOUT,
    # Agent timeouts
    AGENT_CREATION_TIMEOUT,
    AGENT_EXECUTION_TIMEOUT,
    BROWSER_AUTOMATION_TIMEOUT,
    # Helper functions
    get_timeout,
    validate_timeout,
)


class TestTimeoutConstants:
    """Tests for timeout constant values."""

    def test_network_timeouts_positive(self):
        """Test all network timeouts are positive."""
        assert HTTP_REQUEST_TIMEOUT > 0
        assert WEBSOCKET_CONNECT_TIMEOUT > 0

    def test_api_timeouts_reasonable(self):
        """Test API timeouts are in reasonable range."""
        assert 10 <= OPENAI_API_TIMEOUT <= 120
        assert 10 <= ANTHROPIC_API_TIMEOUT <= 120
        assert 10 <= GEMINI_API_TIMEOUT <= 120

    def test_agent_timeouts_longer_than_network(self):
        """Test agent timeouts are longer than network timeouts."""
        assert AGENT_CREATION_TIMEOUT > HTTP_REQUEST_TIMEOUT
        assert AGENT_EXECUTION_TIMEOUT > AGENT_CREATION_TIMEOUT
        assert BROWSER_AUTOMATION_TIMEOUT > WEBSOCKET_CONNECT_TIMEOUT


class TestGetTimeout:
    """Tests for get_timeout function."""

    def test_get_known_timeout(self):
        """Test retrieving known timeout values."""
        assert get_timeout("http_request") == HTTP_REQUEST_TIMEOUT
        assert get_timeout("websocket_connect") == WEBSOCKET_CONNECT_TIMEOUT
        assert get_timeout("agent_creation") == AGENT_CREATION_TIMEOUT
        assert get_timeout("gemini_api") == GEMINI_API_TIMEOUT

    def test_get_unknown_timeout_uses_default(self):
        """Test unknown operation returns default."""
        assert get_timeout("unknown_operation") == 30.0
        assert get_timeout("unknown_operation", default=60.0) == 60.0

    def test_get_timeout_case_sensitive(self):
        """Test operation names are case-sensitive."""
        # Exact match should work
        assert get_timeout("http_request") == HTTP_REQUEST_TIMEOUT

        # Case mismatch should use default
        assert get_timeout("HTTP_REQUEST") == 30.0

    def test_all_timeout_operations_accessible(self):
        """Test all documented operations are accessible."""
        operations = [
            "http_request",
            "http_request_short",
            "http_request_long",
            "websocket_connect",
            "websocket_message",
            "openai_api",
            "anthropic_api",
            "gemini_api",
            "agent_creation",
            "agent_execution",
            "browser_automation",
            "db_query",
            "redis_connect",
            "file_read",
            "observability_event",
            "subprocess",
            "graceful_shutdown",
        ]

        for op in operations:
            timeout = get_timeout(op)
            assert timeout > 0, f"Timeout for '{op}' should be positive"


class TestValidateTimeout:
    """Tests for validate_timeout function."""

    def test_validate_normal_timeout(self):
        """Test validation of normal timeout values."""
        assert validate_timeout(10.0) == 10.0
        assert validate_timeout(30.0) == 30.0
        assert validate_timeout(60.0) == 60.0

    def test_validate_clamps_minimum(self):
        """Test timeout is clamped to minimum."""
        assert validate_timeout(0.0) == 0.1
        assert validate_timeout(-10.0) == 0.1
        assert validate_timeout(0.05) == 0.1

    def test_validate_clamps_maximum(self):
        """Test timeout is clamped to maximum."""
        assert validate_timeout(1000.0) == 600.0
        assert validate_timeout(9999.0) == 600.0

    def test_validate_custom_bounds(self):
        """Test validation with custom min/max bounds."""
        assert validate_timeout(5.0, min_timeout=1.0, max_timeout=100.0) == 5.0
        assert validate_timeout(0.5, min_timeout=1.0, max_timeout=100.0) == 1.0
        assert validate_timeout(200.0, min_timeout=1.0, max_timeout=100.0) == 100.0

    def test_validate_boundary_values(self):
        """Test exact boundary values."""
        assert validate_timeout(0.1, min_timeout=0.1) == 0.1
        assert validate_timeout(600.0, max_timeout=600.0) == 600.0


class TestTimeoutUsage:
    """Integration-style tests for timeout usage patterns."""

    def test_timeout_in_context_manager(self):
        """Test using timeout with context manager."""
        import urllib.request

        timeout = get_timeout("http_request")

        # Should be usable with urllib
        assert isinstance(timeout, (int, float))
        assert timeout > 0

    def test_timeout_with_asyncio(self):
        """Test timeout is compatible with asyncio.wait_for."""
        import asyncio

        timeout = get_timeout("agent_creation")

        async def dummy_task():
            await asyncio.sleep(0.1)
            return "done"

        # Should work with asyncio.wait_for
        result = asyncio.run(asyncio.wait_for(dummy_task(), timeout=timeout))
        assert result == "done"

    def test_validate_before_use(self):
        """Test validation before using timeout."""
        user_timeout = 1000.0  # User-provided timeout

        # Validate to ensure it's in safe range
        safe_timeout = validate_timeout(user_timeout)

        assert safe_timeout == 600.0  # Clamped to max
        assert safe_timeout < user_timeout
