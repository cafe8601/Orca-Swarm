"""
Unit tests for retry logic.

Tests retry_with_backoff decorator, retry_on_failure function,
and RetryContext context manager.
"""

import pytest
import time
from unittest.mock import Mock, patch
from apps.realtime_poc.big_three_realtime_agents.utils.retry import (
    retry_with_backoff,
    retry_on_failure,
    RetryContext,
    retry_network_operation,
    retry_api_call,
)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    def test_success_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        mock_func = Mock(return_value="success")

        @retry_with_backoff(max_attempts=3)
        def func():
            return mock_func()

        result = func()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_success_after_retries(self):
        """Test function succeeds after retries."""
        mock_func = Mock(side_effect=[ConnectionError(), ConnectionError(), "success"])

        @retry_with_backoff(max_attempts=3, initial_delay=0.1)
        def func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        result = func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_all_retries_fail(self):
        """Test all retry attempts fail."""
        mock_func = Mock(side_effect=ConnectionError("Network error"))

        @retry_with_backoff(max_attempts=3, initial_delay=0.1)
        def func():
            return mock_func()

        with pytest.raises(ConnectionError, match="Network error"):
            func()

        assert mock_func.call_count == 3

    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        call_times = []

        @retry_with_backoff(max_attempts=3, initial_delay=0.1, exponential_base=2.0)
        def func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ConnectionError()
            return "success"

        func()

        # Check delays are approximately exponential
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        assert 0.08 < delay1 < 0.15  # ~0.1s (within tolerance)
        assert 0.18 < delay2 < 0.25  # ~0.2s (within tolerance)

    def test_custom_exceptions(self):
        """Test custom exception types."""

        @retry_with_backoff(max_attempts=2, initial_delay=0.1, exceptions=(ValueError,))
        def func():
            raise TypeError("Wrong exception")

        # Should not retry TypeError
        with pytest.raises(TypeError):
            func()

    def test_max_delay_limit(self):
        """Test max delay limit is respected."""
        call_times = []

        @retry_with_backoff(
            max_attempts=5, initial_delay=10.0, exponential_base=10.0, max_delay=0.2
        )
        def func():
            call_times.append(time.time())
            if len(call_times) < 5:
                raise ConnectionError()
            return "success"

        func()

        # All delays should be capped at max_delay
        for i in range(1, len(call_times)):
            delay = call_times[i] - call_times[i - 1]
            assert delay < 0.3  # Should be ~0.2s (max_delay)


class TestRetryOnFailure:
    """Tests for retry_on_failure function."""

    def test_functional_retry(self):
        """Test functional retry interface."""
        counter = {"value": 0}

        def func():
            counter["value"] += 1
            if counter["value"] < 3:
                raise ConnectionError()
            return "success"

        result = retry_on_failure(func, max_attempts=3, initial_delay=0.1)

        assert result == "success"
        assert counter["value"] == 3


class TestRetryContext:
    """Tests for RetryContext context manager."""

    def test_context_success(self):
        """Test successful retry with context manager."""
        counter = 0

        with RetryContext(max_attempts=3, initial_delay=0.1) as retry:
            for attempt in retry:
                counter = attempt
                if attempt == 2:
                    retry.success()
                    break
                retry.failure(ConnectionError("Temp error"))
                time.sleep(retry.get_delay())

        assert counter == 2

    def test_context_all_failures(self):
        """Test all attempts fail with context manager."""
        attempts = []

        with pytest.raises(Exception):
            with RetryContext(max_attempts=3, initial_delay=0.1) as retry:
                for attempt in retry:
                    attempts.append(attempt)
                    retry.failure(ConnectionError())
                    if not retry.should_retry():
                        raise ConnectionError("All failed")
                    time.sleep(retry.get_delay())

        assert len(attempts) == 3

    def test_context_get_delay(self):
        """Test delay calculation in context manager."""
        with RetryContext(max_attempts=3, initial_delay=0.1, exponential_base=2.0) as retry:
            delay1 = retry.get_delay()
            delay2 = retry.get_delay()
            delay3 = retry.get_delay()

            assert delay1 == 0.1
            assert delay2 == 0.2
            assert delay3 == 0.4


class TestConvenienceFunctions:
    """Tests for convenience retry functions."""

    def test_retry_network_operation(self):
        """Test retry_network_operation convenience function."""
        counter = {"value": 0}

        def func():
            counter["value"] += 1
            if counter["value"] < 2:
                raise ConnectionError()
            return "success"

        result = retry_network_operation(func)

        assert result == "success"
        assert counter["value"] == 2

    def test_retry_api_call(self):
        """Test retry_api_call convenience function."""
        counter = {"value": 0}

        def func():
            counter["value"] += 1
            if counter["value"] < 3:
                raise TimeoutError()
            return "success"

        result = retry_api_call(func)

        assert result == "success"
        assert counter["value"] == 3
