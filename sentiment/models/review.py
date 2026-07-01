"""
Data model representing an incoming product review.

The :class:`Review` dataclass provides typed access to raw review data
received from the scraping pipeline and includes factory methods for
safe construction from untyped dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Review:
    """Represents a single product review.

    Attributes:
        review_id:   Unique identifier for the review.
        product_id:  Identifier of the product being reviewed.
        review_text: Raw text content of the review.
        rating:      Numeric rating given by the reviewer (e.g. 1-5).
        sentiment:   Pre-existing sentiment label, if any.
    """

    review_id: str
    product_id: str
    review_text: str
    rating: Optional[float] = None
    sentiment: Optional[str] = None

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Convert the review to a plain dictionary."""
        return {
            "review_id": self.review_id,
            "product_id": self.product_id,
            "review_text": self.review_text,
            "rating": self.rating,
            "sentiment": self.sentiment,
        }

    # ── Factory ────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Review:
        """Create a :class:`Review` from a dictionary.

        Missing or ``None`` text is normalised to an empty string so that
        downstream processing never receives ``None``.

        Args:
            data: Dictionary with review fields.

        Returns:
            A new :class:`Review` instance.

        Raises:
            KeyError: If ``review_id`` or ``product_id`` is missing.
        """
        return cls(
            review_id=str(data["review_id"]),
            product_id=str(data["product_id"]),
            review_text=str(data.get("review_text") or ""),
            rating=data.get("rating"),
            sentiment=data.get("sentiment"),
        )
