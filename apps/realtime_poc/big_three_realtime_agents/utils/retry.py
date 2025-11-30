"""
Retry logic with exponential backoff for Big Three Realtime Agents.

Provides decorators and utilities for handling transient failures
in network operations, API calls, and external services.
"""

import time
import logging
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps


# Exception types that should trigger retries (transient errors)
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,  # Network-related OS errors
)


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Features:
    - Exponential backoff with configurable base and max delay
    - Configurable exception types to retry
    - Optional logging of retry attempts
    - Preserves function metadata

    Args:
        max_attempts: Maximum number of retry attempts (default: 3).
        initial_delay: Initial delay between retries in seconds (default: 1.0).
        exponential_base: Base for exponential backoff (default: 2.0).
        max_delay: Maximum delay between retries in seconds (default: 60.0).
        exceptions: Tuple of exception types to retry (default: RETRYABLE_EXCEPTIONS).
        logger: Optional logger instance for logging retry attempts.

    Returns:
        Decorated function with retry logic.

    Example:
        >>> @retry_with_backoff(max_attempts=3, exceptions=(ConnectionError,))
        ... def fetch_data():
        ...     return requests.get(url)

        >>> @retry_with_backoff(max_attempts=5, initial_delay=2.0, logger=my_logger)
        ... def call_api():
        ...     return client.api_call()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        if logger:
                            logger.error(
                                f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                            )
                        raise

                    # Calculate next delay with exponential backoff
                    current_delay = min(delay, max_delay)

                    if logger:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )

                    time.sleep(current_delay)
                    delay *= exponential_base

            # Should never reach here, but just in case
            raise last_exception

        return wrapper

    return decorator


def retry_on_failure(
    func: Callable,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Non-decorator version of retry_with_backoff for functional usage.

    Useful when you can't use decorators or need dynamic retry configuration.

    Args:
        func: Function to retry.
        max_attempts: Maximum number of retry attempts.
        initial_delay: Initial delay between retries in seconds.
        exponential_base: Base for exponential backoff.
        exceptions: Tuple of exception types to retry.
        logger: Optional logger instance.

    Returns:
        Function result if successful, raises last exception if all attempts fail.

    Example:
        >>> result = retry_on_failure(
        ...     lambda: api_call(),
        ...     max_attempts=3,
        ...     logger=my_logger
        ... )
    """

    @retry_with_backoff(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        exponential_base=exponential_base,
        exceptions=exceptions,
        logger=logger,
    )
    def wrapped():
        return func()

    return wrapped()


class RetryContext:
    """
    Context manager for retry operations with more control.

    Provides fine-grained control over retry behavior within a context.

    Example:
        >>> with RetryContext(max_attempts=3, logger=my_logger) as retry:
        ...     for attempt in retry:
        ...         try:
        ...             result = api_call()
        ...             retry.success()
        ...             break
        ...         except ConnectionError as e:
        ...             retry.failure(e)
        ...             if retry.should_retry():
        ...                 time.sleep(retry.get_delay())
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize retry context.

        Args:
            max_attempts: Maximum number of retry attempts.
            initial_delay: Initial delay between retries in seconds.
            exponential_base: Base for exponential backoff.
            max_delay: Maximum delay between retries in seconds.
            logger: Optional logger instance.
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay
        self.logger = logger

        self.attempt = 0
        self.current_delay = initial_delay
        self.last_exception = None
        self.succeeded = False

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if not self.succeeded and self.last_exception:
            if self.logger:
                self.logger.error(
                    f"All {self.max_attempts} attempts failed: {self.last_exception}"
                )
        return False  # Don't suppress exceptions

    def __iter__(self):
        """Iterate through attempts."""
        for i in range(1, self.max_attempts + 1):
            self.attempt = i
            yield i

    def success(self):
        """Mark operation as successful."""
        self.succeeded = True

    def failure(self, exception: Exception):
        """
        Record failure.

        Args:
            exception: Exception that caused the failure.
        """
        self.last_exception = exception

        if self.logger:
            self.logger.warning(
                f"Attempt {self.attempt}/{self.max_attempts} failed: {exception}"
            )

    def should_retry(self) -> bool:
        """
        Check if should retry.

        Returns:
            True if more attempts available, False otherwise.
        """
        return self.attempt < self.max_attempts

    def get_delay(self) -> float:
        """
        Get current delay and update for next attempt.

        Returns:
            Delay in seconds before next retry.
        """
        delay = min(self.current_delay, self.max_delay)
        self.current_delay *= self.exponential_base
        return delay


# Convenience functions for common retry scenarios

def retry_network_operation(
    func: Callable, logger: Optional[logging.Logger] = None
) -> Any:
    """
    Retry network operations with sensible defaults.

    Args:
        func: Network operation to retry.
        logger: Optional logger instance.

    Returns:
        Function result.
    """
    return retry_on_failure(
        func,
        max_attempts=3,
        initial_delay=1.0,
        exponential_base=2.0,
        exceptions=(ConnectionError, TimeoutError, OSError),
        logger=logger,
    )


def retry_api_call(
    func: Callable, logger: Optional[logging.Logger] = None
) -> Any:
    """
    Retry API calls with longer delays for rate limiting.

    Args:
        func: API call to retry.
        logger: Optional logger instance.

    Returns:
        Function result.
    """
    return retry_on_failure(
        func,
        max_attempts=5,
        initial_delay=2.0,
        exponential_base=2.0,
        exceptions=(ConnectionError, TimeoutError, OSError),
        logger=logger,
    )
