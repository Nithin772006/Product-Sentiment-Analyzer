from typing import Any, Dict, List, Optional
from pymongo.errors import DuplicateKeyError, PyMongoError
from database.config.database import DatabaseManager
from database.config.settings import Settings
from database.models.review import Review
from database.utils.logger import logger
from database.utils.validators import ValidationError, validate_review


class ReviewCollection:
    """Encapsulates CRUD operations on the reviews collection."""

    def __init__(self):
        self.collection_name = Settings.REVIEWS_COLLECTION

    def _get_coll(self):
        """Returns the PyMongo collection reference, or raises an exception if not connected."""
        coll = DatabaseManager.get_collection(self.collection_name)
        if coll is None:
            raise PyMongoError("Database connection is not established.")
        return coll

    def insert_review(self, review_data: Dict[str, Any]) -> bool:
        """Inserts a new review document. Validates the data before inserting."""
        try:
            # Validate input dictionary (will raise ValidationError if invalid)
            validate_review(review_data)

            # Ensure model to_dict is called (formats fields correctly)
            review_obj = Review.from_dict(review_data)
            doc = review_obj.to_dict()

            coll = self._get_coll()
            coll.insert_one(doc)
            logger.info(f"Review inserted successfully: {review_obj.review_id}")
            return True
        except ValidationError as e:
            logger.error(f"Validation failed for review: {e}")
            raise
        except DuplicateKeyError as e:
            logger.error(f"Duplicate review_id error: {e}")
            raise ValueError(f"Review with ID '{review_data.get('review_id')}' already exists.") from e
        except PyMongoError as e:
            logger.error(f"Database error during review insert: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during review insert: {e}")
            raise

    def update_review(self, review_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates an existing review's fields. Validates updated fields if present."""
        try:
            coll = self._get_coll()
            if "review_id" in update_data and update_data["review_id"] != review_id:
                raise ValidationError("Changing review_id is not allowed.")
            if "product_id" in update_data:
                raise ValidationError("Changing product_id is not allowed.")

            # Validate rating and sentiment if present
            if "rating" in update_data:
                rating = update_data["rating"]
                if not isinstance(rating, (int, float)) or not (0.0 <= rating <= 5.0):
                    raise ValidationError(f"rating must be numeric and between 0.0 and 5.0, got: {rating}")
            if "sentiment" in update_data:
                from utils.validators import VALID_SENTIMENTS
                sentiment = update_data["sentiment"]
                if sentiment is not None and sentiment.lower() not in VALID_SENTIMENTS:
                    raise ValidationError(f"sentiment must be one of {VALID_SENTIMENTS}, got: {sentiment}")

            result = coll.update_one({"review_id": review_id}, {"$set": update_data})
            if result.matched_count > 0:
                logger.info(f"Review updated: {review_id}")
                return True
            logger.warning(f"Review not found for update: {review_id}")
            return False
        except ValidationError as e:
            logger.error(f"Validation failed during update for review {review_id}: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error during review update {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during review update {review_id}: {e}")
            raise

    def delete_review(self, review_id: str) -> bool:
        """Deletes a review by review_id."""
        try:
            coll = self._get_coll()
            result = coll.delete_one({"review_id": review_id})
            if result.deleted_count > 0:
                logger.info(f"Review deleted: {review_id}")
                return True
            logger.warning(f"Review not found for deletion: {review_id}")
            return False
        except PyMongoError as e:
            logger.error(f"Database error during review deletion {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during review deletion {review_id}: {e}")
            raise

    def find_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Finds a single review by review_id."""
        try:
            coll = self._get_coll()
            doc = coll.find_one({"review_id": review_id})
            return doc
        except PyMongoError as e:
            logger.error(f"Database error during review find {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during review find {review_id}: {e}")
            raise

    def get_product_reviews(self, product_id: str, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Retrieves list of reviews associated with a specific product_id."""
        try:
            coll = self._get_coll()
            cursor = coll.find({"product_id": product_id}).skip(skip).limit(limit)
            return list(cursor)
        except PyMongoError as e:
            logger.error(f"Database error during get_product_reviews {product_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get_product_reviews {product_id}: {e}")
            raise
