from typing import Any, Dict, Optional
from pymongo.errors import DuplicateKeyError, PyMongoError
from database.config.database import DatabaseManager
from database.config.settings import Settings
from database.models.sentiment import Sentiment
from database.utils.logger import logger
from database.utils.validators import ValidationError, validate_sentiment


class SentimentCollection:
    """Encapsulates CRUD operations on the sentiments collection."""

    def __init__(self):
        self.collection_name = Settings.SENTIMENTS_COLLECTION

    def _get_coll(self):
        """Returns the PyMongo collection reference, or raises an exception if not connected."""
        coll = DatabaseManager.get_collection(self.collection_name)
        if coll is None:
            raise PyMongoError("Database connection is not established.")
        return coll

    def insert_sentiment(self, sentiment_data: Dict[str, Any]) -> bool:
        """Inserts a new sentiment document. Validates the data before inserting."""
        try:
            # Validate input dictionary (will raise ValidationError if invalid)
            validate_sentiment(sentiment_data)

            # Ensure model to_dict is called (formats fields correctly)
            sentiment_obj = Sentiment.from_dict(sentiment_data)
            doc = sentiment_obj.to_dict()

            coll = self._get_coll()
            coll.insert_one(doc)
            logger.info(f"Sentiment inserted successfully for review_id: {sentiment_obj.review_id}")
            return True
        except ValidationError as e:
            logger.error(f"Validation failed for sentiment: {e}")
            raise
        except DuplicateKeyError as e:
            logger.error(f"Duplicate sentiment review_id error: {e}")
            raise ValueError(f"Sentiment with review_id '{sentiment_data.get('review_id')}' already exists.") from e
        except PyMongoError as e:
            logger.error(f"Database error during sentiment insert: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during sentiment insert: {e}")
            raise

    def update_sentiment(self, review_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates sentiment analysis values for a specific review_id."""
        try:
            coll = self._get_coll()
            if "review_id" in update_data and update_data["review_id"] != review_id:
                raise ValidationError("Changing review_id is not allowed.")

            # Partially validate updating scores if present
            from utils.validators import is_numeric, VALID_SENTIMENTS
            if "sentiment" in update_data:
                sentiment = update_data["sentiment"]
                if not isinstance(sentiment, str) or sentiment.lower() not in VALID_SENTIMENTS:
                    raise ValidationError(f"sentiment must be one of {VALID_SENTIMENTS}, got: {sentiment}")
            
            for score_field in ["positive_score", "neutral_score", "negative_score", "confidence_score"]:
                if score_field in update_data:
                    score = update_data[score_field]
                    if not is_numeric(score) or not (0.0 <= score <= 1.0):
                        raise ValidationError(f"{score_field} must be numeric and between 0.0 and 1.0, got: {score}")

            if "compound_score" in update_data:
                compound = update_data["compound_score"]
                if not is_numeric(compound) or not (-1.0 <= compound <= 1.0):
                    raise ValidationError(f"compound_score must be numeric and between -1.0 and 1.0, got: {compound}")

            # Update analyzed_at datetime if not provided
            update_data["analyzed_at"] = update_data.get("analyzed_at") or datetime.utcnow()

            result = coll.update_one({"review_id": review_id}, {"$set": update_data})
            if result.matched_count > 0:
                logger.info(f"Sentiment updated for review_id: {review_id}")
                return True
            logger.warning(f"Sentiment not found for update: {review_id}")
            return False
        except ValidationError as e:
            logger.error(f"Validation failed during update for sentiment {review_id}: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error during sentiment update {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during sentiment update {review_id}: {e}")
            raise

    def get_sentiment(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a sentiment analysis document by review_id."""
        try:
            coll = self._get_coll()
            doc = coll.find_one({"review_id": review_id})
            return doc
        except PyMongoError as e:
            logger.error(f"Database error during get_sentiment {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get_sentiment {review_id}: {e}")
            raise

    def delete_sentiment(self, review_id: str) -> bool:
        """Deletes a sentiment record by review_id."""
        try:
            coll = self._get_coll()
            result = coll.delete_one({"review_id": review_id})
            if result.deleted_count > 0:
                logger.info(f"Sentiment deleted for review_id: {review_id}")
                return True
            logger.warning(f"Sentiment not found for deletion: {review_id}")
            return False
        except PyMongoError as e:
            logger.error(f"Database error during sentiment deletion {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during sentiment deletion {review_id}: {e}")
            raise


from datetime import datetime
