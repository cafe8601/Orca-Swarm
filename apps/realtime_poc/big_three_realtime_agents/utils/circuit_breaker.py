"""
Circuit Breaker pattern implementation for Big Three Realtime Agents.

Prevents cascading failures by temporarily blocking calls to failing services.
Based on Martin Fowler's Circuit Breaker pattern.
"""

import time
import logging
import threading
from typing import Callable, Any, Optional
from enum import Enum
from functools import wraps


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, calls pass through
    OPEN = "open"  # Failures detected, calls blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit Breaker for protecting against cascading failures.

    States:
    - CLOSED: Normal operation, all calls pass through
    - OPEN: After failure threshold, all calls blocked
    - HALF_OPEN: After timeout, allow test calls to check recovery

    Example:
        >>> breaker = CircuitBreaker(
        ...     failure_threshold=5,
        ...     recovery_timeout=30,
        ...     name="gemini_api"
        ... )
        >>>
        >>> result = breaker.call(api_function, arg1, arg2)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
        name: str = "circuit_breaker",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening circuit.
            recovery_timeout: Seconds before transitioning from OPEN to HALF_OPEN.
            half_open_max_calls: Max test calls in HALF_OPEN state before deciding.
            name: Circuit breaker name for logging.
            logger: Optional logger instance.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.name = name
        self.logger = logger or logging.getLogger(__name__)

        # State tracking
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0

        # Thread safety
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        with self._lock:
            return self._failure_count

    @property
    def success_count(self) -> int:
        """Get current success count."""
        with self._lock:
            return self._success_count

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to call.
            *args: Positional arguments for function.
            **kwargs: Keyword arguments for function.

        Returns:
            Function result.

        Raises:
            CircuitBreakerError: If circuit is OPEN.
            Exception: Original exception from function.
        """
        with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self.logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable, try again in "
                        f"{self._time_until_half_open():.1f}s"
                    )

            # In HALF_OPEN, limit test calls
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' max test calls reached in HALF_OPEN"
                    )
                self._half_open_calls += 1

        # Execute the function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure_time is None:
            return False
        return time.time() - self._last_failure_time >= self.recovery_timeout

    def _time_until_half_open(self) -> float:
        """Calculate time remaining until HALF_OPEN transition."""
        if self._last_failure_time is None:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        remaining = self.recovery_timeout - elapsed
        return max(0.0, remaining)

    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            self._failure_count = 0

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1

                # If enough successful test calls, close circuit
                if self._success_count >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._success_count = 0
                    self.logger.info(
                        f"Circuit breaker '{self.name}' closed after successful recovery"
                    )

    def _on_failure(self, exception: Exception):
        """Handle failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            # If in HALF_OPEN and failed, immediately go back to OPEN
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._success_count = 0
                self.logger.warning(
                    f"Circuit breaker '{self.name}' reopened after failed test call: {exception}"
                )

            # If in CLOSED and hit threshold, open circuit
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    self.logger.error(
                        f"Circuit breaker '{self.name}' opened after "
                        f"{self.failure_threshold} consecutive failures: {exception}"
                    )

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._half_open_calls = 0
            self.logger.info(f"Circuit breaker '{self.name}' manually reset")

    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics.

        Returns:
            Dictionary with current stats.
        """
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure_time": self._last_failure_time,
                "time_until_half_open": self._time_until_half_open() if self._state == CircuitState.OPEN else None,
            }


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    name: str = "circuit_breaker",
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Decorator for circuit breaker pattern.

    Creates a circuit breaker instance and wraps the function.

    Args:
        failure_threshold: Number of failures before opening circuit.
        recovery_timeout: Seconds before attempting recovery.
        name: Circuit breaker name.
        logger: Optional logger instance.

    Returns:
        Decorated function with circuit breaker protection.

    Example:
        >>> @circuit_breaker(failure_threshold=5, recovery_timeout=30, name="api")
        ... def call_api():
        ...     return requests.get(url)
    """
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        name=name,
        logger=logger,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return breaker.call(func, *args, **kwargs)

        # Attach breaker instance for external access
        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


# Shared circuit breaker instances for common services
_circuit_breakers = {}
_circuit_breakers_lock = threading.Lock()


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    logger: Optional[logging.Logger] = None,
) -> CircuitBreaker:
    """
    Get or create a shared circuit breaker instance.

    Provides singleton circuit breakers per service name.

    Args:
        name: Circuit breaker name (used as key).
        failure_threshold: Number of failures before opening.
        recovery_timeout: Seconds before recovery attempt.
        logger: Optional logger instance.

    Returns:
        CircuitBreaker instance.

    Example:
        >>> breaker = get_circuit_breaker("gemini_api")
        >>> result = breaker.call(api_function)
    """
    with _circuit_breakers_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                name=name,
                logger=logger,
            )
        return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict:
    """
    Get all active circuit breaker instances.

    Returns:
        Dictionary mapping names to circuit breaker instances.
    """
    with _circuit_breakers_lock:
        return dict(_circuit_breakers)


def reset_all_circuit_breakers():
    """Reset all circuit breakers to CLOSED state."""
    with _circuit_breakers_lock:
        for breaker in _circuit_breakers.values():
            breaker.reset()
