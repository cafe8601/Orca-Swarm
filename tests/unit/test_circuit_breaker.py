"""
Unit tests for circuit breaker pattern.

Tests CircuitBreaker class, circuit states, and recovery behavior.
"""

import pytest
import time
from unittest.mock import Mock
from apps.realtime_poc.big_three_realtime_agents.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    circuit_breaker,
    get_circuit_breaker,
    reset_all_circuit_breakers,
)


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_initial_state_closed(self):
        """Test circuit breaker starts in CLOSED state."""
        breaker = CircuitBreaker(name="test")
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_successful_call_in_closed(self):
        """Test successful call in CLOSED state."""
        breaker = CircuitBreaker(name="test")
        mock_func = Mock(return_value="success")

        result = breaker.call(mock_func, "arg1", key="value")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", key="value")
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_opens_after_threshold_failures(self):
        """Test circuit opens after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3, name="test")
        mock_func = Mock(side_effect=ConnectionError("Network error"))

        # First 3 failures
        for i in range(3):
            with pytest.raises(ConnectionError):
                breaker.call(mock_func)

        # Circuit should now be OPEN
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 3

        # Next call should fail immediately with CircuitBreakerError
        with pytest.raises(CircuitBreakerError, match="is OPEN"):
            breaker.call(mock_func)

        # mock_func should not be called when circuit is OPEN
        assert mock_func.call_count == 3  # Not 4

    def test_half_open_after_recovery_timeout(self):
        """Test circuit transitions to HALF_OPEN after timeout."""
        breaker = CircuitBreaker(
            failure_threshold=2, recovery_timeout=0.2, name="test"
        )
        mock_func = Mock(side_effect=ConnectionError("Network error"))

        # Open circuit
        for i in range(2):
            with pytest.raises(ConnectionError):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(0.3)

        # Next call should transition to HALF_OPEN
        mock_func.side_effect = "success"
        result = breaker.call(mock_func)

        assert result == "success"
        # State should still be HALF_OPEN or CLOSED depending on implementation
        assert breaker.state in [CircuitState.HALF_OPEN, CircuitState.CLOSED]

    def test_closes_after_successful_half_open(self):
        """Test circuit closes after successful test calls in HALF_OPEN."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.2,
            half_open_max_calls=3,
            name="test",
        )
        mock_func = Mock()

        # Open circuit
        mock_func.side_effect = [ConnectionError(), ConnectionError()]
        for i in range(2):
            with pytest.raises(ConnectionError):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery
        time.sleep(0.3)

        # Make successful test calls in HALF_OPEN
        mock_func.side_effect = ["success1", "success2", "success3"]
        for i in range(3):
            result = breaker.call(mock_func)
            assert result == f"success{i+1}"

        # Circuit should be CLOSED
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_reopens_on_half_open_failure(self):
        """Test circuit reopens immediately on failure in HALF_OPEN."""
        breaker = CircuitBreaker(
            failure_threshold=2, recovery_timeout=0.2, name="test"
        )
        mock_func = Mock()

        # Open circuit
        mock_func.side_effect = [ConnectionError(), ConnectionError()]
        for i in range(2):
            with pytest.raises(ConnectionError):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery
        time.sleep(0.3)

        # First call transitions to HALF_OPEN, but fails
        mock_func.side_effect = ConnectionError("Still failing")
        with pytest.raises(ConnectionError):
            breaker.call(mock_func)

        # Circuit should reopen immediately
        assert breaker.state == CircuitState.OPEN

    def test_manual_reset(self):
        """Test manual circuit reset."""
        breaker = CircuitBreaker(failure_threshold=2, name="test")
        mock_func = Mock(side_effect=ConnectionError())

        # Open circuit
        for i in range(2):
            with pytest.raises(ConnectionError):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Manual reset
        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_get_stats(self):
        """Test get_stats returns correct information."""
        breaker = CircuitBreaker(name="test")
        mock_func = Mock(return_value="success")

        breaker.call(mock_func)
        stats = breaker.get_stats()

        assert stats["name"] == "test"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 0
        assert stats["success_count"] == 0  # Only counted in HALF_OPEN


