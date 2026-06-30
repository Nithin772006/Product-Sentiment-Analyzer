from datetime import datetime
from typing import Any, Dict, Optional
from database.utils.validators import validate_sentiment
from database.utils.helper import parse_date


class Sentiment:
    """Represents a Sentiment document schema and helper methods."""

    def __init__(
        self,
        review_id: str,
        sentiment: str,
        positive_score: float,
        neutral_score: float,
        negative_score: float,
        compound_score: float,
        confidence_score: float,
        analyzed_at: Optional[datetime] = None,
    ):
        self.review_id = review_id
        self.sentiment = sentiment.lower()
        self.positive_score = float(positive_score)
        self.neutral_score = float(neutral_score)
        self.negative_score = float(negative_score)
        self.compound_score = float(compound_score)
        self.confidence_score = float(confidence_score)
        self.analyzed_at = analyzed_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Sentiment object into a dictionary for MongoDB insertion."""
        doc = {
            "review_id": self.review_id,
            "sentiment": self.sentiment,
            "positive_score": self.positive_score,
            "neutral_score": self.neutral_score,
            "negative_score": self.negative_score,
            "compound_score": self.compound_score,
            "confidence_score": self.confidence_score,
            "analyzed_at": self.analyzed_at,
        }
        # Run validation before returning dict
        validate_sentiment(doc)
        return doc

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sentiment":
        """Creates a Sentiment object from a dictionary."""
        # Ensure validation is run
        validate_sentiment(data)

        return cls(
            review_id=data["review_id"],
            sentiment=data["sentiment"],
            positive_score=data["positive_score"],
            neutral_score=data["neutral_score"],
            negative_score=data["negative_score"],
            compound_score=data["compound_score"],
            confidence_score=data["confidence_score"],
            analyzed_at=parse_date(data.get("analyzed_at")),
        )
