"""
General-purpose helper functions for the Sentiment Analysis module.

Provides safe JSON I/O and review-dict validation so that higher-level
code stays clean and focused on business logic.
"""

import json
from pathlib import Path
from typing import Any

from sentiment.utils.logger import get_logger

logger = get_logger()

# Keys that every valid review dictionary must contain
_REQUIRED_KEYS: set[str] = {"review_id", "product_id", "review_text"}


def validate_review_dict(data: dict[str, Any]) -> bool:
    """Check whether *data* has the minimum required keys for analysis.

    Args:
        data: A dictionary representing a single review.

    Returns:
        ``True`` if all required keys are present, ``False`` otherwise.
    """
    if not isinstance(data, dict):
        return False
    return _REQUIRED_KEYS.issubset(data.keys())


def safe_read_json(filepath: str | Path) -> list[dict[str, Any]]:
    """Read a JSON file and return its contents as a list of dicts.

    The file may contain either a **single JSON object** or a
    **JSON array** of objects.  In both cases the return value is a list.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A list of dictionaries parsed from the file.
        Returns an empty list on any error.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        logger.error("File not found: %s", filepath)
        return []

    if not filepath.is_file():
        logger.error("Path is not a file: %s", filepath)
        return []

    try:
        raw = filepath.read_text(encoding="utf-8")
    except PermissionError:
        logger.error("Permission denied reading file: %s", filepath)
        return []
    except UnicodeDecodeError:
        logger.error("Unsupported encoding in file: %s", filepath)
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", filepath, exc)
        return []

    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data

    logger.warning("Unexpected JSON type in %s: %s", filepath, type(data).__name__)
    return []


def safe_write_json(
    data: list[dict[str, Any]],
    filepath: str | Path,
) -> bool:
    """Write *data* as a JSON array to *filepath*.

    Parent directories are created automatically if they do not exist.

    Args:
        data: A list of serialisable dictionaries.
        filepath: Destination path.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    filepath = Path(filepath)

    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Results saved to %s", filepath)
        return True
    except PermissionError:
        logger.error("Permission denied writing to: %s", filepath)
        return False
    except (TypeError, ValueError) as exc:
        logger.error("Serialization error: %s", exc)
        return False
