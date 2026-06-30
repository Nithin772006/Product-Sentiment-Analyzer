"""
test_models.py – Unit tests for Product and Review data models.

Tests cover:
* Default field values.
* to_dict() serialisation.
* from_dict() deserialisation.
* Sentiment field always being None.
* Unknown keys ignored by from_dict().
"""

import sys
import unittest
from pathlib import Path

# Ensure the scraper package is importable regardless of CWD
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.product import Product
from models.review import Review


class TestProductModel(unittest.TestCase):
    """Tests for the Product dataclass."""

    def _make_product(self, **kwargs) -> Product:
        defaults = dict(
            product_id="TESTID123",
            product_name="Test Product",
        )
        defaults.update(kwargs)
        return Product(**defaults)

    def test_required_fields(self):
        """Product can be created with only required fields."""
        p = self._make_product()
        self.assertEqual(p.product_id, "TESTID123")
        self.assertEqual(p.product_name, "Test Product")

    def test_optional_fields_default_to_none(self):
        """Optional fields default to None."""
        p = self._make_product()
        for field in ("brand", "category", "price", "discount_price",
                      "overall_rating", "num_ratings", "num_reviews",
                      "description", "availability", "image_url",
                      "product_url", "source"):
            self.assertIsNone(getattr(p, field), f"{field} should be None")

    def test_scraped_at_auto_set(self):
        """scraped_at is automatically populated as an ISO string."""
        p = self._make_product()
        self.assertIsNotNone(p.scraped_at)
        self.assertIn("T", p.scraped_at)  # ISO 8601 contains 'T'

    def test_to_dict_contains_all_fields(self):
        """to_dict() returns all 15 expected fields."""
        p = self._make_product(brand="Acme", price=999.0, source="amazon")
        d = p.to_dict()
        expected_keys = {
            "product_id", "product_name", "brand", "category", "price",
            "discount_price", "overall_rating", "num_ratings", "num_reviews",
            "description", "availability", "image_url", "product_url",
            "source", "scraped_at",
        }
        self.assertEqual(set(d.keys()), expected_keys)

    def test_to_dict_values_correct(self):
        """to_dict() values match the dataclass fields."""
        p = self._make_product(brand="Sony", price=25000.0, source="amazon")
        d = p.to_dict()
        self.assertEqual(d["brand"], "Sony")
        self.assertEqual(d["price"], 25000.0)
        self.assertEqual(d["source"], "amazon")

    def test_from_dict_round_trip(self):
        """Product → dict → Product preserves all values."""
        p = self._make_product(brand="Samsung", category="Electronics",
                               price=15000.0, source="flipkart")
        restored = Product.from_dict(p.to_dict())
        self.assertEqual(restored.product_id, p.product_id)
        self.assertEqual(restored.brand, p.brand)
        self.assertEqual(restored.price, p.price)

    def test_from_dict_ignores_unknown_keys(self):
        """from_dict() silently ignores keys not in the dataclass."""
        data = {
            "product_id": "XYZ",
            "product_name": "Test",
            "unknown_future_field": "value",
        }
        p = Product.from_dict(data)
        self.assertEqual(p.product_id, "XYZ")
        self.assertFalse(hasattr(p, "unknown_future_field"))

    def test_repr(self):
        """__repr__ contains product_id and product_name."""
        p = self._make_product()
        r = repr(p)
        self.assertIn("TESTID123", r)
        self.assertIn("Test Product", r)


class TestReviewModel(unittest.TestCase):
    """Tests for the Review dataclass."""

    def _make_review(self, **kwargs) -> Review:
        defaults = dict(
            review_id="REV000001",
            product_id="TESTID123",
        )
        defaults.update(kwargs)
        return Review(**defaults)

    def test_required_fields(self):
        """Review can be created with only required fields."""
        r = self._make_review()
        self.assertEqual(r.review_id, "REV000001")
        self.assertEqual(r.product_id, "TESTID123")

    def test_sentiment_always_none(self):
        """sentiment field must always be None from the scraper."""
        r = self._make_review()
        self.assertIsNone(r.sentiment)

    def test_sentiment_cannot_be_set_via_from_dict(self):
        """from_dict() resets sentiment to None even if provided."""
        data = {
            "review_id": "R1",
            "product_id": "P1",
            "sentiment": "positive",  # Simulate accidental population
        }
        r = Review.from_dict(data)
        self.assertIsNone(r.sentiment)

    def test_to_dict_has_sentiment_key(self):
        """to_dict() always includes the 'sentiment' key."""
        r = self._make_review()
        d = r.to_dict()
        self.assertIn("sentiment", d)
        self.assertIsNone(d["sentiment"])

    def test_to_dict_contains_all_fields(self):
        """to_dict() returns all 12 expected fields."""
        r = self._make_review()
        d = r.to_dict()
        expected_keys = {
            "review_id", "product_id", "review_title", "review_text",
            "star_rating", "reviewer_name", "verified_purchase",
            "review_date", "helpful_votes", "source", "scraped_at",
            "sentiment",
        }
        self.assertEqual(set(d.keys()), expected_keys)

    def test_from_dict_round_trip(self):
        """Review → dict → Review preserves values and sentiment=None."""
        r = self._make_review(
            review_title="Great product",
            star_rating=5.0,
            verified_purchase=True,
            source="amazon",
        )
        restored = Review.from_dict(r.to_dict())
        self.assertEqual(restored.review_id, r.review_id)
        self.assertEqual(restored.review_title, r.review_title)
        self.assertEqual(restored.star_rating, r.star_rating)
        self.assertIsNone(restored.sentiment)

    def test_optional_fields_default_to_none(self):
        """Optional Review fields default to None."""
        r = self._make_review()
        for field in ("review_title", "review_text", "star_rating",
                      "reviewer_name", "verified_purchase", "review_date",
                      "helpful_votes", "source"):
            self.assertIsNone(getattr(r, field), f"{field} should be None")


if __name__ == "__main__":
    unittest.main()
