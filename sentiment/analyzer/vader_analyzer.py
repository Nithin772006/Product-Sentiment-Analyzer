"""
VADER-based sentiment scoring and classification.

This module wraps NLTK's :class:`~nltk.sentiment.vader.SentimentIntensityAnalyzer`
and provides a reusable, singleton-style interface.  The VADER lexicon
is downloaded automatically on the first call.

Key functions:
    - :func:`get_sentiment_scores` – raw VADER polarity scores
    - :func:`classify_sentiment` – compound → label mapping
    - :func:`compute_confidence` – derives a 0-1 confidence value
"""

from __future__ import annotations

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from sentiment.config.settings import NEGATIVE_THRESHOLD, POSITIVE_THRESHOLD
from sentiment.utils.logger import get_logger

logger = get_logger()

# ── Singleton analyzer instance ────────────────────────────────────────
_analyzer: SentimentIntensityAnalyzer | None = None


def _get_analyzer() -> SentimentIntensityAnalyzer:
    """Return the shared VADER analyzer, creating it on first use."""
    global _analyzer  # noqa: PLW0603

    if _analyzer is None:
        # Ensure lexicon is available
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)

        _analyzer = SentimentIntensityAnalyzer()
        logger.info("VADER SentimentIntensityAnalyzer initialized.")

    return _analyzer


# ── Public API ─────────────────────────────────────────────────────────

def get_sentiment_scores(text: str) -> dict[str, float]:
    """Compute VADER polarity scores for *text*.

    Args:
        text: Pre-processed or raw review text.

    Returns:
        A dictionary with keys ``positive``, ``neutral``,
        ``negative``, and ``compound``.
    """
    analyzer = _get_analyzer()
    vs = analyzer.polarity_scores(text)

    return {
        "positive": vs["pos"],
        "neutral": vs["neu"],
        "negative": vs["neg"],
        "compound": vs["compound"],
    }


def classify_sentiment(compound: float) -> str:
    """Map a VADER compound score to a human-readable label.

    Classification rules (configurable via ``settings.py``):
        - ``compound >= POSITIVE_THRESHOLD``  →  ``"Positive"``
        - ``compound <= NEGATIVE_THRESHOLD``  →  ``"Negative"``
        - otherwise                           →  ``"Neutral"``

    Args:
        compound: The VADER compound score (–1.0 to +1.0).

    Returns:
        One of ``"Positive"``, ``"Negative"``, or ``"Neutral"``.
    """
    if compound >= POSITIVE_THRESHOLD:
        return "Positive"
    if compound <= NEGATIVE_THRESHOLD:
        return "Negative"
    return "Neutral"


def compute_confidence(scores: dict[str, float]) -> float:
    """Derive a 0-1 confidence score from VADER polarity scores.

    The confidence is defined as the absolute value of the compound
    score, which naturally ranges from 0 (neutral / uncertain) to
    1 (strongly polar).

    Args:
        scores: Dictionary returned by :func:`get_sentiment_scores`.

    Returns:
        A float between 0.0 and 1.0.
    """
    return round(abs(scores.get("compound", 0.0)), 4)
