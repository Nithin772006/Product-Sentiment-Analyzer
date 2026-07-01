"""
Centralized configuration for the Sentiment Analysis module.

All settings can be overridden via environment variables or a ``.env`` file
placed in the ``sentiment/`` directory.  Defaults are chosen so the module
works out-of-the-box without any configuration.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────
# Resolve the root of the sentiment package (parent of config/)
_PACKAGE_ROOT: Path = Path(__file__).resolve().parent.parent

# Load .env from the sentiment package root (if it exists)
_env_path: Path = _PACKAGE_ROOT / ".env"
load_dotenv(dotenv_path=_env_path)

# ── File I/O ───────────────────────────────────────────────────────────
INPUT_FILE: str = os.getenv(
    "INPUT_FILE",
    str(_PACKAGE_ROOT / "output" / "sample_reviews.json"),
)

OUTPUT_FILE: str = os.getenv(
    "OUTPUT_FILE",
    str(_PACKAGE_ROOT / "output" / "analyzed_reviews.json"),
)

# ── Logging ────────────────────────────────────────────────────────────
ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "true").lower() in (
    "true",
    "1",
    "yes",
)

LOG_DIR: str = os.getenv("LOG_DIR", str(_PACKAGE_ROOT / "logs"))

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# ── Sentiment thresholds ──────────────────────────────────────────────
POSITIVE_THRESHOLD: float = float(os.getenv("POSITIVE_THRESHOLD", "0.05"))

NEGATIVE_THRESHOLD: float = float(os.getenv("NEGATIVE_THRESHOLD", "-0.05"))

CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