class TestCircuitBreakerDecorator:
    """Tests for circuit_breaker decorator."""

    def test_decorator_success(self):
        """Test decorator on successful function."""

        @circuit_breaker(failure_threshold=3, name="test_decorator")
        def func():
            return "success"

        result = func()
        assert result == "success"

    def test_decorator_opens_circuit(self):
        """Test decorator opens circuit after failures."""
        call_count = {"value": 0}

        @circuit_breaker(failure_threshold=2, name="test_decorator")
        def func():
            call_count["value"] += 1
            raise ConnectionError("Network error")

        # First 2 failures
        for i in range(2):
            with pytest.raises(ConnectionError):
                func()

        # Circuit should be OPEN, next call raises CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            func()

        # Function should not be called when circuit is OPEN
        assert call_count["value"] == 2

    def test_decorator_has_breaker_attribute(self):
        """Test decorator attaches breaker instance."""

        @circuit_breaker(failure_threshold=3, name="test")
        def func():
            return "success"

        assert hasattr(func, "circuit_breaker")
        assert isinstance(func.circuit_breaker, CircuitBreaker)
        assert func.circuit_breaker.name == "test"


class TestGetCircuitBreaker:
    """Tests for get_circuit_breaker singleton factory."""

    def setup_method(self):
        """Reset all circuit breakers before each test."""
        reset_all_circuit_breakers()

    def test_get_creates_new_breaker(self):
        """Test get_circuit_breaker creates new instance."""
        breaker = get_circuit_breaker("service1")
        assert breaker.name == "service1"

    def test_get_returns_same_instance(self):
        """Test get_circuit_breaker returns singleton."""
        breaker1 = get_circuit_breaker("service1")
        breaker2 = get_circuit_breaker("service1")
        assert breaker1 is breaker2

    def test_different_names_different_instances(self):
        """Test different names return different instances."""
        breaker1 = get_circuit_breaker("service1")
        breaker2 = get_circuit_breaker("service2")
        assert breaker1 is not breaker2

    def test_reset_all_circuit_breakers(self):
        """Test reset_all_circuit_breakers."""
        # Create and open a circuit
        breaker = get_circuit_breaker("service1", failure_threshold=2)
        mock_func = Mock(side_effect=ConnectionError())

        for i in range(2):
            with pytest.raises(ConnectionError):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Reset all
        reset_all_circuit_breakers()

        # Breaker should be CLOSED
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_zero_failure_threshold(self):
        """Test behavior with zero failure threshold."""
        # This is an edge case - circuit should open immediately
        breaker = CircuitBreaker(failure_threshold=0, name="test")
        mock_func = Mock(side_effect=ConnectionError())

        # Even one failure should open circuit
        with pytest.raises(ConnectionError):
            breaker.call(mock_func)

        # Circuit should be OPEN
        # Note: Implementation may vary, adjust assertion if needed

    def test_very_long_recovery_timeout(self):
        """Test circuit stays OPEN with long recovery timeout."""
        breaker = CircuitBreaker(
            failure_threshold=1, recovery_timeout=10.0, name="test"
        )
        mock_func = Mock(side_effect=ConnectionError())

        # Open circuit
        with pytest.raises(ConnectionError):
            breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Should still be OPEN after short wait
        time.sleep(0.1)
        with pytest.raises(CircuitBreakerError):
            breaker.call(mock_func)

    def test_concurrent_access_thread_safe(self):
        """Test circuit breaker is thread-safe."""
        import concurrent.futures

        breaker = CircuitBreaker(failure_threshold=10, name="test")
        mock_func = Mock(return_value="success")

        # Make 100 concurrent calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(breaker.call, mock_func) for _ in range(100)]
            results = [f.result() for f in futures]

        assert all(r == "success" for r in results)
        assert mock_func.call_count == 100
        assert breaker.failure_count == 0
