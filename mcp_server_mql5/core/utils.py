import time
from collections.abc import Generator
from contextlib import contextmanager
from threading import Lock
from typing import Any

from .config import logger

"""
Utility functions and classes for the MQL5 MCP Server.

This module includes helpers for rate limiting and execution time logging.
"""

# ==================== RATE LIMITER ====================


class RateLimiter:
    """
    Thread-safe rate limiter using a sliding window.

    Ensures that an operation is not performed more than a specified number of times
    within a one-minute window.
    """

    def __init__(self, calls_per_minute: int = 10) -> None:
        """
        Initialize the rate limiter.

        Args:
            calls_per_minute: Maximum allowed calls per minute. Defaults to 10.
        """
        self.calls_per_minute = calls_per_minute
        self.calls: list[float] = []
        self.lock = Lock()

    def wait_if_needed(self) -> None:
        """
        Blocks execution if the rate limit has been reached until a slot is available.

        This method checks the history of calls in the last minute. If the limit
        is exceeded, it sleeps for the necessary duration.
        """
        with self.lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < 60]

            if len(self.calls) >= self.calls_per_minute:
                sleep_time = 60 - (now - self.calls[0])
                if sleep_time > 0:
                    logger.warning(
                        f"Rate limit reached, sleeping {sleep_time:.2f}s",
                        extra={"calls_in_window": len(self.calls)},
                    )
                    time.sleep(sleep_time)

            self.calls.append(now)


limiter = RateLimiter(calls_per_minute=10)

# ==================== CONTEXT MANAGERS ====================


@contextmanager
def log_execution_time(
    operation: str, **extra_fields: Any
) -> Generator[dict[str, Any], None, None]:
    """
    Context manager to measure and log the execution time of a block of code.

    Args:
        operation: A name/description for the operation being measured.
        **extra_fields: Additional key-value pairs to include in the log record.

    Yields:
        A dictionary containing the extra fields, which can be modified within
        the context to add more information to the final log.
    """
    start = time.time()
    log_data = extra_fields.copy()

    try:
        yield log_data
        duration_ms = (time.time() - start) * 1000
        logger.info(
            f"{operation} completed in {duration_ms:.0f}ms",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "success": True,
                **log_data,
            },
        )
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.error(
            f"{operation} failed after {duration_ms:.0f}ms: {str(e)}",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "success": False,
                "error": str(e),
                **log_data,
            },
            exc_info=True,
        )
        raise
