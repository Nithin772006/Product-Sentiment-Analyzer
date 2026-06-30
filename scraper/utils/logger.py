"""
logger.py – Centralised logging setup for the scraper module.

Usage::

    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Scraper started")
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import settings


def _colour_formatter() -> logging.Formatter:
    """Return a formatter with ANSI colour codes for console output."""

    GREY = "\033[38;5;240m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[1;91m"
    RESET = "\033[0m"

    LEVEL_COLOURS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    class ColourFormatter(logging.Formatter):
        _fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        _date_fmt = "%Y-%m-%d %H:%M:%S"

        def format(self, record: logging.LogRecord) -> str:
            colour = LEVEL_COLOURS.get(record.levelno, RESET)
            formatter = logging.Formatter(
                f"{colour}{self._fmt}{RESET}", datefmt=self._date_fmt
            )
            return formatter.format(record)

    return ColourFormatter()


def setup_logger(name: str = "scraper") -> logging.Logger:
    """Configure and return a named logger.

    Creates:
    * A **RotatingFileHandler** writing to ``logs/scraper.log``.
    * A **StreamHandler** writing coloured output to stdout.

    Calling this function multiple times with the same *name* is safe –
    handlers are only added once.

    Args:
        name: Logger name (typically ``__name__`` of the calling module).

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)

    plain_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # -- File handler (rotating) ------------------------------------------
    file_handler = RotatingFileHandler(
        filename=settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(plain_fmt)
    logger.addHandler(file_handler)

    # -- Console handler (coloured) ----------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(_colour_formatter())
    logger.addHandler(console_handler)

    return logger


# Module-level convenience alias
def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the root 'scraper' hierarchy.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        :class:`logging.Logger`
    """
    # Ensure root logger is set up
    setup_logger("scraper")
    return logging.getLogger(name)
