"""
review.py – Review data model.

Defines the canonical structure for a scraped product review.

The ``sentiment`` field is intentionally set to ``None`` and must **not**
be populated by the scraper.  It is reserved for the Sentiment Analysis
team who will run a separate pipeline to fill it in.

Usage::

    from models.review import Review
    r = Review(
        review_id="A1B2C3D4E5F6G7H8",
        product_id="B0CH7RLKFC",
        review_title="Amazing headphones!",
        ...
    )
    doc = r.to_dict()   # MongoDB-ready dict
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Review:
    """Represents a single scraped customer review.

    Attributes:
        review_id:         Stable unique identifier (SHA-256 hash of key
                           fields or the site's native review ID).
        product_id:        Foreign key referencing the parent
                           :class:`~models.product.Product`.
        review_title:      Headline / summary of the review.
        review_text:       Full body text of the review.
        star_rating:       Numeric star rating given by the reviewer
                           (0.0 – 5.0).
        reviewer_name:     Display name of the reviewer.
        verified_purchase: ``True`` if the platform marks the purchase as
                           verified.
        review_date:       ISO 8601 date string (``'YYYY-MM-DD'``).
        helpful_votes:     Number of 'helpful' upvotes the review received.
        source:            Platform identifier ('amazon' or 'flipkart').
        scraped_at:        ISO 8601 UTC timestamp of when the data was
                           collected.
        sentiment:         **Reserved** – always ``None`` from the scraper.
                           Will be populated by the Sentiment Analysis team.
    """

    review_id: str
    product_id: str
    review_title: str | None = None
    review_text: str | None = None
    star_rating: float | None = None
    reviewer_name: str | None = None
    verified_purchase: bool | None = None
    review_date: str | None = None
    helpful_votes: int | None = None
    source: str | None = None
    scraped_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    # ------------------------------------------------------------------ #
    # IMPORTANT: Do NOT modify or populate this field in the scraper.     #
    # It is reserved for the Sentiment Analysis team.                     #
    # ------------------------------------------------------------------ #
    sentiment: None = None

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a MongoDB-ready dictionary representation.

        The ``sentiment`` key is always present and always ``None`` so
        the backend can rely on a consistent document schema.

        Returns:
            Dict mapping field names to values.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Review":
        """Construct a :class:`Review` from a raw dictionary.

        Unknown keys are silently ignored to allow forward compatibility.
        The ``sentiment`` field, even if present in *data*, is always
        reset to ``None`` to prevent accidental population.

        Args:
            data: Dictionary (e.g. loaded from JSON).

        Returns:
            :class:`Review` instance.
        """
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known_fields}
        # Enforce sentiment = None regardless of input
        filtered["sentiment"] = None
        return cls(**filtered)

    def __repr__(self) -> str:
        return (
            f"Review(id={self.review_id!r}, product={self.product_id!r}, "
            f"rating={self.star_rating}, source={self.source!r})"
        )
