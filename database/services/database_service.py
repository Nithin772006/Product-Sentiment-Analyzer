from typing import Any, Dict, List, Optional
from database.collections.product_collection import ProductCollection
from database.collections.review_collection import ReviewCollection
from database.collections.sentiment_collection import SentimentCollection


class DatabaseService:
    """Unified service offering database CRUD operations across all collections."""

    def __init__(self):
        self.products = ProductCollection()
        self.reviews = ReviewCollection()
        self.sentiments = SentimentCollection()

    # --- Product Operations ---

    def insert_product(self, product_data: Dict[str, Any]) -> bool:
        """Inserts a new product document."""
        return self.products.insert_product(product_data)

    def update_product(self, product_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates product information."""
        return self.products.update_product(product_id, update_data)

    def delete_product(self, product_id: str) -> bool:
        """Deletes a product document and optionally cleans up related reviews."""
        return self.products.delete_product(product_id)

    def find_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a product document by product_id."""
        return self.products.find_product(product_id)

    def get_all_products(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Retrieves a list of all products with pagination."""
        return self.products.get_all_products(limit=limit, skip=skip)

    # --- Review Operations ---

    def insert_review(self, review_data: Dict[str, Any]) -> bool:
        """Inserts a new review document."""
        return self.reviews.insert_review(review_data)

    def update_review(self, review_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates review information."""
        return self.reviews.update_review(review_id, update_data)

    def delete_review(self, review_id: str) -> bool:
        """Deletes a review document and associated sentiment record."""
        # Check if sentiment exists and delete it
        try:
            self.sentiments.delete_sentiment(review_id)
        except Exception:
            pass  # Non-fatal if sentiment did not exist
        return self.reviews.delete_review(review_id)

    def find_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a review document by review_id."""
        return self.reviews.find_review(review_id)

    def get_product_reviews(self, product_id: str, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Retrieves reviews for a specific product."""
        return self.reviews.get_product_reviews(product_id, limit=limit, skip=skip)

    # --- Sentiment Operations ---

    def insert_sentiment(self, sentiment_data: Dict[str, Any]) -> bool:
        """Inserts sentiment analysis details for a review."""
        return self.sentiments.insert_sentiment(sentiment_data)

    def update_sentiment(self, review_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates sentiment analysis scores."""
        return self.sentiments.update_sentiment(review_id, update_data)

    def get_sentiment(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves sentiment analysis values for a review."""
        return self.sentiments.get_sentiment(review_id)

    def delete_sentiment(self, review_id: str) -> bool:
        """Deletes sentiment analysis values for a review."""
        return self.sentiments.delete_sentiment(review_id)
