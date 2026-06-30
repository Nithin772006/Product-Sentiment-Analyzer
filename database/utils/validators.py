import re
from datetime import datetime
from typing import Any, Dict, List

# Valid sentiment strings
VALID_SENTIMENTS = {"positive", "neutral", "negative"}

# ISO 8601 regex for string dates (e.g. YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")


class ValidationError(Exception):
    """Exception raised for validation errors in document structures."""
    pass


def is_valid_date(val: Any) -> bool:
    """Helper to validate date values (datetime object or matching ISO-8601 regex)."""
    if isinstance(val, datetime):
        return True
    if isinstance(val, str):
        return bool(DATE_REGEX.match(val))
    return False


def is_numeric(val: Any) -> bool:
    """Helper to validate numeric values (int or float)."""
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Checks if all required fields are present in the dictionary and not None."""
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: '{field}'")
        if data[field] is None:
            raise ValidationError(f"Required field '{field}' cannot be None")


def validate_product(data: Dict[str, Any]) -> None:
    """Validates product fields against rules:
    - Required fields check
    - Unique/Valid product_id
    - Numeric values for price, discount_price, rating, total_reviews
    - Rating must be between 0.0 and 5.0
    - Price and discount_price must be >= 0
    - Proper dates for created_at, updated_at
    """
    required = ["product_id", "product_name", "brand", "category", "price", "rating"]
    validate_required_fields(data, required)

    # product_id validation
    pid = data.get("product_id")
    if not pid or not isinstance(pid, str):
        raise ValidationError("product_id must be a non-empty string")

    # Numeric ratings check
    rating = data.get("rating")
    if not is_numeric(rating) or not (0.0 <= rating <= 5.0):
        raise ValidationError(f"rating must be numeric and between 0.0 and 5.0, got: {rating}")

    # Total reviews check if present
    if "total_reviews" in data and data["total_reviews"] is not None:
        total_revs = data["total_reviews"]
        if not isinstance(total_revs, int) or total_revs < 0:
            raise ValidationError(f"total_reviews must be a non-negative integer, got: {total_revs}")

    # Price and discount_price validation
    price = data.get("price")
    if not is_numeric(price) or price < 0:
        raise ValidationError(f"price must be a non-negative number, got: {price}")

    if "discount_price" in data and data["discount_price"] is not None:
        disc_price = data["discount_price"]
        if not is_numeric(disc_price) or disc_price < 0:
            raise ValidationError(f"discount_price must be a non-negative number, got: {disc_price}")
        if disc_price > price:
            raise ValidationError(f"discount_price ({disc_price}) cannot exceed the regular price ({price})")

    # Date validations
    for date_field in ["created_at", "updated_at"]:
        if date_field in data and data[date_field] is not None:
            if not is_valid_date(data[date_field]):
                raise ValidationError(f"{date_field} must be a datetime object or ISO-8601 formatted string")


def validate_review(data: Dict[str, Any]) -> None:
    """Validates review fields against rules:
    - Required fields check
    - Unique/Valid review_id and product_id
    - Numeric rating between 0.0 and 5.0
    - Valid sentiment value (if present)
    - Valid review_date and created_at
    """
    required = ["review_id", "product_id", "reviewer_name", "review_text", "rating"]
    validate_required_fields(data, required)

    rid = data.get("review_id")
    if not rid or not isinstance(rid, str):
        raise ValidationError("review_id must be a non-empty string")

    pid = data.get("product_id")
    if not pid or not isinstance(pid, str):
        raise ValidationError("product_id must be a non-empty string")

    rating = data.get("rating")
    if not is_numeric(rating) or not (0.0 <= rating <= 5.0):
        raise ValidationError(f"rating must be numeric and between 0.0 and 5.0, got: {rating}")

    # Sentiment checking
    sentiment = data.get("sentiment")
    if sentiment is not None:
        if not isinstance(sentiment, str) or sentiment.lower() not in VALID_SENTIMENTS:
            raise ValidationError(f"sentiment must be one of {VALID_SENTIMENTS}, got: {sentiment}")

    # Confidence score checking
    if "confidence_score" in data and data["confidence_score"] is not None:
        conf = data["confidence_score"]
        if not is_numeric(conf) or not (0.0 <= conf <= 1.0):
            raise ValidationError(f"confidence_score must be between 0.0 and 1.0, got: {conf}")

    # Helpful votes checking
    if "helpful_votes" in data and data["helpful_votes"] is not None:
        votes = data["helpful_votes"]
        if not isinstance(votes, int) or votes < 0:
            raise ValidationError(f"helpful_votes must be a non-negative integer, got: {votes}")

    # Dates validation
    for date_field in ["review_date", "created_at"]:
        if date_field in data and data[date_field] is not None:
            if not is_valid_date(data[date_field]):
                raise ValidationError(f"{date_field} must be a datetime object or ISO-8601 formatted string")


def validate_sentiment(data: Dict[str, Any]) -> None:
    """Validates sentiment analysis results fields:
    - Required fields check
    - Valid review_id
    - Valid sentiment value (positive, neutral, negative)
    - Scores (positive, neutral, negative, compound, confidence) must be numeric
    - Sentiment scores usually in range 0.0 - 1.0 (compound score range: -1.0 - 1.0)
    """
    required = ["review_id", "sentiment", "positive_score", "neutral_score", "negative_score", "compound_score", "confidence_score"]
    validate_required_fields(data, required)

    rid = data.get("review_id")
    if not rid or not isinstance(rid, str):
        raise ValidationError("review_id must be a non-empty string")

    sentiment = data.get("sentiment")
    if not isinstance(sentiment, str) or sentiment.lower() not in VALID_SENTIMENTS:
        raise ValidationError(f"sentiment must be one of {VALID_SENTIMENTS}, got: {sentiment}")

    # Check scores
    for score_field in ["positive_score", "neutral_score", "negative_score", "confidence_score"]:
        score = data.get(score_field)
        if not is_numeric(score) or not (0.0 <= score <= 1.0):
            raise ValidationError(f"{score_field} must be numeric and between 0.0 and 1.0, got: {score}")

    compound = data.get("compound_score")
    if not is_numeric(compound) or not (-1.0 <= compound <= 1.0):
        raise ValidationError(f"compound_score must be numeric and between -1.0 and 1.0, got: {compound}")

    # Date validation
    if "analyzed_at" in data and data["analyzed_at"] is not None:
        if not is_valid_date(data["analyzed_at"]):
            raise ValidationError(f"analyzed_at must be a datetime object or ISO-8601 formatted string")
