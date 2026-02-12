import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path

"""
Configuration and logging setup for the MQL5 MCP Server.

This module defines constants, default configuration values, and the logging system
used throughout the application. It sets up structured JSON logging and file rotation.
"""

# ==================== CONSTANTS ====================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

MQL5_SEARCH_API = "https://search.mql5.com/api/query"
# Keeping as fallback if needed, but primary is now API
DDG_URL = "https://html.duckduckgo.com/html/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

DEFAULT_HEADERS = {
    "Referer": "https://html.duckduckgo.com/",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# ==================== LOGGING ====================


class StructuredFormatter(logging.Formatter):
    """
    Structured JSON formatter for log records.

    Formats log records as JSON strings, including standard fields (timestamp, level,
    logger, message) and any extra fields passed in the `extra` dictionary.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Extra fields
        for key in [
            "search_term",
            "duration_ms",
            "url",
            "cache_hit",
            "status_code",
            "operation",
            "error",
        ]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(logger_name: str = "mql5_server") -> logging.Logger:
    """
    Configures the application logger with MCP-safe settings.

    Sets up rotating file handlers for JSON logs, text logs, and errors.
    Ensures that logs are NOT propagated to the root logger or printed to stdout/stderr
    (unless in debug mode), as this would interfere with the MCP protocol stdio
    transport.

    Args:
        logger_name: The name of the logger to configure. Defaults to "mql5_server".

    Returns:
        The configured logging.Logger instance.
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Important!

    # Only FileHandlers - NEVER stdout
    json_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{logger_name}.json.log",
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    json_handler.setFormatter(StructuredFormatter())
    logger.addHandler(json_handler)

    text_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{logger_name}.log",
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    text_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(text_handler)

    error_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "errors.log", maxBytes=10_000_000, backupCount=10, encoding="utf-8"
    )
    error_handler.setFormatter(StructuredFormatter())
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    # Stderr only in debug (optional)
    if __debug__:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        stderr_handler.setLevel(logging.ERROR)  # Only critical errors
        logger.addHandler(stderr_handler)

    return logger


# Global logger instance
logger = setup_logging()
