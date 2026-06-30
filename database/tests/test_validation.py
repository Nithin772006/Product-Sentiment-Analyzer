import sys
from unittest.mock import MagicMock
from pathlib import Path

# Setup system path
db_path = Path(__file__).resolve().parent.parent
sys.path.append(str(db_path))
sys.path.append(str(db_path.parent))

# Mock missing modules
try:
    import pymongo
except ImportError:
    mock_pymongo = MagicMock()
    mock_pymongo.ASCENDING = 1
    mock_pymongo.DESCENDING = -1
    mock_pymongo.TEXT = "text"
    sys.modules["pymongo"] = mock_pymongo
    
    mock_errors = MagicMock()
    class PyMongoError(Exception): pass
    class DuplicateKeyError(PyMongoError): pass
    class ConnectionFailure(PyMongoError): pass
    class ConfigurationError(PyMongoError): pass
    class OperationFailure(PyMongoError): pass
    mock_errors.PyMongoError = PyMongoError
    mock_errors.DuplicateKeyError = DuplicateKeyError
    mock_errors.ConnectionFailure = ConnectionFailure
    mock_errors.ConfigurationError = ConfigurationError
    mock_errors.OperationFailure = OperationFailure
    sys.modules["pymongo.errors"] = mock_errors

try:
    import bson
except ImportError:
    mock_bson = MagicMock()
    class ObjectId:
        def __init__(self, val=None):
            self.val = val or "507f1f77bcf86cd799439011"
        def __str__(self):
            return str(self.val)
        def __repr__(self):
            return f"ObjectId('{self.val}')"
    mock_bson.ObjectId = ObjectId
    sys.modules["bson"] = mock_bson

try:
    import dotenv
except ImportError:
    sys.modules["dotenv"] = MagicMock()

from database.utils.validators import (
    ValidationError,
    validate_product,
    validate_review,
    validate_sentiment,
)


class TestValidationRules(unittest.TestCase):
    """Tests the Python application-level schema validation rules."""

    def test_valid_product(self):
        """Should validate a correctly structured product."""
        valid_prod = {
            "product_id": "prod_abc",
            "product_name": "Test Product",
            "brand": "BrandX",
            "category": "CategoryY",
            "price": 99.99,
            "rating": 4.5,
        }
        # Should not raise any exceptions
        try:
            validate_product(valid_prod)
        except ValidationError as e:
            self.fail(f"validate_product failed on valid data with: {e}")

    def test_invalid_product_missing_field(self):
        """Should raise ValidationError when required fields are missing."""
        invalid_prod = {
            "product_id": "prod_abc",
            "product_name": "Test Product",
            "brand": "BrandX",
            # missing category and price
            "rating": 4.5,
        }
        with self.assertRaises(ValidationError):
            validate_product(invalid_prod)

    def test_invalid_product_rating(self):
        """Should raise ValidationError when rating is out of range."""
        invalid_prod = {
            "product_id": "prod_abc",
            "product_name": "Test Product",
            "brand": "BrandX",
            "category": "CategoryY",
            "price": 99.99,
            "rating": 6.0,  # exceeds 5.0
        }
        with self.assertRaises(ValidationError):
            validate_product(invalid_prod)

        invalid_prod["rating"] = -1.0
        with self.assertRaises(ValidationError):
            validate_product(invalid_prod)

    def test_invalid_product_price(self):
        """Should raise ValidationError if price is negative or discount price is higher than price."""
        invalid_prod = {
            "product_id": "prod_abc",
            "product_name": "Test Product",
            "brand": "BrandX",
            "category": "CategoryY",
            "price": -10.0,
            "rating": 4.0,
        }
        with self.assertRaises(ValidationError):
            validate_product(invalid_prod)

        # Discount higher than price
        invalid_prod2 = {
            "product_id": "prod_abc",
            "product_name": "Test Product",
            "brand": "BrandX",
            "category": "CategoryY",
            "price": 50.0,
            "discount_price": 60.0,
            "rating": 4.0,
        }
        with self.assertRaises(ValidationError):
            validate_product(invalid_prod2)

    def test_valid_review(self):
        """Should validate a correctly structured review."""
        valid_rev = {
            "review_id": "rev_xyz",
            "product_id": "prod_abc",
            "reviewer_name": "John Doe",
            "review_text": "Highly durable.",
            "rating": 4.0,
            "sentiment": "positive",
        }
        try:
            validate_review(valid_rev)
        except ValidationError as e:
            self.fail(f"validate_review failed with: {e}")

    def test_invalid_review_sentiment(self):
        """Should raise ValidationError if sentiment label is invalid."""
        invalid_rev = {
            "review_id": "rev_xyz",
            "product_id": "prod_abc",
            "reviewer_name": "John Doe",
            "review_text": "Highly durable.",
            "rating": 4.0,
            "sentiment": "superb",  # not positive, neutral, negative
        }
        with self.assertRaises(ValidationError):
            validate_review(invalid_rev)

    def test_valid_sentiment(self):
        """Should validate a correctly structured sentiment analysis result."""
        valid_sent = {
            "review_id": "rev_xyz",
            "sentiment": "negative",
            "positive_score": 0.05,
            "neutral_score": 0.15,
            "negative_score": 0.80,
            "compound_score": -0.75,
            "confidence_score": 0.95,
        }
        try:
            validate_sentiment(valid_sent)
        except ValidationError as e:
            self.fail(f"validate_sentiment failed with: {e}")


if __name__ == "__main__":
    unittest.main()
