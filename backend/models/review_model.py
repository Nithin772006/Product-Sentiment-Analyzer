from dataclasses import dataclass


@dataclass
class Review:
    """Temporary review model used as a guide for MongoDB documents."""

    product_name: str
    platform: str
    rating: int
    title: str
    review_text: str
    sentiment: str
    sentiment_score: float
