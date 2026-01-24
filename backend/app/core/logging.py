import logging
import os
import sys


_LOGGING_CONFIGURED = False


def configure_logging(level: str | int | None = None) -> None:
    """
    Configure basic structured logging for the backend.

    This function is idempotent and safe to call multiple times.
    """
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    if level is None:
        level_name = os.getenv("API_LOG_LEVEL", "info").upper()
        level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name, ensuring logging is configured."""
    configure_logging()
    return logging.getLogger(name)