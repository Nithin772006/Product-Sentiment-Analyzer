"""
Sentiment Analysis Module – CLI entry point.

Run from the project root::

    python -m sentiment.main
    python sentiment/main.py
    python sentiment/main.py --input data/reviews.json --output data/results.json

If no arguments are provided, the paths default to the values in
``config/settings.py`` (which reads from ``.env`` or environment variables).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the project root is on sys.path so ``sentiment`` is importable
# regardless of where the script is invoked from.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sentiment.analyzer.sentiment_engine import process_file  # noqa: E402
from sentiment.config.settings import INPUT_FILE, OUTPUT_FILE  # noqa: E402
from sentiment.utils.logger import get_logger  # noqa: E402

logger = get_logger()


def _parse_args() -> argparse.Namespace:
    """Parse optional CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run VADER sentiment analysis on product reviews.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=INPUT_FILE,
        help="Path to the input JSON file (default: %(default)s).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=OUTPUT_FILE,
        help="Path to the output JSON file (default: %(default)s).",
    )
    return parser.parse_args()


def main() -> None:
    """Module entry point."""
    args = _parse_args()

    logger.info("Sentiment Analysis Module started.")

    results = process_file(args.input, args.output)

    if results:
        print(f"\n[SUCCESS] Analysis complete – {len(results)} review(s) processed.")
        print(f"          Results saved to: {args.output}\n")
    else:
        print("\n[WARNING] No reviews were processed. Check logs for details.\n")

    logger.info("Sentiment Analysis Module finished.")


if __name__ == "__main__":
    main()
