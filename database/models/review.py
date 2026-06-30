from datetime import datetime
from typing import Any, Dict, Optional
from database.utils.validators import validate_review
from database.utils.helper import parse_date


class Review:
    """Represents a Review document schema and helper methods."""

    def __init__(
        self,
        review_id: str,
        product_id: str,
        reviewer_name: str,
        review_text: str,
        rating: float,
        review_title: Optional[str] = "",
        verified_purchase: Optional[bool] = False,
        review_date: Optional[datetime] = None,
        helpful_votes: Optional[int] = 0,
        sentiment: Optional[str] = None,
        confidence_score: Optional[float] = None,
        created_at: Optional[datetime] = None,
    ):
        self.review_id = review_id
        self.product_id = product_id
        self.reviewer_name = reviewer_name
        self.review_title = review_title
        self.review_text = review_text
        self.rating = float(rating)
        self.verified_purchase = bool(verified_purchase)
        self.review_date = review_date or datetime.utcnow()
        self.helpful_votes = int(helpful_votes) if helpful_votes is not None else 0
        self.sentiment = sentiment.lower() if sentiment is not None else None
        self.confidence_score = float(confidence_score) if confidence_score is not None else None
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Review object into a dictionary for MongoDB insertion."""
        doc = {
            "review_id": self.review_id,
            "product_id": self.product_id,
            "reviewer_name": self.reviewer_name,
            "review_title": self.review_title,
            "review_text": self.review_text,
            "rating": self.rating,
            "verified_purchase": self.verified_purchase,
            "review_date": self.review_date,
            "helpful_votes": self.helpful_votes,
            "sentiment": self.sentiment,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at,
        }
        # Run validation before returning dict
        validate_review(doc)
        return doc

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        """Creates a Review object from a dictionary."""
        # Ensure validation is run
        validate_review(data)

        return cls(
            review_id=data["review_id"],
            product_id=data["product_id"],
            reviewer_name=data["reviewer_name"],
            review_title=data.get("review_title", ""),
            review_text=data["review_text"],
            rating=data["rating"],
            verified_purchase=data.get("verified_purchase", False),
            review_date=parse_date(data.get("review_date")),
            helpful_votes=data.get("helpful_votes", 0),
            sentiment=data.get("sentiment"),
            confidence_score=data.get("confidence_score"),
            created_at=parse_date(data.get("created_at")),
        )
