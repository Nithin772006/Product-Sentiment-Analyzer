"""
Data model representing the result of sentiment analysis on a review.

The :class:`SentimentResult` dataclass captures the sentiment label,
confidence score, and the four VADER polarity scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SentimentResult:
    """Structured output of sentiment analysis for one review.

    Attributes:
        review_id:        Unique review identifier (echoed from input).
        product_id:       Product identifier (echoed from input).
        review_text:      The original (or cleaned) review text.
        sentiment:        Predicted label – ``"Positive"``, ``"Negative"``,
                          or ``"Neutral"``.
        confidence_score: A 0-1 float indicating prediction confidence.
        scores:           VADER polarity scores dictionary with keys
                          ``positive``, ``neutral``, ``negative``, ``compound``.
    """

    review_id: str
    product_id: str
    review_text: str
    sentiment: str
    confidence_score: float
    scores: dict[str, float] = field(default_factory=dict)

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Convert the result to a JSON-serialisable dictionary."""
        return {
            "review_id": self.review_id,
            "product_id": self.product_id,
            "review_text": self.review_text,
            "sentiment": self.sentiment,
            "confidence_score": round(self.confidence_score, 4),
            "scores": {
                "positive": round(self.scores.get("positive", 0.0), 4),
                "neutral": round(self.scores.get("neutral", 0.0), 4),
                "negative": round(self.scores.get("negative", 0.0), 4),
                "compound": round(self.scores.get("compound", 0.0), 4),
            },
        }
