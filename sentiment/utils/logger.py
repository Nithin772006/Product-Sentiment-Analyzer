"""
Logging configuration for the Sentiment Analysis module.

Provides a pre-configured logger named ``sentiment`` that writes to both
the console and a rotating log file inside ``sentiment/logs/``.
"""

import logging
import os
from pathlib import Path

from sentiment.config.settings import ENABLE_LOGGING, LOG_DIR, LOG_LEVEL

_logger: logging.Logger | None = None


def get_logger(name: str = "sentiment") -> logging.Logger:
    """Return the module-wide logger, creating it on first call.

    Args:
        name: Logger name.  Defaults to ``"sentiment"``.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    global _logger  # noqa: PLW0603

    if _logger is not None:
        return _logger

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Prevent duplicate handlers when module is re-imported
    if logger.handlers:
        _logger = logger
        return _logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File handler (only when logging is enabled) ────────────────────
    if ENABLE_LOGGING:
        log_dir = Path(LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "sentiment.log"
        file_handler = logging.FileHandler(
            filename=str(log_file),
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return _logger
